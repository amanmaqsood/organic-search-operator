#!/usr/bin/env python3
"""Minimal Google Search Console client using captured gcloud ADC tokens.

Read commands are immediate. Sitemap submission is dry-run unless --apply is
provided. Access tokens are captured and never printed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"
INSPECTION_API = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
ALLOWED_DIMENSIONS = {"date", "query", "page", "country", "device", "searchAppearance"}


def gcloud_command(arguments: list[str]) -> list[str]:
    executable = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not executable:
        raise ValueError("gcloud is not installed or is not on PATH")
    if sys.platform == "win32" and executable.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", executable, *arguments]
    return [executable, *arguments]


def access_token() -> str:
    command = gcloud_command(["auth", "application-default", "print-access-token"])
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("gcloud authentication check timed out") from exc
    if result.returncode != 0:
        detail = (result.stderr or "gcloud returned an authentication error").strip().splitlines()[-1]
        raise ValueError(f"application-default credentials are unavailable: {detail}")
    token = result.stdout.strip()
    if not token:
        raise ValueError("gcloud returned an empty access token")
    return token


def adc_candidates() -> list[Path]:
    result: list[Path] = []
    if os.environ.get("CLOUDSDK_CONFIG"):
        result.append(Path(os.environ["CLOUDSDK_CONFIG"]) / "application_default_credentials.json")
    if os.environ.get("APPDATA"):
        result.append(Path(os.environ["APPDATA"]) / "gcloud" / "application_default_credentials.json")
    result.append(Path.home() / ".config" / "gcloud" / "application_default_credentials.json")
    return result


def quota_project() -> str | None:
    for path in adc_candidates():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        value = data.get("quota_project_id") if isinstance(data, dict) else None
        if isinstance(value, str) and value:
            return value
    return None


def request_json(
    method: str,
    url: str,
    body: dict | None = None,
    token: str | None = None,
) -> dict:
    captured_token = token or access_token()
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {captured_token}", "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    project = quota_project()
    if project:
        headers["X-Goog-User-Project"] = project
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else {"http_status": response.status}
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(payload).get("error", {}).get("message", payload[:300])
        except json.JSONDecodeError:
            message = payload[:300]
        raise ValueError(f"Google API HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"Google API network error: {exc.reason}") from exc


def atomic_output(path: str | None, data: dict) -> None:
    encoded = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if not path:
        sys.stdout.write(encoded)
        return
    output = Path(path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{output.name}.", dir=str(output.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, output)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    print(json.dumps({"status": "saved", "output": str(output)}, indent=2))


def encoded(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def cmd_sites(args: argparse.Namespace) -> int:
    data = request_json("GET", f"{WEBMASTERS_API}/sites")
    atomic_output(args.output, data)
    return 0


def parse_dimensions(value: str) -> list[str]:
    dimensions = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [item for item in dimensions if item not in ALLOWED_DIMENSIONS]
    if invalid:
        raise ValueError("unsupported GSC dimensions: " + ", ".join(invalid))
    return dimensions


def cmd_performance(args: argparse.Namespace) -> int:
    body = {
        "startDate": args.start,
        "endDate": args.end,
        "dimensions": parse_dimensions(args.dimensions),
        "rowLimit": args.row_limit,
        "startRow": args.start_row,
        "dataState": args.data_state,
    }
    if args.search_type:
        body["type"] = args.search_type
    url = f"{WEBMASTERS_API}/sites/{encoded(args.site)}/searchAnalytics/query"
    data = request_json("POST", url, body)
    data["request_metadata"] = {
        "site": args.site,
        "start": args.start,
        "end": args.end,
        "dimensions": body["dimensions"],
        "data_state": args.data_state,
        "warning": "Position and CTR retain Google Search Console aggregation semantics.",
    }
    atomic_output(args.output, data)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    urls: list[str] = []
    for value in args.url or []:
        if value not in urls:
            urls.append(value)
    if args.urls_file:
        for line in Path(args.urls_file).read_text(encoding="utf-8").splitlines():
            value = line.strip()
            if value and value not in urls:
                urls.append(value)
    if not urls:
        raise ValueError("provide --url or --urls-file")
    if len(urls) > args.max_urls:
        urls = urls[: args.max_urls]
    token = access_token()
    results: list[dict] = []
    for inspection_url in urls:
        try:
            response = request_json(
                "POST",
                INSPECTION_API,
                {"inspectionUrl": inspection_url, "siteUrl": args.site},
                token=token,
            )
            results.append({"url": inspection_url, "status": "completed", "response": response})
        except ValueError as exc:
            results.append({"url": inspection_url, "status": "failed", "error": str(exc)})
    data = {
        "site": args.site,
        "inspection_is_not_submission": True,
        "results": results,
    }
    atomic_output(args.output, data)
    return 0 if all(item["status"] == "completed" for item in results) else 2


def cmd_sitemaps(args: argparse.Namespace) -> int:
    url = f"{WEBMASTERS_API}/sites/{encoded(args.site)}/sitemaps"
    data = request_json("GET", url)
    atomic_output(args.output, data)
    return 0


def cmd_submit_sitemap(args: argparse.Namespace) -> int:
    plan = {
        "status": "dry_run" if not args.apply else "pending",
        "site": args.site,
        "sitemap": args.sitemap,
        "guarantees_indexing": False,
    }
    if not args.apply:
        atomic_output(args.output, plan)
        return 0
    url = f"{WEBMASTERS_API}/sites/{encoded(args.site)}/sitemaps/{encoded(args.sitemap)}"
    response = request_json("PUT", url)
    plan.update({"status": "submitted", "response": response})
    atomic_output(args.output, plan)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sites = sub.add_parser("sites", help="list accessible GSC properties")
    sites.add_argument("--output")
    sites.set_defaults(func=cmd_sites)

    performance = sub.add_parser("performance", help="query Search Analytics data")
    performance.add_argument("--site", required=True)
    performance.add_argument("--start", required=True, help="YYYY-MM-DD")
    performance.add_argument("--end", required=True, help="YYYY-MM-DD")
    performance.add_argument("--dimensions", default="query,page,date")
    performance.add_argument("--row-limit", type=int, default=25000, choices=range(1, 25001))
    performance.add_argument("--start-row", type=int, default=0)
    performance.add_argument("--data-state", choices=("final", "all", "hourly_all"), default="final")
    performance.add_argument("--search-type", choices=("web", "image", "video", "news", "discover", "googleNews"))
    performance.add_argument("--output")
    performance.set_defaults(func=cmd_performance)

    inspect = sub.add_parser("inspect", help="inspect selected URL index state")
    inspect.add_argument("--site", required=True)
    inspect.add_argument("--url", action="append")
    inspect.add_argument("--urls-file")
    inspect.add_argument("--max-urls", type=int, default=10)
    inspect.add_argument("--output")
    inspect.set_defaults(func=cmd_inspect)

    sitemaps = sub.add_parser("sitemaps", help="list submitted sitemaps")
    sitemaps.add_argument("--site", required=True)
    sitemaps.add_argument("--output")
    sitemaps.set_defaults(func=cmd_sitemaps)

    submit = sub.add_parser("submit-sitemap", help="dry-run or submit a sitemap")
    submit.add_argument("--site", required=True)
    submit.add_argument("--sitemap", required=True)
    submit.add_argument("--apply", action="store_true")
    submit.add_argument("--output")
    submit.set_defaults(func=cmd_submit_sitemap)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
