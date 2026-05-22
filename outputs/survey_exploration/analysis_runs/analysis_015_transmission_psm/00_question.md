# analysis_015 — Gender-ideation transmission: correlations + PSM (CFPS, SPEC 5.7)

**Research question:** Is a child's gender ideology associated with their parents'
(intergenerational "regeneration"), and does the association survive matching on
confounders?

**Analysis type:** Intergenerational reproduction — correlation + propensity-score matching.

**Data / sample:** CFPS 2014 & 2020; adult children (age ≥16, all have the ideation battery)
linked to both parents (`pid_f`/`pid_m`; 2020 `pid_a_f`/`pid_a_m`). N = 5,564 / 4,120 with
both parents measured.

**Parts:**
- **(a) Correlations** (Pearson r + p): mother-child, father-child, parent-mean-child, and
  the four gendered paths (mother→daughter, mother→son, father→daughter, father→son).
- **(b) PSM:** treatment = **traditional parent** (top tertile of parent-mean ideation) vs
  **egalitarian** (bottom tertile; middle dropped). Outcome = child ideation index.
  Match covariates = parent mean education, child age, child sex. Estimates the effect of
  having a traditional parent on the child's ideology, net of those confounders.
