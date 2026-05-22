# analysis_007 — Whose ideation matters more in the family? (couples, CFPS 2014)

**Research question:** Within married couples, is the **wife's** gender ideology the
more consequential one for the household division of labour, or the husband's? We put
both spouses' ideation in the same model and compare coefficients.

**Analysis type:** Couple-level (dyadic) association — intergenerational/family practice.

**Data / sample:** CFPS 2014 married couples linked via the spouse pointer `pid_s`;
both spouses must have a valid ideation index and valid daily housework hours
(N = 10,675 complete couples of 10,841 linked).

**Core variables:**
- Explanatory: `wife_ideation`, `husband_ideation` (index [0,1], 1 = most traditional),
  entered together. Controls: wife age, husband age.
- Outcomes: `wife_housework_hrs`, `husband_housework_hrs` (qq9010),
  `wife_share` = wife / (wife + husband) housework hours.

**The test:** compare the wife-ideation vs husband-ideation coefficient in each model
(`whose_ideation_comparison.csv`).

**Caveat:** cross-sectional; housework and attitudes co-measured → associational, not causal.
