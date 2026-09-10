# Automation and state

## Default schedule

- Daily at 07:00 project-local time: quiet monitor and queue update.
- Weekly: action plan, refresh selection, and zero to two reviewable drafts.
- Monthly: full technical audit, sitemap reconciliation, content-drift review,
  provider baseline refresh, and practitioner-intelligence review.

Projects may override the schedule in configuration. Prefer calendar schedules
over an interval that drifts from the intended local time.

## Daily run

1. Read repository instructions, project config, state, last run, queue, and
   experiment ledger.
2. Inspect working-tree status and recent commits. Do not overwrite user work.
3. Fetch only data needed to detect material change. Respect cache age, API
   quotas, final complete dates, and provider failures.
4. Check deployment health, primary landing page, sitemap, robots, priority
   index states, rank 5 to 20 opportunities, high-impression weak-CTR pages, and
   material declines.
5. Re-rank the queue. Refresh before creating new pages.
6. If the run is a weekly drafting run, prepare zero to two work items that pass
   every gate.
7. Run validations. Prepare a review branch or patch when appropriate.
8. Append the run record atomically and update current state.
9. Notify only for a meaningful change, completed review artifact, failure,
   quota problem, or required user action.

## External actions

The automation may automatically read provider data and notify IndexNow only
for an already approved, verified deployment when the project configuration
explicitly enables that behavior.

Require approval for:

- DNS changes;
- new external properties or permissions;
- sitemap mutation or first submission;
- publishing, pushing, merging, or production deployment;
- new directory, profile, PR, outreach, or backlink submissions;
- destructive URL removal or redirect changes.

## Run record

Include:

- run ID, kind, start/end time, evidence dates, and commit base;
- provider availability and quotas;
- GSC setup and property state;
- opportunities added, changed, rejected, or blocked;
- pages drafted, refreshed, approved, published, and verified;
- metadata, links, schema, sitemap, and CTA changes;
- build and validation results;
- Google sitemap and inspection outcomes;
- IndexNow and optional Bing outcomes;
- experiment updates;
- blockers, approvals needed, and next queue.

Record external states as `proposed`, `pending`, `completed`, `failed`, or
`blocked`. Do not collapse these into a single success flag.

## Backlinks and entities

Default to audit-only. Check known profiles, earned mentions, submitted entries,
platform messages, and provider backlink data. New opportunity discovery is
opt-in and limited to legitimate product profiles, relevant directories,
partner/resource pages, and earned media. Every candidate needs a relevance and
risk rationale and requires approval before submission or outreach.
