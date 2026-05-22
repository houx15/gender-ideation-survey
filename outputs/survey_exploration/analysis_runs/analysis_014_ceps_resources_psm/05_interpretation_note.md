# analysis_014 — Interpretation note

## Results (PSM ATT of being a daughter, with p-values; `04_result_table.csv`)

| Outcome | naive girl−boy | PSM ATT | p | robust? |
|---------|---------------:|--------:|---|---------|
| parent expects college | +0.042 | **+0.049** | <0.0001 | yes (stable) |
| tutoring participation | +0.047 | **+0.060** | <0.0001 | yes (stable) |
| log tutoring cost | +0.347 | **+0.345** | <0.0001 | yes (stable) |
| own study desk | +0.014 | **−0.063** | <0.0001 | flips with matching |
| near-daily homework help | −0.043 | +0.004 | 0.50 | n.s. after matching |
| weekly housework hours | +0.637 | **−0.504** | 0.007 | flips with matching |

## What's robust vs what's confounded
1. **Robust: daughters receive MORE educational investment.** College expectations,
   tutoring, and tutoring spending all favour girls and are essentially unchanged by
   matching (p<0.0001). This is the solid finding.
2. **Confounded by family structure: chores and own desk.** The raw "girls do ~0.6 more
   hours of chores" **reverses to −0.5 (p=0.007)** once we match on sibship size and SES,
   and the desk gap turns negative. The likely mechanism: **son-biased fertility** — families
   that wanted a son kept having children, so girls are over-represented in **larger sibships**,
   where every child does more chores and private resources (a desk) are diluted. Comparing
   children in *similar* family structures, the raw girl chore-burden largely reflects *family
   structure*, not gender treatment per se.
3. **Homework help:** no gender difference once matched (p=0.50).

## Caveat (important)
Because child sex is quasi-random, the propensity model is weak and PSM mainly reweights on
family structure, so the *flipped* estimates (chores, desk) are **specification-sensitive**
(they hinge on including sibship size). Read them as "the raw gap is a family-structure
artifact", not as a robust reverse gap. The education-investment findings, stable across
specifications, are the dependable ones.

## How this connects to the ideology question
CEPS still cannot attach parental ideology (no item, no geography). But analysis_013 (CFPS)
shows the ideology signal lands on the **demand/chores** channel — and analysis_014 shows the
raw chore gap is heavily structured by **son-biased fertility**. Together they suggest the
gendered domestic-labour burden is produced jointly by **traditional ideology** *and*
**son-preference fertility behaviour**, more than by unequal schooling investment (where
girls, if anything, do better).

## Next steps
Covariate-set sensitivity (with/without sibship); caliper + bootstrap SEs; hukou/region;
IPW/entropy balancing; merge a CFPS children file to bring ideology to the investment side.
