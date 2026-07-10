---
name: tapa-auto-audit
description: Audit a GA4 property's configuration with Tapa's GA4 Auto Audit via the Tether MCP — ~80 best-practice checks (retention, signals, streams, conversions…) visualised in chat with a workbook download link. Use when the user runs /tapa-auto-audit, asks for a GA4 audit / setup health check, or wants a property's configuration checked against best practice.
---

# Tapa GA4 Auto Audit

Turn a GA4 property ID into (1) the Auto Audit workbook (~80 configuration checks, each
passed / warning / failed / do-manually) and (2) an in-chat visualisation of the audit.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_aa_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_aa_list_properties`, `tapa_aa_run`.
- **Works in normal claude.ai chat.** The audit runs as **your own GA4 access** — the property
  must be one your Google account can see. If Tapa answers that a Google reconnect is needed,
  tell the user to reconnect Google inside Tapa and retry.

## Step 1 — The property (REQUIRED — resolve it, don't guess)

One critical input: the **numeric GA4 property id**.

- If the user gave a property *name* (or nothing), ground it: call `tapa_aa_list_properties`
  with no arguments to list their accounts, then again with the chosen `account_id` to list
  properties, and match by name. If the match is ambiguous, show the candidates and ask.
- If the user gave a numeric id, use it directly.

## Step 2 — Run (synchronous, but slow)

Call `tapa_aa_run` with `property_id`. It's synchronous — the result comes back in the same
call — but can take a minute or two (~80 live GA4 API checks); warn the user it's running.
The output contains a **`results`** object and a **`download_url`** (the audit workbook).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (passed / warnings / failed /
manual counts) and `charts` (self-describing — e.g. the outcome donut and issues by area).
Render **every KPI card and every chart present**, faithfully; skip what's absent. Follow the
visual with the handful of **failed** checks called out by name (from `results`, verbatim) —
those are what the user will act on.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires — the workbook has every check with its detail.

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

In this skill: config-check results → pass green / warning amber / fail red; an overall score → a blue magnitude bar; check categories → categorical series.

## Guardrails

- Never render placeholder numbers — render once, with real values from `results`.
- Never fabricate check outcomes; every verdict comes from `results` / the workbook.
- "Do manually" rows are checks the API can't see — list them as follow-ups, not failures.
