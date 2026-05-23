# 05 · Interpretation note — analysis_026 (v2)

> RQ 5.2 individual-level family practice, deep-dive replacement for
> `analysis_004_cfps_family_practice`. Reports cross-section + lagged
> fits side-by-side and stratifies every outcome by sex.

## v2 update (2026-05-23)

User-supplied five new family-domain variables. All available in CFPS 2020;
two also in 2014 (so two get a lagged frame).

| Variable | 2014 | 2020 | Lagged |
|---|---|---|---|
| `ideal_marriage_age` (qka201) | — | ✓ | — |
| `birth_intention_2y` (qka205) | — | ✓ | — |
| `marriage_sat` (qm801)        | ✓ | ✓ | ✓ |
| `cohab_experience` (eeb501)   | ✓ | ✓ | ✓ |
| `childcare_hours` (qq9013)    | — | ✓ | — |

Three findings worth flagging in v2:

1. **Ideal marriage age (2020): traditional → earlier ideal.** Overall
   β = **−1.45** (p = .005); male **−1.28** (p = .016); **female −1.94**
   (p = .0003). Bigger and tighter than the retrospective first-marriage-age
   contrast in v1, and goes in the same direction: a top-of-scale →
   bottom-of-scale ideation move shifts women's ideal marriage age by
   ~2 years earlier. This is the cleanest "ideology → marriage timing
   intention" gradient in the family bucket so far, and time-ordering is
   relatively clean since `qka201` is asked of unmarried respondents (so
   it's largely future-facing).

2. **Marriage satisfaction (2020): female-only effect, +0.48 (p < .001).**
   Among married women in 2020, traditional ideation is associated with
   marriage satisfaction roughly *half a Likert point* higher; among men,
   essentially flat (β = −0.08 n.s.). Consistent with a "traditional
   division-of-labour matches your expectations → you report higher
   satisfaction" reading for women. 2014 cross-section is null (no
   such gradient), so this is a 2020-specific finding worth corroborating
   in CGSS replication. **Lagged** β = +0.18 n.s. (panel n = 1 580 for
   women), so descriptive, not directional.

3. **Cohabitation experience (panel lagged): male β = +0.18 (p = .01).**
   Unexpected sign — would expect traditional men to *avoid* cohabitation.
   This is on a small sample (n = 354 men with non-missing baseline +
   2020 cohab), so I'd treat it as a oddity awaiting replication, not a
   substantive finding. Reported here because the data shows it, not
   because it confirms theory.

4. **Childcare hours (2020 only)**: all strata n.s. (β ≈ +0.07 male,
   +0.28 female, neither significant). Childcare time may simply be
   too determined by structural factors (presence of a young child,
   employment) for ideation to move in the cross-section.

5. **Birth intention next 2 yr**: small negative, all n.s. Most CFPS
   adults are past prime childbearing in 2020; a sample restricted to
   age 20–40 might be needed to see this.

v2 keeps every v1 result intact (see headline table below). Tables and
figures regenerated; the 11 v1 figures remain plus 6 new tertile-bar
figures (ideal_marriage_age, birth_intention, marriage_sat × 2 waves,
cohab_experience, childcare_hours).

## Headline

| Outcome | 2014 cross β (95 % CI) | 2020 cross β | Lagged β | Reading |
|---|---|---|---|---|
| **Currently married** | **+0.093** (.04 / .14) | **+0.106** | **−0.006 (n.s.)** | Concurrent association is robust and large in both waves; **vanishes** once we control for marital status at baseline → the link is not directional 2014 → 2020. |
| **Ideal children (2014)** | **+0.32** (.22 / .42) | (not asked) | (n/a) | Traditional ideation maps strongly onto larger desired family size, especially among men (β = +0.34) but also among women (+0.26). |
| **Housework hours/day** | overall **−0.25** (p .01) | overall +0.13 (n.s.) | overall +0.19 (n.s.) | The headline gender split: traditional women do **much more** housework (β = **+0.58** in both waves, **+0.50 marginal** in lagged), traditional men do **slightly less** in 2014 (−0.18) and nothing in 2020. |
| **First-marriage age** | small / wide CIs | small / wide CIs | (not estimated) | Descriptive only: traditional women married ≈ 1 year **earlier** (Welch d = −0.27 / −0.40, p ≈ .004 / .06), men no clear difference. *Ideation measured post-marriage* — not a causal claim. |

All β are on the [0, 1] ideation scale, so β = 0.10 means a 10 %-of-scale
shift in ideation associates with a unit change in the outcome.

## Outcome-by-outcome readings

### 1. Currently married (binary)

* Cross-section: β = +0.093 (2014) → +0.106 (2020) on a probability scale.
  Translating: moving from the most-progressive 5 % to the most-traditional
  5 % of the ideation distribution is associated with ~10 percentage points
  higher probability of currently being married.
* Sex-stratified: the effect is **larger for women** (β = +0.140 in 2014,
  +0.159 in 2020) than for men (+0.083 / +0.080). Confirmed by Welch d
  in `welch_tertile_diffs.csv`: female d = 0.32 / 0.42, male d = 0.28 / 0.42.
* **Lagged β = −0.006 (n.s.)**: when we add `currently_married_2014` to
  the RHS, ideation in 2014 carries no incremental information about
  marital status in 2020. This is consistent with two things:
  (i) most CFPS adults are stably married across the panel window, so
  variance is mostly absorbed by the baseline;
  (ii) the cross-section signal is not "ideation predicts later marriage"
  but "married people are more traditional now" — possibly because
  marriage itself reshapes views, or because both share a third common
  cause (cohort, region).

### 2. Ideal children num (CFPS 2014 only)

* β = +0.322 (overall, p < 10⁻¹⁴); +0.340 male, +0.263 female. Cohen's d
  high-vs-low tertile = 0.29 overall.
* Substantive: each .10 step toward traditional is associated with ≈ +0.03
  more desired children. Across the full ideation range, that's ~0.3
  children of difference — non-trivial in a sub-replacement context.
* This is the **clearest "ideology → fertility intention" gradient** in
  the run. Unfortunately 2020 dropped `qm501`, so no panel comparison.
  Worth flagging back to SPEC §5.2 generation: ideal-children is a high-
  variance, well-measured outcome; the 2020 wave's pivot to `qm501a`
  (社会压力) is a regret.

### 3. Housework hours / day — the gender-split story

This is the central RQ 5.2 finding and it survives the lagged frame for
women.

* **2014 cross-section**: overall β = −0.25 (p = .01) — perversely
  *negative* in the unadjusted full sample. The explanation is sex
  composition: the most-traditional men (who are less likely to do
  housework anyway) move the overall slope down.
* When stratified:
  * Male: β = −0.18 (p = .07) — traditional men do *less* housework
    (consistent with a gendered division-of-labour belief held by men).
  * Female: β = **+0.58 (p < 10⁻⁶)** — traditional women do *substantially
    more* housework.
* **2020 cross-section** repeats this pattern with smaller magnitudes
  on the male side (β = +0.19 n.s.) but persistent female β = +0.58
  (p = .003).
* **Lagged frame**: with `housework_2014` on the RHS, female β = +0.50
  (p = .085, marginal). Male β = +0.17 n.s. Read as: *baseline 2014
  ideation predicts how much a woman's daily housework rose between
  2014 and 2020 over and above her 2014 level*. Marginal, but in the
  expected direction with the right sign and same magnitude order as the
  cross-section.
* This is the **academic-grade version of the analysis_004 finding**:
  ideology maps into housework time only on the female side, and the
  effect is large (≈ 35 minutes/day between the bottom and top tertile
  of the ideation distribution, all else equal).

### 4. Age at first marriage — descriptive only

* The CFPS subsample with a measurable first-marriage year is small
  (n = 561 in 2014, 235 in 2020) because the variable is well-populated
  only for those who recorded the marriage in the survey. So OLS is
  noisy.
* Welch comparison (full ever-married sample): in 2014, low-ideation
  (progressive) women married 0.95 years **later** than high-ideation
  women (p = .004, d = −0.27). In 2020, low-vs-high diff = −1.55 years
  for women (p = .056). Men show no difference.
* This is the same picture as `analysis_022` on CGSS: traditional women
  married earlier. **Caveat (analysis_022 framing)**: ideation is measured
  at the survey, so this is "people who ended up traditional married
  earlier", not "ideation drove timing". A true event-history with
  time-varying attitudes is not identifiable with a once-measured index.

## What changes vs. the v1 `analysis_004` run

* Adds sex stratification on every outcome (not just an interaction term).
* Adds the lagged panel frame (ideation 2014 → outcome 2020).
* Adds first-marriage age as a separate, descriptive outcome (was
  absent in 004).
* Reports HC1 robust SEs everywhere (004 used classical SEs).
* Reports Welch / Cohen's d alongside OLS so the magnitudes can be read
  on standardised scales.
* Vector PDF figures (12 of them: per-tertile bar charts, coefficient
  forests, descriptive marriage-age trajectory).

## What this analysis *does* support, after the dual frame

1. **Ideation correlates strongly with marital status** in the cross-
   section, but the correlation does not survive once we hold 2014
   marital status fixed — likely a "marriage reshapes attitudes" story,
   or a shared third cause, rather than ideation → marriage selection.
2. **Ideal-children intention** is strongly predicted by ideation, in
   both sexes, in the only wave that asked. This is the cleanest
   pro-fertility-ideology finding in CFPS.
3. **Housework time** is the only outcome where ideation **survives the
   lagged frame** on the female side (β ≈ +0.50, marginal). Combined
   with the very tight cross-section β ≈ +0.58 (p < .001 in both waves),
   this is the most-defensible "ideology shapes practice" claim in 5.2.
4. The **male side is largely null** for housework and small-positive
   for currently-married. Most of the ideation → family-practice channel
   on the female side, almost none on the male side. Consistent with
   what we already saw in `analysis_025`: marriage and motherhood
   suppress the progressive shift for women, not for men.

## Caveats (read together with the tables)

* Lagged frame is on the ~12 k panel; lots of listwise deletion
  (housework lagged n = 3 200). Effects are noisier than the cross-
  section.
* Wage / income controls are 2014 `income` and 2020 `emp_income`, on
  different scales / coverage. Both enter on `log1p` and effects are
  not directly comparable across waves.
* No PSM here — these are descriptive / linear-adjustment frames. PSM
  for entering-marriage and new-birth is covered in `analysis_025`.
* `urban` flips coding between waves (2014: 1=农, 3=非农; 2020 adds 7=居民
  to urban). Both encoded consistently to 0 = rural, 1 = urban via
  `cfps_panel`.

## Files in this analysis_run

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — tertile × sex × outcome means
* `02_missing_table.csv` — coverage per outcome × frame
* `04_result_table.csv` — tidy OLS / LPM (213 rows)
* `tables/welch_tertile_diffs.csv` — Welch's t and Cohen's d, per stratum
* `figures/*` — 12 PDF figures:
  * `housework_by_tertile_{2014,2020}.pdf`
  * `currently_married_by_tertile_{2014,2020}.pdf`
  * `ideal_children_by_tertile_2014.pdf`
  * `first_marriage_age_2014_descriptive.pdf`
  * `coef_forest_ideation_{2014,2020,lagged}.pdf`
  * `coef_forest_interaction_{2014,2020}.pdf`
  * `summary_forest_all.pdf` — every fit on one chart
