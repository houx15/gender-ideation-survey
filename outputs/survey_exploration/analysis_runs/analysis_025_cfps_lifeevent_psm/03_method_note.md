# 03 · Method note — analysis_025

## Pipeline

1. Load the panel produced by analysis_024
   (`tables/panel.parquet`). 20,100 pids × per-pid covariates.
2. Derive two helper columns:
   * `age_2014 = 2014 − birthy_2014`
   * `income_2014_log = log10(max(income_2014, 0) + 1)`
3. For each (event × sex), build the treatment frame:
   * Apply the at-risk mask (see `SPECS` in `scripts/run.py`).
   * Subset to `female == sex_val`.
   * Define `treat ∈ {0, 1}` from the event indicator.
   * Listwise-drop on `treat`, `delta_ideation`, and the covariates.
   * Skip the fit if `n_treated < 10` OR `n_control < 10`. Failed
     fits are recorded with `note = "insufficient sample"`.
4. ATT estimation: `matching.psm_att_boot(work, "treat",
   "delta_ideation", covs, n_boot=300, seed=0)`.
   * Inner estimator is nearest-neighbour PSM with replacement, no
     caliper. Propensity from logistic regression on standardised
     covariates.
   * Inference is bootstrap-SE-based (re-matches on each resample);
     CI is the 2.5 / 97.5 percentile of the bootstrap ATTs.
5. Balance: `matching.psm_diagnostic` returns matched-pair indices.
   We compute the standardised mean difference (SMD,
   `matching.standardised_mean_difference`) per covariate, pre and
   post matching.
6. Save:
   * `tables/psm_att.csv` — one row per fit
   * `tables/psm_balance.csv` — one row per (fit × covariate)
   * `tables/psm_meta.csv` — top-level counts
   * `figures/psm_att_forest.pdf` — events × sex forest
   * `figures/psm_balance.pdf` — per-fit |SMD| pre vs post dotplot

## Conventions

* All matching is **with replacement** — multiple treated units can
  share the same control, which is fine for ATT estimation.
* No caliper. With small treated groups (n_treated as low as 29 here)
  any caliper that bites tends to drop too many treated to leave a
  usable comparison. We report balance instead so the reader can see
  which fits matched well.
* `n_treated < 10 OR n_control < 10` is a hard floor. Below that the
  bootstrap variance estimate is unreliable.
* The outcome is Δideation, so this is PSM-DiD: the matching adjusts
  for **baseline** selection, and the Δ outcome absorbs every
  individual-fixed factor.

## Interpreting the ATT

* **ATT > 0** ⇒ the event group shifted *more traditional* than the
  matched control group would have under no treatment.
* **ATT < 0** ⇒ the event group shifted *more progressive*.

The "matched control group" is "respondents who looked
observationally identical at 2014 baseline but did not undergo the
event".

## Robustness checks not done here

* Caliper sweep (default 0.05, then 0.01) — re-runs of the same fits
  with different caliper widths.
* Multiple matches per treated unit (kNN with k > 1).
* Inverse-probability-of-treatment weighting (IPTW) as an alternative
  to one-to-one matching.

These are good follow-ups; for this run we stuck with the
analysis_024-aligned single-match baseline so the contrast with the
OLS coefficients is clean.

## Reproducibility

```
python3 outputs/survey_exploration/analysis_runs/analysis_024_cfps_ideation_change/scripts/run.py
# produces the panel.parquet that this analysis depends on
python3 outputs/survey_exploration/analysis_runs/analysis_025_cfps_lifeevent_psm/scripts/run.py
# fits all PSM-DiD specs
python3 -m pytest                          # all 107 tests pass
```
