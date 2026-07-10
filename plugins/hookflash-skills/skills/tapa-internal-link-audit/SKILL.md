---
name: tapa-internal-link-audit
description: Find the best internal-link sources for new pages with Tapa's Internal Link Audit via the Tether MCP — ranks a site's existing pages by content similarity to each new page, visualised in chat with a download link to the results workbook. Use when the user runs /tapa-internal-link-audit, asks where to add internal links for a new page, or wants link-source suggestions from a site crawl.
---

# Tapa Internal Link Audit

Turn a whole-site crawl plus one or more new pages into (1) the Internal Link Audit workbook
(existing pages ranked as internal-link sources per new page) and (2) an in-chat
visualisation of the top opportunities.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_ila_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_ila_options`, `tapa_ila_upload`, `tapa_ila_run`,
  `tapa_ila_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — The two files (BOTH REQUIRED — ask if missing; never guess)

1. **Whole-site crawl** (Screaming Frog export) → `full_crawl_file_url` — the pool of pages
   that could give an internal link.
2. **New page(s) file** → `single_page_file_url` — the page or pages that need links, one row
   per page, same Screaming Frog columns.

If the user gave one file, ask for the other. If they gave two and it's ambiguous which is
the site crawl vs the new pages, **ask**.

Accepted types (also in `tapa_ila_options`): **.csv / .xlsx only** — decline other types.
Required columns for both: `Address, Title 1, Meta Description 1, H1-1, Indexability` (only
Indexable pages count as link sources). If a run fails with a column error, relay it and ask
for a corrected export.

**How to stage each file** — call `tapa_ila_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll

Call `tapa_ila_run` with both `file_url`s. If it returns `answer_status: "pending"` with a
`job_id`, tell the user it's running and poll `tapa_ila_result` until it finishes. Never
abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook: a Summary sheet plus one sheet per new page, sources ranked by similarity).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` and `charts` (self-describing —
e.g. top link sources per page). Render **every KPI card and every chart present**,
faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the per-page sheets hold the full ranked source lists.

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

In this skill: source relevance / similarity score → blue magnitude bar (higher = stronger link source).

## Guardrails

- Never render placeholder numbers or URLs — render once, with real values from `results`.
- Never fabricate link suggestions; everything comes from `results` / the workbook.
