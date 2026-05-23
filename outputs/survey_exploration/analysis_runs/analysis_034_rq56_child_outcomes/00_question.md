# 00 · Research question — analysis_034

## SPEC anchor

RQ 5.6: **Do parents' gender ideation predict their adult child's
practical outcomes — and do the effects differ for sons vs daughters?**

This extends `analysis_033`'s allocation finding from "did parents
underinvest in daughters' education" to a broader question: does
parental ideology cast a long shadow over the *adult* child's life
across the family, work, and time-use domains we built in 026 / 027?

## Outcomes (adult child)

Family domain:
* `currently_married`
* `housework_hours` (daily, CFPS qq9010 / qq9010n)
* `ideal_children` (2014 only)
* `marriage_sat` (qm801, both waves)

Work domain (employed-only models):
* `employed`
* `log_wage_year` (`p_wage` 2014, `emp_income` 2020 — logged)
* `mgmt` (qg14)
* `isei` (qg303code_isei, 2020 only)

Education:
* `edu_yrs`

For each outcome:
* OLS-HC1 of `outcome ~ mother_ideation + father_ideation
  + mother_id × child_female + father_id × child_female
  + child & parent controls`.
* Stratified fits (overall / male child / female child).

## Frames

* `2014_cross`: parent ideation 2014 ↔ adult child outcome 2014
* `2020_cross`: parent ideation 2020 ↔ adult child outcome 2020

No lagged frame — the parent-child dyad panel is too small after
listwise to support it cleanly. Cross-section reads as descriptive
"adult children of more-traditional parents have these outcomes".

## Controls

`child_age_c = (child_age − 35) / 10`, `child_age_c²`, `child_urban`,
`parent_avg_age`, `parent_avg_edu`, `parent_log_income`.

For employment-conditional outcomes (wage, mgmt, isei): restricted to
`child_employed == 1`.

## Caveats

* **Selection on intact parent-pair dyads**: same as `analysis_033`.
  Single-parent or absent-parent children underrepresented.
* **Cross-sectional, descriptive**: parent ideology and child
  outcomes are measured together. The patriarchal-channel reading
  ("parents' ideology shaped child trajectory") is consistent with
  the cross-section direction but not directly identified.
* **Sample size**: parent-pair dyads where the child is an adult
  respondent ≈ 4–5 k per wave. Stratifying by sex and conditioning
  on employment drops some cells well below n = 1 000.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv`,
`05_interpretation_note.md`, `figures/*.pdf`.
