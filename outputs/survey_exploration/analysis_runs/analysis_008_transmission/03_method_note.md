# analysis_008 — Method note

## Sample
Children (adult respondents, age ≥16) linked to **both** parents with
`cfps_linkage.attach_parents` (tested). Both parents must have a valid ideation index.
N = 5,564 (2014) / 4,120 (2020). Coverage attrition in `02_missing_table.csv`
(31,554 children → 6,316 father-linked / 7,191 mother-linked → 5,564 with both, 2014).

## Variables and coding
- All ideation indices: `ideation_lib`, [0,1], 1 = most traditional.
- `child_female`: 1 = daughter. Control `age_c=(age−30)/10`.
- Model A: `child ~ mother + father + child_female + age`.
- Model B: adds `mother×daughter`, `father×daughter` for same/cross-gender paths.

## Method
OLS (tested `stats_helpers.ols`), classical SEs, no weights. Plus the four raw
parent→child path correlations split by child gender (`01_descriptive_table.csv`).

## Interpretation bounds
- Linked parents are disproportionately **co-resident** → selection toward families
  that still live together; transmission estimates may be inflated.
- Cross-sectional, same-wave → cannot separate transmission from ongoing shared
  environment or child→parent influence.
- mother vs father coefficients are close; a **formal equality test** (joint covariance)
  is the needed next step before claiming one parent transmits more.
- No weights; modest CFPS index reliability.

## Next steps
Formal mother=father coefficient test; restrict to co-resident vs non-co-resident to
gauge the co-residence bias; add parent education/region; bring siblings in for
family fixed effects (SPEC 5.7 / sibling comparison).
