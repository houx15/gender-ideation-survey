# 05 · Interpretation note — analysis_024

## Headline

Between CFPS 2014 and 2020, **81.7 % of the 15,859 matched respondents
moved by at least one notch on the four-item ideation index** (|Δ| ≥
0.05 on [0,1]). The aggregate drift is mildly **progressive**
(mean Δ = −0.030, SD = 0.196). But the variance is much larger than the
trend: 46.8 % shifted progressive, 34.8 % shifted traditional, 18.3 %
stayed stable. The headline is therefore *churn*, not directional
consensus.

## Who shifted — and in which direction

| Group split           | n     | mean Δ  | 95 % bootstrap CI | progressive share |
|-----------------------|-------|---------|-------------------|-------------------|
| Male                  | 7,760 | −0.018  | [−0.023, −0.014]  | 0.45              |
| Female                | 8,099 | **−0.042** | [−0.046, −0.038] | 0.49              |
| Rural hukou (2014)    | 11,623| −0.026  | [−0.030, −0.023]  | 0.46              |
| Urban hukou (2014)    | 4,214 | **−0.041** | [−0.047, −0.035] | 0.50              |
| Cohort 1930–49        | 1,391 | −0.012  | [−0.022, −0.002]  | 0.42              |
| Cohort 1950–59        | 2,780 | −0.013  | [−0.019, −0.006]  | 0.42              |
| Cohort 1960–69        | 3,721 | −0.012  | [−0.017, −0.006]  | 0.41              |
| Cohort 1970–79        | 3,228 | −0.031  | [−0.037, −0.024]  | 0.47              |
| Cohort 1980–89        | 2,801 | −0.051  | [−0.058, −0.043]  | 0.54              |
| Cohort 1990–2005      | 1,934 | **−0.074** | [−0.084, −0.064] | 0.57              |

* **Cohort is the dominant gradient.** Younger respondents are the ones
  doing most of the progressive movement; the three cohorts born before
  1970 barely shift on average. Cohen's *d* between 1930–49 and 1990–2005
  is 0.32.
* **Women shifted further progressive than men** (Cohen's *d* = 0.12,
  Welch *t* = −7.6, *p* < 1e-13). The gap is small per-person but
  consistent across cohorts.
* **Urban hukou holders shifted further progressive than rural** (Cohen's
  *d* = 0.076, *p* = 3.7e-05). The size is small, but the direction is
  what the modernisation hypothesis predicts.

## What life events accompanied the shift

Two events have statistically distinguishable raw contrasts (Welch test
on Δideation, "event" vs "no event"):

| Event              | n_yes | mean Δ (event) | mean Δ (no event) | Welch *p*   | Cohen's *d* |
|--------------------|-------|----------------|-------------------|-------------|-------------|
| Had a new child    | 2,648 | **−0.010**     | −0.035            | 2.7e-10     | −0.128      |
| Entered marriage   | 760   | **−0.058**     | −0.029            | 2.2e-04     | 0.148       |
| Got divorced       | 256   | −0.043         | −0.030            | 0.33 (ns)   | 0.064       |
| Lost / left job    | 81    | −0.013         | −0.027            | 0.50 (ns)   | −0.073      |
| Entered work       | 112   | −0.045         | −0.027            | 0.43 (ns)   | 0.095       |
| Widowed            | 380   | −0.018         | −0.031            | 0.20 (ns)   | −0.064      |

The two robust contrasts go in **opposite directions**:

* People who **entered marriage** between 2014 and 2020 shifted *more*
  progressive than peers who did not. The simplest reading is selection:
  newlyweds are concentrated in the younger, more-educated cohort that
  shifted progressive anyway.
* People who **had a new child** shifted *less* progressive than those
  who did not (their Δ is closer to zero). On its face this looks like a
  "traditionalising" effect of parenthood, but the OLS below shows it
  reverses sign once we control for baseline ideation — see next section.

Marital-transition descriptives (sorted from most-progressive to most-traditional shift):

| transition          | n     | mean Δ  | progressive share |
|---------------------|-------|---------|-------------------|
| stable_never_married| 1,227 | −0.076  | 0.56              |
| entered_marriage    | 760   | −0.058  | 0.53              |
| stable_divorced     | 150   | −0.046  | 0.53              |
| divorced            | 256   | −0.043  | 0.50              |
| stable_married      | 12,456| −0.025  | 0.46              |
| stable_widowed      | 483   | −0.007  | 0.42              |

Single-and-stable, plus those entering or leaving marriage, are the
progressive end of the distribution. Long-stable married and stable
widowed are anchored close to zero.

## OLS with baseline-ideation control (N = 10,318; HC1 SEs)

Once we hold baseline 2014 ideation, age, gender, and hukou constant,
the picture shifts:

| Predictor               | β        | HC1 95 % CI       | HC1 *p*  |
|-------------------------|----------|-------------------|----------|
| Female                  | −0.012   | [−0.018, −0.005]  | 3 × 10⁻⁴ |
| Urban hukou (2014)      | **−0.055**| [−0.063, −0.047] | 1 × 10⁻³⁹|
| Age at 2014 (per year)  | **+0.003**| [+0.003, +0.004] | 3 × 10⁻⁷¹|
| Had a new child         | **−0.019**| [−0.030, −0.008] | 5 × 10⁻⁴ |
| Entered marriage        | −0.018   | [−0.035, −0.0002] | 0.047    |
| Got divorced            | +0.003   | [−0.022, +0.028]  | 0.80     |
| Widowed                 | −0.003   | [−0.029, +0.023]  | 0.83     |
| Lost / left job         | +0.025   | [−0.010, +0.060]  | 0.16     |
| Entered work            | −0.018   | [−0.058, +0.023]  | 0.39     |
| Δ household size        | −0.001   | [−0.003, +0.001]  | 0.34     |
| Δ education years       | −0.001   | [−0.003, +0.001]  | 0.41     |
| Baseline ideation (2014)| **−0.644**| [−0.665, −0.623] | < 1e-300 |

Three things worth stressing.

1. **Baseline ideation dominates.** β = −0.644 means roughly two-thirds
   of the 2014 deviation from the population mean is undone by 2020.
   This is the textbook regression-to-the-mean signature: it's the same
   pattern you see when the same instrument is re-administered to the
   same people, partly because ideology genuinely drifts toward the
   contemporary social mean, partly because each Likert measurement has
   item-level noise.
2. **The new-child coefficient reverses sign.** In the raw contrast,
   people with a new child shifted *less* progressive. In the OLS, after
   controlling for baseline ideation, the same group shifted *more*
   progressive (β = −0.019, *p* = 0.0005). Mechanism: new parents are
   selected from younger, more-progressive baselines; once we
   condition on baseline, the within-person effect of having a child is
   in the *progressive* direction, not the traditionalising one.
3. **Hukou and age are the strongest substantive movers.** Urban hukou
   in 2014 is associated with a 0.055 deeper progressive shift than
   rural; each extra year of age is associated with a 0.003 more
   traditional drift (≈ 0.06 across a 20-year age gap). Both swamp the
   life-event terms in magnitude.

Job-status changes (`lost_job`, `entered_work`), divorce, and widowhood
do **not** carry statistically distinguishable signal once the controls
are included. Sample sizes for these events are small (81–380), so the
result is "no evidence", not "evidence of no effect".

## Takeaways for the dissertation chapter

* Ideology is **not stable** for most people across a six-year window —
  the modal experience is movement of at least one battery notch, and
  the direction is heterogeneous.
* The strongest **demographic** predictors of progressive shift are
  younger cohort, urban hukou, and (smaller) being female.
* The strongest **event** predictor that survives the baseline-ideation
  control is **having a new child** — and the sign is the *opposite* of
  what a naïve raw-contrast suggests. This deserves careful attention
  before any causal claim: it could be a within-cohort selection
  artefact, or a real "parenting-toward-equality" effect, or
  measurement-error correlated with childbearing.
* The marital-transition descriptives suggest a clear single-vs-married
  gradient (singles shift more progressive than the stable-married),
  which is conventional in the literature; the OLS adds only modest
  signal once age + hukou are in.
* Job exit and entry are too rare in the panel (n ≤ 112) to support a
  conclusion either way; this would need pooling with another wave or a
  more sensitive employment-history variable to test properly.

## What this analysis **cannot** say

* Causal direction. We do not separate "having a child shifts your
  ideology" from "people whose ideology was already shifting were also
  more likely to have a child".
* Item-level dynamics. The Δideation lumps four items into one mean.
  Whether the shift is concentrated on the housework item versus the
  marry-well item is left to a follow-up.
* Lifecourse generalisability. Only two CFPS waves are used here;
  trajectories from 2010 / 2012 / 2016 / 2018 would tighten the
  within-person variance.

## Files in this analysis_run

* `00_question.md` — research question and scope
* `01_descriptive_table.csv` — variable-by-variable Table 1
* `02_missing_table.csv` — per-variable missingness audit
* `03_method_note.md` — data construction and statistical methods
* `04_result_table.csv` — single tidy table of the key numbers above
* `05_interpretation_note.md` — this file
* `tables/` — every CSV produced by the analysis script
* `figures/` — `delta_ideation_hist.pdf`, `who_changes_forest.pdf`,
  `life_event_forest.pdf`, `ols_coefplot.pdf` (vector PDF, pdf.fonttype=42)
* `scripts/run.py` — the orchestration script
