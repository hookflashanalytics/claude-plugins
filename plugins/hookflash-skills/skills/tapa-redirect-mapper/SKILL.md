---
name: tapa-redirect-mapper
description: Build a site-migration redirect map with Tapa's Redirect Mapper via the Tether MCP — match every old-site URL to its best new-site equivalents by content similarity, visualised in chat with a download link to the results workbook. Use when the user runs /tapa-redirect-mapper, asks for a redirect map / redirect mapping for a migration, or wants old URLs matched to new URLs from two crawl files.
---

# Tapa Redirect Mapper

Turn two Screaming Frog crawls (old site + new site) into (1) the Redirect Mapper results
workbook (top-3 new-site matches per old URL, by title/description/H1 embedding similarity)
and (2) an in-chat visualisation of the mapping quality.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_rm_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_rm_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_rm_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_rm_options`, `tapa_rm_upload`, `tapa_rm_run`, `tapa_rm_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — The two crawl files (BOTH REQUIRED — ask if missing; never guess)

The mapper needs exactly two Screaming Frog crawl exports, and it matters which is which:

1. **Old-site crawl** → becomes `old_crawl_file_url` (the URLs that need redirecting).
2. **New-site crawl** → becomes `new_crawl_file_url` (the redirect destinations).

If the user gave fewer than two files, **ask** for the missing one(s). If they gave two files
but didn't say which site is which, **ask — never assume the order**; a swapped map is worse
than no map.

Accepted types (also in `tapa_rm_options`): **.csv / .xlsx only** — decline other types and ask
for a proper Screaming Frog export. Required columns: `Address, Title 1, Meta Description 1,
H1-1, Indexability` (only Indexable rows are mapped). If a run later fails with a column
error, relay it and ask for a corrected export.

**How to stage each file** — call `tapa_rm_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll

Call `tapa_rm_run` with `old_crawl_file_url` and `new_crawl_file_url`. It submits the job and
polls briefly:

- If it returns the finished output, continue to step 3.
- If it returns `answer_status: "pending"` with a `job_id`, tell the user it's still running
  and poll `tapa_rm_result` with that `job_id` until it finishes. Never abandon a pending job
  or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
results workbook).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, a `meta` line, `kpis` (stat cards — e.g. URLs
mapped, average similarity) and `charts` (each entry self-describes its type, title, labels
and data — e.g. the similarity distribution and the match-confidence split). Render **every
KPI card and every chart present**, faithfully, and skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` from a
visualize connector — call its `read_me` first), render through **that**. Otherwise fall back
to a self-contained HTML artifact: inline CSS + inline SVG only, **no external resources**.
Charts are real data charts built from the numbers in `results` — never decorative shapes.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets are sandboxed and
block downloads). Mention that the link expires — the workbook holds the full redirect map
(Summary, Redirect Map, Best Match Only sheets).

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

In this skill: match confidence / similarity → blue magnitude bar; unmatched or low-confidence rows → amber/grey.

## Guardrails

- Never render placeholder numbers or URLs — render once, with the real values from `results`.
- Never fabricate matches or scores; everything comes from `results` / the workbook.
- Low-similarity matches are flagged by the tool — present them as "needs human review", not
  as confirmed redirects.
