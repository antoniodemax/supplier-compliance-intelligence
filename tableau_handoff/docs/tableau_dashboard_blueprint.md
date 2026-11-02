# Tableau Dashboard Blueprint

**Project:** Supplier Compliance Intelligence
- **Primary stakeholder:** Director of Supply Chain Compliance
- **Central question:** *Which suppliers and compliance information gaps should we prioritise for follow-up?*
- **Reporting cutoff:** 30 September 2026
- **Status:** Phase 2 blueprint only. No Tableau workbook has been built.

This blueprint turns the validated Phase 1 analysis into three connected dashboards and a short presentation narrative. It is grounded in the local, read-only Excel workbook, the validated CSV exports, the [data validation and KPI reconciliation](data_validation_and_kpi_reconciliation.md), the [Tableau handoff](tableau_handoff.md), and the [sensitivity analysis report](../reports/sensitivity_analysis_report.md). Keep the source workbook unchanged.

## 1. Verified evidence and wording

The workbook contains simulated educational data. The following values were recalculated from its tables and match the supplied KPI reference:

| Measure | Verified value | Grain and definition |
|---|---:|---|
| Active suppliers | 800 | Supplier; all 800 have `Supplier_Status = Active` |
| Eligible requests | 2,139 | Request; each row in `Compliance_Requests` is eligible |
| Submitted requests | 1,527 | Request; `Submitted_Flag = 1` |
| Request response rate | 71.4% | 1,527 submitted / 2,139 eligible requests |
| Complete requests | 1,193 | Request; `Complete_Flag = 1` |
| Request completion rate | 55.8% | 1,193 complete / 2,139 eligible requests |
| Supplier response rate | 92.3% | 738 of 800 suppliers submitted at least one request |
| Overdue backlog | 946 | Request; `Overdue_Days > 0` at the cutoff |
| High-risk suppliers | 181 | Supplier; original `Risk_Category = High` |
| PFAS completion rate | 44.7% | 240 complete / 537 PFAS requests |
| Asia-Pacific PFAS incomplete backlog | 107 | Request; region Asia-Pacific, module PFAS, not complete |
| Incomplete requests associated with High-risk suppliers | 314 | Request; 33.2% of 946 incomplete requests and 14.7% of 2,139 eligible requests |

**Response is not completion.** A submission means that something was returned; it can be incomplete or a decline. A complete declaration is not the same as a confirmed compliant supplier. The workbook's `Compliant` outcome is a supplier self-declaration and is not independently verified.

The 946 overdue requests include 334 requests with a submission (281 Incomplete and 53 Declined) and 612 without a submission. Do not label all 946 as unanswered. Use “overdue requests” or “non-complete requests past due,” and show response status separately.

### Risk-score explanation

The workbook's score is an **illustrative management prioritisation model**, not a probability of non-compliance or a legal/regulatory rating:

```text
Overall Risk Score =
    0.35 × Criticality Score
  + 0.30 × Information Gap Score
  + 0.20 × Overdue Severity Score
  + 0.15 × Business Exposure Score
```

The four 0–100 components are:

1. **Criticality:** High / Medium / Low supplier criticality maps to 100 / 60 / 20.
2. **Information gap:** 100 × non-complete eligible requests / eligible requests.
3. **Overdue severity:** minimum of 100 and (maximum overdue days / 120 × 100).
4. **Business exposure:** minimum of 100 and (active parts / 850 × 100).

Approved categories are High ≥ 70, Medium ≥ 40 and < 70, and Low < 40. Reuse the validated `Overall_Risk_Score` and `Risk_Category` from `Risk_Assessment` in Tableau; do not rebuild or silently change their definitions.

The approved sensitivity scenarios hold the component values fixed and change only weights:

| Scenario | Criticality | Information gap | Overdue severity | Business exposure | High suppliers |
|---|---:|---:|---:|---:|---:|
| Original | 35% | 30% | 20% | 15% | 181 |
| Criticality emphasis | 50% | 15% | 20% | 15% | 148 |
| Information-gap emphasis | 25% | 40% | 20% | 15% | 151 |

Using a fixed top-181 ranked cohort for comparison, 164 suppliers remain in that cohort under Criticality Emphasis (17 entrants and 17 exits) and 165 under Information-Gap Emphasis (16 entrants and 16 exits). This is a different concept from each scenario's High category count. State the scenario name and whether a view shows a category or a fixed-size ranked cohort.

## 2. Stakeholder journey and dashboard specifications

Build the dashboards in this sequence: **Executive Overview → Compliance Gaps → Supplier Prioritisation**. Each page should answer one question and provide a clear next step. Use a consistent title bar, cutoff date, simulated-data note, navigation, and definitions.

### A. Executive Overview

**Purpose / question:** How large is the information gap, how is it distributed across suppliers and requests, and what should the stakeholder investigate next?

**KPI cards:** 800 active suppliers; 2,139 eligible requests; 71.4% request response rate; 55.8% request completion rate; 181 High-risk suppliers; 946 overdue requests. Define response and completion in card subtitles or tooltips.

**Worksheet inventory and layout**

| Worksheet | Chart specification | Fields and encodings |
|---|---|---|
| `Overview - KPI Cards` | Six compact text KPI sheets across the top. | Each card uses its measure below; show value, plain-language label, and denominator/definition in a tooltip or subtitle. |
| `Overview - Request Status by Module` | Horizontal stacked bars, one per module. | Rows: `Compliance_Module`; columns: distinct requests; color: `Response_Status`; label segment counts. Use the same status order on every dashboard. Tooltip may include average response time: 55.1 days from campaign start, about 10 days after the 45-day due date—not “55 days late.” |
| `Overview - Supplier Risk by Region` | Stacked bars by region. | Rows: `Region`; columns: distinct suppliers; color: original `Risk_Category`. Count suppliers, not request rows. |
| `Overview - Scenario Category Counts` | Grouped bars by scenario and risk category, using the validated scenario-category export. | Scenario on columns; supplier count on rows; category on color. Add a caption that the chart covers all 800 suppliers and is not changed by request filters. |
| `Overview - Definitions and Caveats` | Small text panel. | Explain response vs completion, cutoff date, simulated data, and illustrative risk score. Include a button/link to Compliance Gaps. |

**Filters:** Region, Compliance Module, Supplier Criticality, and Risk Category. Keep the six verified KPI cards as all-data baseline values and apply filters to the charts only. If a later version makes a card filter-responsive, relabel it as a selected-cohort metric and show its denominator. Scope Risk Category and Response Status filters to charts/details.

**Actions:** Selecting a region or module can filter relevant charts on this dashboard. A Navigation object takes the user to the next dashboard. Repeat key filters on each dashboard and apply each filter to the appropriate worksheets using the same data source; do not rely on a filter action to carry state between dashboard tabs.

**Expected takeaway:** Completion is lower than submission; the stakeholder can see the gap between the two and identify which region/module patterns warrant a closer look. The scenario view shows that a priority list depends partly on management-selected weights.

### B. Compliance Gaps

**Purpose / question:** Which compliance modules and regions have the largest outstanding information gaps, and what kind of response is missing?

**KPI cards:** 946 overdue requests; 44.7% PFAS completion; 107 incomplete Asia-Pacific PFAS requests; 314 incomplete requests associated with High-risk suppliers (33.2% of incomplete requests; 14.7% of all eligible requests).

**Worksheet inventory and layout**

| Worksheet | Chart specification | Fields and encodings |
|---|---|---|
| `Gaps - KPI Cards` | Four text KPI sheets across the top. | Use distinct request counts and the definitions in Section 4. Show the two denominators beside the High-risk incomplete measure. |
| `Gaps - Status by Module` | Horizontal stacked bars. | `Compliance_Module` by distinct `Request_ID`; color by `Response_Status`; label counts. |
| `Gaps - Region Module Heatmap` | Heatmap of incomplete-request counts. | Rows: `Region`; columns: `Compliance_Module`; color and label: distinct incomplete requests. Tooltip: eligible requests, incomplete requests, and completion rate for that region/module cell. Counts show workload; rates provide context where denominators differ. |
| `Gaps - Completion Rate by Module` | Horizontal bars on a fixed 0–100% axis. | Module by request completion rate; label percentage and numerator/denominator. Do not add a target line unless the stakeholder supplies an approved target. |
| `Gaps - Overdue Age by Module` | Stacked bars by overdue-age band, only for overdue requests. | Module by distinct request count; color: `Overdue Age Band`; tooltip: maximum and median overdue days. Age bands are descriptive, not policy thresholds. |
| `Gaps - Request Detail` | A request table for a selected region/module/status. | Request ID, supplier, module, response status, due date, submitted flag, complete flag, overdue days. Do not include raw engagement-event rows in this table. |

**Filters:** Region, Compliance Module, Supplier Criticality, Risk Category, Response Status, and (where useful) Campaign/Due Date. Keep the four verified KPI cards as all-data baseline values and apply filters to the charts/details only. If cards are made responsive, label the selected region/module cohort and show both denominators; exclude Risk Category and Response Status from those cards unless they are explicitly cohort-scoped.

**Actions:** A heatmap cell or module bar filters the request detail table and other gap charts on this dashboard. A Navigation object takes the user to Supplier Prioritisation. Do not make a status selection appear to change an all-request KPI without explaining that the denominator has changed.

**Expected takeaway:** The supplied data shows a PFAS completion rate of 44.7% and 107 incomplete PFAS requests for Asia-Pacific. These are counts of information gaps, not evidence that suppliers violated a regulation.

### C. Supplier Prioritisation

**Purpose / question:** Which suppliers should the compliance team review first, and what recorded factors are driving their illustrative scores?

**KPI cards:** 181 suppliers in the original High category; 314 incomplete requests associated with those suppliers; 33.2% of all incomplete requests; 14.7% of eligible requests. Keep supplier-grain and request-grain counts visibly distinct.

**Worksheet inventory and layout**

| Worksheet | Chart specification | Fields and encodings |
|---|---|---|
| `Priority - Supplier Worklist` | Searchable, sortable table, initially sorted by original score descending. | Supplier ID/name, region, industry, supplier criticality, original category, overall score, information-gap count, maximum overdue days. Show all 800 when no filters are set; offer a High-only view through the category filter. |
| `Priority - Risk vs Information Gap` | Scatterplot, one mark per supplier. | X: `Information_Gap_Score`; Y: `Overall_Risk_Score`; color: `Risk_Category`; size: `Maximum_Overdue_Days` (use a restrained size range). Tooltip: supplier ID/name, region, criticality, four component scores, category and score. Label only selected/top suppliers to avoid overlap. |
| `Priority - Component Profile` | Supplier-level highlight table or four aligned bars for the selected supplier. | Show Criticality, Information Gap, Overdue Severity, and Business Exposure component scores on the same 0–100 scale. Keep component values distinct from their weighted contributions. |
| `Priority - Supplier Requests` | Detail list filtered by the selected supplier. | Request ID, module, response status, due date, submitted/complete flags, overdue days. If follow-up information is displayed, aggregate to request (for example `COUNTD(Engagement_ID)`) or place event details in a separate sheet. |
| `Priority - Scenario Movement` | Optional supplier-level table from `supplier_scenario_comparison.csv`. | Supplier ID, each approved scenario's score/category/rank, and rank changes. Use as a separate source/sheet; negative rank change means movement upward (closer to rank 1). Do not merge this table into request counts. |

**Filters:** Region, Supplier Criticality, Risk Category, Industry Category, Compliance Module, and Response Status. Keep the four verified KPI cards as all-data baseline values and apply filters to the worklist, scatterplot, and detail sheets. Apply module/status filters to request-detail sheets only unless a view is explicitly defined as a request-filtered supplier cohort. Do not imply that filtering request rows recalculates the validated all-request risk score.

**Actions:** Selecting a supplier in the worklist or scatterplot filters the component profile and request-detail sheet by Supplier ID. Provide a clear “clear selection” instruction. Keep the full supplier worklist searchable and sorted by score; a High category is a decision-support signal, not an automatic compliance finding.

**Expected takeaway:** The Director can move from a supplier-level prioritisation signal to the component scores and request records behind it, then assign follow-up. The score helps organise review; it does not prove non-compliance.

## 3. Tableau data model and source preparation

### Primary source: the local Excel workbook

Connect with **Microsoft Excel** to `data/Supplier_Compliance_Intelligence.xlsx`. Use only these four analytical sheets; reference sheets (`START HERE`, `KPI_Summary`, `Risk_Weights`, and `Data_Dictionary`) are documentation/reference, not fact tables for dashboard counts.

| Sheet | Verified records × fields | Grain / key | Actual columns and source types (as read) |
|---|---:|---|---|
| `Supplier_Master` | 800 × 7 | One row per supplier; unique `Supplier_ID` | `Supplier_ID` (text), `Supplier_Name` (text), `Region` (text), `Industry_Category` (text), `Supplier_Criticality` (text), `Active_Part_Count` (integer), `Supplier_Status` (text) |
| `Compliance_Requests` | 2,139 × 11 | One row per request; unique `Request_ID` | `Request_ID` (text), `Supplier_ID` (text), `Compliance_Module` (text), `Campaign_Date` (text date), `Due_Date` (text date), `Submission_Date` (text date; 612 missing), `Response_Status` (text), `Compliance_Outcome` (text), `Overdue_Days` (integer), `Submitted_Flag` (integer 0/1), `Complete_Flag` (integer 0/1) |
| `Supplier_Engagement` | 1,499 × 7 | One row per follow-up event; unique `Engagement_ID` | `Engagement_ID` (text), `Request_ID` (text), `Supplier_ID` (text), `Follow_Up_Date` (text date), `Follow_Up_Channel` (text), `Engagement_Outcome` (text), `Assigned_Team` (text) |
| `Risk_Assessment` | 800 × 11 | One row per supplier at the cutoff; unique `Supplier_ID` | `Supplier_ID` (text), `Assessment_Date` (text date), `Criticality_Score` (integer), `Information_Gap_Score` (decimal), `Overdue_Severity_Score` (decimal), `Business_Exposure_Score` (decimal), `Overall_Risk_Score` (decimal), `Risk_Category` (text), `Eligible_Request_Count` (integer), `Information_Gap_Count` (integer), `Maximum_Overdue_Days` (integer) |

Other sheets are reference material, not analytical fact tables: `START HERE` (11 × 2), `KPI_Summary` (11 × 2), `Risk_Weights` (4 × 3), and `Data_Dictionary` (36 × 3). The four analytical sheets contain no duplicate rows; their expected keys are non-null and unique. Dates are text in Excel and should be converted to Date in Tableau.

In Tableau's **logical layer**, start with `Compliance_Requests` and relate the other tables. Do not double-click into the physical layer to make joins.

```text
Supplier_Master (1) ── Supplier_ID ── (many) Compliance_Requests
        │                                      │
        │                                      └── Request_ID ── (many) Supplier_Engagement
        └── Supplier_ID ── (1) Risk_Assessment
```

| Relationship | Cardinality | Match setting |
|---|---|---|
| Supplier Master ↔ Compliance Requests on `Supplier_ID` | One to many | All records match |
| Supplier Master ↔ Risk Assessment on `Supplier_ID` | One to one | All records match |
| Compliance Requests ↔ Supplier Engagement on `Request_ID` | One to many | Some records match; 1,149 requests have no follow-up |

There are no orphan supplier/request references in the validated workbook. A request can have multiple follow-up events. A physical request-to-engagement join yields 2,648 rows rather than 2,139, which can inflate counts and sums. Use Tableau logical relationships and request-level `COUNTD` fields. Avoid engagement-event dimensions in sheets calculating request KPIs. When follow-up detail is needed, use distinct request/engagement counts and validate the worksheet grain.

### Types to set in Tableau

- Keep all IDs as **String** dimensions, not numbers.
- Set `Campaign_Date`, `Due_Date`, `Submission_Date`, `Follow_Up_Date`, and `Assessment_Date` to **Date**. They are stored as text in the source and use `YYYY-MM-DD`.
- Treat `Submitted_Flag` and `Complete_Flag` as numeric measures containing 0/1.
- Keep `Overdue_Days`, `Active_Part_Count`, risk scores, counts, and rankings numeric. Use `Risk_Category`, module, region, status, channel, outcome, and criticality as dimensions.
- Do not alter source cells or save Tableau type changes back into the original workbook.

### Validated supplementary CSVs

Do not edit these exports. Use them as separate Tableau sources when a scenario view is needed:

| CSV | Verified schema / grain | Recommended use |
|---|---|---|
| `reports/scenario_category_comparison.csv` | 3 category rows × 4 fields: `Category`, `Original`, `Criticality_Emphasis`, `Info_Gap_Emphasis` | Scenario category-count chart. In Tableau, pivot the three scenario count columns into `Scenario` and `Supplier Count`; if pivot is unavailable, use Measure Names/Measure Values. |
| `reports/supplier_scenario_comparison.csv` | 800 unique suppliers × 18 fields: `Supplier_ID`, `Overall_Risk_Score`, `Risk_Category`, `Criticality_Score`, `Information_Gap_Score`, `Overdue_Severity_Score`, `Business_Exposure_Score`, `Risk_Score_Original`, `Risk_Category_Original`, `Rank_Original`, `Risk_Score_Criticality_Emphasis`, `Risk_Category_Criticality_Emphasis`, `Rank_Criticality_Emphasis`, `Risk_Score_Info_Gap_Emphasis`, `Risk_Category_Info_Gap_Emphasis`, `Rank_Info_Gap_Emphasis`, `Rank_Change_Criticality_Emphasis`, `Rank_Change_Info_Gap_Emphasis` | Optional supplier-level score/category/rank movement sheet. This does not contain supplier name, region, or module. |
| `reports/supplier_priority_tiers.csv` | 800 unique suppliers × 7 fields: `Supplier_ID`, `Overall_Risk_Score`, `Risk_Category`, `Supplier_Criticality`, `Information_Gap_Count`, `Maximum_Overdue_Days`, `Priority_Tier` | Optional operational tier view. `Priority_Tier` is a separate illustrative workflow heuristic; do not substitute it for High/Medium/Low risk category. |

For the beginner-safe build, keep scenario exports separate from the primary Excel logical model. The scenario chart is an all-supplier sensitivity view and does not respond to the core request filters. If a later Tableau version supports a cross-connection **logical relationship** to supplier master, it may be added on `Supplier_ID` for a supplier-level drill-down; validate one row per supplier and the 800-supplier totals first. Never physically join a scenario CSV to request or engagement rows. If using separate data sources, treat filter actions between them as optional and test them in Tableau rather than assuming they propagate.

No preparation of the validated source data is required. Tableau-only work is limited to setting date types, creating calculated fields, and optionally pivoting the scenario summary for display.

## 4. Calculated fields

Create these in the primary Excel data source. Tableau may append a table name to repeated names (for example, `[Supplier_ID (Supplier_Master)]`); select the corresponding field from the Data pane. The formulas below use descriptive field names for readability. Use `COUNTD` for IDs, especially where a view could involve related tables.

### Request-level metrics

```tableau
// Eligible Requests
COUNTD([Request_ID])

// Submitted Requests
COUNTD(IF [Submitted_Flag] = 1 THEN [Request_ID] END)

// Request Response Rate
IF [Eligible Requests] = 0 THEN NULL
ELSE [Submitted Requests] / [Eligible Requests]
END

// Complete Requests
COUNTD(IF [Complete_Flag] = 1 THEN [Request_ID] END)

// Request Completion Rate
IF [Eligible Requests] = 0 THEN NULL
ELSE [Complete Requests] / [Eligible Requests]
END

// Incomplete Requests
COUNTD(IF [Complete_Flag] = 0 THEN [Request_ID] END)

// Overdue Backlog
COUNTD(IF [Overdue_Days] > 0 THEN [Request_ID] END)

// Response Days
IF [Submitted_Flag] = 1 THEN DATEDIFF('day', [Campaign_Date], [Submission_Date]) END

// Average Response Time
AVG([Response Days])
```

### Supplier-level and cross-table measures

```tableau
// Active Suppliers
COUNTD(
  IF [Supplier_Status] = "Active"
  THEN [Supplier_ID (Supplier_Master)]
  END
)

// Suppliers With At Least One Submission
COUNTD(
  IF [Submitted_Flag] = 1
  THEN [Supplier_ID (Compliance_Requests)]
  END
)

// Suppliers With At Least One Eligible Request in Current Filter Scope
COUNTD([Supplier_ID (Compliance_Requests)])

// Supplier Response Rate
IF [Suppliers With At Least One Eligible Request in Current Filter Scope] = 0 THEN NULL
ELSE [Suppliers With At Least One Submission]
     / [Suppliers With At Least One Eligible Request in Current Filter Scope]
END

// High-Risk Suppliers (original category)
COUNTD(
  IF [Risk_Category (Risk_Assessment)] = "High"
  THEN [Supplier_ID (Risk_Assessment)]
  END
)

// High-Risk Incomplete Requests
COUNTD(
  IF [Complete_Flag] = 0
     AND [Risk_Category (Risk_Assessment)] = "High"
  THEN [Request_ID]
  END
)

// High-Risk Share of Incomplete Requests
IF [Incomplete Requests] = 0 THEN NULL
ELSE [High-Risk Incomplete Requests] / [Incomplete Requests]
END

// High-Risk Incomplete Share of Eligible Requests
IF [Eligible Requests] = 0 THEN NULL
ELSE [High-Risk Incomplete Requests] / [Eligible Requests]
END
```

The Supplier Response Rate calculation counts a supplier once, even if multiple requests were submitted. In the unfiltered data, all 800 suppliers have at least one eligible request, so the denominator equals the active-supplier count. With a module filter, it becomes the response rate among suppliers with a request for that selected module; label that scope clearly. Do not apply a `Response_Status` or `Risk_Category` filter to the headline rate cards unless the intended denominator is explicitly a filtered cohort.

### Module and regional gap measures

```tableau
// PFAS Requests
COUNTD(IF [Compliance_Module] = "PFAS" THEN [Request_ID] END)

// PFAS Complete Requests
COUNTD(
  IF [Compliance_Module] = "PFAS" AND [Complete_Flag] = 1
  THEN [Request_ID]
  END
)

// PFAS Completion Rate
IF [PFAS Requests] = 0 THEN NULL
ELSE [PFAS Complete Requests] / [PFAS Requests]
END

// APAC PFAS Incomplete Requests
COUNTD(
  IF [Region (Supplier_Master)] = "Asia-Pacific"
     AND [Compliance_Module] = "PFAS"
     AND [Complete_Flag] = 0
  THEN [Request_ID]
  END
)
```

### Display helpers

```tableau
// Request Stage
CASE [Response_Status]
  WHEN "Complete"   THEN "4. Complete"
  WHEN "Incomplete" THEN "3. Submitted - incomplete"
  WHEN "Declined"   THEN "2. Declined"
  WHEN "Pending"    THEN "1. Pending"
END

// Overdue Age Band
IF [Overdue_Days] = 0 THEN "Not overdue"
ELSEIF [Overdue_Days] <= 30 THEN "1-30 days"
ELSEIF [Overdue_Days] <= 60 THEN "31-60 days"
ELSEIF [Overdue_Days] <= 90 THEN "61-90 days"
ELSE "Over 90 days"
END
```

`Risk_Category`, `Overall_Risk_Score`, the four score components, `Information_Gap_Count`, and `Maximum_Overdue_Days` should be reused from `Risk_Assessment`. Do not replace them with a second implementation for dashboard display. For the scenario sheets, reuse scenario columns in the validated exports; the exact weights are documented in Section 1.

## 5. Layout, filters, interaction, and accessibility

- Use a consistent desktop canvas (for example, 1280 × 800 pixels) with a 10–12% title/navigation area, a compact KPI row, two or three main views, and a narrow definition/footer area. Fit the layout to the actual presentation screen before finalising.
- Put navigation buttons for all three dashboards in the same position. Use clear names: **Executive Overview**, **Compliance Gaps**, and **Supplier Prioritisation**.
- Treat the cited KPI cards as all-data baseline values: exclude them from dashboard filters using **Apply to Worksheets → Selected Worksheets**. Apply filters to charts/details and validate their row grain. If cards become filter-responsive, update the label, show the selected cohort and denominator, and recheck the calculation. Scope module/status filters to request sheets and region/criticality/category filters to relevant supplier/request views.
- Use a dashboard filter action (“Use as Filter”) for selecting a region/module or supplier within the current dashboard. Include a visible reset/clear-selection affordance. Use tooltips for explanation, not for information that is essential to reading the chart.
- Keep original risk category colours consistent: **Low blue `#0072B2`**, **Medium amber `#E69F00`**, **High vermilion `#D55E00`**. Always show the category name in labels/legends; never rely on colour alone. Use a separate, consistent palette for response statuses so “Incomplete” is not confused with “High.”
- Format request/supplier counts as whole numbers with thousands separators; percentages to one decimal place; average response days to one decimal; scores to one decimal; overdue days as whole days. Show numerator/denominator in tooltips for rates.
- Use readable titles (18–24 pt), labels (at least 12 pt where practical), strong contrast, restrained gridlines, descriptive worksheet/dashboard titles, and colour-blind-friendly distinctions. Avoid dense labels on 800-point plots; label the table and selected marks instead.
- Put “Simulated educational data — not real supplier records” and “As of 30 September 2026” on each dashboard. Note that Tableau Public content is public; confirm assignment/publication rules before publishing.

## 6. Beginner build and validation sequence

1. **Create a new Tableau workbook** and connect to the local Excel file. Do not edit or replace the source workbook.
2. **Build the logical model** in Section 3. Confirm relationship fields/cardinality and stay in the logical layer.
3. **Set data types** for IDs, dates, numeric measures, and categorical dimensions.
4. **Create the calculated fields** in Section 4. Keep each calculation in the data source that owns its fields.
5. **Build a temporary KPI-check sheet** before styling dashboards. Confirm: 800 suppliers; 2,139 eligible requests; 1,527 submitted; 1,193 complete; 71.4% request response; 55.8% request completion; 92.3% supplier response; 946 overdue; 181 High-risk suppliers; 990 distinct requests with follow-up; 55.1 average response days.
6. **Create the worksheet inventory** in Section 2. First build the views with simple titles and tooltips; add labels and formatting after their counts validate.
7. **Connect the scenario-category CSV separately** for the sensitivity chart. Pivot its three scenario count columns if supported. Check the High/Medium/Low counts against the verified table (Original 181/366/253; Criticality 148/371/281; Information-Gap 151/381/268).
8. **Assemble the three dashboards** in stakeholder order. Add navigation, filters, actions, subtitles, definitions, and the simulated-data footer.
9. **Test filter behavior and row grain.** In particular, verify that a filter does not change a headline denominator unexpectedly, that a supplier is counted once in supplier views, and that request counts remain distinct when supplier/risk fields are used.
10. **Review with the presenter.** They should be able to explain each KPI numerator/denominator, the difference between response and completion, and why the risk score is not a compliance determination before the Tableau workbook is considered ready.

Do not publish as part of this blueprint task. Actual workbook construction, interaction testing, publishing, and presentation slide production are later project work.

## 7. Presentation narrative and talking points

### Opening

> “This dashboard helps the Supply Chain Compliance team decide where to follow up on missing supplier declarations. It separates whether a supplier sent a response from whether that response was complete, and it uses an illustrative score to organise review—not to declare legal compliance.”

### Dashboard talking points

1. **Executive Overview:** “The dataset covers 800 active suppliers and 2,139 eligible requests. Suppliers submitted 1,527 requests, a 71.4% request response rate, but only 1,193 were complete, a 55.8% completion rate. The difference is why submitted responses and completed declarations must be shown separately. There are 946 requests past due at the cutoff.”
2. **Compliance Gaps:** “The gaps are not evenly represented by one headline. PFAS completion is 44.7%, and the Asia-Pacific PFAS incomplete worklist has 107 requests. The 314 incomplete requests associated with High-risk suppliers account for 33.2% of all incomplete requests and 14.7% of all eligible requests. These are workload and information-gap measures, not proof of regulatory violations.”
3. **Supplier Prioritisation:** “The original model assigns 181 suppliers to High. It combines criticality, information gaps, overdue severity, and business exposure. When the approved weights change, the High count changes to 148 or 151, and only 164 or 165 of the original top-181 ranked suppliers remain. This shows that weights affect prioritisation; management should review the underlying evidence and capacity before assigning interventions.”

### Risk methodology in plain language

> “Each supplier has four component scores on a 0-to-100 scale. The original model gives 35% weight to criticality, 30% to information gaps, 20% to overdue severity, and 15% to business exposure. The weighted result is placed into High, Medium, or Low bands. The alternate scenarios change the emphasis to test how the list moves. The model is a transparent triage aid based on this simulated dataset; it is not a probability, legal opinion, or independently validated compliance rating.”

### Proposed intervention (recommendation, not a historical result)

- **Owner:** Director of Supply Chain Compliance as sponsor; regional compliance leads own case assignment; supplier-compliance coordinators conduct and record follow-up.
- **Timeframe:** 30-day pilot, with an initial five-day validation and ownership step.
- **Scope:** Start with the 314 incomplete requests associated with suppliers in the original High category. Separately track the 107 Asia-Pacific PFAS incomplete requests; verify overlap before combining worklists.
- **Proposed success measures:** assign an owner and record a disposition for all 314 cases; obtain at least 32 newly complete declarations (approximately 10% of that starting worklist) by day 30. Report completion and contact outcomes separately. These are proposed pilot targets for stakeholder approval, not observed results or a promised causal effect.
- **Expected operational impact:** a visible, assigned queue; transparent case status; and a measured change in complete declarations, allowing the team to adjust outreach based on recorded outcomes.

### Conclusion

> “Use the dashboards to move from the overall information gap, to the modules and regions where it is visible, to a supplier worklist with its supporting records. Confirm declarations and context with the responsible teams before acting. Revisit the priorities as evidence changes, and treat the score as a starting point for management review.”

### Assumptions and limitations to state

- The workbook is simulated educational data, not a sample of real supplier performance.
- “Eligible request” means every row in `Compliance_Requests`; no separate eligibility flag exists.
- A supplier is counted as responded if at least one request has `Submitted_Flag = 1`, including incomplete and submitted-decline records.
- `Compliant` is a self-declared outcome and is not independently verified.
- The risk components, weights, category thresholds, and top-181 comparison cohort are management choices; sensitivity movements demonstrate their effect, not a uniquely correct ranking.
- Overdue days are measured relative to 30 September 2026; the analysis is not live.
- The aggregate figures do not establish why a request is incomplete, whether a follow-up caused a response, or whether any supplier is legally non-compliant.
- The 30-day intervention and its numeric targets are proposed and should be confirmed by the stakeholder.

## 8. Three-slide PowerPoint outline

These are content specifications only. Do not create final slides or use dashboard screenshots until the Tableau workbook exists and its figures and visuals have been checked.

### Slide 1 — The supplier information gap

- **Main message:** Submission is not completion; the team has a substantial outstanding declaration workload.
- **Supporting evidence:** 800 active suppliers; 2,139 eligible requests; 71.4% request response; 55.8% request completion; 946 overdue requests.
- **Recommended visual:** A simple request funnel or 100% status bar showing Complete, Incomplete, Declined, and Pending. Use request counts and percentages with an explicit denominator of 2,139.
- **Speaker notes:** “A response can still be incomplete or declined. Completion means a complete declaration was received; it does not mean compliance was independently confirmed. The overdue count is requests past due at the 30 September cutoff, not just requests with no response.”

### Slide 2 — Where gaps are concentrated

- **Main message:** The gap varies by module and region, so follow-up should be directed rather than generic.
- **Supporting evidence:** PFAS completion is 44.7% (240/537); Asia-Pacific has 107 incomplete PFAS requests; 314 incomplete requests associated with High-risk suppliers represent 33.2% of incomplete requests and 14.7% of eligible requests.
- **Recommended visual:** Region-by-module heatmap of incomplete counts with completion-rate tooltips, plus a clearly labelled PFAS completion callout. Show denominator context.
- **Speaker notes:** “The PFAS and Asia-Pacific figures describe different slices. Do not assume the 107 requests are all part of the 314 High-risk-supplier requests; check overlap in the dashboard before combining operational queues. These counts indicate missing information, not confirmed non-compliance.”

### Slide 3 — Prioritise review and measure action

- **Main message:** Use the score to organise a review queue, then verify each case and measure follow-up outcomes.
- **Supporting evidence:** 181 suppliers are High under the original weights; the High count is 148 under Criticality Emphasis and 151 under Information-Gap Emphasis; 164 and 165 of the original top-181 ranked suppliers remain in those scenarios. Proposed pilot: assign all 314 High-risk-associated incomplete requests and target at least 32 newly complete by day 30.
- **Recommended visual:** Supplier worklist excerpt (built from the final verified dashboard, not a mock screenshot) alongside a compact scenario comparison and a proposed 30-day action/metric box.
- **Speaker notes:** “The model weighs criticality, information gaps, overdue severity, and business exposure. The alternative weights move suppliers in and out of the priority cohort, so the ranking is a management choice rather than a legal risk score. The pilot target is proposed; compare observed completions and dispositions with the starting worklist before drawing conclusions.”

**Presenter check:** Before presenting, the student should be able to explain each number, denominator, filter effect, score component, and caveat in their own words. Replace no verified figure with an estimate and do not claim that follow-up caused a response.
