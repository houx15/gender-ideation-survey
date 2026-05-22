# analysis_018 — Sibling resemblance & family fixed effects for ideology (CFPS, SPEC 5.7)

**Research question:** How much do siblings resemble each other on gender ideology (how
"family-determined" is it), how much of that does the parents' *measured* ideology explain,
and — within a sibship — are daughters less traditional than their own brothers?

**Why FE can't estimate transmission directly:** parent ideology is identical for siblings,
so a family fixed effect absorbs it. We therefore use the sibling structure for what it *can*
identify: (1) the family-level share of variance (ICC) and (2) within-sibship gaps.

**Analysis type:** Intergenerational reproduction; variance components + fixed effects.

**Data / sample:** CFPS 2014 & 2020. **Real** multi-child families only — ≥2 sampled children
sharing the *same in-sample* father and mother (`pid_f>0 & pid_m>0`, both with valid ideation).
N ≈ 2,378 / 2,584 children in 1,091 / 1,195 families.

**Pieces:**
- **Sibling ICC** of child ideation (one-way), raw and after partialling out `parent_mean`
  ideology (and + age + urban) → share of sibling resemblance attributable to measured parent ideology.
- **Family FE** `ideation ~ female + age` → within-sibship daughter-vs-own-brother gap, net
  of all family-level factors.
