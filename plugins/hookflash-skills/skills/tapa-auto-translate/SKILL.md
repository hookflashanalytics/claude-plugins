---
name: tapa-auto-translate
description: Translate a site's titles, H1s and meta descriptions into other languages with Tapa's Auto Translate via the Tether MCP — Google Cloud Translation over a crawl file, one workbook tab per language, with a download link in chat. Use when the user runs /tapa-auto-translate, wants page metadata translated for international SEO, or asks to translate a crawl/site into given languages.
---

# Tapa Auto Translate

Turn a Screaming Frog crawl plus a language list into the Auto Translate workbook — for every
page, the original and translated Title, H1 and Meta Description, one tab per language
(Google Cloud Translation).

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_at_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_at_options`, `tapa_at_upload`, `tapa_at_run`, `tapa_at_result`.
- **Works in normal claude.ai chat.** The only surface difference is how files travel (step 1).

## Step 1 — Gather the inputs (BOTH REQUIRED — ask if missing; never guess)

1. **Crawl file** (Screaming Frog export) → `crawl_file_url`. Columns: `Address, Title 1,
   Meta Description 1, H1-1` (Indexability is NOT needed for this tool).
2. **Target languages** → `target_languages` (a list of language codes). Call
   `tapa_at_options` and match the user's request against its `languages` catalogue
   (133 code→label entries). If the user named languages, map them to codes from that list;
   if they haven't said which languages, **ask** — never pick languages for them. Unknown
   codes are rejected by Tapa.

Accepted file types (also in `tapa_at_options`): **.csv / .xlsx only** — decline other types.

**How to stage the file** — call `tapa_at_upload` with the filename:
- A CSV whose text you can read → pass the full contents as `content_text` (no trimming).
- A binary `.xlsx`, or a local file in Claude Code / Cowork → omit `content_text`, PUT the raw
  bytes to the returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` into the run.

## Step 2 — Run and poll

Call `tapa_at_run` with `crawl_file_url` and `target_languages` (e.g. `["fr","de"]`). If it
returns `answer_status: "pending"` with a `job_id`, tell the user it's running and poll
`tapa_at_result` until it finishes. Never abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook, one tab per language).

## Step 3 — Report in chat

This tool's `results` carries **KPI stat cards only** (e.g. pages translated, languages) —
render them as a compact stat-card visual (via `show_widget` if available — call its
`read_me` first — else a self-contained inline-CSS artifact). There are no charts for this
tool; do not invent any. A couple of real example rows (original → translated title) quoted
from the workbook are welcome **only if** you actually have them — never fabricate
translations.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the workbook holds every translation, one tab per language.

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

In this skill: KPI cards use the card tokens; give each target language one categorical colour (in order); per-language counts → blue magnitude bars.

## Guardrails

- Only offer languages from `tapa_at_options` — never invent codes.
- Never fabricate translations or counts; everything comes from `results` / the workbook.
- Translation quality is machine-grade: recommend native review before publishing.
