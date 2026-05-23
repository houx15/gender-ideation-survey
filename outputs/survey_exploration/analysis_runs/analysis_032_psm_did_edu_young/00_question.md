# 00 · Research question — analysis_032

## SPEC anchor

RQ 5.4 extension: **PSM-DiD strengthens the young-cohort Δ-edu finding
from `analysis_028 v2`**.

`analysis_028 v2` showed the cleanest directional signal in the
project: for young-cohort women (birthy_2014 ≥ 1990), baseline
ideation in 2014 predicts a −1.37 year change in education by 2020
(p = .006), conditional on 2014 edu and standard covariates. This run
asks whether that signal survives PSM-DiD — and unlike 030 / 031,
this is the cell where the OLS finding is **strong**, so PSM is
testing whether it survives matching rather than checking whether a
marginal OLS finding holds up.

## Design

* **Treatment**: top-tertile vs bottom-tertile of `ideation_2014`
  (middle dropped).
* **Outcome**: `delta_edu_yrs = edu_yrs_2020 − edu_yrs_2014`.
  (Δ is positive only for those still acquiring schooling between
  the waves; this is why young-cohort restriction matters.)
* **Sample restriction**: `birthy_2014 ≥ 1990` (age ≤ 24 in 2014).
* **At-risk pool**: both edu values non-missing AND in the young
  cohort.
* **Covariates for matching**: `birthy_2014`, `edu_yrs_2014`,
  `urban_2014`, `log_income_2014`, `household_n_2014`. **No
  `employed_2014`** — most young respondents in 2014 were still in
  school, so employment is mechanically determined and would absorb
  the variance.

## Methods

Identical to 025 / 030 / 031.

Per **(sex stratum)** — overall / male / female. Female is the
key cell.

## Caveats

* **Small sample** in this cell: panel young-cohort n ≈ 2 700;
  after tertile split + listwise on covariates, expect n_treated
  ≈ 250–350. Bootstrap CIs will be wide.
* **Δ-edu has limited variance** — most respondents are flat at 0.
  The signal lives in the small subset who acquired additional
  schooling between 2014 and 2020.
* PSM on observables.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv` (= `tables/psm_att.csv`),
`05_interpretation_note.md`, `tables/psm_balance.csv`,
`tables/psm_meta.csv`, `figures/*.pdf`.
