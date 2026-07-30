---
name: tapa-full-site-speed-audit
description: Audit a whole site's speed with Tapa's Full Site Speed Audit via the Tether MCP — crawl the domain, benchmark Lighthouse speed by page type (mobile/desktop), pull real-user Core Web Vitals for every country the Chrome UX Report holds, estimate CO2e per page view, research CMS-specific fixes, and compare up to 3 competitors, visualised in chat with a workbook download link. Use when the user runs /tapa-full-site-speed-audit, asks to audit a SITE's speed, benchmark a site vs competitors, or asks about a site's carbon footprint. For a quick check of a few specific URLs, use tapa-page-speed-audit instead.
---

# Tapa Full Site Speed Audit

Turn one domain into a full site-speed audit: speed by page type (Homepage, PDP, PLP,
Article, Service…), real-user Core Web Vitals by country, CO₂e per page view, grounded
CMS-specific advice, and an optional competitor benchmark — as (1) a workbook and (2) an
in-chat visualisation.

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_ssb_*` tools are limited to a small allow-list
  of test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_ssb_*` tools are missing, the user is not
    on the allow-list: explain that Tapa skills are still in testing and access is limited to a
    small test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_ssb_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- Tools under the Tether MCP: `tapa_ssb_options`, `tapa_ssb_run`, `tapa_ssb_result`. (No upload
  tool — the input is just a domain.)
- **Works in normal claude.ai chat.**

## Step 1 — Gather the inputs (ask, don't guess)

- **domain** (REQUIRED): the site to audit, e.g. `example.com`. One domain per run.
- **cms** (ask if not obvious): drives the platform-specific speed research. One of Shopify,
  WordPress, Magento, BigCommerce, Salesforce Commerce Cloud, Wix, Squarespace, Webflow,
  Drupal — omit for custom/unknown platforms (the research section is skipped).
- **device**: `both` (default), `mobile`, or `desktop`. A single device roughly **halves the
  run time** — offer it when the user is in a hurry.
- **competitors** (optional): up to 3 domains benchmarked side by side.

## Step 2 — Run, poll, and NARRATE the wait

Call `tapa_ssb_run`. **This is a long run — typically 10–30 minutes.** Poll `tapa_ssb_result`
while it's pending and **relay the `progress` message to the user each time it changes** — it
narrates every stage (pages discovered while crawling, PSI runs completed, research steps). A
quiet spell means a slow crawl, not a hang. Never abandon a pending job or start a duplicate;
if the user asks "is it stuck?", show the latest progress message.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (mobile/desktop performance,
slowest page type, CO₂e per page view, real-user LCP…) and `charts` (self-describing — speed
by page type, CO₂e by page type, slowest countries, competitor bars). Render **every KPI card
and every chart present**, faithfully; skip what's absent.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the workbook has the Category Summary (averages per page
type, with an example URL each), per-page results, real-user field data by country, and the
CMS research.

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

In this skill: Lighthouse score bands — good ≥90 green `#16A34A`, needs-work 50–89 amber
`#F59E0B`, poor <50 red `#DC2626`; Core Web Vitals pass/fail → green/red; CO₂e per view —
≤0.25 g green, ≤0.5 g amber, above red.

## Guardrails

- Never render placeholder numbers or domains — render once, with real values from `results`.
- Never fabricate scores; every figure comes from `results` / the workbook.
- **Carbon figures are estimates** — always label them "SWDM v4" (the model behind
  websitecarbon.com; v4 figures run ~⅔ lower than older calculators, so compare like with like).
- **Country coverage is data-driven**: only countries with enough Chrome traffic appear in the
  field data — a single-market site often shows just one country. Say so if the user expects more.
- Category Summary metrics are **averages across the category's sampled pages**, not the
  example URL's own scores.
- PSI scores fluctuate run to run — treat small differences (±5) as noise, not regressions.
