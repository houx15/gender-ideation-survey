# 03 · Method note — analysis_031

## Sample

CFPS panel, 2014 → 2020 (n_panel = 20 100). Restricted to panel
members with both `housework_2014` and `housework_2020` non-missing
(n_at_risk = 12 767). After binarising the 2014 ideation and dropping
the middle tertile: n_treated (high) ≈ 1 125, n_control (low) ≈ 1 456
in the overall stratum.

## Variables

* **Treatment** — `treat`: 1 if `ideation_2014` ≥ 67th percentile of
  ideation_2014; 0 if ≤ 33rd; NaN otherwise.
* **Outcome** — `delta_housework = housework_2020 − housework_2014`
  (hr/day; genuine DiD).
* **Covariates** — `birthy_2014`, `edu_yrs_2014`, `urban_2014`,
  `log_income_2014`, `employed_2014`, `marital_2014`,
  `children_n_2014` (extra family-context covariates).

## Methods

Identical pipeline to `analysis_025` and `analysis_030`:
1. Logit propensity, standardized covariates.
2. NN matching, caliper = 0.20.
3. Bootstrap ATT: 300 resamples, percentile CI.
4. SMD balance diagnostic pre/post.

Stratified overall / male / female.

## Caveats

* PSM-DiD on observables. Unmeasured time-varying confounders (e.g.
  a job change, an elderly parent moving in) are not adjusted for.
* Housework time at the lower end has a floor (many men report ~ 0 hr).
  The Δ measure is on `[−24, +24]` but tightly bounded for most
  respondents — `mean(|Δ|) ~ 1 hr/day`, so ATTs on the order of
  0.1 are about 10 % of the typical absolute change.
* Caliper sensitivity not tested.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv`, `05_interpretation_note.md`,
`tables/psm_att.csv`, `tables/psm_balance.csv`, `tables/psm_meta.csv`,
`figures/psm_att_forest.pdf`, `figures/psm_balance.pdf`.
