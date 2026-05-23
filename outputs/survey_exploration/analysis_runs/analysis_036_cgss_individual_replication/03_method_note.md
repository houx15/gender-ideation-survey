# 03 · Method note — analysis_036

## Sample

8 CGSS waves (2010, 2012, 2013, 2015, 2017, 2018, 2021, 2023), pooled.
Listwise filter: ideation, female, birth-year all non-missing.

Pooled N = **86,320** (female fraction 0.52, ideation mean 0.43).

## Variable construction

The CGSS-specific outcome helpers live in
`outputs/survey_exploration/scripts/cgss_outcomes.py` and are locked by
`tests/test_cgss_outcomes.py` (17 tests, all green). Brief recipes:

* **ever_married** — `a69 ∈ {3,4,5,6,7}` = 1; `{1,2}` = 0 (cohab counts
  as not-yet-formally-married); else NaN.
* **age_first_marriage** — `a70 − birth_year`, clipped to `[15, 50]`.
  `a70 = 0` (never married) and `a70 ≥ 9000` (missing sentinel) → NaN.
* **num_children** — `a681 + a682`, each clipped to `[0, 15]`, sum
  clipped to `[0, 15]`. 99 sentinel on either side → NaN.
* **ideal_children** — `a371`, clipped to `[0, 10]`. 99 → NaN.
* **marriage_sat** — `d31` REVERSED so high = more satisfied
  (matches CFPS qm801 in 026); 98 / 99 → NaN.
* **log_income** — `log(a8a + 1)` after stripping sentinels
  `a8a ≥ 9_999_996`.
* **employed** — from `rq51_helpers.employed_indicator`: `a58 ∈ {1,2,3}`
  = 1; `{4,5,6}` = 0.
* **weekly_hours** — `a53a` clipped to `[0, 168]`. Gated on
  `employed == 1`.
* **mgmt_activity** — `a59f ∈ {1,2}` = 1, `{3,4}` = 0. Gated.
* **soe_indicator** — `a59k ∈ {1,2}` (state or collective) = 1,
  `{3,4,5,6}` = 0. Gated. Proxy for 编制.
* **edu_yrs** — from `rq51_helpers.education_years` (CGSS a7a → years
  via the standard CGSS-A7A map).
* **urban** — hukou-based; `rq51_helpers.urban_indicator` (per CGSS
  wave codes; see rq51_helpers).

## Models

For each outcome × stratum:

```
outcome ~ ideation
        + female + ideation × female      (only in stratum = "all")
        + birth_year_c                    (= (birth_year − 1970) / 10)
        + urban
        + edu_yrs                         (dropped if outcome = edu_yrs)
        + log_income                      (dropped if outcome = log_income)
        + wave dummies (drop first present wave)
```

Inference: `ols_robust(..., kind="HC1")` from
`scripts/stats_helpers.py`. Zero-variance regressors (typically
`female` and `ideation × female` in single-sex strata) are dropped
defensively before fitting.

Gating:

* Work-side outcomes (`weekly_hours`, `mgmt_activity`,
  `soe_indicator`) restrict to `employed == 1`.
* `age_first_marriage` and `marriage_sat` restrict to
  `ever_married == 1`.

Strata: `all`, `male`, `female`. In single-sex strata the `female`
and `ideation × female` terms are dropped (no within-stratum variance).

## Output

* `01_descriptive_table.csv` — outcome means per wave.
* `02_missing_table.csv` — per-wave per-outcome n_have / pct_missing.
* `04_result_table.csv` — every coefficient × outcome × stratum
  (wave dummies suppressed).
* `figures/summary_forest_ideation_to_outcome.pdf` — single big forest
  with all outcomes × 3 strata.
* `figures/forest_{family,work,edu}.pdf` — per-group forests.

## Caveats

* Cross-sectional throughout; ideation and outcome are measured at
  the same wave. No causal interpretation should be read into the
  coefficients; they describe associations.
* Wave fixed effects absorb level changes across the 13-year span;
  they do NOT absorb the period × cohort interactions documented in
  023.
* The reduced wave coverage of `marriage_sat`, `ideal_children`,
  and (especially) `weekly_hours` in CGSS 2021/2023 means those
  effects pool across very different sample compositions.
* Multiple testing: 11 outcomes × 3 strata = 33 ideation-coefficient
  cells. The substantive interpretation weights consistency across
  cells and large absolute effects over individual marginal p
  values.
