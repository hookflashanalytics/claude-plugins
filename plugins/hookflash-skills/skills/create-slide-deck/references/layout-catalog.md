# Hookflash template — Layout Catalog

The bundled template (`assets/hookflash-template.pptx`) has **31 slide-master
layouts**. Their names (`26_Title Slide`, etc.) are meaningless — use the
**layout index** below (0–30) with `Deck.add(index)`.

**Always look at the two contact sheets first** — they show every layout
rendered from the real template, and each content box is stamped with its
placeholder `idx` and type, so the images are also your placeholder map:

- `references/layout-catalog-1.jpg` — layouts 0–15
- `references/layout-catalog-2.jpg` — layouts 16–30

For the exact placeholder idxs on any layout, run
`python scripts/decklib.py` (dumps idx + type + size per layout).

**Design system:** dark charcoal (`#1a1a1a`-ish) is the primary background; a
cream/light alternate exists for content-heavy slides. The signature motif is
the coloured triangle-fractal (cyan `#22D3EE`-ish, orange, purple, green) — it
lives on the layouts, so you get it for free. **Never draw your own shapes,
bars, or accent lines** — the template's design is the design.

**Furniture:** `idx 2` (date) and `idx 4` (slide number) exist on most layouts.
Ignore them — don't fill them.

---

## Covers, dividers & brand (dark)

| # | Bg | What it is | Key placeholders | Use for |
|---|----|-----------|------------------|---------|
| **0** | dark | **Cover** — large title + subtitle, motif bottom | `0` title, `1` subtitle | Deck opener / title slide |
| **1** | dark | **Brand divider** — big Hookflash logo, centred | none | Section break, intro holding slide |
| **2** | dark | Near-empty dark canvas, motif only | none | Rare — a custom/full-bleed slide |
| **3** | dark | Section title (title top, motif top-right) | `0` title | Section divider with a heading |
| **4** | dark | Section title (title left) | `0` title | Section divider |
| **5** | dark | Section title (title left, motif centre) | `0` title | Section divider variant |
| **29** | dark | **Closing brand** — big logo + full motif | none | Thank-you / closing slide |

## Statement + imagery

| # | Bg | What it is | Key placeholders | Use for |
|---|----|-----------|------------------|---------|
| **6** | dark | Title + one large image | `0` title, `13` picture | A statement backed by one visual |
| **8** | dark | Title + body + hero image | `0` title, `15` body, `13` picture | Text with a supporting image |
| **9** | light | Title + body + hero image (light) | `0` title, `15` body, `13` picture | Light variant of 8 |
| **7** | dark | Title + body + **two** images | `0` title, `15` body, `13`+`14` pictures | Before/after, two-shot compare |
| **10** | dark | **4 image-cards** (image + caption ×4) | `0` title, `15` intro; cards `16`/`17`pic, `18`/`19`pic, `20`/`21`pic, `22`/`23`pic | 4 items each needing an image |
| **11** | dark | **3 image-cards** | `0` title, `15` intro; cards `16`/`17`pic, `18`/`19`pic, `20`/`21`pic | 3 items each needing an image |

## Text content

| # | Bg | What it is | Key placeholders | Use for |
|---|----|-----------|------------------|---------|
| **12** | dark | Title (left) + body (right) | `0` title, `13` body | One point + explanation |
| **13** | light | Title + body (light) | `0` title, `13` body | Light variant of 12 |
| **14** | light | Title + body (light, alt) | `0` title, `13` body | Light variant |
| **15** | light | Title + **two** body columns | `0` title, `14` left body, `13` right body | Two-column prose |
| **16** | dark | **4 text columns** (10pt body style) | `0` title, columns left→right `26`/`23`/`24`/`25` | 4 short definitions/lists |
| **17** | light | 4 text columns (light) | `0` title, `14`/`23`/`24`/`25` bodies | Light 4-column |
| **18** | light | 4 text columns (light, motif) | `0` title, `14`/`23`/`24`/`25` bodies | Light 4-column variant |
| **19** | light | Plain title on light canvas | `0` title | Big pull-quote / statement |
| **28** | dark | **Overview panel** — title + up to 3 bullets | `0` title, `31`/`32`/`33` bodies | Agenda, summary, simple overview |
| **30** | dark | Capabilities — title + row of icons | `0` title (icons are decorative) | Services/capabilities overview |

## Process, steps & pillars

| # | Bg | What it is | Key placeholders | Use for |
|---|----|-----------|------------------|---------|
| **22** | dark | **3 numbered steps** (circles 1-2-3) | `0` title; step texts `32`/`37`/`42` (one phrase each — no bullet idxs exist) | 3-phase process/methodology |
| **21** | dark | **4 numbered steps** (circles 1-2-3-4) | `0` title; S1 `32`+`14`/`18`/`19`/`33` · S2 `37`+`34`/`35`/`36`/`38` · S3 `42`+`39`/`40`/`41`/`43` · S4 `47`+`44`/`45`/`46`/`48` | 4-phase process (fill ALL idxs) |
| **20** | dark | **3 pillars** with triangle icons + tick lists | `0` title; P1 header `17`, tags `15`/`16`, ticks `14`/`18`/`19` · P2 header `23`, tags `21`/`22`, ticks `20`/`24`/`25` · P3 header `29`, tags `27`/`28`, ticks `26`/`30`/`31` | 3 themes/pillars (fill ALL idxs; headers ≤ ~16 chars) |
| **23** | dark | **4 feature cards** (coloured tabs, tick lists) | per card: kicker `31`/`37`/`43`/`49`, title `32`/`38`/`44`/`50`, 4 bullets `33-36`/`39-42`/`45-48`/`51-54` | 4 features / workstreams / benefits |
| **24** | light | 4 feature cards (light) | same idxs as 23 | Light variant of 23 |

## Results / case study ⭐ (the A/B-test money slides)

These are purpose-built for a Hookflash results story — a narrative on the left
and **big stat callouts** with ▲/▼ arrows in a "Results" strip. Fill each
callout as a pair: number box (`37`/`38`/`39`, e.g. "+18.4%") + label box
(`34`/`35`/`36`, e.g. "Add-to-cart").

| # | Bg | What it is | Key placeholders | Use for |
|---|----|-----------|------------------|---------|
| **25** | light | **Challenge / Process / Results** + hero image | `0` title; `31` Challenge; `32` Process; `43` **hero image/chart** (large); `14` small 2nd image (fill or remove); stat numbers `37`/`38`/`39`, stat labels `34`/`35`/`36`; `33` results note | Flagship A/B-test results slide |
| **26** | light | **Overview / Learnings / Results** + image | `0` title; `31` Overview; `32` Learnings; `14` image; stat numbers `37`/`38`/`39`, labels `34`/`35`/`36` | Results with learnings (light) |
| **27** | dark | **Overview / Results** (no image) | `0` title; `31` Overview; `32`; stat numbers `37`/`38`/`39`, labels `34`/`35`/`36` | Results, dark, text-led |

---

## Placeholder gotchas (learned the hard way)

- **Empty PICTURE placeholders render as a coloured block** (cyan/orange), not
  nothing. On any layout, either fill a picture box (a chart or an image), or
  list it in `remove`. (Layout 25's small `idx 14` is the classic offender.)
  The server now rejects plans that leave one unhandled.
- **Feature cards (23/24) have 4 tick-rows baked into the layout.** The
  checkmarks show whether or not you add text — so fill all four bullets per
  card, or the card looks half-empty with naked ticks. Keep the card **title
  (`32`/`38`/…) to one line** — it sits directly above the kicker and a
  two-line title collides with it.
- **Stat callouts are two placeholders**, not one: the big number
  (`37`/`38`/`39`) and a separate small label above it (`34`/`35`/`36`). The
  ▲/▼ arrows are part of the layout.
- Furniture (`idx 2` date, `idx 4` slide number) — never fill.
- After building, **render and eyeball it** — these are exactly the things that
  only show up in the picture.

## Choosing well (do what a human would)

- **Sandwich:** open dark (0), keep content mostly light where it's text-heavy,
  close dark (29). Don't put 10 identical dark text slides in a row.
- **Match layout to content shape** — 3 things → layout 22/20; 4 things →
  21/23; a results story → 25/26/27; a comparison → 7. Don't force everything
  into the plain title+body layouts (12/13) — that's the "limited" feeling.
- **Vary** layouts across the deck; don't repeat one layout 6× running.
- **Don't overfill.** If a bullet list is long, split across two slides rather
  than shrinking text until it overflows.
- Titles are short (≤ ~6 words). Body bullets are phrases, not paragraphs.
