# Search provider setup

## Google Search Console

### Property selection

Use the exact property identifier returned by Search Console:

- Domain property: `sc-domain:example.com`
- URL-prefix property: `https://www.example.com/`

Prefer a domain property when the user owns DNS. Do not construct or claim a
property exists without listing accessible properties or confirming it in the
authenticated UI.

### Authentication

Use an existing working connector when available. Otherwise use gcloud
application-default credentials. Start read-only when only reporting:

```text
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly,openid,https://www.googleapis.com/auth/userinfo.email
```

Sitemap mutation and URL Inspection require the broader Search Console scope:

```text
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters,openid,https://www.googleapis.com/auth/userinfo.email
```

Add broader Google Cloud scopes only when a separate required operation proves
they are necessary. Never print the access token to chat or logs. Verify access
by making a harmless API call and reporting only its status.

When ADC has a quota project, send it through `X-Goog-User-Project`. The bundled
GSC script reads that value from the ADC file.

### Verification

DNS verification is an external mutation:

1. obtain the exact TXT or CNAME record from an authenticated Google flow;
2. record its host, type, value, requested TTL, and current verification state;
3. prepare the DNS change;
4. request approval immediately before saving it;
5. wait for propagation and recheck;
6. mark verified only after Google confirms it.

Use an authenticated browser only when the API or connector cannot complete the
property or verification step. Never invent verification values.

### Data collection

Record the requested date range, `finalDataThrough`, and the first incomplete
date. Store partial dates but exclude them from complete-period comparisons.

Collect useful views separately:

- totals by date;
- query plus page;
- page only;
- country;
- device.

Do not average already aggregated CTR or position values. Recompute rates only
from compatible clicks and impressions, and preserve the API's aggregation
semantics.

### Inspection and sitemap behavior

The URL Inspection API reports index status. It does not request indexing for a
normal landing page or article. Use it selectively for the primary landing URL,
new or refreshed URLs, anomalous templates, and representative failures.

The Google Indexing API is not a general indexing API. Use it only when the page
qualifies under Google's supported JobPosting or livestream BroadcastEvent
policy.

Submit a sitemap only after approval and only if it is new or materially
changed. Submission does not guarantee crawling or indexing.

## Optional Ahrefs or commercial SEO-data API

Use a commercial provider only when the project already has licensed access or
the user explicitly chooses it. Keep credentials in the host secret store or
environment, never in repository configuration, cached reports, commits, or
tool output.

For a weekly audit, request only the endpoints and rows needed to compare
organic keywords, estimated traffic, competing pages, referring domains, and
lost or gained links. Cache the provider response with its retrieval time,
database, market, mode, and units. Respect row and credit limits.

Keep these metrics separate from Search Console. Ahrefs-style keyword and
traffic values are third-party estimates; GSC reports the site's Google Search
performance. Do not sum, average, or present the two as one dataset. Use the
commercial data to discover or corroborate an opportunity, then measure the
site's outcome with GSC and conversion evidence.

The weekly audit must continue with GSC, repository, and live-site evidence when
the optional provider is unavailable, rate-limited, or out of credits. Record
the exact provider state instead of substituting zero.

## Bing and IndexNow

Prefer IndexNow for canonical URLs added, changed, or deleted after a verified
production deployment.

1. Generate a key once.
2. Host the key file at an allowed location on the production origin.
3. Verify the live key file exactly.
4. Submit only URLs on the configured host.
5. Record response, URL count, and timestamp without logging credentials.

Use `scripts/indexnow.py` in dry-run mode first. Add `--apply` only after the live
deployment and either explicit review-first approval or authorization by every
`autonomous_safe` gate. Autonomous use also requires IndexNow to have been
enabled and verified before the run. A successful response acknowledges
submission, not indexing.

The Bing Webmaster URL Submission API may be used when an existing project
already supports it, but IndexNow is the default. Respect quotas and prioritize
the newest or materially refreshed canonical URLs.
