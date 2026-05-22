# analysis_014 — Method note

## Method
`matching.psm_att` (tested): logistic propensity for `female` on the match covariates
(standardized), nearest-neighbour match with replacement, ATT = mean matched daughter−son
outcome difference, paired-t p-value. Naive (unmatched) girl−boy difference reported
alongside for comparison.

## Variables (tested coding in tests/test_ceps_outcomes.py)
- Outcomes: `expect_college_plus(ba18)`, `yes12(ba02)` tutoring, `log1p(ba03)` cost,
  `yes12(b11)` own desk, `b2201==4` near-daily homework help, `hours_hm` weekly chores.
- Match covariates: `steco_3c` (SES), `stmedu`, `stfedu`, `grade9`, number of siblings
  (`b0201`+`b0202`+`b0203`+`b0204`).

## Interpretation bounds — read before trusting the flipped signs
- **Child sex is quasi-random**, so the propensity model has little predictive power; PSM
  here effectively **reweights on family structure** (mainly sibship size and SES) rather
  than on a strong selection process. The matched estimates are therefore close to
  covariate-adjusted means and **sensitive to which covariates enter** (notably sibship size).
- Consequently: estimates that are stable between naive and PSM (the education-investment
  outcomes) are trustworthy; those that **flip** when sibship size is added (chores, desk)
  should be read as "the raw gap is confounded by family structure", not as a clean reversal.
- Greedy NN with replacement understates SEs (controls reused); treat p-values as approximate.
- Between-student, one child per family; no weights; one-child-policy cohort.

## Next steps
Sensitivity to the covariate set (with/without sibship size); caliper + bootstrap SEs;
add hukou/region; entropy-balancing or IPW as alternative estimators.
