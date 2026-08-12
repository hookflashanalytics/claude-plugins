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

A browser will be open on a real client's live website. These are hard limits, not preferences:

- **You never click a commerce or submit control. The human does.** The funnel walk in Step 2 is
  driven by the person, not by you — you read what fired, you do not press anything. That is the
  design, not a fallback, and it is what makes the walk safe in any browser.
- **Never complete a purchase**, and never click pay, place order, confirm, or anything equivalent.
- **Never submit the final step of a lead form.** Walking forward through intermediate steps is
  fine and is the point. Submitting the last one creates a real lead in the client's CRM, fires
  their conversion tracking (which feeds Google Ads bidding and pollutes the very GA4 data you are
  about to analyse), and may trigger real emails or underwriting lookups. You already know the
  conversion event name from GA4, so there is nothing left to learn by pressing the button.
- **Never enter real personal data.** If you are asked to type anything, obvious test values only
  (`test@test.com`, `Test`, `0000000000`). If a step needs something you cannot fake — a real
  registration or policy number — the user types it.
- **Tell the user before the walk** what is about to happen, and let them confirm. Agencies
  generally have permission to poke around a client's funnel; it is still better raised in advance.

### Which browser

Use whichever browser tooling this session has. **Do not stop to ask the user to choose, and do not
abandon the walk because a particular browser is missing.**

- **A sandboxed in-app browser, if present** — first choice. It carries none of the user's logged-in
  sessions or saved cards.
- **Claude in Chrome, if that is all there is** — acceptable. It is the user's real browser, so say
  so once, and suggest they use a fresh or private window if the client's site is one they shop on.
  The purchase risk lives in *clicking*, and you are not clicking.
- **Neither available** — do not block. Ask the user to walk the funnel in their own browser and
  send you the step URLs and a screenshot per step, then carry on at Step 2c. You lose the event
  trace, so lean harder on the GA4 evidence in 2a, and say on the README tab that the funnel was
  confirmed from the user's account of the walk rather than from observed tag traffic.

## Step 1 — Ground the audit

You need four things before you touch the data: a **GA4 property**, a **URL to start from**, **what
converting means on this site**, and a **date range**. Look up what you can, then ask once for the
rest.

1. Resolve the property. `tapa_ra_list_ga4_properties` lists what the user can reach. If they gave
   you a measurement ID or a site URL instead, `tapa_pf_find` resolves it.
2. **Ask for whatever the user has not already given you — in one message, not a series of them.**
   Two things:
   - **The URL to start the funnel walk from.** Usually the homepage, but plenty of clients want
     the audit aimed at a campaign lander, a category, or one product line. Starting in the wrong
     place wastes the walk.
   - **What kind of funnel this is: ecommerce, lead gen, or something else.** If something else,
     ask them to name the converting action in a few words — book a viewing, start an application,
     register an account, donate.

   Ask even when the site looks obvious. Inferring the funnel from the domain is the single biggest
   way this audit goes wrong: it maps a plausible funnel that is not the one the client is judged
   on, and every number after that is answering the wrong question. Two sentences from the user
   removes it. If they have already said both things in their brief, do not ask again.
3. Default the date range to the **last complete calendar month**. Record which range you used on
   the workbook's README tab and on every data tab.

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

### 2b. Watch a human walk it

You need each step's URL and layout, and confirmation that the events fire where you think. Do not
click through yourself — bot protection challenges automated walks, and a human decides what is
safe to submit.

1. Open the starting URL from Step 1 in whichever browser this session has (see [Which
   browser](#which-browser)).
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

### 2c. Confirm before you pull

Show the user the derived funnel as a short table — step, event, where it fires, the URL — plus the
page-type patterns you propose (home, product lander, PLP, PDP, blog…). Ask them to confirm or
correct it.

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
| Step-to-step drop-off by device, by channel group, and by top landing pages | Whose leak it is |
| Each funnel step × device category | Where the volume is vs where the conversion is |
| Each funnel step × session default channel group | Which traffic gets how deep |
| Landing page × sessions × conversions × conversion rate | The pages worth testing at all |
| Landing page grouped by page type | Which *kind* of page carries the business |
| Landing page × device | A page that converts on desktop and dies on mobile |
| Landing page × channel group | The combination effects — often the real finding |
| Session default channel group × sessions × conversion rate | Which traffic converts |
| Session source/medium × sessions × conversion rate | The grain below channel group — where the paid and referral stories hide |
| Campaign × sessions × conversion rate (where paid traffic exists) | Which spend lands on which pages |
| Device category × sessions × conversion rate | The headline device split |
| New vs returning × sessions × conversion rate | Whether the funnel serves first-time visitors |
| Country × sessions × conversion rate | Whether one market drags the average |
| Daily sessions and conversions across the range | Seasonality, launch spikes, tracking gaps |

If the property, the funnel walk, or the user's brief suggests another split matters for this
client (site search use, logged-in state, a promo parameter), pull it too and give it a tab. The
list above is the floor, not the ceiling.

Then run these checks before you interpret anything:

- **Plausibility.** Flag any rate that is impossible (>100%), any two near-identical pages with a
  wildly different rate (a 4x gap between `/car-insurance` and `/insurance/car` is a tracking or
  redirect artefact far more often than a UX finding), and any step whose completion rate exceeds
  the step before it. **Report these as data-quality findings on the Data quality tab. Do not
  write a test hypothesis on top of one.** This is the single biggest way an automated audit
  embarrasses itself.
- **Sampling and thresholding.** If a response came back sampled or thresholded, record that on the
  slice's tab and on the Data quality tab. Do not quietly present a sampled number as fact.
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
eyeballing it, and state the MDE each surviving test can detect. **Every candidate — kept or
dropped — gets a row on the Opportunities tab with its gap, its volume, its MDE arithmetic, and
the verdict.** The dropped list is not waste; it is half of what the team is reviewing.

Rank what survives on: size of the measured gap × traffic affected × how directly it touches the
primary conversion.

## Step 5 — Design the tests

For each surviving opportunity, write a test in the house format:

- **Hypothesis**, as IF / THEN / BECAUSE. The BECAUSE must cite the finding it came from, with the
  number. "BECAUSE only 24% of mobile sessions scroll far enough to see all products" — not
  "BECAUSE users prefer clarity".
- **Test type** (usually AB Test), **Pages**, **Audience**, **Primary metric**,
  **Secondary metrics** (bounce rate and the downstream conversion, so you catch a win that moves
  the top of the funnel and breaks the bottom).
- **Expected MDE** from Step 4.

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
| **README** | Property and id, date range, the starting URL and funnel type the user gave, who confirmed the funnel and when, a one-line index of every tab, a summary of any data-quality flags, and the generated timestamp |
| **Funnel** | The confirmed funnel as a table (step, event, where it fires, URL), then the step-to-step drop-off tables: whole property, by device, by channel group, by top landing pages |
| **One tab per Step 3 slice** | The full table for that slice, named plainly (`Landing pages`, `LP x Device`, `LP x Channel`, `Sources`, `Campaigns`, `Devices`, `New vs returning`, `Countries`, `Daily trend`…) |
| **Data quality** | Every plausibility flag, sampling/thresholding note, and `(not set)`/Unassigned bucket, each with where it was seen and what it means for reading the data |
| **Opportunities** | Every candidate from Step 4, kept and dropped: the measured gap, the volume behind it, the MDE arithmetic (sessions per variant, detectable effect), the verdict, and the reason |
| **Hypotheses** | One row per surviving test: name, IF, THEN, BECAUSE, evidence (tab + row/segment it traces to), pages, audience, primary metric, secondary metrics, expected MDE, the seven priority sub-scores, total, rank |

Rules for the build:

- **Write real numbers, not strings.** Rates go in as fractions with a `0.0%` number format,
  volumes as integers with `#,##0` — the team will want to re-derive and re-sort, and a column of
  text can do neither.
- Formatting is light and consistent: bold header row (white on blue `#2F6BED`), freeze the header,
  autofilter on every data tab, sensible column widths. No charts this phase — the review is about
  the data, and a dependable table beats a decorative one.
- Every data tab states its own date range and its source tool in a line above the header, so a
  tab forwarded on its own still says what it is.
- **Do not trim, round away, or top-N a tab to make it tidy.** Comprehensiveness is what the team
  asked to see.

Then **verify before handover (ADR-0006)**: reopen the file with openpyxl and check that every
expected tab exists and holds the rows you meant to write, spot-check at least three numbers
against the original tool responses, and confirm every evidence pointer on the Hypotheses tab names
a tab that actually exists. Fix and rebuild anything that fails; never deliver a workbook you have
not reopened.

## Deliver

Hand over the workbook file, and in chat:

- the funnel used, and that the user confirmed it before the pull
- what was pulled: the count of slices and rows, and anything that came back truncated or sampled
- the headline findings, briefly — three to five, each with its number
- tests proposed and candidates dropped, as counts
- any data-quality flags worth a sentence

Say plainly that this phase produces no deck: the workbook **is** the deliverable, for the
experimentation team to review the foundation the deck will later stand on.

## Avoid these

- **Do not stop and offer the user a menu when a tool is unavailable.** A missing browser has a
  defined degradation above. Take it, finish the audit, and report what was missing at handover.
  Ask only when proceeding would be *unsafe* or would make the output *wrong* — which is exactly
  the two asks this skill does have: the starting URL and funnel type in Step 1, and the funnel
  confirmation in 2c. Those two are required. Everything else you work out yourself.
- **Never invent behavioural evidence.** You have GA4 and screenshots. You do not have scroll maps,
  click maps or session recordings. If a hypothesis needs "users don't scroll", either get it from a
  GA4 `scroll` event or say the evidence is missing.
- **Never present a plausibility-flagged number as a finding.** It is a tracking bug until proven
  otherwise — it belongs on the Data quality tab, not under a hypothesis.
- **Never compare to "industry benchmarks".** We do not have a benchmark source. Compare segments
  within the property instead.
- **Never write a hypothesis whose BECAUSE number is not in a data tab.** The traceability is the
  point of this deliverable.
- **No em dashes in hypothesis and test text** — it gets pasted into client-facing decks later.
- Do not promise a test will win. Say what it is designed to move and what it can detect.
