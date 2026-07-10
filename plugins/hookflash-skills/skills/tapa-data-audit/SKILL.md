---
name: tapa-data-audit
description: Check whether a tracking change hurt GA4 data with Tapa's GA4 Data Audit via the Tether MCP — an after-vs-before health audit around a change date (trends, channel mix, event deltas, LLM narrative), visualised in chat with a workbook link. Use when the user runs /tapa-data-audit, asks "did our GA4 data break after X", or wants data checked around a tag/consent/site change.
---

# Tapa GA4 Data Audit

Turn a GA4 property + a described tracking change + its date into (1) the Data Audit
workbook (after-vs-before comparison, up to 14 complete days each side) and (2) an in-chat
visualisation of what moved.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_da_*` tools
  are gated to allow-listed users during rollout — if you don't see them, reconnect and confirm
  you're on the allow-list.
- Tools under the Tether MCP: `tapa_da_list_properties`, `tapa_da_run`, `tapa_da_result`.
- **Works in normal claude.ai chat.** The audit runs as **your own GA4 access**. If Tapa
  answers that a Google reconnect is needed, tell the user to reconnect Google inside Tapa.

## Step 1 — Gather the three critical inputs (ASK for any that are missing; never guess)

1. **GA4 property** → `property_id` (numeric). If the user gave a name or nothing, ground it
   with `tapa_da_list_properties` (no args → accounts; with `account_id` → properties) and
   match by name; if ambiguous, show candidates and ask.
2. **What changed** → `change_description` (plain English, ≤2000 chars — it feeds the audit's
   narrative). If the user hasn't described the change, ask — "a change happened" isn't
   enough; what kind (tag added/removed, consent banner, migration…) shapes the analysis.
3. **When it changed** → `change_date` (YYYY-MM-DD). Must be **yesterday or earlier** —
   audits only use complete days. If the change was today, say the audit needs at least one
   complete day of after-data and offer to run tomorrow.

Optional: `property_label` (friendly name for the report) — use the property's display name
from discovery; don't ask.

The before/after comparison windows are derived server-side — never ask the user for windows.

## Step 2 — Run and poll

Call `tapa_da_run`. If it returns `answer_status: "pending"` with a `job_id`, tell the user
it's running (it queries GA4 day by day) and poll `tapa_da_result` with that `job_id` until
it finishes. Never abandon a pending job or start a duplicate run.

The finished output is text JSON with a **`results`** object and a **`download_url`** (the
workbook).

## Step 3 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary.** The `results` object is the same config
Tapa's own results viewer renders: `title`, `meta`, `kpis` (headline totals + signals) and
`charts` (self-describing — e.g. the daily trend line, channel donut, biggest event
changes). Render **every KPI card and every chart present**, faithfully; skip what's absent.
Quote the audit's own executive summary (from `results`) beneath the visual — it's the
plain-English verdict.

**How to render:** if an interactive-widget tool is available (e.g. `show_widget` — call its
`read_me` first), render through **that**; otherwise a self-contained HTML artifact (inline
CSS + inline SVG only, no external resources). Charts are real data charts from `results`.

## Step 4 — The workbook link

Put the `download_url` as a **plain clickable link in your reply** (widgets block downloads).
Mention that the link expires.

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

In this skill: health checks → pass green / warn amber / fail red; after-vs-before deltas → positive green, negative red; channel mix → categorical series.

## Guardrails

- Never render placeholder numbers — render once, with real values from `results`.
- Never fabricate signals; the audit's thresholds are deliberately conservative — report what
  it flags, and don't invent additional "problems" it didn't.
- A quiet audit ("no significant signals") is a good result — present it as such.
