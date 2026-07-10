---
name: tapa-weather-correlation
description: Correlate GA4 conversions with weather using Tapa's Weather Correlation via the Tether MCP — daily conversions for an event vs temperature/precipitation/wind for a location, scored 0-100 per metric and visualised in chat. Use when the user runs /tapa-weather-correlation, asks whether weather affects their sales/conversions, or wants an event correlated against weather.
---

# Tapa Weather Correlation

Correlate a GA4 event's daily conversions against weather (temperature, precipitation, wind
— Open-Meteo) for a location and date range. **No file output** — the deliverable is the
correlation scores + time series, visualised in chat.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_wc_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_wc_options`, `tapa_wc_list_properties`, `tapa_wc_run`,
  `tapa_wc_result`.
- **Works in normal claude.ai chat.** Runs as **your own GA4 access**.

## Step 1 — Gather the five critical inputs (ASK for any that are missing; never guess)

1. **GA4 property** → `property_id` (numeric). Ground names via `tapa_wc_list_properties`
   (no args → accounts; with `account_id` → properties); if ambiguous, show candidates and ask.
2. **Event** → `event_name` (e.g. `purchase`). If unsure which event counts, ask.
3. **Date range** → `start_date` + `end_date` (YYYY-MM-DD). Longer ranges give steadier
   correlations — suggest 2–3 months if the user has no preference, but let them decide.
4. **Location** → `location` (e.g. "Greater London", "Manchester", "United Kingdom").
5. **Location type** → `location_type`, OPTIONAL: `region` (default), `city`, or `country` —
   offer exactly the choices from `tapa_wc_options`. Country mode averages several major
   cities and also returns per-city detail.

## Step 2 — Run and poll

Call `tapa_wc_run`. If it returns `answer_status: "pending"` with a `job_id`, tell the user
it's running and poll `tapa_wc_result` with that `job_id` until it finishes. Never abandon a
pending job or start a duplicate run.

The finished output carries the **`results`** JSON: `correlation_results` (per weather
metric: a 0–100 `score` + a plain-English `message`), a `time_series` (`dates`,
`conversions`, `avg_temp_c`, `precipitation_mm`, `wind_speed_kmh`), and for country mode
`weighted_correlation_results` + `processed_cities` + an `analysis_note`.

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** There is no download link for this tool —
the visual IS the deliverable:

- **Correlation scores** — one scored bar (0–100) per weather metric, labelled with the
  metric, its score, and its `message` verbatim. Use `weighted_correlation_results` as the
  headline in country mode (note the averaging via `analysis_note`).
- **Time series** — a line chart of daily `conversions` with the strongest-correlating
  weather metric overlaid (dual axis), built from `time_series`.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

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

In this skill: correlation strength 0–100 → blue magnitude bar; if you show the sign, positive green / negative red.

## Guardrails

- Never fabricate scores or series points — everything comes from `results`.
- Correlation ≠ causation: report strong scores as "moves with the weather", flag likely
  confounders (seasonality, promotions) rather than claiming weather drives sales.
- If every score is weak, say so plainly — that's a legitimate finding.
