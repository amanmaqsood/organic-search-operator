# Practitioner intelligence

Practitioner posts are idea discovery, not authority. Review the watchlist
monthly when recent social or web research is available.

An author's reputation is not evidence that a numeric claim is true. Preserve
the source and wording in the experiment ledger, but automate only the
underlying mechanism that is compatible with official guidance and project
data.

## Starter watchlist

### Workflow and execution

- `@borjafat`: scheduled SEO systems, link magnets, and automation workflows.
- `@hridoyreh`: frequent tactical checklists, GSC mining, image SEO, free tools,
  refreshes, and backlink ideas.
- `@mehrab_build`: programmatic SEO with unique-value warnings.
- `@seonatia`: startup audits and GSC opportunity mining.
- `@codyschneider`: SaaS bottom-of-funnel content and measurement workflows.
- `@askOkara`: automated audit and content workflows; treat vendor claims as
  self-interested evidence.

### Diagnostics and technical SEO

- `@foley_seo`: indexing and AI Overview testing.
- `@Charles_SEO`: crawling, rendering, and technical implementation.
- `@SEOKeval`: ecommerce SEO and AEO observations.

### Brand, authority, and links

- `@fatjoedavies`: brand-led search, digital PR, and link strategy.
- `@jakezward`: multi-surface search and authority systems.
- `@indexsy`: commercial and local SEO; screen higher-risk tactics carefully.

The list is seeded from research performed on 2026-09-10. It is not exhaustive,
and inclusion is not endorsement.

The 2026-09-14 review of Alex Groberman's summary of a Search Engine Journal
interview with Perplexity's Jesse Dwyer informed `PT-19` through `PT-22` below.
The article remains a practitioner hypothesis source, not a trusted default
watchlist addition. Its promotional examples, retrieval constants, and causal
claims are not project evidence.

## Experiment intake

For each tip, record:

- source handle, source URL, publication date, and retrieval date;
- exact claim without promotional framing;
- applicable project and page type;
- official-guidance check;
- evidence quality and conflicts of interest;
- expected mechanism and business metric;
- risks, reversibility, control or comparison, and stop condition;
- outcome after the measurement window.

Reject a tip when it relies on fabricated proof, doorway pages, mass low-value
content, link manipulation, copying community content, forced indexing, or an
unverifiable performance claim.

Use recent-research tooling when available, but do not require social-platform
credentials for the core operator. Label unavailable source coverage.

## Practitioner-derived decision checks

Run these checks during queue construction. They are decision prompts, not
ranking factors or mandatory quotas. Record the relevant check ID in the
opportunity or experiment record.

| ID | Practitioner idea | Automation decision |
| --- | --- | --- |
| `PT-01` | Specific claims are easier to evaluate than vague claims. | Flag vague landing-page claims. Replace them with a number only when a dated, scoped, verifiable source exists; otherwise make the wording precise without inventing a metric. |
| `PT-02` | Comparison pages can serve valuable commercial intent. | Consider a comparison or alternatives page only when current query, customer, or SERP evidence shows distinct evaluation intent. Require a fair method, current facts, disclosed relationship, and original usefulness. Do not assume a `9x` return or copy third-party traffic-value estimates as revenue. |
| `PT-03` | A useful existing page may be a better asset than a new page. | Prefer a materially useful refresh when the existing URL already matches intent and has history or project evidence. Preserve the URL when appropriate, update genuinely stale material, and measure the result. Never promise a fixed position gain. |
| `PT-04` | Important pages need relevant internal paths. | Find contextually relevant source pages and add only links that help readers and crawlers. Use descriptive natural anchors. There is no fixed target such as 20 to 30 links. |
| `PT-05` | Specific buyer questions can reveal valuable intent. | Research complete buyer situations and natural-language questions. Satisfy the intent with a section when possible; create a page only when the intent and value are genuinely distinct. Do not optimize for a fixed query length. |
| `PT-06` | Non-branded search can show new-audience growth. | Report branded and non-branded performance separately when the provider supports it. Prioritize qualified non-branded growth for acquisition, but retain branded, total, conversion, and revenue measures for context. |
| `PT-07` | Readers benefit from reaching the answer quickly. | For question-led pages, put a clear, qualified answer near the beginning. Do not enforce a 100-word cutoff when context, safety, or accuracy requires more explanation. |
| `PT-08` | Buyer guides and best-tools pages can support evaluation. | Create one only when the site can offer first-hand testing, transparent criteria, accurate competitor data, useful differentiation, and conflict disclosure. Never assert that an AI system trains on or repeats whichever page ranks first, and never self-award an unsupported top position. |
| `PT-09` | Buyer situations can deserve tailored pages. | Use industry, budget, role, or use-case pages only when each has distinct needs, proof, examples, and a place in the site architecture. Consolidate thin variations to avoid doorway or scaled-content patterns. |
| `PT-10` | A maintained body of useful content builds context over time. | Maintain and publish when evidence and quality gates pass. Do not publish merely to satisfy a daily cadence, simulate freshness, or keep a model from “forgetting” the brand. |

## Source hierarchy for these checks

Use current official documentation first, then project evidence, then
independent studies, and finally practitioner observations. Useful baseline
references include:

- [Google people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google generative AI search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [Google link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)
- [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies)
- [Search Console branded and non-branded analysis](https://support.google.com/webmasters/answer/17010961)
- [OpenAI publisher discovery controls](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)

Re-check official guidance during the monthly practitioner review because
search and AI discovery behavior changes. A failed or unavailable check remains
`unverified`; it does not become evidence for or against the tip.

## Compound search-asset checks

A practitioner reported using the following architecture on ScrollLaunch. The
reported outcome is not proof that the same architecture will work elsewhere.
Apply these additional checks to the project's own product, data, audience, and
indexation evidence.

| ID | Reported strategy | Automation decision |
| --- | --- | --- |
| `PT-11` | Combine Search Console with a commercial SEO-data API for recurring audits. | Use GSC as the first-party baseline. Add Ahrefs or another licensed provider only when access already exists and its data changes a decision. Compare like-for-like provider windows and report unavailable data honestly. |
| `PT-12` | Create makers, countries, categories, tags, alternatives, technology, and archive pages around each launch. | Treat each page family as a candidate template. Approve it only when every URL has distinct public data, user value, browseable hierarchy, canonical rules, lifecycle handling, and no doorway or index-bloat risk. |
| `PT-13` | Build free tools that lead users toward the main product. | Prefer a free tool when it solves a real adjacent task, has evidenced demand, works without deceptive gating, and has a natural measured conversion path. Include security, abuse, privacy, maintenance, and operating-cost checks. |
| `PT-14` | Build a directory or leaderboard as an independent search surface. | Require a defensible dataset, transparent inclusion and ranking method, update cadence, correction path, useful filters, stable canonical pages, and conflict disclosure. Reject pay-to-rank, fabricated metrics, copied databases, and thin combinations. |
| `PT-15` | Publish machine-readable files and interfaces for agents. | On the first run, create and validate `llms.txt`, `llms-full.txt`, and experimental `ai.txt` from verified public canonical content. Keep them synchronized. Consider Markdown catalogs, OpenAPI, public APIs, CLI, or MCP only when they expose a real supported capability. Never claim a ranking benefit. |
| `PT-16` | Keep a permanent page for every product or launch. | Preserve a stable canonical URL while the page remains truthful and useful. Add status, history, maker, alternatives, and related context when supported. Merge, redirect, archive, or `noindex` expired and duplicate pages according to user value instead of keeping zombie URLs forever. |
| `PT-17` | Connect products to related entity and collection pages. | Design a crawlable contextual graph between useful parent, child, sibling, and conversion pages. Prevent orphan pages and excessive faceted combinations. Link because the relationship helps a visitor, not to circulate an abstract authority score. |
| `PT-18` | Prefer genuinely useful pages over random generated pages. | This is a hard gate. A generated page must contain original data, functionality, analysis, or decision help that would remain useful without search traffic. Otherwise consolidate or do not publish. |
| `PT-19` | Different people or sessions may receive different AI answers for the same question. | Treat prompt checks as provider-specific observations. Record the exact prompt, surface, model, date, locale, session state, persona, cited URLs, and brand wording; repeat when practical and never report one sample as a stable rank. |
| `PT-20` | Search and answer systems may retrieve useful sections within a page. | Improve reader-useful answer units with descriptive headings, explicit subjects, direct qualified answers, evidence, dates, and limitations. Never force 2-to-4-word fragments, token targets, FAQ formatting, or a fixed page length. |
| `PT-21` | Citations can differ from ordinary search rankings. | Measure each surface with its own first-party evidence when available: Google generative impressions, Bing citations and grounding queries, attributed referrals, conversions, crawler eligibility, and controlled prompt samples. Do not merge them into a universal AI score. |
| `PT-22` | A broad body of aligned content can supply more potential answers. | Add or expand content only for distinct evidenced user value. Reject repeated explanations, one-page-per-prompt variants, and scale for its own sake; prefer improving the best matching canonical page and consolidate duplication. |

For the detailed provider, answer-unit, prompt-sampling, and decision-clock
rules behind these checks, follow
[AI-assisted search visibility](ai-visibility.md).
