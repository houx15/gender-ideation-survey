# analysis_013 — Method note

## Designs and helpers (all tested)
- **Rung 2:** `cfps_linkage.family_gender_gap` → per mixed-gender family,
  mean(daughters) − mean(sons); regressed on parent ideology + age gap via
  `stats_helpers.ols` (now returns p-values). Families: 129–503 depending on outcome/age.
- **Rung 3:** `matching.psm_att` — logistic propensity for `female` on (age, parent
  ideology), nearest-neighbour match (with replacement), ATT = mean matched daughter−son
  difference, paired-t p-value. Run overall and within parent-ideology strata (median split).
- **Moderation test:** `outcome ~ female + parent_mean + female×parent_mean + age (+age²)`;
  the `female×parent_mean` coefficient is the moderation effect with its p-value.

## Coding
- ideation index (`ideation_lib`), parent_mean = mean of both parents; female = 1 woman.
- eduy (`cfps20XXeduy`, age ≥ 25), housework (`qq9010`/`qq9010n`), `clean_continuous`-bounded.

## Interpretation bounds
- **Linked-sample / co-residence selection persists** in rungs 3 and the interaction
  (children must be linked to both parents → co-resident-biased). The within-family rung 2
  removes family-level confounds but is underpowered.
- PSM covariates are limited (age, parent ideology); child sex is quasi-random, which helps,
  but unobserved family factors correlated with sibling sex composition remain.
- Stratified PSM ATTs test the gap *within* a stratum; the **moderation OLS** is the proper
  test of whether the gap *differs* by ideology.
- Cross-sectional; classical SEs; no survey weights.

## Next steps
Add richer match covariates (parent education, region, sibship size); cluster SEs by family;
weights; pool waves; replicate the housework moderation with CGSS time-use.
