# Content and editorial policy

## Page gate

A new page must have all of the following:

- distinct, evidenced search intent;
- a defined relationship to the primary landing page;
- a reason to exist beyond what already ranks or already exists on the site;
- original or first-party value such as product evidence, screenshots, tested
  steps, data, expert input, templates, calculators, or specific examples;
- a conversion role and internal-link plan;
- sources appropriate to the claim and topic risk;
- no unresolved cannibalization;
- a measurement hypothesis and review date.

If the page fails, refresh an existing URL, merge the idea, keep it as a
candidate, or reject it.

## Drafting

Match the format and depth to intent. Do not impose a universal word count,
heading count, FAQ, schema type, or image count. Every section and media asset
must help the user complete the task or evaluate the product.

Use only verified claims. Never invent first-hand experience, customer results,
rankings, comparisons, quotes, reviews, awards, or statistics. Clearly label
hypotheses and estimates.

Audit claims for specificity, but do not force every claim into a number. A
numeric claim must identify what was measured, for whom, over what period, and
where the evidence lives. When proof is absent, replace vague hype with a
precise qualitative statement or mark the claim for founder review.

For question-led pages, provide the useful answer early and qualify it as the
topic requires. Do not enforce an arbitrary first-100-words rule, especially
when safety, legal, or factual context is necessary.

Use comparison, alternative, location, and programmatic pages only when each URL
has independently useful content. Variable substitution is not unique value.

Comparison, alternatives, and best-tools pages also require transparent
selection criteria, current verifiable facts, balanced treatment, and disclosure
of the publisher's relationship to the products. Never present estimated
traffic value as revenue or claim that an AI system will repeat the page.

Industry, budget, role, and use-case pages must address materially different
buyer needs with distinct proof and examples. If the answer would mostly repeat
another page, add a section to that page instead.

Reddit-intent pages are controlled experiments. Check GSC and the current SERP
first. Prefer adding a useful section to an existing page. Do not copy posts or
comments, imply Reddit affiliation, or treat community anecdotes as authority
for factual claims.

## Sensitive topics

For health, medical, pregnancy, medication, finance, legal, safety, childcare,
food, supplements, or other high-stakes topics:

- use primary regulators, national health bodies, official labels, standards,
  and peer-reviewed sources as appropriate;
- preserve qualifications, contraindications, dates, and uncertainty;
- avoid personalized advice and unsupported safety claims;
- include professional guidance when the evidence or user decision requires it;
- require human review before publication.

## Prose pass

Preferred path: invoke `$prose-humanizer` in embedded mode after the factual
draft is stable. Ask it to preserve the source ledger, citations, URLs, names,
numbers, dates, modality, chronology, causality, limitations, and required
technical language.

Fallback path when that skill is unavailable:

1. build an atomic claim and citation ledger;
2. remove empty setup, inflated significance, vague authority, sales varnish,
   forced patterns, false suspense, prompt residue, and generic conclusions;
3. keep supported specificity and the project's real voice;
4. diff the output against the ledger;
5. fail the edit if it adds a narrator, experience, causal claim, metric,
   comparison, endorsement, or certainty not present in the evidence.

Never describe content as undetectable, human-authored, or guaranteed to pass a
detector. The target is faithful, specific, useful prose.

## Page completion

Verify metadata, canonical, structured data when eligible, accessible media,
internal links in both directions, CTA alignment, mobile rendering, source
quality, build output, and live behavior. Preserve facts and citations through
all generators.

For internal links, choose existing pages whose readers genuinely benefit from
the destination and use descriptive natural anchors. There is no universal link
count. Record the source URLs so the change can be reviewed and measured.
