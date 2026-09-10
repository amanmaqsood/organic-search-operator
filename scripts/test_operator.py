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
