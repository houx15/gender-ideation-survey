# analysis_006 — Method note

## Sample
CFPS 2014 (N=29,765) / 2020 (N=21,404) adults with ≥1 valid ideation item and valid
years of schooling (coverage ≈94%/94%; see `02_missing_table.csv`).

## Variables and coding
- **ideation index** (outcome): `ideation_lib`, [0,1], 1 = most traditional.
- **eduy**: `cfps2014eduy` / `cfps2020eduy` (completed years of schooling),
  `clean_continuous` to [0,22] (negatives = missing codes → NaN).
- **edu_group** (descriptive): none/primary/lower-sec/upper-sec/college/postgrad cut
  at 0/6/9/12/16 years.
- **female**: 1 = woman; controls `age_c=(age−40)/10`, `age_c2`.

## Method
OLS `ideation ~ eduy + female + eduy×female + age + age²`, per wave; classical SEs;
no weights. The interaction tests whether schooling's egalitarian association is
stronger for women.

## Interpretation bounds
- Even with the education→attitude direction, this is observational: selection into
  education correlates with family background and unmeasured traits.
- `eduy` treats schooling as linear; the descriptive `edu_group` table shows the shape
  (the divergence is concentrated at college+).
- No weights; modest CFPS index reliability.

## Next steps
Replicate in CGSS (more waves, retrospective parent education available); add parental
background; spline for eduy; bring in CEPS for the adolescent education/science field
(SPEC 5.4) where attitudes and schooling are measured closer in time.
