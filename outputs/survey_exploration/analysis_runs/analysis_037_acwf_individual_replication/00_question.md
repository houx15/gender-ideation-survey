# 00 · Research question — analysis_037

## SPEC anchor

Do the individual-level ideation → outcome correlations from CFPS
(analyses 026 / 027 / 028) replicate in the **ACWF (中国妇女地位调查)**
repeated cross-sections — and does ACWF add outcomes that CFPS / CGSS
do not directly measure?

## ACWF coverage of the dissertation's outcomes

ACWF (1990 / 2000 / 2010) is a 3-wave repeated cross-section. Like
CGSS, it has no panel pid and no household structure, so only
**individual-level cross-sectional correlations** can be replicated.

ACWF's *unique* contribution beyond CFPS and CGSS is its directly
asked household-division-of-labour question:

| Outcome | ACWF variable(s) | Note |
|---|---|---|
| `wife_does_more_housework` | e8_c (2000), F6B (2010) | Categorical "in the couple, who does more housework"; NOT directly asked in CFPS or CGSS in this form |
| `leadership_ever` | d4_a (2000), E6A (2010) | "have you ever held a leadership / management position"; comparable to but distinct from CGSS a59f current-mgmt |
| `housework_hours_1990` | h_work (1990) | Minutes/day → hours/day (raw measure; only available in 1990 wave) |
| `first_marriage_age_1990` | w32 (1990) | Direct self-report of age at first marriage (only 1990) |
| `log_income` | w151/c18_a/C18AA | Cf. CGSS a8a |
| `edu_yrs` | b6/b4_a/B3A → years | Cf. CGSS a7a |
| `employed` | b7/c1_a/C1A | Cf. CGSS a58 |

## Design

Per outcome, with the waves that have the outcome present:

```
outcome ~ ideation + female + ideation × female
        + birth_year_c + urban + edu_yrs + log_income
        + wave fixed effects
```

OLS-HC1. Stratified by sex (all / male / female). Same template as
analysis_036.

## Caveats

* **Cross-sectional throughout**; ideation and outcome contemporaneous.
* **Cohort range is narrow**: ACWF's youngest cohort in its latest
  wave (2010) is roughly 1990-born, ~age 20. CFPS and CGSS reach
  into the 1990s and 2000s cohorts at adult ages.
* **ACWF 1990 ideation α** is 0.64; ACWF 2000 α not directly checked
  here; CFPS 2014 α is 0.37. So effect-size comparison across surveys
  should be done in ratio / direction terms, not absolute β.
* `wife_does_more_housework` is the **respondent's own report** of
  who does more in their own couple — no separate husband-side
  measurement. Selection-into-couples and self-serving reporting are
  both plausible.
* The 1990 housework variable is in **minutes/day**; we clip to
  ≤ 1080 min (18 h) and convert. The raw distribution has a heavy
  upper-end tail that suggests some respondents reported weekly
  totals — caveat for the 1990-only fit.

## Files

`scripts/run.py`, `00_question.md`, `01_descriptive_table.csv`,
`02_missing_table.csv`, `03_method_note.md`, `04_result_table.csv`,
`05_interpretation_note.md`, `figures/forest_ideation_to_outcome_acwf.pdf`.
