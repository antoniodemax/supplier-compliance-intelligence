import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', 30)

PROJECT_ROOT = Path(__file__).resolve().parent
WORKBOOK = PROJECT_ROOT / 'data' / 'Supplier_Compliance_Intelligence.xlsx'
CUTOFF = pd.Timestamp('2026-09-30')

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

HASH_AT_START = sha256(WORKBOOK)
checks = []

def check(area, description, passed, detail=''):
    checks.append((area, description, bool(passed), detail))
    print(f'{"[PASS]" if passed else "[FAIL]"} {area}: {description} {detail}')

print('Workbook:', WORKBOOK)
print('SHA-256 :', HASH_AT_START)

# Load the four main tables
sm = pd.read_excel(WORKBOOK, sheet_name='Supplier_Master')
cr = pd.read_excel(WORKBOOK, sheet_name='Compliance_Requests')
se = pd.read_excel(WORKBOOK, sheet_name='Supplier_Engagement')
ra = pd.read_excel(WORKBOOK, sheet_name='Risk_Assessment')

print('\nLoaded tables:')
print('Supplier_Master:', sm.shape)
print('Compliance_Requests:', cr.shape)
print('Supplier_Engagement:', se.shape)
print('Risk_Assessment:', ra.shape)

# Check component scores
component_cols = ['Criticality_Score', 'Information_Gap_Score', 'Overdue_Severity_Score', 'Business_Exposure_Score']
print('\nComponent score stats:')
print(ra[component_cols].describe())

# Verify original risk score
ra['Recalculated_Original'] = (
    ra['Criticality_Score'] * 0.35 +
    ra['Information_Gap_Score'] * 0.30 +
    ra['Overdue_Severity_Score'] * 0.20 +
    ra['Business_Exposure_Score'] * 0.15
)

match = np.isclose(ra['Overall_Risk_Score'], ra['Recalculated_Original'], atol=0.01).all()
check('Risk', 'Original risk formula reproduces within 0.01', match,
      f'max diff = {(ra["Overall_Risk_Score"] - ra["Recalculated_Original"]).abs().max():.4f}')

cat_match = (ra['Risk_Category'] == pd.cut(ra['Overall_Risk_Score'],
    bins=[-np.inf, 40, 70, np.inf], labels=['Low', 'Medium', 'High'])).all()
check('Risk', 'Risk categories match threshold definition', cat_match)

print('\n=== Original validation complete ===')

# Scenario definitions: (Criticality, Information Gap, Overdue Severity, Business Exposure)
scenarios = {
    'Original': (0.35, 0.30, 0.20, 0.15),
    'Criticality_Emphasis': (0.50, 0.15, 0.20, 0.15),
    'Info_Gap_Emphasis': (0.25, 0.40, 0.20, 0.15)
}

# Verify each scenario sums to 1.0
for name, weights in scenarios.items():
    total = sum(weights)
    check('Weights', f'{name} weights sum to 100%', np.isclose(total, 1.0),
          f'sum = {total:.2f}')

# Calculate risk scores for each scenario
for name, (w_crit, w_info, w_overdue, w_biz) in scenarios.items():
    col_name = f'Risk_Score_{name}'
    ra[col_name] = (
        ra['Criticality_Score'] * w_crit +
        ra['Information_Gap_Score'] * w_info +
        ra['Overdue_Severity_Score'] * w_overdue +
        ra['Business_Exposure_Score'] * w_biz
    )

    # Assign risk category
    ra[f'Risk_Category_{name}'] = pd.cut(
        ra[col_name],
        bins=[-np.inf, 40, 70, np.inf],
        labels=['Low', 'Medium', 'High']
    )

    # Rank by descending score (1 = highest risk)
    ra[f'Rank_{name}'] = ra[col_name].rank(ascending=False, method='min').astype(int)

    print(f'{name}: score range {ra[col_name].min():.2f} - {ra[col_name].max():.2f}')
    print(f'  Categories: {ra[f"Risk_Category_{name}"].value_counts().to_dict()}')

# Category counts for each scenario
category_comparison = {}
for name in scenarios.keys():
    cat_col = f'Risk_Category_{name}'
    counts = ra[cat_col].value_counts().reindex(['High', 'Medium', 'Low']).fillna(0).astype(int)
    category_comparison[name] = counts
    print(f'\n{name} category counts:')
    print(counts)

cat_df = pd.DataFrame(category_comparison)
cat_df.index.name = 'Category'
print('\nCategory comparison table:')
print(cat_df)

# Top 181 suppliers in each scenario
top181_comparison = {}
for name in scenarios.keys():
    rank_col = f'Rank_{name}'
    top181 = set(ra[ra[rank_col] <= 181]['Supplier_ID'])
    top181_comparison[name] = top181
    print(f'\n{name} top 181: {len(top181)} suppliers')

# Suppliers entering/leaving High category compared to Original
orig_high = set(ra[ra['Risk_Category_Original'] == 'High']['Supplier_ID'])
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    new_high = set(ra[ra[f'Risk_Category_{name}'] == 'High']['Supplier_ID'])
    entering = new_high - orig_high
    leaving = orig_high - new_high
    print(f'\n{name} vs Original:')
    print(f'  Entering High: {len(entering)} suppliers')
    print(f'  Leaving High: {len(leaving)} suppliers')
    print(f'  Net change: {len(new_high) - len(orig_high)}')

# Suppliers entering/leaving top 181 ranking
orig_top181 = top181_comparison['Original']
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    new_top181 = top181_comparison[name]
    entering = new_top181 - orig_top181
    leaving = orig_top181 - new_top181
    print(f'\n{name} vs Original (top 181 ranking):')
    print(f'  Entering top 181: {len(entering)} suppliers')
    print(f'  Leaving top 181: {len(leaving)} suppliers')

# Calculate rank changes
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    ra[f'Rank_Change_{name}'] = ra[f'Rank_{name}'] - ra['Rank_Original']

# Largest upward movements (improved rank = lower number = better)
print('\n=== Largest rank improvements (upward movement) ===')
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    col = f'Rank_Change_{name}'
    top_improved = ra.nsmallest(10, col)[['Supplier_ID', 'Rank_Original', f'Rank_{name}', col]]
    print(f'\n{name} - Top 10 improved:')
    print(top_improved.to_string(index=False))

# Largest downward movements (worsened rank = higher number = worse)
print('\n=== Largest rank declines (downward movement) ===')
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    col = f'Rank_Change_{name}'
    top_declined = ra.nlargest(10, col)[['Supplier_ID', 'Rank_Original', f'Rank_{name}', col]]
    print(f'\n{name} - Top 10 declined:')
    print(top_declined.to_string(index=False))

# High overdue severity suppliers (top quartile = 75th percentile)
overdue_threshold = ra['Overdue_Severity_Score'].quantile(0.75)
high_overdue = ra[ra['Overdue_Severity_Score'] >= overdue_threshold]['Supplier_ID']
print(f'\nHigh overdue severity threshold (75th percentile): {overdue_threshold:.1f}')
print(f'Suppliers with high overdue severity: {len(high_overdue)}')

# High criticality suppliers (Criticality_Score = 100 = High criticality)
high_criticality = ra[ra['Criticality_Score'] == 100]['Supplier_ID']
print(f'Suppliers with High criticality (score=100): {len(high_criticality)}')

# Check rank changes for these groups
for name in ['Criticality_Emphasis', 'Info_Gap_Emphasis']:
    col = f'Rank_Change_{name}'

    # High overdue severity suppliers
    high_overdue_changes = ra[ra['Supplier_ID'].isin(high_overdue)][['Supplier_ID', 'Rank_Original', f'Rank_{name}', col, 'Overdue_Severity_Score']]
    avg_change = high_overdue_changes[col].mean()
    print(f'\n{name} - High overdue severity suppliers (n={len(high_overdue_changes)}):')
    print(f'  Average rank change: {avg_change:.1f} (negative = improved)')
    print(f'  Max improvement: {high_overdue_changes[col].min():.0f}')
    print(f'  Max decline: {high_overdue_changes[col].max():.0f}')

    # High criticality suppliers
    high_crit_changes = ra[ra['Supplier_ID'].isin(high_criticality)][['Supplier_ID', 'Rank_Original', f'Rank_{name}', col, 'Criticality_Score']]
    avg_change = high_crit_changes[col].mean()
    print(f'\n{name} - High criticality suppliers (n={len(high_crit_changes)}):')
    print(f'  Average rank change: {avg_change:.1f} (negative = improved)')
    print(f'  Max improvement: {high_crit_changes[col].min():.0f}')
    print(f'  Max decline: {high_crit_changes[col].max():.0f}')

# Convert date columns
for df in [cr, se]:
    for date_col in ['Campaign_Date', 'Due_Date', 'Submission_Date', 'Follow_Up_Date']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')

# Total incomplete requests
total_incomplete = (cr['Complete_Flag'] == 0).sum()
total_eligible = len(cr)
print(f'\nTotal incomplete requests (Complete_Flag = 0): {total_incomplete}')
print(f'Total eligible requests: {total_eligible}')
print(f'Incomplete rate: {total_incomplete/total_eligible*100:.1f}%')

# Incomplete requests belonging to High-risk suppliers
high_risk_suppliers = set(ra[ra['Risk_Category_Original'] == 'High']['Supplier_ID'])
high_risk_incomplete = cr[(cr['Complete_Flag'] == 0) & (cr['Supplier_ID'].isin(high_risk_suppliers))]
high_risk_incomplete_count = len(high_risk_incomplete)
print(f'\nIncomplete requests from High-risk suppliers: {high_risk_incomplete_count}')

# Two different denominators:
share_of_incomplete = high_risk_incomplete_count / total_incomplete * 100
share_of_eligible = high_risk_incomplete_count / total_eligible * 100
print(f'Share of ALL incomplete requests: {share_of_incomplete:.1f}%')
print(f'Share of ALL eligible requests: {share_of_eligible:.1f}%')

# Verify PFAS completion rate
pfas_requests = cr[cr['Compliance_Module'] == 'PFAS']
pfas_complete = pfas_requests[pfas_requests['Complete_Flag'] == 1]
pfas_completion_rate = len(pfas_complete) / len(pfas_requests) * 100
print(f'\nPFAS completion rate: {pfas_completion_rate:.1f}% ({len(pfas_complete)}/{len(pfas_requests)})')

# Verify Asia-Pacific + PFAS backlog
apac_suppliers = sm[sm['Region'] == 'Asia-Pacific']['Supplier_ID']
apac_pfas_incomplete = cr[
    (cr['Complete_Flag'] == 0) &
    (cr['Compliance_Module'] == 'PFAS') &
    (cr['Supplier_ID'].isin(apac_suppliers))
]
apac_pfas_count = len(apac_pfas_incomplete)
print(f'Asia-Pacific + PFAS incomplete requests: {apac_pfas_count}')

# Also verify overdue definition
total_overdue = (cr['Overdue_Days'] > 0).sum()
never_submitted = cr['Submission_Date'].isna().sum()
print(f'\nTotal overdue requests (Overdue_Days > 0): {total_overdue}')
print(f'Never submitted (Submission_Date is NaN): {never_submitted}')

# Definitions used:
print('\n=== DEFINITIONS ===')
print('Incomplete request: Complete_Flag = 0 (includes Pending, Incomplete, Declined statuses)')
print('Overdue request: Overdue_Days > 0 (all non-complete requests past due by cutoff)')
print('Never submitted: Submission_Date is NaN (581 Pending + 31 Declined without date = 612)')

# Supplier prioritisation framework
ra_prior = ra.merge(sm[['Supplier_ID', 'Supplier_Criticality', 'Region', 'Industry_Category']], on='Supplier_ID', how='left')

def assign_priority_tier(row):
    score = row['Overall_Risk_Score']
    criticality = row['Supplier_Criticality']
    info_gaps = row['Information_Gap_Count']
    max_overdue = row['Maximum_Overdue_Days']

    if score >= 70 and criticality == 'High' and (info_gaps >= 2 or max_overdue > 60):
        return 'Tier 1 - Critical'
    elif score >= 70 or (criticality == 'High' and info_gaps >= 1):
        return 'Tier 2 - High Priority'
    elif score >= 40 and (info_gaps >= 2 or max_overdue > 30):
        return 'Tier 3 - Elevated'
    else:
        return 'Tier 4 - Standard'

ra_prior['Priority_Tier'] = ra_prior.apply(assign_priority_tier, axis=1)

tier_counts = ra_prior['Priority_Tier'].value_counts()
print('\nPriority tier distribution:')
print(tier_counts)

# Show Tier 1 and 2 suppliers
tier12 = ra_prior[ra_prior['Priority_Tier'].isin(['Tier 1 - Critical', 'Tier 2 - High Priority'])]
print(f'\nTier 1 + Tier 2 suppliers: {len(tier12)}')
print(tier12[['Supplier_ID', 'Overall_Risk_Score', 'Supplier_Criticality', 'Information_Gap_Count', 'Maximum_Overdue_Days', 'Priority_Tier']].sort_values('Overall_Risk_Score', ascending=False).head(20).to_string(index=False))

# Export comparison datasets
export_cols = ['Supplier_ID', 'Overall_Risk_Score', 'Risk_Category',
             'Criticality_Score', 'Information_Gap_Score', 'Overdue_Severity_Score', 'Business_Exposure_Score']

for name in scenarios.keys():
    export_cols.extend([f'Risk_Score_{name}', f'Risk_Category_{name}', f'Rank_{name}'])

comparison_df = ra[export_cols].copy()
comparison_df['Rank_Change_Criticality_Emphasis'] = comparison_df['Rank_Criticality_Emphasis'] - comparison_df['Rank_Original']
comparison_df['Rank_Change_Info_Gap_Emphasis'] = comparison_df['Rank_Info_Gap_Emphasis'] - comparison_df['Rank_Original']

reports_dir = PROJECT_ROOT / 'reports'
comparison_df.to_csv(reports_dir / 'supplier_scenario_comparison.csv', index=False)
print(f'\nSaved supplier scenario comparison: {len(comparison_df)} rows')

cat_df.to_csv(reports_dir / 'scenario_category_comparison.csv')
print('Saved scenario category comparison')

priority_export = ra_prior[['Supplier_ID', 'Overall_Risk_Score', 'Risk_Category',
                            'Supplier_Criticality', 'Information_Gap_Count', 'Maximum_Overdue_Days',
                            'Priority_Tier']].copy()
priority_export.to_csv(reports_dir / 'supplier_priority_tiers.csv', index=False)
print('Saved supplier priority tiers')

# Final checks
check('Integrity', 'All 800 suppliers present in all scenarios', len(ra) == 800)
check('Integrity', 'No missing risk scores', ra[[f'Risk_Score_{name}' for name in scenarios.keys()]].notna().all().all())
check('Integrity', 'Categories assigned for all scenarios', ra[[f'Risk_Category_{name}' for name in scenarios.keys()]].notna().all().all())
check('Integrity', 'Ranks assigned for all scenarios', ra[[f'Rank_{name}' for name in scenarios.keys()]].notna().all().all())
check('Integrity', 'Workbook unchanged (SHA-256 identical)', sha256(WORKBOOK) == HASH_AT_START)

summary = pd.DataFrame(checks, columns=['Area', 'Check', 'Passed', 'Detail'])
print(f'\n{summary.Passed.sum()} / {len(summary)} checks passed')
print(summary.groupby('Area').Passed.agg(['sum', 'count']))

failed = summary[~summary.Passed]
if not failed.empty:
    raise AssertionError(f'Failed checks:\n{failed.to_string()}')

print('\n=== ALL CHECKS PASSED ===')
