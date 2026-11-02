# Phase 1 Sensitivity Analysis Report

Date verified: 2026-11-02
Source workbook: `data/Supplier_Compliance_Intelligence.xlsx` (read-only)
Primary analysis: [`notebooks/02_sensitivity_analysis.ipynb`](../notebooks/02_sensitivity_analysis.ipynb), which independently recalculates the scenarios from the local workbook and checks them against the validated exports and this report.

Supporting artifacts: `run_analysis.py`, [`notebooks/02_sensitivity_analysis_recovered.ipynb`](../notebooks/02_sensitivity_analysis_recovered.ipynb), `reports/supplier_scenario_comparison.csv`, `reports/scenario_category_comparison.csv`, `reports/supplier_priority_tiers.csv`

## Scope
This report reflects the approved Phase 1 risk-sensitivity analysis using the original weighted risk formula and the alternative scenario weights in `run_analysis.py`:

- Original: (Criticality 0.35, Information Gap 0.30, Overdue 0.20, Business Exposure 0.15)
- Criticality Emphasis: (0.50, 0.15, 0.20, 0.15)
- Info Gap Emphasis: (0.25, 0.40, 0.20, 0.15)

## Scenario results

| Scenario | High | Medium | Low |
|---|---:|---:|---:|
| Original | 181 | 366 | 253 |
| Criticality Emphasis | 148 | 371 | 281 |
| Info Gap Emphasis | 151 | 381 | 268 |

## Top 181 retention and movement

The original top-181 set contains 181 suppliers.

| Scenario | Top 181 count | Retained from Original | Entrants | Exits |
|---|---:|---:|---:|---:|
| Criticality Emphasis | 181 | 164 | 17 | 17 |
| Info Gap Emphasis | 181 | 165 | 16 | 16 |

Interpretation:
- The size of the top-priority set stays constant at 181, but the composition changes materially.
- The criticality-weighted scenario has the greatest rotational change because it strengthens the effect of high criticality suppliers and weakens the effect of other drivers.
- The scenario weights, risk categories, and top-181 cohort are management-judgment choices. These scenario comparisons show the consequences of changing those choices while holding components fixed; they do not establish a uniquely correct priority list.

## Largest rank movements

Rank change convention:
- Negative change = upward movement in rank (supplier improves / moves closer to the top)
- Positive change = downward movement in rank (supplier worsens / moves lower)

### Criticality Emphasis
- Largest upward movement: `SUP-0699`
  - Original rank: 437
  - Criticality rank: 217
  - Rank change: -220
  - Criticality_Score: 100
  - Overdue_Severity_Score: 0.0
  - Original category: Medium
  - New category: Medium
- Largest downward movement: `SUP-0118`
  - Original rank: 524
  - Criticality rank: 708
  - Rank change: +184
  - Criticality_Score: 20
  - Overdue_Severity_Score: 25.0
  - Original category: Medium
  - New category: Low

### Info Gap Emphasis
- Largest upward movement: `SUP-0210`
  - Original rank: 411
  - Info Gap rank: 281
  - Rank change: -130
  - Criticality_Score: 20
  - Overdue_Severity_Score: 75.83
  - Original category: Medium
  - New category: Medium
- Largest downward movement: `SUP-0788`
  - Original rank: 458
  - Info Gap rank: 567
  - Rank change: +109
  - Criticality_Score: 100
  - Overdue_Severity_Score: 0.0
  - Original category: Medium
  - New category: Low

## Category movement

### Criticality Emphasis vs Original

| Original \ New | High | Medium | Low |
|---|---:|---:|---:|
| High | 136 | 45 | 0 |
| Medium | 12 | 311 | 43 |
| Low | 0 | 15 | 238 |

Summary:
- 45 suppliers moved from High to Medium.
- 43 moved from Medium to Low.
- 12 moved from Medium to High.
- 15 moved from Low to Medium.

### Info Gap Emphasis vs Original

| Original \ New | High | Medium | Low |
|---|---:|---:|---:|
| High | 147 | 34 | 0 |
| Medium | 4 | 338 | 24 |
| Low | 0 | 9 | 244 |

Summary:
- 34 suppliers moved from High to Medium.
- 24 moved from Medium to Low.
- 4 moved from Medium to High.
- 9 moved from Low to Medium.

## Verification status

The following were verified without modifying the source workbook or overwriting validated outputs:
- `run_analysis.py` runs successfully in the existing Python virtual environment.
- `notebooks/02_sensitivity_analysis.ipynb` independently recalculates every supplier score, category, rank, top-181 movement, and category transition; its clean-kernel run passed 36 / 36 checks against the workbook, three CSV exports, and this report.
- `notebooks/02_sensitivity_analysis_recovered.ipynb` executes successfully and passes 10 / 10 checks against the existing CSVs.
- `reports/supplier_scenario_comparison.csv` contains all 800 suppliers and the scenario deltas.
- `reports/scenario_category_comparison.csv` matches the category totals for each scenario.
- `reports/supplier_priority_tiers.csv` contains the supplier-level priority tier assignments.
- 10 / 10 integrity checks passed in the script.

## Limitations and caveats

- The primary sensitivity notebook reads the local workbook and the validated exports; it does not write to the workbook or regenerate reports. Use `run_analysis.py` when intentionally regenerating exports.
- This is a sensitivity analysis of an illustrative prioritisation model, not a legal or regulatory risk rating.
- The project is intentionally stopped at Phase 1 and does not proceed to Tableau or dashboard development.
