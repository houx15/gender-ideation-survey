# 03 · Method note — analysis_032

## Sample

CFPS panel, 2014 → 2020, restricted to young cohort (birthy_2014 ≥ 1990).
n_young_panel = 2 697; with treatment binary (top vs bottom ideation
tertile) = 1 783; Δedu_yrs non-missing = 2 607.

In the female stratum after listwise on all matching covariates:
n_treated ≈ 115, n_control ≈ 120.

## Variables

* **Treatment** — `treat`: 1 if `ideation_2014` ≥ 67th percentile (within
  this young-cohort frame); 0 if ≤ 33rd; NaN otherwise.
* **Outcome** — `delta_edu_yrs = edu_yrs_2020 − edu_yrs_2014`.
* **Covariates** — `birthy_2014`, `edu_yrs_2014`, `urban_2014`,
  `log_income_2014`, `household_n_2014`. **No `employed_2014`** —
  most young respondents in 2014 were still in school, so employment
  is mechanically determined.

## Methods

Identical pipeline to `analysis_025 / 030 / 031`:
1. Logit propensity, standardized covariates.
2. NN matching, caliper = 0.20.
3. Bootstrap ATT: 300 resamples, percentile CI.
4. SMD balance diagnostic pre/post.

Stratified overall / male / female.

## Caveats

* **Small sample** in the female cell (n_treated = 115). Bootstrap CI
  is wide.
* **Δedu_yrs is heavy-tailed at 0**: most respondents didn't acquire
  additional schooling in the 6-year window. The ATT estimates the
  mean Δ — pulled down by the small subset who *did* acquire schooling
  and where the ideation gradient is strongest.
* PSM on observables. Unmeasured family ideology, peer effects, region
  ideology are not adjusted for.
* `urban_2014` defined via hukou (qa301: 1 → 0 rural; 3 → 1 urban).
  The young cohort in 2014 may not yet have their adult hukou status
  finalised in some cases; treated as 2014 status here.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv` (= `tables/psm_att.csv`),
`05_interpretation_note.md`, `tables/psm_balance.csv`,
`tables/psm_meta.csv`, `figures/psm_att_forest.pdf`,
`figures/psm_balance.pdf`.
