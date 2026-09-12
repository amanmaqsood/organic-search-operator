---
name: organic-search-operator
description: >
  Bootstrap, audit, plan, draft, and monitor evidence-led SEO and GEO growth for
  a website. Use when asked to connect Google Search Console, submit or inspect
  sitemaps, notify Bing through IndexNow, audit a site or repository, improve a
  landing page, build a supporting content cluster, create an organic-search
  plan, investigate indexing, mine GSC opportunities, refresh declining pages,
  generate llms.txt, llms-full.txt, and ai.txt, evaluate useful programmatic
  page systems or free tools, or configure a recurring SEO automation with
  optional bounded autonomy and recent audience intelligence. Produces
  reviewable changes by default and never promises rankings or indexing.
---

# Organic Search Operator

Grow one designated conversion page and its supporting topic cluster using
project evidence. Treat rankings as diagnostics; optimize for qualified organic
conversions or revenue.

## Operating contract

- Read the repository instructions and `CONTEXT.md` before acting.
- Preserve unrelated changes. Start repository work with status and recent
  history checks.
- Work review-first unless project policy explicitly selects
  `autonomous_safe`. In review-first mode, get explicit approval before
  publishing, pushing, changing DNS, changing production SEO directives,
  creating external properties, or submitting a new sitemap.
- In `autonomous_safe`, complete at most one reversible work item inside the
  configured mutation envelope. Never treat that mode as unrestricted access.
- Never claim a URL is indexed because it was submitted. Never promise a rank,
  traffic level, or date.
- Treat creator tips as hypotheses. Validate them against official guidance,
  current SERPs, the project's data, and a reversible experiment.
- Do not create doorway pages, scaled low-value pages, fake reviews, fake
  awards, fabricated experience, paid-link schemes, or detector-evasion copy.
- Keep credentials out of repositories, reports, logs, and tool output.
- Prefer existing project commands, generators, content models, and deployment
  conventions over generic replacements.

## Route the request

1. If `.organic-search/config.json` is absent, run **Bootstrap**.
2. If the user asks for setup or access, run **Provider setup**.
3. If the user asks what to do, run **Audit and plan**.
4. If the user asks for content or page changes, run **Execute a work item**.
5. If the user asks for daily or recurring work, run **Automation setup**.
6. If the user asks for status, report from evidence and state; do not mutate.

Read only the references needed for the selected route:

- [Project contract](references/project-contract.md)
- [Search provider setup](references/search-provider-setup.md)
- [Audit and opportunity model](references/audit-and-planning.md)
- [Content and editorial policy](references/content-and-editorial.md)
- [GEO and entity guidance](references/geo-and-entity.md)
- [Machine-readable discovery set](references/machine-readable-discovery.md)
- [Automation and state](references/automation-and-state.md)
- [Automation prompt template](references/automation-prompt-template.md)
- [Recent intelligence and autonomous action](references/recent-intelligence.md)
- [Practitioner intelligence and PT-01 through PT-18 decision checks](references/practitioner-intelligence.md)
- [Report contract](references/report-contract.md)

## Bootstrap

1. Detect the site framework, content source of truth, build command,
   deployment branch, production origin, sitemap, robots file, analytics setup,
   and existing SEO tooling. Do not guess unresolved production values.
2. Ask only for missing business decisions: brand, canonical origin, primary
   landing URL, conversion event, markets, languages, and regulated-topic
   status.
3. Initialize project state without overwriting existing files:

   ```text
   python <skill>/scripts/seo_operator.py init --project <repo> \
     --brand <brand> --origin <https://example.com> \
     --landing-url <https://example.com/product> \
     --conversion-event <event> --timezone <IANA timezone>
   ```

4. Validate the result with `seo_operator.py validate --project <repo>`.
5. Record detected commands and adapters in `.organic-search/config.json`.
   Store no secrets there.
6. On the first automation run, or the first post-upgrade run missing any part
   of the discovery set, detect the public source directory, build the verified
   public-content manifest, and follow
   [Machine-readable discovery set](references/machine-readable-discovery.md)
   to generate `llms.txt`, `llms-full.txt`, and experimental `ai.txt`.

## Provider setup

Follow [Search provider setup](references/search-provider-setup.md).

- Use exact GSC property identifiers. Prefer `sc-domain:example.com` when the
  user owns the domain and DNS verification is possible.
- Use gcloud application-default credentials with the minimum required Search
  Console scopes. Capture tokens inside scripts; never print them.
- Read performance by query, page, date, country, and device as separate useful
  views. Mark incomplete dates as partial.
- Use URL Inspection only for selective diagnosis. It reports state and does
  not request indexing for ordinary pages.
- Use sitemap discovery and submission for Google. Use IndexNow for Bing and
  other participating engines after a verified production change.
- If authenticated browser work is necessary, inspect and prepare values, but
  pause before DNS or irreversible account mutations.

## Audit and plan

Follow [Audit and opportunity model](references/audit-and-planning.md).

Collect evidence in this order:

1. repository and deployment health;
2. crawlability, indexability, canonicals, sitemap, robots, rendering, status
   codes, structured data, internal links, and performance;
3. GSC totals plus query-by-page evidence, segmented without naively averaging
   CTR or position across aggregations;
4. primary landing-page intent, conversion path, proof, objections, and
   internal authority;
5. current SERP shape, competitors, and gaps;
6. content inventory, duplication, cannibalization, decay, and orphan pages;
7. optional Bing, AI-assisted search, backlink/entity, and
   practitioner-experiment evidence.
8. a current Last 30 Days brief for scheduled cycles, treated as supporting
   evidence rather than proof of demand.
9. practitioner-derived PT-01 through PT-18 checks, with unsupported numeric and
   causal claims rejected rather than converted into quotas.

Produce a ranked queue. Prefer, in order:

1. blockers to crawling, rendering, canonicalization, indexing, or conversion;
2. existing pages in positions 5 to 20 with meaningful impressions;
3. high-impression pages with weak CTR relative to comparable project pages;
4. declining pages with preserved intent;
5. missing high-intent pages that add distinct value;
6. broader informational content only when it supports the landing-page cluster.

Find 5 to 10 opportunities per cycle. This is a research queue, not a publishing
quota. Draft zero to two items only when they pass the opportunity and quality
gates.

## Execute a work item

1. Confirm intent and check for an existing page that already serves it.
2. Prefer refreshing an existing relevant URL over creating a duplicate.
3. Build a brief with evidence, differentiator, conversion role, internal links,
   required proof, sources, and a measurable hypothesis.
4. Edit the source of truth, not generated output. Follow the project's existing
   generator and media conventions.
5. Apply [Content and editorial policy](references/content-and-editorial.md).
   When `$prose-humanizer` is available, invoke it in embedded mode after facts
   and citations are stable. Otherwise use the built-in fidelity checklist.
6. Run project-specific formatting, content validation, build, link, schema,
   canonical, sitemap, and route checks.
7. Apply the configured policy. In `review_first`, present the diff and expected
   measurement plan without publishing or pushing. In `autonomous_safe`, follow
   [Recent intelligence and autonomous action](references/recent-intelligence.md)
   and proceed only when every authorization gate passes.
8. After an authorized production deployment, verify the live URL. Notify
   IndexNow for added, changed, or deleted canonical URLs when it was already
   enabled and verified. A first sitemap submission always requires approval.

## Automation setup

Follow [Automation and state](references/automation-and-state.md).
Use [Automation prompt template](references/automation-prompt-template.md) as
the base prompt when creating a project automation; resolve every placeholder
from confirmed project configuration.
For every scheduled cycle, follow
[Recent intelligence and autonomous action](references/recent-intelligence.md).
Apply the decision checks in
[Practitioner intelligence](references/practitioner-intelligence.md) when
building and selecting from the queue.
On the first scheduled run and after relevant canonical content changes, follow
[Machine-readable discovery set](references/machine-readable-discovery.md).

- Default rhythm: quiet daily monitor at 07:00 project-local time, weekly action
  plan and drafting batch, monthly full audit and baseline refresh.
- Stay silent when daily state is unchanged and no action is required.
- Every cycle must consult a Last 30 Days brief that is no more than 24 hours
  old. Reuse the same-day brief instead of repeating paid or slow source calls.
- The first run creates all three machine-readable discovery files. An existing
  project missing any part bootstraps it on the next eligible run. Later runs
  update files only when their verified canonical source changes.
- Daily work in `review_first` may inspect, measure, prioritize, draft, test,
  and prepare a review. In `autonomous_safe`, it may complete one eligible,
  reversible action without per-run approval.
- Read project state first and write an append-only run record before finishing.
- Stop or slow content creation when indexation, duplication, engagement,
  conversion, or quality signals deteriorate.
- Never turn practitioner numbers into automatic thresholds unless current
  official guidance or project evidence validates them for this project.
- When the host offers a scheduler, use its supported automation mechanism. For
  local repository work, prefer a project-scoped recurring task. Do not handwrite
  scheduler directives when a scheduling tool is available.

## Completion gate

Before reporting success, verify:

- configuration and state validate;
- claims and citations survive the prose pass;
- `llms.txt`, `llms-full.txt`, and `ai.txt` match the current public manifest,
  contain no excluded content, and are live-verified after deployment;
- no intent collision or orphan page was introduced;
- touched canonical URLs resolve as expected and are indexable by policy;
- build and relevant tests pass;
- external actions are distinguished as completed, pending, blocked, or merely
  proposed;
- the run report and next queue are recorded.

If a required data source is unavailable, label it unavailable. Do not turn
missing data into zero or infer success from the absence of an error.
