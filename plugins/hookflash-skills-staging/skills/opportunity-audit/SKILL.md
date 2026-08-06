---
name: opportunity-audit
description: Turn a GA4 property into a client-ready Opportunity Audit deck — pull the data, map the client's real conversion funnel, find where the money is leaking, and propose prioritised A/B tests with before/after mockups of each proposed change. Use when the user runs /opportunity-audit, asks for an opportunity audit, a CRO audit of a whole site, "where should we test first", a test backlog or roadmap from analytics, or points at a GA4 property and asks what to test. Works for lead gen and ecommerce. Not for reading a finished test's results — that is /tapa-results-analysis — and not for a single page's heuristic review, which is /hypothesis-ux-audit.
---

# Opportunity Audit

Point at a GA4 property, come away with a deck: what the data says, where the drop-off is, and a
prioritised set of test proposals with a mockup of each one. Lead gen or ecommerce, so long as the
tracking is decent.

The deck repeats one motif per opportunity — **data slide → observation slide → test card** — so its
length is a function of how many opportunities clear the bar, not a fixed page count.

## Prerequisites

1. **Tether connected** with the Tapa tools available. Check `tapa_funnel_get` and `tapa_shot_run`
   are in your tool list. If not, the user needs the `hookflash-skills` plugin installed and Tether
   authorised — say so and stop.
2. **GA4 access.** These tools run as the user's own Google grant. If a call returns a
   reconnect error, send them to `tapa.hookflash.co.uk/connect`.
3. **A browser you can drive** — only for a first-time audit on a client (Step 2). Later audits
   read the stored funnel spec and need no browser at all.

## Safety rules that are not negotiable

You will be driving a browser around a real client's live website. These are hard limits, not
preferences:

- **Never complete a purchase.** On ecommerce you may add to cart and reach the checkout page.
  Stop there. Never click pay, place order, confirm, or anything equivalent.
- **Never submit the final step of a lead form.** Walking forward through intermediate steps is
  fine and is the point. Submitting the last one creates a real lead in the client's CRM, fires
  their conversion tracking (which feeds Google Ads bidding and pollutes the very GA4 data you are
  about to analyse), and may trigger real emails or underwriting lookups. You already know the
  conversion event name from GA4, so there is nothing left to learn by pressing the button.
- **Never enter real personal data.** Obvious test values only (`test@test.com`, `Test`,
  `0000000000`). If a step demands something you cannot fake — a real registration number, a real
  policy number — stop and ask the user to walk that step themselves.
- **Use the in-app browser**, never Claude in Chrome. The in-app one has no access to the user's
  real sessions or saved cards, so there is no payment method to fire by accident.
- **Tell the user before the walk** that you will be moving through their client's funnel with test
  data, and let them confirm. Agencies generally have permission to do this; it is still better
  raised in advance.

## Step 1 — Ground the property and check for a stored spec

Ask only for what you cannot look up. You need a GA4 property and a date range.

1. Resolve the property. `tapa_ra_list_ga4_properties` lists what the user can reach. If they gave
   you a measurement ID or a site URL instead, `tapa_pf_find` resolves it.
2. **`tapa_funnel_get` with the property id.** This decides how much work the audit is:
   - **A confirmed spec exists** → skip Step 2 entirely. Go to Step 3.
   - **An unconfirmed spec exists** → show it to the user, ask them to confirm or correct it, then
     `tapa_funnel_put` with `confirmed: true`. Skip the walk.
   - **Nothing stored** → Step 2.
3. Default the date range to the **last complete calendar month**. Say which range you used on
   every slide, as the example deck does.

## Step 2 — Map the real funnel (first audit for a client only)

A GA4 property id does not tell you what converting means. `quote_start`, `begin_checkout`,
`generate_lead`, `form_submit_step3` — you cannot guess which matter or what order they come in,
and getting it wrong invalidates the whole audit. So derive it, then have a human confirm it once,
then store it forever.

### 2a. Derive candidates from GA4

- **If the standard ecommerce events are present** (`view_item`, `add_to_cart`, `begin_checkout`,
  `purchase`) the funnel is those, in that order. You are done deriving — go to 2c.
- **Otherwise** (lead gen, or custom ecommerce): list event names with
  `tapa_ra_list_ga4_event_names`, then use `answer_client_data_question` to get each event's
  **volume** and — this is the useful bit — **which page paths it fires on**. An event's page
  distribution tells you empirically where in the journey it sits, which is more reliable than its
  name and more reliable than asking the client, who often does not know.
- **Check the property's key events** (`get_ga4_property_config`). What the client marked as a
  conversion is the strongest single signal you have.
- Infer order from volume containment: if A fires on 100% of sessions, B on 26% and C on 17%, and C
  never appears without B, that is a funnel.

### 2b. Watch a human walk it

You need each step's URL and layout, and confirmation that the events fire where you think. Do not
click through yourself — bot protection challenges automated walks, and a human decides what is
safe to submit.

1. Open the site's homepage in the in-app browser.
2. Tell the user, in these terms: *"Walk the funnel the way a customer would, from here to just
   before the final submit. **Pause two or three seconds on each page** so I can capture what
   fired. Don't submit the last step."*
3. **After each page they land on**, run one JS call to read the tag traffic:

   ```js
   (() => {
     const r = performance.getEntriesByType('resource').map(e => e.name);
     const hits = r.filter(u => /\/g\/collect|\/ccm\/collect|google-analytics\.com\/(g|j|r)\/collect/i.test(u));
     return JSON.stringify({
       url: location.href,
       title: document.title,
       events: hits.map(u => {
         const q = new URLSearchParams(u.split('?')[1] || '');
         return { en: q.get('en'), tid: q.get('tid'), dl: q.get('dl'),
                  params: [...q].filter(([k]) => k.startsWith('ep.') || k.startsWith('epn.')) };
       }),
       dataLayerEvents: (window.dataLayer || []).map(o => o && o.event).filter(Boolean),
     });
   })()
   ```

   **Three things to know about this:**
   - Use `performance.getEntriesByType('resource')`, **not** `read_network_requests`. The network
     log misses tag traffic — it will hand you forty image requests and report no analytics hits on
     a page that fired plenty.
   - **The buffer resets on every page navigation**, which is why you must read once per page. On a
     single-page-app funnel it never resets and one read at the end gets everything.
   - **The collect endpoint is often first-party** (`metrics.client.com/g/collect`, not
     `google-analytics.com`) because of server-side tagging. Match on the path, as above. Record
     whichever host you actually saw — it goes in the spec.
   - The `tid` parameter gives you the measurement ID for free. Cross-check it against the property
     you resolved in Step 1; if they disagree, you are looking at the wrong property and everything
     downstream is wrong.
4. As they go, capture a screenshot of each step and note the URL.

### 2c. Confirm and store

Show the user the derived funnel as a short table — step, event, where it fires, the URL — plus the
page-type patterns you propose (home, product lander, PLP, PDP, blog…). Ask them to confirm or
correct it. **This is the one place you must ask.** Then `tapa_funnel_put` with `confirmed: true`.

Only set `confirmed: true` when a human has actually said yes. Every later audit trusts a confirmed
spec without asking again, so a confirmed guess quietly corrupts every audit after it.

## Step 3 — The scoped GA4 pass

Now that the funnel means something, pull the numbers. This is the analysis the deck is built on.
Use `answer_client_data_question` for the slices and `run_ga4_funnel_report` for step-to-step
drop-off.

Pull, at minimum:

| Slice | Why it earns a slide |
|---|---|
| Device × each funnel step | Where the volume is vs where the conversion is |
| Landing page × sessions × conversion rate | The pages worth testing at all |
| Landing page grouped by page type | Which *kind* of page carries the business |
| Channel group × sessions × conversion rate | Which traffic converts |
| Landing page × channel group | The combination effects — often the real finding |
| Step-to-step drop-off, whole funnel | Where the leak is |
| Step-to-step drop-off by device and by top landing pages | Whose leak it is |

Then run these checks before you interpret anything:

- **Plausibility.** Flag any rate that is impossible (>100%), any two near-identical pages with a
  wildly different rate (a 4x gap between `/car-insurance` and `/insurance/car` is a tracking or
  redirect artefact far more often than a UX finding), and any step whose completion rate exceeds
  the step before it. **Report these as data-quality findings. Do not write a test hypothesis on
  top of one.** This is the single biggest way an automated audit embarrasses itself.
- **Sampling and thresholding.** If a response came back sampled or thresholded, say so on the
  slide. Do not quietly present a sampled number as fact.
- **`(not set)` and Unassigned.** Report the bucket rather than dropping it; a large one is itself
  a finding.

## Step 4 — Find the opportunities, and drop the ones you cannot test

An opportunity is a **measured gap**: this page, device, or channel underperforms its comparable
peers, on real volume. Not "the CTA could be clearer".

Then apply the filter that keeps this honest. **For each candidate, work out the minimum detectable
effect at that segment's current traffic over a four-week run, and drop the candidates that cannot
reach significance.** A page doing 400 sessions a month cannot produce a significant result however
good the idea is, and a backlog full of unpowered tests is the standard failure of automated CRO.

Rough guide at 95% confidence and 80% power, two-sided, per variant: you need roughly
`16 × p(1-p) / (p × mde)²` sessions per variant. Compute it properly per candidate rather than
eyeballing it, state the MDE each surviving test can detect, and list what you dropped and why —
that list is genuinely useful to the client.

Rank what survives on: size of the measured gap × traffic affected × how directly it touches the
primary conversion.

## Step 5 — Design the tests

For each surviving opportunity, write a test card in the house format:

- **Hypothesis**, as IF / THEN / BECAUSE. The BECAUSE must cite the finding it came from, with the
  number. "BECAUSE only 24% of mobile sessions scroll far enough to see all products" — not
  "BECAUSE users prefer clarity".
- **Test type** (usually AB Test), **Pages**, **Audience**, **Primary metric**,
  **Secondary metrics** (bounce rate and the downstream conversion, so you catch a win that moves
  the top of the funnel and breaks the bottom).
- **Expected MDE** from Step 4.

Every card must trace back to a slide. If you cannot point at the data that motivated it, cut it.

Then prioritise, using the house weights: Expected uplift ×4, Data backed ×4, Development effort
×4, Traffic volume ×3, Strategic alignment ×2, Design effort ×2, Asset effort ×1.

## Step 6 — Screenshots and mockups

For each test card you need two images: the element as it is, and the element as proposed.

1. **Capture the current state** with `tapa_shot_run`. Pass `selector` for the element the test
   changes — that gives a clean shot of the actual element instead of a crop of a page shot at
   guessed coordinates. Batch the URLs (8 per call, desktop and mobile).
   - For a page you cannot reach from the server (behind a login or a part-filled form), use the
     screenshots you took during the Step 2 walk.
2. **Build the variation** with `tapa_var_run`: the capture's `filename`, a `region`, and a
   concrete instruction. Always pass a region — the region, not the instruction, is what stops the
   model redrawing the client's logo and grid. Region coordinates are pixels in the source image;
   use the `width`/`height` that `tapa_shot_run` reported, which for a full-page capture is not the
   same as CSS pixels.
3. **Look at every image before it goes near the deck** (ADR-0006). Check: did the model change
   only what you asked; is the brand intact; is there a consent wall still covering the hero; did a
   full-page shot come back with holes where lazy content had not loaded. If the variation drifted,
   tighten the region and run again. Two rounds, then fall back to showing the original with the
   change described in words — an honest description beats a wrong picture.

## Step 7 — Build the deck

Use `build_slide_deck` with the `hookflash_general` template. No new template is needed; these
layouts already do the job:

| Layout | Use | Placeholders |
|---|---|---|
| 19 | Section divider | `0` title |
| 15 | **Data slide** | `0` title, `13` chart, `14` findings bullets |
| 8 | **Observation slide** | `0` title, `13` screenshot, `15` commentary |
| 7 | **Test card** | `0` title, `13` Original image, `14` Variation image, `15` hypothesis + metrics |
| 28 | Closing summary | `0` title, `31`/`32`/`33` text blocks |

Charts go in `charts` with an `at`, and can target any placeholder. Images go in `images` with an
`at` and **must** target a PICTURE placeholder — on layouts 7 and 8 that is `13` and `14`.

**Every PICTURE placeholder must be consumed or the build 400s.** So a test card on layout 7 needs
*both* images: if you only have an Original, either put something real in `14` or use a different
layout. Do not fill it with a placeholder image.

Structure: title → what we looked at → then, per opportunity, data slide + observation slide + one
test card per test → prioritised backlog → appendix of the slices that did not earn a slide.

Then **review the returned thumbnails. Never deliver a slide you have not looked at.** Check for
overflowing text, collided boxes, cropped images, and empty placeholders. A 400 from the build
lists what is missing — fix and call again. Two rebuild rounds, then ship what you have and say
what is imperfect.

## Deliver

In chat: the headline findings as a short visual summary, the deck download link as plain text, the
count of tests proposed and dropped, and anything the data could not answer. Offer the funnel spec
as a note — "stored, so the next audit for this client skips the walk".

## Avoid these

- **Never invent behavioural evidence.** You have GA4 and screenshots. You do not have scroll maps,
  click maps or session recordings. If a hypothesis needs "users don't scroll", either get it from a
  GA4 `scroll` event or say the evidence is missing.
- **Never present a plausibility-flagged number as a finding.** It is a tracking bug until proven
  otherwise.
- **Never compare to "industry benchmarks".** We do not have a benchmark source. Compare segments
  within the property instead.
- **No em dashes in client-facing slide text.**
- **Never leave a template zone filled with filler.** Cut the slide instead.
- Do not promise a test will win. Say what it is designed to move and what it can detect.
