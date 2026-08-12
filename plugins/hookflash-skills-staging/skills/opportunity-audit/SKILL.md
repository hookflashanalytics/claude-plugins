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
     `google-analytics.com`) because of server-side tagging. Match on the path, as above. Record
     whichever host you actually saw — it goes on the Funnel tab.
   - The `tid` parameter gives you the measurement ID for free. Cross-check it against the property
     you resolved in Step 1; if they disagree, you are looking at the wrong property and everything
     downstream is wrong.
5. Capture a screenshot of each step as you go, and note its URL.

**When the walk blocks, hand that one step over — do not abandon the walk.** A bot challenge, a
login wall, a step that needs a real registration or policy number: say which step and what it
needs, ask the user to get you past that one thing, and carry on yourself from the other side. The
same goes for anything you judge to be past the stop line. Handing over a step is normal; handing
over the whole walk is what this step exists to avoid.

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

**Pull `totalUsers` alongside sessions on every slice, and converting users alongside conversions.**
Step 4 powers its tests on users, because that is what a test randomises on, and it cannot go back
for them later without re-running the whole pass. A slice with sessions but no users forces an
estimate onto every candidate that comes from it.

If the property, the funnel walk, or the user's brief suggests another split matters for this
client (site search use, logged-in state, a promo parameter), pull it too and give it a tab. The
list above is the floor, not the ceiling.

Then run these checks before you interpret anything. **These are gates on what you may conclude,
not a deliverable of their own** — the workbook has no data-quality tab. What each check produces
is a disqualification (a number that cannot become a hypothesis) and a sentence at handover.

- **Plausibility.** Flag any rate that is impossible (>100%), any two near-identical pages with a
  wildly different rate (a 4x gap between `/car-insurance` and `/insurance/car` is a tracking or
  redirect artefact far more often than a UX finding), any step whose completion rate exceeds the
  step before it, and any segment whose average order value or revenue per session is wildly out of
  line with the rest (usually cross-property or partial tracking). **A flagged number is
  disqualified: it does not become an opportunity and it does not become a hypothesis.** This is
  the single biggest way an automated audit embarrasses itself.
- **Sampling, thresholding and truncation.** If a response came back sampled, thresholded or
  row-limited, say so in the context line at the top of that slice's own tab (`Top 100 of 8,077 by
  sessions`). A top-N presented as a complete table is a lie the reader cannot detect.
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

Two-sided, 95% confidence, 80% power, comparing two proportions:

```
n per arm  = K · p(1-p) / (p · mde_rel)²
mde_rel    = sqrt( K · p(1-p) / n ) / p

K = 2 · (z(0.975) + z(0.80))²  =  2 · (1.95996 + 0.84162)²  =  15.6978
```

Use **15.6978**. `16` is the familiar rounded form and it is ~1% conservative, which is harmless,
but write the constant you used into the tab's context line either way so the number can be checked.

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
| **README** | Client and property name, GA4 property id, measurement id, date range, the property totals for the range, and a one-line index of every tab. Nothing else — no data-source line, no funnel-type or starting-URL echo, no who-confirmed-it line, no derivation note, no generated timestamp. The reviewer knows how the workbook was made; the README is there to say what is in it |
| **Funnel** | The confirmed funnel as a table (step, event, where it fires, URL), then the step-to-step drop-off tables: whole property, by device, by channel group, by top landing pages |
| **One tab per Step 3 slice** | The full table for that slice, named plainly (`Landing pages`, `LP x Device`, `LP x Channel`, `Sources`, `Campaigns`, `Devices`, `New vs returning`, `Countries`, `Daily trend`…) |
| **Opportunities** | Every candidate from Step 4 — KEEP, STRETCH and DROP: the measured gap, the segment's users over the range, users per arm, the arm count, the baseline per-user rate, `n·p`, the detectable relative effect (or `cannot be powered`), the verdict, and the reason. The context line states the constant, the confidence and power, and the unit |
| **Hypotheses** | One row per KEEP or STRETCH test: name, IF, THEN, BECAUSE, evidence (tab + row/segment it traces to), pages, audience, primary metric, secondary metrics, expected MDE, its Step 4 verdict, the seven priority sub-scores, total, rank |

Rules for the build:

- **Write real numbers, not strings.** Rates go in as fractions with a `0.0%` number format,
  volumes as integers with `#,##0` — the team will want to re-derive and re-sort, and a column of
  text can do neither.
- Formatting is light and consistent: bold header row (white on blue `#2F6BED`), freeze the header,
  autofilter on every data tab. No charts this phase — the review is about the data, and a
  dependable table beats a decorative one.
- **Every column is wide enough for its contents. No truncated cells anywhere in the workbook.**
  openpyxl has no autofit, so width is something you compute — see [Column widths and context
  lines](#column-widths-and-context-lines) below. This is not cosmetic: a cut-off cell in the middle
  of a review workbook is read as a mistake in the data.
- Every data tab carries one context line above the header: what the tab is, its date range, and
  any truncation or thresholding that applies to it (`Top 100 of 8,077 landing pages by sessions`).
  Not the source tool — every tab has the same source and repeating it fifteen times is noise.
- **Do not trim, round away, or top-N a tab to make it tidy.** Comprehensiveness is what the team
  asked to see.

### Column widths and context lines

Run both of these over **every sheet** as the last thing before saving, widths first. Do not
hand-pick widths per tab — they drift, and the tab you forget is the one that gets forwarded.

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

Then **verify before handover (ADR-0006)**: reopen the file with openpyxl and check that every
expected tab exists and holds the rows you meant to write, spot-check at least three numbers
against the original tool responses, and confirm every evidence pointer on the Hypotheses tab names
a tab that actually exists. **Recompute the MDE on at least two Opportunities rows from the inputs
printed on that row** and confirm they match what you wrote — the formula is easy to apply to the
wrong `p` — and confirm no row prints a detectable effect where `n·p < 10` or the result exceeds
0.5. **Check the widths too** — for every sheet, assert that each column's
width is at least the longest `display_len` in it (or that the column wraps and is at `MAX_W`), and
that every context line is either unwrapped with no row height or merged with one — a wrapped
banner with no height set is the crammed-cell bug. Those checks cost nothing and catch a tab you
built before adding a long row. Fix and rebuild
anything that fails; never deliver a workbook you have not reopened.

## Deliver

Hand over the workbook file, and in chat:

- the funnel used, and that the user confirmed it before the pull
- what was pulled: the count of slices and rows, and anything that came back truncated or sampled
- the headline findings, briefly — three to five, each with its number
- tests proposed and candidates dropped, as counts
- **the data-quality flags from Step 3**, in plain sentences: what looked wrong, where, and what
  you disqualified because of it. This is the only place they appear, so do not compress them to
  "some data-quality issues were found"

Say plainly that this phase produces no deck: the workbook **is** the deliverable, for the
experimentation team to review the foundation the deck will later stand on.

## Avoid these

- **Do not stop and offer the user a menu when a tool is unavailable.** A missing browser has a
  defined degradation above. Take it, finish the audit, and report what was missing at handover.
  Ask only when proceeding would be *unsafe* or would make the output *wrong* — which is exactly
  the two asks this skill does have: the starting URL and funnel type in Step 1, and the funnel
  confirmation in 2c. Those two are required and there is no third. In particular **do not ask
  permission to start the walk** — announce it and go. Everything else you work out yourself,
  including the whole route through the funnel.
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
