# 05 · Interpretation note — analysis_024 (v3)

## Scope

Supplementary to RQ 5.1 (analysis_023). Of the 20,100 respondents in
both CFPS 2014 and 2020, 15,859 have a computable Δideation, and 81.7 %
of those moved by at least one notch of the 4-item battery
(|Δ| ≥ 0.05). This run asks (A) *who* drives that movement and (B)
*which life events* go with it, stratified by sex (overall, male,
female).

> v3 simplification: only the **whole-sample denominator** is reported
> for life-event contrasts (`event = 1` vs `event = 0` across the
> relevant sex stratum). The at-risk-restricted version explored in v2
> shrank n_yes too far for the rarer events (e.g. fertile-age
> `had_new_child` n_yes = 94 panel-wide, ≈0 for women under 45) to
> support inference. The `at_risk_for_event` helper stays in
> `cfps_panel.py` as documented library code for follow-up work.

## Headline

* Aggregate Δideation 2014→2020: mean = −0.030 (SD 0.196). 46.8 %
  shifted progressive, 34.8 % traditional, 18.3 % stable.
* The dominant gradient is **birth cohort** — younger cohorts shifted
  far more progressive than older ones.
* The dominant **life-event** signal is **female-only**: having a
  rostered new child and entering marriage both push women ≈0.04 more
  progressive than female peers, after baseline-ideation control.
* The one male-only signal is **widowhood** (β = −0.050, *p* = 0.030)
  — substantively striking but underpowered (n_yes = 119).

## Who shifted

| Group split            | n      | mean Δ  | progressive share |
|------------------------|--------|---------|-------------------|
| Male                   | 7,760  | −0.018  | 0.45              |
| Female                 | 8,099  | **−0.042** | 0.49           |
| Rural hukou (2014)     | 11,623 | −0.026  | 0.46              |
| Urban hukou (2014)     | 4,214  | **−0.041** | 0.50           |
| Cohort 1930–49         | 1,391  | −0.012  | 0.42              |
| Cohort 1950–59         | 2,780  | −0.013  | 0.42              |
| Cohort 1960–69         | 3,721  | −0.012  | 0.41              |
| Cohort 1970–79         | 3,228  | −0.031  | 0.47              |
| Cohort 1980–89         | 2,801  | −0.051  | 0.54              |
| Cohort 1990–2005       | 1,934  | **−0.074** | 0.57           |

Cohen's *d* between the oldest and youngest cohort is 0.32. Women shift
further progressive than men (d = 0.12, *p* < 1e-13). Urban-hukou
2014 shifted further progressive than rural (d = 0.076, *p* = 4e-5).

## Life-event contrasts (whole-sample denominator)

`tables/life_event_means_{all,male,female}.csv`. Diff = mean(event=1)
− mean(event=0); negative diff means the event group shifted more
progressive than the no-event group.

### Overall sample

| Event              | n_yes  | mean(yes) | mean(no) | diff    | Welch *p*  |
|--------------------|--------|-----------|----------|---------|------------|
| Had a new child    | 2,648  | −0.010    | −0.035   | +0.025  | 3 × 10⁻¹⁰  |
| Entered marriage   | 760    | −0.058    | −0.029   | −0.029  | 2 × 10⁻⁴   |
| Got divorced       | 256    | −0.043    | −0.030   | −0.013  | 0.33 (ns)  |
| Widowed            | 380    | −0.018    | −0.031   | +0.012  | 0.20 (ns)  |
| Lost / left job    | 81     | −0.013    | −0.027   | +0.014  | 0.50 (ns)  |
| Entered work       | 112    | −0.045    | −0.027   | −0.018  | 0.43 (ns)  |

### Male sample

| Event              | n_yes | mean(yes) | mean(no) | diff   | Welch *p*  |
|--------------------|-------|-----------|----------|--------|------------|
| Had a new child    | 1,301 | −0.005    | −0.021   | +0.016 | 5 × 10⁻³   |
| Entered marriage   | 374   | −0.034    | −0.018   | −0.017 | 0.13 (ns)  |
| Got divorced       | 159   | −0.019    | −0.018   | −0.001 | 0.95 (ns)  |
| Widowed            | 119   | −0.022    | −0.018   | −0.004 | 0.85 (ns)  |
| Lost / left job    | 38    | +0.005    | −0.017   | +0.022 | 0.47 (ns)  |
| Entered work       | 62    | −0.028    | −0.017   | −0.011 | 0.75 (ns)  |

### Female sample

| Event              | n_yes | mean(yes) | mean(no) | diff    | Welch *p* |
|--------------------|-------|-----------|----------|---------|-----------|
| Had a new child    | 1,347 | −0.014    | −0.047   | **+0.033** | 9 × 10⁻¹⁰ |
| Entered marriage   | 386   | −0.081    | −0.040   | **−0.041** | 2 × 10⁻⁴  |
| Got divorced       | 97    | −0.081    | −0.041   | −0.040  | 0.068 (∼)  |
| Widowed            | 261   | −0.017    | −0.043   | **+0.026** | 0.024     |
| Lost / left job    | 43    | −0.029    | −0.040   | +0.011  | 0.71 (ns) |
| Entered work       | 50    | −0.066    | −0.039   | −0.027  | 0.38 (ns) |

The clean reading: **the female panel carries all of the life-event
signal**. Three contrasts cross conventional significance: women who
had a new child shifted less progressive than other women (+0.033, *p*
≈ 9e-10); women who entered marriage shifted *more* progressive
(−0.041, *p* = 2e-4); women who were widowed shifted less progressive
(+0.026, *p* = 0.024). In the male panel only the new-child contrast
has any signal at all (+0.016, *p* = 0.005), and the OLS below shows it
disappears once baseline ideation is controlled.

## OLS by sex (HC1 SEs)

`tables/ols_delta_ideation_{all,male,female}.csv`. RHS variables
identical across the three specifications, with `female` dropped from
the within-sex fits. Selected coefficients with HC1 95 % CI:

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

Bold = HC1 *p* < 0.05.

Three things worth stressing:

1. **The new-child coefficient flips sign in the female panel.** In the
   raw whole-sample contrast (Welch), women with a new child shifted
   *less* progressive than other women (+0.033). In the OLS, after
   conditioning on baseline ideation + age + hukou, the same group
   shifted *more* progressive (β = −0.042, *p* < 1e-6). Mechanism: women
   who gain a rostered child are selected from younger, more-traditional
   baselines; once we condition on that selection, the within-person
   effect goes in the progressive direction. The male panel has no
   such effect either way.

2. **Hukou and age are roughly twice as strong for women as for men.**
   Urban hukou shifts women 0.080 more progressive than rural women but
   men only 0.035. Age drifts women 0.005 traditional per year vs 0.002
   for men. Over a 30-year age gap that compounds to 0.15 vs 0.06.

3. **Widowed men** shifted 0.050 more progressive than partnered men.
   *p* = 0.030 with n_yes = 119, so we flag it as a striking but
   underpowered finding. No equivalent signal for women.

## Important caveat — `had_new_child` is contaminated

Of the 2,785 panel-wide `had_new_child = 1` cases, **all are aged ≥ 54
in 2014, median age 63**. These are not biological births — they're
rostering changes (adult children re-appearing in the 2020 child
roster). The indicator is therefore best read as "respondent's number
of rostered children grew", not "respondent had a baby". The female
OLS coefficient (β = −0.042) is robust *within the data we have*, but
the substantive claim "new motherhood reduces traditionalism" cannot
be made from this evidence alone — it would require pulling the CFPS
child file and reconstructing the event from child birth-years. We
note this in the discussion and leave the cleaner reconstruction for a
follow-up.

## Takeaways

* The biggest substantive driver of progressive shift across CFPS 2014
  → 2020 is **young, urban, female**.
* Life-event signal is overwhelmingly concentrated in the **female**
  panel. The events that matter, after baseline-ideation control, are
  *entering marriage* and *gaining a rostered child*; both push women
  ≈0.04 more progressive than peers. The male panel shows nothing
  comparable, except a striking-but-fragile widowhood effect.
* Job-status changes carry no signal in either sex; sample sizes
  (n_yes ≤ 112) too small.

## What this analysis cannot claim

* **Causation.** Two-wave designs cannot separate "event causes
  attitude" from "attitude predicts event".
* **A clean motherhood-→-progressive interpretation**, for the
  measurement reasons above.
* **Within-item dynamics**: all results are on the 4-item mean.

## Files in this analysis_run

* `00_question.md` — research question and scope
* `01_descriptive_table.csv` — variable-by-variable Table 1
* `02_missing_table.csv` — per-variable missingness audit
* `03_method_note.md` — data construction and statistical methods
* `04_result_table.csv` — single tidy table of the key numbers
* `05_interpretation_note.md` — this file
* `tables/life_event_means_{all,male,female}.csv` — Welch contrasts
* `tables/ols_delta_ideation_{all,male,female}.csv` — OLS by sex
* `tables/ols_meta.csv` — per-stratum sample sizes
* `figures/life_event_forest_{all,male,female}.pdf` — one forest per
  sex stratum, all six life events. n_yes is folded into each y-tick
  label so the count no longer collides with the CI whisker.
* `figures/life_event_forest_family.pdf` — focused M-vs-F forest of
  family-change events: had a new child, entered marriage, got
  divorced. Y-tick labels show both M and F n_yes.
* `figures/life_event_forest_job.pdf` — focused M-vs-F forest of
  job-change events: lost / left job, entered work.
* `figures/did_trajectory_family.pdf` / `did_trajectory_job.pdf` —
  classic 2-point DiD plots of mean ideation in 2014 and 2020 for
  treated (event=1) vs control (event=0), per event × sex. Each
  panel prints `DiD = (treated slope) − (control slope)`. These are
  visualisations of the same naïve DiD that the OLS coefficients
  estimate (controls being the whole-sample no-event group, no
  matching). For the matched-control version, see analysis_025.
* `figures/ols_coefplot_{all,male,female}.pdf` — one coefplot per sex
  stratum (HC1 95 % CI; baseline-ideation in footnote)
* `figures/who_changes_forest_{all,male,female}.pdf` — demographic
  forests (cohort + hukou; gender block in the pooled figure only).
  X-axes are matched so the three figures line up visually.
  `tables/who_changes_{all,male,female}.csv` carry the underlying
  numbers.
* `figures/delta_ideation_hist.pdf` — unchanged
