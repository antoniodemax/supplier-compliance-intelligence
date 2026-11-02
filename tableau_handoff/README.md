# Tableau Handoff Package

This folder is a portable build package for the Supplier Compliance Intelligence Tableau dashboards. Copy the
entire `tableau_handoff` folder to the Windows laptop. The workbook is simulated educational data; do not treat it
as real supplier information. Keep the Excel workbook read-only.

## Folder contents

```text
tableau_handoff/
├── README.md
├── Supplier_Compliance_Intelligence.xlsx
├── data_exports/
│   ├── scenario_category_comparison.csv
│   ├── supplier_priority_tiers.csv
│   └── supplier_scenario_comparison.csv
├── docs/
│   ├── data_validation_and_kpi_reconciliation.md
│   ├── tableau_dashboard_blueprint.md
│   └── tableau_handoff.md
└── reports/
    └── sensitivity_analysis_report.md
```

The three documents in `docs/` explain the findings, detailed dashboard design, and shorter Tableau setup. The
sensitivity report is for context and verification; it is **not** a Tableau data source. The validation and
sensitivity notebooks and Python scripts remain in the original project and are not required to build the
dashboards.

## Which files to connect to Tableau

### Main source: Excel workbook

In Tableau, choose **Connect → Microsoft Excel** and open
`Supplier_Compliance_Intelligence.xlsx` from this folder. Use these four analytical worksheets:

1. `Compliance_Requests`
2. `Supplier_Master`
3. `Risk_Assessment`
4. `Supplier_Engagement`

Build relationships in Tableau's **logical layer**, not physical joins. Start with `Compliance_Requests`, then
relate supplier master and risk assessment by `Supplier_ID`, and engagement by `Request_ID`:

```text
Supplier_Master (one) ── Supplier_ID ── (many) Compliance_Requests
        │                                      │
        └── Supplier_ID ── (one) Risk_Assessment
                                               │
                                               └── Request_ID ── (many) Supplier_Engagement
```

The relationship from supplier master to risk assessment is one-to-one. The other two are one-to-many. The
`Supplier_ID` in `Supplier_Engagement` is redundant for this model; use the request relationship and do not add a
second relationship on that field.

The workbook's other sheets—`START HERE`, `KPI_Summary`, `Risk_Weights`, and `Data_Dictionary`—are reference
material. They are useful for validation and explanations, but should not be added as extra fact tables to the
dashboard model.

### Scenario and priority CSVs: separate sources

Connect these CSVs separately only for their relevant views:

| File | Connect for | Grain |
|---|---|---|
| `data_exports/scenario_category_comparison.csv` | Overview scenario/category-count chart | Three rows, one per risk category; scenario values are separate columns |
| `data_exports/supplier_scenario_comparison.csv` | Optional scenario score, category, rank, and movement detail | One row per supplier; 800 unique `Supplier_ID` values |
| `data_exports/supplier_priority_tiers.csv` | Optional operational priority-tier view | One row per supplier; 800 unique `Supplier_ID` values |

For the beginner-safe build, **keep each CSV separate from the Excel logical model**. Do not physically join or
blend scenario rows into supplier, request, or engagement records. The blueprint describes a possible
cross-connection logical relationship by `Supplier_ID` for a future version, but it is optional: only consider it
if the Tableau version supports it and the resulting supplier keys and totals validate. It is not needed for the
three core dashboards.

Do not connect the Markdown documents as data. Use the dashboard design and definitions in
`docs/tableau_dashboard_blueprint.md`; use `reports/sensitivity_analysis_report.md` to understand verified
sensitivity results.

## Grain, keys, and relationships

| Dataset | Rows | One row represents | Primary key | Relationship key |
|---|---:|---|---|---|
| `Supplier_Master` | 800 | One supplier | `Supplier_ID` | `Supplier_ID` to requests and risk assessment |
| `Compliance_Requests` | 2,139 | One compliance-module request for one supplier | `Request_ID` | `Supplier_ID` to supplier; `Request_ID` to engagement |
| `Risk_Assessment` | 800 | One supplier's assessment at the cutoff | `Supplier_ID` | `Supplier_ID` to supplier master |
| `Supplier_Engagement` | 1,499 | One follow-up event | `Engagement_ID` | `Request_ID` to compliance requests |

The IDs are text. All expected keys are present and unique, and the inspected relationships have no orphan
supplier/request references. There are 1,499 engagement events for 990 distinct requests; 1,149 requests have no
follow-up event. Multiple follow-up events can refer to a single request.

## Measures that must not be double-counted

- **Requests:** count distinct `Request_ID` for request totals, incomplete requests, overdue requests, and
  requests with a follow-up. At request grain, `Submitted_Flag` and `Complete_Flag` are 0/1 and can be summed.
  Do not sum those flags after expanding requests to engagement-event rows.
- **Suppliers:** use distinct `Supplier_ID` for supplier counts and response rates. A supplier can have multiple
  requests.
- **Engagements:** count distinct `Engagement_ID` for event totals; count distinct `Request_ID` for requests with
  any follow-up. These answer different questions.
- **Risk values:** the four components and overall score are at supplier grain. Do not sum them over requests or
  engagement events. Show them at one supplier per mark/row; if aggregated, choose and label an appropriate
  aggregation rather than presenting a sum.
- **Active part counts:** `Active_Part_Count` is repeated when supplier data is viewed alongside multiple
  requests. Do not sum it over request or event rows.
- **Overdue:** `Overdue_Days > 0` gives 946 non-complete requests past due at 30 September 2026. This is not the
  same as never submitted (612). It includes submitted incomplete and submitted declined requests.
- **Average response time:** 55.1 days from campaign date to submission date, averaged over submitted records
  with a date. It is not “55 days late”; the request due date is 45 days after campaign start.

Use the workbook relationships, and prefer `COUNTD` for IDs in multi-table views. A physical request-to-engagement
join increases row count from 2,139 to 2,648 and inflates request-level measures.

## Risk calculations already provided

The `Risk_Assessment` sheet already contains:

- `Criticality_Score`
- `Information_Gap_Score`
- `Overdue_Severity_Score`
- `Business_Exposure_Score`
- `Overall_Risk_Score`
- `Risk_Category`
- `Eligible_Request_Count`
- `Information_Gap_Count`
- `Maximum_Overdue_Days`

**Reuse these validated values. Do not recalculate or silently change the approved formula in Tableau.**

```text
Overall Risk Score =
    0.35 × Criticality Score
  + 0.30 × Information Gap Score
  + 0.20 × Overdue Severity Score
  + 0.15 × Business Exposure Score
```

The components are based on the Risk Weights reference sheet:

- Criticality: High = 100, Medium = 60, Low = 20.
- Information gap: 100 × non-complete requests / eligible requests.
- Overdue severity: minimum of 100 and (maximum overdue days / 120 × 100).
- Business exposure: minimum of 100 and (active parts / 850 × 100).

Categories are **High ≥ 70**, **Medium ≥ 40 and < 70**, and **Low < 40**. They are management prioritisation
bands—not probabilities of non-compliance or legal/regulatory ratings. A complete supplier declaration is not
proof that the supplier is compliant; the workbook's `Compliant` outcome is self-declared and not independently
verified.

Approved sensitivity scenarios are also available in the separate supplier/category CSV exports:

| Scenario | Criticality | Information gap | Overdue severity | Business exposure |
|---|---:|---:|---:|---:|
| Original | 35% | 30% | 20% | 15% |
| Criticality emphasis | 50% | 15% | 20% | 15% |
| Information-gap emphasis | 25% | 40% | 20% | 15% |

The scenario files should remain separate data sources in the first build. Their values show how management
weighting choices change categories and ranking; they do not prove one scenario is uniquely correct.

## First-build checks

1. Set the workbook date fields (`Campaign_Date`, `Due_Date`, `Submission_Date`, `Follow_Up_Date`, and
   `Assessment_Date`) to **Date** in Tableau. The Excel source stores these as text in `YYYY-MM-DD` form.
2. Verify a request-level sheet shows 2,139 distinct requests before adding any filters.
3. Verify supplier-level counts show 800 distinct suppliers.
4. Build a KPI check against the workbook reference: 1,527 submitted, 1,193 complete, 71.4% request response,
   55.8% request completion, 92.3% supplier response, 946 overdue, and 181 original High-risk suppliers.
5. Keep baseline KPI cards separate from chart filters unless the cards are explicitly relabelled with the
   selected cohort and denominator.
6. Put “Simulated educational data — not real supplier records” and “As of 30 September 2026” on each dashboard.
   Tableau Public workbooks are public, so confirm publication requirements before publishing.
7. Follow `docs/tableau_dashboard_blueprint.md` for dashboard layouts, worksheet inventory, filters, actions,
   presentation narrative, and further validation.

## Copy integrity

The workbook, blueprint, supporting documents, sensitivity report, and three CSV exports were copied without
editing. Their SHA-256 hashes were compared with the original project files after copying; all matched. The
source workbook and source exports remain unchanged in the original project.
