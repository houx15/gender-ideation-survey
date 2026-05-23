# 03 · Method note — analysis_028

## Sample frames

| Frame | n | Predictor | Time-ordering |
|---|---|---|---|
| `2014_cross` | 31 554 (≥1 valid item) | `ideation_2014` ↔ `edu_yrs_2014` | reverse-causal |
| `2020_cross` | 22 692 | `ideation_2020` ↔ `edu_yrs_2020` | reverse-causal |
| `2014_young_cohort` | 3 812 (birthy ≥ 1990, age ≤ 24 in 2014) | `ideation_2014` ↔ `edu_yrs_2014` | weakly reverse-causal |
| `2020_young_cohort` | 5 198 (birthy ≥ 1990, age ≤ 30 in 2020) | `ideation_2020` ↔ `edu_yrs_2020` | weakly reverse-causal |
| `lagged_young_cohort_delta` | 2 697 panel (birthy_2014 ≥ 1990) | `ideation_2014` → `edu_yrs_2020 \| edu_yrs_2014` | **directional** |

The directional frame puts `edu_yrs_2014` on the RHS, so the β on
`ideation_2014` is the change-in-education prediction.

## Variable coding

* **edu_yrs** — `cfps20{14,20}eduy_im`, CFPS imputed years, kept to [0, 22].
* **edu_level** (descriptive only) — unified ordinal mapped via
  `unify_edu_level(s, wave)`:

  | Unified | 2014 `cfps2014edu` | 2020 `w01` |
  |---|---|---|
  | 0 illiterate / no school | 1, 9 | 0, 10, 1, 2 |
  | 1 primary               | 2 | 3 |
  | 2 junior high           | 3 | 4 |
  | 3 senior high           | 4 | 5 |
  | 4 college (大专)        | 5 | 6 |
  | 5 bachelor              | 6 | 7 |
  | 6 masters               | 7 | 8 |
  | 7 PhD                   | 8 | 9 |

* **ideation** — `ideation_lib`, [0, 1], 1 = most traditional.

## Methods

1. **Welch's t and Cohen's d** between top vs bottom ideation tertile per
   sex stratum.
2. **OLS-HC1** on `edu_yrs`. Overall fits include `ideation × female`
   to test gender moderation.
3. **Cohort breakdown** (`tables/edu_by_cohort.csv`): mean `edu_yrs` by
   birth-decade × ideation tertile × sex. Makes the reverse-causality
   structure visible (older cohorts → both less education and more
   traditional ideation).

## Controls

`female` (overall fits only), `age_c = (age − 40) / 10`, `age_c2`,
`urban` (hukou), `log_income`. **No `edu_yrs` on the RHS** — it's the
outcome.

## Interpretation bounds

* **(A) / (B) are reverse-causal**. Adult final education is largely
  set by the early 20s; ideation in 2014 / 2020 is measured ≥ 20 years
  later for the older cohort. The cross-section β is a snapshot of who
  *ended up* traditional given their schooling — not "ideology
  affected the schooling decision".
* **(C) is weakly reverse-causal**. For respondents born ≥ 1990, some
  schooling is still in progress at the time of the 2014 ideation
  measurement (e.g. a 1994-born respondent was 20 in 2014, possibly
  still in college; 1992-born respondents would have finished bachelor
  and could pursue a masters). The cross-section is still partly
  reverse-causal but the gap is narrower.
* **(D) is directional**. `ideation_2014` is fixed at measurement;
  `edu_yrs_2020 − edu_yrs_2014 ≥ 0` happens after. Controlling
  `edu_yrs_2014` on the RHS isolates the change. *This is the cleanest
  causal frame we can build with this data*.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — tertile × sex × edu_yrs means
* `02_missing_table.csv`
* `04_result_table.csv` — tidy OLS-HC1 (~80 rows)
* `tables/welch_tertile_diffs.csv`
* `tables/edu_by_cohort.csv` — birth-decade × ideation × sex grid
* `figures/*.pdf`
