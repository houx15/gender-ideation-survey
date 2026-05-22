# analysis_022 — Method note

## Sample
Pooled CGSS 2010–2023 ever-married respondents. `age_marr = a70 − birth_year`, birth year
from the per-wave variable (a3a/a301/a31/A3_1), `clean_continuous` bounds: birth [1920,2007],
marriage year [1940,2023], age at first marriage [15,50] (drops the 9998 missing code and
implausible ages). N = 71,560.

## Method
`stats_helpers.ols` (tested), classical SEs, wave fixed effects. `decade_c=(birth−1970)/10`
controls birth cohort (both marriage age and ideology trend with cohort). Descriptive mean
age at first marriage by ideation tertile × gender.

## Interpretation bounds (the central issue)
- **Reverse time order:** ideation is measured ~decades after first marriage, so the causal
  arrow cannot run ideation→timing. The association reflects some mix of: marriage/marital
  life shaping later attitudes, stable selection (people who marry young differ), and cohort.
- The `decade_c` control and wave FE remove the cross-cohort trend, but the **within-cohort**
  association is still descriptive, not causal.
- A genuine **event-history/survival** analysis is not identifiable: it needs the attitude
  measured *before* (and ideally time-varying through) the at-risk period, which CGSS's single
  post-hoc measurement cannot provide.
- No survey weights; classical SEs ignore clustering; ever-married selection (never-married excluded).

## Next steps
A survey with attitudes measured *prior to* marriage (panel with youth baseline, e.g. a
CEPS-style follow-up into adulthood) would be needed for causal timing. Otherwise treat as
descriptive; add weights and clustered SEs.
