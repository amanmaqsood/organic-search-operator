# Changelog

All notable changes follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/amanmaqsood/organic-search-operator/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/amanmaqsood/organic-search-operator/releases/tag/v1.0.0
