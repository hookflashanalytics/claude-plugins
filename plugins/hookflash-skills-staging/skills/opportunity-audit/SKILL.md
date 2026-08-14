---
name: opportunity-audit
description: Turn a GA4 property into the data foundation of an Opportunity Audit — map the client's real conversion funnel, pull every split that could inform testing (funnel steps, landing pages, page types, channels, sources, devices and more), and deliver an Excel workbook of all the data pulled plus a tab of prioritised test hypotheses with the reasoning and the exact numbers behind each. Use when the user runs /opportunity-audit, asks for an opportunity audit, a CRO audit of a whole site, "where should we test first", a test backlog or roadmap from analytics, or points at a GA4 property and asks what to test. Works for lead gen and ecommerce. Not for reading a finished test's results — that is /tapa-results-analysis — and not for a single page's heuristic review, which is /hypothesis-ux-audit.
---

# Opportunity Audit (data-foundation phase)

Point at a GA4 property, come away with a workbook: every split of the data worth pulling, where
the drop-off is, and a prioritised set of test hypotheses, each one citing the tab and the number
it came from.

**Why a workbook and not a deck.** The experimentation team is reviewing whether this audit stands
on good foundations — does it find the right funnel, and does it pull a comprehensive enough set of
data to inform good tests? So this phase delivers the foundation itself, fully inspectable, rather
than the deck built on top of it. The deck build (screenshots, mockups, `build_slide_deck`) is
parked, not gone; its steps live in this file's git history and return once the team signs off.

The bias of this phase is **comprehensiveness over curation**. A slice that turns out to show
nothing still goes in the workbook — it is evidence of what was checked.

## Prerequisites

1. **Tether connected** with the Tapa tools available. Check `answer_client_data_question` and
   `tapa_ra_list_ga4_properties` are in your tool list. If not, the user needs the
   `hookflash-skills` plugin installed and Tether authorised — say so and stop.
2. **GA4 access.** These tools run as the user's own Google grant. If a call returns a
   reconnect error, send them to `tapa.hookflash.co.uk/connect`.
3. **A session that can write files** — the workbook is built locally with Python + openpyxl
   (Cowork or Claude Code). If you cannot create files in this session, say so and stop rather
   than delivering tables pasted into chat.
4. **A browser you can drive** — every audit maps the funnel by walking it (Step 2). If there is
   no browser, there is a defined degradation below; do not abandon the audit.

## Safety rules that are not negotiable

You drive the walk yourself (Step 2b), on a real client's live website, in a browser that may hold
the user's real logins and saved cards. You are browsing and adding to a basket, nothing more.
These are hard limits, not preferences:

- **Stop at the last step before money or a submitted record.** For ecommerce that means you may
  browse, add to cart, open the cart and enter the checkout, and you stop when a payment method,
  card field, or place-order control is on screen. For lead gen you may open the form and move
  through intermediate steps, and you stop before the final submit. **The stop is the point of the
  walk, not an interruption of it** — everything past it is the one thing you must not do.
- **Never complete a purchase.** Never click pay, place order, confirm order, buy now as a final
  step, or anything equivalent, in any circumstance, however the page is worded. If you are unsure
  whether a control commits the order, it does — do not click it.
- **Never submit the final step of a lead form.** It creates a real lead in the client's CRM, fires
  their conversion tracking (which feeds Google Ads bidding and pollutes the very GA4 data you are
  about to analyse), and may trigger real emails or underwriting lookups. You already know the
  conversion event name from GA4, so there is nothing left to learn by pressing the button.
- **Never enter real personal data, and never enter payment details at all.** Where an intermediate
  step needs a value to move on, use obvious test values (`test@test.com`, `Test`,
  `0000000000`). Card numbers are never test values — if a step will not advance without one, you
  have reached the stop line.
- **Never sign in, create an account, or accept terms.** If the funnel requires a login, stop and
  hand that step to the user.
- **Say what you are doing, then do it.** Post one line naming the route and the stop line, and
  start walking. Do not wait for permission: the user asked for this audit, agencies have
  permission to use their clients' funnels, and nothing before the stop line needs a human
  decision. The stop line is what keeps the walk safe, not a confirmation prompt.

**Your walk fires real events into the client's GA4** — a `view_item`, an `add_to_cart`, probably a
`begin_checkout`, in the property you are about to analyse. One session against a month of traffic
changes nothing measurable, but do not repeat the walk more than you need to, and never walk a
funnel to "see what happens" outside Step 2.

### Which browser

Use whichever browser tooling this session has. **Do not stop to ask the user to choose, and do not
abandon the walk because a particular browser is missing.**

- **A sandboxed in-app browser, if present** — first choice, and more so now that you are the one
  clicking. It carries none of the user's logged-in sessions or saved cards, so a checkout page
  cannot be pre-filled with real payment details.
- **Claude in Chrome, if that is all there is** — acceptable, with one extra precaution. It is the
  user's real browser: saved cards, saved addresses, and a possible existing basket. Say so once as
  you start — a statement, not a question — and note that a private window is cleaner if the client
  is a site they actually shop on. Carry on without waiting for an answer. Here the stop rule is
  the only thing standing between the walk and a real order, so treat it as absolute rather than as
  guidance.
- **Neither available** — do not block. Ask the user to walk the funnel in their own browser and
  send you the step URLs and a screenshot per step, then carry on at Step 2c. You lose the event
  trace, so lean harder on the GA4 evidence in 2a, and say at handover that the funnel was
  confirmed from the user's account of the walk rather than from observed tag traffic.

## Step 1 — Ground the audit

You need five things before you touch the data: a **GA4 property**, a **URL to start from**, **what
converting means on this site**, a **date range**, and **which channel grouping to report on**. Look
up what you can, then ask once for the rest.

1. Resolve the property. `tapa_ra_list_ga4_properties` lists what the user can reach. If they gave
   you a measurement ID or a site URL instead, `tapa_pf_find` resolves it.
2. **Look up the property's channel groupings before you ask about them.**
   `list_ga4_metrics_and_dimensions` returns the dimensions *this property* actually has, custom
   ones included, so it tells you whether a custom channel group exists and what its API name is.
   Never guess that name — read it from the listing. Look for every dimension whose name or UI name
   mentions a channel group: the default (`sessionDefaultChannelGroup`), the primary grouping, and
   any custom grouping the client has built. Then you can ask a specific question instead of a
   vague one.
3. **Ask for whatever the user has not already given you — in one message, not a series of them.**
   Four things:
   - **The URL to start the funnel walk from.** Usually the homepage, but plenty of clients want
     the audit aimed at a campaign lander, a category, or one product line. Starting in the wrong
     place wastes the walk.
   - **What kind of funnel this is: ecommerce, lead gen, or something else.** If something else,
     ask them to name the converting action in a few words — book a viewing, start an application,
     register an account, donate.
   - **The date range**, offering the last complete calendar month as the default so they can
     simply accept it. Say the actual dates rather than the words, so a "yes" is unambiguous.
     Longer ranges make sampling and thresholding more likely, and every extra day lands on the
     daily tabs, so it is worth them choosing deliberately rather than discovering it later.
   - **Which channel grouping to report on**, naming what you found in step 2 — "this property has
     a custom channel group called X as well as GA4's default: default, custom, or both?" If a
     custom grouping exists, **both** is the default answer and the one to assume if they do not
     answer that part: a client with a custom grouping generally reads their reports in it, and the
     default grouping is what makes the numbers comparable to every other audit.

   Ask even when the site looks obvious. Inferring the funnel from the domain is the single biggest
   way this audit goes wrong: it maps a plausible funnel that is not the one the client is judged
   on, and every number after that is answering the wrong question. A few sentences from the user
   removes it. Anything they have already said in their brief, do not ask again — this is one
   message covering only the gaps.
4. Record the date range and the channel grouping on the workbook's README tab, and the date range
   on every data tab.

## Step 2 — Map the real funnel

A GA4 property id does not tell you what converting means. `quote_start`, `begin_checkout`,
`generate_lead`, `form_submit_step3` — you cannot guess which matter or what order they come in,
and getting it wrong invalidates the whole audit. So derive it from the data, walk it, and have the
user confirm it before you pull anything.

**Every audit maps the funnel fresh.** Nothing is stored between runs and nothing is looked up.
Opportunity audits are a new-client exercise, run about once per client, so there is almost never a
previous spec to reuse — and a spec that has been sitting around since the site was last redesigned
is worse than no spec, because it is trusted without being checked.

### 2a. Derive candidates from GA4

The funnel type the user gave you in Step 1 says which way to go. It is a starting point, not the
answer: confirm it against the events actually present, and if the data flatly contradicts what
they said, tell them rather than quietly following either one.

- **Ecommerce, standard events present** (`view_item`, `add_to_cart`, `begin_checkout`, `purchase`)
  — the funnel is those, in that order. You are done deriving; go to 2c.
- **Lead gen, or ecommerce on custom events, or something else** — list event names with
  `tapa_ra_list_ga4_event_names`, then use `answer_client_data_question` to get each event's
  **volume** and — this is the useful bit — **which page paths it fires on**. An event's page
  distribution tells you empirically where in the journey it sits, which is more reliable than its
  name and more reliable than asking the client, who often does not know. Read the candidates
  against the converting action the user named: the event that marks *that* action is the bottom of
  the funnel, and the steps are what reliably precedes it.
- **Check the property's key events** (`get_ga4_property_config`). What the client marked as a
  conversion is the strongest single signal you have.
- Infer order from volume containment: if A fires on 100% of sessions, B on 26% and C on 17%, and C
  never appears without B, that is a funnel.

### 2b. Walk it yourself

You need each step's URL and layout, and confirmation that the events fire where you think. **Walk
it yourself.** You know from Step 1 whether this is ecommerce, lead gen or something else, and you
know the converting action, which is enough to find the route without being led through it. Do not
hand the clicking to the user and wait — that turns a two-minute job into a ten-minute one and
often stalls entirely when they step away.

1. Open the starting URL from Step 1 in whichever browser this session has (see [Which
   browser](#which-browser)).
2. Post one line saying the route you are taking and where you will stop — then start walking in
   the same turn. It is a note to the user, not a question to them, so do not end the turn on it.
3. **Follow the route for the funnel type.** These are the shapes; adapt to the site in front of
   you rather than forcing it to match.

   | Funnel type | Route | Stop at |
   |---|---|---|
   | **Ecommerce** | Home → a category / PLP → a product page → add to cart → open cart → begin checkout → the first checkout step (email, address, shipping) | The moment a payment method or card field appears |
   | **Lead gen** | Home → the service or offer page → open the form → complete intermediate steps with test values → the final step | Before the final submit |
   | **Something else** | Home → the page that starts the action the user named → forward through each step | Before the step that commits the record |

   Pick the *obvious* path a customer would take: a mainstream category, a best-seller or featured
   product that is in stock, the standard form. You are mapping the common journey, not an edge
   case. If the product you picked is out of stock or the path dead-ends, back up and take another.

4. **After every navigation**, run one JS call to read the tag traffic:

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

   **Four things to know about this:**
   - Use `performance.getEntriesByType('resource')`, **not** `read_network_requests`. The network
     log misses tag traffic — it will hand you forty image requests and report no analytics hits on
     a page that fired plenty.
   - **The buffer resets on every page navigation**, which is why you must read once per page. On a
     single-page-app funnel it never resets and one read at the end gets everything.
   - **The collect endpoint is often first-party** (`metrics.client.com/g/collect`, not
     `google-analytics.com`) because of server-side tagging. Match on the path, as above. Note
     whichever host you actually saw — it is a tracking observation, so it goes in the handover
     message, not in the workbook.
   - The `tid` parameter gives you the measurement ID for free. Cross-check it against the property
     you resolved in Step 1; if they disagree, you are looking at the wrong property and everything
     downstream is wrong.
5. Capture a screenshot of each step as you go, and note its URL.

**Keep the commentary to one line per step.** "Step 3: added to cart, `add_to_cart` fired" is the
whole update. The user is waiting to confirm a funnel, not reading a transcript of your reasoning —
what you inferred, what you tried and what the tag setup implies is held back for the handover
message at the end (see [Deliver](#deliver)), not narrated into chat as you go.

**When the walk blocks, hand that one step over — do not abandon the walk.** A bot challenge, a
login wall, a step that needs a real registration or policy number: say which step and what it
needs, ask the user to get you past that one thing, and carry on yourself from the other side. The
same goes for anything you judge to be past the stop line. Handing over a step is normal; handing
over the whole walk is what this step exists to avoid.

### 2c. Confirm before you pull

**The confirmation is a table. Not a description of a table, and not a paragraph the user has to
read to find the funnel in.** They are being asked one question — is this the right journey — and
they should be able to answer it from a single glance at four columns.

Post exactly this, in this order, and nothing else:

1. **One sentence** saying where the funnel came from ("Derived from GA4 key events and confirmed by
   walking the site").
2. **The table.** One row per step, in funnel order:

   | Step | Event | Page URL | Users in range |
   |---|---|---|---|
   | 1 | `view_item_list` | `/collections/all` | 84,204 |
   | 2 | `view_item` | `/products/…` | 48,210 |
   | 3 | `add_to_cart` | `/products/…` | 17,538 |
   | 4 | `begin_checkout` | `checkout.client.com/…` | 4,982 |
   | 5 | `purchase` | `checkout.client.com/thank-you` | 1,331 |

   Those four columns and no others. The URL is the page the event actually fires on, as you observed
   it in the walk — a real path, not a description of one ("the PDP"). Users in range is there
   because a funnel that does not descend is a funnel in the wrong order, and that is the single
   most useful thing on the row for spotting it.
3. **The page-type patterns** you propose, as one short line each: `PDP: /products/*`.
4. **Notes, only if there is something the user must know to answer** — at most three, one line
   each, no paragraphs. "Checkout is on a Shopify domain, so client-side tag capture came back empty;
   GA4 does record `begin_checkout` and `purchase`."
5. **The question**, one line.

**Everything else you learned waits for the handover, and none of it goes in the workbook.** Tag
architecture, CSP behaviour, which sub-report carried the metrics, what you tried before it worked,
how you reasoned your way to the route — all of it is real and some of it is a genuine finding, and
none of it belongs in a confirmation prompt. Keep it for the tracking observations at
[Deliver](#deliver), where it is two or three sentences to the person who ran the audit. **It does
not become a tab or a block in the workbook.** The workbook goes to the experimentation team, who
are reading it to decide what to test; how the client's tags are wired is not their question, and a
Tracking notes block sitting above the drop-off tables is the first thing they have to scroll past.
The same restraint applies during the walk itself: one line per step at most, not a running
commentary on what you are inferring.

**Wait for a yes.** This is the second and last thing you ask them, and it is the one that protects
the audit: everything from Step 3 on is measured against this funnel, so a wrong step here does not
produce a slightly-off workbook, it produces a confident workbook about the wrong journey. Carry the
confirmed funnel forward in this session and record it on the workbook's Funnel tab. Nothing is
saved for next time.

## Step 3 — The comprehensive GA4 pass

Now that the funnel means something, pull the numbers. This pass feeds the workbook, and the
workbook has no space constraint, so the deck-era instinct to pull only what earns a slide does not
apply. **Pull every slice below, at full depth** — full tables, not top tens. If a tool response
comes back truncated or row-limited, say so on that slice's tab rather than presenting the part as
the whole. Use `answer_client_data_question` for the slices and `run_ga4_funnel_report` for
step-to-step drop-off.

| Slice | What it can reveal |
|---|---|
| Step-to-step drop-off, whole funnel | Where the leak is |
| Step-to-step drop-off by device and by channel group | Whose leak it is |
| Each funnel step × device category | Where the volume is vs where the conversion is |
| Each funnel step × channel group | Which traffic gets how deep |
| Landing page × sessions × conversions × conversion rate† | The pages worth testing at all |
| Landing page grouped by page type | Which *kind* of page carries the business |
| Landing page × device | A page that converts on desktop and dies on mobile |
| Landing page × channel group | The combination effects — often the real finding |
| Channel group × sessions × conversion rate† | Which traffic converts |
| Session source/medium × sessions × conversion rate† | The grain below channel group — where the paid and referral stories hide |
| Campaign × sessions × conversion rate† (where paid traffic exists) | Which spend lands on which pages |
| Device category × sessions × conversion rate† | The headline device split |
| New vs returning × sessions × conversion rate† | Whether the funnel serves first-time visitors |
| Country × sessions × conversion rate† | Whether one market drags the average |
| Daily sessions and conversions across the range | Seasonality, launch spikes, tracking gaps |
| **Daily event counts, top 20 events** | Which behaviours move together, and which day a tracking change landed |
| **Item name × items viewed / added to cart / purchased** (ecommerce) | Which products lose people, and where |

**† Every "conversion rate" in that table is a workbook calculation, never a metric you ask GA4
for.** Pull the two counts — `sessions` (and `totalUsers`) with `keyEvents` — and divide in the
workbook. Asking for `sessionKeyEventRate` or `userKeyEventRate` directly costs you the de-sampling
below, so the tab comes back an estimate for no gain.

**Both broken-down drop-offs come from `run_ga4_funnel_report` with `breakdown_dimension` set** —
`deviceCategory` for one, the chosen channel dimension for the other, `breakdown_limit` up to 15.
Not from an event-count slice broken down by the same dimension. It looks like the same table and it
is not: the funnel report counts users who reached step N *having passed through the steps before
it*, so its per-step counts nest and its completion rates are real. Event counts do not nest — a
channel whose users mostly skip the collection page and land straight on a PDP produces
`view_item ÷ view_item_list` of **1,400%**, which is arithmetic, not a funnel. If a breakdown value
the user cares about falls outside `breakdown_limit`, run the funnel again filtered to that value
rather than reconstructing it from event counts.

**Wherever a slice is broken down by channel, use the grouping the user chose in Step 1.** If they
asked for both, that slice gets **two tabs** — one per grouping, each named for the grouping it
uses — not one tab with the two mixed. A custom grouping is the client's own definition of their
traffic and the default is what makes the audit comparable to every other one; they answer different
questions, so they get different tabs.

### The two tabs from the review

**Daily event counts.** Rank the property's events by volume over the range, drop the ones that
carry no signal for this purpose, and pull the top 20 that remain, by day:

- **Excluded from the ranking:** `session_start`, `page_view`, `user_engagement`, `begin_checkout`,
  `add_shipping_info`, `add_payment_info`. The first three swamp any list by construction; the last
  three are funnel steps that already have their own tabs and their own drop-off analysis.
- Dates down the rows, one column per event, a total row at the top under the context line, ordered
  by event volume descending so the widest columns are nearest the dates.
- This is one `answer_client_data_question` call using `pivots` — `date` down, `eventName` across,
  `eventCount` as the metric — with the excluded events removed by a `not` dimension filter on
  `eventName`, and the pivot limited to 20 values ordered by `eventCount`.
- **A pivot cannot be de-sampled.** If the pivot comes back sampled, re-pull it as a flat
  `date` × `eventName` × `eventCount` table with `desample` set and build the grid yourself in the
  workbook — same tab, exact numbers. Only leave it as a sampled pivot if that flat pull also comes
  back an estimate, and then say so on the tab.

**Item performance** — ecommerce only, skip it for lead gen. `itemName` against `itemsViewed`,
`itemsAddedToCart` and `itemsPurchased`, full table, with two rates computed in the workbook:
add-to-cart rate (added ÷ viewed) and purchase rate (purchased ÷ added). Put each rate immediately
to the right of the count it is derived from, so a reader can follow one product across the row.
Include the property total as the first row, labelled, so a product's share is readable.

If the property has no item-scoped data — an ecommerce site whose `view_item` events carry no items
array is common — the tab still exists and its context line says the metrics returned empty and why
that is a tracking finding, not an absence of products. Do not deliver a blank grid with no
explanation, and do not quietly drop the tab.

### Ask GA4 for exact numbers, not estimates

**Set `desample` on every `answer_client_data_question` slice you pull.** These numbers go into a
workbook the client's experimentation team will read as fact, and GA4 hands back a sampled estimate
in exactly the same shape as an exact answer. With `desample` set, a sampled query is re-run across
acquisition-cohort buckets and summed, which is exact; an unsampled query costs nothing extra, so
there is no reason to leave it off.

It has three limits worth knowing before you design a query:

- **It only works on additive count metrics.** Ask for `sessions`, `totalUsers`, `keyEvents`,
  `eventCount`, `itemsViewed` and compute the rates yourself in the workbook. A query that asks GA4
  for a rate metric directly cannot be de-sampled — you would be adding percentages together — and
  the tool will tell you it declined. This is the same reason the workbook stores rates as
  fractions computed from two counts.
- **`metric_filters` block it**, because GA4 applies them inside each bucket, so a row that only
  clears the threshold in total would disappear. Pull the rows and filter them yourself.
- **`run_ga4_funnel_report` has no `desample` parameter at all**, and neither does a pivot. Do not
  go looking for one and never say you set one. Both still report their own completeness, so a
  sampled answer from either can be *recorded* — but only one of them can be *fixed*.

**A sampled funnel has no workaround, and the workbook has to say so.** A pivot does: re-pull it
flat and de-sample that (see the daily-events tab above), same tab, exact numbers. A funnel does
not. Shortening the range or dropping the breakdown may well return an unsampled answer, but it is
an answer to a *different question* — a shorter range is not the range the rest of the audit reports
on, and a funnel without its breakdown is not the tab you were asked for. That is a trade, not a
fix, and it must never be presented as one. So when a funnel answer comes back sampled, record it in
three places and move on:

1. The **Funnel tab's context line**, on the drop-off block it applies to.
2. Its row on **Data completeness**, with `no workaround: GA4 cannot de-sample a funnel report` in
   the notes column. A sampled row with an empty notes column reads as an oversight; this is the one
   case where the reader needs to know that nothing was left undone.
3. **One sentence at handover.**

Every step-to-step rate on a sampled funnel tab is then an estimate. It can still motivate a
hypothesis, but it cannot be the sole evidence for one, and Step 4 says so in that candidate's
reason column.

**Read `data.completeness` on every response and keep it** — one record per slice. It carries
whether the answer was sampled and how much was read, whether it was de-sampled and whether that
came out exact, whether rows were **thresholded** (withheld for privacy, so the totals are genuinely
short), whether a cardinality `(other)` row swallowed the tail, and whether the table was truncated.
These become the Data completeness tab, and you cannot reconstruct them afterwards.

If a response comes back with **no `completeness` block at all**, the connected Tether predates this
and cannot tell you. Do not block and do not guess: build the tab with `unknown` in every column,
and say at handover that this run cannot report sampling because the Tether connection needs
updating. An `unknown` a reader can see beats a blank that reads as "fine".

**A missing value inside the block gets the same treatment.** `percentRead` is `null` whenever GA4
returned no sampling metadata for that query, which is common and is not the same thing as 100%.
Write `unknown` in that cell, not a blank and not an assumed 100 — the row is still meaningful,
because `sampled: false` alongside it is GA4 saying it did not sample.

**Pull `totalUsers` alongside sessions on every slice, and converting users alongside conversions.**
Step 4 powers its tests on users, because that is what a test randomises on, and it cannot go back
for them later without re-running the whole pass. A slice with sessions but no users forces an
estimate onto every candidate that comes from it.

The item tab is the exception: item metrics are item-scoped, not user-scoped, so there is no
sensible user count to pair with them and no attempt should be made to invent one. It is a diagnostic
tab — it says which products lose people — and any test it suggests is powered on the users of the
pages involved, taken from the landing-page or page-type tabs, never on item counts.

If the property, the funnel walk, or the user's brief suggests another split matters for this
client (site search use, logged-in state, a promo parameter), pull it too and give it a tab. The
list above is the floor, not the ceiling.

Then run these checks before you interpret anything. **These are judgement gates on what you may
conclude**, and they are not the same thing as the Data completeness tab: that tab is a mechanical
record of what GA4 said about each response, while these are your reading of whether a number can
be believed. What each check produces is a disqualification (a number that cannot become a
hypothesis) and a sentence at handover.

- **Plausibility.** Flag any rate that is impossible (>100%), any two near-identical pages with a
  wildly different rate (a 4x gap between `/car-insurance` and `/insurance/car` is a tracking or
  redirect artefact far more often than a UX finding), any step whose completion rate exceeds the
  step before it, and any segment whose average order value or revenue per session is wildly out of
  line with the rest (usually cross-property or partial tracking). **A flagged number is
  disqualified: it does not become an opportunity and it does not become a hypothesis.** This is
  the single biggest way an automated audit embarrasses itself.
- **Sampling, thresholding and truncation.** Every one of these lands on the Data completeness tab
  from the record you kept above, and anything that changes how a *particular* tab should be read
  also goes in that tab's own context line (`Top 100 of 8,077 by sessions`). A top-N presented as a
  complete table is a lie the reader cannot detect. **Thresholded is the one to think hardest
  about**: those rows are gone, so the totals on that tab are short by an unknown amount and a
  conversion rate computed from them is not just imprecise but biased. Say so on the tab, and treat
  a rate from a thresholded segment the way you treat any other implausible number.
- **`(not set)` and Unassigned.** Keep the bucket in the table rather than dropping it, and if it
  is large enough to distort how a tab reads, say so in that tab's context line.

Raise every flag from these checks **in chat at handover** (see [Deliver](#deliver)), in plain
sentences. They matter most for the ones you throw away, so say what you disqualified and why.

## Step 4 — Find the opportunities, and drop the ones you cannot test

An opportunity is a **measured gap**: this page, device, or channel underperforms its comparable
peers, on real volume. Not "the CTA could be clearer".

Then apply the filter that keeps this honest. **For each candidate, work out the minimum detectable
effect at that segment's current traffic over a four-week run, and drop the candidates that cannot
reach significance.** A page doing 400 sessions a month cannot produce a significant result however
good the idea is, and a backlog full of unpowered tests is the standard failure of automated CRO.

### The MDE calculation

Two-sided, 95% confidence, 80% power, comparing two proportions. **This is deliberately the same
calculation as Results Analysis's design sample size** (`_ra_required_users_per_arm` in Tapa's
`results_summary.py`, which is the PEA workbook's hidden "Sample Size" column). The same team reads
both numbers, so they must not disagree.

```
C       = (z(0.975) + z(0.80))²  =  (1.95996 + 0.84162)²  =  7.8489
p_v     = p · (1 + mde_rel)                  the variation's rate at the MDE
avg_var = ( p(1-p) + p_v(1-p_v) ) / 2        each arm's variance, averaged

n per arm = 2 · avg_var · C / (p_v - p)²
```

Solved for the MDE at a known `n`, that is a quadratic with a closed form — no iteration:

```python
def mde_relative(p, n_per_arm, C=7.8489):
    a = p * (n_per_arm + C)
    b = -C * (1 - 2 * p)
    c = -2 * C * (1 - p)
    return (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
```

**Do not simplify `avg_var` to a single shared `p(1-p)`.** It looks equivalent and is not: a
variation that genuinely improves a low base rate carries more variance than the control, so
assuming the control's variance for both arms understates the sample needed. Measured on the first
run, the shared-`p` shortcut reported 19.13% for the homepage where the correct figure is 20.05%,
and delivered **76.4% power, not the 80% it claimed**. The error is negligible at high base rates
(the two checkout-step candidates move by 0.3% and 0.0%) and material at the low ones, which are
exactly the candidates sitting near the threshold.

Write `C` and the confidence and power into the tab's context line so the number can be checked.

Four rules about the inputs. Each of them changes the answer, and three of them are easy to get
subtly wrong:

1. **Use one unit for `p` and `n`, and make it the unit you will randomise on — users.** A test
   assigns a *visitor* to an arm, so sessions are not independent trials: 274,336 sessions from
   197,957 users is 1.39 sessions per user, and counting them as 274,336 independent draws
   overstates your evidence. Take `n` = users in the segment and `p` = converting users / users in
   the segment.

   **Do not "correct" a session-grain number by dividing `n` and leaving `p` alone.** Converting
   both together is close to neutral — the homepage candidate moves from 19.31% to 19.26% — because
   dividing `n` by sessions-per-user multiplies `p` by the same factor and the two cancel. Mixing
   the grains is what produces a wrong answer, in either direction. So pull users alongside
   sessions for every slice in Step 3, and if a segment only has session data, convert both
   (`p_user = p_session × sessions per user`) and say so on the row.

2. **Check the approximation is valid before you print a number: `n · p ≥ 10` in each arm.** Below
   that the normal approximation does not hold and the formula returns arithmetic, not a fact. Site
   search at 303 users and 1.19% gives `n·p` = 3.6, and the formula duly reports a detectable
   effect of 209%. **Where `n · p < 10`, or where `mde_rel` comes out above 0.5, write
   `cannot be powered` in place of the number.** A relative MDE of 144% means "the variation would
   have to more than double the rate", which nobody needs to three decimal places, and printing it
   makes a sound verdict look like false precision.

3. **Divide the traffic by the number of arms you will actually run**, not always two. Three arms
   (control + two variations) is `/3` and a meaningfully worse MDE. State the arm count.

4. **Get the four-week volume from the Daily trend tab, not from `monthly × 28/31`.** That
   shortcut assumes traffic is uniform, and it rarely is — July had a single day 61% above the
   median. Use the mean daily users over the range × 28, and if the range contains an obvious spike
   or outage, say so on the row.

**Check the completeness of the tab a candidate came from before you power a test on it.** The whole
calculation is only as good as `n` and `p`. If the tab is marked exact on the Data completeness tab,
say nothing. If it is sampled and could not be de-sampled, the row's reason column says the volume
is a GA4 estimate — the verdict usually survives, but a candidate sitting within a percentage point
of a band boundary should not be presented as if the band were certain. If the tab is thresholded,
`p` is computed from a numerator and denominator that are both short, so say that in the reason
column too.

### The KEEP threshold

Three bands, and **these numbers are fixed — do not pick your own bar per run.** A threshold chosen
in the moment makes the verdict column unreproducible; two runs of this audit have already used 20%
and 25% and therefore disagreed about which tests survive.

| Detectable relative effect | Verdict | What it means |
|---|---|---|
| ≤ 10% | **KEEP** | Properly powered. A normal CRO win shows up. |
| 10% – 25% | **STRETCH** | Only a large win is provable. A real 8% improvement returns "no significant difference". |
| > 25%, or cannot be powered | **DROP** | The test cannot answer the question. |

**STRETCH is the band that matters, because most candidates land in it.** On the first real run,
five of seven survivors sat between 16.4% and 19.1% — all comfortably "KEEP" under a 20% bar, while
none of them could have proven the kind of uplift the team would actually expect from the change.
Calling those the same thing as a 4.4% MDE hides the whole problem. A two-band pass/fail always
resolves to "nearly everything passed", which is how an audit ends up recommending tests that
cannot conclude.

For every STRETCH row, say in the reason column what would move it to KEEP. It is usually one of
three things: a longer run, a pooled segment (all PDPs rather than one), or a primary metric further
up the funnel where the base rate is higher — a 55% add-to-cart step needs a fraction of the traffic
a 1.4% purchase rate does, which is exactly why the two checkout-step candidates are the only clean
KEEPs on that run.

**Every candidate — kept, stretch or dropped — gets a row on the Opportunities tab with its gap,
its volume, its MDE arithmetic, and the verdict.** The dropped list is not waste; it is half of what
the team is reviewing.

Rank what survives on: size of the measured gap × traffic affected × how directly it touches the
primary conversion.

## Step 5 — Design the tests

Write a test for every KEEP and every STRETCH candidate — a STRETCH is a real test with a caveat,
not a reject. Nothing marked DROP or `cannot be powered` gets a hypothesis. In the house format:

- **Hypothesis**, as IF / THEN / BECAUSE. The BECAUSE must cite the finding it came from, with the
  number. "BECAUSE only 24% of mobile sessions scroll far enough to see all products" — not
  "BECAUSE users prefer clarity".
- **Test type** (usually AB Test), **Pages**, **Audience**, **Primary metric**,
  **Secondary metrics** (bounce rate and the downstream conversion, so you catch a win that moves
  the top of the funnel and breaks the bottom).
- **Expected MDE** from Step 4, and its verdict, so a STRETCH test cannot be read as comfortably
  powered once it is out of the Opportunities tab.

Every test must trace back to the data: its row on the Hypotheses tab names the workbook tab (and
the row or segment on it) that motivated it, and the BECAUSE quotes a number that appears there.
If you cannot point at the data that motivated it, cut it.

Then prioritise, using the house weights: Expected uplift ×4, Data backed ×4, Development effort
×4, Traffic volume ×3, Strategic alignment ×2, Design effort ×2, Asset effort ×1. Keep the
per-criterion scores, not just the total — the team wants to see the weighing, not the verdict.

## Step 6 — Build the review workbook

One `.xlsx`, built with openpyxl, in this tab order:

| Tab | Contents |
|---|---|
| **README** | Client and property name, GA4 property id, measurement id, date range, which channel grouping the audit reports on, the property totals for the range, and a one-line index of every tab. Nothing else — no data-source line, no funnel-type or starting-URL echo, no who-confirmed-it line, no derivation note, no generated timestamp. The reviewer knows how the workbook was made; the README is there to say what is in it |
| **Data completeness** | One row per data tab, from the records kept in Step 3: rows in the tab, rows GA4 matched, truncated, sampled, % of data read, whether it was de-sampled and whether that came out exact (or why it was skipped), thresholded, `(other)` row present, and a notes column. Second tab deliberately — a caveat you have to scroll to is a caveat nobody reads |
| **Funnel** | The confirmed funnel as the same four-column table the user confirmed in 2c (step, event, page URL, users), then the drop-off: whole property, then by device, then by channel group. Laid out as [The Funnel tab](#the-funnel-tab) describes. **No Tracking notes block and no landing-page breakdown** |
| **One tab per Step 3 slice** | The full table for that slice, named plainly (`Landing pages`, `LP x Device`, `LP x Channel`, `Sources`, `Campaigns`, `Devices`, `New vs returning`, `Countries`, `Daily trend`, `Events by day`, `Items`…). Where the user asked for both channel groupings, the two tabs say which is which (`Channel (default)`, `Channel (custom)`) |
| **Opportunities** | Every candidate from Step 4 — KEEP, STRETCH and DROP: the measured gap, the segment's users over the range, users per arm, the arm count, the baseline per-user rate, `n·p`, the detectable relative effect (or `cannot be powered`), the verdict, and the reason. The context line states the constant, the confidence and power, and the unit |
| **Hypotheses** | One row per KEEP or STRETCH test: name, IF, THEN, BECAUSE, evidence (tab + row/segment it traces to), pages, audience, primary metric, secondary metrics, expected MDE, its Step 4 verdict, the seven priority sub-scores, total, rank |

Rules for the build:

- **Write real numbers, not strings.** Rates go in as fractions with a `0.0%` number format,
  volumes as integers with `#,##0` — the team will want to re-derive and re-sort, and a column of
  text can do neither.
- Formatting is light and consistent: bold header row (white on blue `#2F6BED`), freeze the header,
  autofilter on every data tab.
- **Charts go on the same tab as the data they plot**, to the right of the table — not on a charts
  tab of their own. That is the team's explicit preference: the point of a chart here is to be seen
  while reading the numbers it came from. See [Charts](#charts) below for which tabs get one and how
  to place it.
- **Every column is wide enough for its contents. No truncated cells anywhere in the workbook.**
  openpyxl has no autofit, so width is something you compute — see [Column widths and context
  lines](#column-widths-and-context-lines) below. This is not cosmetic: a cut-off cell in the middle
  of a review workbook is read as a mistake in the data.
- Every data tab carries one context line above the header: what the tab is, its date range, and
  any truncation or thresholding that applies to it (`Top 100 of 8,077 landing pages by sessions`).
  Not the source tool — every tab has the same source and repeating it fifteen times is noise.
- **Do not trim, round away, or top-N a tab to make it tidy.** Comprehensiveness is what the team
  asked to see.

### The Funnel tab

This tab answers one question — where does this funnel leak, and for whom — so everything on it is
the funnel, read in funnel order. Four blocks, in this order, and nothing else:

1. **The confirmed funnel**, the four-column table from 2c.
2. **Whole-property drop-off**: step, active users, completion rate, abandonments, abandonment rate.
3. **By device**, one block per device category.
4. **By channel group**, one block per channel. Where the user asked for both groupings, the custom
   blocks follow the default ones under their own heading.

**Blocks 3 and 4 are grouped by the breakdown value, not by the step.** Each device and each channel
gets its own small heading and its own complete funnel underneath it, steps in funnel order, exactly
like block 2:

```
Organic Search
Step | Event            | Active users | Completion rate | Abandonments
1    | view_item_list   |       84,204 |                 |
2    | view_item        |       48,210 |           57.3% |       35,994
3    | add_to_cart      |       17,538 |           36.4% |       30,672
```

Then the next channel, then the next. **What this replaces is one long table of every
(channel, step) pair sorted by user count**, which is what the first runs produced: reading one
channel's funnel out of it means finding five rows scattered across seventy, and comparing two
channels means doing that twice and holding it in your head. The team reads this tab a channel at a
time, so the table is laid out a channel at a time. Order the blocks by the first step's users,
descending, so the channels that matter are at the top.

Two things not on this tab, both deliberate:

- **No landing-page breakdown.** A funnel per landing page is the same information the
  `Landing pages` and `LP x Channel` tabs already carry at full depth, and it made this tab twice as
  long as everything else on it put together.
- **No Tracking notes block.** Tracking observations go in the handover message (see
  [Deliver](#deliver)). This tab is for the experimentation team, and how the tags are wired is not
  what they are here to read.

### Column widths and context lines

Run both of these over **every sheet** once the data is written, widths first, and only then add the
charts — the whole build order is: write every tab → `fit_columns` → `fit_banner_rows` → charts →
save. Do not hand-pick widths per tab; they drift, and the tab you forget is the one that gets
forwarded.

```python
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

MIN_W, MAX_W = 9, 55   # characters; past MAX_W a column wraps instead of stretching

def display_len(cell):
    """Width of the value AS EXCEL WILL SHOW IT, not as Python stores it."""
    v = cell.value
    if v is None:
        return 0
    fmt = cell.number_format or "General"
    if isinstance(v, (int, float)) and not isinstance(v, bool) and fmt != "General":
        if fmt.rstrip('"').endswith("%"):
            dp = len(fmt.split(".")[1].rstrip('%"')) if "." in fmt else 0
            return len(f"{v * 100:.{dp}f}%")
        dp = len(fmt.split(".")[1]) if "." in fmt else 0
        return len(f"{v:,.{dp}f}") + (2 if "£" in fmt or "$" in fmt else 0)
    return max(len(line) for line in str(v).split("\n"))

def banner_rows_of(ws):
    """Rows with a single populated cell: the context line and any section labels.
    They are prose, not table cells, and are handled separately below."""
    return {r[0].row for r in ws.iter_rows()
            if sum(c.value is not None for c in r) <= 1}

def fit_columns(ws):
    banner_rows = banner_rows_of(ws)      # measuring these stretches column A to 200
    for col in ws.columns:
        idx = col[0].column
        widest = 0
        for c in col:
            if c.row in banner_rows:
                continue
            n = display_len(c)
            if c.font and c.font.bold:
                n = int(n * 1.15)      # bold renders wider than regular
            widest = max(widest, n)
        if widest == 0:
            continue
        ws.column_dimensions[get_column_letter(idx)].width = min(max(widest + 2, MIN_W), MAX_W)
        if widest + 2 > MAX_W:          # prose column: wrap rather than run off screen
            for c in col:
                if c.row not in banner_rows:
                    c.alignment = Alignment(wrap_text=True, vertical="top")
```

Then treat the context lines, **after** the widths are final — the treatment depends on how much
room they have to spill into:

```python
import math
LINE_H = 15.0   # points per line of text at 11pt

def fit_banner_rows(ws, last_col):
    """A context line either spills across the empty cells or is merged and given
    the height it needs. What it must never do is wrap inside one narrow column."""
    room = sum(ws.column_dimensions[get_column_letter(i)].width or 8.43
               for i in range(1, last_col + 1))
    for r in sorted(banner_rows_of(ws)):
        cell = next((c for c in ws[r] if c.value is not None), None)
        if cell is None:
            continue
        text = str(cell.value)
        if len(text) <= room * 0.95:
            cell.alignment = Alignment(wrap_text=False, horizontal="left", vertical="center")
            ws.row_dimensions[r].height = None          # one line, Excel's default
        else:
            ws.merge_cells(start_row=r, start_column=cell.column,
                           end_row=r, end_column=last_col)
            cell.alignment = Alignment(wrap_text=True, horizontal="left", vertical="top")
            span = sum(ws.column_dimensions[get_column_letter(i)].width or 8.43
                       for i in range(cell.column, last_col + 1))
            ws.row_dimensions[r].height = math.ceil(len(text) / max(span * 0.95, 1)) * LINE_H
```

**The failure this fixes:** the context cell inherits `wrap_text` from the header styling, the
column beside it is 9 characters wide because it holds a `Rank` integer, and a 150-character
sentence stacks itself one word per line inside that column while the row height shows three of
them. It reads as a formatting accident, which is what the first runs looked like on Hypotheses and
Opportunities.

Two rules that go with the code:

- **Run `fit_columns` on every sheet first, then `fit_banner_rows`.** The spill room is the sum of
  the final column widths, so the order is not optional.
- **Keep a context line to one sentence.** Spilling only works while the text is shorter than the
  table is wide, and most tabs are narrower than they look — 11 of the 17 tabs on the first run had
  a context line longer than the whole table. The Opportunities line was 293 characters and the
  Hypotheses line 388; those two fit only because those tabs are unusually wide. If a tab needs a
  paragraph of method explanation, that paragraph belongs in the README, and the tab gets the one
  line that says what it is.

Three traps in the width code, all of which produce a wrong width silently:

- **Measure the rendered string, not the stored value.** A conversion rate stored as
  `0.01934489093666161` and formatted `0.0%` displays as `1.9%` — four characters, not twenty.
  Sizing off `len(str(value))` gives you a column six times too wide, and it is why widths and
  number formats have to be applied *before* fitting.
- **Skip the banner rows.** The context line above each header is one long sentence in column A
  with nothing beside it. It is supposed to spill across the empty cells; measuring it makes
  column A absurd and every other column look cramped by comparison.
- **Do not set row heights on wrapped data columns.** Excel auto-fits the height of a wrapped row
  only while the height is unset. Set it explicitly — even to something generous — and the text is
  clipped instead. The merged context line is the one exception, and only because merged cells never
  auto-fit at all, so its height has to be computed. Never merge inside a data table.

### Charts

Every chart in this workbook is built by the one function below, so that fifteen tabs produce
fifteen charts that look like they belong together. **Do not hand-roll a chart for one tab** — if a
tab needs something the function does not do, add the argument rather than writing a second
chart-builder, or the workbook ends up with two visual languages in it.

A chart is a reading aid, not decoration: it goes to the right of the table on that same tab, and if
the tab is a lookup table (`Sources` with 400 rows, `Items` with 90 products) the chart plots the
head of it and its title says so.

| Tab | Chart | Plotted against |
|---|---|---|
| Funnel | Three: (1) bar, active users per step, funnel order; (2) grouped bar, step completion rate by device; (3) grouped bar, step completion rate by channel, top 6 channels | Never sorted by size — the order *is* the finding. Charts 2 and 3 plot the *rate*, not the users, because that is what makes two segments of different size comparable |
| Landing pages, LP x Device, LP x Channel, Page types | Bar of sessions, top 15 rows, with conversion rate on a **secondary axis** | A rate against session counts is invisible on one axis |
| Channel, Sources, Campaigns, Devices, Countries, New vs returning | Bar of sessions with conversion rate on a secondary axis, top 15 | |
| Daily trend | Line, sessions and conversions by date, conversions on a secondary axis | |
| Events by day | Line, one series per event, top 8 events only | 20 lines is a scribble; the table still holds all 20 |
| Items | Bar of items viewed, top 15 products, with add-to-cart rate on a secondary axis | |
| Opportunities | Bar of the detectable relative effect per candidate, KEEP first | `cannot be powered` rows are left out of the chart and stay in the table |
| Data completeness, Hypotheses, README | No chart | Neither prose nor a manifest plots |

**Every chart is labelled on both axes.** Pass `x_title` and `y_title` on every call, and `y2_title`
whenever there is a secondary series. A chart whose axes are unlabelled is asking the reader to
guess what they are looking at, and the numbers on this workbook are the whole point of it.

```python
import openpyxl
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import (
    CharacterProperties, Font as DrawFont, Paragraph, ParagraphProperties, RichTextProperties,
)
from openpyxl.utils import get_column_letter

TAPA_BLUE, TAPA_INK, GRID, INK = "2F6BED", "9AA5B1", "E2E1E0", "26241F"
AXIS_TEXT = "595959"
# Multi-series charts only. Single-series charts are always TAPA_BLUE.
SERIES_COLOURS = ["2F6BED", "0A7D51", "8755B9", "C43F3E", "E08A1E", "1D76BC", "6B7A8F", "17A2A2"]


def _text(size=900, bold=False, colour=AXIS_TEXT):
    return RichText(p=[Paragraph(pPr=ParagraphProperties(
        defRPr=CharacterProperties(sz=size, b=bold, solidFill=colour,
                                   latin=DrawFont(typeface="Calibri"))),
        endParaRPr=CharacterProperties(sz=size))])


def _style_axis(axis, *, title, number_format=None, gridlines=False, rotation=None):
    axis.delete = False                    # openpyxl leaves this unset and Excel hides the axis
    axis.title = title
    if axis.title is not None:
        axis.title.overlay = False
        axis.title.tx.rich.p[0].pPr = ParagraphProperties(
            defRPr=CharacterProperties(sz=900, b=False, solidFill=AXIS_TEXT))
    if number_format:
        axis.numFmt = number_format
    axis.majorTickMark, axis.minorTickMark = "out", "none"
    axis.spPr = GraphicalProperties(ln=LineProperties(solidFill=GRID, w=9525))
    axis.txPr = _text()
    if rotation is not None:
        axis.txPr.bodyPr = RichTextProperties(rot=rotation, vert="horz")
    axis.majorGridlines = ChartLines(
        spPr=GraphicalProperties(ln=LineProperties(solidFill=GRID, w=9525))) if gridlines else None


def add_chart(ws, *, kind, header_row, first_row, last_row, cat_col, value_cols,
              title, x_title, y_title, anchor_col, secondary=(), y2_title=None,
              y_format="#,##0", y2_format="0.0%", rotate_labels=True):
    """One chart, anchored two columns clear of the table on the same sheet.

    `value_cols`/`secondary` are 1-based column indexes. Anything in `secondary` is drawn as a
    line on the right-hand axis — a 1.9% rate and a 40,000-session bar cannot share one axis,
    and forcing them to makes the rate a flat line along zero.
    """
    primary = BarChart() if kind == "bar" else LineChart()
    primary.title = title
    primary.title.overlay = False          # or Excel draws it inside the plot area
    primary.title.tx.rich.p[0].pPr = ParagraphProperties(
        defRPr=CharacterProperties(sz=1100, b=True, solidFill=INK))
    primary.height, primary.width = 8.5, 17
    primary.roundedCorners = False
    primary.varyColors = False             # or a one-series bar gets a colour and a legend per point

    cats = Reference(ws, min_col=cat_col, min_row=first_row, max_row=last_row)
    for col in value_cols:
        primary.add_data(Reference(ws, min_col=col, min_row=header_row, max_row=last_row),
                         titles_from_data=True)
    primary.set_categories(cats)
    n_series = len(primary.series)
    multi = n_series > 1
    for i, s in enumerate(primary.series):
        colour = SERIES_COLOURS[i % len(SERIES_COLOURS)] if multi else TAPA_BLUE
        if kind == "bar":
            s.graphicalProperties.solidFill = colour
            s.graphicalProperties.line.noFill = True
        else:
            s.graphicalProperties.line.solidFill = colour
            s.graphicalProperties.line.width = 20000
            s.marker.symbol, s.smooth = "none", False

    _style_axis(primary.x_axis, title=x_title,
                rotation=(-2700000 if rotate_labels else None))   # -45 degrees, in 1/60000ths
    _style_axis(primary.y_axis, title=y_title, number_format=y_format, gridlines=True)
    primary.x_axis.axPos, primary.y_axis.axPos = "b", "l"   # openpyxl defaults the cat axis to "l"

    if secondary:
        right = LineChart()
        for col in secondary:
            right.add_data(Reference(ws, min_col=col, min_row=header_row, max_row=last_row),
                           titles_from_data=True)
        right.set_categories(cats)
        for s in right.series:
            s.graphicalProperties.line.solidFill = TAPA_INK
            s.graphicalProperties.line.width = 20000
            s.marker.symbol, s.smooth = "none", False
        right.y_axis.axId = 200            # a second axis needs its own id
        right.y_axis.crosses = "max"       # ... and must cross at the far side
        _style_axis(right.y_axis, title=y2_title, number_format=y2_format, gridlines=False)
        right.x_axis = primary.x_axis
        n_series += len(right.series)      # count BEFORE the merge, see below
        primary += right

    if n_series > 1:
        primary.legend.position, primary.legend.overlay = "b", False
        primary.legend.txPr = _text()
    else:
        primary.legend = None              # one series needs no legend, and Excel legends the points

    ws.add_chart(primary, f"{get_column_letter(anchor_col)}{header_row}")
```

**Long category labels get a `Chart label` column.** Excel truncates a rotated axis label to
whatever fits and appends an ellipsis, so a landing-page chart comes back as fifteen bars captioned
`/products/currentbody-…`, all identical. **A rotated label holds about 24 characters at this chart
size**, so wherever the category text can run past that — `Landing pages`, `LP x Device`,
`LP x Channel`, `Sources`, `Campaigns`, `Items`, `Countries`, and any other text category — write
one extra column immediately to the right of the table, headed `Chart label`, holding the shortened
form (`text if len(text) <= 24 else "..." + text[-21:]`, which keeps the tail, where the pages
differ), point `cat_col` at that column and anchor the chart two columns clear of *it*. Keep it out
of the autofilter range: it is a chart aid, not data.

The two funnel comparison charts have the same problem and a neater answer than truncation: their
categories are step transitions, and a completion rate belongs to the step it lands on, so **label
them by the destination step alone** — `-> add_to_cart`, `-> begin_checkout`, `-> purchase`. Short,
unambiguous, and no ellipsis. `add_to_cart -> begin_checkout` is 29 characters and comes back cut.

Six things that go wrong, in order of how easily they go unnoticed. The first three were all
present in every chart of the first runs and are the reason those charts had no axes at all:

- **`delete` is unset by default, and Excel reads that as "hide this axis".** Nothing errors, and
  what you get is the chart the reviewer described as rudimentary: no tick labels, no numbers, no
  category names, just bars floating over gridlines. `_style_axis` sets `delete = False` on every
  axis including the secondary one, and that single line is most of the difference.
- **A second value axis brings its own gridlines, and two sets at two different scales is the mess
  of unevenly spaced horizontal rules** the reviewer flagged on `Page types` — they are not
  mis-spaced, they are two evenly spaced sets drawn over each other. Only the primary value axis
  gets `majorGridlines`; the secondary gets `None`.
- **openpyxl defaults the category axis to `axPos="l"`**, which is not where a column chart's
  categories go. Set it to `"b"` explicitly.
- **A series can be drawn across the chart title.** With the axes hidden, Excel gives the plot area
  the full frame right up to the top edge, so a rate that peaks near the axis maximum is drawn
  through the title text. `title.overlay = False` alone does not prevent it — the axes have to exist
  for Excel to reserve the title band. Fixed by the first bullet, but check for it: the tabs where
  it shows are the ones whose secondary series peaks on an early category.
- **A rate on the primary axis is a flat line at zero.** Rates are stored as fractions, so 0.019
  plotted beside 40,000 has no visible height. Any chart mixing a volume and a rate needs the
  secondary axis and its `0.0%` format.
- **After `primary += right`, `primary.series` still holds only the primary's own series.** The
  secondary chart's series are reachable, but not there, so `len(primary.series)` on a bar-plus-rate
  chart is 1 and a naive "hide the legend when there is one series" test strips the legend from
  exactly the charts that need one — the reader can no longer tell the bars from the line. Count
  before the merge, which is what `n_series` above is for.
- **Plot from the sorted table, cap the categories, and never chart a `cannot be powered` row.** A
  bar chart with 400 categories is a grey smear, so take the head of the already-ordered table and
  put the cap in the title (`top 15 of 412 landing pages`) so nobody reads it as the whole picture.
  A `cannot be powered` row has no number to plot and openpyxl draws the text as a zero-height bar,
  which reads as "no effect detectable" rather than "not measurable".

Then **verify before handover (ADR-0006)**: reopen the file with openpyxl and check that every
expected tab exists and holds the rows you meant to write, spot-check at least three numbers
against the original tool responses, and confirm every evidence pointer on the Hypotheses tab names
a tab that actually exists. **Recompute the MDE on at least two Opportunities rows from the inputs
printed on that row** and confirm they match what you wrote — the formula is easy to apply to the
wrong `p` — and confirm no row prints a detectable effect where `n·p < 10` or the result exceeds
0.5. **Check the widths too** — for every sheet, assert that each column's
width is at least the longest `display_len` in it (or that the column wraps and is at `MAX_W`), and
that every context line is either unwrapped with no row height or merged with one — a wrapped
banner with no height set is the crammed-cell bug. **Check the Data completeness tab has a row for
every data tab in the workbook** and no rows for tabs that do not exist: a missing row reads as
"that tab was fine". Those checks cost nothing and catch a tab you built before adding a long row.
Fix and rebuild anything that fails; never deliver a workbook you have not reopened.

**Check the charts, and check them properly.** A chart that failed to build leaves no error behind,
just a tab that looks like the old workbook, and every fault the last round was reviewed for was
silent. So for each chart, assert:

- `len(ws._charts)` is 3 on Funnel, 1 on every tab the table above says gets one, and 0 on README,
  Data completeness and Hypotheses.
- **`x_axis.delete` and `y_axis.delete` are both `False`, not `None`** — `None` is the default and
  it means "no axis". If there is a secondary axis, check it too. This is the single check that
  would have caught the whole last round.
- Exactly **one** axis on the chart carries `majorGridlines`.
- `x_axis.title` and `y_axis.title` are set, and `y2_title` wherever there is a secondary series.
- The chart's anchor column is clear of the last populated column (including a `Chart label`
  column, where the tab has one), so no chart sits on top of its own table.

**Reading the XML back is not the same as seeing the chart.** If this session can drive Excel
(Windows COM: `$co.Chart.Export("chart.png","PNG")` per `ChartObject`), export one chart from a tab
with a secondary axis and one from a tab with a single series, and look at them: both axes labelled,
one set of evenly spaced gridlines, the title clear of every series, no ellipsis in the category
labels. If it cannot, say at handover that the charts were verified structurally but not rendered.

## Deliver

Hand over the workbook file, and in chat:

- the funnel used, and that the user confirmed it before the pull
- the date range and which channel grouping the tabs use
- what was pulled: the count of slices and rows
- **completeness in one or two sentences**, pointing at the tab: how many tabs came back exact, how
  many were sampled and de-sampled, anything that could not be de-sampled and why, and anything
  thresholded or truncated. "All 18 tabs exact" is a perfectly good version of this and worth
  saying — the team asked how they would know, so silence is not an answer. **If a funnel came back
  sampled, say that there is no workaround for it** rather than leaving it as an unexplained gap
- the headline findings, briefly — three to five, each with its number
- tests proposed and candidates dropped, as counts
- **the data-quality flags from Step 3**, in plain sentences: what looked wrong, where, and what
  you disqualified because of it. This is the only place they appear, so do not compress them to
  "some data-quality issues were found"
- **the tracking observations from the walk**, two or three sentences at most: the collect endpoint
  host, a checkout on a third-party domain, an event firing somewhere unexpected, a step whose tags
  could not be read client-side. This is the one place they go — they are a real finding for whoever
  ran the audit, and they are not for the workbook

Say plainly that this phase produces no deck: the workbook **is** the deliverable, for the
experimentation team to review the foundation the deck will later stand on.

## Avoid these

- **Do not stop and offer the user a menu when a tool is unavailable.** A missing browser has a
  defined degradation above. Take it, finish the audit, and report what was missing at handover.
  Ask only when proceeding would be *unsafe* or would make the output *wrong* — which is exactly
  the asks this skill does have, and no others: **one message in Step 1** covering the starting URL,
  the funnel type, the date range and the channel grouping (only the parts the brief did not
  already supply), and **the funnel confirmation in 2c**. In particular **do not ask permission to
  start the walk** — announce it and go. Everything else you work out yourself, including the whole
  route through the funnel and every decision about how the workbook is built.
- **Never invent behavioural evidence.** You have GA4 and screenshots. You do not have scroll maps,
  click maps or session recordings. If a hypothesis needs "users don't scroll", either get it from a
  GA4 `scroll` event or say the evidence is missing.
- **Never present a plausibility-flagged number as a finding.** It is a tracking bug until proven
  otherwise — it is disqualified from the Opportunities and Hypotheses tabs, and reported in chat.
- **Never compare to "industry benchmarks".** We do not have a benchmark source. Compare segments
  within the property instead.
- **Never write a hypothesis whose BECAUSE number is not in a data tab.** The traceability is the
  point of this deliverable.
- **No em dashes in hypothesis and test text** — it gets pasted into client-facing decks later.
- Do not promise a test will win. Say what it is designed to move and what it can detect.
