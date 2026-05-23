# 03 · Method note — analysis_035

## Sample

Adult-child × parent-pair dyads with all three ideations non-missing
(both parents and child are adult respondents with ≥ 1 valid item):

| Wave | n_adults | n_full_dyads (all 3 ideations) |
|---|---|---|
| 2014 | 31 554 | 5 565 |
| 2020 | 22 692 | 4 120 |

Parent pid pointers via the famconf join (same as `analysis_033 / 034`).

## Methods

### Part A — Transmission OLS

```
child_ideation ~ mother_ideation + father_ideation + child_female
              + mother_id × child_female + father_id × child_female
              + age_c + age_c2 + urban
              + parent_avg_age + parent_avg_edu + parent_log_income
              [ + child_edu_yrs ]  ← mediator variant
```

HC1 robust SEs. Two model variants:
* **Base**: no `child_edu_yrs` on RHS. The β on mother_id / father_id
  is the total ideation-transmission slope.
* **+ edu mediator**: adds `child_edu_yrs`. The β shrinkage relative
  to the base model indicates how much of the transmission operates
  *via* the child's schooling (mediation à la Baron-Kenny step 3).

Stratified fits (overall / male / female child) reported for both
variants.

### Part B — Within-family parent-child correlations

Pearson and Spearman r of `(child_ideation, parent_ideation)` per
wave, by sex stratum and (for mother) by parent-child age gap bin.
Reported in `tables/parent_child_correlations.csv`.

## Controls

`age_c = (child_age − 35) / 10`, `age_c²`, `urban`, `parent_avg_age`,
`parent_avg_edu`, `parent_log_income`. For mediator variant:
`child_edu_yrs`.

## Caveats

* **Cross-sectional**. Parent and child ideation measured simultaneously.
  Direct inheritance / shared cohort / current ongoing convergence
  cannot be separated.
* **Selection on intact dyads** as in 033 / 034.
* **Mediation decomposition is informal** (β shrinkage between two OLS).
  A formal mediation analysis (Imai-Keele, structural equation model)
  would give a clean indirect-effect estimate; not implemented here.
* **Multiple testing**: 9 outcomes × 2 waves × 3 strata × 2 mediator
  variants × 2 parents. The substantive interpretation weights the
  consistency of direction across cells over individual marginal p
  values.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — mean child ideation by parent tertile × child sex
* `02_missing_table.csv`
* `04_result_table.csv` — every term × wave × stratum × mediator-variant
* `tables/parent_child_correlations.csv` — Pearson + Spearman r per cell
* `figures/scatter_{mother,father}_child_{2014,2020}.pdf` — joint distribution + OLS slope
* `figures/transmission_forest.pdf` — coefficient forest with vs without edu mediator
