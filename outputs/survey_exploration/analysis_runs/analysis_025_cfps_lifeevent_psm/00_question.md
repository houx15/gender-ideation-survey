# analysis_025 — PSM-DiD on CFPS life events

## Origin

Direct follow-up to analysis_024 (RQ 5.1 supplement). The naïve and
OLS-adjusted contrasts there are vulnerable to selection on observable
baseline characteristics: women who entered marriage between 2014 and
2020 are systematically younger / more urban / more educated than
those who did not, and the OLS in analysis_024 only corrects for that
linearly. PSM corrects non-parametrically.

## Research question

For each 0→1 life event between CFPS 2014 and 2020, **what is the
average treatment effect on the treated (ATT) on Δideation, after
matching treated respondents to controls who looked identical at
baseline 2014?**

Stratified by sex (male / female), under the unconfoundedness
assumption (selection-on-observables, no hidden confounders).

## Why PSM is the right tool here

* Two-wave panel data; Δideation as the outcome already absorbs every
  time-invariant individual factor (cohort, sex, hukou, baseline
  personality). This is the DiD half.
* The remaining concern is selection into the event on **observable**
  baseline differences (e.g. women who marry are younger). PSM
  matches on those observables non-parametrically. This is the PSM
  half.
* Together → PSM-DiD, the workhorse of two-wave panel-event studies.

## What PSM cannot fix

1. **Hidden confounders.** If "wanting to marry" predicts both
   marriage and ideological shift, no observable-only design recovers
   the true causal effect.
2. **Measurement error in the event variable.** `had_new_child` is
   contaminated by roster artefacts at older ages (analysis_024 §
   "Important caveat"). PSM matches on what's measured; it cannot
   reconstitute the underlying biological event.
3. **Sample size.** Treated groups are small for several events; the
   bootstrap CIs are wide.

## Inputs

* `outputs/survey_exploration/analysis_runs/analysis_024_cfps_ideation_change/tables/panel.parquet`
  — the per-pid panel built by `cfps_panel.build_panel()`.
* Helper: `outputs/survey_exploration/scripts/matching.py`
  (`psm_att_boot`, `psm_diagnostic`, `standardised_mean_difference`).

## Events analysed (treated condition restricted to at-risk pool)

| Event              | At-risk pool (2014 state)                  | Treated (=1)                            |
|--------------------|--------------------------------------------|------------------------------------------|
| entered_marriage   | never-married OR cohab in 2014             | married in 2020                          |
| had_new_child      | fertile age (F≤45, M≤55) in 2014            | rostered child count grew by 2020        |
| divorced           | married OR cohab in 2014                   | divorced in 2020                         |
| widowed            | married OR cohab in 2014                   | widowed in 2020                          |
| lost_job           | employed in 2014                           | not employed in 2020                     |
| entered_work       | not employed in 2014                       | employed in 2020                         |

## Propensity covariates

Shared baseline: `ideation_2014`, `birthy_2014`, `edu_yrs_2014`,
`income_2014_log` (log10(income+1)), `urban_2014`.

Event-specific additions:
* marital events (entered_marriage, divorced, widowed): + `marital_2014`
* `had_new_child`: + `children_n_2014`
