# analysis_010 — Gendered educational investment, household-matched (SPEC 5.5)

**Why this run exists:** review of analysis_009 raised two valid problems:
1. **Household structure was not matched** — linking any in-sample parent–child pair
   ignores co-residence, sibling structure and which household a child belongs to.
2. **Life stage / education censoring** — a young child's low years-of-schooling means
   "still in school", not under-investment.

**Research question:** Do more traditional parents invest less in **daughters'**
education *relative to their own sons* — tested within the family and at completed-
schooling ages?

**Analysis type:** Intergenerational reproduction; within-family (sibling) design.

**Data / sample:** CFPS 2014 & 2020. Families defined by shared parents (`pid_f`,`pid_m`).
- Part A: child education ~ parent ideology, restricted to **age ≥ 25** (completed schooling).
- Part B: **one-son-one-daughter families** — daughter-minus-son education gap regressed
  on parent ideology (367/385 families all-ages; 107/189 with both siblings ≥25).

**Core variables:** child years of schooling; `mother_pi`/`father_pi` and
`parent_mean` ideation; `child_female`; within-family `eduy_diff` (daughter−son) and `age_gap`.
