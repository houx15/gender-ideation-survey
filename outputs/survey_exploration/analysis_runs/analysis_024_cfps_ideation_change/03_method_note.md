# 03 · Method note — analysis_024

## Panel construction (`scripts/cfps_panel.py`)

1. Load CFPS 2014 adult file (`cfps2014_adult.dta`) with the four
   gender-ideation items `qm1101..qm1104`, the pid, and the variables
   needed for life events.
2. Load CFPS 2020 adult file (`cfps2020_adult.dta`) with the same items
   and the 2020 counterparts of the life-event variables.
3. Normalize each Likert item to `[0,1]` via `ideation_lib.normalize_item`
   (same recoding as `surveys/processed/`); `ideation_index` is the mean
   of valid items per wave.
4. Both wave files contain a small number of duplicate `pid` rows from
   the multi-module joining of the original .dta — we keep the first
   occurrence per pid (no information loss because the items are
   constant across module joins).
5. Inner-join on `pid` → 20,100 respondents.
6. Compute Δs as `2020 − 2014` for every measured quantity. Δ is NaN
   whenever either endpoint is missing.

## Variable definitions

| Concept                | 2014 source                       | 2020 source                            | Codes / cleaning |
|------------------------|-----------------------------------|----------------------------------------|------------------|
| Gender-ideation index  | mean of `qm1101..qm1104` (z)      | mean of `qm1101..qm1104` (z)           | 0=progressive, 1=traditional |
| Female                 | `cfps_gender` (0=female)          | `gender` (0=female)                    | 1 if female else 0 |
| Birth year             | `cfps_birthy`                     | `ibirthy`                              | range 1920–2010   |
| Urban hukou            | `qa301` ∈ {1=农业, 3=非农业}      | `qa301` ∈ {1, 3, 7=居民}               | 1 if non-agric / resident, 0 if agric, else NaN |
| Marital status         | `qea0`                            | `qea0`                                 | 1=never, 2=married, 3=cohab, 4=divorced, 5=widowed |
| Employed               | `employ2014` ∈ {0,1}              | `employ` ∈ {0,1,2}                     | 1 if working, 0 if unemployed, NaN if retired / DK / out-of-LF |
| Children (rostered)    | non-null `pid_c1..pid_c10`        | non-null `qf1_a_1..qf1_a_8`            | count of valid IDs |
| Household size         | non-null `pid_a_1..pid_a_17` + 1  | `fml_count`                            | sentinel codes → NaN |
| Education years        | `cfps2014eduy_im`                 | `cfps2020eduy_im`                      | range 0–22 |
| Personal income        | `income`                          | `emp_income`                           | sentinel codes → NaN |

All CFPS missing-code sentinels (`-10, -9, -8, -2, -1, 0`) become NaN.
Direction-of-change is classified with `eps = 0.05` on the [0,1] index
(one notch on the 4-item battery).

## Life-event derivations

* `had_new_child`     := `delta_children_n > 0`
* `lost_job`          := `employed_2014 == 1 AND employed_2020 == 0`
* `entered_work`      := `employed_2014 == 0 AND employed_2020 == 1`
* `marital_transition`: discrete label produced by
  `cfps_panel.marital_transition()` — values include
  `stable_married`, `stable_never_married`, `entered_marriage`,
  `divorced`, `widowed`, `remarried`, `started_cohab`, etc.
* `entered_marriage`, `divorced`, `widowed`: 0/1 derived from the above.

Each binary event is NaN (not 0) whenever either endpoint is missing.

## Statistical methods

* **Group descriptives**: mean Δideation per group, bootstrap 95 % CI of
  the mean (`descriptive_stats.bootstrap_mean_ci`, 1,000 resamples,
  seed = 0). Shares of `progressive` / `stable` / `traditional` per group.
* **Effect sizes for binary splits** (gender, hukou): Cohen's *d*,
  Hedges' *g* (small-sample-corrected), Welch's *t* with 95 % CI of the
  mean difference (`descriptive_stats.welch_ci_diff`).
* **Life-event contrasts**: per binary event, Welch's *t* with
  bootstrap CIs for each side and Cohen's *d* on the Δideation values.
* **OLS**: `delta_ideation ~ female + urban_2014 + age_2014 +
  had_new_child + lost_job + entered_work + entered_marriage +
  divorced + widowed + delta_household_n + delta_edu_yrs +
  ideation_2014`. Both classical (homoskedastic) and HC1
  heteroskedasticity-robust standard errors are reported. Baseline
  ideation is included to control for mechanical regression to mean.

## Reproducibility

* `python3 -m pytest tests/test_cfps_panel.py` exercises the 16
  cleaning / transition unit tests.
* `python3 outputs/survey_exploration/analysis_runs/analysis_024_cfps_ideation_change/scripts/run.py`
  rebuilds all tables and figures from raw `.dta`.
