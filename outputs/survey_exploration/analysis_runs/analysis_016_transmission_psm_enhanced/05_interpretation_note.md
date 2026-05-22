# analysis_016 — Interpretation note

## Transmission is robust (and now honestly inferred)
`04_result_table.csv` — ATT of having a traditional vs egalitarian parent on child ideation:

| Wave | Spec | ATT | paired SE | **boot SE** | boot 95% CI | boot p |
|------|------|----:|----------:|------------:|-------------|-------:|
| 2014 | all ages, base | 0.057 | 0.0043 | **0.0100** | [0.034, 0.073] | 1.2e-08 |
| 2014 | all ages, +urban | 0.068 | 0.0051 | **0.0092** | [0.046, 0.083] | 2.1e-13 |
| 2014 | **formative 16–30** | 0.052 | 0.0058 | **0.0113** | [0.034, 0.078] | 5.0e-06 |
| 2020 | all ages, base | 0.052 | 0.0057 | **0.0116** | [0.017, 0.062] | 7.7e-06 |
| 2020 | all ages, +urban | 0.039 | 0.0058 | **0.0110** | [0.016, 0.059] | 3.7e-04 |
| 2020 | **formative 16–30** | 0.037 | 0.0078 | **0.0147** | [0.012, 0.069] | 0.011 |

## What this establishes
1. **The transmission effect survives everything we threw at it** — richer matching
   (parent education + urban/rural) and the 16–30 formative window. ATT ≈ 0.04–0.07 on the
   [0,1] index: children of traditional parents are meaningfully more traditional than
   comparable children of egalitarian parents.
2. **Bootstrap SEs are ~2× the paired-t SEs** (e.g. 0.011 vs 0.006 in 2020), confirming the
   earlier caveat that matching-with-replacement made the paired-t p-values too small. But
   even with honest inference the effect is significant in every spec (boot p < 0.05, and
   ≪0.001 in most) and **every bootstrap CI excludes zero**.
3. Adding urban/rural slightly lowers the 2020 estimate (0.052 → 0.039), so a little of the
   raw transmission reflects urban/rural composition — but the core effect persists.

## Bottom line
Gender-ideology regeneration is a robust feature of the data: parental ideology predicts
adult-child ideology net of parent education, urban/rural, and child demographics, in the
formative-age window, under bootstrap inference. The honest effect size is ~0.04–0.07.

## Caveats
Not a clean causal effect (shared environment, genes, co-residence selection); tertile
split; no weights; province/region and family SES not yet in the match.

## Next steps
Family SES + region in the match; family fixed effects; survey weights; later, provincial
ideology climate.
