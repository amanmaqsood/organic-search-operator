#!/usr/bin/env python3
"""Generate, verify, and submit IndexNow keys and URL batches safely."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,128}$")


def atomic_text_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def read_key(args: argparse.Namespace) -> str:
    key: str | None = None
    if getattr(args, "key_file", None):
        key = Path(args.key_file).read_text(encoding="utf-8").strip()
    elif getattr(args, "key_env", None):
        key = os.environ.get(args.key_env)
    if not key:
        raise ValueError("IndexNow key is unavailable; use --key-file or set --key-env")
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError("IndexNow key must be 8 to 128 URL-safe ASCII characters")
    return key


def normalize_host(value: str) -> str:
    value = value.strip().lower()
    if "://" in value:
        value = urllib.parse.urlparse(value).netloc.lower()
    if not value or "/" in value or " " in value:
        raise ValueError("host must be a bare domain name")
    return value


def collect_urls(args: argparse.Namespace, host: str) -> list[str]:
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
    if len(urls) > 10000:
        raise ValueError("IndexNow batches cannot exceed 10,000 URLs")
    for value in urls:
        parsed = urllib.parse.urlparse(value)
        if parsed.scheme not in ("http", "https") or parsed.netloc.lower() != host:
            raise ValueError(f"URL must use configured host {host}: {value}")
        if parsed.fragment:
            raise ValueError(f"URL must not contain a fragment: {value}")
    return urls


def validate_key_location(host: str, value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or parsed.netloc.lower() != host:
        raise ValueError("key location must be an HTTPS URL on the configured host")
    return value


def cmd_generate(args: argparse.Namespace) -> int:
    output = Path(args.output).resolve()
    if output.exists() and not args.force:
        raise ValueError(f"refusing to replace existing key file: {output}")
    key = secrets.token_hex(16)
    atomic_text_write(output, key)
    print(json.dumps({"status": "generated", "output": str(output), "key_was_printed": False}, indent=2))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    host = normalize_host(args.host)
    location = validate_key_location(host, args.key_location)
    key = read_key(args)
    try:
        with urllib.request.urlopen(location, timeout=30) as response:
            live = response.read().decode("utf-8", errors="replace").strip()
    except urllib.error.URLError as exc:
        raise ValueError(f"could not fetch IndexNow key location: {exc.reason}") from exc
    matched = secrets.compare_digest(live, key)
    print(json.dumps({"status": "verified" if matched else "mismatch", "key_location": location}, indent=2))
    return 0 if matched else 2


def cmd_submit(args: argparse.Namespace) -> int:
    host = normalize_host(args.host)
    location = validate_key_location(host, args.key_location)
    key = read_key(args)
    urls = collect_urls(args, host)
    summary = {
        "status": "dry_run" if not args.apply else "pending",
        "host": host,
        "key_location": location,
        "url_count": len(urls),
        "guarantees_indexing": False,
    }
    if not args.apply:
        print(json.dumps(summary, indent=2))
        return 0

    payload = json.dumps({"host": host, "key": key, "keyLocation": location, "urlList": urls}).encode("utf-8")
    request = urllib.request.Request(
        args.endpoint,
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response.read()
            status_code = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise ValueError(f"IndexNow HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"IndexNow network error: {exc.reason}") from exc

    summary.update({"status": "submitted", "http_status": status_code})
    print(json.dumps(summary, indent=2))
    return 0


def add_key_source(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--key-file")
    group.add_argument("--key-env", default=None, help="environment variable containing the key")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate-key", help="generate a key without printing it")
    generate.add_argument("--output", required=True)
    generate.add_argument("--force", action="store_true")
    generate.set_defaults(func=cmd_generate)

    verify = sub.add_parser("verify-key", help="compare the local key to its live public file")
    verify.add_argument("--host", required=True)
    verify.add_argument("--key-location", required=True)
    add_key_source(verify)
    verify.set_defaults(func=cmd_verify)

    submit = sub.add_parser("submit", help="dry-run or submit canonical URLs")
    submit.add_argument("--host", required=True)
    submit.add_argument("--key-location", required=True)
    submit.add_argument("--url", action="append")
    submit.add_argument("--urls-file")
    submit.add_argument("--endpoint", default=INDEXNOW_ENDPOINT)
    submit.add_argument("--apply", action="store_true")
    add_key_source(submit)
    submit.set_defaults(func=cmd_submit)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
