---
name: pull-crawl-and-site-speed
description: Pull a domain's most recent NIGHTLY crawl AND nightly site speed audit from Tapa's monitoring pipelines via the Tether MCP, merged into ONE styled workbook (Summary + crawl pages + crawl trends + speed pages + speed trends), with a deep link into the Tapa Crawler Dashboard and AI insights written by Claude into the workbook's Summary tab. Use when the user runs /pull-crawl-and-site-speed or asks for a combined nightly report, "the full nightly picture", or crawl + speed together for a site. For just the crawl use pull-crawl; for just speed use pull-site-speed; to collect fresh data use tapa-site-crawler / tapa-full-site-speed-audit.
---

# Pull Crawl + Site Speed (nightly, one workbook)

Turn one domain into its combined nightly report: crawl health AND site speed
in a single workbook with 30-day trends for both, a Summary tab whose
AI-insights box YOU fill in (cross-referencing the two datasets), plus an
in-chat visualisation and a dashboard deep link.

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
- **Works in normal claude.ai chat** (the insights-into-workbook step needs file handling — see
  Step 5).

## Step 1 — Gather the inputs (ask, don't guess)

- **domain** (REQUIRED): the client site, e.g. `example.com`. One domain per run.

That's it. This skill always passes `report: "both"`.

## Step 2 — Run (synchronous)

Call `tapa_nr_run` with `{ domain, report: "both" }`. The answer comes back in the same
call: a `download_url` (the merged workbook) and a `results` object (KPIs + charts +
`results.meta`).

- **One half can be missing** (e.g. crawl present, speed not) — the workbook then ships the
  half that exists and `info` explains the gap. Relay it; don't call that a failure.
- If **neither** exists, the domain isn't in the nightly registry: relay the `info` message
  and offer /tapa-site-crawler or /tapa-full-site-speed-audit instead. Never fabricate.
- **The crawl and the audit can be from different nights** (they are separate pipelines).
  Both stamps are in `results.meta` (`crawl_started_at`, `speed_started_at`) — always state
  both dates, and point it out when they differ.

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** Render **every KPI card and every chart
present** in `results` — the crawl block (pages crawled, % indexable, broken pages, issues
per page, 30-day health trend) and the speed block (mobile/desktop performance, CO₂e per
view, 30-day performance trend) — faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link and the dashboard link

- Put the `download_url` as a **plain clickable link in your reply** (widgets block
  downloads). Mention that the link expires. The workbook holds: **Summary** (both runs'
  stamps and KPIs, the AI-insights box), **Crawl Pages**, **Crawl Trends**, **Speed Pages**
  and **Speed Trends**.
- Also share `results.meta.dashboard_url` as a plain link — it opens the **Tapa Crawler
  Dashboard's Health view** with this domain preselected and the date set to Today (the
  Site speed tab is one click away inside the dashboard).

## Step 5 — AI insights (you write them)

The workbook's Summary tab has a placeholder box (its cell is named in
`results.meta.insights_cell`). The server never fills it — you do.

1. Write 4–8 sharp insights **cross-referencing the two datasets** — that's this skill's
   whole point over running the two pulls separately: heavy pages vs slow page types, broken
   pages vs their template's speed, crawl-health trend vs performance trend, and the single
   most valuable fix overall. Judge Core Web Vitals by field data when present (Google's
   thresholds: LCP 2.5s/4s, INP 200ms/500ms, CLS 0.1/0.25). Cite real numbers and URLs.
2. **If you can execute code and edit files** (Claude Code / Cowork): download the workbook,
   replace the placeholder text in that exact cell with your insights (openpyxl: load, set the
   cell's value, save — the cell is merged and wrapped, so just set the anchor cell), then
   **verify by re-reading the cell** — the placeholder text must be gone and your text present.
   Deliver the edited workbook to the user as the file deliverable.
3. **If you cannot edit files** (plain claude.ai chat): give the insights in chat and tell the
   user the workbook's insights box is intentionally left as a placeholder.

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
`#DC2626`; Lighthouse score bands — good ≥90 green, needs-work 50–89 amber, poor <50 red;
CO₂e per view — ≤0.25 g green, ≤0.5 g amber, above red.

## Guardrails

- Never render placeholder numbers or domains — render once, with real values from `results`.
- Never fabricate crawl contents or scores; every figure comes from `results` / the workbook.
- **Carbon figures are estimates** — always label them "SWDM v4".
- PSI scores fluctuate run to run — treat small differences (±5) as noise, not regressions.
- The nightly crawl may be capped (`Page cap` on the Summary tab); issue flags arrive with a
  06:30 UTC rebuild — a pre-06:30 pull says so on its Summary tab.
- 30-day trends only reach back as far as the nightly pipelines have run for this domain — a
  short series is normal early on; say so rather than calling it a data problem.
