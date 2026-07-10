---
name: tapa-cannibalisation-detector
description: Scan a whole site for keyword/content cannibalisation with Tapa's standalone Cannibalisation Detector via the Tether MCP — flags page pairs whose titles/descriptions/H1s are ≥70% similar, visualised in chat with a download link to the results workbook. Use when the user runs /tapa-cannibalisation-detector, asks which pages cannibalise each other, or wants overlapping/competing pages found in a site crawl.
---

# Tapa Cannibalisation Detector

Turn a whole-site Screaming Frog crawl into (1) the Cannibalisation Detector workbook (page
pairs flagged as risks with similarity scores) and (2) an in-chat visualisation of the worst
overlaps.

This is the **standalone detector** (whole-crawl content-embedding similarity). It is
different from Content EEATer's Search-Console cannibalisation sub-check — if the user wants
a single blog post audited, use `/tapa-content-eeater` instead.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_cd_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_cd_options`, `tapa_cd_upload`, `tapa_cd_run`, `tapa_cd_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — The crawl file (REQUIRED — ask if missing; never guess)

One input: a **whole-site Screaming Frog crawl export** → `crawl_file_url`. If the user
hasn't provided one, ask for it (the tool needs a crawl file — it does not crawl the site
itself; offer `/tapa-site-crawler` if they need a crawl).

Accepted types (also in `tapa_cd_options`): **.csv / .xlsx only** — decline other types.
Required columns: `Address, Title 1, Meta Description 1, H1-1, Indexability` (only Indexable
pages with text are compared; at least 2 needed). If a run fails with a column error, relay
it and ask for a corrected export.

**How to stage the file** — call `tapa_cd_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll

Call `tapa_cd_run` with `crawl_file_url`. If it returns `answer_status: "pending"` with a
`job_id`, tell the user it's running (large crawls compare every page pair) and poll
`tapa_cd_result` until it finishes. Never abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook: Summary + Cannibalisation Risks sheets).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (e.g. pages compared, risk pairs
found) and `charts` (self-describing — e.g. the most-similar pairs and the risk-band split).
Render **every KPI card and every chart present**, faithfully; skip what's absent. If no
pairs were flagged, show that as the (good) headline result — not an empty chart.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the Risks sheet holds every flagged pair with its score.

## Visualisation style (Hookflash house standard)

Use these exact values for **every** chart, bar, KPI card and table you render in the
step above, so all Tapa reports look consistent. Keep visuals self-contained — inline
CSS + inline SVG only, no external resources (CDN scripts / chart libs / web fonts are
blocked and the visual collapses to raw HTML).

- **Font:** system sans-serif (`-apple-system, Segoe UI, Roboto, Arial, sans-serif`).
- **Card:** white `#FFFFFF` background, text `#111827`, muted labels `#6B7280`, hairline borders `#E5E7EB`.
- **Bars:** empty track `#F3F4F6`, 2px rounded corners, one consistent bar height, value label at the bar's end.
- **Categorical series (assign in this order):** blue `#2F6BED`, green `#22C55E`, purple `#8B5CF6`, orange `#F97316`, teal `#14B8A6`.
- **Status / bands:** good/pass green `#16A34A`, warning/borderline amber `#F59E0B`, poor/critical red `#DC2626`, neutral/none grey `#9CA3AF`.
- **Deltas (vs a baseline / previous period):** positive green `#16A34A`, negative red `#DC2626`, flat grey `#6B7280`.
- **Single-measure magnitude / score:** one blue ramp light→dark — never a rainbow.
- Pair colour with a text label or icon (never colour alone); sentence case; round every displayed number.

In this skill: title/description/H1 similarity → blue magnitude bar; risk level high/medium/low → red/amber/grey.

## Guardrails

- Never render placeholder numbers or URLs — render once, with real values from `results`.
- Never fabricate overlaps; every pair and score comes from `results` / the workbook.
- Similarity ≥ 0.70 is a *risk flag*, not proof of cannibalisation — recommend human review.
