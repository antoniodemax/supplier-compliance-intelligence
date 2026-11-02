# Supplier Compliance Intelligence

Business intelligence project for the Quantic MSBA *Communicating with Data* assignment. It uses a **simulated**
multinational manufacturing supplier-compliance dataset to help the Director of Supply Chain Compliance see where
supplier compliance information is missing, understand the possible exposure, and decide which suppliers to act on
first.

Deliverables: a Tableau Public dashboard, supported by a validated Python analysis and an executive presentation.

## Project structure

```
supplier-compliance-intelligence/
├── data/
│   └── Supplier_Compliance_Intelligence.xlsx   # local source workbook — READ-ONLY, not committed
├── notebooks/
│   ├── 01_validation_and_kpis.ipynb               # data validation + KPI reconciliation
│   ├── 02_sensitivity_analysis.ipynb              # primary Phase 1 sensitivity analysis
│   └── 02_sensitivity_analysis_recovered.ipynb   # supplementary CSV-only audit
├── docs/
│   ├── data_validation_and_kpi_reconciliation.md  # plain-language results
│   ├── tableau_handoff.md                         # concise data model + calculated fields
│   └── tableau_dashboard_blueprint.md             # Phase 2 dashboards + presentation outline
├── reports/                                    # validated Phase 1 outputs
├── CLAUDE.md                                   # project context for AI assistants
├── requirements.txt
├── run_analysis.py                             # reproducible Phase 1 sensitivity calculations
├── .gitignore                                  # local data, environments, secrets, and caches
└── README.md
```

The supplied workbook is labelled simulated educational data, but it is assignment-provided source material and
is intentionally excluded from Git. Keep it at `data/Supplier_Compliance_Intelligence.xlsx` locally; do not
commit or redistribute it. The primary sensitivity notebook reads this local workbook and the validated report
exports; it does not write to either.

## Setup

The virtual environment already exists at `.venv` (Python 3.12.3).

```bash
cd ~/Projects/supplier-compliance-intelligence
source .venv/bin/activate
pip install -r requirements.txt   # only needed when recreating the environment
```

## Running the validation notebook

1. Open `notebooks/01_validation_and_kpis.ipynb` in VS Code (Jupyter extension).
2. Select the kernel from `.venv`.
3. Run **Restart & Run All**.

The final cell prints `N / N checks passed` and raises an error if any check fails. The notebook also confirms the
workbook's SHA-256 hash is identical before and after running.

## Phase 1 sensitivity analysis

The primary, self-contained analysis is `notebooks/02_sensitivity_analysis.ipynb`. Open it with the `.venv`
kernel and run **Restart & Run All**. It recalculates the approved scenarios from the local workbook, checks
the category/rank and top-181 movements, and compares all supplier-level results with the validated CSV exports
and [`reports/sensitivity_analysis_report.md`](reports/sensitivity_analysis_report.md). It does not write files.

To independently regenerate the three supplier/category CSV exports:

```bash
.venv/bin/python run_analysis.py
```

The script requires the local source workbook. It checks the original risk formula, scenario weights, score,
category and rank integrity, and workbook hash. The supplementary
`notebooks/02_sensitivity_analysis_recovered.ipynb` validates the existing CSVs without recalculating scenarios
or writing files.

## Key rules

- **The source workbook is read-only.** Never overwrite, rename or edit `data/Supplier_Compliance_Intelligence.xlsx`.
- Reporting cutoff: **30 September 2026**.
- Submission ≠ completion ≠ confirmed regulatory compliance.
- The risk score is an *illustrative prioritisation model*, not a validated legal risk rating.
- In Tableau, use **logical relationships**, not physical joins (see `docs/tableau_handoff.md`).

## Phase 2 Tableau blueprint

[`docs/tableau_dashboard_blueprint.md`](docs/tableau_dashboard_blueprint.md) is the implementation-ready plan
for the Executive Overview, Compliance Gaps, and Supplier Prioritisation dashboards. It includes the verified
data model and calculations, worksheet inventory, filter/action guidance, validation sequence, presentation
narrative, and a three-slide outline. This document is a blueprint only; no Tableau workbook or final slides have
been created.
