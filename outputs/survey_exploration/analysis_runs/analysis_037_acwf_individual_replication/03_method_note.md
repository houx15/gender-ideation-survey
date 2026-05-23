# 03 · Method note — analysis_037

## Sample

3 ACWF waves (1990, 2000, 2010) pooled. Listwise filter on ideation,
female, birth-year non-missing.

Pooled N = **65,973** (female fraction 0.53, ideation mean 0.42).

## Variable construction

The ACWF-specific outcome helpers live in
`outputs/survey_exploration/scripts/acwf_outcomes.py` and are locked by
`tests/test_acwf_outcomes.py` (6 tests, all green).

| Outcome | Recipe | Waves |
|---|---|---|
| `wife_does_more_housework` | e8_c / F6B == 2 → 1; {1,3} → 0 | 2000, 2010 |
| `leadership_ever` | d4_a / E6A == 1 → 1; ==0 → 0; 7/9 → NaN | 2000, 2010 |
| `housework_hours_1990` | h_work clipped to [0,1080] min, then /60 to hr/day | 1990 |
| `first_marriage_age_1990` | w32 directly in years, clipped [15,50] | 1990 |
| `log_income` | log(personal_income + 1) | 1990, 2000, 2010 |
| `edu_yrs` | b6/b4_a/B3A via ACWF level-to-years map (rq51_helpers) | all 3 |
| `employed` | rq51_helpers.employed_indicator (per-wave codes) | all 3 |

`birthy`, `urban` (hukou, falling back to community type for 1990),
`edu_yrs`, `log_income`, `employed` are derived via
`rq51_helpers.*` and re-indexed against `load_recoded` row order.

## Models

```
outcome ~ ideation + female + ideation × female      (only stratum=all)
        + birth_year_c                                (= (birth_year − 1960) / 10)
        + urban
        + edu_yrs                                     (dropped if outcome = edu_yrs)
        + log_income                                  (dropped if outcome = log_income)
        + wave dummies (first present wave dropped)
```

Fit via `stats_helpers.ols_robust(..., kind="HC1")`. Zero-variance
regressors removed before fit (e.g., `female` in single-sex strata).
Strata: `all`, `male`, `female`.

Pooled waves per outcome:

* `wife_does_more_housework`, `leadership_ever`: 2000 + 2010 (with one
  wave dummy)
* `housework_hours_1990`, `first_marriage_age_1990`: 1990 single-wave
  (no wave dummies)
* `log_income`, `edu_yrs`, `employed`: all 3 waves (2 wave dummies)

## Caveats

* **Cross-sectional throughout**; ideation and outcomes measured at
  the same wave. No causal interpretation should be read into the
  coefficients.
* The wave fixed effect for 2-wave pooled outcomes is identified by
  the 2000–2010 contrast only.
* CFPS-equivalent multi-item ideation index in ACWF has reasonable
  α (1990: 0.64; 2010: 0.56) but the items are not the same as in
  CGSS or CFPS — so levels are not comparable across programs (slopes
  and directional pattern are).
* The 1990 `h_work` (minutes/day) has a heavy-tailed distribution
  suggesting some respondents reported other periodicities;
  clipping at 1080 min/day removes the worst cases but does not
  fully clean the measure.
* Multiple testing: 7 outcomes × 3 strata = 21 ideation cells.
  Substantive interpretation weights consistency over individual
  marginal p values.
