# AI-assisted search visibility

Use this reference when a project wants visibility or measurement across Google
generative search features, Microsoft AI experiences, ChatGPT search, or
Perplexity. Treat each provider as a separate surface. Do not infer a universal
AI ranking from one provider, prompt, citation, or referral.

## Evidence order

Prefer evidence in this order:

1. the provider's first-party property report;
2. attributed referral and conversion analytics;
3. verified crawler and live-page access;
4. reproducible prompt samples;
5. third-party estimates and practitioner observations.

Keep the layers separate. An impression is not a citation, a citation is not a
click, and a click is not a conversion. Missing provider data is `unavailable`,
not zero.

## First-run eligibility audit

Record the result and retrieval time for each applicable check:

- Google Search Console property access, the Search generative AI inclusion
  control, and the Generative AI performance report;
- Bing Webmaster Tools access and AI Performance availability;
- `OAI-SearchBot`, `PerplexityBot`, and ordinary search crawler access in
  `robots.txt`, server responses, and any WAF configuration;
- important content in crawlable rendered HTML, with semantic headings and
  accessible interactive controls;
- analytics attribution for `utm_source=chatgpt.com` and any other verified AI
  referral sources.

Changing a provider inclusion control, crawler policy, WAF rule, account,
property, permission, or analytics configuration is an external mutation. In
an unattended run, inspect existing access only. Never start a login, consent,
device-code, ownership-verification, or credential flow.

Use an existing API or connector when it exposes the needed report. Otherwise
accept a user-provided export. Do not scrape an authenticated dashboard during
unattended automation. Record a UI-only or unsupported report as unavailable
to automation and provide the smallest one-time setup instruction.

## Provider measurements

### Google Search

When available, collect Generative AI performance impressions by date, page,
country, and device for complete periods. Keep these rows separate from the
ordinary Search Performance dataset. The dedicated report is visibility data;
do not manufacture clicks, queries, positions, citations, or conversions that
the report does not provide.

Check the Search generative AI inclusion control read-only. Changing it always
requires an explicit user decision because it changes whether the site's links
and content can appear in Google's supported generative features.

### Bing and Microsoft AI experiences

When available, collect total citations, average cited pages, page-level
citation activity, sampled grounding queries, and trends from Bing Webmaster
Tools AI Performance. These values do not establish placement, rank, authority,
or the role of a URL inside an answer.

Use grounding queries to inspect whether an existing page is clear and
complete for a real intent. Do not create one page per phrase. Prefer improving
or expanding the best matching canonical page.

### ChatGPT

Verify that `OAI-SearchBot` is not unintentionally blocked when the project
wants ChatGPT search discovery. Keep GPTBot training controls separate from
search discovery controls. Measure attributed referrals and the configured
conversion event when analytics contains `utm_source=chatgpt.com`.

### Perplexity

Verify `PerplexityBot` access and, when a WAF is present, validate requests
against Perplexity's current published IP ranges rather than trusting a user
agent alone. `Perplexity-User` is a user-triggered fetcher with different
behavior; do not describe its access as ordinary crawling or training.

## Answer-unit quality

An answer unit is a reader-useful section that can stand on its own without
losing the page's surrounding meaning. Improve a section when this also helps a
person:

- use a descriptive heading;
- identify the subject instead of relying on ambiguous pronouns;
- answer the qualified question directly near the start;
- include the conditions, limitations, units, date, or market that make the
  answer accurate;
- support externally verifiable claims with suitable primary sources;
- link to the next useful detail or conversion step when appropriate;
- keep tables, images, video, and visible text consistent about the same entity.

Do not split prose into tiny fragments, repeat the same explanation across many
pages, force FAQ formatting, or target a fixed word, token, section, or page
length. Google can understand passages inside a page and explicitly says that
special AI chunking is unnecessary. A page still needs coherent purpose,
original value, and a satisfying reading experience.

## Prompt observation panel

Use prompt sampling only as a controlled observation:

- maintain a small stable panel covering discovery, evaluation, comparison,
  objection, and high-intent questions relevant to the project;
- record the exact prompt, provider, model or surface, date, locale, session
  state, configured persona, observed brand wording, and cited URLs;
- repeat samples when practical to expose answer variability;
- keep anonymous/default and deliberately configured persona tests separate;
- never put customer secrets, personal memories, or sensitive account context
  into unattended tests;
- do not convert samples into a universal rank or share-of-voice score unless
  the method, denominator, limitations, and repeatability are documented.

Use sampled changes to form a hypothesis. Require provider, analytics, Search
Console, conversion, or project evidence before an autonomous content change.

## Decision clock

Collect eligibility and available provider data during the quiet daily monitor.
Unless a technical blocker requires immediate repair, select AI-visibility work
during the weekly decision cycle using complete comparable periods. A 28-day
comparison is the default when the site has enough data; adapt the window to
seasonality and volume and record the reason.

Do not rewrite a page because of one citation loss, one prompt response, or one
day of impressions. Preserve an experiment window and stop condition.

## Current primary references

Re-check these during the monthly provider review because interfaces and
capabilities change:

- Google generative AI optimization guidance:
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google Generative AI performance report:
  https://support.google.com/webmasters/answer/16984139
- Google Search generative AI control:
  https://support.google.com/webmasters/answer/16908024
- Bing Webmaster Tools AI Performance:
  https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
- OpenAI publisher and developer FAQ:
  https://help.openai.com/en/articles/12627856
- Perplexity crawler documentation:
  https://docs.perplexity.ai/docs/resources/perplexity-crawlers
