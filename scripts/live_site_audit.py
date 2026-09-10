#!/usr/bin/env python3
"""Read-only sitemap and on-page audit for a production origin."""

from __future__ import annotations

import argparse
import concurrent.futures
import gzip
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser


USER_AGENT = "OrganicSearchOperator/1.0 (+read-only audit)"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.h1_count = 0
        self.canonical = ""
        self.description = ""
        self.robots = ""
        self.og_image = ""
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        lowered = tag.lower()
        if lowered == "title":
            self._in_title = True
        elif lowered == "h1":
            self.h1_count += 1
        elif lowered == "link" and "canonical" in values.get("rel", "").lower().split():
            self.canonical = values.get("href", "").strip()
        elif lowered == "meta":
            name = values.get("name", "").lower()
            prop = values.get("property", "").lower()
            if name == "description":
                self.description = values.get("content", "").strip()
            elif name in ("robots", "googlebot"):
                self.robots = f"{self.robots},{values.get('content', '')}".strip(",")
            elif prop == "og:image":
                self.og_image = values.get("content", "").strip()
        elif lowered == "a" and values.get("href"):
            self.links.append(values["href"].strip())

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data


def fetch(url: str, max_bytes: int = 5_000_000) -> tuple[int, str, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError(f"response exceeded {max_bytes} bytes: {url}")
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return response.status, response.geturl(), raw, response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), exc.read(1000), exc.headers.get("Content-Type", "")


def xml_locations(raw: bytes) -> tuple[str, list[str]]:
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"invalid sitemap XML: {exc}") from exc
    kind = root.tag.rsplit("}", 1)[-1]
    locations = [
        (element.text or "").strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "loc" and (element.text or "").strip()
    ]
    return kind, locations


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    return urllib.parse.urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def audit_page(url: str, origin_host: str) -> dict:
    try:
        status, final_url, raw, content_type = fetch(url)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {"url": url, "status": "fetch_failed", "error": str(exc), "issues": ["fetch_failed"]}

    result = {
        "url": url,
        "http_status": status,
        "final_url": final_url,
        "content_type": content_type,
        "issues": [],
        "internal_links": [],
    }
    if status != 200:
        result["issues"].append(f"http_{status}")
    if "html" not in content_type.lower():
        result["issues"].append("not_html")
        return result

    parser = PageParser()
    try:
        parser.feed(raw.decode("utf-8", errors="replace"))
    except Exception as exc:
        result["issues"].append(f"html_parse_error:{type(exc).__name__}")

    canonical = urllib.parse.urljoin(final_url, parser.canonical) if parser.canonical else ""
    result.update(
        {
            "title": parser.title.strip(),
            "description": parser.description,
            "h1_count": parser.h1_count,
            "canonical": canonical,
            "robots": parser.robots,
            "og_image": urllib.parse.urljoin(final_url, parser.og_image) if parser.og_image else "",
        }
    )
    if not result["title"]:
        result["issues"].append("missing_title")
    if not parser.description:
        result["issues"].append("missing_meta_description")
    if parser.h1_count == 0:
        result["issues"].append("missing_h1")
    elif parser.h1_count > 1:
        result["issues"].append("multiple_h1")
    if not canonical:
        result["issues"].append("missing_canonical")
    elif normalize_url(canonical) != normalize_url(final_url):
        result["issues"].append("canonical_mismatch")
    if "noindex" in parser.robots.lower():
        result["issues"].append("noindex")
    if not parser.og_image:
        result["issues"].append("missing_og_image")

    internal: list[str] = []
    for href in parser.links:
        absolute = urllib.parse.urljoin(final_url, href)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme in ("http", "https") and parsed.netloc.lower() == origin_host:
            normalized = normalize_url(absolute)
            if normalized not in internal:
                internal.append(normalized)
    result["internal_links"] = internal
    return result


def gather_sitemap_urls(sitemap_url: str, origin_host: str, max_urls: int) -> tuple[list[str], list[dict]]:
    queue = [sitemap_url]
    seen_maps: set[str] = set()
    urls: list[str] = []
    sitemap_reports: list[dict] = []
    while queue and len(urls) < max_urls:
        current = queue.pop(0)
        if current in seen_maps:
            continue
        seen_maps.add(current)
        status, final_url, raw, _ = fetch(current)
        report = {"url": current, "http_status": status, "final_url": final_url, "issues": []}
        if status != 200:
            report["issues"].append(f"http_{status}")
            sitemap_reports.append(report)
            continue
        try:
            kind, locations = xml_locations(raw)
        except ValueError as exc:
            report["issues"].append(str(exc))
            sitemap_reports.append(report)
            continue
        report.update({"type": kind, "location_count": len(locations)})
        sitemap_reports.append(report)
        if kind == "sitemapindex":
            for location in locations:
                if urllib.parse.urlparse(location).netloc.lower() == origin_host and location not in seen_maps:
                    queue.append(location)
        elif kind == "urlset":
            for location in locations:
                parsed = urllib.parse.urlparse(location)
                if parsed.netloc.lower() != origin_host:
                    report["issues"].append(f"foreign_url:{location}")
                elif location not in urls:
                    urls.append(location)
                    if len(urls) >= max_urls:
                        break
        else:
            report["issues"].append(f"unexpected_root:{kind}")
    return urls, sitemap_reports


def cmd_audit(args: argparse.Namespace) -> int:
    origin = normalize_url(args.origin).rstrip("/")
    parsed_origin = urllib.parse.urlparse(origin)
    if parsed_origin.scheme != "https" or not parsed_origin.netloc:
        raise ValueError("origin must be an absolute HTTPS URL")
    sitemap_url = args.sitemap or f"{origin}/sitemap.xml"
    robots_url = f"{origin}/robots.txt"
    robots_status, robots_final, robots_raw, _ = fetch(robots_url, max_bytes=1_000_000)
    urls, sitemap_reports = gather_sitemap_urls(sitemap_url, parsed_origin.netloc.lower(), args.max_urls)

    pages: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(audit_page, url, parsed_origin.netloc.lower()) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            pages.append(future.result())
    pages.sort(key=lambda item: item["url"])

    sitemap_set = {normalize_url(url) for url in urls}
    inbound = Counter()
    for page in pages:
        for link in page.get("internal_links", []):
            if link in sitemap_set:
                inbound[link] += 1
    for page in pages:
        normalized = normalize_url(page["url"])
        if inbound[normalized] == 0 and normalized.rstrip("/") != origin:
            page["issues"].append("no_sampled_internal_inlinks")
        page["sampled_internal_inlinks"] = inbound[normalized]

    issue_counts = Counter(issue for page in pages for issue in page.get("issues", []))
    report = {
        "origin": origin,
        "read_only": True,
        "robots": {
            "url": robots_url,
            "http_status": robots_status,
            "final_url": robots_final,
            "contains_sitemap_directive": b"sitemap:" in robots_raw.lower(),
        },
        "sitemaps": sitemap_reports,
        "sampled_url_count": len(pages),
        "issue_counts": dict(sorted(issue_counts.items())),
        "pages": pages,
        "limitations": [
            "Internal-link counts cover only sampled sitemap URLs.",
            "This parser does not render client-side JavaScript.",
            "A clean audit does not imply indexing or ranking.",
        ],
    }
    encoded_report = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded_report)
        print(json.dumps({"status": "saved", "output": args.output, "sampled_urls": len(pages)}, indent=2))
    else:
        sys.stdout.write(encoded_report)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--sitemap")
    parser.add_argument("--max-urls", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return cmd_audit(args)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
