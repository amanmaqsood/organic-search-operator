#!/usr/bin/env python3
"""Unit tests for the dependency-free Organic Search Operator helpers."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import gsc_api
import indexnow
import live_site_audit
import machine_readable
import seo_operator


class BootstrapTests(unittest.TestCase):
    def init_args(self, project: str) -> argparse.Namespace:
        return argparse.Namespace(
            project=project,
            brand="Example",
            origin="https://www.example.com/",
            landing_url="https://www.example.com/product",
            conversion_event="signup",
            timezone="UTC",
            market=["United States", "Canada"],
            language=["en"],
            regulated_topic=None,
            force=False,
        )

    def test_init_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                result = seo_operator.cmd_init(self.init_args(directory))
            self.assertEqual(result, 0)
            self.assertEqual(seo_operator.validate_project(Path(directory)), [])
            config = json.loads((Path(directory) / ".organic-search" / "config.json").read_text())
            self.assertEqual(config["project"]["canonical_origin"], "https://www.example.com")
            self.assertEqual(config["automation"]["max_drafts_per_weekly_cycle"], 2)
            self.assertEqual(config["automation"]["recent_intelligence"]["provider"], "last30days")
            self.assertEqual(config["automation"]["autonomy"]["max_actions_per_daily_cycle"], 1)
            self.assertEqual(
                config["machine_readable"]["required_files"],
                ["llms.txt", "llms-full.txt", "ai.txt"],
            )
            self.assertTrue(config["ai_visibility"]["monitor_daily"])
            self.assertEqual(config["ai_visibility"]["decision_cadence"], "weekly")
            self.assertEqual(config["ai_visibility"]["comparison_window_days"], 28)
            self.assertEqual(config["ai_visibility"]["sampled_prompts"], "observational")

    def test_init_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self.init_args(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(args)
            with self.assertRaisesRegex(ValueError, "already exists"):
                with contextlib.redirect_stdout(io.StringIO()):
                    seo_operator.cmd_init(args)

    def test_cross_origin_landing_url_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "canonical origin"):
            seo_operator.validate_landing_url("https://example.com", "https://other.example/page")

    def test_secret_like_config_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            path = Path(directory) / ".organic-search" / "config.json"
            config = json.loads(path.read_text())
            config["search_console"]["access_token"] = "do-not-store"
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = seo_operator.validate_project(Path(directory))
            self.assertTrue(any("prohibited secret-like keys" in item for item in errors))

    def test_set_mode_enables_bounded_autonomy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
                result = seo_operator.cmd_set_mode(
                    argparse.Namespace(project=directory, mode="autonomous_safe")
                )
            self.assertEqual(result, 0)
            config = json.loads((Path(directory) / ".organic-search" / "config.json").read_text())
            self.assertEqual(config["policy"]["mode"], "autonomous_safe")
            self.assertEqual(seo_operator.validate_project(Path(directory)), [])

    def test_autonomous_action_budget_cannot_exceed_one(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            path = Path(directory) / ".organic-search" / "config.json"
            config = json.loads(path.read_text())
            config["automation"]["autonomy"]["max_actions_per_daily_cycle"] = 2
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = seo_operator.validate_project(Path(directory))
            self.assertIn("automation.autonomy.max_actions_per_daily_cycle must be 1", errors)

    def test_recent_intelligence_cannot_be_older_than_24_hours(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            path = Path(directory) / ".organic-search" / "config.json"
            config = json.loads(path.read_text())
            config["automation"]["recent_intelligence"]["max_age_hours"] = 48
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = seo_operator.validate_project(Path(directory))
            self.assertIn("automation.recent_intelligence.max_age_hours must be 24", errors)

    def test_machine_readable_output_cannot_escape_project(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            path = Path(directory) / ".organic-search" / "config.json"
            config = json.loads(path.read_text())
            config["machine_readable"]["output_directory"] = "../outside"
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = seo_operator.validate_project(Path(directory))
            self.assertIn("machine_readable.output_directory must be detect or stay inside the project", errors)

    def test_ai_visibility_rejects_daily_content_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            path = Path(directory) / ".organic-search" / "config.json"
            config = json.loads(path.read_text())
            config["ai_visibility"]["decision_cadence"] = "daily"
            path.write_text(json.dumps(config), encoding="utf-8")
            errors = seo_operator.validate_project(Path(directory))
            self.assertIn("ai_visibility.decision_cadence must be weekly", errors)

    def test_pre_v1_4_config_uses_ai_visibility_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
            root = Path(directory) / ".organic-search"
            config_path = root / "config.json"
            config = json.loads(config_path.read_text())
            del config["ai_visibility"]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            self.assertEqual(seo_operator.validate_project(Path(directory)), [])

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = seo_operator.cmd_status(argparse.Namespace(project=directory))
            self.assertEqual(result, 0)
            status = json.loads(output.getvalue())
            self.assertEqual(status["ai_visibility"], seo_operator.ai_visibility_defaults())

    def test_configure_machine_readable_resolves_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                seo_operator.cmd_init(self.init_args(directory))
                result = seo_operator.cmd_configure_machine_readable(
                    argparse.Namespace(
                        project=directory,
                        output_directory="public",
                        manifest_path=".organic-search/machine-readable.json",
                        max_full_bytes=1_000_000,
                    )
                )
            self.assertEqual(result, 0)
            config = json.loads(
                (Path(directory) / ".organic-search" / "config.json").read_text()
            )
            self.assertEqual(config["machine_readable"]["output_directory"], "public")
            self.assertEqual(seo_operator.validate_project(Path(directory)), [])


class MachineReadableTests(unittest.TestCase):
    def manifest(self) -> dict:
        return {
            "schema_version": 1,
            "site": {
                "name": "Example",
                "origin": "https://example.com",
                "summary": "A useful example product.",
                "last_updated": "2026-09-12",
                "robots_url": "https://example.com/robots.txt",
                "sitemap_url": "https://example.com/sitemap.xml",
            },
            "sections": [
                {
                    "name": "Primary pages",
                    "pages": [
                        {
                            "title": "Example product",
                            "url": "https://example.com/product",
                            "description": "Product details and pricing.",
                            "content": "Example helps teams complete useful work.",
                            "public": True,
                            "canonical": True,
                            "indexable": True,
                        }
                    ],
                }
            ],
        }

    def configured_project(self, directory: str) -> Path:
        project = Path(directory)
        state_dir = project / ".organic-search"
        state_dir.mkdir()
        (state_dir / "config.json").write_text(
            json.dumps(
                {
                    "machine_readable": {
                        "manifest_path": ".organic-search/machine-readable.json",
                        "output_directory": "public",
                        "max_full_bytes": 1_000_000,
                    }
                }
            ),
            encoding="utf-8",
        )
        (state_dir / "machine-readable.json").write_text(
            json.dumps(self.manifest()), encoding="utf-8"
        )
        return project

    def test_renders_all_three_files(self) -> None:
        outputs = machine_readable.render_outputs(self.manifest())
        self.assertEqual(set(outputs), {"llms.txt", "llms-full.txt", "ai.txt"})
        self.assertIn("https://example.com/product", outputs["llms.txt"])
        self.assertIn("Example helps teams", outputs["llms-full.txt"])
        self.assertIn("not a universal standard", outputs["ai.txt"])

    def test_rejects_non_public_or_cross_origin_pages(self) -> None:
        manifest = self.manifest()
        page = manifest["sections"][0]["pages"][0]
        page["public"] = False
        with self.assertRaisesRegex(ValueError, "public must be true"):
            machine_readable.render_outputs(manifest)
        page["public"] = True
        page["url"] = "https://other.example/product"
        with self.assertRaisesRegex(ValueError, "site.origin"):
            machine_readable.render_outputs(manifest)

    def test_apply_is_idempotent_and_protects_manual_edits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.configured_project(directory)
            first = machine_readable.execute(project, apply=True)
            self.assertEqual(set(first["changed"]), {"llms.txt", "llms-full.txt", "ai.txt"})
            second = machine_readable.execute(project, apply=True)
            self.assertEqual(second["changed"], [])

            (project / "public" / "ai.txt").write_text("manual edit\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside the generator"):
                machine_readable.execute(project, apply=True)


class ProviderHelperTests(unittest.TestCase):
    def test_gsc_dimensions(self) -> None:
        self.assertEqual(gsc_api.parse_dimensions("query,page,date"), ["query", "page", "date"])
        with self.assertRaisesRegex(ValueError, "unsupported"):
            gsc_api.parse_dimensions("query,keyword")

    def test_indexnow_rejects_foreign_urls(self) -> None:
        args = argparse.Namespace(url=["https://other.example/page"], urls_file=None)
        with self.assertRaisesRegex(ValueError, "configured host"):
            indexnow.collect_urls(args, "example.com")

    def test_indexnow_accepts_unique_same_host_urls(self) -> None:
        args = argparse.Namespace(
            url=["https://example.com/a", "https://example.com/a", "https://example.com/b"],
            urls_file=None,
        )
        self.assertEqual(indexnow.collect_urls(args, "example.com"), ["https://example.com/a", "https://example.com/b"])


class AuditParserTests(unittest.TestCase):
    def test_page_parser_extracts_core_fields(self) -> None:
        parser = live_site_audit.PageParser()
        parser.feed(
            '<html><head><title>Example</title><meta name="description" content="Useful page">'
            '<link rel="canonical" href="https://example.com/a"><meta property="og:image" content="/a.png">'
            '</head><body><h1>Example</h1><a href="/b">Next</a></body></html>'
        )
        self.assertEqual(parser.title, "Example")
        self.assertEqual(parser.h1_count, 1)
        self.assertEqual(parser.canonical, "https://example.com/a")
        self.assertEqual(parser.links, ["/b"])

    def test_sitemap_parser(self) -> None:
        kind, urls = live_site_audit.xml_locations(
            b'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            b'<url><loc>https://example.com/</loc></url></urlset>'
        )
        self.assertEqual(kind, "urlset")
        self.assertEqual(urls, ["https://example.com/"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
