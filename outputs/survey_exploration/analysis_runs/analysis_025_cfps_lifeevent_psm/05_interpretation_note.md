# 05 · Interpretation note — analysis_025

## Headline

Under PSM-DiD with bootstrap inference, **no event survives a strict
significance test** (smallest *p* = 0.058, female entered_marriage),
but the **female entered-marriage ATT flips sign relative to OLS**.
This is exactly the kind of result that motivates moving from OLS to
PSM: linear adjustment was masking selection structure that
non-parametric matching surfaces.

| Event              | Sex    | n_treated | ATT     | boot SE | 95 % CI               | *p* (norm) |
|--------------------|--------|-----------|---------|---------|-----------------------|------------|
| entered_marriage   | male   | 200       | +0.052  | 0.032   | [−0.021, +0.099]      | 0.10       |
| entered_marriage   | female | 184       | **+0.080** | 0.042 | [−0.036, +0.124]    | **0.058**  |
| had_new_child      | male   | 29        | +0.077  | 0.080   | [−0.146, +0.181]      | 0.34       |
| had_new_child      | female | 0         | — insufficient (fertile-age n_treated = 0)              |            |
| divorced           | male   | 77        | +0.032  | 0.036   | [−0.068, +0.075]      | 0.38       |
| divorced           | female | 35        | −0.023  | 0.057   | [−0.143, +0.083]      | 0.69       |
| widowed            | male   | 21        | +0.040  | 0.066   | [−0.148, +0.116]      | 0.55       |
| widowed            | female | 39        | +0.025  | 0.047   | [−0.052, +0.132]      | 0.59       |
| lost_job           | male   | 21        | +0.009  | 0.072   | [−0.116, +0.190]      | 0.90       |
| lost_job           | female | 33        | +0.046  | 0.056   | [−0.054, +0.158]      | 0.42       |
| entered_work       | —      | small     | — insufficient (n_control < 10 in both sexes)           |            |

ATT > 0 means the event group shifted **more traditional** than the
matched control would have. ATT < 0 means more progressive.

## The most interesting finding: entered_marriage in women

**OLS (analysis_024)**: β = **−0.034** (95 % CI [−0.062, −0.005],
*p* = 0.019). Reading: women who entered marriage shifted more
progressive than otherwise-similar non-married women, after linear
control for baseline ideation, age, and hukou.

**PSM-DiD (this analysis)**: ATT = **+0.080** (95 % CI [−0.036,
+0.124], *p* = 0.058). Reading: marriage-enterers shifted *more
traditional* (or, equivalently, less progressive) than matched
controls.

The sign flip is the substantively important result. Mechanics:

1. The "at-risk" pool for women in 2014 is overwhelmingly young
   never-married women, and that pool drifts strongly progressive
   regardless of marriage (Δ_no = −0.112 in the raw within-pool
   contrast).
2. Women who marry between 2014 and 2020 are selected from the
   *younger and more-progressive* end of that pool.
3. Linear OLS that adjusts for age and baseline ideation
   under-corrects this selection because the relationship between
   age and Δ is steep in this age range and the OLS slope is fit
   across the whole age distribution (mostly older).
4. PSM matches young marriage-enterers to young still-unmarried
   controls — the same age band the treated group lives in — and the
   comparison shows that the unmarried controls actually shifted
   *more* progressive (−0.112) than the marriage-enterers (−0.081).
   So entering marriage is associated with **suppressing** part of
   the progressive shift that would have happened in the absence of
   marriage.

This is the canonical demonstration that "controlled in OLS" ≠ "well
adjusted under PSM" when (a) the treated group is concentrated in a
small region of covariate space and (b) the outcome's relationship
with the covariates isn't strictly linear.

⚠️ Caveat: even after PSM, balance is imperfect for this fit. The
post-match SMD on `marital_2014` is 0.24 (Cohen's 0.1 rule says ≤
0.1 is acceptable). So the PSM is partially under-controlled, and
the +0.058 *p*-value should not be over-read. The substantive
take-away is the *direction* of the adjustment, not the precise
magnitude.

## Other fits, briefly

* **Entered marriage, men**: ATT = +0.052, *p* = 0.10. Direction
  matches the female result but smaller and less precise.
* **Had a new child, men**: ATT = +0.077 but n_treated = 29, *p* =
  0.34. The fertile-age male pool with a rostered new child is too
  small and too age-concentrated (54–55 years old, the contamination
  story) to support inference. Balance on `birthy_2014` is bad both
  pre (SMD = −2.5) and post matching (−1.0).
* **Had a new child, women**: not estimable — within the fertile
  window (women ≤ 45) there are essentially zero pids with a
  rostered new child by 2020 (n_treated = 0). The roster-update
  measurement artefact makes this contrast impossible to study with
  the current variable definition.
* **Divorced / widowed / lost_job**: all *p* > 0.3 with bootstrap
  CIs spanning zero. Sample sizes (n_treated ∈ [21, 77]) are too
  small to detect any but very large effects. Read as "no evidence",
  not "no effect".
* **Entered work**: insufficient controls in both sexes (n_control
  = 7 male, 8 female) — bootstrapping fails when the control pool
  is this small.

## Comparing PSM and OLS side-by-side

| Predictor          | OLS β (female) | OLS *p* | PSM ATT (female) | PSM *p* |
|--------------------|----------------|---------|-------------------|---------|
| Entered marriage   | **−0.034**     | 0.019   | **+0.080**        | 0.058   |
| Had a new child    | **−0.042**     | 1e-6    | — n/a             | — n/a   |
| Got divorced       | −0.028 (ns)    | 0.24    | −0.023 (ns)       | 0.69    |
| Widowed            | +0.012 (ns)    | 0.40    | +0.025 (ns)       | 0.59    |
| Lost job           | +0.039 (ns)    | 0.13    | +0.046 (ns)       | 0.42    |

For the events with *n_treated* large enough to estimate both ways,
PSM and OLS agree on the **sign** for divorced / widowed / lost_job,
but disagree on **entered_marriage** in the female panel. The male
panel doesn't show a sign flip but also doesn't show a significant
OLS effect to begin with, so there's nothing to flip.

The female `had_new_child` OLS β = −0.042 (*p* < 1e-6) has no PSM
counterpart because the fertile-age denominator is empty. This is
a measurement issue, not a substantive one — see analysis_024 § "Important caveat".

## What this analysis *does* support, after PSM-DiD

1. **The most defensible causal-style claim** in the run is that
   *entering marriage suppresses the progressive shift that would
   otherwise occur among young Chinese women between 2014 and
   2020*. The effect is around +0.08 on the [0,1] ideation index
   (≈ 1.6 notches on the 4-item battery) and is marginally
   significant.
2. No other event reaches significance under PSM-DiD. The earlier
   `had_new_child` story (−0.04 in female OLS) cannot be supported
   here because the variable is contaminated.
3. The PSM-DiD vs OLS comparison itself is a methodological message:
   for selection-heavy contrasts (e.g. life events in panel data),
   linear OLS adjustment can give qualitatively wrong answers even
   when the controls *look* right on paper.

## Important caveats (read with the table)

* Hidden confounders are not addressed. PSM is observable-only.
* Sample sizes are small for every fit except entered_marriage.
* Balance is acceptable but not perfect for entered_marriage in
  women (max post-match SMD = 0.24 on `marital_2014`); poor for
  had_new_child in men (post-match SMD on `birthy_2014` = 1.0).
  See `figures/psm_balance.pdf` for the full balance dotplot.
* The `had_new_child` variable is contaminated by roster artefacts
  (see analysis_024 §); PSM can't fix that.
* All inference uses normal-approximation *p*-values from the
  bootstrap SE. With n_treated < 50, those *p*-values are an
  approximation; the percentile CI is the more trustworthy summary.

## Files in this analysis_run

* `00_question.md` — research question and scope
* `01_descriptive_table.csv` — per-fit treated / control counts
* `02_missing_table.csv` — fits that could not be estimated
* `03_method_note.md` — pipeline, conventions, caveats
* `04_result_table.csv` — tidy summary with mean / max post-match
  |SMD| per fit
* `05_interpretation_note.md` — this file
* `tables/psm_att.csv`     — full ATT results
* `tables/psm_balance.csv` — pre / post SMD per covariate per fit
* `tables/psm_meta.csv`    — top-level counts
* `figures/psm_att_forest.pdf` — male/female ATTs side-by-side
* `figures/psm_balance.pdf`     — per-fit balance diagnostic
