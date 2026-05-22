# analysis_018 — Method note

## Sample (a fix worth noting)
**Real** multi-child families only: both parents must be in-sample (`pid_f>0 & pid_m>0`) with
valid ideation, so siblings genuinely share the same couple. An earlier version that built the
family key from raw parent-id pointers lumped all *unlinked* respondents into pseudo-families
(`-8_-8`/`0_0`), grossly inflating N and the ICC — corrected here. Final: ≥2 sampled siblings
per real couple; N ≈ 2,378 (2014) / 2,584 (2020), 1,091 / 1,195 families.

## Methods (tested helpers)
- **`stats_helpers.icc_oneway`**: one-way random-effects ICC on groups with ≥2 members
  (sibling resemblance). Residual ICC: regress child ideation on `parent_mean` (and
  + age + urban) via pooled OLS, take residuals, recompute ICC on the same children. The drop
  vs raw = share of sibling resemblance accounted for by measured parent ideology.
- **`stats_helpers.fe_ols`**: within-family (demeaned) OLS `ideation ~ female + age_c`,
  df = N − n_families − k. Coefficients identified only from within-sibship variation.

## Interpretation bounds
- ICC is a *variance share*, not causal; "parent ideology explains X% of sibling resemblance"
  means the measured index, net of nothing else — broader shared environment is in the rest.
- FE removes all family-level confounds but cannot speak to transmission magnitude (constant
  within family); it identifies the within-sibship **gender** and **age** gradients only.
- Multi-child, both-parent-linked, co-resident-biased sample; CFPS one-child-policy era means
  multi-child families are a minority (and selected — more rural/traditional). No weights.

## Next steps
Decompose ICC by urban/rural and cohort; sibling sex-composition effects; survey weights;
later, add provincial ideology climate as a between-family predictor.
