# analysis_017 — Interpretation note

## Result: transmission survives the SES proxy
`04_result_table.csv` (CFPS 2014, ATT of traditional vs egalitarian parent on child ideation):

| Spec | ATT | bootstrap SE | 95% CI | boot p |
|------|----:|-------------:|--------|-------:|
| edu + urban (no income) | 0.0675 | 0.0092 | [0.046, 0.083] | 2e-13 |
| **edu + urban + income** | **0.0583** | 0.0075 | [0.050, 0.079] | 5e-15 |
| edu + urban + income, **formative 16–30** | 0.0478 | 0.0096 | [0.033, 0.073] | 7e-07 |

## What this shows
1. **Adding the parent-income proxy modestly attenuates the effect** (0.068 → 0.058, ~13%),
   because parent education and urban/rural already capture most of the SES variation income
   would. The marginal SES contribution beyond education + urban/rural is small.
2. **Transmission remains robust and highly significant** in every spec — bootstrap CIs all
   exclude zero, p ≪ 0.001 — including in the 16–30 formative window (ATT ≈ 0.048).
3. So the parent→child ideation link is **not an artifact of family SES** as far as we can
   proxy it: net of parent education, urban/rural, and parent income, children of traditional
   parents are ~0.05–0.06 more traditional than comparable children of egalitarian parents.

## Honest limit
This is an SES *proxy*, not household income — no CFPS family file is available, and 2020 has
no personal-income variable, so the income control exists for **2014 only** and is individual-
level. A family-file household-income control would be stronger; the effect's stability across
the controls we *can* add makes a full reversal unlikely, but it is not ruled out.

## Where the regeneration question stands (survey-only)
Transmission is confirmed and robust to: richer matching (education, urban/rural, income),
the formative-age window, and bootstrap inference. Both parents transmit roughly equally;
honest effect size ≈ 0.05–0.07 on the [0,1] index.

## Next steps
CFPS **family file** for true household income (if obtainable); family/sibling fixed effects;
survey weights; then the provincial ideology climate (deferred per current scope).
