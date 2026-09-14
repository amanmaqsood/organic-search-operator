#!/usr/bin/env python3
"""Initialize, validate, and journal Organic Search Operator project state."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SCHEMA_VERSION = 1
STATE_DIR = ".organic-search"
SENSITIVE_KEY = re.compile(r"(?:token|secret|password|api[_-]?key|cookie|credential)", re.I)
IANA_TIMEZONE_SHAPE = re.compile(r"^[A-Za-z_+-]+(?:/[A-Za-z0-9_.+-]+)+$")
POLICY_MODES = ("review_first", "autonomous_safe")
MACHINE_READABLE_FILES = ("llms.txt", "llms-full.txt", "ai.txt")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json_write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def normalize_origin(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("canonical origin must be an absolute HTTPS URL")
    if parsed.path not in ("", "/") or parsed.params or parsed.query or parsed.fragment:
        raise ValueError("canonical origin must not contain a path, query, or fragment")
    return f"https://{parsed.netloc.lower()}"


def validate_landing_url(origin: str, landing_url: str) -> str:
    parsed = urlparse(landing_url.strip())
    expected = urlparse(origin)
    if parsed.scheme != "https" or parsed.netloc.lower() != expected.netloc.lower():
        raise ValueError("primary landing URL must be HTTPS and use the canonical origin")
    if parsed.query or parsed.fragment:
        raise ValueError("primary landing URL must not contain a query or fragment")
    path = parsed.path or "/"
    return f"{origin}{path}"


def valid_timezone_name(value: str) -> bool:
    if value == "UTC":
        return True
    try:
        ZoneInfo(value)
        return True
    except ZoneInfoNotFoundError:
        # Windows Python often ships without the optional tzdata package. Keep
        # the helper dependency-free while rejecting offsets and arbitrary text.
        return bool(IANA_TIMEZONE_SHAPE.fullmatch(value))


def split_values(values: list[str] | None, fallback: list[str]) -> list[str]:
    if not values:
        return fallback
    result: list[str] = []
    for value in values:
        for item in value.split(","):
            item = item.strip()
            if item and item not in result:
                result.append(item)
    return result or fallback


def state_paths(project: Path) -> dict[str, Path]:
    root = project.resolve() / STATE_DIR
    return {
        "root": root,
        "config": root / "config.json",
        "state": root / "state.json",
        "runs": root / "runs.jsonl",
        "experiments": root / "experiments.jsonl",
        "gitignore": root / ".gitignore",
    }


def recent_intelligence_defaults() -> dict:
    return {
        "provider": "last30days",
        "required_each_cycle": True,
        "max_age_hours": 24,
        "agent_mode": True,
        "failure_behavior": "maintenance_only",
    }


def autonomy_defaults() -> dict:
    return {
        "max_actions_per_daily_cycle": 1,
        "max_new_pages_per_daily_cycle": 1,
        "require_clean_worktree": True,
        "require_green_checks": True,
        "require_known_deployment_route": True,
        "require_rollback_path": True,
        "rollback_on_live_verification_failure": True,
    }


def machine_readable_defaults() -> dict:
    return {
        "create_on_first_run": True,
        "update_when_source_changes": True,
        "required_files": list(MACHINE_READABLE_FILES),
        "manifest_path": ".organic-search/machine-readable.json",
        "output_directory": "detect",
        "max_full_bytes": 1_000_000,
        "ai_txt_status": "experimental_nonstandard",
    }


def ai_visibility_defaults() -> dict:
    return {
        "monitor_daily": True,
        "decision_cadence": "weekly",
        "comparison_window_days": 28,
        "google_genai_report": "auto_if_available",
        "bing_ai_performance": "auto_if_available",
        "chatgpt_referrals": "auto_if_available",
        "sampled_prompts": "observational",
    }


def valid_project_relative_path(value: object, allow_detect: bool = False) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if allow_detect and value == "detect":
        return True
    candidate = Path(value)
    return not candidate.is_absolute() and ".." not in candidate.parts


def initial_config(args: argparse.Namespace) -> dict:
    origin = normalize_origin(args.origin)
    landing_url = validate_landing_url(origin, args.landing_url)
    if not valid_timezone_name(args.timezone):
        raise ValueError(f"timezone must be UTC or an IANA-style name: {args.timezone}")

    return {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "brand": args.brand.strip(),
            "canonical_origin": origin,
            "primary_landing_url": landing_url,
            "conversion_event": args.conversion_event.strip(),
            "timezone": args.timezone,
            "markets": split_values(args.market, ["project-defined"]),
            "languages": split_values(args.language, ["en"]),
            "regulated_topics": split_values(args.regulated_topic, []),
        },
        "site": {
            "content_source": "detect",
            "build_command": "detect",
            "validation_commands": [],
            "deployment_branch": "detect",
        },
        "search_console": {
            "property": "",
            "sitemap_url": f"{origin}/sitemap.xml",
        },
        "indexnow": {
            "enabled_after_approval": False,
            "key_location": "",
        },
        "machine_readable": machine_readable_defaults(),
        "ai_visibility": ai_visibility_defaults(),
        "automation": {
            "daily_local_time": "07:00",
            "weekly_day": "Monday",
            "monthly_day": 1,
            "max_opportunities_per_cycle": 10,
            "max_drafts_per_weekly_cycle": 2,
            "quiet_when_unchanged": True,
            "recent_intelligence": recent_intelligence_defaults(),
            "autonomy": autonomy_defaults(),
        },
        "policy": {
            "mode": "review_first",
            "backlink_discovery": False,
            "require_human_review_for_sensitive_topics": True,
            "preferred_prose_skill": "prose-humanizer",
        },
    }


def initial_state() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": utc_now(),
        "last_run": None,
        "baselines": {},
        "queue": [],
        "provider_state": {
            "google_search_console": {"status": "unconfigured"},
            "google_genai": {"status": "unconfigured"},
            "indexnow": {"status": "unconfigured"},
            "bing_webmaster": {"status": "optional"},
            "bing_ai_performance": {"status": "optional"},
            "chatgpt_referrals": {"status": "optional"},
            "sampled_prompts": {"status": "optional"},
        },
    }


def cmd_init(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    if not project.is_dir():
        raise ValueError(f"project directory does not exist: {project}")
    paths = state_paths(project)
    if paths["config"].exists() and not args.force:
        raise ValueError(f"configuration already exists: {paths['config']}")

    config = initial_config(args)
    paths["root"].mkdir(parents=True, exist_ok=True)
    atomic_json_write(paths["config"], config)
    if not paths["state"].exists():
        atomic_json_write(paths["state"], initial_state())
    for journal in (paths["runs"], paths["experiments"]):
        journal.touch(exist_ok=True)
    if not paths["gitignore"].exists():
        paths["gitignore"].write_text("cache/\ntmp/\n*.token\n*.credentials.json\n", encoding="utf-8")

    print(json.dumps({"status": "initialized", "directory": str(paths["root"])}, indent=2))
    return 0


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def walk_keys(value: object, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            dotted = f"{prefix}.{key}" if prefix else str(key)
            if SENSITIVE_KEY.search(str(key)):
                found.append(dotted)
            found.extend(walk_keys(nested, dotted))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(walk_keys(nested, f"{prefix}[{index}]"))
    return found


def validate_project(project: Path) -> list[str]:
    paths = state_paths(project)
    errors: list[str] = []
    try:
        config = load_json(paths["config"])
    except ValueError as exc:
        return [str(exc)]
    try:
        state = load_json(paths["state"])
    except ValueError as exc:
        errors.append(str(exc))
        state = {}

    if config.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"config schema_version must be {SCHEMA_VERSION}")
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"state schema_version must be {SCHEMA_VERSION}")

    project_config = config.get("project")
    if not isinstance(project_config, dict):
        errors.append("project must be an object")
        project_config = {}
    for field in ("brand", "canonical_origin", "primary_landing_url", "conversion_event", "timezone"):
        if not isinstance(project_config.get(field), str) or not project_config.get(field, "").strip():
            errors.append(f"project.{field} must be a non-empty string")

    origin = project_config.get("canonical_origin", "")
    landing = project_config.get("primary_landing_url", "")
    try:
        normalized = normalize_origin(origin)
        if normalized != origin:
            errors.append("project.canonical_origin is not normalized")
        if validate_landing_url(normalized, landing) != landing:
            errors.append("project.primary_landing_url is not normalized")
    except ValueError as exc:
        errors.append(str(exc))

    tz_name = project_config.get("timezone", "")
    if not valid_timezone_name(tz_name):
        errors.append(f"project.timezone must be UTC or an IANA-style name: {tz_name}")

    automation = config.get("automation", {})
    max_opportunities = automation.get("max_opportunities_per_cycle")
    max_drafts = automation.get("max_drafts_per_weekly_cycle")
    if not isinstance(max_opportunities, int) or not 5 <= max_opportunities <= 10:
        errors.append("automation.max_opportunities_per_cycle must be between 5 and 10")
    if not isinstance(max_drafts, int) or not 0 <= max_drafts <= 2:
        errors.append("automation.max_drafts_per_weekly_cycle must be between 0 and 2")

    policy = config.get("policy", {})
    mode = policy.get("mode")
    if mode not in POLICY_MODES:
        errors.append("policy.mode must be review_first or autonomous_safe")

    recent = automation.get("recent_intelligence")
    autonomy = automation.get("autonomy")
    if recent is not None:
        if not isinstance(recent, dict):
            errors.append("automation.recent_intelligence must be an object")
        else:
            if recent.get("provider") != "last30days":
                errors.append("automation.recent_intelligence.provider must be last30days")
            if recent.get("required_each_cycle") is not True:
                errors.append("automation.recent_intelligence.required_each_cycle must be true")
            if recent.get("max_age_hours") != 24:
                errors.append("automation.recent_intelligence.max_age_hours must be 24")
            if recent.get("agent_mode") is not True:
                errors.append("automation.recent_intelligence.agent_mode must be true")
            if recent.get("failure_behavior") != "maintenance_only":
                errors.append("automation.recent_intelligence.failure_behavior must be maintenance_only")
    if autonomy is not None:
        if not isinstance(autonomy, dict):
            errors.append("automation.autonomy must be an object")
        else:
            if autonomy.get("max_actions_per_daily_cycle") != 1:
                errors.append("automation.autonomy.max_actions_per_daily_cycle must be 1")
            if autonomy.get("max_new_pages_per_daily_cycle") != 1:
                errors.append("automation.autonomy.max_new_pages_per_daily_cycle must be 1")
            for field in (
                "require_clean_worktree",
                "require_green_checks",
                "require_known_deployment_route",
                "require_rollback_path",
                "rollback_on_live_verification_failure",
            ):
                if autonomy.get(field) is not True:
                    errors.append(f"automation.autonomy.{field} must be true")
    if mode == "autonomous_safe":
        if not isinstance(recent, dict):
            errors.append("autonomous_safe requires automation.recent_intelligence")
        if not isinstance(autonomy, dict):
            errors.append("autonomous_safe requires automation.autonomy")
        if policy.get("require_human_review_for_sensitive_topics") is not True:
            errors.append("autonomous_safe requires human review for sensitive topics")

    machine = config.get("machine_readable")
    if machine is not None:
        if not isinstance(machine, dict):
            errors.append("machine_readable must be an object")
        else:
            if machine.get("create_on_first_run") is not True:
                errors.append("machine_readable.create_on_first_run must be true")
            if machine.get("update_when_source_changes") is not True:
                errors.append("machine_readable.update_when_source_changes must be true")
            if machine.get("required_files") != list(MACHINE_READABLE_FILES):
                errors.append("machine_readable.required_files must contain llms.txt, llms-full.txt, and ai.txt")
            if not valid_project_relative_path(machine.get("manifest_path")):
                errors.append("machine_readable.manifest_path must stay inside the project")
            if not valid_project_relative_path(machine.get("output_directory"), allow_detect=True):
                errors.append("machine_readable.output_directory must be detect or stay inside the project")
            max_full_bytes = machine.get("max_full_bytes")
            if not isinstance(max_full_bytes, int) or not 10_000 <= max_full_bytes <= 5_000_000:
                errors.append("machine_readable.max_full_bytes must be between 10000 and 5000000")
            if machine.get("ai_txt_status") != "experimental_nonstandard":
                errors.append("machine_readable.ai_txt_status must be experimental_nonstandard")

    ai_visibility = config.get("ai_visibility")
    if ai_visibility is not None:
        if not isinstance(ai_visibility, dict):
            errors.append("ai_visibility must be an object")
        else:
            if ai_visibility.get("monitor_daily") is not True:
                errors.append("ai_visibility.monitor_daily must be true")
            if ai_visibility.get("decision_cadence") != "weekly":
                errors.append("ai_visibility.decision_cadence must be weekly")
            comparison_days = ai_visibility.get("comparison_window_days")
            if not isinstance(comparison_days, int) or not 7 <= comparison_days <= 90:
                errors.append("ai_visibility.comparison_window_days must be between 7 and 90")
            for field in (
                "google_genai_report",
                "bing_ai_performance",
                "chatgpt_referrals",
            ):
                if ai_visibility.get(field) != "auto_if_available":
                    errors.append(f"ai_visibility.{field} must be auto_if_available")
            if ai_visibility.get("sampled_prompts") != "observational":
                errors.append("ai_visibility.sampled_prompts must be observational")

    gsc_property = config.get("search_console", {}).get("property", "")
    if gsc_property and not (
        gsc_property.startswith("sc-domain:")
        or gsc_property.startswith("https://")
        or gsc_property.startswith("http://")
    ):
        errors.append("search_console.property has an invalid property identifier")

    sensitive = walk_keys(config)
    if sensitive:
        errors.append("configuration contains prohibited secret-like keys: " + ", ".join(sensitive))
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    errors = validate_project(project)
    output = {"status": "valid" if not errors else "invalid", "errors": errors}
    print(json.dumps(output, indent=2))
    return 0 if not errors else 2


def cmd_status(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    paths = state_paths(project)
    errors = validate_project(project)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, indent=2))
        return 2
    config = load_json(paths["config"])
    state = load_json(paths["state"])
    summary = {
        "status": "ready",
        "brand": config["project"]["brand"],
        "origin": config["project"]["canonical_origin"],
        "primary_landing_url": config["project"]["primary_landing_url"],
        "policy_mode": config["policy"]["mode"],
        "recent_intelligence": config.get("automation", {}).get(
            "recent_intelligence", recent_intelligence_defaults()
        ),
        "machine_readable": config.get("machine_readable", machine_readable_defaults()),
        "ai_visibility": config.get("ai_visibility", ai_visibility_defaults()),
        "gsc_property": config["search_console"]["property"] or "unconfigured",
        "indexnow": state.get("provider_state", {}).get("indexnow", {}).get("status", "unknown"),
        "queue_size": len(state.get("queue", [])),
        "last_run": state.get("last_run"),
    }
    print(json.dumps(summary, indent=2))
    return 0


def cmd_set_mode(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    paths = state_paths(project)
    errors = validate_project(project)
    if errors:
        raise ValueError("project validation failed: " + "; ".join(errors))
    config = load_json(paths["config"])
    automation = config.setdefault("automation", {})
    automation.setdefault("recent_intelligence", recent_intelligence_defaults())
    automation.setdefault("autonomy", autonomy_defaults())
    policy = config.setdefault("policy", {})
    policy["mode"] = args.mode
    if args.mode == "autonomous_safe":
        policy["require_human_review_for_sensitive_topics"] = True
    atomic_json_write(paths["config"], config)
    post_errors = validate_project(project)
    if post_errors:
        raise ValueError("updated project validation failed: " + "; ".join(post_errors))
    print(
        json.dumps(
            {
                "status": "updated",
                "mode": args.mode,
                "action_budget": automation["autonomy"]["max_actions_per_daily_cycle"],
            },
            indent=2,
        )
    )
    return 0


def cmd_configure_machine_readable(args: argparse.Namespace) -> int:
    project = Path(args.project).resolve()
    paths = state_paths(project)
    errors = validate_project(project)
    if errors:
        raise ValueError("project validation failed: " + "; ".join(errors))
    if not valid_project_relative_path(args.output_directory):
        raise ValueError("output directory must stay inside the project")
    if not valid_project_relative_path(args.manifest_path):
        raise ValueError("manifest path must stay inside the project")
    if not 10_000 <= args.max_full_bytes <= 5_000_000:
        raise ValueError("max full bytes must be between 10000 and 5000000")

    config = load_json(paths["config"])
    settings = machine_readable_defaults()
    settings["output_directory"] = args.output_directory
    settings["manifest_path"] = args.manifest_path
    settings["max_full_bytes"] = args.max_full_bytes
    config["machine_readable"] = settings
    atomic_json_write(paths["config"], config)
    post_errors = validate_project(project)
    if post_errors:
        raise ValueError("updated project validation failed: " + "; ".join(post_errors))
    print(
        json.dumps(
            {
                "status": "updated",
                "output_directory": args.output_directory,
                "manifest_path": args.manifest_path,
                "required_files": list(MACHINE_READABLE_FILES),
            },
            indent=2,
        )
    )
    return 0


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def cmd_record(args: argparse.Namespace, kind: str) -> int:
    project = Path(args.project).resolve()
    paths = state_paths(project)
    errors = validate_project(project)
    if errors:
        raise ValueError("project validation failed: " + "; ".join(errors))
    record = load_json(Path(args.file).resolve())
    record.setdefault("recorded_at", utc_now())
    if kind == "run":
        if not record.get("run_id") or not record.get("kind"):
            raise ValueError("run record requires run_id and kind")
        append_jsonl(paths["runs"], record)
        state = load_json(paths["state"])
        state["last_run"] = {
            "run_id": record["run_id"],
            "kind": record["kind"],
            "recorded_at": record["recorded_at"],
            "status": record.get("status", "unknown"),
        }
        atomic_json_write(paths["state"], state)
    else:
        if not record.get("experiment_id") or not record.get("claim"):
            raise ValueError("experiment record requires experiment_id and claim")
        append_jsonl(paths["experiments"], record)
    print(json.dumps({"status": "recorded", "type": kind}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="initialize project configuration and state")
    init.add_argument("--project", required=True)
    init.add_argument("--brand", required=True)
    init.add_argument("--origin", required=True)
    init.add_argument("--landing-url", required=True)
    init.add_argument("--conversion-event", required=True)
    init.add_argument("--timezone", default="UTC")
    init.add_argument("--market", action="append")
    init.add_argument("--language", action="append")
    init.add_argument("--regulated-topic", action="append")
    init.add_argument("--force", action="store_true", help="replace config only; preserve state and journals")
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="validate project configuration and state")
    validate.add_argument("--project", required=True)
    validate.set_defaults(func=cmd_validate)

    status = sub.add_parser("status", help="show a secret-free project summary")
    status.add_argument("--project", required=True)
    status.set_defaults(func=cmd_status)

    set_mode = sub.add_parser("set-mode", help="select review-first or bounded autonomous operation")
    set_mode.add_argument("--project", required=True)
    set_mode.add_argument("--mode", required=True, choices=POLICY_MODES)
    set_mode.set_defaults(func=cmd_set_mode)

    machine = sub.add_parser(
        "configure-machine-readable",
        help="configure first-run generation of llms.txt, llms-full.txt, and ai.txt",
    )
    machine.add_argument("--project", required=True)
    machine.add_argument("--output-directory", required=True)
    machine.add_argument(
        "--manifest-path",
        default=".organic-search/machine-readable.json",
    )
    machine.add_argument("--max-full-bytes", type=int, default=1_000_000)
    machine.set_defaults(func=cmd_configure_machine_readable)

    record_run = sub.add_parser("record-run", help="append a run record and update current state")
    record_run.add_argument("--project", required=True)
    record_run.add_argument("--file", required=True)
    record_run.set_defaults(func=lambda args: cmd_record(args, "run"))

    record_experiment = sub.add_parser("record-experiment", help="append a practitioner or project experiment")
    record_experiment.add_argument("--project", required=True)
    record_experiment.add_argument("--file", required=True)
    record_experiment.set_defaults(func=lambda args: cmd_record(args, "experiment"))
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
