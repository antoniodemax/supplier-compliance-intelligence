# Project context — Supplier Compliance Intelligence

Quantic MSBA *Communicating with Data* assignment. Stakeholder: Director of Supply Chain Compliance. Final
deliverable: Tableau Public dashboard + executive presentation, supported by a validated Python analysis.

**Academic integrity:** the assignment belongs to the student. Keep explanations understandable, never invent
findings, statistics or test results, and distinguish verified facts from assumptions.

## Hard rules

- `data/Supplier_Compliance_Intelligence.xlsx` is **read-only**. Never write, rename, delete or re-save it.
- Do not install packages, change system settings or use sudo without explicit approval.
- Keep the project lean: pandas + openpyxl + Jupyter only. No frameworks, agents or extra dependencies.
- Verify baseline claims with `notebooks/01_validation_and_kpis.ipynb` and sensitivity claims with
  `notebooks/02_sensitivity_analysis.ipynb` before stating them.

## Environment

- Python 3.12.3 virtualenv at `.venv` — run Python as `.venv/bin/python`.
- Dependencies pinned in `requirements.txt`.

## Data facts (verified in notebook 01)

- Tables and grain: `Supplier_Master` (800, one per supplier), `Compliance_Requests` (2,139, one per supplier ×
  module), `Supplier_Engagement` (1,499, one per follow-up event), `Risk_Assessment` (800, one per supplier).
- Keys `Supplier_ID`, `Request_ID`, `Engagement_ID` are unique; all relationships have zero orphans.
- Dates are stored as text `YYYY-MM-DD` and must be converted.
- Reporting cutoff 2026-09-30. All 11 `KPI_Summary` values reconcile exactly.
- Risk model reproduces within rounding (≤ 0.005).

## Business rules

- Overall_Risk_Score = 0.35 Criticality + 0.30 Information Gap + 0.20 Overdue Severity + 0.15 Business Exposure.
- High ≥ 70; Medium ≥ 40 and < 70; Low < 40.
- Submission ≠ completion ≠ confirmed regulatory compliance. The risk score is illustrative, not a legal rating.
- Tableau: logical relationships only — a physical join turns 2,139 request rows into 2,648.

## Docs

- `docs/data_validation_and_kpi_reconciliation.md` — plain-language results.
- `docs/tableau_handoff.md` — data model, calculated fields, wording guardrails.
- `notebooks/02_sensitivity_analysis.ipynb` — primary Phase 1 scenario calculations and export/report checks.
- `reports/sensitivity_analysis_report.md` — verified scenario findings and limitations.
