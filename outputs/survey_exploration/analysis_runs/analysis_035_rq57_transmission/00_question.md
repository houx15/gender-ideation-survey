# 00 · Research question — analysis_035

## SPEC anchor

RQ 5.7: **Does parental gender ideation transmit to their adult child's
ideation? Does transmission differ for sons vs daughters and between
mother and father?**

This run completes the intergenerational arm. 034 looked at parent
ideation → child practical outcomes (edu, work, marriage); this one
asks the more direct question: does the child *inherit* the ideology
itself?

## Design

For each adult-child × parent-pair dyad:

1. **Raw transmission**: OLS-HC1 of `child_ideation ~ mother_id +
   father_id + child_female + interactions + child & parent controls`.

2. **Sex-of-parent asymmetry**: compare the mother-ideation and
   father-ideation coefficients within each sex stratum. Does daughter
   inherit more from mother or father? Same question for son.

3. **Within-family ICC**: parent–child intraclass correlation of
   ideation, overall and by subgroup.

4. **Mediation via child's edu**: how much of the parent → child
   ideation transmission is mediated by the schooling level the child
   reached? A sequential / structural decomposition (separate models
   with and without `child_edu_yrs` on the RHS).

## Frames

`2014_cross` and `2020_cross`, separately. No lagged (the panel of
parent-child dyads with all four ideation values is too small after
listwise).

## Sample

CFPS adult-child × parent-pair dyads where:
* child is adult respondent with ≥ 1 valid item
* both parents are adult respondents with ≥ 1 valid item

Expected n: ~5 500 dyads in 2014, ~4 100 in 2020.

## Controls

Child: age_c = (child_age − 35) / 10, age_c², urban.
Parent: parent_avg_age, parent_avg_edu, parent_log_income.

For the mediation decomposition: child_edu_yrs added.

## Caveats

* **Cross-sectional**: parent and child ideology measured together.
  Inheritance / shared environment / current convergence cannot be
  separated.
* **Selection on intact dyads** as in 033 / 034.
* **Mediation decomposition** is the difference between two OLS β —
  a structural mediation model (Baron-Kenny / Imai-Keele) would tighten
  the interpretation. Here we just report the β shrinkage.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv`,
`05_interpretation_note.md`, `tables/icc.csv`, `figures/*.pdf`.
