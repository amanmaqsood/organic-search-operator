#!/usr/bin/env python3
"""Generate and verify llms.txt, llms-full.txt, and ai.txt from public content."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


STATE_DIRECTORY = ".organic-search"
OUTPUT_NAMES = ("llms.txt", "llms-full.txt", "ai.txt")
DEFAULT_MAX_FULL_BYTES = 1_000_000


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def atomic_text_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_json_write(path: Path, value: dict) -> None:
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    atomic_text_write(path, encoded)


def load_json_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def normalize_origin(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("site.origin must be an absolute HTTPS origin")
    if parsed.path not in ("", "/") or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("site.origin must not contain a path, query, or fragment")
    return f"https://{parsed.netloc.lower()}"


def validate_same_origin_url(value: str, origin: str, field: str) -> str:
    parsed = urlparse(value.strip())
    expected = urlparse(origin)
    if parsed.scheme != "https" or parsed.netloc.lower() != expected.netloc.lower():
        raise ValueError(f"{field} must be HTTPS and use site.origin")
    if parsed.params or parsed.query or parsed.fragment:
        raise ValueError(f"{field} must not contain parameters, a query, or a fragment")
    return f"{origin}{parsed.path or '/'}"


def single_line(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    normalized = " ".join(value.split())
    if any(character in normalized for character in ("\x00", "\r", "\n")):
        raise ValueError(f"{field} must be a single line")
    return normalized


def safe_relative_path(value: object, field: str) -> Path:
    text = single_line(value, field)
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must stay inside the project")
    return path


def validate_manifest(value: dict) -> dict:
    if value.get("schema_version") != 1:
        raise ValueError("manifest schema_version must be 1")
    raw_site = value.get("site")
    if not isinstance(raw_site, dict):
        raise ValueError("manifest site must be an object")

    origin = normalize_origin(single_line(raw_site.get("origin"), "site.origin"))
    updated = single_line(raw_site.get("last_updated"), "site.last_updated")
    try:
        date.fromisoformat(updated)
    except ValueError as exc:
        raise ValueError("site.last_updated must use YYYY-MM-DD") from exc

    site = {
        "name": single_line(raw_site.get("name"), "site.name"),
        "origin": origin,
        "summary": single_line(raw_site.get("summary"), "site.summary"),
        "last_updated": updated,
        "robots_url": validate_same_origin_url(
            single_line(raw_site.get("robots_url"), "site.robots_url"), origin, "site.robots_url"
        ),
        "sitemap_url": validate_same_origin_url(
            single_line(raw_site.get("sitemap_url"), "site.sitemap_url"), origin, "site.sitemap_url"
        ),
    }
    for optional in ("contact_url", "terms_url", "privacy_url"):
        if raw_site.get(optional):
            site[optional] = validate_same_origin_url(
                single_line(raw_site[optional], f"site.{optional}"), origin, f"site.{optional}"
            )

    raw_sections = value.get("sections")
    if not isinstance(raw_sections, list) or not raw_sections:
        raise ValueError("manifest sections must be a non-empty array")

    sections: list[dict] = []
    seen_urls: set[str] = set()
    page_count = 0
    for section_index, raw_section in enumerate(raw_sections):
        if not isinstance(raw_section, dict):
            raise ValueError(f"sections[{section_index}] must be an object")
        section_name = single_line(raw_section.get("name"), f"sections[{section_index}].name")
        raw_pages = raw_section.get("pages")
        if not isinstance(raw_pages, list) or not raw_pages:
            raise ValueError(f"sections[{section_index}].pages must be a non-empty array")
        pages: list[dict] = []
        for page_index, raw_page in enumerate(raw_pages):
            prefix = f"sections[{section_index}].pages[{page_index}]"
            if not isinstance(raw_page, dict):
                raise ValueError(f"{prefix} must be an object")
            for flag in ("public", "canonical", "indexable"):
                if raw_page.get(flag) is not True:
                    raise ValueError(f"{prefix}.{flag} must be true")
            url = validate_same_origin_url(
                single_line(raw_page.get("url"), f"{prefix}.url"), origin, f"{prefix}.url"
            )
            if url in seen_urls:
                raise ValueError(f"duplicate canonical page URL: {url}")
            seen_urls.add(url)
            content = raw_page.get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError(f"{prefix}.content must contain public Markdown text")
            if "\x00" in content:
                raise ValueError(f"{prefix}.content contains a null byte")
            pages.append(
                {
                    "title": single_line(raw_page.get("title"), f"{prefix}.title"),
                    "url": url,
                    "description": single_line(
                        raw_page.get("description"), f"{prefix}.description"
                    ),
                    "content": content.strip(),
                    "public": True,
                    "canonical": True,
                    "indexable": True,
                }
            )
            page_count += 1
        sections.append({"name": section_name, "pages": pages})

    if page_count > 5_000:
        raise ValueError("manifest may contain at most 5000 pages")
    return {"schema_version": 1, "site": site, "sections": sections}


def render_llms(manifest: dict) -> str:
    site = manifest["site"]
    lines = [
        f"# {site['name']}",
        "",
        f"> {site['summary']}",
        "",
        f"Canonical origin: {site['origin']}",
        f"Content last updated: {site['last_updated']}",
        "",
        "## Machine-readable resources",
        "",
        f"- [Full public content]({site['origin']}/llms-full.txt): Extended Markdown corpus.",
        f"- [Sitemap]({site['sitemap_url']}): Canonical URL discovery.",
        f"- [Robots policy]({site['robots_url']}): Crawler access rules.",
    ]
    for section in manifest["sections"]:
        lines.extend(["", f"## {section['name']}", ""])
        for page in section["pages"]:
            lines.append(f"- [{page['title']}]({page['url']}): {page['description']}")
    return "\n".join(lines).rstrip() + "\n"


def render_llms_full(manifest: dict) -> str:
    site = manifest["site"]
    lines = [
        f"# {site['name']} — Full public content",
        "",
        f"> {site['summary']}",
        "",
        f"Canonical origin: {site['origin']}",
        f"Content last updated: {site['last_updated']}",
        "",
        "This generated file mirrors selected public, canonical, indexable content. The linked",
        "canonical HTML pages remain authoritative when wording or dates differ.",
    ]
    for section in manifest["sections"]:
        lines.extend(["", f"## {section['name']}"])
        for page in section["pages"]:
            lines.extend(
                [
                    "",
                    f"### {page['title']}",
                    "",
                    f"Canonical URL: {page['url']}",
                    "",
                    page["description"],
                    "",
                    page["content"],
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def render_ai(manifest: dict) -> str:
    site = manifest["site"]
    lines = [
        f"# {site['name']} AI discovery information",
        "",
        "> Experimental publisher-authored discovery file. This is not a universal standard or a ranking signal.",
        "",
        f"Canonical-Origin: {site['origin']}",
        f"Content-Last-Updated: {site['last_updated']}",
        f"Robots-Policy: {site['robots_url']}",
        f"Sitemap: {site['sitemap_url']}",
        f"LLMS-Index: {site['origin']}/llms.txt",
        f"LLMS-Full: {site['origin']}/llms-full.txt",
        "",
        "## Purpose",
        "",
        site["summary"],
        "",
        "## Authoritative public pages",
        "",
    ]
    for section in manifest["sections"]:
        for page in section["pages"]:
            lines.append(f"- [{page['title']}]({page['url']}): {page['description']}")
    lines.extend(
        [
            "",
            "## Accuracy and permissions",
            "",
            "- Prefer the canonical HTML page when this file and a page differ.",
            "- Follow robots.txt, page-level robots directives, terms, and applicable law.",
            "- Do not infer endorsements, guarantees, affiliations, or permissions not stated on a canonical page.",
            "- This file does not grant training, copyright, licensing, or reuse permission.",
        ]
    )
    for label, key in (("Contact", "contact_url"), ("Terms", "terms_url"), ("Privacy", "privacy_url")):
        if key in site:
            lines.append(f"- {label}: {site[key]}")
    return "\n".join(lines).rstrip() + "\n"


def render_outputs(manifest: dict, max_full_bytes: int = DEFAULT_MAX_FULL_BYTES) -> dict[str, str]:
    normalized = validate_manifest(manifest)
    outputs = {
        "llms.txt": render_llms(normalized),
        "llms-full.txt": render_llms_full(normalized),
        "ai.txt": render_ai(normalized),
    }
    full_size = len(outputs["llms-full.txt"].encode("utf-8"))
    if full_size > max_full_bytes:
        raise ValueError(
            f"llms-full.txt would be {full_size} bytes, above the configured {max_full_bytes}-byte limit"
        )
    return outputs


def resolve_inside(project: Path, relative: Path, field: str) -> Path:
    resolved = (project / relative).resolve()
    try:
        resolved.relative_to(project)
    except ValueError as exc:
        raise ValueError(f"{field} must stay inside the project") from exc
    return resolved


def project_settings(project: Path) -> tuple[Path, Path, int]:
    config = load_json_object(project / STATE_DIRECTORY / "config.json")
    settings = config.get("machine_readable")
    if not isinstance(settings, dict):
        raise ValueError("config.machine_readable is missing; configure it before generation")
    output_value = settings.get("output_directory")
    if output_value == "detect":
        raise ValueError("config.machine_readable.output_directory must be resolved before generation")
    output_dir = resolve_inside(
        project,
        safe_relative_path(output_value, "machine_readable.output_directory"),
        "machine_readable.output_directory",
    )
    manifest_path = resolve_inside(
        project,
        safe_relative_path(settings.get("manifest_path"), "machine_readable.manifest_path"),
        "machine_readable.manifest_path",
    )
    max_bytes = settings.get("max_full_bytes", DEFAULT_MAX_FULL_BYTES)
    if not isinstance(max_bytes, int) or not 10_000 <= max_bytes <= 5_000_000:
        raise ValueError("machine_readable.max_full_bytes must be between 10000 and 5000000")
    return manifest_path, output_dir, max_bytes


def output_plan(project: Path) -> tuple[dict[str, str], dict, Path, Path]:
    manifest_path, output_dir, max_bytes = project_settings(project)
    raw_manifest = load_json_object(manifest_path)
    normalized_manifest = validate_manifest(raw_manifest)
    outputs = render_outputs(normalized_manifest, max_bytes)
    state_path = project / STATE_DIRECTORY / "machine-readable-state.json"
    state = load_json_object(state_path) if state_path.exists() else {}
    return outputs, normalized_manifest, output_dir, state_path


def inspect_changes(project: Path) -> dict:
    outputs, manifest, output_dir, state_path = output_plan(project)
    previous_state = load_json_object(state_path) if state_path.exists() else {}
    previous_outputs = previous_state.get("outputs", {})
    changed: list[str] = []
    unchanged: list[str] = []
    conflicts: list[str] = []

    for name, expected in outputs.items():
        target = output_dir / name
        expected_hash = digest_text(expected)
        if not target.exists():
            changed.append(name)
            continue
        current_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        if current_hash == expected_hash:
            unchanged.append(name)
            continue
        prior = previous_outputs.get(name, {}) if isinstance(previous_outputs, dict) else {}
        prior_hash = prior.get("sha256") if isinstance(prior, dict) else None
        if not prior_hash:
            conflicts.append(f"{name}: unmanaged existing file differs")
        elif current_hash != prior_hash:
            conflicts.append(f"{name}: file changed outside the generator")
        else:
            changed.append(name)

    source_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return {
        "outputs": outputs,
        "output_directory": output_dir,
        "state_path": state_path,
        "source_hash": digest_text(source_json),
        "changed": changed,
        "unchanged": unchanged,
        "conflicts": conflicts,
    }


def execute(project: Path, apply: bool) -> dict:
    plan = inspect_changes(project)
    if plan["conflicts"]:
        raise ValueError("; ".join(plan["conflicts"]))

    if apply:
        output_hashes: dict[str, dict[str, str]] = {}
        for name, value in plan["outputs"].items():
            target = plan["output_directory"] / name
            if name in plan["changed"]:
                atomic_text_write(target, value)
            output_hashes[name] = {"sha256": digest_text(value)}
        atomic_json_write(
            plan["state_path"],
            {
                "schema_version": 1,
                "source_hash": plan["source_hash"],
                "updated_at": utc_now(),
                "outputs": output_hashes,
            },
        )

    return {
        "status": "applied" if apply else "planned",
        "changed": plan["changed"],
        "unchanged": plan["unchanged"],
        "output_directory": str(plan["output_directory"]),
        "source_hash": plan["source_hash"],
    }


def cmd_generate(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    print(json.dumps(execute(project, args.apply), indent=2))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    plan = inspect_changes(project)
    current = not plan["changed"] and not plan["conflicts"]
    print(
        json.dumps(
            {
                "status": "current" if current else "stale",
                "changed": plan["changed"],
                "unchanged": plan["unchanged"],
                "conflicts": plan["conflicts"],
            },
            indent=2,
        )
    )
    return 0 if current else 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="plan or write the three discovery files")
    generate.add_argument("--project", required=True)
    generate.add_argument("--apply", action="store_true", help="write missing or generator-owned files")
    generate.set_defaults(func=cmd_generate)

    check = sub.add_parser("check", help="verify the files match the current public manifest")
    check.add_argument("--project", required=True)
    check.set_defaults(func=cmd_check)
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
