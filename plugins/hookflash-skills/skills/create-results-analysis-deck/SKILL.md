---
name: create-results-analysis-deck
description: >-
  Turn a completed A/B-test results analysis into Hookflash's client-facing PEA
  results one-pager — one branded slide per test (Overview / Results /
  Learnings / Recommendations + Original/Variation visuals), built server-side
  from the real PEA template via the `build_slide_deck` tool. Use when the user
  runs /create-results-analysis-deck, asks for a results slide, one-pager, PEA
  slide, or deck from an A/B test's results, or wants the output of
  /tapa-results-analysis turned into slides. Works in ANY client (normal chat,
  web, Cowork) with no local PowerPoint or python needed.
---

# /create-results-analysis-deck — the PEA results one-pager

You produce a real `.pptx` on Hookflash's **PEA one-pager template**: a dark
left panel with baked-in **Overview / Results / Learnings / Recommendations**
section headers, and a cream right panel for **Original / Variation** visuals.
One slide = one test. Assembly is server-side via the **`build_slide_deck`**
MCP tool with **`template: "pea_results_1pager"`**, which returns a download
link *plus a JPEG thumbnail of every slide* — your design review.

The section headers are baked into the layout artwork, so the server rejects
a plan that leaves any section empty (a 400 lists the missing idxs). **Never
satisfy the gate with filler — get the real content first.**

## Step 0 — Preconditions (the build tool)

This skill builds the deck by calling the **`build_slide_deck`** MCP tool
(served by the **Tether** connector).

- **If `build_slide_deck` is NOT in your available tools:** the Tether
  connector isn't connected, or its tools haven't loaded in this session yet.
  Tell the user, in plain English:
  > To build the slide I need Hookflash's **Tether** connector switched on.
  > Turn on / reconnect the **Tether** connector, then **start a new chat**
  > (tool lists are cached per chat), and run `/create-results-analysis-deck`
  > again.

  Then stop — don't build the deck any other way (no local PowerPoint, no
  invented design; the whole point is the real PEA template).
- You do **not** need Cowork or any local tooling — building is server-side.

## Step 1 — Gather the content (per test)

The slide is **recommendation-led**, not a data dump. For each test you need:

| Content | Where it comes from |
|---|---|
| Test code + name | The ticket / the user (e.g. `HF-042: Sticky basket CTA`) |
| Description (one line: what changed) | Ticket or user |
| Dates ran | The analysis date range |
| Pages targeted | Ticket or user |
| Results — the KPI numbers | **A completed results analysis in this chat** (the `results` object from `/tapa-results-analysis`), or numbers the user pastes. **Never invent or recompute numbers.** |
| Learnings (one line) | Draft it from the result; confirm wording with the user if unsure |
| Recommendations (one line) | Draft it from the result (roll out / iterate / stop); this is the slide's point — make it decisive |
| Original + Variation screenshots | Optional — public **https** image URLs from the user. Ask once; don't block on it (there's a chart fallback) |

If there is **no results analysis in the chat yet**, point the user to run
`/tapa-results-analysis` first (it pulls the GA4 numbers this slide needs) —
or accept figures they paste, attributed to them.

## Step 2 — Fill the one-pager (layout 0, verified plan format)

One `slides[]` entry per test, always `"layout": 0`. Placeholder map
(**keys are strings**; idxs `2`/`4` are date/page furniture — never fill):

| idx | Section | Fill with | Fit (10pt box) |
|---|---|---|---|
| `"0"` | Title (18pt) | `"HF-042: Sticky basket CTA"` — `code: name`, one line | ≤ ~60 chars |
| `"31"` | Overview · description | `"Description: pinned add-to-basket CTA on scroll for mobile PDPs"` | **one line**, ≤ ~75 chars |
| `"35"` | Overview · dates | `"Dates ran: 1 Jun – 21 Jun 2026"` | one line |
| `"36"` | Overview · pages | `"Pages targeted: mobile product detail pages"` | one line |
| `"32"` | Results | Array, one metric per line: `"Add-to-basket up 18.4% (99% ss)"` · `"Revenue per user up 4.2% (not significant, 88% conf)"` | 2–4 lines, ≤ ~75 chars each |
| `"34"` | Learnings | One sentence — what we now know | ≤ ~150 chars |
| `"33"` | Recommendations | One decisive sentence — roll out / iterate / stop | ≤ ~150 chars |
| `"45"` / `"46"` | Right-panel labels | See visuals below | one line each |
| `43` / `44` | Picture boxes (right panel) | `images` / `charts` / `remove` — see below | — |

Hard rules:
- **Overview rows `31`/`35`/`36` are ONE paragraph each, label inline** — a
  second paragraph collides with the row below (verified on a real render).
- Keep the labels the template uses: `Description:` / `Dates ran:` /
  `Pages targeted:` — that's the house wording.
- Metric lines state the KPI, direction, uplift % and significance. Down =
  `"down x%"`. Not significant = say so with the confidence. The numbers come
  from the analysis — never rounded into a better story.

**Right panel — pick ONE of these:**
- **Screenshots (preferred):** `"images": [{"at": 43, "url": "<original>"},
  {"at": 44, "url": "<variation>"}]`, `"45": "Original"`, `"46": "Variation"`.
  Only user-supplied public https URLs — never invent imagery.
- **No screenshots → chart fallback:** a native chart of the primary KPI in
  box 43, its name in the label above:
  `"charts": [{"at": 43, "type": "column", "categories": ["Control", "Variation"],
  "series": {"Add-to-basket rate (%)": [4.9, 5.8]}}]`, `"45": "Add-to-basket rate (%)"`,
  and `"remove": [44, 46]`. (Two KPIs? Put a second chart in 44 with its label
  in 46 instead of removing them.)
- **Neither:** `"remove": [43, 44, 45, 46]` — but prefer the chart; an empty
  right panel wastes half the slide.

## Step 3 — Build

Call **`build_slide_deck`** once with the whole plan:
`template: "pea_results_1pager"`, `filename` = `"<code> results one-pager"`
(or the client/sprint name for a multi-test deck), and the `slides` array.
A **400** lists exactly which section idxs are missing — fill them with real
content and call again.

## Step 4 — Review the thumbnails (mandatory)

The tool returns `warnings` plus a **JPEG thumbnail of every slide**. **Never
deliver a slide you haven't looked at.** Check each thumbnail for:

- text overflowing its section — Learnings/Recommendations wrap fine to 2
  lines, but 3+ lines collide with the next section header: tighten the copy
- Overview rows colliding (a two-line description does this — shorten it)
- metric lines wrapping (shorten KPI names, not the numbers)
- awkward screenshot crops (images are centre-cropped to portrait boxes —
  a full-page screenshot usually survives; a wide banner doesn't. If a crop
  fails, swap that box to the chart fallback)
- chart axis labels unreadable or the chart drowning in whitespace

Treat each `warnings` entry as guilty until the thumbnail proves it innocent.
If a slide fails, fix the plan and rebuild — **at most two rebuild rounds**,
then ship the best version rather than looping.

## Step 5 — Deliver

Give the user the download link and a one-line summary per slide (test →
verdict → recommendation). Offer to tweak wording or swap visuals — that's
just adjusting the plan and calling `build_slide_deck` again.

## Notes

- Every figure comes from the results analysis (or the user). If a KPI was
  underpowered, the Results line should say so — don't dress it up.
- The template + builder + section gates live in Tapa
  (`backend/app/services/slide_deck.py`, template key `pea_results_1pager`);
  thumbnails come from LibreOffice in the same service. If the template
  changes, update Tapa's gate tables and this placeholder map together.
