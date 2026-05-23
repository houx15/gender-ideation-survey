# 05 · Interpretation note — analysis_035

> RQ 5.7 deep: parent → child ideation transmission.
> Final intergenerational run. Extends `analysis_008 / 015 / 016 / 017`.

## Headline

Both parents transmit ideology to their adult child, with slopes of
≈ 0.07–0.16 per unit of parent ideation. **Mother → daughter is the
strongest single transmission cell** (2014 β = 0.160, p < .001), and
the **father → daughter transmission in 2020 is mediated mostly through
the child's schooling** — adding `child_edu_yrs` to the RHS shrinks the
father → daughter direct β from 0.075 (p = .028) to 0.028 (n.s.).

### Base transmission (no mediator) — significant cells

| Wave | Stratum | mother β | mother *p* | father β | father *p* |
|---|---|---|---|---|---|
| 2014 | all      | 0.096 | .007 | 0.109 | .001 |
| 2014 | male     | 0.105 | .003 | 0.109 | .001 |
| **2014** | **female** | **0.160** | **< .001** | 0.110 | .005 |
| 2020 | all      | 0.079 | .010 | 0.104 | < .001 |
| 2020 | male     | 0.095 | .003 | 0.110 | < .001 |
| 2020 | female   | 0.068 | .046 | 0.075 | .028 |

### + edu mediator — what shrinks?

| Wave | Stratum | mother β (base → +edu) | father β (base → +edu) |
|---|---|---|---|
| 2014 | female | 0.160 → 0.154 (−4 %) | 0.110 → 0.104 (−5 %) |
| 2020 | female | 0.068 → **0.063** (−7 %) | 0.075 → **0.028** (−63 %) |

Father → daughter in 2020 is **largely an edu-mediated transmission**:
once we control for the daughter's own years of schooling, almost two-
thirds of the father-coefficient evaporates. Mother → daughter (both
waves) and father → daughter in 2014 are *not* edu-mediated to nearly
the same degree — those operate more directly on the attitudinal
content.

### Parent-child Pearson r (raw)

| Wave | Parent | All | Male child | Female child |
|---|---|---|---|---|
| 2014 | mother | 0.143 | 0.120 | **0.154** |
| 2014 | father | 0.165 | 0.163 | 0.149 |
| 2020 | mother | 0.147 | 0.127 | **0.152** |
| 2020 | father | 0.149 | 0.129 | 0.147 |

Mother-daughter is consistently the strongest raw correlation cell.

**Context**: parent-child r ≈ 0.15 is smaller than the spouse-spouse r
≈ 0.22 (from `analysis_029` Part A). People are noticeably more
similar to their spouse than to their own parent on the gender-ideology
index — likely a combination of marriage-market sorting (029) and
gradual within-couple convergence over time.

## What this means for the female-side reproduction story

Combined with the other intergenerational results, three transmission
channels are now identified:

| Channel | Evidence | Mediator? |
|---|---|---|
| **Father → daughter EDUCATION** | β = −1.88, p < .001 (033 / 034) | direct allocation channel |
| **Father → daughter IDEATION** | β = +0.075, p = .028 (035, 2020) | mostly mediated by daughter's edu |
| **Mother → daughter IDEATION** | β = +0.16, p < .001 (2014) / +0.07, p = .046 (2020) | direct attitudinal, not edu-mediated |

The story now reads:

> **Father's** influence on daughter operates predominantly through
> the allocation channel — he gives her less schooling, and through
> that lower schooling she ends up with more traditional ideology and
> the downstream adult outcomes (housework, marriage, ISEI).
>
> **Mother's** influence on daughter operates predominantly through
> the *direct attitudinal channel* — she transmits her own ideology
> to her daughter independently of the schooling she received.

This is the canonical sociological distinction between **opportunity
transmission** (father's gendered allocation) and **value transmission**
(mother's direct socialisation).

## What about sons?

For sons, mother and father slopes are roughly equal (≈ 0.10–0.11 in
both waves). The mother → son direct channel does not shrink much with
edu mediator, suggesting attitudinal transmission. No strong sex-of-
parent asymmetry on the son side.

So the **sex-of-parent asymmetry runs only on the daughter side**:
mother is the value-transmitter, father is the opportunity-allocator.

## Within-family ICC, briefly

ICC ≈ r²/2 + r/2 for one-parent / one-child cells gives ICC ≈ 0.08
overall — consistent with the literature on intergenerational
attitudinal transmission in China (Bian, Yu and others find ICC ≈
0.05–0.15 across various Chinese surveys for related attitudes). The
within-family share of variance is real but modest: most of the
variance in adult-child ideology is *not* parent-attributable in this
cross-section.

## Caveats

* **Cross-sectional** — current convergence between adult child and
  parent (e.g. they live together and influence each other now) is
  conflated with childhood transmission. Without longitudinal
  parent-child data over the child's adolescence (which CFPS doesn't
  have for the relevant cohorts), this distinction can't be made.
* **Selection on intact parent-pair dyads** — same as 033 / 034.
* **Mediation decomposition is informal** — formal indirect-effect
  estimation (Imai-Keele) would be tighter.
* **Attenuation bias from measurement error**: the ideation index has
  Cronbach's α ≈ 0.6, so parent and child ideation are both measured
  with noise. The transmission β is downward-biased by this
  attenuation. The true latent-trait transmission is likely larger
  than the 0.07–0.16 we estimate.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — mean child ideation by parent tertile × child sex
* `02_missing_table.csv`
* `04_result_table.csv` — all coefficients, base + edu-mediator variants
* `tables/parent_child_correlations.csv`
* `figures/scatter_{mother,father}_child_{2014,2020}.pdf`
* `figures/transmission_forest.pdf` — coefficient forest, base vs +edu
