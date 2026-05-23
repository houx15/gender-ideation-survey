# 03 · Method note — analysis_030

## Sample

CFPS panel, 2014 → 2020 (n_panel = 20 100). Restricted to
`employed_2020 == 1` and ISEI 2020 non-missing (n_at_risk ≈ 13 225).
After binarising the 2014 ideation and dropping the middle tertile:
n_treated (high-ideation 2014) ≈ 1 281, n_control (low-ideation 2014)
≈ 2 090 in the overall stratum.

## Variables

* **Treatment** — `treat`: 1 if `ideation_2014` ≥ 67th percentile of
  ideation_2014, 0 if ≤ 33rd percentile, NaN otherwise.
* **Outcome** — `isei_2020`: `qg303code_isei` (current main-job ISEI),
  cleaned to [10, 90].
* **Covariates** — `birthy_2014`, `edu_yrs_2014`, `urban_2014`
  (hukou-based 0/1), `log_income_2014` (= log1p(income_2014)),
  `employed_2014`.

## Methods

1. **Logit propensity** `treat ~ standardized covariates`, fit on the
   stratum's at-risk subsample.
2. **Nearest-neighbour matching** on propensity, with replacement,
   caliper = 0.20 (propensity units). Treated units outside caliper
   are dropped.
3. **Point ATT** via `matching.psm_att`.
4. **Bootstrap inference** via `matching.psm_att_boot`: 300 resamples,
   re-matching on each, bootstrap SE + percentile CI.
5. **Balance diagnostic** via `matching.standardised_mean_difference`
   pre / post matching, per covariate (`psm_balance.csv`).

## Stratification

`overall / male / female`. The female cell is the one where the
lagged OLS β in `analysis_027` was significant (β = −4.25, p = .035).

## Caveats

* **Selection on observables**. Anything unobserved that predicts
  both 2014 ideation and 2020 ISEI is not adjusted for. The PSM
  estimate is "the average effect among matched units, under the
  no-unobserved-confounder assumption".
* **No 2014 ISEI baseline** → cannot DiD. This is PSM on the level
  of 2020 ISEI given 2014 covariates (including ideation).
* **At-risk restriction**: ISEI is only collected for those employed
  in 2020. Selection on employment is upstream of the PSM. If the
  ideation→employment channel is itself non-null, the ISEI ATT among
  the employed is a **conditional** effect, not the average
  population effect.
* **Middle tertile dropped** for sharper contrast — standard "treatment
  dose" simplification for PSM with continuous exposure. Sensitivity
  to the cut would require additional fits (not done here).

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — raw mean ISEI by stratum × treatment
* `02_missing_table.csv`
* `04_result_table.csv` — = `tables/psm_att.csv`
* `tables/psm_balance.csv` — SMD pre / post per covariate per stratum
* `tables/psm_meta.csv` — top-level counts
* `figures/psm_att_forest.pdf` — ATT forest across strata
* `figures/psm_balance.pdf` — balance plot per stratum
