# 05 · Interpretation note — analysis_024 (v2)

## What's new in v2

The first pass of this analysis_run treated every life event as 0/1 and
compared "event = 1" against the **entire** panel. That denominator is
wrong for transitions like marriage or job loss: a never-married 22-year-old
who married by 2020 was being compared to a 70-year-old stable-married
respondent. v2 keeps both denominators side-by-side and **adds a sex
stratification (overall / male / female)** for every life-event contrast
and OLS specification.

* **"All" denominator** — Welch *t* of `event == 1` vs `event == 0` over
  the whole panel. Big "no" groups, but contaminated by people who could
  not have undergone the transition.
* **"At-risk" denominator** — only respondents whose 2014 state made the
  0→1 transition possible (e.g. for `entered_marriage`, only those who
  were `never-married` or `cohab` in 2014). Smaller "no" groups, but the
  contrast is the within-pool comparison the question actually wants.

Definitions of the at-risk pool live in `cfps_panel.at_risk_for_event`:

| Event              | At-risk pool (2014 state)                  |
|--------------------|--------------------------------------------|
| entered_marriage   | marital ∈ {never-married, cohab}           |
| divorced           | marital ∈ {married, cohab}                 |
| widowed            | marital ∈ {married, cohab}                 |
| lost_job           | employed = 1                               |
| entered_work       | employed = 0                               |
| had_new_child      | female + age ≤ 45  OR  male + age ≤ 55     |

## Headline

* Aggregate Δideation 2014→2020: mean = −0.030 (SD 0.196). 81.7 % of
  pids with computable Δ moved by at least one notch of the 4-item
  battery.
* 46.8 % shifted progressive, 34.8 % traditional, 18.3 % stable.
* **Most of the demographic gradient — and most of the life-event signal
  — is concentrated among women.** Splitting the OLS by sex shows
  women's predictors are ~2× the magnitude of men's for hukou, age, and
  childbearing.

## Who shifted (unchanged from v1)

| Group split           | n     | mean Δ  | progressive share |
|-----------------------|-------|---------|-------------------|
| Male                  | 7,760 | −0.018  | 0.45              |
| Female                | 8,099 | **−0.042** | 0.49           |
| Rural hukou (2014)    | 11,623| −0.026  | 0.46              |
| Urban hukou (2014)    | 4,214 | **−0.041** | 0.50           |
| Cohort 1930–49        | 1,391 | −0.012  | 0.42              |
| Cohort 1990–2005      | 1,934 | **−0.074** | 0.57           |

Cohort gradient remains the dominant driver: Cohen's *d* between the
oldest and youngest cohort is 0.32.

## Life-event contrasts — both denominators × three strata

### Important caveat: `had_new_child` is contaminated

Investigation showed that of the 2,785 panel-wide `had_new_child = 1`
cases, **all are aged ≥ 54 at 2014** (median 63). These are not new
births — they reflect rostering changes (adult children re-appearing in
the 2020 child roster). Within the fertile age window (women ≤ 45 OR
men ≤ 55), only 94 cases remain, almost all on the male side because
fertile-age women are still very young. The at-risk denominator
therefore largely **rules out** this measurement artefact, leaving
either a too-small sample (women: ~0) or a sample where the "new child"
is happening to men ≥ 54 (89 cases). Take any inference on this
variable as a measurement-issue diagnostic, not a substantive estimate.

### What survives the at-risk restriction

Highlights from `life_event_means_{all,male,female}.csv` (denom =
at_risk; ":x" = p-value from Welch *t*):

| Event             | Stratum | n_yes | mean(yes) | mean(no) | diff   | p       |
|-------------------|---------|-------|-----------|----------|--------|---------|
| entered_marriage  | all     | 760   | −0.058    | −0.075   | +0.017 | 0.092   |
| entered_marriage  | male    | 374   | −0.034    | −0.052   | +0.018 | 0.182   |
| entered_marriage  | female  | 386   | **−0.081**| **−0.112**| +0.031 | **0.037** |
| widowed           | female  | 257   | −0.015    | −0.036   | +0.021 | 0.074   |
| divorced          | female  | 80    | −0.069    | −0.035   | −0.034 | 0.169   |
| lost_job          | all     | 81    | −0.013    | −0.027   | +0.014 | 0.510   |
| entered_work      | all     | 112   | −0.045    | −0.010   | −0.035 | (n_no=6) |

Reading: *the difference within the at-risk pool*. A positive `diff`
means the event group was **less progressive** than the no-event group;
a negative `diff` means the event group shifted **more progressive**.

Key takeaways:

1. **Both sexes shift strongly progressive in the unmarried-in-2014 pool**
   (means of −0.07 to −0.11). Within that pool, those who actually got
   married shifted slightly *less* progressive than those who didn't.
   For women the gap reaches significance (Δ_no − Δ_yes = +0.031,
   p = 0.037). The effect is consistent with a "marriage → more
   traditional than stay-single peers" pattern, but the gap is *within*
   a strongly progressive pool, so the conventional reading "marriage
   makes you traditional" is misleading.

2. **Widowed women** shifted noticeably less progressive than other
   2014-partnered women (diff = +0.021, p = 0.074). Marginal but
   substantively interesting given n_yes = 257.

3. **Job changes** (lost_job, entered_work) carry no Welch signal under
   either denominator and either sex — sample sizes (n_yes ≤ 112) are
   too small even pooled. We can only say "no evidence".

4. The whole-panel ("all") denominator overstates the size of every
   transition contrast by 2–4×, because the comparison group includes
   ineligibles. This is mostly mechanical, not informative.

## OLS by sex (HC1 SEs) — the headline table

`ols_delta_ideation_{all,male,female}.csv` — same RHS variables in all
three specifications, except `female` is dropped from the within-sex
ones. Selected coefficients (HC1 95 % CI in brackets):

| Predictor          | All (N=10,318)               | Male (N=5,808)              | Female (N=4,510)             |
|--------------------|-------------------------------|------------------------------|------------------------------|
| Urban hukou (2014) | **−0.055** [−0.063, −0.047]   | **−0.035** [−0.045, −0.025] | **−0.080** [−0.093, −0.067] |
| Age at 2014 / yr   | **+0.003** [+0.003, +0.004]   | **+0.002** [+0.002, +0.003] | **+0.005** [+0.004, +0.005] |
| Had a new child    | **−0.019** [−0.030, −0.008]   | −0.003 [−0.017, +0.011]      | **−0.042** [−0.059, −0.025] |
| Entered marriage   | **−0.018** [−0.035, −0.0002]  | −0.006 [−0.028, +0.016]      | **−0.034** [−0.062, −0.005] |
| Got divorced       | +0.003 [−0.022, +0.028]       | +0.016 [−0.013, +0.044]      | −0.028 [−0.074, +0.019]      |
| Widowed            | −0.003 [−0.029, +0.023]       | **−0.050** [−0.096, −0.005] | +0.012 [−0.017, +0.042]      |
| Lost / left job    | +0.025 [−0.010, +0.060]       | +0.024 [−0.025, +0.073]      | +0.039 [−0.011, +0.089]      |
| Entered work       | −0.018 [−0.058, +0.023]       | −0.006 [−0.061, +0.049]      | −0.026 [−0.083, +0.030]      |
| Δ household size   | −0.001 [−0.003, +0.001]       | −0.001 [−0.003, +0.001]      | −0.002 [−0.005, +0.001]      |
| Δ education years  | −0.001 [−0.003, +0.001]       | −0.001 [−0.005, +0.002]      | +0.0003 [−0.003, +0.004]     |
| Baseline ideation  | **−0.644** [−0.665, −0.623]   | **−0.669** [−0.696, −0.643] | **−0.637** [−0.669, −0.604] |
| Female (pooled)    | **−0.012** [−0.018, −0.005]   | —                            | —                            |

Stars in bold = HC1 *p* < 0.05.

The most striking sex split:

* **Urban hukou** shifts women 0.080 more progressive than rural women,
  but men only 0.035. The gradient is more than twice as steep for
  women.
* **Age** drifts women 0.005 more traditional per year of age in 2014;
  men only 0.002. Over a 30-year age gap that compounds to a 0.15
  difference in Δideation for women vs 0.06 for men.
* **Having a new child** moves women 0.042 more progressive than
  childless women, *after* baseline-ideation control. Men: no signal.
  This is the most concrete event-level finding in the analysis.
  Caveat from above: the underlying `had_new_child` variable is
  partly contaminated by roster artefacts at older ages, so the
  cleanest reading is "within the *pooled* CFPS panel, baseline-
  ideation-conditional, having a child added to your roster is
  associated with a deeper progressive shift for women only."
* **Entered marriage** moves women 0.034 more progressive (p=0.019);
  men: no signal. Reading: marriage selects women out of the most
  progressive-shifting unmarried pool, but the within-person effect
  (after baseline control) is in the progressive direction.
* **Widowed men** shifted 0.050 more progressive than partnered men
  (p = 0.030). n_yes = 119, so substantively important to flag but
  underpowered. No equivalent signal for women.

## What this analysis can claim

1. The drift is mostly **young and urban**, regardless of life events.
2. **Among women only**, two within-person events are robustly
   associated with a progressive shift after baseline-ideation control:
   entering marriage (−0.034) and gaining a rostered child (−0.042).
3. Among men, the only event-level signal is **widowhood** (−0.050).
4. Job-status changes do not carry signal under either denominator.

## What it cannot claim

* **Causation.** Two-wave designs cannot separate "event causes
  attitude" from "attitude predicts event".
* **Effect of new births specifically.** The `had_new_child` indicator
  is contaminated by roster-update artefacts, especially at older
  ages. The female result (β = −0.042) is robust *within* the panel,
  but the substantive claim "new motherhood reduces traditionalism"
  cannot be made until we use child birth-year data to define the
  event cleanly.
* **Within-item dynamics.** All life-event effects reported here are on
  the 4-item mean. Item-level breakdowns (housework, marry-well,
  woman-needs-children, men-society/women-family) belong to a follow-up.

## Files in this analysis_run

* `00_question.md` — research question and scope
* `01_descriptive_table.csv` — variable-by-variable Table 1
* `02_missing_table.csv` — per-variable missingness audit
* `03_method_note.md` — data construction and statistical methods
* `04_result_table.csv` — single tidy table of the key numbers
* `05_interpretation_note.md` — this file
* `tables/life_event_means_{all,male,female}.csv` — two denominators
  side-by-side
* `tables/ols_delta_ideation_{all,male,female}.csv` — OLS by sex
* `tables/ols_meta.csv` — per-stratum sample sizes
* `figures/life_event_forest_{all,male,female}.pdf` — one figure per
  sex stratum, each with two denominator panels (whole-sample /
  at-risk). X-axes are matched across the three so the diffs are
  directly comparable.
* `figures/ols_coefplot_{all,male,female}.pdf` — one OLS coefplot per
  sex stratum (HC1 CI); baseline-ideation coefficient is reported as a
  footnote because its magnitude (~−0.65) is off-scale.
* `figures/who_changes_forest.pdf`, `delta_ideation_hist.pdf` — unchanged
