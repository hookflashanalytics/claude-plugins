---
name: tapa-url-mapper
description: Map a site's URLs to new destinations with Tapa's URL Mapper via the Tether MCP — an LLM follows your worked examples per page type, visualised in chat with a download link to the results workbook. Use when the user runs /tapa-url-mapper, wants URLs mapped to a new structure from example mappings, or asks for a URL map / migration mapping driven by page-type examples.
---

# Tapa URL Mapper

Turn an old-site crawl plus worked example mappings into (1) the URL Mapper results workbook
(a destination URL per crawled URL, with confidence + QA sheets) and (2) an in-chat
visualisation of mapping confidence.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_um_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_um_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_um_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_um_options`, `tapa_um_upload`, `tapa_um_run`, `tapa_um_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — Gather the inputs (ASK for anything required that's missing; never guess)

**Required:**
1. **Old-site crawl** (Screaming Frog export) → `crawl_file_url`. Columns: `Address, Title 1,
   Meta Description 1, H1-1, Indexability`.
2. **Example mappings file** → `example_file_url`. Columns: `page type, url, destination url`.
   Its `page type` column **defines the page-type vocabulary** the mapper uses — tell the user
   this if their examples look thin (a page type with no example can't be mapped well).

**Optional (offer once, don't push):**
- **Equivalence list** (hreflang/market-equivalent URLs) → `equivalence_file_url`.
- **Context notes** (free-text mapping rules, e.g. "blog posts move under /insights/") →
  `context_text`.

Accepted types (also in `tapa_um_options`): **.csv / .xlsx only** — decline other types. If a
run later fails with a column error, relay it and ask for a corrected export.

**How to stage each file** — call `tapa_um_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll (this one is long-running)

Call `tapa_um_run` with the gathered inputs. This is the slowest Tapa tool (LLM-generative,
up to ~30 minutes on large crawls) and it reports progress:

- If it returns `answer_status: "pending"` with a `job_id`, tell the user it's running (relay
  any `progress` message), then poll `tapa_um_result` with that `job_id` until it finishes.
  Never abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
results workbook: Full URL Map, Needs Approval, QA and Summary sheets).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (e.g. URLs mapped, needs-approval
count) and `charts` (self-describing — e.g. confidence split, page-type mix). Render **every
KPI card and every chart present**, faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires. Point the user at the **Needs Approval** sheet — those rows are
the mapper's own low-confidence flags.

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

In this skill: mapping confidence → blue magnitude bar; per page-type groups → categorical series.

## Guardrails

- Never render placeholder numbers or URLs — render once, with real values from `results`.
- Never fabricate mappings; everything comes from `results` / the workbook.
- Low-confidence rows are "needs human review", not confirmed mappings — say so.
