---
name: run-results-analysis
description: Analyse a Hookflash A/B test end-to-end — pull GA4 results via the Tether Tapa tools, compute significance, visualise the results in chat, and on request build an on-brand slide deck. Use when the user runs /run-results-analysis, pastes an experiment or ticket and asks how a test performed, or asks to analyse, report on, or make a deck for an A/B test's results or significance.
---

# Run Results Analysis

Turn an A/B test into (1) the Tapa results workbook, (2) an in-chat results visualisation
with significance, and (3) — only when the user asks — an on-brand slide deck.

## Prerequisites (read first)

- **Use your Tether MCP connector, signed in as an allow-listed user.** The `tapa_ra_*` tools are
  gated to allow-listed users during rollout (staging for everyone; production for allow-listed
  users) — if you don't see them, reconnect and confirm you're on the allow-list.
- **Works in normal claude.ai chat** when the analysis returns a structured `results` object and
  slides are built server-side (`tapa_ra_generate_deck`). **Cowork / Claude Code is only needed
  for the fallbacks** (parsing the `.xlsx` yourself, or local deck building) — see the fallback
  notes in steps 3 and 5.
- Tools under the Tether MCP: `tapa_ra_list_ga4_properties`, `tapa_ra_list_ga4_audiences`,
  `tapa_ra_list_ga4_event_names`, `tapa_ra_generate_audience_excel`, `tapa_ra_audience_result`,
  `tapa_ra_generate_deck`.
- This `SKILL.md` is **self-sufficient** for the primary flow. `REFERENCE.md` and `scripts/` are
  optional depth + Cowork-only fallbacks — install the **whole folder** to get them, but the happy
  path works without them.

## Step 1 — Gather the required inputs (ASK if any are missing; do not guess)

Required — if the user hasn't given all four, ask for the missing ones before continuing:
1. **Date range** (start + end, YYYY-MM-DD).
2. **GA4 property** (name or id — resolve with `tapa_ra_list_ga4_properties`).
3. **Audiences** — either the audience names to compare (need **≥2**), **or** an **experiment
   name**: list the property's audiences with `tapa_ra_list_ga4_audiences` and match by name; if
   the match is ambiguous, show the candidates and ask.
4. **Control audience (REQUIRED — always ask, never assume).** The user must nominate which
   audience is the **control** — the group that was *not* shown a variation. Uplift and confidence
   are computed for every other audience *against this control*, and the control itself shows no
   uplift/confidence. If the user hasn't said which is control, ask before running.
5. **KPIs being tested** — one or more, as `{label, event_name, [condition]}`. Ground
   `event_name` with `tapa_ra_list_ga4_event_names` when unsure.

Optional:
- **Custom start** — only if the user needs it. If none is given, **assume session start** and
  do not ask.

## Step 2 — Run the analysis

Call `tapa_ra_generate_audience_excel` with `ga4_property_id`, `start_date`, `end_date`,
`audiences`, `kpis`. **List the control audience FIRST in `audiences`** — Tapa treats the first
entry as the baseline, so uplift/confidence for the rest are computed against it and the control's
own uplift/confidence come back blank. The output is a **text JSON** payload with a `download_url`
(the workbook) and a **`results`** object. If it returns a `job_id` (still running), poll
`tapa_ra_audience_result` until finished. (The tool returns a link, not a file attachment — hand
the `download_url` to the user as a clickable link.)

## Step 3 — Read the results

Use the **`results` object** from the output — Tapa computes per-variation/per-device counts plus
conversion rate, uplift, confidence and significance (matching Tapa's own panel). No parsing
needed. Keep the whole `results` object verbatim; you pass it to `tapa_ra_generate_deck` later.

*Fallback (Cowork/Claude Code only):* if `results` is absent, download the `.xlsx` and compute with
`scripts/stats.py` (see REFERENCE.md).

## Step 4 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary** — even when the result is "not significant".

**How to render it (for working buttons):** if an interactive-widget tool is available (e.g.
`show_widget` from a visualize connector — call its `read_me` first), render through **that**, because
it exposes a `sendPrompt(...)` hook so buttons can act. Only if no widget tool is available, fall
back to a native HTML artifact (buttons that need `sendPrompt` won't fire there — see the gate below).
Either way the markup is **self-contained**: inline CSS + inline SVG only, **no external resources**
(CDN scripts / chart libs / web fonts get blocked and the artifact "collapses" to raw HTML). Keep JS
minimal; render bars as static inline SVG/CSS.

Content, per KPI:
- A **results table**: variation · users · conversions · conversion rate · uplift · confidence.
- A **conversion-rate bar chart** by variation (one bar per variation; label each with its %).
- A **verdict badge**: "Significant (NN.N% conf)" / "Not significant" / "Underpowered" (flag any
  variation with very few conversions — e.g. <25 — as underpowered, not a real result).
- Header line: property · date range · audiences.

**Sheet download → a plain text link in the chat message, NOT a widget button.** The widget runs
in a sandboxed iframe that blocks `window.open`/downloads, so put the workbook `download_url` as a
normal clickable link in your reply alongside the widget (it always works). `scripts/viz_template.html`
is the ready pattern for the widget itself.

**One widget button — "Generate Slides"** — firing
`sendPrompt('generate results-analysis slides for <experiment>')`. `sendPrompt` *is* allowed in the
sandbox, so this works.

**Avoid these two failures (both seen in testing):**
- **Never render with a placeholder URL.** Put the *actual* `download_url` from the tool output into
  the button before you render — do not render a `DOWNLOAD_URL_PLACEHOLDER` and then re-render (that
  produces the visual twice). Render once, with real values.
- **The chart must be a real data bar chart** built from the numbers (inline SVG/CSS bars). Never
  emit decorative/abstract shapes or a generated image as "the graph".

Then **STOP — never generate slides here.** The user decides after seeing significance. If the
surface can't fire the Generate Slides button (no `sendPrompt`, e.g. plain chat), **also ask in text**
whether they want slides for any result, and wait for the reply.

## Step 5 — Generate slides (only on the user's explicit go-ahead)

Call **`tapa_ra_generate_deck`** with the `results` object from step 3 and a `summary` (experiment
name, test type, pages, audience, primary metric, hypothesis IF/THEN/BECAUSE). It returns the
finished `.pptx` as a **`download_url`** (table + overall conversion-rate bar + device-split chart
per KPI) — hand the user that link. Works in any client.

*Fallback (Cowork/Claude Code only):* if `tapa_ra_generate_deck` is unavailable,
`get_slide_template({ template:"results_analysis" })` → download → fill with `scripts/build_deck.py`.

## Notes
- Never fabricate numbers — every figure comes from Tapa's `results`. If a KPI has too few
  conversions to be conclusive, say so (surface it as underpowered).
- Terminology: "variation" = a compared audience; "uplift" = variation rate ÷ control rate − 1.
