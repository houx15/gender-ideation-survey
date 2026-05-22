# analysis_021 — Method note

## Sample
Eight CGSS waves pooled (2010–2023, excl. 2011). Birth-year variable per wave:
`a3a` (2010/12/13/23), `a301` (2015), `a31` (2017/18), `A3_1` (2021); `clean_continuous`
to [1920, 2007]. Gender via `ideation_lib` (female=1 from a2/A2==2). Pooled N = 86,318.

## Method
`stats_helpers.ols` (tested), classical SEs. Wave fixed effects (dummies, first wave
dropped) absorb wave-level differences (period + design changes incl. the 2023 split-ballot).
`decade_c = (birth_year − 1970)/10`. Descriptive gender gap computed within decade cohorts.

## Interpretation bounds
- Pooled cross-sections cannot separate age, period, and cohort; with 8 waves and wave FE
  this is a stronger cohort *description* than CFPS but still not a full APC decomposition.
- No survey weights (sample, not population); classical SEs ignore CGSS clustering.
- CGSS 2023 ideation block is a split-ballot sub-module (smaller effective N that wave) —
  absorbed by the wave FE.
- a421–a425 index reliability is modest (analysis_001).

## Next steps
Formal APC model; survey weights + clustered SEs; replicate by urban/rural; compare the
cohort slope to CFPS for cross-survey consistency (levels not comparable, slopes are).
