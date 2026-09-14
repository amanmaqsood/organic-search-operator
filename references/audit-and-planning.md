# Audit and opportunity model

Apply [Technical quality gate](technical-quality-gate.md) to the repository and
live-site evidence before scoring content or distribution work.

## Evidence clock

Record the retrieval time, provider's final complete date, comparison window,
deployment time, and known search updates. Never compare an incomplete current
window with a complete prior window without labeling the mismatch.

## Audit layers

### Repository and deployment

- working-tree state and recent commits;
- detected production branch and deployment adapter;
- source-of-truth content and generated outputs;
- build, generation, lint, and test commands;
- environment requirements without revealing values.

### Technical discovery

- HTTP status and redirect chains;
- robots directives and meta robots;
- canonical presence, uniqueness, and agreement;
- sitemap validity, limits, lastmod accuracy, and canonical URL coverage;
- JavaScript rendering and discoverable links;
- mobile layout and Core Web Vitals evidence;
- title, description, H1, structured data, Open Graph image, and language tags;
- broken, orphaned, redirected, duplicate, and soft-404 pages.

Cross-check both directions: sitemap URLs must be canonical and indexable, and
canonical indexable pages should appear in an appropriate sitemap unless the
project documents an exception.

### Search performance

Segment branded and non-branded queries using the provider's classification when
available, with an explicit brand-term fallback. Record which method was used
and its limitations. Evaluate query and page together before assigning an
intent. Inspect country and device differences when they could change the
recommended action.

Look for:

- positions 5 to 20 with at least 100 impressions in the selected complete
  window;
- high-impression, low-CTR pages compared with project pages at similar
  positions and SERP shapes;
- pages losing clicks, impressions, or query coverage across like-for-like
  windows;
- queries with no page that directly satisfies their intent;
- multiple pages competing for the same intent;
- indexed pages with no useful impressions and no conversion role.

Track total, branded, and non-branded results separately. Qualified non-branded
clicks and conversions are useful acquisition measures, but they do not replace
brand demand, total search health, conversion quality, or revenue.

Apply the `PT-01` through `PT-10` checks in
[Practitioner intelligence](practitioner-intelligence.md) to the queue. For
each applicable check, retain the project evidence, competing explanation,
expected metric, review date, and stop condition. Do not add points merely
because a tip is popular or came from a recognized practitioner.

Also apply `PT-11` through `PT-18` when the project has product records,
structured entities, free-tool potential, directory data, or agent-facing
interfaces. Audit prospective page families as systems: sample generated URLs,
measure uniqueness and indexation, inspect filter combinations and lifecycle
states, and verify that the pages form a useful browseable hierarchy.

Use Search Console as the first-party search baseline. A licensed Ahrefs API or
equivalent provider may add keyword, competitor, and link evidence when already
configured, but it is optional and must not replace GSC or conversion data.
Keep provider metrics separate because their databases and estimates differ.

Thresholds are defaults, not universal truths. Scale them to the site's data
volume and record any change.

### AI-assisted search visibility

Follow [AI-assisted search visibility](ai-visibility.md). Keep Google
generative impressions, Bing citations and grounding queries, ChatGPT referral
sessions and conversions, crawler eligibility, and sampled prompts as separate
observations.

Collect available evidence during the daily monitor. Unless a crawl or access
blocker requires immediate repair, evaluate an AI-specific content change in
the weekly cycle using complete comparable periods. Use 28 days as the default
comparison window when volume and seasonality make it meaningful, and record
any adapted window.

Use an observed grounding query or prompt to inspect the best existing
canonical page. Improve its answer units when doing so makes the page clearer
and more useful to people. Do not create a page for every phrase or infer that
one provider's citation behavior is a universal ranking system.

## Opportunity record

Each candidate needs:

- stable identifier;
- page or proposed canonical URL;
- intent and funnel stage;
- evidence and evidence dates;
- problem statement;
- proposed action;
- expected business effect;
- effort and risk;
- dependencies and approval needs;
- measurement metric and review date;
- duplicate and cannibalization result.

## Priority

Rank by expected qualified impact, confidence, effort, reversibility, and risk.
Do not rank by search volume alone.

For scheduled work, incorporate the current
[recent intelligence brief](recent-intelligence.md) without treating public
discussion as proof of demand. Use the 100-point score and risk penalty defined
there. Keep every component visible in the opportunity record.

Use this order when scores are close:

1. unblock crawling, indexing eligibility, or conversion;
2. improve a proven existing page;
3. satisfy missing bottom-of-funnel intent;
4. strengthen internal links and topical structure;
5. create supporting informational material.

## Stop conditions

Pause new content and diagnose when any applies:

- recent pages remain unindexed beyond the project's normal discovery window;
- rising indexed URL count coincides with falling qualified clicks or
  conversions;
- new pages overlap existing intent;
- engagement or conversion quality falls materially;
- source quality or original evidence is insufficient;
- the site has unresolved crawl, canonical, security, or deployment failures.
