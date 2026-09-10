# Audit and opportunity model

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

Segment branded and non-branded queries with an explicit brand-term list.
Evaluate query and page together before assigning an intent. Inspect country and
device differences when they could change the recommended action.

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

Thresholds are defaults, not universal truths. Scale them to the site's data
volume and record any change.

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
