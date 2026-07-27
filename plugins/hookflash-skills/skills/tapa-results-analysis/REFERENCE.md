# Reference — Tapa Results Analysis (Cowork-only fallback depth)

## Tether tools

All are MCP tools on the Tether connector; call them as the signed-in user.

| Tool | Args | Returns |
| --- | --- | --- |
| `tapa_ra_list_ga4_accounts` | — | `{accounts:[{name,...}]}` |
| `tapa_ra_list_ga4_properties` | `account_id` | `{properties:[{displayName, property/id}]}` |
| `tapa_ra_list_ga4_audiences` | `property_id` | `{audiences:[{name, resourceName}]}` |
| `tapa_ra_list_ga4_event_names` | `property_id` | `{event_names:[...]}` |
| `tapa_ra_generate_audience_excel` | `ga4_property_id, start_date, end_date, audiences[], kpis[], report_name?` | `download_url` + `results`, or `{job_id}` |
| `tapa_ra_audience_result` | `job_id` | the workbook + `results` when finished, else status |

**KPI shape:** `{ label, event_name, condition?: { param, value, operator: exact|contains|gt|lt|regex } }`.
`audiences` needs **≥2** names (**control first** — Tapa treats the first entry as the baseline).

**Custom start:** the tool analyses from session start by default. Only pass/handle a custom
start if the user explicitly asks for one.

## What the numbers are

Tapa queries GA4 `activeUsers` filtered to each KPI event, so every KPI count is **converted
users** — users who fired the event at least once — not the number of times the event fired.
The `results` JSON's `conversions` field and this fallback's parsing both hold converted users;
always label them "converted users" in output. The workbook heads the columns **Users** and
**Converted Users**.

<a id="workbook"></a>
## Parsing the workbook (fallback when `results` is absent)

The `.xlsx` is Tapa's output; **inspect it before mapping** (layouts change):
1. Open with `openpyxl` (or pandas). Print `wb.sheetnames` and the header row of each sheet.
2. Locate, per **KPI** and per **variation** (and per **device** where present): **Users**
   and **Converted Users** (or count + rate). There is usually an "Executive Summary" sheet
   plus per-KPI detail; device splits may be columns or their own rows.
3. Build a dict like (the `conversions` keys hold converted-user counts — `stats.py` expects
   that key name):
   ```json
   {"kpis": [{"label": "Add to Cart", "variations": [
       {"name": "Original", "users": 5162, "conversions": 1859,
        "by_device": {"desktop": {"users": 3000, "conversions": 1200}, "mobile": {...}}},
       {"name": "Variation 1", "users": 5105, "conversions": 1831, "by_device": {...}}]}]}
   ```
Feed that dict to `scripts/stats.py`. If a field is missing, say so rather than infer.

## Statistics (scripts/stats.py)

### What "Confidence" means — read before reporting any number

Confidence is `1 − p` from a two-sided two-proportion test. **`p` is the probability of seeing a
gap at least this big IF the variation and control were truly identical.** So:

> **Confidence is the confidence that a gap this size is not luck.**

It is **not** the probability the variation is better, not the probability the variation wins, and
not the chance the result "is real". Those are Bayesian posterior quantities and this tool does not
compute them — asserting them is the transposed-conditional fallacy. Use the wording above verbatim
when you have to explain the number.

### The peeking caveat — state this whenever a test is still running

A confidence figure is only valid **at a sample size committed to before the test started**.
Checking repeatedly and stopping when the number crosses 95% is *optional stopping*: it inflates
the false-positive rate far above 5% (with enough looks, a null test will eventually cross).

- **Never present a mid-flight crossing of 95% as a result.** If the test has not reached its
  planned horizon, report the uplift and the confidence as a progress reading, not a verdict.
- The tool encourages repeated evaluation (scheduled re-runs, a days-to-significance countdown).
  That convenience does not make the mid-flight number a decision.

### The numbers

- **Conversion rate** = converted users / users per variation.
- **Uplift** = variation_rate / control_rate − 1 (report as %).
- **Significance** = two-proportion test → p-value → confidence = 1 − p. Flag **significant** at
  the test's threshold (default 95%) *only when the planned sample size has been reached*. Below
  threshold = **not significant**; very few converted users = **underpowered** (call it out).
  - The server uses an **unpooled** standard error (the confidence-interval form) rather than
    pooling under the null. This is a deliberate choice — it matches Optimizely's fixed-horizon
    frequentist mode and Minitab's default — and it moves the confidence figure by under
    0.02 percentage points on realistic inputs.
  - **Known inconsistency:** `scripts/stats.py` currently computes the **pooled** z-test, so this
    fallback can differ from the server in the last decimal place. Prefer the server's `results`
    object. (Reconciliation is tracked as a follow-up.)
- **Multiple comparisons — uncorrected.** One run tests every KPI × 4 device splits × every
  variation, each at α = 0.05, with **no correction applied**. Eight KPIs against one variation is
  32 tests, at which point roughly a 4-in-5 chance of at least one spurious "significant" result is
  expected under a true null. Treat one KPI at the overall level as the decision; everything else,
  and every device split, is **exploratory** — report it as a signal to investigate, never as a
  finding in its own right.
- **The formula is inherited and fixed.** Hookflash inherited this calculation from its Head of CRO
  and its continuity is a requirement — the server reports it at every count, and the workbook keeps
  the live `TDIST` formula on every row. Two changes were trialled and reverted: a count-based gate
  (a false-negative machine — it suppressed 500/10,000 vs 3/10,000, a broken variation the formula
  correctly calls at 100%) and a switch to Fisher's exact test on thin counts (defensible, but it
  moves an inherited number). See ADR-0006 decision 5.
- **Thin counts are flagged, not recalculated.** Below 10 of either outcome in either arm the formula
  reads anti-conservatively — measured over 3,570 scenarios, up to 68 pp high, with 176 cases where
  it says ≥95% and an exact test does not, and none in the reverse direction. Those comparisons carry
  `low_event_count_note`, which quotes the exact-test figure as a cross-check. Report the verdict
  *and* the caution; never substitute the cross-check for the headline figure.
- **`not_testable_reason`** is now narrow: no users in a group, or no conversions in either group.
  Report the reason; never reconstruct a figure from the counts.
- **Predicted end date.** `n = 2V(z_α+z_β)²/d²` per arm at 95% confidence / 80% power, divided by the
  daily users of the **slower arm**, minus days elapsed. Same calculation as the workbook's hidden
  `Sample Size` column. The server returns it as `time_to_significance` with an `outcome` of
  `estimate`, `estimate_too_long` or `no_difference_yet` (SKILL.md Step 3 has the wording for each).

  **Know what it is.** This is a *prospective design* formula — "how many users would a test need to
  have an 80% chance of detecting an effect of size d?" — pressed into answering a question about a
  test already running. The object that would properly answer "will THIS test be significant by day
  X" is conditional/predictive power, reporting a probability rather than a date. That rewrite is
  recorded in ADR-0006 decision 9 as the better answer and is not built. Until it is, the only honest
  reading is *"the sample a test would need for an 80% chance of resolving a gap this size"*.

  **It is not a countdown, and the difference is large.** Targeting 80% power makes the requirement
  exactly `(z_α+z_β)²/z_α² = 2.043x` the sample at which the measured gap would *first* cross 95%. In
  days *remaining* the two readings diverge by 2.4x to 6.2x, because elapsed days are subtracted from
  both. So "if the current gap holds, significant in N days" is wrong by about a factor of two and
  must never be said. The label the server returns names the basis for this reason.

  It is sized against the **observed** gap (the inherited basis). A one-standard-error haircut was
  trialled and removed: uncalibrated, and the cautious figure it produced reached the reader in 0 of
  246 measured scenarios. A 95% interval bound cannot be used instead — a not-yet-significant
  comparison always has an interval containing zero. An agreed MDE replaces the basis when supplied
  (`basis: "mde"`), but nothing requires one.

  **Two biases run in opposite directions and largely cancel**, which is why the figure is defensible
  as it stands. It targets a fixed-horizon threshold, valid only at a single pre-committed look, so
  anytime-valid inference would require materially *more*; but it is sized for 80% power rather than
  the gap's crossing point, so it already reports 2.043x *more* than the deterministic reading.
  Anytime-valid methods typically need ~1.5–2.5x the fixed-horizon crossing sample, the band this
  figure already sits in. Do not present the date as tight, and do not describe the figure as simply
  optimistic — it is conservative in one respect and optimistic in another.

### Audience mode is not a randomised experiment

`tapa_ra_generate_audience_excel` compares arbitrary GA4 audiences. When those audiences are the
variation audiences of a real A/B test, users were randomised and causal language is fair. When
they are any other audience (returning vs new, mobile vs desktop, a behavioural segment), **users
selected themselves into the groups**. The arithmetic still runs and still prints a confidence
figure, but it carries no causal meaning: the groups differ in every way that made them different
audiences, not just in the thing being compared. Report those as **descriptive comparisons** and do
not claim one audience "caused" or "drove" the difference.

## Out of scope

Slides/decks are a separate skill (`/create-results-analysis-deck`) — no deck building, slide
templates, or "Generate Slides" buttons here. The in-chat visualisation spec (including the standard style
block) lives in `SKILL.md`.
