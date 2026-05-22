# analysis_002 — Method note

## Sample
CFPS adult respondents with ≥1 valid ideation item, birth year in [1930, 2004],
and known gender. Birth-year coverage is high (92.6% in 2014, 87.5% in 2020);
final analysis N = 31,383 (2014) and 22,632 (2020). See `02_missing_table.csv`.

## Variables and coding
- **Index:** `ideation_lib` recoding, [0,1], 1 = most traditional (see analysis_001).
- **Birth year:** `cfps_birthy` (2014), `ibirthy` (2020). Values outside 1930–2004 → NaN.
- **Cohort (descriptives):** decade bins 1930–49, 50s, 60s, 70s, 80s, 1990–2004.
- **Cohort (model):** continuous `decade_c = (birthy − 1970)/10`, so the coefficient
  is the change in index per 10 years of later birth; the 1970 cohort is the reference.
- **female:** 1 = woman, 0 = man.

## Method
OLS: `index ~ decade_c + female + decade_c:female`, fit per wave by least squares
with classical (homoskedastic) standard errors computed from (X'X)⁻¹σ². This is an
exploratory association model, not a causal estimate.

## Why this method
A linear cohort term plus a gender interaction is the most parsimonious way to test
(a) whether later cohorts are less traditional and (b) whether the gender gap itself
shifts across cohorts. Decade-binned descriptives accompany it so non-linearity is visible.

## Interpretation bounds
- No survey weights (sample, not population, estimates).
- Classical SEs; heteroskedasticity-robust SEs are a sensible next step.
- Period vs cohort cannot be separated with two waves; this is a cohort *description*,
  not an age-period-cohort decomposition.
- CFPS index reliability is modest (analysis_001), so read magnitudes as approximate.

## Alternatives for next step
Pooled APC-style model across CGSS years (more time points); robust/clustered SEs;
spline or factor-by-cohort terms; replicate in CGSS to check robustness.
