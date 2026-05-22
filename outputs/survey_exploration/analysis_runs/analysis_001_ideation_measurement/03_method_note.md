# analysis_001 — Method note

## Sample choice
All respondents with at least one valid item on the core battery. We do not require
complete cases for the index (mean of valid items), but `04_result_table.csv`
computes internal consistency on complete cases only (alpha needs complete rows).

## Variable choice
The **core comparable battery** is the set of agree/disagree gender-role items that
recur within each survey family. Richer one-off modules (CGSS 2012 ISSP block,
CGSS 2017 d18x gender-role block, CGSS 2015 c8x work-equality) are intentionally
excluded here to keep the index comparable across years; they are logged in
`tables/ideation_item_discovery.csv` for targeted future analyses.

## Coding
- Each raw Likert item → [0,1] via `ideation_lib.normalize_item`.
- `agree_code` records whether raw 1 or raw `scale_max` means "strongly agree"
  (ACWF agree=1; CFPS/CGSS agree=5). This is read from the actual value labels
  (see `03_value_label_audit.csv`), not assumed.
- Direction: "traditional" items → agreeing scores 1; "progressive" items
  (e.g., men should share housework, equal leadership) are reversed so 1 still = traditional.
- Missing: any raw value outside [1, scale_max] (negatives, 7/8/9/98/99, system-missing)
  → NaN before scoring. No imputation. See `04_missing_value_report.csv`.

## Gender coding
- CFPS: raw 0=female, 1=male → `female`=1 if raw 0.
- CGSS / ACWF 2000 / ACWF 2010 / ACWF 1990: 1=male, 2=female → `female`=1 if raw 2.
- `1` in `female` means the respondent is a woman.

## Methods
- **Internal consistency:** standardized Cronbach's alpha + mean inter-item
  correlation on the normalized items.
- **Distribution:** N, mean, SD, min, max of the index overall and by gender.
- No weights applied (this is a measurement/descriptive pass; design weights are
  catalogued in task-3 audit and should be added for population estimates).

## Interpretation bounds
- Alpha is sensitive to the number of items; CFPS has only 4 items, so a low alpha
  is partly mechanical.
- Cross-survey absolute levels are NOT comparable (different item counts/content);
  only within-survey trends and within-sample gender gaps are interpreted.

## Alternatives for next step
Factor analysis / IRT for dimensionality; weighted estimates; separate sub-indices
(family-role vs leadership vs housework) where item counts allow.
