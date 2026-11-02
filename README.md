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
│   └── 02_sensitivity_analysis_recovered.ipynb   # read-only audit of sensitivity exports
├── docs/
│   ├── data_validation_and_kpi_reconciliation.md  # plain-language results
│   └── tableau_handoff.md                      # data model + calculated fields for Tableau
├── reports/                                    # validated Phase 1 outputs
├── CLAUDE.md                                   # project context for AI assistants
├── requirements.txt
├── run_analysis.py                             # reproducible Phase 1 sensitivity calculations
├── .gitignore                                  # local data, environments, secrets, and caches
└── README.md
```

The supplied workbook is labelled simulated educational data, but it is assignment-provided source material and
is intentionally excluded from Git. Keep it at `data/Supplier_Compliance_Intelligence.xlsx` locally; do not
commit or redistribute it. The malformed legacy file `notebooks/02_sensitivity_analysis.ipynb` is preserved
locally and excluded from Git. Use the recovered audit notebook listed above instead.

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

Run the scenario calculations and regenerate the three supplier/category CSV exports with:

```bash
.venv/bin/python run_analysis.py
```

The script requires the local source workbook. It checks the original risk formula, scenario weights, score,
category and rank integrity, and workbook hash. The recovered sensitivity notebook validates the existing CSVs
and summarizes category, top-181, supplier-rank, and category-transition changes without rerunning calculations
or writing files.

## Key rules

- **The source workbook is read-only.** Never overwrite, rename or edit `data/Supplier_Compliance_Intelligence.xlsx`.
- Reporting cutoff: **30 September 2026**.
- Submission ≠ completion ≠ confirmed regulatory compliance.
- The risk score is an *illustrative prioritisation model*, not a validated legal risk rating.
- In Tableau, use **logical relationships**, not physical joins (see `docs/tableau_handoff.md`).
