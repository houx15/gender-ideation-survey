# 00 · Research question — analysis_027

## SPEC anchor

RQ 5.3: **Does gender ideation associate with or predict labour-force
participation, wages, leadership / management posts, and promotion?**

The user-defined scope (deeper / academic-level version of
`analysis_005_cfps_work_leadership`):

| Outcome | 2014 var | 2020 var | Notes |
|---|---|---|---|
| **Employed** | `employ2014` | `employ` | binary; already in panel |
| **Log monthly wage** | `qg11` | `qg11` | per-period; primary wage measure |
| **Log yearly wage** | `emp_income` (≈ `p_wage`) | `emp_income` | total earnings; robustness check |
| **Management role** | `qg14` | `qg14` | binary 是/否 |
| **Promotion** | `qg15` | `qg15` | binary (1/2/3 → 1, 78/79 → 0). *Was missing from analysis_005.* |
| **Has subordinate** | `qg17` | `qg17` | binary |
| **Has 编制** (bianzhi) | — | `qg2032` | 2020 only |
| **Occupation ISEI** | — | `qg303code_isei` | 2020 only; current main job |

## Design

Same dual-frame pattern as analysis_023 / 025 / 026:

* **2014 cross-section** (~31.5 k adults)
* **2020 cross-section** (~22.7 k adults)
* **Lagged panel** (`ideation_2014 → outcome_2020 + outcome_2014`) for the
  six outcomes that exist in both waves.

Each outcome × frame stratified to **overall / male / female**, with
`ideation × female` in the overall fit.

Wage and management / subordinate / promotion models condition on
**employed = 1** (the natural at-risk pool); employment itself is modelled
on the full sample.

## Methods

* **Welch's t / Cohen's d** between top vs bottom ideation tertile, per
  sex stratum.
* **OLS-HC1** for continuous (log wage, ISEI) and **LPM-HC1** for binary
  (employed, mgmt, promotion, has_sub, bianzhi).
* **Lagged** fits include the 2014 level of the outcome on the RHS, so
  the ideation coefficient is on the change.

## Controls

Following user instruction (2026-05-23): `female` (overall only),
`age_c = (age − 40) / 10`, `age_c2`, `urban` (hukou), `edu_yrs`,
`log_income` (2014: `log1p(income)`; 2020: `log1p(emp_income)`).

## Caveats

* **Wage scales differ across waves** (p_wage 2014 vs emp_income 2020;
  qg11 is yearly-equivalent monthly in both). Cross-wave levels are not
  directly comparable. Both reported in log1p form for symmetry.
* **Mgmt / promotion / sub** condition on `employed == 1` → selection on
  labour-force participation, which itself relates to ideology and sex.
  Caveat in 03_method_note.
* **bianzhi** (`qg2032`) is 2020-only and only asked of those employed
  in formal-sector jobs; very high missingness (~ 90 %).
* **ISEI** is the ISEI prestige score for the current main job; only
  in 2020 and only for the employed.

## Files

* `scripts/run.py` — pipeline
* `tables/welch_tertile_diffs.csv` — Welch's t & Cohen's d
* `01_descriptive_table.csv`, `02_missing_table.csv`,
  `04_result_table.csv`, `05_interpretation_note.md`
* `figures/*` — vector PDFs (`pdf.fonttype=42`)
