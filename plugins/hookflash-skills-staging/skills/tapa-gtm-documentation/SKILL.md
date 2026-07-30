---
name: tapa-gtm-documentation
description: Document a GTM container with Tapa's GTM Documentation via the Tether MCP — turns a container export .json into a styled workbook of every tag (vendor, triggers, variables, paused state), visualised in chat with a download link. Use when the user runs /tapa-gtm-documentation, wants a GTM container documented/audited into a spreadsheet, or shares a GTM export asking what's in it.
---

# Tapa GTM Documentation

Turn a GTM container export into (1) the GTM Documentation workbook (every tag with vendor,
tool connection, triggers, blocking triggers, paused state, custom code and variables) and
(2) an in-chat visualisation of the container's makeup.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_gd_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_gd_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_gd_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_gd_options`, `tapa_gd_upload`, `tapa_gd_run`.
- **Works in normal claude.ai chat.** The only surface difference is how the file travels
  (step 1). This tool is synchronous — no polling.

## Step 1 — The container export (REQUIRED — ask if missing; never guess)

One input: a **GTM container export** → `container_file_url`. **Only `.json` is accepted** —
decline other types. If the user doesn't have the export, tell them how: in Google Tag
Manager, **Admin → Export Container**, pick the workspace/version, download the `.json`.

**How to stage it** — call `tapa_gd_upload` with the filename:
- A `.json` whose text you can read → pass the full contents as `content_text` (no trimming).
- A local file in Claude Code / Cowork → omit `content_text`, PUT the raw bytes to the
  returned `upload_url` exactly as `how_to_upload` says.
- Either way, pass the returned `file_url` as `container_file_url`.

## Step 2 — Run (synchronous)

Call `tapa_gd_run` with `container_file_url`. The result comes back in the same call: a
**`results`** object plus a **`download_url`** (the workbook). If the container has no tags,
Tapa says so — report that and stop (there's no file).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (e.g. tags, paused, custom-code
counts) and `charts` (self-describing — e.g. tags by vendor and the paused/active split).
Render **every KPI card and every chart present**, faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the workbook is the full tag-by-tag documentation.

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

In this skill: tags per vendor → categorical series; paused tags → grey `#9CA3AF`; counts → blue magnitude bars.

## Guardrails

- Never render placeholder numbers — render once, with real values from `results`.
- Never fabricate tags or vendors; everything comes from `results` / the workbook.
