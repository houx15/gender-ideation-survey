# 00 · Research question — analysis_036

## SPEC anchor

Do the individual-level ideation → outcome correlations found in CFPS
(analyses 026 / 027 / 028) replicate in CGSS — a different, larger,
nationally-fielded repeated cross-section with 8 waves (2010–2023)?

CGSS has no household structure and no panel pid, so we can only
**replicate the individual-level cross-sectional correlations**. The
couple analysis (029), the parent–child runs (033 / 034 / 035), and the
panel PSM-DiD designs (025 / 030 / 031 / 032) cannot be reproduced
here.

## Outcomes (mapped from CFPS findings)

| Outcome | CFPS analysis | CGSS variable | Waves with the outcome |
|---|---|---|---|
| `ever_married` | 026 | a69 | all 8 |
| `age_at_first_marriage` | 026 | a70 − birth year | all 8 |
| `num_children` | 026 | a681 + a682 | 7/8 (no 2021) |
| `ideal_children` | 026 | a371 | 6/8 (no 2012, 2013) |
| `marriage_satisfaction` | 026 | d31 (reversed) | 3/8 (2015, 2017, 2021) |
| `log_personal_income` | 027 | log(a8a + 1) | all 8 |
| `employed` | 027 | a58 ∈ {1,2,3} | all 8 |
| `weekly_hours` | 027 | a53a (employed only) | all 8 |
| `mgmt_activity` | 027 | a59f ∈ {1,2} (employed only) | all 8 |
| `soe_indicator` | 027 | a59k ∈ {1,2} (employed only) — 编制 proxy | all 8 |
| `edu_yrs` | 028 | a7a → years via CGSS map | all 8 |

## Design

Pooled across all available waves with the outcome present:

```
outcome ~ ideation + female + ideation × female
        + birth_year_c + urban_hukou + edu_yrs + log_income
        + wave fixed effects
```

OLS-HC1 robust standard errors. We avoid putting the outcome on the
RHS (e.g. when outcome = `log_income`, the income control is dropped).
Outcomes that are conditional on employment or marriage are gated:
work-side outcomes restrict to currently-employed respondents
(`employed == 1`); `age_at_first_marriage` and `marriage_sat` restrict
to ever-married respondents.

Stratified replicates: `male` and `female` subsamples, dropping the
`female` and `ideation × female` terms.

## Sample

Pooled CGSS N ≈ 86,300 with ideation, sex, and birth-year all
non-missing. Per-outcome N varies with wave coverage and gating.

## Caveats

* **Cross-sectional**: simultaneity / reverse causation between
  ideation and life-course outcomes (e.g. having children may
  retraditionalize ideation, not the other way round).
* **Wave heterogeneity**: outcomes that are only in a subset of waves
  (marriage satisfaction, ideal children) have far less power than
  the all-wave outcomes; reported effects pool over the wave fixed
  effects.
* **SOE / 编制 proxy is approximate**: a59k state-or-collective
  ownership over-counts the strictly-defined establishment payroll
  (编制), but the gradient is informative.
* **No couple or family-member data**: spouse-side variables (a72,
  a75a) are NOT used here; couple-analysis is left to CFPS (029).

## Files

`scripts/run.py`, `00_question.md`, `01_descriptive_table.csv`,
`02_missing_table.csv`, `03_method_note.md`, `04_result_table.csv`,
`05_interpretation_note.md`, `figures/*.pdf`.
