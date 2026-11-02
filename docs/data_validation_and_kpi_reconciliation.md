# Data Validation & KPI Reconciliation

Source: `data/Supplier_Compliance_Intelligence.xlsx` (simulated educational data).
Evidence: [`notebooks/01_validation_and_kpis.ipynb`](../notebooks/01_validation_and_kpis.ipynb), which ran
**50 / 50 checks passed**. The workbook's SHA-256 hash was unchanged before and after the run.
Reporting cutoff: **30 September 2026**.

## 1. What is in the workbook

| Sheet | Rows | Columns | One row represents | Unique key |
|---|---|---|---|---|
| Supplier_Master | 800 | 7 | a supplier | Supplier_ID |
| Compliance_Requests | 2,139 | 11 | one compliance module requested from one supplier | Request_ID |
| Supplier_Engagement | 1,499 | 7 | one follow-up contact about a request | Engagement_ID |
| Risk_Assessment | 800 | 11 | a supplier's risk score at the cutoff | Supplier_ID |

Reference sheets: START HERE, KPI_Summary (11 metrics), Risk_Weights, Data_Dictionary. The workbook contains no
formulas, Excel tables or hidden sheets.

Compliance modules: RoHS (543 requests), REACH (538), PFAS (537), CMRT (521). Each supplier receives 1–4 modules,
never the same module twice.

## 2. Data quality results

- **No duplicate rows** in any table, and every key is unique and never blank.
- **Missing values:** only `Submission_Date` has blanks (612). This is expected: 581 are Pending, and 31 are
  Declined without a submission date.
- **Dates are stored as text** (`YYYY-MM-DD`). All values convert to valid dates.
- **Date logic is consistent.** Every due date is the campaign date + 45 days. No submission comes before its
  campaign or after the cutoff, and every follow-up falls between the campaign date and the cutoff.
- **The flags mean what the Data Dictionary says.** `Submitted_Flag` = 1 exactly when a submission date exists.
  `Complete_Flag` = 1 exactly when the status is Complete. `Overdue_Days` = days from the due date to the cutoff
  for every non-complete request, and 0 for complete requests.
- **All 800 suppliers are "Active",** so Supplier_Status can't be used as a filter.

## 3. Relationships

| Relationship | Result |
|---|---|
| Supplier_Master → Compliance_Requests (Supplier_ID) | No orphans; every supplier has 1–4 requests |
| Supplier_Master → Risk_Assessment (Supplier_ID) | Exactly one assessment per supplier |
| Compliance_Requests → Supplier_Engagement (Request_ID) | No orphans; 990 requests have 1–4 follow-ups, 1,149 have none |

The Supplier_ID in Supplier_Engagement always matches the supplier on the linked request.

**Why this matters for Tableau:** joining requests to engagements physically produces **2,648 rows instead of
2,139**, because a request can have up to four follow-ups. That would inflate every request-level count and rate.
Tableau's logical relationships avoid this.

## 4. Request status and compliance outcome

| Response status | Requests | Submitted | Compliance outcome |
|---|---|---|---|
| Complete | 1,193 | all | 941 Compliant, 101 Non-compliant, 151 Unknown |
| Incomplete | 281 | all | Not assessed |
| Declined | 84 | 53 yes, 31 no | Not assessed |
| Pending | 581 | none | Not assessed |

These are three different things:
- **Submitted** (1,527): the supplier sent something back. It may still be incomplete or a decline.
- **Complete** (1,193): the supplier provided a complete declaration.
- **Declared compliant** (941): what the supplier says about itself. The Data Dictionary states this is
  *not independently verified*.

## 5. Risk model check

`Overall_Risk_Score = 0.35 × Criticality + 0.30 × Information Gap + 0.20 × Overdue Severity + 0.15 × Business Exposure`

| Component | Rule (from Risk_Weights) | Reproduced? |
|---|---|---|
| Criticality | High = 100, Medium = 60, Low = 20 | Exact |
| Information gap | 100 × non-complete requests / eligible requests | Yes (rounding ≤ 0.004) |
| Overdue severity | min(100, maximum overdue days / 120 × 100) | Yes (rounding ≤ 0.004) |
| Business exposure | min(100, active parts / 850 × 100) | Yes (rounding ≤ 0.005) |
| Overall score | weighted sum above | Yes (rounding ≤ 0.005) |
| Category | High ≥ 70, Medium ≥ 40, Low < 40 | All 800 match |

Result: 181 High, 366 Medium, 253 Low.

Two suppliers sit just above the High threshold, so a small change in inputs would change their category:
SUP-0610 (70.01) and SUP-0205 (70.12).

The score is an **illustrative prioritisation model**, not a validated legal risk rating.

## 6. KPI reconciliation

Every value was recalculated from the data tables and matches `KPI_Summary`. Nothing needed adjusting.

| KPI | Grain | Formula | Calculated | Reference |
|---|---|---|---|---|
| Active suppliers | Supplier | suppliers with status Active | 800 | 800 |
| Eligible requests | Request | count of requests | 2,139 | 2,139 |
| Submitted requests | Request | sum of Submitted_Flag | 1,527 | 1,527 |
| Request response rate | Request | submitted / eligible | 71.39% | 71.4% |
| Request completion rate | Request | complete / eligible | 55.77% | 55.8% |
| Supplier response rate | Supplier | suppliers with ≥ 1 submitted request / 800 | 92.25% (738) | 92.3% |
| Overdue backlog | Request | requests with Overdue_Days > 0 | 946 | 946 |
| Average response time | Submitted requests | mean days from campaign date to submission date | 55.14 days | 55.1 |
| High-priority suppliers | Supplier | Risk_Category = High | 181 | 181 |
| Requests with follow-up | Request | distinct Request_ID in Supplier_Engagement | 990 | 990 |
| Follow-up conversion rate | Followed-up requests | requests with any "Responded later" / 990 | 48.59% (481) | 48.59% |

The project brief listed the first ten of these. KPI_Summary also contains an eleventh, Follow-up conversion rate,
which also reconciles.

## 7. Points to word carefully

These are not data errors, but each could easily be misstated.

1. **"Overdue backlog" (946) is every non-complete request.** It includes 334 requests the supplier *did* submit
   (281 Incomplete and 53 Declined). The latest due date is 26 Sep 2026, so by the cutoff every non-complete request
   is past due. If "overdue" meant "never submitted", the figure would be 612.
2. **Response time is measured from campaign start.** Suppliers had 45 days. The average of 55.1 days means the
   average submission arrived about 10 days **after** the due date (median 55 days).
3. **Follow-up conversion is counted per request.** Counted per follow-up event instead, the share is 37.0%.
4. **"Responded later" lines up exactly with submission.** All 481 followed-up requests with a "Responded later"
   event were submitted, and none of the other 509 were. This shows an association. It does **not** show that the
   follow-up caused the response.
5. **"Complete" doesn't mean compliant.** Use "complete declarations" and "declared compliant (not independently
   verified)".
6. **Simulated data:** the dataset is labelled *simulated educational data — not real supplier records*.

## 8. Open questions

None block the analysis. These are assumptions to confirm with the assignment brief if possible:

- "Eligible requests" is taken as every request row. The data has no separate eligibility field.
- "Supplier response" counts any submission, including Incomplete and submitted Declines. That definition matches
  the reference value.

## 9. Phase 1 risk sensitivity analysis

The primary, executable scenario analysis is [`notebooks/02_sensitivity_analysis.ipynb`](../notebooks/02_sensitivity_analysis.ipynb).
It recalculates the Original, Criticality Emphasis, and Information-Gap Emphasis scores for all 800 suppliers,
then verifies categories, ranks, top-181 membership, category transitions, and supplier movement against the
validated CSV exports and [`reports/sensitivity_analysis_report.md`](../reports/sensitivity_analysis_report.md).
The notebook reads the source workbook and reports only; it does not write outputs. Run it with the project's
`.venv` kernel and the local, read-only workbook.

The scenario weights and score thresholds are management choices for an illustrative prioritisation model. The
scenario results demonstrate how rankings respond to those choices; they do not establish a legal/regulatory
rating or a uniquely correct intervention order. The supplementary
[`notebooks/02_sensitivity_analysis_recovered.ipynb`](../notebooks/02_sensitivity_analysis_recovered.ipynb)
provides a CSV-only audit that does not require opening the workbook.
