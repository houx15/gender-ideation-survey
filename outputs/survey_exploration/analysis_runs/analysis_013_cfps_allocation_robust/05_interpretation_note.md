# analysis_013 — Interpretation note

## Headline (now with p-values): parental ideology shapes the DEMAND side significantly
The formal moderation test `female × parent_ideology` (`interaction_test_table.csv`):

| Outcome | Wave | female×parent_ideology | p | Reading |
|---------|------|------------------------|---|---------|
| Housework | 2014 | **+0.67** | **0.038** | traditional parents → daughters do more chores rel. to sons |
| Housework | 2020 | **+1.23** | **0.022** | same, larger |
| Education | 2014 | −2.60 | 0.061 | traditional parents erode daughters' schooling edge (marginal) |
| Education | 2020 | −1.38 | 0.216 | same direction, not significant |

**So parental gender ideology significantly increases daughters' relative housework burden
(p<0.05 in both waves), and suggestively reduces their relative education (marginal in 2014).**

## What each rung adds
- **Rung 2 (within-family, all mixed-gender, 129–503 families):** parent-ideology coefficient
  on the gender gap is non-significant for both education and housework (p ≥ 0.13) — the
  within-family contrast is clean but still underpowered.
- **Rung 3 (PSM, all families) with ideology strata (`psm_result_table.csv`):**
  - *Education:* daughters get MORE schooling than matched sons overall (2014 +1.14; 2020
    +0.54; p<0.001), but the advantage is **concentrated in egalitarian families** — in
    traditional families it shrinks (2014 +0.90) or **disappears** (2020 −0.18, p=0.46).
  - *Housework:* daughters do significantly more everywhere; in 2020 the burden is far
    heavier in **traditional** families (+0.94, p<0.001) than egalitarian (+0.23).
  - The moderation OLS confirms the housework pattern is statistically significant.

## Bottom line
Earlier (analysis_012) we could only say "directionally son-favouring, not significant."
With the expanded sample, PSM, and a formal moderation test, the picture sharpens:
**parental traditionalism does NOT make parents educate daughters less in a clearly
significant way, but it DOES significantly raise the housework daughters do relative to
their brothers.** Ideology bites hardest on the *domestic-labour* channel — exactly the
self-enacted/demand side that recurs throughout this project (analysis_004/007).

## Caveats
Linked-sample co-residence selection (rungs 3 & moderation); limited PSM covariates;
cross-sectional; no weights. Stratified ATTs test within-stratum gaps; the moderation OLS
is the proper across-stratum test.

## Next steps
Richer match covariates + clustered SEs + weights; pool waves; CGSS time-use replication of
the housework moderation; CEPS for the investment side measured during schooling (analysis_014).
