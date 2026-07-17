---
name: tapa-content-decay-detector
description: Find decaying search queries with Tapa's Content Decay Detector via the Tether MCP — compares two Search Console Queries exports and classes every query Declining/Stable/Growing with click, impression, CTR and position deltas, visualised in chat with a workbook download link. Use when the user runs /tapa-content-decay-detector, asks which queries or content are decaying/losing clicks, or wants two GSC periods compared.
---

# Tapa Content Decay Detector

Turn two Google Search Console "Queries" exports into (1) the Content Decay workbook (every
query classed Declining / Stable / Growing with metric deltas) and (2) an in-chat
visualisation of the decay picture.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_cdd_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_cdd_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_cdd_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_cdd_options`, `tapa_cdd_upload`, `tapa_cdd_run`,
  `tapa_cdd_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — The two exports (BOTH REQUIRED — ask if missing; never guess the order)

Two GSC **Queries** exports, and the period order matters:

1. **Period 1 = the OLDER window** → `period1_file_url`.
2. **Period 2 = the NEWER window** → `period2_file_url`.

If the user gave fewer than two files, ask. If they gave two but didn't say which covers the
earlier dates, **ask — a swapped order flips every trend**. (Filenames or the user's framing
often make it obvious; confirm when in doubt.)

Accepted types (also in `tapa_cdd_options`): **.csv / .xlsx only** — decline other types.
The query column may be named `Top queries`, `Query` or `Keyword`; metric columns (Clicks,
Impressions, CTR, Position) are matched case-insensitively. If a run fails with a column
error, relay it and ask for a corrected export.

**How to stage each file** — call `tapa_cdd_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll

Call `tapa_cdd_run` with both `file_url`s. If it returns `answer_status: "pending"` with a
`job_id`, tell the user it's running and poll `tapa_cdd_result` until it finishes. Never
abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook: Summary, Full List, and per-status sheets).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (e.g. declining / stable / growing
counts) and `charts` (self-describing — e.g. the status mix and the biggest click losses).
Render **every KPI card and every chart present**, faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the Declining sheet is where the action is.

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

In this skill: Declining → red `#DC2626`, Stable → grey `#9CA3AF`, Growing → green `#16A34A`; click/impression/CTR/position deltas → positive green, negative red.

## Guardrails

- Never render placeholder numbers or URLs — render once, with real values from `results`.
- Never fabricate trends; every figure comes from `results` / the workbook.
- Declining = clicks down ≥10% between periods; call it a signal to investigate, not proof
  the content is bad (seasonality and SERP changes also move clicks).
