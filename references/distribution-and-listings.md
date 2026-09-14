# Audience-first distribution and listings

Use this reference when the user asks to launch, list, or submit a product to a
directory or community. The goal is qualified discovery and measurable customer
acquisition. A backlink is an incidental result, never a promised ranking gain.

Platform rules, prices, eligibility, and account requirements change. Recheck
the official submission page and community rules on the day of a campaign.
Third-party DR scores are directional vendor estimates, not Google metrics and
not acceptance criteria.

## Non-negotiable boundary

- Do not buy links, join link networks, add reciprocal badges for ranking value,
  fabricate reviews, solicit votes, evade moderation, or mass-submit.
- Never select “any signed-in email.” The user must intentionally identify the
  account or email for that platform. Do not extract or expose saved passwords,
  cookies, tokens, or session data.
- Account creation, final public submission, posts, comments, messages, and
  purchases require confirmation at the moment of the action. A prior general
  instruction does not remove that checkpoint.
- Hand CAPTCHA, OTP, MFA, passkeys, identity verification, and suspicious-login
  challenges to the user. Do not bypass them.
- Keep listing and outreach work outside `autonomous_safe`. An unattended cycle
  may research fit and prepare a packet, but may not create accounts or publish.
- Follow the current platform terms. If automation or unattended access is
  disallowed or unclear, switch to a manual handoff packet.

These rules align the workflow with Google's
[spam policies](https://developers.google.com/search/docs/essentials/spam-policies),
including its treatment of automated link creation and low-quality directory
links.

## Readiness and fit gate

Before opening a submission form, verify:

1. The product and chosen destination URL are public, stable, truthful, mobile
   usable, and have a working conversion path.
2. Pricing or availability, privacy, terms, contact/support, category, audience,
   and founder/company identity are explicit where applicable.
3. The technical quality gate has no unresolved blocker on the destination.
4. Claims, feature status, metrics, pricing, screenshots, and testimonials have
   an owner-approved source of truth.
5. The platform's current audience and eligibility match the product. A dev-tool
   community is not a generic SaaS directory; a prelaunch service is not a fit
   for every mature product.
6. The campaign has a measurement hypothesis: referral sessions, qualified
   signups, activation, conversion, assisted conversion, or useful feedback.

Do not impose arbitrary prerequisites such as a fixed number of alternative
pages, users, screenshots, reviews, or indexed pages. Prepare only the assets
the platform actually requires and the audience needs.

## Listing packet

Create one reviewed packet before browser work. Use
`examples/listing-packet.json` as the portable shape. It contains:

- exact identity/account choice and owner;
- canonical destination URL plus permitted campaign parameters;
- factual category, audience, pricing/availability, launch stage, and support;
- source-backed tagline, short description, long description, founder note,
  tags, and disclosures;
- owned logo, real screenshots, demo link, and optional launch card;
- platform fit, rule-check date, payment/reciprocity state, and required fields;
- confirmation, submission, moderation, live URL, and measurement states.

Stabilize facts first. When `$prose-humanizer` is installed, invoke it in
embedded mode to improve the listing copy without changing claims, dates,
prices, feature status, limitations, or disclosures. If it is unavailable, use
the skill's fidelity checklist. Never describe the result as undetectable or
pretend it was written from personal experience.

Prefer real owned assets. If an image is required and no suitable marketing
asset exists, the host may use its image-generation capability to create a
clearly promotional launch card or illustration, then show it to the user for
review. Never generate fake UI screenshots, customers, testimonials, awards,
metrics, integrations, or product capabilities.

## Browser adapter order

1. Use the host's supported visible browser/computer-use capability when it is
   available and the user wants browser assistance.
2. Otherwise use installed Playwright with a dedicated automation profile.
3. Use a user-started Chrome DevTools Protocol session only when needed and
   supported; CDP has lower fidelity than Playwright's native protocol.
4. If none is safe or allowed, provide the packet and exact manual steps.

Do not automate a browser's default personal Chrome profile. Playwright notes
that Chrome's default profile automation is unsupported; use a separate user
data directory. See the official
[BrowserType](https://playwright.dev/docs/api/class-browsertype) and
[authentication](https://playwright.dev/docs/auth) guidance.

For each platform: navigate, inspect the current rules, fill reversible fields,
upload reviewed assets, and stop immediately before account creation or public
submission. Show the exact identity, destination, copy, price, disclosures, and
button/action to the user. Continue only after action-time confirmation, then
record the result and live URL without claiming moderation approval.

## Seed platform registry

This is a dated routing seed, not a permanent truth. Revalidate every selected
platform before work.

### Founder-controlled launch or community channels

- **Product Hunt** — broad technology launch; personal account and current
  launch rules. Its official guide states that new accounts wait before posting
  and that launches are not limited to a mythical “best day.”
  [Official launch guide](https://www.producthunt.com/launch)
- **Hacker News Show HN** — only something the maker built that people can try;
  avoid routine announcements, landing-only pages, and vote requests.
  [Official Show HN guidance](https://news.ycombinator.com/showhn.html)
- **Peerlist Launchpad** — maker/project credibility and a weekly launch model;
  verify the required profile/project state.
  [Official Launchpad guide](https://help.peerlist.io/individual/launchpad/how-to-launch-a-project-on-peerlist-launchpad)
- **Indie Hackers** — founder story, milestone, or useful lesson when community
  rules permit. Its terms restrict some scraping and automated processes.
  [Products](https://www.indiehackers.com/products) · [Terms](https://www.indiehackers.com/terms)
- **r/SideProject** — founder-controlled community post; read current rules and
  flair requirements, participate honestly, and require final confirmation.
  [Current rules](https://www.reddit.com/r/SideProject/about/rules)

### Strong only when the product fits

- **BetaList** — prelaunch or recently launched products; current service is
  editorial and paid rather than a guaranteed free listing.
  [Official support](https://betalist.com/support)
- **AlternativeTo** — software alternatives; verified identity, moderation,
  and current promotional/link rules apply.
  [Official FAQ](https://alternativeto.net/faq/)
- **SaaSHub** — released English-language software/SaaS fitting its acceptance
  rules; not a generic waitlist or agency submission.
  [Official submission page](https://www.saashub.com/services/submit)
- **SourceForge** — qualifying business software in an existing category, with
  review/waitlist or paid options.
  [Official vendor page](https://sourceforge.net/software/vendors/new)
- **DevHunt** — developer tools with the required GitHub identity and repository
  workflow. [Official repository](https://github.com/MarsX-dev/devhunt)
- **OpenAlternative** — open-source alternatives only.
  [Official submission page](https://openalternative.co/submit)
- **SideProjectors** — use only when seeking a buyer or cofounder; it is a
  marketplace, not a generic backlink directory.
  [Official site](https://www.sideprojectors.com/)
- **Startup Stash** — verify current form, price, review time, and category
  before preparing the submission.
  [Official add-listing page](https://startupstash.com/add-listing/)

### Measured experiments

Revalidate **Uneed, Launching Next, Microlaunch, StartupBase, Startup Buffer,
PitchWall, Tiny Startups, TinyLaunch**, and similar launch catalogs. Use them
only when the current audience and moderation quality justify the time. Track
referrals and qualified outcomes; stop repeating channels that produce only a
link or bot traffic.

TinyLaunch currently advertises an agent interface, but OTP, plan selection,
payment, and final publication still require the owner at the checkpoint.
[TinyLaunch agent documentation](https://www.tinylaunch.com/agents)

### Disabled or unverified by default

Disable any service that sells dofollow-link packages, reciprocal homepage or
footer badges, bulk cross-site placement, or a “network” whose main value is
link equity. This includes the backlink-product behavior observed during the
2026-09 review of **Fazier, EarlyHunt, Aura++, Smol Launch, LaunchIgniter,
OpenHunts**, and some offerings associated with **Startup Fame** or **Tiny
Startups**. A future run may reclassify a platform only after current official
terms show a genuine audience-first use that avoids the link scheme.

Keep **Startup Ranking** and any platform whose official submission path cannot
be verified in `unverified` state. Do not guess a form or use a third-party
submission service.

## Measurement and maintenance

Record `planned -> packet_ready -> form_prepared -> confirmed -> submitted ->
under_review -> live | rejected | withdrawn`. Distinguish a submitted form from
an approved live listing. Recheck live facts after pricing, positioning, URLs,
or major product changes, normally quarterly rather than daily.

Use tagged URLs only where platform rules allow them. Measure referral quality,
signup, activation, conversion, assisted outcomes, and useful feedback. Keep
third-party authority metrics as optional context; never optimize to DR alone or
attribute an organic ranking change to a listing without a credible experiment.

