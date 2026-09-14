# Project contract

Use `.organic-search/` as the portable project state directory.

## Files

- `config.json`: public project configuration and detected adapters.
- `state.json`: current baselines, content queue, provider state, and latest run.
- `runs.jsonl`: append-only run records.
- `experiments.jsonl`: append-only practitioner and project experiments.
- `machine-readable.json`: reviewed public canonical content manifest used to
  generate the three origin-root discovery files.
- `machine-readable-state.json`: generator ownership and content hashes.
- `cache/`: replaceable provider responses. Do not commit by default.

Never store access tokens, cookies, OAuth client secrets, Bing API keys, or DNS
credentials in these files.

## Required configuration

- schema version
- brand
- canonical HTTPS origin
- primary landing URL on that origin
- conversion event
- IANA timezone
- primary markets and languages
- regulated-topic classification
- content source of truth
- build and validation commands when detected
- GSC property when confirmed
- sitemap URL when confirmed
- IndexNow key location when deployed
- first-run machine-readable generation policy, manifest path, detected public
  source directory, size limit, and experimental `ai.txt` status
- AI-visibility daily monitoring, weekly decision cadence, comparison window,
  and provider availability policy
- recent intelligence provider, 24-hour freshness rule, and failure behavior
- policy mode and one-action autonomous budget

`scripts/seo_operator.py init` creates a conservative review-first starter. The
user or agent must replace placeholders before provider mutations or publishing.
Use `seo_operator.py set-mode --mode autonomous_safe` only after the project has
a known deployment route, validation commands, and rollback path.

## Content states

Use these states:

`candidate -> planned -> drafting -> ready_for_review -> approved -> published`

`blocked`, `rejected`, and `failed` may be entered from any non-published state.
In `review_first`, only user approval moves `ready_for_review` to `approved`. In
`autonomous_safe`, a work item may make that transition when every mutation-
envelope gate passes; record the authorization source as
`autonomous_safe_policy`. A successful live verification moves `approved` to
`published`.

Preserve prior state and append transitions to a run record. Do not silently
reopen rejected topics or reuse a published intent for a new URL.

## Idempotency

- Normalize canonical origins and URLs before comparison.
- Use URL plus intent as a work-item identity.
- Use date plus run kind as a run identity.
- Do not resubmit unchanged sitemaps on every run.
- Notify IndexNow only for canonical URLs changed since the last successful
  notification.
- Regenerate machine-readable files only when their normalized public source
  manifest changes. Refuse to overwrite an unmanaged or manually diverged file.
