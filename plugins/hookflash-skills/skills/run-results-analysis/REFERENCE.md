# Reference — Hookflash Results Analysis

## Tether tools (staging)

All are MCP tools on the Tether connector; call them as the signed-in user.

| Tool | Args | Returns |
| --- | --- | --- |
| `tapa_ra_list_ga4_accounts` | — | `{accounts:[{name,...}]}` |
| `tapa_ra_list_ga4_properties` | `account_id` | `{properties:[{displayName, property/id}]}` |
| `tapa_ra_list_ga4_audiences` | `property_id` | `{audiences:[{name, resourceName}]}` |
| `tapa_ra_list_ga4_event_names` | `property_id` | `{event_names:[...]}` |
| `tapa_ra_generate_audience_excel` | `ga4_property_id, start_date, end_date, audiences[], kpis[], report_name?` | `download_url` + resource, or `{job_id}` |
| `tapa_ra_audience_result` | `job_id` | the workbook when finished, else status |
| `get_slide_template` | `template:"results_analysis"` | template metadata + signed `download_url` |

**KPI shape:** `{ label, event_name, condition?: { param, value, operator: exact|contains|gt|lt|regex } }`.
`audiences` needs **≥2** names (control first if known).

**Custom start:** the tool analyses from session start by default. Only pass/handle a custom
start if the user explicitly asks for one.

<a id="workbook"></a>
## Parsing the workbook

The `.xlsx` is Tapa's output; **inspect it before mapping** (layouts change):
1. Open with `openpyxl` (or pandas). Print `wb.sheetnames` and the header row of each sheet.
2. Locate, per **KPI** and per **variation** (and per **device** where present): **users/sessions**
   and **conversions** (or conversion count + rate). There is usually an "Executive Summary" sheet
   plus per-KPI detail; device splits may be columns or their own rows.
3. Build a dict like:
   ```json
   {"kpis": [{"label": "Add to Cart", "variations": [
       {"name": "Original", "users": 5162, "conversions": 1859,
        "by_device": {"desktop": {"users": 3000, "conversions": 1200}, "mobile": {...}}},
       {"name": "Variation 1", "users": 5105, "conversions": 1831, "by_device": {...}}]}]}
   ```
Feed that dict to `stats.py` and `build_deck.py`. If a field is missing, say so rather than infer.

## Statistics (scripts/stats.py)

- **Conversion rate** = conversions / users per variation.
- **Uplift** = variation_rate / control_rate − 1 (report as %).
- **Significance** = two-proportion z-test → p-value → confidence = 1 − p. Flag **significant**
  at the test's threshold (default 95%). Below threshold = **not significant**; very low
  conversions = **underpowered** (call it out).
- **Predicted end date** = required sample size for the target **MDE** at **power** (default 80%)
  and **alpha** (default 5%), minus users so far, divided by current daily users → days remaining.

<a id="viz"></a>
## In-chat visualisation

Render a self-contained artifact/widget (no external CDNs — inline SVG/CSS). Include:
- A header line: property, date range, audiences, primary KPI.
- Per KPI: a **table** (variation | users | conversions | conv. rate | uplift | confidence),
  a **conversion-rate bar chart** by variation, and a **significant / not significant** badge.
- A **"Generate Slides"** button:
  ```html
  <button onclick="(window.sendPrompt
      ? window.sendPrompt('Generate the results-analysis slide deck for ' + EXPERIMENT)
      : alert('Reply: generate slides'))">Generate Slides</button>
  ```
  `sendPrompt` exists in Cowork / Claude Code widgets; the fallback covers plain chat.
- Do **not** trigger slide generation automatically — the button/reply is the gate.

`scripts/viz_template.html` is a starting point; adapt it to the real numbers.

## Slide population (scripts/build_deck.py)

Template = the hosted `results_analysis` deck (16:9, Aptos, 34 layouts; seed slides
`Traffic`, `Insight`, `Test summary`). Do not rebuild the theme — add slides from its layouts.

**Per KPI**, add:
1. A **results table** (same columns as the viz table).
2. An **overall conversion-rate bar chart** (one bar per variation).
3. A **device-split chart** (grouped bars: variation × device, conversion rate).

Fill the `Test summary` seed slide's placeholders (test name, hypothesis IF/THEN/BECAUSE, test
type, pages, audience, primary metric) from the ticket/inputs. `build_deck.py` documents the
layout indices it assumes — verify against the real template on first run and adjust.
