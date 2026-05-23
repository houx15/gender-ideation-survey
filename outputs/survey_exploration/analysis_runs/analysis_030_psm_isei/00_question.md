# 00 · Research question — analysis_030

## SPEC anchor

RQ 5.3 extension: **PSM strengthens the ISEI prestige finding from
analysis_027**.

`analysis_027` showed that for women, baseline ideation in 2014
predicts a 4.25-point lower ISEI (p = .035) on the lagged frame —
the cleanest directional signal in the work bucket. This run asks
whether that signal survives propensity-score matching, which
provides a second identification strategy under selection-on-
observables.

## Design

* **Treatment**: top-tertile vs bottom-tertile of `ideation_2014`.
  (Middle tertile dropped to sharpen the contrast — standard
  "treatment dose" simplification for PSM with continuous exposure.)
* **Outcome**: `isei_2020` (qg303code_isei, current main job).
* **At-risk pool**: panel members employed in 2020 with non-missing
  ISEI (CFPS 2020 only collects ISEI for the employed).
* **Covariates for matching**: `birthy_2014`, `edu_yrs_2014`,
  `urban_2014`, `log_income_2014`, `employed_2014`.

This is **PSM, not PSM-DiD**: ISEI is 2020-only, so we cannot
difference. The estimate is the ATT of being in the high-ideation
group on 2020 ISEI, among matched units.

## Methods

Mirroring `analysis_025`:

1. **Propensity score**: logistic of `treatment ~ covariates`
   (standardized), via `matching.psm_att`.
2. **Bootstrap inference**: 300 resamples, re-matching on each,
   bootstrap SE + percentile CI via `matching.psm_att_boot`.
3. **Balance diagnostic**: SMD pre/post matching per covariate via
   `matching.standardised_mean_difference` + `matching.psm_diagnostic`.

Per **(sex stratum)** — overall / male / female. The female cell is
the one where the lagged-OLS β was significant.

## Caveats

* PSM rests on selection-on-observables. Anything unmeasured that
  predicts both 2014 ideation and 2020 ISEI is not adjusted for.
* No 2014 baseline ISEI → cannot DiD. The ATT is on the 2020 *level*
  conditional on the 2014 covariates, not on the *change*.
* CFPS 2020 ISEI is only collected for `employed == 1`. Selection on
  employment is upstream; the at-risk filter conditions on it. PSM
  cannot fix selection on a variable that's not in the covariate set
  for ALL panel members.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv` (= `tables/psm_att.csv`),
`05_interpretation_note.md`, `tables/psm_balance.csv`,
`tables/psm_meta.csv`, `figures/*.pdf`.
