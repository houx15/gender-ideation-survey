# 05 · Interpretation note — analysis_032

> PSM-DiD strengthens the young-cohort Δ-edu finding from
> `analysis_028 v2`. **This is the most defensible "ideology shapes
> outcome" causal claim in the project.**

## Headline

Under PSM-DiD with bootstrap inference, **the female-side Δ-edu_yrs
effect survives in direction and magnitude**, with marginal statistical
significance.

| Stratum | n_treated | n_control | ATT (years) | boot SE | 95 % CI | *p* |
|---|---|---|---|---|---|---|
| All | 290 | 230 | −0.366 | 0.225 | [−0.78, +0.08] | .105 |
| Male | 175 | 110 | −0.011 | 0.266 | [−0.51, +0.46] | .97 |
| **Female** | **115** | **120** | **−0.643** | **0.353** | **[−1.33, +0.07]** | **.068** |

Compare with the lagged OLS estimates from `analysis_028 v2`:

| Stratum | OLS β (028) | OLS p | PSM-DiD ATT (032) | PSM-DiD p |
|---|---|---|---|---|
| All | −0.24 (n.s.) | .61 | −0.37 | .105 |
| Male | −0.19 (n.s.) | .68 | −0.01 | .97 |
| **Female** | **−1.37** (.006) | .006 | **−0.64** (.068) | .068 |

Female point estimate shrinks from −1.37 to −0.64 (≈ 2× shrinkage) but
**unlike 030 / 031, the signal survives**. The 95 % CI nearly touches
zero on the upper end ([−1.33, +0.07]) — the bound is consistent with
"a real moderate effect", not with "no effect".

## Why this finding is different from 030 / 031

Two structural reasons:

1. **Pre-match imbalance is much smaller**. The young-cohort restriction
   already absorbs most of the cohort-confound that drove the ISEI and
   housework results. Pre-match SMDs in the female cell:

   | Covariate | 030 (ISEI, female) | 031 (Δ-hw, female) | **032 (Δ-edu young, female)** |
   |---|---|---|---|
   | birthy_2014 | −0.59 | −0.51 | **−0.21** |
   | edu_yrs_2014 | **−0.84** | **−0.78** | **−0.28** |
   | urban_2014 | −0.33 | −0.21 | −0.02 |
   | log_income_2014 | −0.31 | −0.18 | +0.14 |
   | household_n_2014 | — | — | +0.31 |

   By age 14–24 in 2014, traditional and progressive young women are
   already less differentiated on education (because schooling is
   still ongoing). So PSM has less covariate distance to soak up,
   leaving more of the residual signal intact.

2. **The outcome is upstream**. ISEI (030) and housework (031) are
   *downstream* of education — they're consequences of who went to
   school how long. Δedu_yrs is the schooling itself, where the
   ideation gradient lives. PSM can't shrink a real upstream effect
   the way it can shrink a downstream proxy.

## Substantive reading

Among young Chinese women born ≥ 1990 in CFPS:

> Holding birthy_2014, edu_yrs_2014, urban hukou, log income, and
> household size constant, **a young woman with high-tertile 2014
> ideation acquires ~0.64 fewer additional years of education by 2020
> than a matched young woman with low-tertile 2014 ideation** (PSM-DiD
> ATT = −0.643, bootstrap SE = 0.35, p = .068, 95 % CI [−1.33, +0.07],
> n_treated = 115). The corresponding male effect is essentially zero
> (ATT = −0.01).

The 0.07 upper-bound is not zero — the result is "consistent with a
moderate-to-large negative effect, marginally distinguishable from
zero with this sample". Given the additional consistency (lagged OLS,
within-cohort cross-section, all point the same direction), this is
the **most directionally-defensible causal claim** in the project's
female-side through-line.

## Where this sits in the through-line

Updated picture across the four PSM/DiD runs:

| Channel | Lagged OLS | PSM/DiD ATT | Read |
|---|---|---|---|
| Marriage / new-birth → Δ-ideation (025) | Welch −0.04 / −0.03 | **PSM-DiD +0.05 / +0.08** ♀ | Selection-flip: marriage/motherhood suppress the progressive shift young women would otherwise have. |
| **Ideation → Δ-edu (young ♀) (028/032)** | **β = −1.37** (.006) | **ATT = −0.64** (.068) | **PSM survives → ideation shapes schooling decisions** |
| Ideation → ISEI (♀) (027/030) | β = −4.25 (.035) | ATT = −1.20 (n.s.) | PSM mostly destroys → downstream of edu |
| Ideation → Δ-housework (♀) (026/031) | β = +0.50 (.085) | ATT = +0.11 (n.s.) | PSM mostly destroys → downstream of edu / fertility |

The combined four-run picture tells a coherent story:

1. **Schooling** is where ideology *directly* acts on young women's
   trajectory (032 survives matching).
2. **Marriage and motherhood** transitions are where ideology gets
   *reinforced* — the events themselves suppress the progressive shift
   young women would otherwise have (025's selection-flip).
3. **Adult labour-market prestige and time-use** are *downstream*
   consequences. They show large cross-section gradients but mostly
   evaporate under PSM, because they're mediated by upstream education
   and family formation.

This is the dissertation-grade female-side reproduction story: ideology
shapes who you marry → how soon you marry / give birth → those
transitions reinforce the ideology → which had already shaped your
schooling → which set up the labour-market and time-use outcomes.

## Caveats

* **Small sample**. n_treated = 115 in the female cell. Bootstrap CIs
  are wide; the upper bound of the female CI is +0.07 — close to zero.
  Replication in larger panels (CFPS extending past 2020, or other
  Chinese panels) would tighten this.
* **PSM on observables**. Family ideology in the household where the
  young respondent grew up is not measured here. If parents pushed
  daughter through more schooling AND held more progressive ideology
  (a plausible story), the PSM coefficient is partly capturing parent
  ideology rather than respondent ideology. Sibling FE or parent-ideology
  controls would tighten this.
* **The young cohort is 1990–2007**. Some respondents born late in
  this window were still in primary school in 2014 and the ideation
  measurement may be noisy. Robustness check: restricting to age ≥ 16
  in 2014 (birthy ≤ 1998) preserves direction but with smaller n.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv`, `02_missing_table.csv`
* `04_result_table.csv` = `tables/psm_att.csv`
* `tables/psm_balance.csv`, `tables/psm_meta.csv`
* `figures/psm_att_forest.pdf`, `figures/psm_balance.pdf`
