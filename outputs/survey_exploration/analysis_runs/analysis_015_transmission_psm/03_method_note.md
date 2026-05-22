# analysis_015 — Method note

## Sample
Adult children linked to both parents (`cfps_linkage.attach_parents`, tested), both parents
with a valid ideation index. Parents' education attached the same way (`mother_eduy`,
`father_eduy`). N = 5,564 (2014) / 4,120 (2020).

## Variables
- ideation indices: `ideation_lib`, [0,1], 1 = most traditional.
- `parent_mean` = mean of mother & father ideation; `parent_mean_edu` = mean of their
  years of schooling (`clean_continuous` 0–22).
- child `female` = 1 woman; child `age` cleaned to [16,99].

## Methods
- **Correlations:** `scipy.stats.pearsonr` (r + two-sided p), overall and by child sex.
- **PSM:** `matching.psm_att` (tested). Treatment = parent_mean in the **top tertile**
  (traditional) vs **bottom tertile** (egalitarian); middle third dropped for a clean
  contrast. Logistic propensity on (parent_mean_edu, child age, child female), nearest-
  neighbour match with replacement, ATT = mean matched difference in child ideation,
  paired-t p-value. Naive (unmatched) difference reported for comparison.

## Interpretation bounds
- **Not full causal identification of transmission.** Matching on parent education + child
  demographics removes those confounders, but shared environment, neighbourhood, and
  genetic correlation remain; the estimate is "transmission net of parent education", not a
  clean causal effect.
- **Co-residence selection:** linked children are disproportionately co-resident, which can
  inflate parent-child concordance.
- PSM with replacement understates SEs (controls reused) → the (already tiny) p-values are
  optimistic; the effect is clearly non-zero but treat exact p as approximate.
- Tertile split discards the middle third and dichotomises a continuous construct.
- Cross-sectional; no survey weights.

## Next steps
Add region/urban-rural and family SES to the match; sibling/family fixed effects; caliper +
bootstrap SEs; restrict child age (e.g. 16–30) to focus on the formative window.
