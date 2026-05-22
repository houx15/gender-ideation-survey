# analysis_018 — Interpretation note

## (1) Siblings resemble each other — but parent ideology is only a small part of why
`01_descriptive_table.csv`:

| Wave | sibling ICC (raw) | after parent ideology | parent ideology explains | after +age+urban |
|------|------------------:|----------------------:|-------------------------:|-----------------:|
| 2014 | 0.260 | 0.230 | **11.4%** | 0.214 |
| 2020 | 0.196 | 0.184 | **6.4%** | 0.125 |

- **~20–26% of the variance in children's ideology is between-family** (siblings are clearly
  alike) — ideology is substantially family-clustered.
- **The parents' *measured* gender ideology accounts for only 6–11% of that sibling
  resemblance.** Most of what makes siblings alike is *other* shared family/community factors
  (region, SES, schooling, local norms) — adding urban/rural removes more (esp. 2020).
- This qualifies the transmission story honestly: parental gender attitudes are a *real but
  modest* channel; the bulk of intergenerational similarity flows through the broader shared
  environment, not the specific attitude score.

## (2) Within a sibship, daughters are less traditional than their own brothers
Family-FE `ideation ~ female + age` (`04_result_table.csv`), net of ALL family-level factors:

| Wave | female (daughter − own brother) | p |
|------|--------------------------------:|---|
| 2014 | **−0.044** | <0.001 |
| 2020 | **−0.101** | <0.001 |

Even comparing a daughter to her **own brother** in the same household, the daughter is
significantly less traditional — and the gap **more than doubled** between 2014 and 2020. This
is the cleanest possible evidence (family-confounders fully absorbed) of the gender divergence
in ideology, and that it is widening — consistent with the cohort crossover (analysis_002) and
the daughters-less-traditional result (analysis_008).

## Bottom line
Ideology is strongly family-clustered, but parents' measured attitudes explain only a small
slice of sibling resemblance; meanwhile, within the same family daughters are increasingly more
egalitarian than their brothers. Transmission is real yet partial, and a within-generation
gender divergence is opening up inside families.

## Caveats
ICC = variance share, not causal; FE can't estimate transmission magnitude; multi-child
families are a selected minority in the one-child-policy era; co-residence-biased; no weights.

## Next steps
ICC by urban/rural & cohort; sibling sex-composition; weights; then provincial ideology climate
as a between-family predictor (deferred).
