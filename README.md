# Organic Search Operator

[![Validate](https://github.com/amanmaqsood/organic-search-operator/actions/workflows/validate.yml/badge.svg)](https://github.com/amanmaqsood/organic-search-operator/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An evidence-led SEO and GEO agent skill for Codex, Claude Code, and other
Agent Skills-compatible tools. It bootstraps a website project, audits technical
and content health, mines Google Search Console opportunities, prepares
reviewable improvements, notifies Bing through IndexNow, and maintains a quiet
recurring improvement loop.

It does not promise rankings, force indexing, mass-publish low-value articles,
or push production changes without approval.

## Explain it like I am ten

This skill is like a careful gardener for your website. First, it checks whether
Google and Bing can find the site and whether anything is broken. Then it looks
at which pages people already visit, finds good chances to improve them, and
suggests useful new pages that connect to your main product page. It can prepare
better words, links, titles, and technical fixes, but it asks before publishing
important changes. Every day it checks whether the website is improving, keeps
notes about what worked, and stops making new pages if the results get worse.

## What it does

- Creates a portable `.organic-search/` project configuration and run history.
- Audits repository, deployment, crawling, canonicals, sitemaps, metadata,
  structured data, internal links, and sampled live URLs.
- Connects to Google Search Console through an existing connector or gcloud ADC.
- Collects performance views by query, page, date, country, and device.
- Finds rank 5 to 20 refresh opportunities, weak-CTR pages, declines, content
  gaps, orphan pages, and cannibalization risks.
- Centers the plan on one conversion landing page and its supporting cluster.
- Finds 5 to 10 opportunities per cycle, without turning them into a publishing
  quota.
- Produces no more than two reviewable drafts in a weekly cycle, and may produce
  none when the evidence or quality is weak.
- Uses `$prose-humanizer` when available, with an integrity-first fallback.
- Inspects selected GSC URL states and submits approved sitemaps.
- Notifies Bing and other participating engines through IndexNow after verified
  production changes.
- Tracks practitioner tips as experiments instead of blindly applying them.
- Supports a quiet daily monitor, weekly work plan, and monthly full audit.

## SEO and GEO

SEO work improves discovery and performance in search engines. GEO work makes
important facts, entities, evidence, and answers easier for AI-assisted search
systems to understand and cite. This skill treats both as evidence and content
quality work. It does not claim that an AI system will mention a brand or that a
search engine will index a submitted URL.

Read [GEO and entity guidance](references/geo-and-entity.md) for the specific
checks and measurements.

## Requirements

- An agent that supports the Agent Skills format.
- Python 3.10 or newer for the bundled helper scripts.
- Node.js only if you install through the `skills` CLI.
- Google Cloud CLI for the optional direct Search Console script path.
- Ownership or approved access to any site, Search Console property, DNS zone,
  or repository you ask the skill to change.

The core skill has no Python package dependencies. CI installs PyYAML only for
repository metadata validation.

## Install

The [`skills` CLI](https://github.com/vercel-labs/skills) supports Codex, Claude
Code, and many other agents.

### Interactive installation

```bash
npx skills add amanmaqsood/organic-search-operator
```

Choose the agent and project or global scope when prompted.

### Codex

Install globally for Codex:

```bash
npx skills add amanmaqsood/organic-search-operator -g -a codex
```

### Claude Code

Install globally for Claude Code:

```bash
npx skills add amanmaqsood/organic-search-operator -g -a claude-code
```

### Codex and Claude Code together

```bash
npx skills add amanmaqsood/organic-search-operator -g -a codex -a claude-code
```

### Project-only installation

Remove `-g` to install only for the current project:

```bash
npx skills add amanmaqsood/organic-search-operator -a codex
```

### Update

```bash
npx skills update organic-search-operator -g -y
```

If an agent-specific link is not created correctly by the CLI, use its
interactive installer or copy this repository manually to one of these paths:

| Agent | Global path | Project path |
| --- | --- | --- |
| Codex | `~/.codex/skills/organic-search-operator/` | `.agents/skills/organic-search-operator/` |
| Claude Code | `~/.claude/skills/organic-search-operator/` | `.claude/skills/organic-search-operator/` |
| Generic Agent Skills | `~/.agents/skills/organic-search-operator/` | `.agents/skills/organic-search-operator/` |

Restart or reload the agent after a manual installation.

## Use it from your agent

Invoke the skill explicitly:

```text
Use $organic-search-operator to bootstrap this website project for
https://www.example.com and improve the /product landing page for qualified
signups.
```

Other useful prompts:

```text
Use $organic-search-operator to audit this repository and production site. Give
me the highest-confidence fixes and do not change files.
```

```text
Use $organic-search-operator to connect the confirmed Search Console property,
find rank 5 to 20 opportunities, and prepare a reviewable refresh.
```

```text
Use $organic-search-operator to configure its quiet daily monitor, weekly plan,
and monthly audit for this project. Do not publish or push without approval.
```

The host must provide a scheduler if you want unattended recurring execution.
The skill uses the host's supported automation mechanism rather than inventing
its own scheduler format.

## Command-line helpers

The agent normally chooses these commands for you. They can also be run by hand.
On Windows, replace `python3` with `python` when needed.

### Project state

Initialize a project without overwriting an existing configuration:

```bash
python3 scripts/seo_operator.py init \
  --project /absolute/path/to/site \
  --brand "Example Brand" \
  --origin "https://www.example.com" \
  --landing-url "https://www.example.com/product" \
  --conversion-event "qualified_signup" \
  --timezone "Asia/Kolkata" \
  --market "India,United States" \
  --language "en"
```

Validate and inspect the secret-free state:

```bash
python3 scripts/seo_operator.py validate --project /absolute/path/to/site
python3 scripts/seo_operator.py status --project /absolute/path/to/site
```

Append structured run and experiment records:

```bash
python3 scripts/seo_operator.py record-run \
  --project /absolute/path/to/site --file run-record.json

python3 scripts/seo_operator.py record-experiment \
  --project /absolute/path/to/site --file experiment-record.json
```

See [`examples/`](examples/) for record shapes.

### Read-only live-site audit

```bash
python3 scripts/live_site_audit.py \
  --origin "https://www.example.com" \
  --sitemap "https://www.example.com/sitemap.xml" \
  --max-urls 100 \
  --output live-audit.json
```

The audit does not render client-side JavaScript. Its internal-link counts cover
only sampled sitemap URLs.

### Google Search Console

Authenticate read-only when you only need reports:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly,openid,https://www.googleapis.com/auth/userinfo.email
```

Use the broader Search Console scope only for sitemap mutation or URL Inspection:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,openid,https://www.googleapis.com/auth/userinfo.email
```

List accessible properties and collect final performance data:

```bash
python3 scripts/gsc_api.py sites --output gsc-sites.json

python3 scripts/gsc_api.py performance \
  --site "sc-domain:example.com" \
  --start 2026-08-01 \
  --end 2026-08-28 \
  --dimensions query,page,date \
  --data-state final \
  --output gsc-performance.json
```

Inspect a small set of priority URLs:

```bash
python3 scripts/gsc_api.py inspect \
  --site "sc-domain:example.com" \
  --url "https://www.example.com/product" \
  --output gsc-inspection.json
```

List sitemaps or prepare a dry-run submission:

```bash
python3 scripts/gsc_api.py sitemaps \
  --site "sc-domain:example.com"

python3 scripts/gsc_api.py submit-sitemap \
  --site "sc-domain:example.com" \
  --sitemap "https://www.example.com/sitemap.xml"
```

Add `--apply` only after approval:

```bash
python3 scripts/gsc_api.py submit-sitemap \
  --site "sc-domain:example.com" \
  --sitemap "https://www.example.com/sitemap.xml" \
  --apply
```

URL Inspection reports Google's current state. It does not request indexing for
ordinary pages. Sitemap submission also does not guarantee indexing.

### IndexNow and Bing discovery

Generate a key without printing it:

```bash
python3 scripts/indexnow.py generate-key --output public/indexnow-key.txt
```

Deploy the key file, then verify it:

```bash
python3 scripts/indexnow.py verify-key \
  --host "www.example.com" \
  --key-location "https://www.example.com/indexnow-key.txt" \
  --key-file public/indexnow-key.txt
```

Prepare a dry run:

```bash
python3 scripts/indexnow.py submit \
  --host "www.example.com" \
  --key-location "https://www.example.com/indexnow-key.txt" \
  --key-file public/indexnow-key.txt \
  --url "https://www.example.com/product"
```

Add `--apply` after the updated canonical URL and key file are live and the
submission is approved. An accepted IndexNow request is a discovery notification,
not proof that Bing indexed the URL.

## Default automation rhythm

| Cycle | Default work |
| --- | --- |
| Daily at 07:00 project time | Quiet health monitor and queue update |
| Weekly | Opportunity plan, refresh selection, zero to two reviewable drafts |
| Monthly | Full technical, content-drift, sitemap, provider, and practitioner audit |

Daily work may inspect, measure, prioritize, draft, test, and prepare a review.
Publishing, pushing, merging, deployment, DNS changes, new external properties,
outreach, and first sitemap submissions require approval.

## Safety model

- Review-first changes by default.
- No credentials in project configuration, logs, reports, or command output.
- No doorway pages, content farms, fake reviews, fake awards, fabricated
  experience, paid-link schemes, or copied community posts.
- No fixed publishing quota.
- Sensitive medical, financial, legal, safety, pregnancy, childcare, and similar
  topics require stronger sources and human review.
- Practitioner posts enter an experiment ledger. They are not treated as facts.
- Missing provider data is reported as unavailable, never as zero.
- Submission, inspection, indexing, ranking, and conversion are separate states.

Read [the operating contract](SKILL.md) for the full rules.

## Repository structure

```text
organic-search-operator/
├── SKILL.md                  Agent entrypoint and routing
├── CONTEXT.md                Domain language
├── agents/openai.yaml        Codex interface metadata
├── scripts/                  Portable helper commands and tests
├── references/               Mode-specific operating guidance
├── examples/                 Safe example configuration and records
├── docs/adr/                 Durable design decisions
└── licenses/                 Upstream MIT notices
```

## Development

Run the tests:

```bash
python3 scripts/test_operator.py
```

Validate the skill package after installing PyYAML:

```bash
python3 -m pip install PyYAML==6.0.2
python3 scripts/validate_skill.py .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Limits

This project is an automation and decision framework, not an SEO guarantee. It
cannot create Search Console ownership, bypass provider permissions, guarantee
indexing, or make unsupported claims true. Search systems and their APIs change;
verify high-impact behavior against current official documentation.

## License and acknowledgements

The project is available under the [MIT License](LICENSE). Workflow patterns were
adapted from [NotFair Plugin](https://github.com/nowork-studio/notfair-plugin),
and fallback prose checks were informed by
[Humanizer](https://github.com/blader/humanizer). Their MIT notices are retained
under [`licenses/`](licenses/). The preferred prose integration is the user's
separately installed `prose-humanizer` skill.
