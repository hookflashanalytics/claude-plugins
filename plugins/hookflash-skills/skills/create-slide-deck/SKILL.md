---
name: create-slide-deck
description: >-
  Build a polished, on-brand Hookflash PowerPoint deck from a brief, topic,
  document, or analysis — using the REAL Hookflash template's slide master, not
  an invented design. Use whenever the user runs /create-slide-deck, or asks to
  "make/create/build a slide deck / presentation / .pptx", "turn this into
  slides", "put this in a deck", "write me a presentation", or wants slides
  produced from content they provide. You choose the right layout per slide from
  the Layout Catalog below (like a designer flipping through the master), the
  deck is assembled server-side via the `build_slide_deck` tool, and you then
  REVIEW the returned per-slide thumbnails like a design director — fixing any
  defective slide before handing over the download link. Works in ANY client
  (normal chat, web, Cowork) with no local PowerPoint or python needed.
---

# /create-slide-deck — build an on-brand Hookflash deck

You produce a real `.pptx` that uses Hookflash's **actual slide master** — its
fonts, colours, dark/light backgrounds and triangle motif. You never invent a
design system, and you never dump text blindly into boxes. The workflow is a
designer's workflow: **pick the right layout for each slide**, fill it
completely, then **look at the result and fix what's wrong**. Assembly happens
server-side via the **`build_slide_deck`** MCP tool, which returns a download
link *plus a JPEG thumbnail of every slide* — your design review.

The server also enforces **quality gates**: composite layouts (cards, pillars,
steps) are all-or-nothing, and picture boxes must get a chart, an image, or be
removed. A 400 error means the plan violates a gate — it tells you exactly
what's missing. **Don't satisfy a gate with filler text; pick a layout that
matches your content's shape instead.**

## Step 0 — Preconditions (the build tool)

This skill builds the deck by calling the **`build_slide_deck`** MCP tool
(served by the **Tether** connector).

- **If `build_slide_deck` is NOT in your available tools:** the Tether connector
  isn't connected, or its tools haven't loaded in this session yet. Tell the
  user, in plain English:
  > To build the deck I need Hookflash's **Tether** connector switched on. Turn
  > on / reconnect the **Tether** connector, then **start a new chat** (tool
  > lists are cached per chat), and run `/create-slide-deck` again.

  Then stop — don't try to build the deck any other way (no local PowerPoint, no
  generic design tool; the whole point is the real template).
- You do **not** need Cowork or any local tooling — building is server-side.

## Step 1 — Understand the brief

Read whatever the user gave (a brief, doc, analysis, or data). If it's thin, ask
1–2 sharp questions (audience? key takeaway? roughly how many slides?). A good
default is **8–14 slides**. For a results/analysis hand-off, a **single results
slide** is often what's wanted — don't pad it.

Then shape the content BEFORE choosing layouts: one idea per slide, expressed as
a short title (≤ ~6 words) plus 3–6 phrase-length points. If an idea needs two
slides, it's two ideas.

## Step 2 — Choose layouts (the Layout Catalog)

Pick the layout that fits each slide's content **shape**, by index (0–30). The
contact sheets `references/layout-catalog-1.jpg` / `-2.jpg` show every layout
rendered, if present — but the tables below are authoritative.

**Design system:** dark charcoal is the primary background; a cream/light
alternate exists for content-heavy slides. The triangle-fractal motif lives on
the layouts — you get it for free. **Never invent shapes, bars or accent
lines.** **Furniture:** idxs `2` (date) and `4` (slide number) exist on most
layouts — never fill them.

### Quick router — content shape → layout

| Your content is… | Use |
|---|---|
| Deck opener / closer / section break | 0 / 29 / 3·4·5 |
| One idea + 4–6 supporting points | 12 (dark) · 13/14 (light) |
| One bold statement (+ optional image or chart) | 6, or 19 for a short light one-liner |
| A two-sided compare | 15 (text) · 7 (two images) |
| Exactly 3 rich themes (tags + proof points) | 20 |
| Exactly 3 short steps/reasons | 22 |
| Exactly 4 steps with detail | 21 |
| Exactly 4 features (heading + sub + 4 ticks) | 23 (dark) · 24 (light) |
| Exactly 4 short definitions | 16 (dark) · 17/18 (light) |
| 3–4 items each with an image | 11 / 10 |
| Agenda of exactly 3 parts | 28 |
| A/B-test or case-study results | 25 (hero chart) · 26 · 27 |

### Covers, dividers & brand (dark)
| # | What it is | Placeholders |
|---|-----------|--------------|
| 0 | **Cover** | `0` title, `1` subtitle — the subtitle renders as a kicker ABOVE the title; keep it one short line |
| 1 | Brand divider (big logo) | none |
| 2 | Near-empty dark canvas | none |
| 3 / 4 / 5 | Section titles (variants) | `0` title |
| 29 | **Closing brand** — logo + motif | none — the standard last slide |

### Statement + imagery (picture boxes need a chart, an image, or `remove`)
| # | What it is | Placeholders |
|---|-----------|--------------|
| 6 | Big statement + one large visual | `0` title (large, fits ~3 lines), `13` picture (4.6×4.1") |
| 8 / 9 | Title + body + hero visual (dark / light) | `0` title, `15` body, `13` picture (5.4×5.5" right half) |
| 7 | Title + body + **two** images | `0` title, `15` body, `14`+`13` pictures (2.8" squares) |
| 10 | **4 image-cards** | `0`, `15` intro · bodies `16`/`18`/`20`/`22` · 0.5" icon pics `17`/`19`/`21`/`23` |
| 11 | **3 image-cards** | `0`, `15` intro · bodies `16`/`18`/`20` · icon pics `17`/`19`/`21` |

### Text content
| # | What it is | Placeholders |
|---|-----------|--------------|
| 12 | Title left + body right (dark, 16pt) | `0`, `13` body — needs 4–6 points or it looks empty |
| 13 | Light variant, narrow body (4.0") | `0`, `13` |
| 14 | Light variant, tall body (5.7×4.6") | `0`, `13` |
| 15 | Title + two body columns (light) | `0`, `14` left, `13` right |
| 16 | **4 text columns** (dark, 10pt!) | `0`, columns left→right `26`/`23`/`24`/`25` |
| 17 / 18 | 4 text columns (light / light+motif) | `0`, columns left→right `14`/`23`/`24`/`25` |
| 19 | Short statement on light | `0` only (6.0×0.9" top-left) — ≤ ~12 words or it dominates the slide awkwardly |
| 28 | **Agenda panel** (dark) | `0` title, rows `31`/`32`/`33` — has a baked-in "Overview" heading, so DON'T also title it "Overview"; exactly 3 one-line rows |
| 30 | Capabilities icon row | `0` only (icons are decorative) |

### Composite layouts — all-or-nothing (server-enforced)
Their pills, ticks, numbers and dividers are baked into the layout artwork and
render even when empty — so using one means filling **every** idx listed.

| # | What it is | Full idx map |
|---|-----------|--------------|
| 20 | **3 pillars** (icon, header, 2 tag pills, 3 tick bullets) | P1: header `17`, tags `15`/`16`, ticks `14`/`18`/`19` · P2: header `23`, tags `21`/`22`, ticks `20`/`24`/`25` · P3: header `29`, tags `27`/`28`, ticks `26`/`30`/`31`. Headers are 20pt — keep ≤ ~16 chars; tags are 1–2 words; ticks ≤ ~5 words |
| 21 | **4 numbered steps** (header + 4 bullets each) | S1: `32` + `14`/`18`/`19`/`33` · S2: `37` + `34`/`35`/`36`/`38` · S3: `42` + `39`/`40`/`41`/`43` · S4: `47` + `44`/`45`/`46`/`48` |
| 22 | **3 numbered steps** | `32` / `37` / `42` — one short phrase each (wraps to ~2 lines fine) |
| 23 / 24 | **4 feature cards** (dark / light) | C1: heading `32`, sub `31`, ticks `33`–`36` · C2: `38`, `37`, `39`–`42` · C3: `44`, `43`, `45`–`48` · C4: `50`, `49`, `51`–`54`. Card headings one line |
| 25 | **Case study** ⭐ Challenge/Process/Results | `31` challenge, `32` process, `33` results note, stat numbers `37`/`38`/`39` + labels `34`/`35`/`36`, hero pic `43` (put the chart here), small pic `14` (usually `remove`) |
| 26 | Results w/ learnings (light) | `31` overview, `32` learnings, stats as 25, small pic `14` |
| 27 | Results, text-led (dark, no pics) | `31` overview, `32` results, stats as 25 |

### Styling inside a box (verified against the template)
- Text lands with the template's own style: **no bullets, level-0 size per box**
  (16pt bodies, 10pt columns, 20pt pillar headers…).
- **Never use `level` > 0** — higher levels fall out of the layout's style into
  big, bulleted master defaults (inverted hierarchy).
- Hierarchy inside one box = rich items: a **bold** first line, optionally with
  `size`: e.g. in a 10pt column, `{"text": "Statistical", "bold": true,
  "size": 14}` then body lines at `{"size": 12}`. In 16pt bodies, plain
  `{"text": "…", "bold": true}` reads as a header without a size bump.
- Stats on 25/26/27: the big number is the `37`/`38`/`39` box (`"+18.4%"`), its
  label the matching `34`/`35`/`36` (`"Add-to-cart"`). Fill both of every pair.

### Images & charts
- **`charts`** render natively in any picture box with the house palette
  (control blue → variant green…). Use a chart for any numeric story — the 25
  hero box `43` is the classic spot.
- **`images`** take a public **https URL the user supplied** (client logo,
  screenshot, product shot). Never invent/hotlink stock imagery. No image? Use
  a chart, `remove` the box, or prefer a text layout.

### Composing the deck
- Sandwich: open dark (0), keep text-heavy content light, close dark (29).
- **Vary layouts** — never the same content layout twice in a row, and avoid
  using any one more than twice per deck (the server warns at 3).
- **Never repeat a slide title** — one idea, one slide (the server warns).
- Section dividers (3/4/5) only between real chapters, not before every slide.

## Step 3 — Storyboard + self-critique

Draft one line per slide: **layout index → title → what fills it.** Then
critique your own storyboard against this checklist *before* building:

1. Does every composite layout have enough real content to fill it completely —
   no filler invented to satisfy the gate?
2. Any duplicate titles or split ideas? Merge them.
3. Same layout twice in a row, or 3+ times overall? Vary it.
4. Titles ≤ ~6 words? Points phrase-length (≤ ~12 words)?
5. Every picture box accounted for (chart / user image / remove)?
6. Would slide N look empty? (12/13/14 with fewer than 4 points, a column with
   one line…) — pick a tighter layout instead.

Show the storyboard to the user for a non-trivial deck, then build.

## Step 4 — Build via `build_slide_deck`

Turn the storyboard into a `slides` array and call **`build_slide_deck`** once
with the whole plan. Each slide:

```json
{
  "layout": 25,
  "text": {
    "0": "Sticky add-to-cart on mobile PDP",
    "31": ["Mobile add-to-cart 12% below desktop", "High PDP exit"],
    "32": ["Pinned CTA on scroll", "3 weeks, 50/50, mobile only"],
    "34": "Add-to-cart", "37": "+18.4%",
    "35": "Transactions", "38": "+6.1%",
    "36": "Significance", "39": "99%",
    "33": "Clear winner — roll out to 100% of mobile."
  },
  "remove": [14],
  "charts": [
    { "at": 43, "type": "column", "title": "Add-to-cart rate (%)",
      "categories": ["Control", "Variant"],
      "series": { "Add-to-cart rate": [4.9, 5.8] } }
  ]
}
```

Rules for the plan:
- **`text`** keys are placeholder idxs (as strings). A **string** fills one
  line; an **array** fills one paragraph per item. Items are strings or rich
  dicts `{"text": …, "bold": true?, "size": pt?}` (see Styling above).
- **`charts`** go into a picture placeholder (`at`); house palette applied
  server-side. **`images`** are `{ "at": idx, "url": "https://…" }`.
- **`remove`** any unused picture placeholder.
- Pass **`template: "hookflash_general"`** (the default) and a **`filename`**
  (the deck title).
- A **400** lists exactly what a quality gate needs (e.g. missing idxs on a
  composite layout). Fix the plan — or switch layout — and call again.

## Step 5 — Review the thumbnails (mandatory)

The tool returns `warnings` plus a **JPEG thumbnail of every slide**. This is
your design review. **Never deliver a deck you haven't looked at.**

Inspect EVERY thumbnail for:
- text overflowing its box, colliding with artwork, or clipped
- near-empty slides (one lonely line in a big box, a column half the height of
  its neighbours)
- walls of text; unreadably small text
- two consecutive slides that look near-identical
- awkward image crops; charts with unreadable labels
- anything a design director would bounce

Treat each `warnings` entry as guilty until the thumbnail proves it innocent.
If any slide fails: adjust those slides in the plan and call
`build_slide_deck` again (the full plan rebuilds). **At most two rebuild
rounds** — then ship the best version rather than looping.

## Step 6 — Deliver

Give the user the download link and a one-line summary (slide count + the
storyboard). Offer to tweak specific slides — that's just adjusting the plan
and calling `build_slide_deck` again.

## Notes

- Never invent numbers — every figure comes from the user's content/analysis.
- Building is server-side; there are no local files to manage. The template +
  builder + quality gates live in Tapa (`/api/general/slide_deck/build`,
  `backend/app/services/slide_deck.py`); thumbnails come from LibreOffice in
  the same service. If the template changes, regenerate this catalog with
  `scripts/build_catalog.py` and update Tapa's `REQUIRED_TEXT` metadata to
  match.
