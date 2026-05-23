# 03 · Method note — analysis_029

## Sample

| Wave | n_couples | Source of spouse pid |
|---|---|---|
| 2014 | 10 841 | `pid_s` in `cfps2014_adult.dta` |
| 2020 |  6 624 | `pid_a_s` from `cfps2020_famconf.dta`, joined to `cfps2020_adult.dta` |

Couples built via `cfps_linkage.build_couples` (already TDD-locked). Only
different-sex pairs retained; reciprocal rows collapsed. Both spouses must
have ≥ 1 valid ideation item.

## Parts

### Part A — assortative mating on ideation

* **Within-couple Pearson r** of ideation, overall and broken down by
  wife's birth decade / couple urban status / wife's education tertile
  (`tables/assortative_mating_correlations.csv`).
* **OLS-HC1** of `wife_ideation ~ husband_ideation + controls` and the
  reverse, where controls = `wife_age_c`, `husband_age_c`, `wife_edu_yrs`,
  `husband_edu_yrs`, `couple_urban`. The coefficient on the partner's
  ideation is the **ideology-based residual sorting** estimate.

### Part B — whose ideology drives the division

* **Dyadic OLS-HC1** of:
  - `wife_housework_hours ~ wife_ideation + husband_ideation + (controls)`
  - `husband_housework_hours ~ ditto`
  - `wife_childcare_hours ~ ditto`  (2020 only)
  - `husband_childcare_hours ~ ditto`  (2020 only)
* Controls = `wife_age_c`, `husband_age_c`, `wife_edu_yrs`,
  `husband_edu_yrs`, `wife_log_income`, `husband_log_income`,
  `couple_urban`.
* Comparing the **wife_ideation vs husband_ideation** coefficients on
  the same outcome tells us whose belief is more "translating" into
  the division.

### Part C — marriage satisfaction by gap / typology

* `gap_ideation = |wife_ideation − husband_ideation|`
* **Typology** (median split on each spouse's ideation):
  - `concordant_progressive` — both below median (reference)
  - `concordant_traditional` — both above median
  - `woman_more_traditional` — wife above, husband below
  - `man_more_traditional`   — husband above, wife below
* **OLS-HC1** of `wife_marriage_sat` (`qm801`) and `husband_marriage_sat`
  on `gap_ideation` + the three typology dummies + all standard couple
  controls.

## Caveats

* **Cross-sectional**: matching and current attitudes measured together.
  We cannot disentangle "sorted on ideology at marriage" from "shared
  marriage reshaped both partners' attitudes".
* **Selection on intact mutually-respondent couples**: divorced /
  separated / lost-spouse pairs drop out. The sample is "currently
  married AND both spouses interviewed in the wave".
* **Spouse-pid coverage**: not all CFPS married adults have a spouse
  in the sample. The 10 841 couples in 2014 are ~ 47 % of married
  adult women in CFPS 2014.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` (per-wave couple counts + raw r)
* `02_missing_table.csv` (per-spouse-variable coverage)
* `04_result_table.csv` (unified)
* `tables/assortative_mating_correlations.csv`
* `tables/assortative_mating_regression.csv`
* `tables/dyadic_division_regression.csv`
* `tables/marriage_sat_typology_regression.csv`
* `figures/couple_ideation_scatter_{2014,2020}.pdf`
* `figures/dyadic_forest_{2014,2020}.pdf`
* `figures/sat_by_typology_{2014,2020}.pdf`
