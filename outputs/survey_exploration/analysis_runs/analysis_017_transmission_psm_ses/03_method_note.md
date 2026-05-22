# analysis_017 — Method note

## Sample
CFPS 2014 children linked to both parents (`cfps_linkage.attach_parents`, tested), both
parents' ideation valid. Treatment/control = top/bottom tertile of parent-mean ideation.
N_treated ≈ 2,500 (all ages) / 2,000 (formative 16–30).

## Variables and coding
- ideation index: `ideation_lib`, [0,1], 1 = most traditional.
- `parent_mean_edu`: mean of mother & father years of schooling (`clean_continuous` 0–22).
- `urban`: `urban14` (0 乡村 / 1 城镇).
- **`parent_log_income`**: `log1p` of the mean of mother & father `p_income`
  (`clean_continuous` 0–1e7; **zeros kept** as real non-earners, negatives → NaN).
- child `age` (formative window 16–30), child `female`.

## Method
`matching.psm_att` (point + paired) and `matching.psm_att_boot` (n=300 bootstrap; SE = SD of
bootstrap ATTs, p normal-approx, percentile CI) — both tested. Specs add income on top of
the analysis_016 match to isolate the SES contribution.

## Interpretation bounds
- **Household income is unavailable** (no family file; 2020 lacks personal income), so SES is
  proxied by **parents' personal income + education + urban/rural** — an imperfect, individual-
  level proxy, not household income.
- Income is noisy (47% legitimate zeros; top-coding/brackets); `log1p` keeps zeros.
- Otherwise as analysis_016: not a clean causal effect (shared environment, genes, co-residence
  selection); tertile split; no weights; CFPS 2014 only (2020 income unavailable).

## Next steps
If a CFPS **family file** can be supplied, use household income/per-capita income directly;
family fixed effects; survey weights; then the provincial ideology climate.
