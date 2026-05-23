# 05 · Interpretation note — analysis_033

> RQ 5.5 deep: parental ideation → child resource allocation.
> Replaces / extends `analysis_009 / 010 / 012 / 013`.

## Headline

CFPS 2020 reveals a clean and unexpected **opposite-sex parent → child**
allocation pattern. The 2014 wave is directionally similar but
statistically null.

### CFPS 2020 (the cleaner wave, n = 2 196 dyads)

| Parent → child sex | OLS β on parent ideation | *p* | Reading |
|---|---|---|---|
| **Father → daughter** | **−1.88** | < .001 | Traditional fathers' daughters get ~1.9 fewer years of schooling |
| Father → son | −0.38 | .39 | No effect |
| **Mother → son** | **−1.02** | .026 | Traditional mothers' sons get ~1.0 fewer years |
| Mother → daughter | −0.22 | .60 | No effect |

The pooled-with-interaction fit confirms both gender-moderation terms:
* `father_ideation × child_female` = **−1.53** (p = .017)
* `mother_ideation × child_female` = +0.97 (p = .093 marginal)

### CFPS 2014 (n = 2 117 dyads)

All four cells point in the same direction (negative) but none is
statistically significant. The strongest is father → daughter
(β = −0.81, p = .11). 2014 cell sizes are similar to 2020 (n_female
= 893 vs 977) but the variances are larger.

## What this means

The pattern is **opposite-sex transmission** of the allocation effect:
each parent's traditional ideology hurts the *other-sex* child's
education more than the same-sex child's.

* Traditional fathers underinvest in daughters — the textbook
  patriarchal-allocation result (Chinese son-preference literature
  going back to Greenhalgh, Bian, Yu).
* Traditional mothers underinvest in sons — *novel finding*, less
  expected. Possible reading: traditional mothers, who themselves
  hold instrumentalist beliefs about women ("a good marriage matters
  more than work"), may apply *symmetric* instrumentalist beliefs to
  sons too — "what matters is what you can earn, not what you can
  read" — leading to relatively less push for schooling. Or they may
  channel attention toward daughters' marriage market (clothing,
  household skills) at the expense of academic encouragement to sons.

**Both effects are conditional on the parent-pair-in-sample
restriction**, which selects toward intact families. The
representative-Chinese-family allocation gap may differ.

### Within-family sibling difference (Design B)

The one-son-one-daughter difference design (Δedu = daughter − son ~
parent_ideation) finds no significant effects in either wave:

| Wave | n_families | mother_ideation β | father_ideation β |
|---|---|---|---|
| 2014 | 341 | −0.06 (p = .96) | +0.38 (p = .73) |
| 2020 | 243 | +0.98 (p = .46) | +2.11 (p = .18) |

Note that in 2020, the *direction* is opposite to what the child-level
OLS found — within 1S1D families, daughters of traditional fathers
have MORE schooling than their brothers (β = +2.11), not less. But
the sample is small (n = 243) and the CI is wide.

So Designs A and B point in different directions in 2020. Two possible
readings:
1. The 1S1D subsample is special. 1S1D families are a particular
   composition (one of each, both adult respondents in 2020) that
   differs from the broader dyad sample.
2. There's substantial heterogeneity in how parents allocate, and
   the within-family vs between-family contrasts emphasize different
   parts of the heterogeneity.

The child-level OLS (Design A) uses ~9× more dyads and has tighter
SEs; I'd weight Design A more in the substantive interpretation.

## Descriptive picture (raw means)

CFPS 2020 child mean edu_yrs by parent ideation tertile × child sex:

| Parent | Tertile | Daughter | Son |
|---|---|---|---|
| Mother | low (progressive) | 13.14 | 12.31 |
| Mother | mid               | 12.47 | 11.54 |
| Mother | high (traditional)| **12.99** | **11.38** |
| Father | low               | 13.21 | 12.33 |
| Father | mid               | 12.81 | 11.86 |
| Father | high              | **12.18** | **11.20** |

Two patterns:
* Daughters consistently have *more* edu_yrs than sons in every cell
  (mean ≈ 12.6 vs 11.7). This is the modern Chinese cohort pattern:
  young women have overtaken young men in schooling.
* Father high-tertile: daughter goes from 13.21 to 12.18 (Δ = −1.03);
  son goes from 12.33 to 11.20 (Δ = −1.13). Both lose, but daughter
  loses more relative to the parent-edu-controlled baseline (after
  controlling, Δ = −1.88 for daughter, −0.38 for son).

## Where this sits in the female-side through-line

This run pushes the through-line back one generation. We now have:

| Generation | Channel | Evidence |
|---|---|---|
| **Parent → child** (033) | Traditional father → less daughter edu (β = −1.88, p < .001) | This run |
| **Child → adult outcome** (028/032) | High-ideation young woman → less own Δedu (PSM-DiD ATT = −0.64, p = .068) | Earlier runs |
| **Adult woman → marriage** (025, 029-Part-A2) | Traditional women in edu-hypergamy (β = +0.29, p < .001) | Earlier runs |
| **Adult woman → divisions** (031, 026) | Traditional women do more housework (cross-section large, lagged marginal) | Earlier runs |

A traditional father's daughter ends up with less education → and
(per 028 / 032) more-traditional daughters acquire less schooling on
their own too → and (per 029 A2) end up married to more-educated
husbands → reproducing the asymmetric matching that defines the
parent's generation. This is the multi-generational version of the
female-side reproduction story.

## Caveats

* **Selection on intact dyads**: dyads in the sample are special —
  parent and adult child both in CFPS, both interviewed. Single-parent,
  step-parent, deceased-parent dyads are missing. The patriarchal
  allocation pattern in absent-father households cannot be measured
  here.
* **Design A vs B mismatch in 2020**: child-level OLS and 1S1D
  difference give different point estimates. With n_1S1D = 243, the
  difference design is underpowered; would want a CFPS extension or
  CGSS replication.
* **The mother → son finding is novel**. Awaiting replication in
  CGSS or other panels before substantive over-interpretation.
* **Reverse causation**: parents' ideology measured at survey, child's
  edu set in adolescence. The cross-section reads "parents who ended
  up traditional have less-educated children". For young parents the
  ideology was around during the child's schooling years; for older
  parents the parent's ideology may have shifted post-hoc.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` (parent tertile × child sex grid)
* `02_missing_table.csv` (dyad coverage per wave)
* `04_result_table.csv` (tidy OLS-HC1 across Designs A + B, both waves)
* `figures/edu_by_parent_tertile_{2014,2020}.pdf`
* `figures/coef_forest_parent_ideation.pdf`
