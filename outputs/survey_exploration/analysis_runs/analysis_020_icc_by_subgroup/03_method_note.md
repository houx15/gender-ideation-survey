# analysis_020 — Method note

## Sample
Real multi-child families (both parents in-sample, `pid_f>0 & pid_m>0`, valid parent ideation;
≥2 sampled siblings) — same construction as analysis_018. Subgroups computed at the family
level: urban = family mean child-urban ≥ 0.5; older/younger sibship = family mean child age
≥ / < the median family-mean age. Subgroups reported only when ≥30 families.

## Method
`stats_helpers.icc_oneway` (tested) within each subgroup; residual ICC = ICC of residuals
from a pooled OLS of child ideation on `parent_mean`. Difference (raw − residual) / raw =
share of sibling resemblance accounted for by measured parent ideology.

## Interpretation bounds
- ICC is a variance share, not causal; subgroup ICCs are descriptive.
- "Cohort" is proxied by the family's mean child age — coarse, and confounded with parental
  age/period; not a true cohort design.
- Family-level urban assignment is approximate (uses the children's modal urban status).
- Multi-child families are a selected minority (one-child-policy era), more rural/traditional;
  subgroup Ns are moderate. No weights.

## Next steps
Decompose by parental cohort directly (needs parent birth year); urban×cohort cells; weights.
