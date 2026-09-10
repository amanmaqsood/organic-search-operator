# Automation prompt template

Resolve every bracketed value before scheduling. Keep notification preferences
in the scheduler configuration, not inside this prompt.

```text
Use $organic-search-operator to run the recurring organic-search cycle for
[BRAND] in [ABSOLUTE_PROJECT_PATH]. The canonical origin is [CANONICAL_ORIGIN],
the primary landing page is [PRIMARY_LANDING_URL], and the primary conversion
event is [CONVERSION_EVENT]. Read the repository instructions and
.organic-search/config.json, state.json, runs.jsonl, and experiments.jsonl before
acting. Preserve unrelated user changes.

Determine the cycle from the project-local date. Every run performs the quiet
daily monitor. On [WEEKLY_DAY], also prepare the weekly opportunity plan and up
to two reviewable drafts or refreshes. On day [MONTHLY_DAY] of the month, also
perform the full technical, content-drift, sitemap, provider-baseline, and
practitioner-intelligence audit.

Start with repository status and recent commits. Detect the source-of-truth
content system and existing project commands. Never edit generated output when a
generator or source model owns it.

If search-provider setup is incomplete, perform safe read-only preflight checks.
Use an existing connector or gcloud ADC for Google Search Console. Use the exact
configured property. Do not print tokens. Record unavailable access, incomplete
dates, permission errors, quota limits, or verification blockers as such. Never
claim a property is verified, a sitemap is submitted, or a URL is indexed
without provider evidence.

Inspect the primary landing page, robots.txt, sitemap, priority URL health, and
recent Search Console performance. Analyze complete periods by compatible views,
including query plus page, page, country, and device when relevant. Prioritize
crawl, rendering, canonical, indexability, and conversion blockers. Then
prioritize existing pages in positions 5 to 20, comparable high-impression weak-
CTR pages, and meaningful declines. Refresh a relevant existing URL before
creating a new one.

Maintain 5 to 10 ranked opportunities. This is not a publishing quota. Create
zero to two drafts only during the weekly cycle and only when each topic has
distinct evidenced intent, original value, a conversion role, bidirectional
internal links, suitable sources, no unresolved cannibalization, and a
measurement hypothesis. Stop or slow creation when indexation, duplication,
engagement, conversion, source quality, or technical health deteriorates.

For prose, stabilize facts and citations first. Prefer $prose-humanizer in
embedded mode when it is available. Preserve all claims, citations, links,
names, numbers, dates, modality, chronology, causality, limitations, safety
language, and technical terms. Never fabricate experience, reviews, rankings,
outcomes, or authority. Never describe text as undetectable or human-authored.

Treat Reddit-intent pages as experiments. Check project data and the current
SERP first, prefer improving an existing page, do not copy community material or
imply affiliation, and use authoritative sources for factual claims. For
regulated or sensitive topics, use the project-approved primary authorities and
require human review.

Backlink and entity work is audit-only unless project configuration explicitly
enables discovery. Do not submit profiles, contact people, or create external
listings without approval. Reject link farms, paid-link schemes, fabricated
endorsements, fake reviews, and reciprocal manipulation.

Run the project build and relevant validations for every proposed change. Check
canonical uniqueness, indexability policy, sitemap membership, internal links,
metadata, schema eligibility, media, and live routes as applicable. Prepare a
review branch or patch, but do not publish, push, merge, deploy, change DNS,
create external properties, or submit a new sitemap without explicit approval.

After an already approved production deployment, verify the live canonical URLs.
When project configuration explicitly enables it, notify IndexNow only for
canonical URLs added, materially changed, or deleted since the last successful
notification. An accepted submission does not mean indexed.

Append an atomic run record before finishing. Include evidence dates, provider
states, ranked opportunities, changes proposed, validations, approvals needed,
submission states, experiments, blockers, and the next queue. Update current
state without erasing history. Report only meaningful changes, completed review
artifacts, failures, quota problems, or required user actions.
```
