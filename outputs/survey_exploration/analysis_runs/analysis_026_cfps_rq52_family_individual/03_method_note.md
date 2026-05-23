# 03 · Method note — analysis_026

## Sample frames

| Frame | n | Predictor | Outcomes |
|---|---|---|---|
| `2014_cross` | 31 554 (≥1 valid ideation item) | `ideation_2014` | `currently_married`, `first_marriage_age`, `ideal_children`, `housework_hours` |
| `2020_cross` | 22 692 (≥1 valid ideation item) | `ideation_2020` | `currently_married`, `first_marriage_age`, `housework_hours` (ideal-children **not asked** in 2020) |
| `lagged_2014to2020` | ~20 100 panel (depends on coverage) | `ideation_2014` | `currently_married_2020`, `housework_2020`; controls include `outcome_2014` so the β is on the *change* |

## Variable coding (locked by `tests/test_cfps_outcomes.py`)

* **currently_married** — `qea0 == 2 → 1`; `{1,3,4,5} → 0`; missing → NaN.
* **first_marriage_age** — `qea205y − birthy`, kept to [15, 50]; restricted to
  `qea2071 == 1` (first marriage) where the flag is non-missing. Both inputs
  range-filtered (`qea205y` ∈ [1940, 2024]; birthy ∈ [1900, 2010]).
* **ideal_children** — `qm501`, kept to [0, 10]. 2014 only.
* **housework_hours** — `qq9010` (2014) / `qq9010n` (2020), hours / day, kept to
  [0, 24].
* **ideation** — `ideation_lib`, [0, 1], 1 = most traditional.
* **female** — 1 = woman; controls `age_c = (age − 40) / 10`, `age_c2`,
  `urban` (qa301: 1→0, 3/7→1), `edu_yrs` ∈ [0, 22], `log_income = log1p(emp_income)`.

## Methods

1. **Welch's t and Cohen's d** on each outcome, comparing top vs bottom
   ideation tertile, reported per sex stratum (`welch_tertile_diffs.csv`).
2. **OLS with HC1 robust SEs** for continuous outcomes; **linear-probability
   model with HC1** for the binary `currently_married`. The "overall" fit
   includes `ideation × female` so gender-moderation is formally tested.
   Sex-stratum fits drop `female` (zero variance) and the interaction.
3. **Lagged fits** put `outcome_2014` on the RHS so the coefficient on
   `ideation_2014` is interpreted as predicting the change in the outcome
   between 2014 and 2020, controlling for the 2014 level.
4. **Zero-variance regressors** are dropped defensively before fitting (e.g.
   when a covariate is constant inside a stratum after listwise deletion).

## Interpretation bounds

* Cross-sectional → **associational**; reverse causation is plausible
  (currently-married people may have grown more traditional through
  marriage, not the other way round).
* Lagged is **directional** but on the smaller panel (n ≈ 5–13 k post
  listwise depending on outcome); restricted to those alive in both waves
  and with no item-level missingness on ideation 2014.
* **First-marriage age is descriptive** in either wave: ideation is measured
  *after* the marriage event (median CFPS respondent married ~1995). The
  Welch / OLS contrast tells you who-ended-up-traditional differs by who
  married earlier — not that ideation drove timing.
* **Ideal children is 2014-only** (qm501 dropped from the 2020 wave).
* **Housework time** has a strongly gendered floor (≥ 40 % of CFPS men
  report < 1 h/day, ≥ 80 % of women report ≥ 1 h/day). OLS on raw hours
  reported; the LPM-style β on female respondents drives most of the
  ideation effect.

## Files

* `00_question.md` — question and design.
* `01_descriptive_table.csv` — tertile × sex × outcome means.
* `02_missing_table.csv` — per-outcome coverage.
* `03_method_note.md` — this file.
* `04_result_table.csv` — tidy OLS / LPM results (one row per term per fit).
* `05_interpretation_note.md` — substantive reading.
* `tables/welch_tertile_diffs.csv` — Welch's t & Cohen's d.
* `figures/*.pdf` — vector outputs (`pdf.fonttype=42`).
