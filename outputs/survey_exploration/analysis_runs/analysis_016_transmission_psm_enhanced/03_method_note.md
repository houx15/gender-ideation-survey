# analysis_016 — Method note

## Sample
CFPS 2014 & 2020 children linked to both parents (`cfps_linkage.attach_parents`, tested),
both parents' ideation valid. Treatment/control = top/bottom tertile of parent-mean
ideation (middle third dropped). Specs: all-ages base, all-ages +urban, formative 16–30 +urban.

## Variables and coding
- ideation index: `ideation_lib`, [0,1], 1 = most traditional.
- `parent_mean_edu`: mean of mother & father years of schooling (`clean_continuous` 0–22).
- `urban`: `urban14`/`urban20` (0 = 乡村, 1 = 城镇), `clean_continuous(0,1)` (−9 etc → NaN).
- child `age` (formative window 16–30), child `female`.

## Method
- `matching.psm_att` (tested): logit propensity for treatment on covariates, NN match with
  replacement, ATT + paired-t.
- `matching.psm_att_boot` (tested): **bootstrap** (n=300) — resample rows, re-match, re-estimate;
  SE = SD of bootstrap ATTs; p from normal approx; 2.5/97.5 percentile CI. This is the honest
  inference (the paired-t SE understates uncertainty under matching-with-replacement).

## Interpretation bounds
- "Transmission net of parent education + urban/rural" — **not** a clean causal effect:
  shared environment, neighbourhood, genetic correlation, and co-residence selection remain.
- Tertile dichotomisation discards the middle third and a continuous construct.
- Bootstrap resamples rows (not the matching structure exactly) → approximate but far more
  honest than paired-t.
- Cross-sectional; no survey weights; province/region not yet used.

## Next steps
Add family SES (from CFPS family file) and region to the match; sibling/family fixed effects;
caliper sensitivity; survey weights; then (later) the provincial ideology climate.
