# Changelog

All notable changes follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.4.0] - 2026-09-14

- Added a provider-specific AI visibility audit for Google generative search,
  Bing AI Performance, ChatGPT referrals, relevant crawlers, and controlled
  prompt observations.
- Added answer-unit quality guidance that favors clear, evidenced sections for
  readers while rejecting artificial micro-chunking and repeated prompt pages.
- Added `PT-19` through `PT-22` to preserve answer variability, separate AI
  visibility metrics, and gate content scale on distinct public value.
- Added a daily-collection and weekly-decision clock with a configurable 28-day
  comparison default to reduce reactions to noisy single observations.
- Added project configuration, provider state, run-record fields, validation,
  examples, and tests for the AI visibility policy.

## [1.3.1] - 2026-09-12

- Added a post-upgrade bootstrap rule so existing projects missing any part of
  the three-file discovery set create it on their next eligible run.

## [1.3.0] - 2026-09-12

- Added first-run generation and change-aware maintenance for `llms.txt`,
  `llms-full.txt`, and experimental `ai.txt`.
- Added a dependency-free generator with dry-run, apply, validation,
  source-hash, idempotency, size-limit, and manual-edit protection.
- Added project configuration and an example public-content manifest for the
  three-file discovery set.
- Added `PT-11` through `PT-18` checks for GSC plus optional Ahrefs evidence,
  programmatic page families, free tools, directories and leaderboards,
  permanent product-page lifecycle, internal graphs, and genuine utility.
- Documented that machine-readable files are not Google ranking signals and
  that `ai.txt` remains experimental and non-standard.

## [1.2.0] - 2026-09-12

- Added `PT-01` through `PT-10` practitioner-derived decision checks to every
  automation cycle.
- Added claim-specificity, comparison, refresh-first, internal-link,
  buyer-question, non-branded measurement, answer-first, buyer-guide,
  situation-page, and responsible-cadence rules.
- Explicitly rejected unsupported performance multiples, position promises,
  link and word-count quotas, and claims about how ChatGPT trains or forgets.
- Added official-guidance links and experiment/report fields for verification
  state and rejected claims.

## [1.1.0] - 2026-09-10

- Added a Last 30 Days recent-intelligence brief to every scheduled cycle, with
  a 24-hour reuse window and maintenance-only fallback on missing coverage.
- Added opt-in `autonomous_safe` mode with a one-action and one-new-page budget.
- Added explicit autonomous mutation, validation, deployment, live verification,
  rollback, sensitive-topic, and prohibited-action gates.
- Added deterministic `set-mode` configuration support and validation tests.
- Added opportunity scoring that favors qualified business impact over raw
  traffic or trend volume.

## [1.0.0] - 2026-09-10

- Added project bootstrap, validation, status, and append-only run records.
- Added token-safe Google Search Console helpers.
- Added dry-run-first sitemap and IndexNow submission workflows.
- Added a read-only sampled live-site audit.
- Added landing-page-first opportunity, editorial, automation, and reporting
  contracts.
- Added practitioner experiment intake and `prose-humanizer` integration.
- Added Codex, Claude Code, and manual installation guidance.

[Unreleased]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/amanmaqsood/organic-search-operator/releases/tag/v1.0.0
