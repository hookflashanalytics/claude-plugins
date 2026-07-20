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

- **Conversion rate** = converted users / users per variation.
- **Uplift** = variation_rate / control_rate − 1 (report as %).
- **Significance** = two-proportion z-test → p-value → confidence = 1 − p. Flag **significant**
  at the test's threshold (default 95%). Below threshold = **not significant**; very few
  converted users = **underpowered** (call it out).
- **Predicted end date** = required sample size for the target **MDE** at **power** (default 80%)
  and **alpha** (default 5%), minus users so far, divided by current daily users → days remaining.

## Out of scope

Slides/decks are a separate skill (`/create-slide-deck`) — no deck building, slide templates, or
"Generate Slides" buttons here. The in-chat visualisation spec (including the standard style
block) lives in `SKILL.md`.
