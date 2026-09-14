#!/usr/bin/env python3
"""Read-only, bounded technical-quality audit for a production origin."""

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


USER_AGENT = "OrganicSearchOperator/1.5 (+read-only audit)"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._heading_level: int | None = None
        self._heading_text: list[str] = []
        self._in_json_ld = False
        self._json_ld_text: list[str] = []
        self.h1_count = 0
        self.headings: list[dict] = []
        self.canonical = ""
        self.description = ""
        self.robots = ""
        self.og_image = ""
        self.viewport = ""
        self.html_lang = ""
        self.links: list[str] = []
        self.images: list[dict] = []
        self.json_ld_blocks: list[str] = []
        self.resource_urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        lowered = tag.lower()
        if lowered == "html":
            self.html_lang = values.get("lang", "").strip()
        elif lowered == "title":
            self._in_title = True
        elif re.fullmatch(r"h[1-6]", lowered):
            self._heading_level = int(lowered[1])
            self._heading_text = []
            if lowered == "h1":
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
            elif name == "viewport":
                self.viewport = values.get("content", "").strip()
            elif prop == "og:image":
                self.og_image = values.get("content", "").strip()
        elif lowered == "a" and values.get("href"):
            self.links.append(values["href"].strip())
        elif lowered == "img":
            self.images.append(
                {
                    "src": values.get("src", "").strip(),
                    "alt_present": "alt" in values,
                    "alt": values.get("alt", "").strip(),
                    "width": values.get("width", "").strip(),
                    "height": values.get("height", "").strip(),
                }
            )
        elif lowered == "script" and values.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_text = []

        if lowered in ("img", "script", "iframe", "source", "video", "audio") and values.get("src"):
            self.resource_urls.append(values["src"].strip())
        if lowered == "link" and values.get("href"):
            self.resource_urls.append(values["href"].strip())

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered == "title":
            self._in_title = False
        elif self._heading_level is not None and lowered == f"h{self._heading_level}":
            self.headings.append(
                {"level": self._heading_level, "text": " ".join(self._heading_text).strip()}
            )
            self._heading_level = None
            self._heading_text = []
        elif lowered == "script" and self._in_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_text).strip())
            self._in_json_ld = False
            self._json_ld_text = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._heading_level is not None:
            self._heading_text.append(data)
        if self._in_json_ld:
            self._json_ld_text.append(data)


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


def fetch_status(url: str) -> tuple[int, str, str]:
    """Fetch response metadata without treating a large page body as broken."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.geturl(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        if exc.code not in (405, 501):
            return exc.code, exc.geturl(), exc.headers.get("Content-Type", "")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Range": "bytes=0-1023"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response.read(1024)
            return response.status, response.geturl(), response.headers.get("Content-Type", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.geturl(), exc.headers.get("Content-Type", "")


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


def schema_types(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        candidate = value.get("@type")
        if isinstance(candidate, str):
            found.append(candidate)
        elif isinstance(candidate, list):
            found.extend(item for item in candidate if isinstance(item, str))
        for nested in value.values():
            found.extend(schema_types(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(schema_types(nested))
    return found


def heading_has_jump(headings: list[dict]) -> bool:
    levels = [item["level"] for item in headings]
    return any(current > previous + 1 for previous, current in zip(levels, levels[1:]))


def slug_needs_review(url: str) -> bool:
    path = urllib.parse.unquote(urllib.parse.urlparse(url).path)
    segments = [segment for segment in path.split("/") if segment]
    return any(
        segment != segment.lower()
        or "_" in segment
        or "--" in segment
        or len(segment) > 100
        for segment in segments
    )


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
    parsed_images = [
        {**item, "src": urllib.parse.urljoin(final_url, item["src"]) if item["src"] else ""}
        for item in parser.images
    ]
    parsed_schema: list[str] = []
    invalid_schema = 0
    for block in parser.json_ld_blocks:
        if not block:
            invalid_schema += 1
            continue
        try:
            parsed_schema.extend(schema_types(json.loads(block)))
        except json.JSONDecodeError:
            invalid_schema += 1

    mixed_resources = [
        urllib.parse.urljoin(final_url, resource)
        for resource in parser.resource_urls
        if urllib.parse.urljoin(final_url, resource).lower().startswith("http://")
    ]
    missing_alt = sum(1 for image in parsed_images if not image["alt_present"])
    empty_alt = sum(1 for image in parsed_images if image["alt_present"] and not image["alt"])
    missing_dimensions = sum(1 for image in parsed_images if not image["width"] or not image["height"])

    result.update(
        {
            "title": parser.title.strip(),
            "description": parser.description,
            "h1_count": parser.h1_count,
            "headings": parser.headings,
            "canonical": canonical,
            "robots": parser.robots,
            "og_image": urllib.parse.urljoin(final_url, parser.og_image) if parser.og_image else "",
            "viewport": parser.viewport,
            "html_lang": parser.html_lang,
            "images": {
                "count": len(parsed_images),
                "missing_alt_attribute": missing_alt,
                "empty_alt": empty_alt,
                "missing_explicit_dimensions": missing_dimensions,
            },
            "structured_data": {
                "block_count": len(parser.json_ld_blocks),
                "types": sorted(set(parsed_schema)),
                "invalid_block_count": invalid_schema,
                "static_html_only": True,
            },
            "mixed_content_resources": mixed_resources,
            "broken_internal_links": [],
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
    if heading_has_jump(parser.headings):
        result["issues"].append("heading_level_jump")
    if any(not item["text"] for item in parser.headings):
        result["issues"].append("empty_heading")
    if not canonical:
        result["issues"].append("missing_canonical")
    elif normalize_url(canonical) != normalize_url(final_url):
        result["issues"].append("canonical_mismatch")
    if "noindex" in parser.robots.lower():
        result["issues"].append("noindex_in_sitemap")
    if not parser.og_image:
        result["issues"].append("missing_og_image")
    if not parser.viewport:
        result["issues"].append("missing_viewport_meta")
    if missing_alt:
        result["issues"].append("images_missing_alt_attribute")
    if missing_dimensions:
        result["issues"].append("images_missing_explicit_dimensions")
    if invalid_schema:
        result["issues"].append("invalid_static_json_ld")
    if mixed_resources:
        result["issues"].append("mixed_content")
    if slug_needs_review(final_url):
        result["issues"].append("url_slug_review")

    internal: list[str] = []
    for href in parser.links:
        absolute = urllib.parse.urljoin(final_url, href)
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme in ("http", "https") and parsed.netloc.lower() == origin_host:
            normalized = normalize_url(absolute)
            if normalized not in internal:
                internal.append(normalized)
            if parsed.scheme == "http" and "http_internal_link" not in result["issues"]:
                result["issues"].append("http_internal_link")
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


def check_destination(url: str) -> dict:
    try:
        status, final_url, content_type = fetch_status(url)
        return {"url": url, "http_status": status, "final_url": final_url, "content_type": content_type}
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {"url": url, "status": "fetch_failed", "error": str(exc)}


def issue_severity(issue: str) -> str:
    if issue in {
        "fetch_failed",
        "canonical_mismatch",
        "noindex_in_sitemap",
        "broken_internal_link",
        "mixed_content",
        "http_internal_link",
    } or re.fullmatch(r"http_[45]\d\d", issue):
        return "blocking"
    if issue in {
        "missing_title",
        "missing_meta_description",
        "missing_h1",
        "missing_canonical",
        "heading_level_jump",
        "empty_heading",
        "images_missing_alt_attribute",
        "invalid_static_json_ld",
        "missing_viewport_meta",
        "not_html",
    }:
        return "required_review"
    return "advisory"


def https_enforcement(origin_host: str) -> dict:
    source = f"http://{origin_host}/"
    try:
        status, final_url, _ = fetch_status(source)
        enforced = urllib.parse.urlparse(final_url).scheme == "https"
        return {"url": source, "http_status": status, "final_url": final_url, "redirects_to_https": enforced}
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return {"url": source, "status": "unavailable", "error": str(exc), "redirects_to_https": None}


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
    sources_by_target: dict[str, list[dict]] = {}
    for page in pages:
        for link in page.get("internal_links", []):
            if link in sitemap_set:
                inbound[link] += 1
            sources_by_target.setdefault(link, []).append(page)
    for page in pages:
        normalized = normalize_url(page["url"])
        if inbound[normalized] == 0 and normalized.rstrip("/") != origin:
            page["issues"].append("no_sampled_internal_inlinks")
        page["sampled_internal_inlinks"] = inbound[normalized]

    page_status = {normalize_url(page["url"]): page for page in pages}
    targets = sorted(sources_by_target)[: args.max_link_checks]
    link_checks: list[dict] = []
    unknown_targets = [target for target in targets if target not in page_status]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        checked = list(pool.map(check_destination, unknown_targets))
    checked_by_url = {item["url"]: item for item in checked}
    for target in targets:
        if target in page_status:
            page = page_status[target]
            check = {
                "url": target,
                "http_status": page.get("http_status"),
                "final_url": page.get("final_url", target),
                "source": "sampled_page",
            }
            if page.get("status") == "fetch_failed":
                check["status"] = "fetch_failed"
        else:
            check = checked_by_url[target]
            check["source"] = "bounded_link_check"
        link_checks.append(check)
        broken = check.get("status") == "fetch_failed" or int(check.get("http_status") or 0) >= 400
        if broken:
            for source_page in sources_by_target[target]:
                source_page.setdefault("broken_internal_links", []).append(target)
                if "broken_internal_link" not in source_page["issues"]:
                    source_page["issues"].append("broken_internal_link")

    title_pages: dict[str, list[dict]] = {}
    description_pages: dict[str, list[dict]] = {}
    for page in pages:
        if page.get("title"):
            title_pages.setdefault(page["title"].casefold(), []).append(page)
        if page.get("description"):
            description_pages.setdefault(page["description"].casefold(), []).append(page)
    for group in title_pages.values():
        if len(group) > 1:
            for page in group:
                page["issues"].append("duplicate_sampled_title")
    for group in description_pages.values():
        if len(group) > 1:
            for page in group:
                page["issues"].append("duplicate_sampled_meta_description")

    issue_counts = Counter(issue for page in pages for issue in page.get("issues", []))
    severity_counts = Counter()
    for issue, count in issue_counts.items():
        severity_counts[issue_severity(issue)] += count
    robots_issues = []
    if robots_status != 200:
        robots_issues.append(f"http_{robots_status}")
    if b"sitemap:" not in robots_raw.lower():
        robots_issues.append("missing_sitemap_directive")
    sitemap_issues = sum(len(report.get("issues", [])) for report in sitemap_reports)
    if robots_status != 200:
        severity_counts["required_review"] += 1
    if b"sitemap:" not in robots_raw.lower():
        severity_counts["required_review"] += 1
    if sitemap_issues:
        severity_counts["blocking"] += sitemap_issues
    https_report = https_enforcement(parsed_origin.netloc.lower())
    if https_report["redirects_to_https"] is False:
        severity_counts["blocking"] += 1

    report = {
        "origin": origin,
        "read_only": True,
        "technical_quality_gate": {
            "severity_counts": dict(sorted(severity_counts.items())),
            "robots_issue_count": len(robots_issues),
            "sitemap_issue_count": sitemap_issues,
            "interpretation": {
                "blocking": "Likely prevents or materially harms intended discovery, access, or canonical delivery.",
                "required_review": "Expected on applicable indexable pages; inspect context before changing.",
                "advisory": "Useful review signal, not a universal ranking rule.",
            },
        },
        "https_enforcement": https_report,
        "robots": {
            "url": robots_url,
            "http_status": robots_status,
            "final_url": robots_final,
            "contains_sitemap_directive": b"sitemap:" in robots_raw.lower(),
            "issues": robots_issues,
        },
        "sitemaps": sitemap_reports,
        "sampled_url_count": len(pages),
        "checked_internal_link_count": len(link_checks),
        "link_check_limit": args.max_link_checks,
        "link_checks": link_checks,
        "issue_counts": dict(sorted(issue_counts.items())),
        "pages": pages,
        "limitations": [
            "Internal-link and duplicate-metadata counts cover only sampled sitemap URLs.",
            "Broken-link checks are same-origin and bounded by --max-link-checks.",
            "Static HTML cannot prove mobile usability, image compression, or client-injected schema.",
            "Core Web Vitals field data and Lighthouse lab diagnostics require separate tools and must not be merged.",
            "Empty alt text can be correct for decorative images; review it in rendered context.",
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
    parser.add_argument("--max-link-checks", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.max_urls < 1 or args.max_link_checks < 0 or args.concurrency < 1:
            raise ValueError("max URLs and concurrency must be positive; max link checks may be zero")
        return cmd_audit(args)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
