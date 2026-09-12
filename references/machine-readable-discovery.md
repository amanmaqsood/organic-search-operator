# Machine-readable discovery set

Use this route on the first automation run and whenever canonical public
content changes. The required set is `llms.txt`, `llms-full.txt`, and `ai.txt`
at the deployed origin root.

These files are an accessibility and discovery layer for compatible agents.
They are not a Google ranking factor, a substitute for crawlable HTML,
`robots.txt`, a sitemap, structured data, or an API, and they cannot guarantee
indexing, citations, or recommendations. Google currently says it ignores AI
text files for Search. OpenAI and Perplexity document crawler access through
`robots.txt`, not these files.

## First-run workflow

1. Detect the framework's source directory that deploys files at `/`. Do not
   edit a generated build directory when the repository has a public source
   directory or generator.
2. Inventory public, canonical, indexable pages. Exclude authenticated,
   personalized, draft, preview, `noindex`, duplicate, redirected, expired,
   private, licensed-without-redistribution, and regulated content that should
   not be replicated.
3. Create `.organic-search/machine-readable.json` from the source of truth. Each
   page needs a title, canonical URL, concise description, and faithful public
   Markdown content. Set `public`, `canonical`, and `indexable` to `true` only
   after checking them.
4. Configure the public source directory:

   ```text
   python <skill>/scripts/seo_operator.py configure-machine-readable \
     --project <repo> --output-directory <public-source-directory>
   ```

5. Preview, review conflicts, then generate:

   ```text
   python <skill>/scripts/machine_readable.py generate --project <repo>
   python <skill>/scripts/machine_readable.py generate --project <repo> --apply
   python <skill>/scripts/machine_readable.py check --project <repo>
   ```

6. Run the repository build and verify live HTTP 200 responses for
   `/llms.txt`, `/llms-full.txt`, and `/ai.txt`. Confirm that every listed URL
   resolves to the intended canonical page.

In `review_first`, generation creates a reviewable local change but does not
publish it. In `autonomous_safe`, the coordinated three-file generation counts
as one work item and may proceed only when the ordinary clean-worktree,
validation, deployment, live-verification, and rollback gates pass.

## File contracts

### `llms.txt`

Generate a concise CommonMark index following the community `llms.txt`
proposal: one site heading, one summary, and grouped links with truthful
descriptions. Include the canonical origin, content date, sitemap, robots file,
and `llms-full.txt` link. Keep it curated rather than dumping every URL.

### `llms-full.txt`

Generate a faithful Markdown corpus for the public canonical pages in the
manifest. The default size limit is 1,000,000 UTF-8 bytes and is configurable
between 10,000 and 5,000,000 bytes. If the corpus exceeds the limit, improve
selection or split the source architecture before increasing the limit. Do not
silently truncate content or replace it with unsupported summaries.

### `ai.txt`

Generate the operator's explicitly experimental publisher manifest. State that
it is not a universal standard or ranking signal. Link the canonical origin,
robots policy, sitemap, both LLM files, and authoritative pages. State that the
canonical HTML wins on disagreement and that the file does not grant training,
copyright, licensing, reuse, endorsement, or other permissions.

Do not use `ai.txt` to override `robots.txt`, page-level directives, terms, or
law. Because multiple incompatible `ai.txt` proposals exist, do not claim
support by Google, OpenAI, Anthropic, Perplexity, or another platform without
current first-party documentation.

## Ownership and updates

The generator writes `.organic-search/machine-readable-state.json` with source
and output hashes. On later runs it rewrites only changed generator-owned
files. It refuses to overwrite an unmanaged existing file or a generated file
that someone edited outside the generator. Reconcile that conflict in review
instead of forcing an overwrite.

Refresh the manifest and generated files when any included page's facts,
pricing, availability, canonical URL, public/indexable state, or substantive
content changes. Do not change dates without a substantive source change. A
daily run may return `current` and make no commit.

## Beyond text files

Treat OpenAPI, public REST APIs, CLI commands, MCP servers, and Markdown
catalogs as product capabilities, not SEO decorations. Recommend them only when
the product has stable public data or actions, authentication and rate limits
are understood, sensitive fields are excluded, documentation is maintainable,
and users or agents have a real task to complete.

Official and primary references:

- Google generative AI Search guidance:
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- OpenAI publisher discovery guidance:
  https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Perplexity crawler guidance:
  https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- Community `llms.txt` proposal: https://llmstxt.org/
