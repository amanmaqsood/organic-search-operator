# Automation and state

## Default schedule

- Daily at 07:00 project-local time: quiet monitor and queue update.
- Weekly: action plan, refresh selection, and zero to two reviewable drafts.
- Monthly: full technical audit, sitemap reconciliation, content-drift review,
  provider baseline refresh, and practitioner-intelligence review.

Every scheduled cycle consults Last 30 Days research. Run it fresh once per
project-local calendar day and reuse that brief for later cycles on the same day.
Projects may override the schedule. Prefer calendar schedules over an interval
that drifts from the intended local time.

## Daily run

1. Read repository instructions, project config, state, last run, queue, and
   experiment ledger.
2. Inspect working-tree status and recent commits. Do not overwrite user work.
3. Consult the current recent intelligence brief. Run `$last30days` in agent
   mode when the cached brief is absent, over 24 hours old, or about a different
   project topic. Follow [Recent intelligence and autonomous action](recent-intelligence.md).
4. Fetch the remaining data needed to detect material change. Respect cache
   age, API quotas, final complete dates, and provider failures.
5. Check deployment health, primary landing page, sitemap, robots, priority
   index states, rank 5 to 20 opportunities, high-impression weak-CTR pages, and
   material declines.
6. Apply the `PT-01` through `PT-10` practitioner-derived checks. Look for
   unsupported vague claims, useful refreshes, missing contextual links,
   specific buyer questions, qualified non-branded growth, early-answer clarity,
   defensible comparisons, and genuinely distinct buyer situations. Treat every
   observation as a hypothesis until project evidence supports it.
7. Re-rank the queue using qualified impact, project evidence, recent
   intelligence, landing-page support, confidence, reversibility, and risk.
8. Apply the configured policy. In `review_first`, prepare the appropriate
   review artifact. In `autonomous_safe`, select and complete at most one
   eligible work item, including at most one new page.
9. Run validations and, when authorized, deploy and verify the focused change.
   Roll it back when deployment or live verification fails.
10. Append the run record atomically and update current state.
11. Notify only for a meaningful change, completed review artifact or
    autonomous action, failure, quota problem, rollback, or required user action.

## External actions

The automation may always read already authorized provider data. In
`review_first`, external mutations retain the approval rules below. In
`autonomous_safe`, the narrow mutation envelope in
[Recent intelligence and autonomous action](recent-intelligence.md) authorizes
one reversible action, its existing deployment workflow, and an IndexNow notice
for verified canonical URLs when IndexNow was configured in advance.

Always require approval for:

- DNS changes;
- new external properties or permissions;
- sitemap first submission;
- new directory, profile, outreach, or backlink submissions;
- destructive URL removal, redirect, domain, or URL migration changes;
- purchases, billing, credentials, ownership, or account changes.

In `review_first`, also require approval for sitemap mutation, publishing,
pushing, merging, and production deployment. In `autonomous_safe`, those actions
do not need per-run approval only when every autonomous gate passes. A first
sitemap submission and the always-forbidden actions remain outside the mutation
envelope in both modes.

## Run record

Include:

- run ID, kind, start/end time, evidence dates, and commit base;
- provider availability and quotas;
- recent intelligence topic, retrieval time, age, coverage, and artifact;
- GSC setup and property state;
- opportunities added, changed, rejected, or blocked;
- opportunity score components and authorization source;
- pages drafted, refreshed, approved, published, and verified;
- metadata, links, schema, sitemap, and CTA changes;
- build and validation results;
- Google sitemap and inspection outcomes;
- IndexNow and optional Bing outcomes;
- experiment updates;
- applicable practitioner check IDs, verification state, and rejected numeric
  or causal claims;
- autonomous action count, new-page count, commit, deployment, live
  verification, and rollback;
- blockers, approvals needed, and next queue.

Record external states as `proposed`, `pending`, `completed`, `failed`, or
`blocked`. Do not collapse these into a single success flag.

## Backlinks and entities

Default to audit-only. Check known profiles, earned mentions, submitted entries,
platform messages, and provider backlink data. New opportunity discovery is
opt-in and limited to legitimate product profiles, relevant directories,
partner/resource pages, and earned media. Every candidate needs a relevance and
risk rationale. Submission or outreach always requires approval and is never in
the autonomous-safe mutation envelope.
