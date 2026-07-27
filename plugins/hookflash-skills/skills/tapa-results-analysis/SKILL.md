---
name: tapa-results-analysis
description: Analyse a Hookflash A/B test end-to-end — pull GA4 results via the Tether Tapa tools, compute significance, and visualise the results in chat with the raw converted-user counts, a conversion-rate bar and a confidence-vs-threshold bar. Use when the user runs /tapa-results-analysis, pastes an experiment or ticket and asks how a test performed, or asks to analyse, report on, or read the results/significance of an A/B test. Building a slide or deck from the results is a SEPARATE skill — point the user to /create-results-analysis-deck; do not build slides here.
---

# Run Results Analysis

Turn an A/B test into (1) the Tapa results workbook and (2) an in-chat results visualisation that
**always shows the raw converted-user counts** and **how close each variation is to significance**.
**Slides are out of scope** — if the user wants a slide, they run the separate
`/create-results-analysis-deck` skill (see [Slides are a separate skill](#slides-are-a-separate-skill)).

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

### What "confidence" means, and when it counts — READ BEFORE WRITING ANY VERDICT

**Confidence is the confidence that a gap this size is not luck.** It is `1 − p`, where `p` is the
probability of seeing a gap at least this large if the variation and control were truly identical.

**Never** describe it as the probability the variation is better, the probability the variation
wins, or the chance the result "is real". Those are a different (Bayesian) quantity that this tool
does not compute. Use the phrasing in bold above when the user asks what the number means.

**A confidence figure is only a verdict at a pre-committed sample size.** Repeatedly checking a
running test and calling it as soon as it crosses 95% is *optional stopping* — it pushes the true
false-positive rate far above 5%, because a test that is genuinely doing nothing will still wander
across the threshold if you look often enough.

- **Do not present a mid-flight crossing of 95% as a result.** If the test has not reached a
  planned end point, present confidence as a progress reading and say plainly that it is not yet a
  decision.
- If the user asks "is it significant yet?" mid-test, answer with the current uplift and confidence
  **and** the caveat — do not answer with a yes.
- Scheduled re-runs of the same experiment compound this. Every extra look is another chance to
  cross by luck.

**One KPI decides; the rest are exploratory.** A single run tests every KPI × 4 device splits ×
every variation at α = 0.05 with **no multiple-comparison correction**. With 8 KPIs and one
variation that is 32 tests, where at least one spurious "significant" is more likely than not.
Lead with the KPI the test was designed to move, at the **overall** level. Report other KPIs and
every device split as exploratory signals worth investigating, never as findings.

**Audience mode is not automatically an experiment.** If the audiences being compared are the
variation audiences of a real A/B test, users were randomised and causal language is fine. If they
are any other GA4 audience (new vs returning, a behavioural segment), users **selected themselves**
into the groups — report the comparison descriptively and do not say one group "caused" or "drove"
the difference. Ask which situation applies if it is not obvious.

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

**Thin counts still get a verdict, from the same formula.** Small conversion counts never suppress
the confidence figure. A variation so broken that 3 users convert out of 10,000 against a 5% control
is overwhelmingly significant, and the formula says so — that is exactly the result a client most
needs to hear, so **never dismiss a low-count comparison as untestable.**

Those comparisons carry `low_event_count_note`, which flags the verdict as fragile and quotes an
exact-test cross-check figure. When present, report the confidence **and** the caution: one more
event either way can move it, and at these counts the formula tends to read a little high. Do not
bury the verdict, do not swap in the cross-check figure as the headline, and do not treat the note as
a reason to ignore the result.

**`not_testable_reason` is now rare** — it means there is genuinely nothing to compare (no users in
a group, or no conversions in either group). When it is set, `confidence` and `significant` are
`null` **by design**. Report the reason. **Never fill the gap yourself** — do not compute a figure
from the counts, and do not call it "not significant", which is a different statement.

**Days-to-significance projection:** each variation that is not yet significant *and is testable*
carries `time_to_significance`, whose `outcome` is one of three things. Read `outcome` first and
report accordingly — do not reach past it for a number:

| `outcome` | Fields | Say |
|---|---|---|
| `range` | `days_remaining_optimistic`, `days_remaining_cautious`, `cautious_beyond_horizon` | "roughly N–M more days"; when `cautious_beyond_horizon` is true, "roughly N+ more days, possibly longer" |
| `too_close_to_call` | `horizon_days` | "too close to call to estimate — the gap so far is within the margin of error" |
| `estimate_too_long` | `horizon_days`, `days_remaining_optimistic` | "estimated time too long to be meaningful (over N days)" — always quote `horizon_days` so the reader knows what was hit |

**Never phrase either refusal as impossibility.** Do not say the test "cannot"
reach significance, "will never" get there, or "cannot resolve in N days". Those
are claims about the experiment; these fields are facts about **our estimate**,
which is deliberately cautious — a test will often cross significance sooner than
the figures imply. If asked what it means, the honest answer is "we can't put a
useful number on it yet", not "it won't happen".

**Present it as an estimate, never a date the test will hit.** It assumes daily traffic continues,
and it is sized against the observed gap **less one standard error** — deliberately cautious,
because the observed gap is flattering at exactly the moments someone checks on a test (winner's
curse). `basis` says which effect it used (`observed_less_one_se`, or `mde` when an agreed minimum
detectable effect was supplied). Say "roughly N more days on current traffic" rather than
"significant in N days".

`too_close_to_call` and `estimate_too_long` are **useful answers, not failures** — often the most
valuable thing the tool can say. Report them plainly rather than hunting for a number to show
instead. Most in-flight tests land on one of them (measured: ~83% of projections), which is expected
— an early or low-powered test genuinely cannot be projected. **But never report a bare refusal:
always carry the condition or threshold it hit**, so it reads as an attempt rather than a shrug. (The whole field is absent on runs from before it existed — omit the line;
never derive it yourself.)

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
4. **Verdict badge** — "Significant (NN.N% conf)" / "Not significant" / **"Not testable"**.
   Use "Not testable" whenever `not_testable_reason` is set, and put the reason itself in the
   badge's footnote — never substitute "Not significant", which claims something different.
   When not significant and `time_to_significance` is present, append the projection per the
   `outcome` table in Step 3 — "Not significant — roughly N–M more days on current traffic", or
   "too close to call to estimate", or "estimated time too long to be meaningful (over N days)" —
   with a footnote
   carrying the Step 3 caveat (assumes traffic holds; sized against the observed gap less one
   standard error; an estimate, not a date).
   - **If the test is still running, the badge is a progress reading, not a decision.** Where the
     test has no agreed end point, label a crossing as "≥95% — but the test is still running"
     rather than a bare "Significant", and carry the peeking caveat from Step 3.
   - Badge the **primary KPI at the overall level** as the headline. Device splits and secondary
     KPIs get their own rows but are labelled **exploratory** — never promote the best-looking one
     to the headline.
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

> Want this as a slide? Run **`/create-results-analysis-deck`** — it fills Hookflash's PEA results
> one-pager from this analysis.

**Avoid these failures (seen in testing):**
- **Never render with a placeholder URL.** Put the *actual* `download_url` into the link before you
  render — do not render a `DOWNLOAD_URL_PLACEHOLDER` and re-render (that produces the visual twice).
- **Charts must be real data bars** built from the numbers (inline SVG/CSS). Never decorative/abstract
  shapes or a generated image as "the graph".
- **Never omit the converted-users count** — every percentage must be backed by its "X of Y".
- **Never label the counts "conversions"** — they are converted users (see Step 3).

## GA4 quota discipline (every run is expensive)

Each analysis run costs several GA4 Data API requests against a **per-property hourly quota shared
by the whole team** — batch decisions up front, don't iterate:

- **Decide the date range once** before running. Never re-run the same test across multiple
  windows to explore or "narrow down".
- **Never probe a launch date with repeated runs.** To find when a test/audience started
  collecting data, use ONE GA4 report — `date` dimension, filtered to the audience (e.g. via
  Tether's `answer_client_data_question`) — and read the first active date.
- **A zero-user audience is broken, not a date-range problem.** Do not retry other windows; tell
  the user the audience is returning no users and needs checking in GA4.

## Slides are a separate skill

Deck/slide generation has been **removed from this skill on purpose**. A results slide is about the
**recommendation and the meaning** of the result, not the raw test detail — so it lives in its own
skill and stays a one-slide-at-a-time, recommendation-led output. If the user wants a slide or deck,
tell them to run **`/create-results-analysis-deck`**: it fills Hookflash's client-facing PEA results
one-pager (Overview / Results / Learnings / Recommendations) from the analysis already in this chat.
Do not call `tapa_ra_generate_deck` or build slides here.

## Notes
- Never fabricate numbers — every figure comes from Tapa's `results` (or the derived
  `converted_users = round(users × rate)`). If a KPI has too few converted users to be conclusive,
  say so (surface it as underpowered).
- Terminology: "variation" = a compared audience; "converted users" = users who fired the KPI
  event at least once (held in the `results` JSON's `conversions` field); "conversion rate" =
  converted users ÷ users; "uplift" = variation rate ÷ control rate − 1; "confidence" = `1 − p`
  from a two-sided two-proportion test — **the confidence that a gap this size is not luck**, not
  the probability the variation is better.
- **Banned phrasings** (all assert something the tool does not compute): "NN% confident the
  variation is better", "NN% probability the variation wins", "NN% chance the result is real",
  "NN% sure it works". Say "NN% confidence that a gap this size is not luck" instead.
