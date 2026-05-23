# 03 · Method note — analysis_027

## Sample frames

| Frame | n | Predictor | At-risk pool |
|---|---|---|---|
| `2014_cross` | 31 554 adults (≥1 valid item) | `ideation_2014` | full / `employed==1` for wage / mgmt / promotion / sub |
| `2020_cross` | 22 692 adults | `ideation_2020` | full / `employed==1` for wage / mgmt / promotion / sub / bianzhi / isei |
| `lagged_2014to2020` | ~12 000 panel (varies by outcome) | `ideation_2014` | full / `employed_2020==1` |

## Variable coding (locked by `tests/test_cfps_outcomes.py`)

* **employed** — `employ`/`employ2014`: 1 → 1; {0, 2, 3, 9} → 0; 8 / negatives → NaN.
* **log_wage_month** — `log1p(qg11)`, with `qg11` cleaned to [0, 1 000 000].
  `qg11` is the per-month main-job wage; sentinels (−8 etc.) → NaN.
* **log_wage_year** — `log1p(p_wage)` (2014) / `log1p(emp_income)` (2020),
  cleaned to [0, 10 000 000]. **Cross-wave levels are not directly comparable**
  (different definitions / coverage); only within-wave gradients and
  interactions are interpreted.
* **mgmt** — `qg14` via `yes_no` (1=是 → 1; {0, 5}=否 → 0).
* **promotion** — `qg15` via `promotion_indicator`: {1, 2, 3} (admin /
  technical / both) → 1; {78, 79} (neither / no upward room) → 0;
  everything else NaN. **New for the project** (was missing from
  `analysis_005`).
* **has_sub** — `qg17` via `yes_no`.
* **bianzhi** — `qg2032` via `yes_no` (2020 only).
* **isei** — `qg303code_isei` (current main job's International Socio-Economic
  Index of Occupational Status), cleaned to [10, 90]. 2020 only.
* **ideation** — `ideation_lib`, [0, 1], 1 = most traditional.

## Methods

1. **Welch's t and Cohen's d** between top vs bottom ideation tertile,
   per sex stratum (`tables/welch_tertile_diffs.csv`).
2. **OLS-HC1** (continuous: log wages, ISEI) and **LPM-HC1** (binary:
   employed, mgmt, promotion, has_sub, bianzhi).
3. **Lagged fits** put `outcome_2014` on the RHS (where available) so
   the ideation coefficient is interpreted as predicting the change
   between 2014 and 2020. For 2020-only outcomes (bianzhi, ISEI), no
   2014 baseline is available — the coefficient is read as ideation
   2014 → outcome 2020 controlling for everything else.
4. **Wage outcomes drop `log_income` from the controls** — for most CFPS
   respondents wage income essentially *is* total income, so the two
   are near-perfectly collinear and put all explanatory weight on
   `log_income`. All other outcomes keep `log_income` as a control.

## Controls

Per user instruction (2026-05-23): `female` (overall fits only),
`age_c = (age − 40) / 10`, `age_c2`, `urban` (hukou: qa301 → 0 = rural /
1 = urban), `edu_yrs` (`cfps20{14,20}eduy_im`), `log_income`
(per-wave income: 2014 `income`, 2020 `emp_income`). For wage outcomes
`log_income` is dropped (see above).

Sex-stratified fits drop the `female` regressor and the
`ideation × female` interaction (zero variance within stratum).

## Interpretation bounds

* **Selection on employment**. Wage / management / promotion / sub /
  bianzhi / isei models condition on `employed == 1`. Employment itself
  relates to ideology and (especially) sex, so the conditional
  coefficient is biased by the selection. Reported here without a
  Heckman correction; a follow-up Heckman or matched estimate is the
  natural next step.
* **Wage zeros**. The yearly-wage variable (`p_wage` 2014, `emp_income`
  2020) is filled with 0 for many employed respondents (self-employed,
  informal, family workers). `log1p(0) = 0` so these contribute to the
  fit. Excluding them would tighten the rate-of-pay interpretation but
  loses ~one-third of the sample. The monthly variable (`qg11`) is
  cleaner per-period; both are reported.
* **2014 monthly wage anomaly**. The `log_wage_month` β in 2014 is
  *positive* overall (+0.20) — the opposite sign from the much-larger
  yearly contrast (−0.74). The monthly variable in 2014 is sparser
  (n_nonmissing = 8 083 vs 31 553 for yearly) and disproportionately
  represents the formally-employed sub-sector, where the selection
  pattern by ideation runs the other way. The yearly variable is the
  more conservative read.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — 8 outcomes × 3 strata × 3 frames × 3 tertiles
* `02_missing_table.csv` — coverage per outcome × frame
* `04_result_table.csv` — tidy OLS / LPM (HC1, every term)
* `tables/welch_tertile_diffs.csv` — Welch's t & Cohen's d
* `figures/*.pdf` — vector outputs (`pdf.fonttype=42`)
