# Replication & extension guide — analysis_023 (RQ 5.1 deep-dive)

This document describes how to reproduce every CSV and PDF in
`analysis_runs/analysis_023_rq51_deep/`, what each script does, and how to
extend the analysis with a new survey-year or a new variable.  It is the
single entry point if you (or a future collaborator) want to re-run, audit,
or build on this work.

---

## 1.  Directory layout

```text
gender-ideation-survey/                                ← repo root
├── surveys/                                           ← raw .dta files (gitignored)
├── reference/
│   └── stata_convert.do                              ← user-provided CFPS 2014 ISEI/aspirations dofile
├── outputs/
│   └── survey_exploration/
│       ├── scripts/                                   ← tested helper library
│       │   ├── ideation_lib.py                       ← canonical [0,1] index per survey
│       │   ├── rq51_helpers.py                       ← urban / edu / income / employ / ISEI / cleaning
│       │   ├── descriptive_stats.py                  ← describe_var, cohen_d, hedges_g, welch_ci_diff, bootstrap_mean_ci
│       │   ├── stats_helpers.py                      ← ols, ols_robust (HC0/HC1), wls, icc_oneway, fe_ols
│       │   ├── cfps_outcomes.py, ceps_outcomes.py    ← labour / education helpers
│       │   ├── cfps_linkage.py, matching.py          ← family linkage, PSM
│       │   └── verify_coding.py                      ← coding-audit helper
│       └── analysis_runs/
│           └── analysis_023_rq51_deep/                ← THIS RUN
│               ├── 00_question.md
│               ├── 01_descriptive_table.csv
│               ├── 02_missing_table.csv
│               ├── 03_method_note.md
│               ├── 04_result_table.csv
│               ├── 05_interpretation_note.md
│               ├── PAPER.md                          ← academic write-up (RQ 5.1)
│               ├── REPLICATION.md                    ← this file
│               ├── tables/                           ← all CSV outputs
│               ├── figures/                          ← all vector PDFs
│               │   └── _geo/china_provinces.geojson  ← DataV.Aliyun province polygons
│               └── scripts/
│                   ├── run.py                        ← base run (cleaning, items, trends, breakdowns)
│                   ├── run_descriptives.py           ← Table 1 per (program, year)
│                   ├── run_stats.py                  ← bootstrap CI, effect sizes, OLS, plots
│                   └── run_map.py                    ← province choropleths
└── tests/                                            ← pytest suite (79 passing)
    ├── test_ideation_lib.py
    ├── test_reproduce_reference.py
    ├── test_rq51_helpers.py
    ├── test_descriptive_stats.py
    ├── test_stats_helpers.py
    ├── test_cfps_outcomes.py
    ├── test_ceps_outcomes.py
    ├── test_cfps_linkage.py
    └── test_matching.py
```

---

## 2.  Run order

From the repository root, in order:

```bash
# 0.  Run the test suite first.  If it doesn't pass, do not produce outputs.
python -m pytest tests/ -q

# 1.  Base run: cleaning table, item & index descriptives, pooled & by-wave
#     cohort trend (SE), CFPS pid-dedup, within-cohort gender / urban tables,
#     baseline correlation table.
python outputs/survey_exploration/analysis_runs/analysis_023_rq51_deep/scripts/run.py

# 2.  Paper-grade Table 1 per (program, year).
python outputs/survey_exploration/analysis_runs/analysis_023_rq51_deep/scripts/run_descriptives.py

# 3.  Statistical upgrade: bootstrap CIs, effect sizes (Cohen's d + Hedges' g
#     + Welch CIs), Fisher-z correlation, per-program OLS with HC1 robust SEs,
#     two ISEI specs, and all the v2 figures.
python outputs/survey_exploration/analysis_runs/analysis_023_rq51_deep/scripts/run_stats.py

# 4.  Province choropleths (CFPS / CGSS / ACWF).  Requires geopandas.
python outputs/survey_exploration/analysis_runs/analysis_023_rq51_deep/scripts/run_map.py
```

The four scripts are independent (no in-memory shared state) but they share
the same helper library, so any change in `outputs/survey_exploration/scripts/`
will be picked up on the next run.

### Run-time and outputs

| Script | ~Wall time | Writes to |
|--------|-----------:|-----------|
| `run.py`             | 1–2 min | `tables/{cleaning_steps,ideation_items,ideation_index,cfps_repeat_summary,cohort_trend_pooled,cohort_trend_by_wave,within_cohort_gender,within_cohort_urban,correlation_table}.csv`<br>`figures/{cohort_trend_pooled,cohort_trend_by_wave}.pdf` |
| `run_descriptives.py`| <1 min  | `tables/descriptives_{dataset}_{year}.csv` (13 files) + `descriptives_long.csv` |
| `run_stats.py`       | 1–2 min | `tables/{cohort_trend_bootstrap,effect_sizes_gender,effect_sizes_urban,correlation_table_v2,ols_models,ols_meta,ols_cfps2020_with_isei,ols_cfps2014_youth_aspiration}.csv`<br>`figures/{cohort_trend_bootstrap,gender_gap_forest,urban_gap_forest,correlation_heatmap,ols_coefplot,ols_coefplot_isei}.pdf` |
| `run_map.py`         | <1 min  | `tables/province_means.csv`<br>`figures/province_map_{cfps,cgss,acwf}.pdf` |

A separate one-off audit `tables/missingness_audit.csv` is regenerated inside
the project tree directly (see §6 of the method note).

---

## 3.  Environment

- Python 3.12 (any 3.10+ should work).  Required packages:
  `pandas`, `numpy`, `scipy`, `pyreadstat`, `statsmodels`, `scikit-learn`
  (for matching), `geopandas`, `pyshp` (for `run_map.py`), `matplotlib`.
- macOS notes: `sips` (used for ad-hoc PDF → PNG previews) is available
  on macOS by default and not required to reproduce outputs.
- Stata is *not* required.  `reference/stata_convert.do` is consulted as
  a coding reference; its mappings are re-implemented in
  `rq51_helpers.cfps2014_aspiration_isei` and `cfps2014_aspiration_edu_years`.

---

## 4.  Files at a glance

### Tables (`tables/`)

| File | Produced by | Description |
|------|-------------|-------------|
| `cleaning_steps.csv` | run.py | raw → final analytic *N* per (dataset, year) |
| `ideation_items.csv` | run.py | per-item descriptives (raw n / mean / sd / direction / missing %) |
| `ideation_index.csv` | run.py | aggregate index descriptives + Cronbach's α |
| `cfps_repeat_summary.csv` | run.py | pid dedup summary across CFPS 2014 / 2020 |
| `cohort_trend_pooled.csv` | run.py | (program × cohort) mean ± SE |
| `cohort_trend_by_wave.csv` | run.py | (program × cohort × wave) mean ± SE |
| `cohort_trend_bootstrap.csv` | run_stats.py | (program × cohort) mean + percentile-bootstrap 95 % CI |
| `within_cohort_gender.csv` | run.py | F-mean, M-mean, F − M, Welch *t* |
| `within_cohort_urban.csv` | run.py | U-mean, R-mean, U − R, Welch *t* |
| `effect_sizes_gender.csv` | run_stats.py | Welch *t* / df / *p* / 95 % CI of diff / Cohen's *d* / Hedges' *g* |
| `effect_sizes_urban.csv` | run_stats.py | same for urban-rural |
| `correlation_table.csv` | run.py | per (program × wave) Pearson *r* + *p* (legacy) |
| `correlation_table_v2.csv` | run_stats.py | same + Fisher-*z* 95 % CI |
| `ols_models.csv` | run_stats.py | per-program OLS, classical + HC1 SEs |
| `ols_meta.csv` | run_stats.py | *N* and df per program |
| `ols_cfps2020_with_isei.csv` | run_stats.py | CFPS 2020 OLS with current-job ISEI |
| `ols_cfps2014_youth_aspiration.csv` | run_stats.py | CFPS 2014 youth OLS with aspirational ISEI + edu |
| `descriptives_{dataset}_{year}.csv` | run_descriptives.py | Table 1 per survey-year |
| `descriptives_long.csv` | run_descriptives.py | combined long-format Table 1 |
| `missingness_audit.csv` | one-off | NaN ≠ 0 audit per (survey, variable) |
| `province_means.csv` | run_map.py | mean ideation per (program, province) pooled across waves |

### Figures (`figures/`, all vector PDF, `pdf.fonttype = 42`)

| File | Produced by | Shows |
|------|-------------|-------|
| `cohort_trend_pooled.pdf` | run.py | three pooled-per-program lines, error bars = SE |
| `cohort_trend_by_wave.pdf` | run.py | every wave plotted; same program → same colour |
| `cohort_trend_bootstrap.pdf` | run_stats.py | bucket means with bootstrap 95 % CI ribbons (solid) + LOESS smooth on continuous birth year (dashed) |
| `gender_gap_forest.pdf` | run_stats.py | Cohen's *d* (F − M) with 95 % CI per (program × cohort) |
| `urban_gap_forest.pdf` | run_stats.py | Cohen's *d* (U − R) with 95 % CI per (program × cohort) |
| `correlation_heatmap.pdf` | run_stats.py | Pearson *r* of ideation with edu_yrs / log_income / employed / female / urban, by (program × wave) |
| `ols_coefplot.pdf` | run_stats.py | main per-program OLS coefs with 95 % CI (HC1) |
| `ols_coefplot_isei.pdf` | run_stats.py | auxiliary ISEI OLS specs (CFPS 2020 adult + CFPS 2014 youth) |
| `province_map_{cfps,cgss,acwf}.pdf` | run_map.py | provincial choropleths (with non-representativeness caveat banner) |

---

## 5.  Helper library

### `outputs/survey_exploration/scripts/ideation_lib.py`

- `SURVEYS` — dictionary mapping (dataset, year) → file path, gender variable,
  province variable, scale max, agree code, and item list.
- `normalize_item(series, scale_max, agree_code, direction)` — maps a raw
  Likert item to [0,1] where 1 = most traditional.
- `load_recoded(dataset, year, extra_cols=None)` — returns
  `(df, meta, norm_cols, idx_col_name)`.  `df` always contains the raw
  items, the normalised item columns (suffix `_z`), a harmonised `female`
  0/1 column, `province_raw`, `n_valid_items`, and `ideation_index`.
- `cronbach_alpha(item_df)` — standardised α.

### `outputs/survey_exploration/scripts/rq51_helpers.py`

Per-survey configuration tables (every map is grep-able):

| Table | Purpose |
|-------|---------|
| `HUKOU_VARS` | hukou-based urban/rural per (dataset, year) |
| `BIRTH_VARS` | birth-year variable + plausible range; encodes special cases (ACWF 1990 = age, ACWF 2000/2010 = 2-digit year) |
| `INCOME_VARS` | personal-income variable + valid range with sentinels excluded |
| `EDU_VARS` | level-to-years mapping per survey (continuous education years) |
| `EMP_VARS` | employment indicator per survey |
| `ISEI_VARS` | ISEI variable per survey (currently only CFPS 2020) |
| `_CGSS_A7A_YEARS`, `_ACWF_LEVEL_YEARS` | level → years lookups |
| `_CFPS_KS801_TO_ISCO88`, `_ISCO88_TO_ISEI`, `_CFPS_QC201_TO_YEARS` | CFPS 2014 youth aspiration (per `reference/stata_convert.do`) |
| `_CFPS_MISSING_CODES` | CFPS sentinel set treated as NaN |
| `COHORTS` | birth-year cohort buckets |

Functions:

- `cohort_label(year)` — bucket label, NaN if out-of-range.
- `cfps_dedup_keep_latest(df, pid_col, wave_col, value_col, change_eps)` —
  dedup CFPS by pid, keep latest wave, return (`deduped`, `summary`)
  where `summary` includes `n_pids_in_both_waves` and `n_pids_changed`.
- `cleaning_steps_table(dataset, year)` — per (dataset, year) list of
  `{step, n}` rows from raw to final.
- `urban_indicator(dataset, year)` — hukou-based 0 (rural) / 1 (urban),
  NaN otherwise.
- `birth_year(dataset, year)` — 4-digit, handles ACWF 1990 age → year and
  ACWF 2000/2010 2-digit encoding.
- `personal_income(dataset, year)` — RMB.
- `education_years(dataset, year)` — continuous years from per-survey
  level → years map (or direct years for CFPS imputed).
- `employed_indicator(dataset, year)` — 0/1 currently employed.
- `occupation_isei(dataset, year)` — current-job ISEI (CFPS 2020 only;
  others NaN-aligned).
- `cfps2014_aspiration_isei()` — youth (kr1==4) aspirational ISEI.
- `cfps2014_aspiration_edu_years()` — youth aspirational education years.

### `outputs/survey_exploration/scripts/descriptive_stats.py`

Pure stats (no I/O):

- `describe_var(series, name, explanation)` — Table-1 row.
- `describe_frame(df, varspec)` — Table-1 over a (column, name,
  explanation) list.
- `cohen_d(a, b)` / `hedges_g(a, b)` — standardised mean difference.
- `welch_ci_diff(a, b, alpha=0.05)` — Welch test + CI of mean diff.
- `bootstrap_mean_ci(arr, n_boot=1000, seed=0, alpha=0.05)` — percentile
  bootstrap.

### `outputs/survey_exploration/scripts/stats_helpers.py`

- `ols(X, y)` — classical (homoskedastic) SEs.
- `ols_robust(X, y, kind="HC1")` — heteroskedasticity-robust SEs
  (HC0 = White; HC1 = small-sample-corrected Stata default).
- `wls(X, y, w)` — weighted least squares with robust sandwich SEs.
- `icc_oneway(value, group)` — one-way ANOVA ICC.
- `fe_ols(df, group_col, y_col, x_cols)` — within-demeaned OLS.

---

## 6.  How to extend

### 6.1  Adding a new survey-year

1. Drop the .dta into `surveys/` (gitignored).
2. In `outputs/survey_exploration/scripts/ideation_lib.py`, add an entry to
   `SURVEYS` for the new `(dataset, year)` with:
   - `file`: relative path,
   - `gender_var` and `province_var` names,
   - `scale_max` and `agree_code` (high or low code = agree),
   - `items`: dict of `{var: (short_label, "traditional" | "progressive")}`.
3. In `rq51_helpers.py`, add per-survey entries to:
   - `HUKOU_VARS`, `BIRTH_VARS`, `INCOME_VARS`, `EDU_VARS`, `EMP_VARS`
     (and `ISEI_VARS` if a direct field exists).
4. Add the survey-year to the `BIRTH` / cohort scripts in
   `analysis_runs/analysis_021_cgss_cohort_replication/` and
   `analysis_runs/analysis_022_marriage_timing/` if it's a CGSS wave.
5. Add an integration test for the new survey to
   `tests/test_rq51_helpers.py` (probe at least urban, employed, income,
   edu_yrs, birthy ranges + NaN counts).
6. Re-run the test suite first, then the four run scripts in order
   (§ 2 above).

### 6.2  Adding a new variable to Table 1 / OLS

1. Add a per-survey extractor to `rq51_helpers.py` (with a per-survey
   config dict; never hard-code variable names in the analysis script).
2. Write at least one defensive test: for one survey known to have refused
   codes, assert that `n_NaN` > 0 and `n_zero` is *not* equal to the count
   of refused codes (proves NaN ≠ 0).
3. Add the new variable to `VARSPEC` in `run_descriptives.py`.
4. Add the column to the `_attach_context` keep-list in `run_stats.py`.
5. Add the variable to the X-matrix in `build_ols_per_program` (and update
   the `dropna(subset=...)` list).
6. Re-run.

### 6.3  Adding a new statistical test or figure

1. If pure (no I/O), put it in `descriptive_stats.py` and write at least
   one synthetic-data unit test.
2. If it consumes raw survey data, put the I/O-touching code in
   `run_stats.py` and write an integration test that checks the output
   CSV has the expected shape / N.
3. All figures are vector PDF with `pdf.fonttype = 42`; reuse the
   `PROGRAM_COLOR` palette and the `COHORTS_ORDER` axis.

### 6.4  When tests fail after raw-data changes

If a `.dta` file is replaced / re-curated, the integration tests in
`tests/test_rq51_helpers.py` will trip on the assumed *N*-of-respondents
constants (e.g. CFPS 2014 raw rows = 39 768).  This is by design — the
test failure forces a deliberate update of the documented assumptions.
Investigate the source change, update the assertions, and re-run.

---

## 7.  Conventions

- **Raw data is gitignored.**  `surveys/` is never committed.
- **Outputs are tracked.**  Every CSV and PDF in `analysis_runs/*/` is
  committed, so collaborators have the reproducible result without
  needing the raw data.
- **Missing values are NaN, never 0.**  Locked by tests; audited via
  `tables/missingness_audit.csv`.
- **Education is continuous (years), not categorical (level).**
- **Urban / rural is hukou-based.**
- **Occupation is ISEI** (where available); other occupation codings are
  not used as continuous regressors.
- **Effect sizes are reported alongside p-values.**
- **All figures are vector PDF.**
- **Helpers are tested; analysis scripts orchestrate.**  No untested
  business logic in `run*.py`.
- **Every assumption that varies by survey lives in a per-survey config
  dict, not inside an `if dataset == ...` chain.**

---

## 8.  Known pitfalls

- **`pyreadstat.read_dta` with `usecols=` preserves row order** across
  multiple reads of the same file.  This lets us call separate
  per-variable extractors and concatenate them by row index.  If you
  swap reader libraries, this assumption needs re-verification.
- **`pyreadstat` returns Stata `tab` levels as ints / floats depending on
  storage type.**  Always coerce with `pd.to_numeric(..., errors="coerce")`
  before comparing to codes.
- **`pd.NA` does not interoperate cleanly with float dtypes.**  Use
  `np.nan` in float64 Series (cfps_outcomes was migrated to this
  convention).
- **Stata sentinels vary across surveys.**  ACWF 2000 uses 999996–999999;
  ACWF 2010 uses 9999997; CGSS uses 9999996–9999999; CFPS uses
  −10..−1 + 79.  Each is handled per-survey in the config dicts.
- **Project-boundary hook blocks writes outside `surveys/...`/
  `outputs/...`/`tests/...`/etc.**  Use in-project paths (or
  `/tmp` redirects are blocked and would need `--dangerously-…`).

---

## 9.  Where to read next

- `PAPER.md` — academic write-up of the substantive findings.
- `00_question.md` — the original RQ 5.1 statement.
- `03_method_note.md` — methodological detail (v1 + v2 upgrade).
- `05_interpretation_note.md` — section-by-section result narration.
- `09_findings_summary.md` (project-wide) — synthesis across all RQs.
