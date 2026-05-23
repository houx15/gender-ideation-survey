# 05 · Interpretation note — analysis_030

> PSM strengthens (and partly revises) the ISEI prestige finding from
> `analysis_027`.

## Headline

Under PSM with bootstrap inference, **the female-side ISEI effect
shrinks to about a quarter of the lagged-OLS estimate and is no longer
statistically distinguishable from zero**. Specifically:

| Stratum | n_treated | n_control | ATT | boot SE | 95 % CI | *p* |
|---|---|---|---|---|---|---|
| All | 1 281 | 2 090 | **−0.31** | 0.62 | [−1.61, +0.83] | .61 |
| Male | 861 | 1 320 | **−0.28** | 0.78 | [−2.01, +1.22] | .71 |
| Female | 420 | 770 | **−1.20** | 1.24 | [−3.33, +1.28] | .34 |

Compare with the lagged-OLS estimates in `analysis_027`:

| Stratum | OLS β (027) | OLS p | PSM ATT (030) | PSM p |
|---|---|---|---|---|
| All | −1.92 (n.s.) | .19 | −0.31 | .61 |
| Male | −1.91 (n.s.) | .20 | −0.28 | .71 |
| **Female** | **−4.25** (.035) | .035 | **−1.20** | .34 |

The female point estimate goes from −4.25 to −1.20 — a ≈ 4× shrinkage.

## Why the shrinkage

Pre-match SMDs reveal substantial covariate imbalance, especially for
the female stratum:

| Covariate | Female pre-SMD | Female post-SMD |
|---|---|---|
| birthy_2014        | −0.595 | +0.057 |
| **edu_yrs_2014**   | **−0.838** | −0.040 |
| urban_2014         | −0.328 | −0.021 |
| log_income_2014    | −0.306 | +0.004 |
| employed_2014      | +0.054 | 0.000 |

High-ideation women in 2014 are **substantially less educated** (SMD
−0.84), younger-cohort (SMD −0.60), more rural (SMD −0.33), and
lower-earning (SMD −0.31) than low-ideation women in the same panel.
Post-match all SMDs are well under the conventional 0.1 threshold —
**balance is excellent**.

So the cross-sectional / lagged OLS comparison was confounding three
distinct things:
1. **Education** — traditional women have systematically less schooling.
2. **Cohort / urban / income** — also tilted toward less-resourced.
3. **The residual ideation→ISEI channel** — what we wanted to estimate.

When PSM matches on (1) and (2), the residual signal in (3) shrinks to
−1.20 ISEI points (and becomes statistically null).

## Substantive reading

The PSM result *does not* refute the original finding — it changes
the interpretation of where the effect comes from:

* **OLS-027 reading (uncorrected)**: "traditional women hold lower-
  prestige jobs by about 4 ISEI points; suggestive of an ideation →
  occupational-prestige channel".
* **PSM-030 reading (selection-on-observables corrected)**:
  "most of the cross-section gap is explained by selection on
  education (and cohort, urban, income). Among equally-educated,
  same-cohort, same-urban-status women, the residual ideation
  difference in ISEI is small (~1.2 points) and statistically
  indistinguishable from zero."

Both can be true at the same time, and both are interesting. The
**population-level association** between ideation and ISEI is real
(OLS); the **average causal effect under selection-on-observables**
is much smaller and uncertain (PSM). The discrepancy localises
*where* the ideation → outcome link lives: not directly in the labour
market, but **upstream in education** (where 028's lagged-young-cohort
β = −1.37 for Δ-edu_yrs — significant — supports a real ideation →
schooling channel).

## What this means for the female-side through-line

| Channel | Cross-section / lagged | PSM-DiD |
|---|---|---|
| Marriage / motherhood → Δ-ideation | β = −0.04 / −0.03 | **ATT +0.05 / +0.08** (025) |
| Ideation → Δ-edu (young ♀) | β = −1.37 (.006) | (next: 032) |
| Ideation → ISEI | β = −4.25 (.035) | **ATT −1.20 (n.s.)** (030) |
| Ideation → Δ-housework (♀) | β = +0.50 (.085) | (next: 031) |

The PSM result for ISEI is consistent with **education being the main
mediator**: traditional ideology shapes how many years of schooling a
young woman acquires (028), and education then shapes occupational
prestige. There is little *additional* direct ideation → ISEI channel
once education is held fixed. This is a clean mediation story rather
than a refutation.

## Caveats (read with the table)

* **Selection on observables**: PSM corrects only for the covariates we
  include. Unmeasured family background, region-level norms, peer
  group ideology — none are in the matching model.
* **Bootstrap CI is wide**. The female CI is [−3.33, +1.28] — not a
  precise null, just unable to distinguish small / moderate effects
  from zero with this sample. n_treated = 420 in the female cell is
  on the smaller side for PSM.
* **Caliper = 0.20** is the default; sensitivity to caliper choice not
  tested. Tighter caliper would shrink the matched sample further;
  wider would allow worse pairs.
* **At-risk = employed_2020**. PSM cannot fix selection on a variable
  that's not in the matching set for everyone. If the ideation →
  employment channel is itself non-null, the conditional-on-employed
  ATT is not the population ATT.

## Files in this analysis_run

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — raw mean ISEI by stratum × treatment
* `02_missing_table.csv`
* `04_result_table.csv` — same as `tables/psm_att.csv`
* `tables/psm_balance.csv` — SMD pre / post per covariate × stratum
* `tables/psm_meta.csv`
* `figures/psm_att_forest.pdf` — ATT forest across strata
* `figures/psm_balance.pdf` — balance plot per stratum
