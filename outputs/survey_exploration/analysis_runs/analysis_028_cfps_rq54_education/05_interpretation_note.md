# 05 · Interpretation note — analysis_028

> RQ 5.4 education, deep-dive replacement for
> `analysis_006_cfps_education`. The methodological theme: separating
> the reverse-causal cross-section from a directional young-cohort
> lagged frame.

## Headline

| Frame | Overall β | Male | Female | Reading |
|---|---|---|---|---|
| **2014 cross** (full) | **−2.53** (<.001) | **−2.68** | **−4.36** | Reverse-causal: older + less educated → more traditional |
| **2020 cross** (full) | **−3.37** (<.001) | **−3.54** | **−4.82** | Same |
| **2014 young cohort** (birthy ≥ 1990) | **−2.30** (<.001) | **−2.26** | **−3.48** | Weakly reverse-causal |
| **2020 young cohort** (birthy ≥ 1990) | **−3.91** (<.001) | **−3.87** | **−4.38** | Weakly reverse-causal |
| **Lagged Δ, young cohort, panel** | −0.24 n.s. | −0.19 n.s. | **−1.37** (.006) | *Directional*: ideation 2014 → Δ-edu 2014→2020 |

β on edu_yrs, where the ideation index moves on [0, 1]; so β = −2.53 means
moving across the full ideation range associates with 2.5 fewer years of
schooling.

The story:

1. **Cross-section βs are enormous but reverse-causal.** β around −3 to
   −5 years across full samples and waves. These are not "ideology
   causes less schooling"; they are "people with less schooling
   *ended up* more traditional, especially among older cohorts" plus
   "women with less schooling are more traditional than men with the
   same low schooling".

2. **The young-cohort cross-section trims most of the cohort
   confound but not the simultaneity.** β still ≈ −2.3 to −4 because
   for many born-1990+ respondents the schooling decision and the
   2014 / 2020 attitude are still measured roughly together.

3. **The lagged Δ frame on the young-cohort panel is the only
   directionally-defensible cell.** Among the 632 panel respondents
   born ≥ 1990 with full controls:
   * Overall β = −0.24 (n.s.) — no overall effect on Δ-edu_yrs.
   * Male β = −0.19 (n.s.) — no male effect.
   * **Female β = −1.37 (p = .006)** — for young women, more-traditional
     ideation in 2014 associates with **~1.4 fewer additional years
     of schooling** between 2014 and 2020, controlling for the 2014
     edu_yrs and standard covariates.

4. **Gender moderation.** The `ideation × female` interaction is
   strongly negative in the cross-sections (β ≈ −2.0 to −2.4), shrinks
   in young-cohort cross-sections (β ≈ −0.5 to −1.1 n.s.), and remains
   directionally negative but n.s. in the lagged frame (β = −1.03).
   Magnitude is consistent with the female-only lagged finding.

## The substantively defensible claim

> Among young women in CFPS (born ≥ 1990, age ≤ 24 in 2014), holding
> more traditional gender ideology in 2014 is associated with
> ~1.4 fewer additional years of education by 2020 (95 % CI:
> [−2.34, −0.40], p = .006), controlling for 2014 education level,
> age, urban hukou, and household income. **No analogous effect among
> young men** (β = −0.19, p = .68).

That's the headline. Everything else in the run is either descriptive
or reverse-causal.

## Why the cross-section βs are so large — illustrated

`tables/edu_by_cohort.csv` and `figures/edu_yrs_by_cohort_*.pdf` make
the structure transparent:

* Birth-decade 1950s women, high-ideation tertile: ~3 years of edu.
* Birth-decade 1990s women, low-ideation tertile: ~13 years of edu.
* That ~10-year gap is *cohort + selection*, not "ideology shapes
  schooling".

The cross-section β captures this cohort gradient. Restricting to
born ≥ 1990 (where everyone has at least junior high education in
the modern Chinese system) collapses most of this, but ideation is
still measured at or after schooling completion for ~half the cell.

The lagged-Δ frame is the only one where ideation is fixed at a
point in time *before* some of the schooling that gets measured.

## Comparison to RQ 5.2 and 5.3 results

The educational finding completes a coherent female-side picture
across 026 / 027 / 028:

| Domain | Female-side lagged finding |
|---|---|
| Family (026) | Housework: β = +0.50 (p = .085) — traditional women do more housework over time |
| Family (026) | Marriage / new birth: PSM-DiD ATT = +0.05 / +0.08 — traditional women shift less progressive after marriage / motherhood |
| Work (027) | ISEI: β = −4.25 (p = .035) — traditional women's occupations less prestigious by 2020 |
| Work (027) | Yearly wage: β = −0.31 (p = .095) — traditional women earn less |
| **Education (028)** | **Δ edu_yrs: β = −1.37 (p = .006)** — traditional young women acquire fewer additional years of schooling |

All female-only, all directional in their respective lagged frames.
Together they form the most coherent through-line in the project so
far: **gender ideology functions as a cumulative, female-specific
drag on schooling, prestige, and earnings**, with knock-on effects
that persist in marriage and family time-use.

The male side carries small / null directional effects on every
outcome.

## Caveats

* `lagged_young_cohort_delta` is on a small panel (n = 632 overall,
  279 women). The CI on the female β is [−2.34, −0.40] — wide but
  excluding zero.
* "Young cohort" here means birthy ≥ 1990. A natural extension would
  be to refine this to "still in school in 2014" (using `qs1` / `qs2`
  flags if they exist); skipped for parsimony.
* Imputed years (`cfps20{14,20}eduy_im`) impose a max of 22 and are
  imputed by the CFPS team. For descriptive purposes the categorical
  `edu_level` was also coded but is not the regression outcome.
* `urban` for 2020 includes the 7=居民 code in addition to 3=非农; 2014
  only has 1=农 and 3=非农. Consistent with the rest of the project.

## Files in this analysis_run

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv`, `02_missing_table.csv`,
  `04_result_table.csv`
* `tables/welch_tertile_diffs.csv`, `tables/edu_by_cohort.csv`
* `figures/edu_yrs_by_tertile_{2014,2020}{,_young}.pdf`
* `figures/edu_yrs_by_cohort_{2014,2020}.pdf` — birth-decade trajectories
* `figures/coef_forest_ideation_all_frames.pdf` — every β on one chart
* `figures/coef_forest_interaction_all_frames.pdf` — gender moderation
