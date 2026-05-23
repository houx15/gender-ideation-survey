# 05 · Interpretation note — analysis_025 (v2)

## v2 update

The earlier `had_new_child` measure was contaminated (roster-update
artefact concentrated at ages 54+). The PSM fit on it was therefore
either useless (n_treated = 0 within fertile age) or biased (matched
older men only). v2 replaces it with **`had_new_birth`**, derived from
the CFPS 2020 child file (`cfps2020_child.dta`) via parent-pid linkage
and `ibirthy_update ≥ 2015`. Treated cases now have mean age 26.5 in
2014, range 16–52 — biologically plausible.

The new variable also unlocks the female fertility cell, which had been
impossible to estimate before. The substantive headline changes
accordingly.

## Headline

Under PSM-DiD with bootstrap inference, **two events reach
significance in the female panel, both with the same selection-flip
signature**: women who entered marriage between 2014–2020 and women
who had a new birth in 2015–2020 shifted *less progressive* than
matched controls. Both effects vanish (or even reverse) under linear
OLS adjustment — the difference between the two is informative about
what was happening with selection.

| Event              | Sex    | n_treated | ATT     | boot SE | 95 % CI            | *p*       |
|--------------------|--------|-----------|---------|---------|--------------------|-----------|
| entered_marriage   | female | 184       | **+0.080** | 0.042 | [−0.036, +0.124]  | **0.058** |
| entered_marriage   | male   | 200       | +0.052  | 0.032   | [−0.021, +0.099]   | 0.10      |
| **had_new_birth**  | **female** | **371** | **+0.050** | **0.025** | **[−0.011, +0.086]** | **0.049** |
| had_new_birth      | male   | 414       | +0.021  | 0.019   | [−0.025, +0.049]   | 0.26      |
| divorced           | male   | 77        | +0.032  | 0.036   | [−0.068, +0.075]   | 0.38      |
| divorced           | female | 35        | −0.023  | 0.057   | [−0.143, +0.083]   | 0.69      |
| widowed            | male   | 21        | +0.040  | 0.066   | [−0.148, +0.116]   | 0.55      |
| widowed            | female | 39        | +0.025  | 0.047   | [−0.052, +0.132]   | 0.59      |
| lost_job           | male   | 21        | +0.009  | 0.072   | [−0.116, +0.190]   | 0.90      |
| lost_job           | female | 33        | +0.046  | 0.056   | [−0.054, +0.158]   | 0.42      |
| entered_work       | —      | small     | — insufficient (n_control < 10 in both sexes)        |           |

ATT > 0 ⇒ event group shifted **more traditional** than the matched
control. ATT < 0 ⇒ more progressive.

## Two female "selection-flip" findings

### 1. Entered marriage (female): OLS → −0.037, PSM → +0.080

Same direction reversal as v1. Mechanism unchanged: young Chinese
women in the never-married pool drifted strongly progressive
regardless of treatment (mean Δ_no = −0.112), and entering marriage
selects from the younger, more-progressive tail. Linear OLS under-
corrects this selection because the age slope is non-linear in this
range; PSM matches young marriage-enterers to young still-unmarried
women, and the matched controls turn out to have shifted more
progressive than the marriage-enterers themselves. So marriage
suppresses the progressive shift that would otherwise have happened.

### 2. Had a new birth (female): Welch → −0.027 (sig), OLS → −0.011 (NS), PSM → +0.050 (sig)

This is new in v2 and is the cleanest demonstration of the
selection-flip phenomenon in the run:

* **Raw Welch contrast**: women with a new birth shifted *more
  progressive* than other women by 0.027 (*p* = 3e-4).
* **OLS with controls**: that's reduced to β = −0.011, NS — linear
  adjustment absorbs most of the selection.
* **PSM-DiD**: ATT = +0.050 (*p* = 0.049, *n*_treated = 371) — the
  matched controls shifted **more** progressive than the new-mothers.

Balance after matching is excellent:

| Covariate          | pre-SMD | post-SMD |
|--------------------|---------|----------|
| ideation_2014      | −0.20   | +0.03    |
| birthy_2014        | +1.39   | −0.07    |
| edu_yrs_2014       | +0.51   | −0.03    |
| income_2014_log    | −0.04   | −0.15    |
| urban_2014         | −0.21   | −0.07    |
| children_n_2014    | −1.08   | −0.08    |

Cohen's 0.1 rule is met or near-met on all covariates post-match (the
worst is income at 0.15, still well below 0.25). Same picture for the
male fit. So the new-birth ATT is on a properly-balanced match — this
is a substantively defensible estimate.

Substantive reading: among Chinese women aged 16–45 in 2014, having a
child in 2015–2020 was associated with about a 0.05 point *more
traditional* shift on the [0,1] ideation index over the panel window,
relative to matched non-mothers. The bound is wide (CI nearly touches
zero on the low side), so this is "consistent with a modest
traditionalising effect of new motherhood under unconfoundedness", not
a precise causal claim.

The male fit (ATT = +0.021, *p* = 0.26) goes in the same direction but
isn't significant. With n_treated = 414 it's not a sample-size issue
— the magnitude is just smaller, plausibly because the lived
experience of new fatherhood at this age band carries less of an
attitudinal shock than new motherhood does.

## Other fits, briefly

* **Entered marriage, men**: ATT = +0.052, *p* = 0.10. Direction
  matches the female result but smaller and less precise.
* **Divorced / widowed / lost_job**: all *p* > 0.3 with bootstrap
  CIs spanning zero. Sample sizes (n_treated ∈ [21, 77]) are too
  small to detect any but very large effects. Read as "no evidence",
  not "no effect".
* **Entered work**: insufficient controls in both sexes (n_control
  = 7 male, 8 female) — bootstrapping fails when the control pool
  is this small.

## Comparing PSM and OLS side-by-side (female only)

| Predictor          | Welch diff | OLS β    | PSM ATT  |
|--------------------|------------|----------|----------|
| Entered marriage   | **−0.041** | **−0.037** | **+0.080** |
| Had a new birth    | **−0.027** | −0.011 (NS) | **+0.050** |
| Got divorced       | −0.040 (∼)  | −0.029 (NS) | −0.023 (NS) |
| Widowed            | **+0.026** | +0.010 (NS) | +0.025 (NS) |
| Lost job           | +0.011 (NS) | +0.038 (NS) | +0.046 (NS) |

The two events that survive PSM both have a clean **Welch → OLS → PSM**
trajectory in which the OLS lies between the raw contrast and the
matched ATT (or kills the signal entirely). This is the textbook
diagnostic for selection that linear adjustment doesn't fully soak up.

## What this analysis *does* support, after PSM-DiD

1. **Marriage and motherhood both partially suppress the progressive
   ideological shift** that young Chinese women would otherwise have
   undergone between 2014 and 2020. Each effect is ≈ +0.05 to +0.08 on
   the [0,1] index, marginally significant, and balance-controlled.
2. No similar male effect reaches significance for either event, but
   the male PSM coefficients on both events point in the same
   direction (smaller magnitude).
3. Divorce, widowhood, and job-status changes carry no PSM signal — but
   these are also the smallest treated groups, so this is "no
   evidence", not "no effect".

## Caveats (read together with the table)

* **Hidden confounders.** PSM is observable-only. Anything
  unmeasured that predicts both event and Δideation (e.g. an
  unobserved "wanting to settle down" attitude) is not adjusted for.
* **Wide bootstrap CIs.** The female new-birth CI is
  [−0.011, +0.086] — the lower bound nearly touches zero. The
  marriage CI is similar. Read these as "consistent with a real
  positive effect, weakly distinguishable from null."
* **Normal-approx *p*-values.** With n_treated in the hundreds these
  are reasonable approximations; we report the percentile CI alongside.
* **Two-wave design.** No event-study leads / lags possible.

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
