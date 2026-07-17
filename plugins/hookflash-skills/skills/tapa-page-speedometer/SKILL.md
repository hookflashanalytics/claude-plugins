---
name: tapa-page-speedometer
description: Test page speed with Tapa's Page Speedometer via the Tether MCP — Google PageSpeed Insights over a list of URLs, Lighthouse scores and Core Web Vitals visualised in chat with a workbook download link. Use when the user runs /tapa-page-speedometer, asks how fast pages are, wants Lighthouse/PSI/Core Web Vitals scores, or asks for a page speed report.
---

# Tapa Page Speedometer

Turn a list of URLs into (1) the Page Speedometer workbook (Lighthouse performance scores +
Core Web Vitals per page, via Google PageSpeed Insights) and (2) an in-chat visualisation.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_ps_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_ps_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_ps_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_ps_options`, `tapa_ps_run`, `tapa_ps_result`. (No upload
  tool — the input is just URLs.)
- **Works in normal claude.ai chat.**

## Step 1 — The URL list (REQUIRED — ask if missing; never guess)

The tool needs one or more **full page URLs** (including `https://`). If the user named a site
but not pages, **ask which pages matter** — e.g. homepage, a product page, a category/listing
page, a blog post — rather than inventing URLs. Each URL takes ~15–30 seconds to test, so keep
the list modest (key templates, not whole sitemaps; hard limit 50 per run).

## Step 2 — Run and poll

Call `tapa_ps_run` with `urls`. If it returns `answer_status: "pending"` with a `job_id`, tell
the user it's running and poll `tapa_ps_result` until it finishes. Never abandon a pending job
or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (e.g. URLs tested, average
Lighthouse score, slowest page) and `charts` (self-describing — e.g. score bars per URL and
LCP/TBT/CLS columns). Render **every KPI card and every chart present**, faithfully; skip
what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the workbook has the full per-URL metric detail.

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

In this skill: Lighthouse/PSI score bands — good ≥90 green `#16A34A`, needs-work 50–89 amber `#F59E0B`, poor <50 red `#DC2626`; Core Web Vitals pass/fail → green/red.

## Guardrails

- Never render placeholder numbers or URLs — render once, with real values from `results`.
- Never fabricate scores; every figure comes from `results` / the workbook.
- PSI scores fluctuate run to run — treat small differences (±5) as noise, not regressions.
