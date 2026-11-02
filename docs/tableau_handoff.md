# Tableau Handoff

Everything here was verified in [`notebooks/01_validation_and_kpis.ipynb`](../notebooks/01_validation_and_kpis.ipynb).
See [`data_validation_and_kpi_reconciliation.md`](data_validation_and_kpi_reconciliation.md) for the evidence.

## 1. Connect

Tableau Public: **Connect → Microsoft Excel →** `data/Supplier_Compliance_Intelligence.xlsx`.
Use a **copy** of the workbook if Tableau needs to move it. Never edit the original.

Use these four sheets: `Supplier_Master`, `Compliance_Requests`, `Supplier_Engagement`, `Risk_Assessment`. The other
sheets are reference only.

## 2. Data model — logical relationships (not joins)

Drag `Compliance_Requests` onto the canvas first, so it is the root table at the request grain. Then relate the
others by dragging them onto the canvas. Do **not** double-click into the physical layer to create joins.

```
Supplier_Master ──(Supplier_ID)── Compliance_Requests ──(Request_ID)── Supplier_Engagement
       │
       └──(Supplier_ID)── Risk_Assessment
```

| Relationship | Fields | Cardinality | Referential integrity |
|---|---|---|---|
| Supplier_Master – Compliance_Requests | Supplier_ID = Supplier_ID | One – Many | All records match |
| Supplier_Master – Risk_Assessment | Supplier_ID = Supplier_ID | One – One | All records match |
| Compliance_Requests – Supplier_Engagement | Request_ID = Request_ID | One – Many | Some records match (1,149 requests have no follow-up) |

Leave `Supplier_Engagement.Supplier_ID` unrelated. Use `Supplier_Master.Supplier_ID` for supplier-level views.

**Sanity check:** after building, `COUNTD([Request_ID])` and `COUNT([Compliance_Requests])` must both be **2,139**.
A physical join would give 2,648.

## 3. Data types to fix

All date fields arrive as **text**. Change each one's data type to **Date**: `Campaign_Date`, `Due_Date`,
`Submission_Date`, `Follow_Up_Date` and `Assessment_Date`. The format is `YYYY-MM-DD`, and all values parse.

Set `Submitted_Flag` and `Complete_Flag` as **measures**, aggregated with SUM.

## 4. Calculated fields

Reporting cutoff:
```
// Cutoff Date
#2026-09-30#
```

Request-level KPIs:
```
// Eligible Requests
COUNTD([Request_ID])                                           // 2,139

// Submitted Requests
SUM([Submitted_Flag])                                          // 1,527

// Request Response Rate
SUM([Submitted_Flag]) / COUNTD([Request_ID])                   // 71.4%

// Request Completion Rate
SUM([Complete_Flag]) / COUNTD([Request_ID])                    // 55.8%

// Overdue Backlog
COUNTD(IF [Overdue_Days] > 0 THEN [Request_ID] END)            // 946

// Response Days  (row-level)
DATEDIFF('day', [Campaign_Date], [Submission_Date])

// Average Response Time
AVG([Response Days])                                           // 55.1 (null submissions are ignored)
```

Supplier-level KPIs:
```
// Active Suppliers
COUNTD(IF [Supplier_Status] = 'Active' THEN [Supplier_ID (Supplier_Master)] END)   // 800

// Supplier Responded  (LOD, supplier-level 0/1)
{ FIXED [Supplier_ID (Supplier_Master)] : MAX([Submitted_Flag]) }

// Supplier Response Rate
SUM({ FIXED [Supplier_ID (Supplier_Master)] : MAX([Submitted_Flag]) })
  / COUNTD([Supplier_ID (Supplier_Master)])                    // 92.3%

// High-Priority Suppliers
COUNTD(IF [Risk_Category] = 'High' THEN [Supplier_ID (Risk_Assessment)] END)       // 181
```

Follow-up KPIs:
```
// Requests With Follow-up
COUNTD([Request_ID (Supplier_Engagement)])                     // 990

// Responded Later Request  (request-level 0/1)
{ FIXED [Request_ID (Supplier_Engagement)] :
    MAX(IF [Engagement_Outcome] = 'Responded later' THEN 1 ELSE 0 END) }

// Follow-up Conversion Rate
COUNTD(IF [Responded Later Request] = 1 THEN [Request_ID (Supplier_Engagement)] END)
  / COUNTD([Request_ID (Supplier_Engagement)])                 // 48.6%
```

Tableau names duplicate field names after their table, for example `Supplier_ID (Supplier_Master)`. Match whatever
names your data pane shows.

Optional helper for status views:
```
// Request Stage
CASE [Response_Status]
  WHEN 'Complete'   THEN '4. Complete'
  WHEN 'Incomplete' THEN '3. Submitted – incomplete'
  WHEN 'Declined'   THEN '2. Declined'
  WHEN 'Pending'    THEN '1. No response'
END
```

**Validation:** build a single "KPI check" sheet showing every value above and compare it with `KPI_Summary` before
designing the dashboards.

## 5. Useful dimensions

- **Supplier:** Region (4), Industry_Category (5), Supplier_Criticality (3), Risk_Category (3), Active_Part_Count.
- **Request:** Compliance_Module (RoHS, REACH, PFAS, CMRT), Response_Status, Compliance_Outcome, Campaign_Date
  (Oct 2025 – Aug 2026), Overdue_Days (0–319).
- **Engagement:** Follow_Up_Channel (Email, Phone, Escalation), Assigned_Team, Engagement_Outcome.
- **Risk:** the four component scores, Overall_Risk_Score, Maximum_Overdue_Days, Information_Gap_Count.

Avoid Supplier_Status as a filter, because every supplier is Active.

## 6. Wording guardrails for dashboard titles and tooltips

| Say | Avoid |
|---|---|
| "Submitted" / "responded" | "complete" or "compliant" for submitted requests |
| "Complete declarations" | "compliant suppliers" |
| "Declared compliant (supplier self-declaration, not independently verified)" | "confirmed compliant" |
| "Overdue backlog: non-complete requests past due (946)" | "unanswered requests" (only 612 were never submitted) |
| "Average 55 days from campaign start; about 10 days past the 45-day due date" | "55 days late" |
| "Requests with a follow-up that later responded (48.6%)" | "follow-up caused responses" |
| "Illustrative prioritisation score" | "legal / regulatory risk rating" |
| "Simulated data" (footer) | presenting suppliers as real companies |

Mention near the risk view that SUP-0610 (70.01) and SUP-0205 (70.12) are only just over the High threshold.

## 7. Before publishing to Tableau Public

- Tableau Public workbooks are **public**. This dataset is simulated, but don't add anything confidential.
- Re-check the KPI sheet against `KPI_Summary` after any data-model change.
