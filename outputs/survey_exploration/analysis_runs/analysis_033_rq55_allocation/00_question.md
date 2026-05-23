# 00 · Research question — analysis_033

## SPEC anchor

RQ 5.5: **Do parents with more traditional gender ideation allocate
educational resources differently to sons vs daughters?**

The canonical "gendered investment" test in the Chinese family-sociology
literature: parents with traditional ideology are expected to channel
more schooling toward sons. We test this with two complementary designs:

## Two designs

### A. Child-level OLS (full parent-child dyad sample)

Outcome: child's adult `edu_yrs`. Predictors:
- `mother_ideation`, `father_ideation`
- `child_female`
- **Key interactions**: `mother_ideation × child_female`,
  `father_ideation × child_female` — the formal "gendered allocation"
  test

Controls: `child_age`, `child_urban`, `parent_avg_age`,
`parent_avg_edu`, parent's log income.

Stratification: pooled with interaction terms (the gendered test
*is* the interaction). Sex-stratified fits also reported for
descriptive comparison.

### B. One-son-one-daughter sibling difference (cleanest design)

Within families that have exactly one daughter and exactly one son:
**Outcome** = `daughter_edu_yrs − son_edu_yrs` (already implemented
in `cfps_linkage.one_son_one_daughter_diff`, used in `analysis_010`).

**Predictor**: `mother_ideation`, `father_ideation`. Negative sign
means traditional parents give the daughter *less* schooling than the
son.

This design **differences out all family-level confounders** — parent
education, region, urban, household SES, family composition. Only
mother and father ideation remain as time-invariant family-level
predictors. The cleanest identification we have for this question.

## Frames

* `2014_cross`: parent ideation in 2014 × child edu_yrs in 2014
* `2020_cross`: parent ideation in 2020 × child edu_yrs in 2020
* (no lagged — child's adult edu is mostly set, and the panel of
  parent-child dyads is too small after listwise to support a real
  panel design here)

## Sample

CFPS adult-child dyads where:
- Child is an adult respondent (age ≥ 16) with valid `edu_yrs`
- Both parents are adult respondents with valid ideation in the wave

Expected: ~3 000-6 000 dyads with both parents per wave; 1S1D
subsample: ~500-1 000 families.

## Methods

* **OLS-HC1** for the child-level design.
* **OLS-HC1** for the within-family difference design.
* Welch / Cohen's d descriptives by parent-ideation tertile × child sex.

## Controls

`child_age`, `child_urban`, `parent_avg_age`, `parent_avg_edu`,
`parent_log_income`. The within-family difference design drops the
parent-level controls (differenced out).

## Caveats

* **Cross-sectional**: parent ideology measured now, child education
  largely set already. Reverse causation less plausible than for the
  child's own ideation (parents shape children, not vice-versa), but
  a third common cause (region / cohort) cannot be ruled out.
* **Selection on having both parents in sample**: dyads where both
  parents are adult CFPS respondents skew toward intact / co-resident
  families. Single-parent or non-co-resident-parent dyads are
  underrepresented.

## Files

`scripts/run.py`, `01_descriptive_table.csv`, `02_missing_table.csv`,
`03_method_note.md`, `04_result_table.csv`,
`05_interpretation_note.md`, `tables/*.csv`, `figures/*.pdf`.
