---
name: pull-crawl
description: Pull a domain's most recent NIGHTLY crawl from Tapa's monitoring pipeline via the Tether MCP — a styled workbook (Summary + every crawled page + a 30-day crawl-health Trends tab of charts), a deep link into the Tapa Crawler Dashboard, and AI insights delivered by Claude in chat. Use when the user runs /pull-crawl, asks for "last night's crawl", "the latest crawl of X", or wants the stored nightly crawl data for a site. This PULLS data already collected each night — to crawl a site fresh right now, use tapa-site-crawler instead.
---

# Pull Crawl (nightly)

Turn one domain into its latest nightly crawl report: a workbook with the full
crawl and a 30-day crawl-health Trends tab of charts, plus an in-chat
visualisation, YOUR insights in chat, and a dashboard deep link.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_nr_*` tools are limited to a small allow-list
  of test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_nr_*` tools are missing, the user is not
    on the allow-list: explain that Tapa skills are still in testing and access is limited to a
    small test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_nr_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_nr_options`, `tapa_nr_run`. (No upload tool — the input is
  just a domain. Synchronous — no polling, no job_id.)
- **Works in normal claude.ai chat.**

## Step 1 — Gather the inputs (ask, don't guess)

- **domain** (REQUIRED): the client site, e.g. `example.com`. One domain per run.

That's it. This skill always passes `report: "crawl"`.

## Step 2 — Run (synchronous)

Call `tapa_nr_run` with `{ domain, report: "crawl" }`. The answer comes back in the same
call: a `download_url` (the workbook) and a `results` object (KPIs + charts +
`results.meta`).

- If the response has **no file and an `info` message**, the domain isn't in the nightly crawl
  registry. Relay the message and offer a fresh one-off crawl via /tapa-site-crawler instead.
  Never fabricate a report for it.
- The crawl is **last night's** (nightly pipeline, 00:00 Europe/London). Its exact start time
  is in `results.meta.crawl_started_at` — always tell the user the crawl's date and time.

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** Render **every KPI card and every chart
present** in `results` (pages crawled, % indexable, broken pages, issues per page; the 30-day
crawl-health and pages-crawled trend lines), faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link and the dashboard link

- Put the `download_url` as a **plain clickable link in your reply** (widgets block
  downloads). Mention that the link expires. The workbook holds: **Summary** (run stamps and
  health KPIs), **Pages** (every crawled page with its issues), and **Trends** (line charts
  of per-night crawl health over the last 30 days; the numbers behind them sit on a hidden
  "Trends Data" sheet).
- Also share `results.meta.dashboard_url` as a plain link — it opens the **Tapa Crawler
  Dashboard's Health view** with this domain preselected and the date set to Today.

## Step 5 — AI insights (in chat, after the visual)

The workbook deliberately carries data only — the insights are YOURS, written in chat under
the visualisation. Write 3–6 sharp insights from the data: broken pages and where they
cluster, indexability shifts, issue hot-spots, trend direction over the 30 days, and the
single most valuable fix. Cite real numbers and URLs from `results`; every figure must come
from the data, never from memory of similar sites.

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

In this skill: status buckets — 2xx green `#16A34A`, 3xx amber `#F59E0B`, 4xx/5xx red
`#DC2626`, no response grey `#9CA3AF`.

## Guardrails

- Never render placeholder numbers or domains — render once, with real values from `results`.
- Never fabricate crawl contents; if the user asks what was found, read the workbook data
  rather than guessing.
- The nightly crawl may be capped (`Page cap` on the Summary tab) — on sites larger than the
  cap, absent pages can reflect crawl coverage, not the site.
- Issue flags (missing titles, duplicates, thin content…) are computed by a 06:30 UTC rebuild;
  a crawl pulled before then says so on its Summary tab — mention it if present.
- 30-day trends only reach back as far as the nightly pipeline has run for this domain — a
  short series is normal early on; say so rather than calling it a data problem.
