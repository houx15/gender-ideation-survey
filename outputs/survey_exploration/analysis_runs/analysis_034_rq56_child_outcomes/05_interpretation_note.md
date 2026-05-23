# 05 · Interpretation note — analysis_034

> RQ 5.6 deep: parental ideation → adult child outcomes.
> Extends `analysis_009` / `016` / `017` with the full template.

## Headline

Parental ideology casts a clear shadow over adult children's lives,
**predominantly on the female (daughter) side and predominantly via
the father**. Across nine outcomes, the largest and tightest effects
are:

### CFPS 2020 (significant parent → child effects, |p| < .05)

| Outcome | Child sex | Parent | β | *p* | Substantive |
|---|---|---|---|---|---|
| **ISEI prestige** | **daughter** | **father** | **−12.03** | **.002** | Daughters of traditional fathers in 12-pt-lower-ISEI occupations |
| `edu_yrs` | daughter | father | **−1.88** | < .001 | (matches 033's allocation finding) |
| `edu_yrs` | son | mother | **−1.02** | .026 | (matches 033's opposite-sex pattern) |
| `marriage_sat` | daughter | mother | **−0.82** | .012 | Traditional mother's daughters report ≈ 0.8 Likert-pts *lower* marriage satisfaction |
| `housework_hours` | daughter | mother | **+0.68** | .015 | Traditional mother's daughters do ~0.7 hr/day more housework |
| `currently_married` | daughter | father | +0.137 | .039 | Slightly more likely currently married |
| `employed` | all child | father | +0.145 | .012 | Traditional father's adult children slightly more likely employed |

### CFPS 2014

| Outcome | Child sex | Parent | β | *p* |
|---|---|---|---|---|
| `ideal_children` | daughter | mother | +0.31 | .023 |
| `currently_married` | all | mother | +0.13 | .065 (marginal) |
| `employed` | daughter | mother | −0.25 | .045 |

## The clean female-side father-channel

The single most striking result: **father → daughter ISEI = −12.03
(p = .002, n = 472)**. The daughter's own ideation, even in OLS, was
−5.57 (027), and PSM destroyed that to −1.20 (030, n.s.). But the
father's ideation effect on his adult daughter's ISEI is more than
**twice as large** as the daughter's own ideation effect — and survives
HC1 inference at p = .002.

This pattern repeats across outcomes:

| Outcome | Father → daughter | Mother → daughter |
|---|---|---|
| edu_yrs              | **−1.88** (.001) | −0.22 (n.s.) |
| ISEI                 | **−12.03** (.002) | **+6.16** (.10, marginal — note POSITIVE) |
| currently_married    | **+0.137** (.039) | +0.13 (n.s. within stratum) |
| marriage_sat         | n.s.             | **−0.82** (.012) |
| housework_hours      | n.s.             | **+0.68** (.015) |

Notable: the mother → daughter ISEI is *positive* and marginal (+6.16,
p = .10). One plausible reading: a traditional mother who has herself
been pushed out of the higher-prestige labour market may explicitly
push the daughter toward education + a "respectable job", partially
offsetting the father's underinvestment. But this is speculation; the
marginal p value warrants caution.

## Through three generations

Combined with 028 (the daughter's own ideation effect on her own edu)
and 029 (the matching pattern she ends up in) and 025 (how marriage
reinforces her ideology), this run completes the multigenerational
female-side picture:

```
Father (traditional)
  └─► invests less in daughter's education          (033, 034: β = −1.88)
       └─► daughter completes less schooling
            └─► she herself holds more traditional ideology
                 └─► she acquires even less additional schooling     (032: ATT = −0.64)
                      └─► she marries educationally up               (029 A2: β = +0.29)
                           └─► she does more housework               (031: ATT = +0.11, OLS β = +0.58)
                                └─► her marriage reinforces her ideology (025: ATT = +0.05–0.08)
                                     └─► she invests less in HER daughter… (repeats)
```

Each step has empirical support. Not all steps are causally identified
in the strictest sense, but the consistency of direction and the
several PSM/DiD-surviving links in 025 + 032 + this run's father→daughter
ISEI make it a **defensible reproduction story across two adult
generations of Chinese women in CFPS**.

## What about sons?

The male-child side has a few significant cells but they don't form
a coherent picture in the same way:

* Mother → son edu: −1.02 (significant) — sons of traditional mothers
  less educated. Same pattern as the daughter side but for sons,
  driven by mother.
* Father → son: mostly n.s. across outcomes.
* Mother → son wage: −0.69 (marginal, p = .07) — sons of traditional
  mothers earn slightly less, consistent with the edu effect upstream.

So the **mother → son** channel is real and consistent with a "mother's
investment in son's schooling shapes his earnings later". But the
magnitudes are smaller than the father → daughter channel, and the
mother → son channel does not have the dense secondary architecture
(marriage, housework, ISEI) that the father → daughter channel has.

## Caveats

* **Cross-sectional**: parent ideology measured now, child outcomes
  measured now. Parents who ended up traditional may have done so
  *because* of the child's trajectory, not the other way. The
  "parents shape children" reading is the natural one (parents'
  ideology in adolescence was *also* traditional) but cannot be
  separated from "shared cohort / regional / family-SES confounders".
* **Selection on intact parent-pair dyads** as in 033.
* **Multiple comparisons risk**: 108 ideation-coefficient cells fitted;
  some will be significant by chance. The substantive interpretation
  weights the cells where the direction + significance + magnitude
  cohere across outcomes (father → daughter; mother → son edu) over
  individual marginal cells.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — mean outcome by parent tertile × child sex
* `02_missing_table.csv`
* `04_result_table.csv` — every term × outcome × wave × stratum
* `figures/summary_forest_parent_to_child.pdf`
* `figures/forest_{outcome}.pdf` — per-outcome focused forest
