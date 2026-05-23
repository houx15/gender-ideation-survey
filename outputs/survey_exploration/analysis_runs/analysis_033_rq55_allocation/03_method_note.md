# 03 · Method note — analysis_033

## Sample

| Wave | n_adults (with ≥1 valid ideation item) | n_dyads (both parents in sample) | n_dyads w/ valid both-parent ideation | n_1S1D families |
|---|---|---|---|---|
| 2014 | 31 554 | ~12 000 | 5 565 | ~340 |
| 2020 | 22 692 | ~8 000 | 4 120 | ~245 |

Dyad = (adult respondent child, mother adult-respondent, father
adult-respondent). Parent pid pointers from `cfps_linkage`-style
famconf join:

* 2014: `pid_f`, `pid_m` in `cfps2014_famconf.dta`
* 2020: `pid_a_f`, `pid_a_m` in `cfps2020_famconf.dta`

Only dyads where the parent is an adult respondent with ≥ 1 valid
ideation item enter the analysis.

## Variable coding

* **Child's** `edu_yrs` (outcome): `cfps20{14,20}eduy_im` cleaned to
  [0, 22].
* **Parent's** ideation: `ideation_lib` index, [0, 1], 1 = traditional.
  Read off the parent's own adult-questionnaire row.
* **Parent's** `edu_yrs`, `log_income`, `age`: same definitions as in
  prior runs, taken from the parent's adult-questionnaire row.
* **Child controls**: `age_c = (age − 25) / 10`, `age_c2`, `urban`,
  `parent_avg_age`, `parent_avg_edu`, `parent_log_income`.

## Methods

### Design A — Child-level OLS

```
child_edu_yrs ~ mother_ideation + father_ideation + child_female
             + mother_ideation × child_female
             + father_ideation × child_female
             + age_c + age_c2 + urban
             + parent_avg_age + parent_avg_edu + parent_log_income
```

HC1 robust SEs. The two interactions are the gendered-allocation test:
a negative `father_id × female` means traditional fathers underinvest
in daughters relative to sons (the patriarchal prediction).

Stratified fits (drop the interactions + child_female) also reported.

### Design B — One-son-one-daughter sibling difference

Restrict to families with exactly 1 daughter + 1 son (both adult
respondents in the wave). Compute `Δedu = daughter_edu − son_edu`.

```
Δedu ~ mother_ideation + father_ideation + mother_edu + father_edu + urban
```

(parent ideation/edu/urban are constant within the family — they're
just the parents' levels — but they're the only available family-level
predictors of the within-family allocation gap.)

A negative coefficient on parent_ideation means: in more-traditional
families, the daughter receives *less* schooling than the son does
(by this many years on average).

This design **differences out** all unobserved family-level
confounders (region, family SES, household composition, parents'
own gender constellation). It is the cleanest gendered-allocation test
the data supports.

## Caveats

* **Cross-sectional**: parent ideology measured now, child education
  largely complete. Less reverse-causation pressure than for child
  ideation (parents shape children more than vice versa), but
  cohort / regional norms common to parents AND child remain.
* **Sample selection**: dyads where both parents are adult CFPS
  respondents skew toward intact / co-resident families. Single-parent
  and absent-parent dyads underrepresented.
* **1S1D sample is small** (n ≈ 240–340 families). Bootstrap-style
  CIs on the differences are wide.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — mean child edu by parent tertile × child sex
* `02_missing_table.csv` — dyad coverage per wave
* `04_result_table.csv` — tidy OLS-HC1 (designs A + B, both waves)
* `figures/edu_by_parent_tertile_{2014,2020}.pdf`
* `figures/coef_forest_parent_ideation.pdf`
