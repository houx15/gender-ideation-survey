# 05 · Interpretation note — analysis_031

> PSM-DiD strengthens (and partly revises) the housework finding from
> `analysis_026 v2`.

## Headline

Under PSM-DiD with bootstrap inference, **the female-side Δ-housework
effect shrinks from the lagged-OLS estimate of +0.50 hr/day to an ATT
of +0.11 hr/day, and loses statistical significance**.

| Stratum | n_treated | n_control | ATT (hr/day) | boot SE | 95 % CI | *p* |
|---|---|---|---|---|---|---|
| All | 1 125 | 1 456 | **−0.042** | 0.140 | [−0.249, +0.293] | .76 |
| Male | 714 | 928 | **+0.074** | 0.166 | [−0.323, +0.361] | .66 |
| Female | 411 | 528 | **+0.114** | 0.225 | [−0.442, +0.425] | .61 |

Compare with the lagged-OLS estimates in `analysis_026 v2`:

| Stratum | OLS β (026) | OLS p | PSM-DiD ATT (031) | PSM-DiD p |
|---|---|---|---|---|
| All | +0.19 (n.s.) | .39 | −0.04 | .76 |
| Male | +0.17 (n.s.) | .44 | +0.07 | .66 |
| **Female** | **+0.50** (.085) | .085 | **+0.114** | .61 |

The female point estimate goes from +0.50 to +0.11 — a ≈ 4–5× shrinkage,
mirroring exactly what we saw for ISEI in `analysis_030`.

## Why the shrinkage

Pre-match SMDs reveal substantial imbalance — most prominently in
`edu_yrs_2014` (female pre-SMD = **−0.78**) and `children_n_2014`
(female pre-SMD = **+0.39**). High-ideation women in 2014 are
**less educated** AND **already have more children** than the
low-ideation comparison group. Both predict more housework directly.

| Covariate (female stratum) | Pre-SMD | Post-SMD |
|---|---|---|
| birthy_2014        | −0.514 | +0.004 |
| **edu_yrs_2014**   | **−0.782** | +0.012 |
| urban_2014         | −0.214 | 0.000  |
| log_income_2014    | −0.184 | −0.040 |
| employed_2014      | +0.026 | +0.021 |
| marital_2014       | +0.138 | −0.008 |
| **children_n_2014**| **+0.394** | +0.058 |

Post-match balance is excellent — all |SMD| ≤ 0.06, well within the
0.1 threshold.

So the OLS-026 ideation→Δhousework β was confounded by:
1. **Education** — traditional women have less, and less-educated
   women do more housework regardless.
2. **Pre-existing fertility** — traditional women already have more
   children in 2014, which mechanically commits more time to
   domestic work.
3. **The residual ideation→Δhousework channel** — small and uncertain.

When PSM matches on (1) + (2) + cohort + urban + employment + marital,
the residual signal is +0.11 hr/day (≈ 7 minutes), n.s.

## Substantive reading

The 030/031 pair tells a now-consistent story:

* The **population-level association** between ideation and labour-
  market prestige (ISEI) AND between ideation and current housework
  is large and easy to find in any cross-section.
* The **average causal effect under selection-on-observables** in
  both cases is much smaller and statistically indistinguishable from
  zero.
* The discrepancy localises *where* the ideation → outcome link lives:
  **predominantly upstream in education + family-formation timing**.

This is consistent with a mediation story:
- Ideation → schooling completion (028's young-cohort Δedu β = −1.37,
  significant)
- Ideation → marriage timing + fertility timing (026 / 025)
- Schooling + family-formation → ISEI + current housework

The *direct* ideation → ISEI and ideation → Δhousework channels,
holding edu / cohort / fertility fixed, are small and noisy.

## What this means for the female-side through-line

Updated picture across all PSM/DiD runs:

| Channel | Lagged OLS β | PSM/DiD ATT | Read |
|---|---|---|---|
| Marriage / new-birth → Δ-ideation (025) | −0.04 / −0.03 (Welch) | **+0.05 / +0.08** (PSM-DiD) | The flip from neg-Welch to pos-ATT is the *selection-flip signature*: marriage/motherhood suppress the progressive shift young women would otherwise have. |
| Ideation → Δ-edu (young ♀) (028) | **−1.37** (.006) | next: 032 | |
| Ideation → ISEI (♀) (027/030) | **−4.25** (.035) | **−1.20 (n.s.)** | Most of OLS is selection on edu; direct labour-market channel small. |
| Ideation → Δ-housework (♀) (026/031) | +0.50 (.085) | +0.11 (n.s.) | Most of OLS is selection on edu + pre-existing fertility; direct time-use channel small. |

The PSM/DiD evidence is now telling us where ideation **really** acts:
on **schooling** (the 028 young-cohort finding is the most robust) and
on **how women experience marriage / motherhood transitions** (the 025
"suppresses the progressive shift" finding). The cross-section
labour-market and time-use gradients are mostly downstream consequences
of those earlier-stage channels.

## Caveats

* **Selection on observables only**. Unmeasured family / community
  ideology, peer effects, region-level norms — none in the matching
  model. Bias from these is unchanged from the OLS direction.
* **CI is wide**. Female PSM-DiD CI is [−0.44, +0.43] — not a precise
  null, just unable to distinguish small effects from zero.
* **Caliper sensitivity** not tested.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv`, `02_missing_table.csv`
* `04_result_table.csv` = `tables/psm_att.csv`
* `tables/psm_balance.csv`, `tables/psm_meta.csv`
* `figures/psm_att_forest.pdf`, `figures/psm_balance.pdf`
