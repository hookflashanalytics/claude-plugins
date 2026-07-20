---
name: tapa-results-analysis
description: Analyse a Hookflash A/B test end-to-end — pull GA4 results via the Tether Tapa tools, compute significance, and visualise the results in chat with the raw converted-user counts, a conversion-rate bar and a confidence-vs-threshold bar. Use when the user runs /tapa-results-analysis, pastes an experiment or ticket and asks how a test performed, or asks to analyse, report on, or read the results/significance of an A/B test. Building a slide or deck from the results is a SEPARATE skill — point the user to /create-slide-deck; do not build slides here.
---

# Run Results Analysis

Turn an A/B test into (1) the Tapa results workbook and (2) an in-chat results visualisation that
**always shows the raw converted-user counts** and **how close each variation is to significance**.
**Slides are out of scope** — if the user wants a deck, they run the separate `/create-slide-deck`
skill (see [Slides are a separate skill](#slides-are-a-separate-skill)).

## Prerequisites (read first)

- **Use your Tether MCP connector.** The `tapa_ra_*` tools are limited to a small allow-list of
  test users while Tapa skills are in testing.
  - If NO Tether tools are available at all, the Tether connector isn't connected or enabled for
    this session — tell the user to reconnect/enable it, then retry.
  - If other Tether tools are available but the `tapa_ra_*` tools are missing, the user is not on
    the allow-list: explain that Tapa skills are still in testing and access is limited to a small
    test group for now — Connor Jennings (AI Ops) can add them.
- **If a `tapa_ra_*` call fails with an authentication or authorisation error from Tapa**, the
  user hasn't authenticated the Tapa app yet: direct them to https://tapa.hookflash.co.uk/connect
  and explain they need to sign in there to authenticate the app, then retry.
- **Works in normal claude.ai chat** — the analysis returns a structured `results` object and the
  visualisation renders client-side. **Cowork / Claude Code is only needed for the fallback**
  (parsing the `.xlsx` yourself) — see the fallback note in step 3.
- Tools under the Tether MCP: `tapa_ra_list_ga4_properties`, `tapa_ra_list_ga4_audiences`,
  `tapa_ra_list_ga4_event_names`, `tapa_ra_generate_audience_excel`, `tapa_ra_audience_result`.
- This `SKILL.md` is self-sufficient. `REFERENCE.md` / `scripts/` are optional Cowork-only depth.

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

## Step 3 — Read the results (and lock in the raw counts)

Use the **`results` object** from the output — Tapa computes per-variation/per-device counts plus
conversion rate, uplift, confidence and significance (matching Tapa's own panel). No parsing
needed.

**The KPI counts are CONVERTED USERS, not conversions.** Tapa queries GA4 `activeUsers` filtered
to the KPI event, so each count is the number of *users who fired the event at least once* — not
the number of times the event fired. The `results` JSON names this field `conversions` for
historical reasons; **always label it "converted users" in everything you show** (the workbook
itself heads the column "Converted Users"). Never call these figures "conversions".

**Always resolve a raw converted-users COUNT for every variation, on every KPI — this is a hard
requirement.** (A past report showed counts for some metrics but not others; that must not happen.)
If `results` includes a count, use it; if it only gives users + rate, derive
`converted_users = round(users × rate)`. For every percentage you show, you must be able to state
the "**X of Y users**" behind it.

*Fallback (Cowork/Claude Code only):* if `results` is absent, download the `.xlsx` and compute with
`scripts/stats.py` (see REFERENCE.md).

## Step 4 — Visualise in chat — ALWAYS (do not substitute plain text)

**You must render a visual, not a text summary** — even when the result is "not significant".

**How to render it:** if an interactive-widget tool is available (e.g. `show_widget` from a
visualize connector — call its `read_me` first), render through that; otherwise fall back to a
self-contained HTML artifact. Either way the markup is **self-contained**: inline CSS + inline SVG
only, **no external resources** (CDN scripts / chart libs / web fonts get blocked and the artifact
"collapses" to raw HTML). Render bars as static inline SVG/CSS.

Render, per KPI, in this order, using the **Standard visualisation style** below:

1. **Raw-values table (transparency — always):** columns
   *variation · users · **converted users (count)** · conversion rate · uplift · confidence*.
   Every row has a converted-users count (derive if needed). Control shows "—" for uplift/confidence.
   This table is the transparency layer — it must always be present.
2. **Conversion-rate bar** — one horizontal bar per variation (control first). Label each bar with
   **the rate AND the raw count**, e.g. `60.76%  ·  5,855 / 9,635` (converted users / users), so
   the percentage is never shown without its underlying numbers.
3. **Confidence bar (how close to significant)** — one horizontal bar per *variation* (not the
   control), scaled 0–100%, with a marked **95% significance threshold** line. This visualises how
   close the test is to a reliable result. Fill colour by band (see palette): ≥95% green,
   90–95% amber, <90% grey.
4. **Verdict badge** — "Significant (NN.N% conf)" / "Not significant" / "Underpowered" (flag any
   variation with very few converted users — e.g. <25 — as underpowered, not a real result).
5. **Header line:** property · date range · audiences.

### Standard visualisation style (use these exact values — consistency across every report)

- **Font:** system sans-serif stack (`-apple-system, Segoe UI, Roboto, Arial, sans-serif`) — no
  web fonts (blocked in the sandbox).
- **Card:** white `#FFFFFF` background, text `#111827`, muted labels `#6B7280`, hairline borders `#E5E7EB`.
- **Control / baseline:** blue `#2F6BED`.
- **Variations (assign in this order):** green `#22C55E`, purple `#8B5CF6`, orange `#F97316`, teal `#14B8A6`.
- **Significance bands:** pass/significant green `#16A34A`; approaching amber `#F59E0B`; below/none grey `#9CA3AF`.
- **Uplift text:** positive green `#16A34A`; negative red `#DC2626`; zero/neutral grey `#6B7280`.
- **Bars:** empty track `#F3F4F6`, 2px rounded corners, one consistent bar height across all charts,
  value label at the bar's end.
- **95% threshold marker:** dashed line `#111827` with a small `95%` tick label.

*(This is the house default. If a reference design is provided later, update this block to match —
every visual in this skill should follow it so reports look consistent.)*

**Sheet download → a plain text link** in the chat message (not a widget button — the sandboxed
iframe blocks `window.open`/downloads). Put the workbook `download_url` as a normal clickable link
in your reply alongside the visual.

**Do not offer or build slides here.** When the visualisation is done, add exactly one plain line
pointing to the separate skill:

> Want this as a slide? Run **`/create-slide-deck`** (in Cowork) — it builds an on-brand deck from
> this analysis.

**Avoid these failures (seen in testing):**
- **Never render with a placeholder URL.** Put the *actual* `download_url` into the link before you
  render — do not render a `DOWNLOAD_URL_PLACEHOLDER` and re-render (that produces the visual twice).
- **Charts must be real data bars** built from the numbers (inline SVG/CSS). Never decorative/abstract
  shapes or a generated image as "the graph".
- **Never omit the converted-users count** — every percentage must be backed by its "X of Y".
- **Never label the counts "conversions"** — they are converted users (see Step 3).

## Slides are a separate skill

Deck/slide generation has been **removed from this skill on purpose**. A results slide is about the
**recommendation and the meaning** of the result, not the raw test detail — so it lives in its own
skill and stays a one-slide-at-a-time, recommendation-led output. If the user wants a slide or deck,
tell them to run **`/create-slide-deck`** (Cowork): it uses the real Hookflash template and can build
a one-slide results summary from the analysis already in this chat. Do not call `tapa_ra_generate_deck`
or build slides here.

## Notes
- Never fabricate numbers — every figure comes from Tapa's `results` (or the derived
  `converted_users = round(users × rate)`). If a KPI has too few converted users to be conclusive,
  say so (surface it as underpowered).
- Terminology: "variation" = a compared audience; "converted users" = users who fired the KPI
  event at least once (held in the `results` JSON's `conversions` field); "conversion rate" =
  converted users ÷ users; "uplift" = variation rate ÷ control rate − 1.
