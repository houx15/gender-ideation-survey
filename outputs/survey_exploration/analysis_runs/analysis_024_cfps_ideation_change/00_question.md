# analysis_024 — Who shifts ideology between CFPS 2014 and 2020?

## Origin

Supplementary analysis derived from RQ 5.1 (analysis_023). In the CFPS
2014→2020 panel, of 20,100 respondents present in both waves, 15,859 have
a computable change in the gender-ideation index, and 81.7 % of those (≈
13,000 pids) moved in one direction or the other by at least one notch of
the 4-item battery (|Δ| ≥ 0.05 on a [0,1] index). The question is **who
shifts, and which life events go with which direction of shift.**

## Research questions

1. **Who changes?** Conditional on observed change, is the shift
   patterned by gender, birth cohort, and rural / urban hukou?
2. **What life events go with change?** Within-individual, do the
   2014–2020 transitions in marital status, employment, household size,
   and number of co-rostered children predict the direction and
   magnitude of the ideological shift?

## Scope and caveats

* CFPS only — ACWF and CGSS lack genuine panel structure for the same
  respondents over time.
* The analysis is **exploratory**. We report effect sizes, classical and
  HC1 standard errors, and 95 % bootstrap CIs, but treat the patterns as
  hypothesis-generating, not causal. We have only two waves, no
  pre-treatment controls beyond baseline 2014 values, and the
  "treatments" (entering marriage, having a child, losing a job) are
  jointly determined with the outcome.
* Missing-code handling is the same defensive convention used in
  analysis_023: any of {-10, -9, -8, -2, -1, 0} → NaN. No silent zeros.

## Expected sample sizes

| Filter                                  | N      |
|-----------------------------------------|--------|
| pids in CFPS 2014 ∩ pids in CFPS 2020   | 20,100 |
| with a computable Δideation             | 15,859 |
| OLS sample (all controls non-missing)   | 10,318 |
