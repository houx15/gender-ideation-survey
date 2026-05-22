# analysis_012 — Method note

## Design
Within-family one-son-one-daughter difference (`cfps_linkage.one_son_one_daughter_diff`,
tested): for each family with exactly one son and one daughter, compute the daughter−son
gap in the outcome, then regress that gap on the family's parent ideology + the sibling
age gap. The within-family difference removes every family-level confound; parent ideology
(constant within family) is the predictor of the *gender gap*.

## Variables and coding
- **parent_mean**: mean of mother's and father's ideation index ([0,1], 1 = most traditional).
- **eduy_gap / hw_gap**: daughter minus son, from `cfps20XXeduy` and housework hours
  (`qq9010` 2014 / `qq9010n` 2020), each `clean_continuous`-bounded.
- Education run at age ≥ 25 (completed schooling) and all ages; housework all ages.
- `age_gap` (daughter−son age) controls for the older sibling having more schooling/chores.

## Method
OLS (tested `stats_helpers.ols`), classical SEs, no weights. Son-favouring allocation ⇒
negative parent-ideology coefficient on the education gap, positive on the housework gap.

## Interpretation bounds
- **Underpowered:** one-son-one-daughter families number 107–385; estimates are noisy.
- Which son vs daughter remains co-resident/linked is itself selected (analysis_010 caveat).
- Education for under-25s is censored (still in school); the ≥25 subset is small.
- Housework for co-resident adult children reflects life stage (enrolment, employment) as
  well as demand; `age_gap` only partly controls this.
- Cross-sectional; parent ideology measured contemporaneously, not during the child's youth.

## Next steps
The proper test needs **parental ideology linked to during-childhood resource allocation** —
e.g., a **CFPS children's questionnaire** (per-child education expenditure, expectations,
tutoring) merged to parent ideology, or a survey carrying both. Pool more CFPS waves to grow
the one-son-one-daughter sample; consider family fixed effects on all mixed-gender sibships.
