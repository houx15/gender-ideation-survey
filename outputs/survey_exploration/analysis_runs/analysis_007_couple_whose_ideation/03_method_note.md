# analysis_007 — Method note

## Sample
CFPS 2014 married couples built with `cfps_linkage.build_couples` from `pid_s`
(tested: dedups reciprocal rows, drops out-of-sample spouses and same-sex pairs).
10,841 couples linked; 10,675 have both ideation indices and both housework hours
with a positive total (the `wife_share` denominator).

## Variables and coding
- **ideation**: `ideation_lib`, [0,1], 1 = most traditional. `wife_`/`husband_` assigned
  by the CFPS gender flag.
- **housework hours**: qq9010, `clean_continuous` to [0,24].
- **wife_share**: wife_hw / (wife_hw + husband_hw), defined only when the sum > 0.
- Controls: wife/husband age centered at 40 (per decade).

## Method
Three OLS models (tested `stats_helpers.ols`, classical SEs) each include BOTH spouses'
ideation. The comparison of interest is the wife- vs husband-ideation coefficient within
each model (`whose_ideation_comparison.csv`).

## Interpretation bounds
- Cross-sectional, co-measured → associational, not causal; reverse causation possible.
- Asymmetry is partly mechanical: wives do more housework on average (2.9 vs 1.5 hrs),
  so there is more variance to explain on the wife side.
- A formal test of coefficient equality (wife vs husband) needs the joint covariance;
  here we report point estimates + individual t-stats and flag the equality test as a
  next step.
- Couples skew co-resident; married-only; no weights; modest CFPS index reliability.

## Next steps
Seemingly-unrelated / stacked model with a formal wife=husband coefficient test;
add relative-resources controls (education, income) to separate ideology from bargaining
power; replicate with couple-linked time-use in CGSS.
