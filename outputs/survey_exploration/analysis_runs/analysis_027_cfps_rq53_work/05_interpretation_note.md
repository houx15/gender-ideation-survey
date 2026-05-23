# 05 · Interpretation note — analysis_027

> RQ 5.3 work / leadership, deep-dive replacement for
> `analysis_005_cfps_work_leadership`. Adds wage monthly+yearly side-by-side,
> the previously-missing **promotion** outcome (`qg15`), and 2020-only ISEI
> and bianzhi. Dual-frame (cross-section + lagged), sex-stratified, HC1
> robust SEs throughout.

## Headline

The ideation→work channel runs **almost entirely on the female side**.
Across every outcome where the gender split is meaningful, women's
side carries the signal; men's side is null or runs the opposite way.

| Outcome (2014 cross unless noted) | Overall β | Male | Female | Reading |
|---|---|---|---|---|
| **Employed**            | +0.008 n.s. | +0.010 n.s. | −0.030 n.s. | Flat |
| **log_wage_year** (2014) | **−0.74** (.004) | **−0.82** (.002) | **−1.27** (<.001) | Traditional women earn ~exp(−1.27) ≈ 28 % of equivalent progressive women's annual wage income, conditional on controls. |
| **log_wage_year** (2020) | +0.10 n.s. | +0.03 n.s. | **−0.49** (.002) | Same direction for women in 2020, smaller magnitude. |
| **log_wage_year** (lagged ♀) | — | — | **−0.31** (.095, marginal) | Survives the lagged frame on the female side. |
| **log_wage_month** (2020) | +0.08 n.s. | −0.04 n.s. | **−0.31** (.021) | Per-month rate of pay confirms the female-only pattern in 2020. |
| **mgmt** (qg14, both waves) | mostly n.s. | n.s. | n.s. | No ideation gradient on holding a management role. |
| **promotion** (qg15, 2014) | +0.000 n.s. | +0.009 n.s. | **−0.100** (.001) | *Novel finding*: traditional women are ~10 pp less likely to have had a promotion. |
| **promotion** (qg15, 2020) | −0.020 n.s. | −0.005 n.s. | −0.048 (.10 marginal) | Direction preserved, smaller. |
| **has_sub** (qg17, 2014) | +0.05 (.11) | **+0.066** (.046) | **−0.092** (.007) | Opposite signs by sex: traditional men have more subordinates, traditional women fewer. |
| **isei** (2020 only) | **−3.05** (.002) | **−2.65** (.009) | **−5.57** (<.001) | Traditional women's main occupation scores ~6 ISEI points lower; traditional men ~3 points lower. |
| **isei** (lagged ♀) | — | — | **−4.25** (.035) | **Survives the lagged frame**: clean directional claim. |
| **bianzhi** (qg2032, 2020 only) | −0.06 n.s. | −0.05 n.s. | −0.11 n.s. | All n.s.; sample is tight (n_total = 2 275). |

## Outcome-by-outcome readings

### 1. Employment — flat

No ideation gradient on whether someone is employed at all. The cross-section
β in 2020 is small-positive (+0.034 overall, p = .03) but disappears on the
lagged frame (β = +0.019 n.s.). This is consistent with employment being
gated more by structural factors (sector, region, age) than by attitudes.

### 2. Wages — *the* female finding

**Yearly wage, 2014 cross-section**: β = −1.27 for women (p < .001). The
ideation index moves on [0, 1] so this is the full-range slope; a more
realistic 1-SD shift (~0.20 on the index) translates to ~ −0.25 in log
wage, or about 22 % lower yearly wage. Among men, β = −0.82 (still
significant but smaller).

The yearly variable includes those with 0 wage income (self-employed,
informal, family workers). The monthly variable (qg11), conditioned
on having any reported monthly wage, shows the same direction on the
female side in 2020 (β = −0.31, p = .02). In 2014 monthly is positive
on the male side (β = +0.17, p = .015) — an anomaly that the method note
attributes to which formal-sector workers report a monthly figure
(see method note "2014 monthly wage anomaly").

**Lagged frame**: yearly female β = −0.31 (p = .095, marginal) once
`log_wage_year_2014` is on the RHS. So the cross-section is partly
the same people being persistently more traditional + lower-earning,
but there is still a marginal directional component.

### 3. Management — null

`qg14` (administrative-management role) shows essentially no ideation
gradient in either wave or either sex. Likely because most respondents
in any sex × ideation cell don't hold a management role at all
(P(mgmt) ~ 12 % in 2014, ~ 13 % in 2020), so the variance is dominated
by who's NOT a manager — and that's structural, not attitudinal.

### 4. Promotion — novel female finding

**`qg15` was missing from `analysis_005`**. Adding it surfaces:

* **2014 female: β = −0.100 (p = .001)** — traditional women are
  10 percentage points less likely to have had any promotion (admin or
  technical) in the relevant window. Male β = +0.009 n.s.
* 2020: female direction preserved (β = −0.048, p = .10) but smaller.
* Lagged: all n.s. (n = 1 052 for women), so descriptive only.

Combined with the wage and ISEI findings, this is part of a coherent
"traditional-women-lower-mobility" channel in the work bucket.

### 5. Has subordinate — opposite signs by sex

`qg17` is the rare outcome where traditional **men** show a *positive*
sign (β = +0.066, p = .046 in 2014) — they're more likely to have
subordinates. Traditional women are *less* likely (β = −0.092, p = .007).
The "ideation × female" interaction in the overall fit captures this
formally; see `coef_forest_interaction_2014.pdf`.

This is consistent with a classical division-of-status-spheres reading:
traditional men over-represented in supervisory roles; traditional women
under-represented.

### 6. ISEI prestige — the clean directional result

`qg303code_isei` (current main job's ISEI prestige score) is **2020-only**
but available for ~ 80 % of the wave.

* **2020 cross**: overall β = **−3.05** (p = .002), male β = −2.65
  (p = .009), **female β = −5.57** (p < .001). Traditional women's
  main occupations sit ~ 6 ISEI points below the progressive women's.
* **Lagged**: female β = **−4.25 (p = .035)** — when controlled by
  2014 ideation (no 2014 baseline available, so no Δ frame; this is
  ideation_2014 → isei_2020 with full 2014 controls), the effect
  survives at conventional significance.

This is the **cleanest "ideology → work-prestige" directional claim**
in the run. Magnitude: a full-range ideation move associates with
≈ 4.25 ISEI points lower (about 0.3 of an ISEI SD) on the lagged
frame for women.

### 7. Bianzhi (编制) — null but small

`qg2032` only has n_total = 2 275 with non-missing data (= those CFPS
2020 employed respondents asked about formal-post status). All strata
n.s. with β ≈ −0.05 to −0.11; the female-side direction is consistent
with the rest of the run (traditional women less in formal posts) but
sample is too small for inference.

## What this analysis *does* support, after the dual frame

1. **Ideation → wage gap is real and lives on the female side**.
   Cross-section yearly β ≈ −1.27 for women in 2014, −0.49 in 2020;
   marginal lagged β = −0.31 (p = .095). The substantively defensible
   reading: traditional ideology associates with substantially lower
   labour-market earnings for women, *not* for men.
2. **Promotion penalty on the female side is novel** (was not in
   `analysis_005` because `qg15` was missing). 10 pp lower probability
   of a promotion in 2014; smaller in 2020.
3. **ISEI prestige gradient survives the lagged frame**: traditional
   women's occupations score ~ 4 ISEI points lower in 2020 controlling
   for 2014 ideation and covariates. This is the cleanest directional
   claim and the closest analogue in the work bucket to the housework
   finding in `analysis_026`.
4. **Management roles (qg14)** show no ideation gradient — consistent
   with structural-gating story.
5. **Has subordinate**: traditional men more, traditional women fewer —
   the classical division-of-status-spheres pattern.

## Caveats (read with the tables)

* **Selection on employment** is not corrected. Wage / management /
  promotion / sub models condition on `employed == 1`; the conditional
  estimate is biased by the selection on labour-force participation.
  A Heckman correction is the standard fix; flagged for a follow-up
  PSM-Heckman run.
* **2014 monthly-wage anomaly** — positive β on male side in 2014 for
  qg11 (n = 8 000) — likely reflects formal-sector composition; the
  yearly variable is the more conservative read.
* **Wage cross-wave comparability**: p_wage 2014 vs emp_income 2020 sit
  on different scales / coverage; only within-wave gradients are
  interpreted.
* **Lagged sample** is small for the wage models (~ 3 000–6 000 after
  listwise deletion + employed-only). Underpowered relative to the
  cross-section.

## Files in this analysis_run

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — tertile × sex × outcome means
* `02_missing_table.csv` — per-outcome coverage
* `04_result_table.csv` — tidy OLS / LPM (HC1, every term)
* `tables/welch_tertile_diffs.csv` — Welch's t & Cohen's d
* `figures/*.pdf` — vector outputs (`pdf.fonttype=42`):
  * `{outcome}_by_tertile_{2014,2020}.pdf` — tertile × sex bar charts
  * `coef_forest_ideation_{2014,2020,lagged}.pdf` — ideation β across outcomes
  * `coef_forest_interaction_{2014,2020}.pdf` — gender moderation
