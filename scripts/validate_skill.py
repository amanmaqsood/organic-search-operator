#!/usr/bin/env python3
"""Validate package structure, metadata, local links, and public-release hygiene."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "NOTICE.md",
    "CONTEXT.md",
    "agents/openai.yaml",
    "scripts/machine_readable.py",
    "references/machine-readable-discovery.md",
    "examples/machine-readable-manifest.json",
)
PRIVATE_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I),
    re.compile(r"gh[oprsu]_[A-Za-z0-9]{12,}"),
    re.compile(r"(?:access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]+", re.I),
)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid YAML in {path}: {exc}") from exc


def skill_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
    if not match:
        raise ValueError("SKILL.md is missing YAML frontmatter")
    try:
        value = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid SKILL.md frontmatter: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("SKILL.md frontmatter must be an object")
    return value


def local_link_errors(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in LINK_PATTERN.finditer(text):
        destination = match.group(1).strip()
        if destination.startswith(("http://", "https://", "#", "mailto:")):
            continue
        destination = destination.split("#", 1)[0]
        if not destination:
            continue
        target = (path.parent / destination).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(root)} links outside package: {destination}")
            continue
        if not target.exists():
            errors.append(f"{path.relative_to(root)} has missing link: {destination}")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    if errors:
        return errors

    try:
        metadata = skill_frontmatter(root / "SKILL.md")
    except ValueError as exc:
        errors.append(str(exc))
        metadata = {}
    if metadata.get("name") != "organic-search-operator":
        errors.append("SKILL.md name must be organic-search-operator")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("SKILL.md description must be a non-empty string")

    yaml_paths = [root / "agents" / "openai.yaml"]
    yaml_paths.extend((root / ".github").rglob("*.yml"))
    yaml_paths.extend((root / ".github").rglob("*.yaml"))
    for path in yaml_paths:
        try:
            load_yaml(path)
        except ValueError as exc:
            errors.append(str(exc))

    for path in root.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in (".md", ".yaml", ".yml", ".json", ".py", ".txt") or path.name in ("LICENSE", ".gitignore"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                errors.append(f"text file is not UTF-8: {path.relative_to(root)}")
                continue
            if "[" + "TODO" in text or "TODO" + ":" in text:
                errors.append(f"unfinished placeholder in {path.relative_to(root)}")
            for pattern in PRIVATE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"possible private value in {path.relative_to(root)}")
                    break
        if path.suffix.lower() == ".md":
            errors.extend(local_link_errors(path, root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(f"Valid organic-search-operator package: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
