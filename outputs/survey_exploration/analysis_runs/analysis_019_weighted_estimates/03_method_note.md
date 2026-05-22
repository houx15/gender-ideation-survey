# analysis_019 — Method note

## Variables
- ideation index: `ideation_lib`, [0,1], 1 = most traditional.
- weight: `rswt_natcs14` (2014, raw expansion weight, median ~26,700) /
  `rswt_natcs20n` (2020, standardized, median ~0.8). `clean_continuous` to drop ≤0.
- `female` = 1 woman; `parent_mean` = mean of both parents' ideation; `age_c = (age−30)/10`.

## Methods
- Weighted mean = Σwx/Σw.
- Weighted regressions: `stats_helpers.wls` (tested) — WLS point estimates with a
  heteroskedasticity-robust **sandwich** covariance, weights normalized to mean 1.
  Compared against unweighted `ols`.

## Interpretation bounds
- Cross-section weights make estimates representative of the adult population in each wave,
  but do **not** fix non-random *linkage* selection in the transmission sample (children
  linked to co-resident parents) — weighting and selection are different problems.
- Robust sandwich SEs ignore the CFPS clustered/stratified design (PSU clustering would
  widen SEs further); treat weighted p-values as a reasonable but not survey-exact inference.
- No design (PSU/strata) variables used.

## Next steps
Full survey design (PSU + strata) SEs if design variables are available; weighted PSM;
weighted within-family estimates.
