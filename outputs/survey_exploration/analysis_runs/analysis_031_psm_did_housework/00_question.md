# 00 · Research question — analysis_031

## SPEC anchor

RQ 5.2 individual extension: **PSM-DiD strengthens the housework
finding from `analysis_026`**.

`analysis_026 v2` showed that for women, baseline ideation in 2014
predicts a 0.50 hr/day rise in housework on the lagged frame
(β = +0.50, p = .085, marginal) — the only family-domain outcome to
survive the lagged frame on the female side. This run asks whether
that signal survives PSM-DiD, with the housework_2014 baseline used
as the DiD pre-period.

## Design

* **Treatment**: top-tertile vs bottom-tertile of `ideation_2014`.
* **Outcome**: `Δhousework = housework_2020 − housework_2014`
  (so this is genuine PSM-DiD, not PSM on a level).
* **At-risk pool**: panel members with both `housework_2014` and
  `housework_2020` non-missing.
* **Covariates for matching**: `birthy_2014`, `edu_yrs_2014`,
  `urban_2014`, `log_income_2014`, `employed_2014`,
  `marital_2014`, `children_n_2014` (extra family-context covariates
  since the outcome is housework).

## Methods

Identical pipeline to `analysis_025`:

1. Logit propensity score
2. Nearest-neighbour matching with caliper = 0.2
3. Bootstrap ATT (300 resamples)
4. SMD pre / post balance diagnostic

Per **(sex stratum)** — overall / male / female. Female is the
expected-signal cell.

## Caveats

* PSM on observables. The covariate set is the **same as 030** plus
  `marital_2014` and `children_n_2014` — important because housework
  time is strongly determined by life-stage (married + with kids do
  more).
* Δhousework can be negative (people housework less in 2020 than 2014).
  The PSM ATT estimates the average effect among matched units; signs
  read normally.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv` (= `tables/psm_att.csv`),
`05_interpretation_note.md`, `tables/psm_balance.csv`,
`tables/psm_meta.csv`, `figures/*.pdf`.
