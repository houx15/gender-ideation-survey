# 05 — Measurement decisions

Decisions made while auditing and recoding the gender-ideation battery. Every
decision is backed by the audit tables in this folder; raw data was never modified.

## Core comparable battery (what we index)
| Survey | Years | Items | Scale | "Agree" pole |
|--------|-------|-------|-------|--------------|
| ACWF (妇女地位) | 1990 | w611–w618 (8) | 5-pt | raw **1** = agree |
| ACWF | 2000 | i3_a,b,c,d,e,g,h,i (8) | 4-pt | raw **1** = agree |
| ACWF | 2010 | J2A–J2I (9) | 4-pt | raw **1** = agree |
| CFPS | 2014, 2020 | qm1101–qm1104 (4) | 5-pt | raw **5** = agree |
| CGSS | 2010,12,13,15,17,18,23 | a421–a425 (5) | 5-pt | raw **5** = agree |
| CGSS | 2021 | A42_1–A42_5 (5) | 5-pt | raw **5** = agree |

The "agree" pole was read from the **actual value labels** in each file
(`03_value_label_audit.csv`), not assumed — e.g. CGSS `a421` 1=完全不同意…5=完全同意,
ACWF `w611` 1=非常同意…5=不同意.

## Direction and index convention
- Each item normalized to **[0,1] with 1 = most traditional**.
- Traditional items: agreeing → 1. Progressive items (men share housework, equal
  leadership, women no-less-capable, promote equality, child takes mother's surname) →
  reversed so agreeing → 0. Direction per item is in `02_variable_candidates.csv`.
- Respondent index = **mean of valid normalized items** (no imputation).
- This reproduces `surveys/processed/gender_ideation_by_year.csv` **exactly**
  (analysis_001 cross-check, diff = 0.0000), so the established methodology is preserved.

## Missing-value handling
Any raw value outside the valid Likert range [1, scale_max] → NaN before scoring:
negatives (−1/−2/−3/−8 "不知道/拒答/不适用"), 7/8/9, 98/99, and system-missing.
Per-item missing codes and counts are in `04_missing_value_report.csv`.

## Internal consistency (defensibility of a single index)
From analysis_001 `04_result_table.csv` (standardized Cronbach's α):
- ACWF 2000 α=0.71 (best); ACWF/CGSS mostly **0.56–0.66**.
- **CFPS α=0.37 (2014) / 0.51 (2020)** — only 4 items, weakest. Prefer single-item
  analyses in CFPS, or report the index with explicit caution.
- Mean inter-item r ≈ 0.11–0.26.

**Decision:** keep the mean index for within-survey trend/gap description, but
(a) never compare absolute levels across surveys, and (b) keep single-item versions
available for sensitivity, especially in CFPS.

## Bonus / non-core ideation content (logged, not yet indexed)
`tables/ideation_item_discovery.csv` flags richer one-off modules to mine later:
- CGSS 2012 ISSP block (m104, m105, m201, m202), 2015 work-equality (c81–c84),
  2017 gender-role/son-preference block (d181–d185, d193 传宗接代, d14 boy/girl preference).
- CFPS 2020 parent–child care variables (qf2xx/qf6xx/qf7xx) for division-of-labour.

## Gender coding
female=1/male=0. CFPS raw 0=female,1=male → female if 0. CGSS/ACWF 1=male,2=female →
female if 2. ACWF 1990 `b3` 1=male,2=female.

## Known data-structure notes
- **CGSS 2011 has no ideation module** (only a housework-help item) — excluded.
- **CGSS 2023 ideation block is a split-ballot sub-module** (~38% system-missing,
  effective N≈7,000) — usable but it is a sub-sample, not the full wave.
- CFPS valid coverage ≈79% (battery asked of age ≥16; M-module not-applicable below that).
