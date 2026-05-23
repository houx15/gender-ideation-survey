# analysis_023 — Method note

## Datasets

13 dataset-years are loaded through the canonical recoding pipeline
(`outputs/survey_exploration/scripts/ideation_lib.py`):

- **ACWF** (中国妇女地位调查): 1990 (w1990_fixed), 2000, 2010
- **CFPS** (China Family Panel Studies, adult file): 2014, 2020
- **CGSS** (Chinese General Social Survey): 2010, 2012, 2013, 2015, 2017, 2018,
  2021, 2023

Auxiliary context variables (birth year, urban/rural, education, employment,
personal income) are loaded by `rq51_helpers` which keeps one config block per
survey-year so every per-survey assumption is grep-able.

## Index construction (recap)

For each survey-year the canonical item battery is read, each item is mapped
to [0,1] via `ideation_lib.normalize_item`, and the per-respondent index is the
*mean of valid items*.  Direction: 1 = most traditional, 0 = most progressive.
Reversed (progressive) items are flipped before averaging.  Items, scale
extremes, and missing/agree codes for every survey live in
`tables/ideation_items.csv`.

## Cleaning steps (per dataset, per year)

`tables/cleaning_steps.csv` records the row count at each step:

1. `raw_rows` — the full .dta file.
2. `has_any_item_value` — at least one raw ideology-item value is non-missing.
3. `has_one_valid_norm_item` — at least one item maps into [0,1] after
   missing-code exclusion.
4. `has_gender` — `female` is 0 or 1.
5. `has_birth_year` — birth year is within plausible range
   (ACWF 1990 uses age→birth year; ACWF 2000/2010 use 2-digit-year encoding;
   CGSS 2018 uses provincial name; everywhere else direct numeric).
6. `final_analysis_sample` — intersection of steps 3–5.

## Cohort buckets

`COHORTS = [(1930,1949), (1950,1959), (1960,1969), (1970,1979), (1980,1989),
(1990,2005)]` — identical to analysis_021/022 so figures align.

## CFPS pid deduplication

The two CFPS waves (2014, 2020) are stacked and deduplicated by `pid`, keeping
the **latest** wave per respondent.  `cfps_dedup_keep_latest` also reports:

- `n_pids_in_both_waves`: pids that appear in both 2014 and 2020.
- `n_pids_changed`: of those, how many have |Δ ideation| ≥ 0.01 (the absolute
  index gap that exceeds a one-item rounding artefact on a 5-point scale).

The CFPS counts are recorded in `tables/cfps_repeat_summary.csv`.

## Cohort trend (figures)

Both figures use vector PDF (`pdf.fonttype = 42` so text stays editable):

- `figures/cohort_trend_pooled.pdf` — one point per (program × cohort), pooled
  across waves of each program.  Three lines (CFPS / CGSS / ACWF), error bars
  = standard error of the mean.
- `figures/cohort_trend_by_wave.pdf` — every wave plotted as its own line
  cluster, slight x-jitter per wave so they don't overlap; same colour per
  program.  Errors bars = SE.

## Within-cohort breakdowns

- `within_cohort_gender.csv` — F-mean, M-mean, F−M, Welch's t per (program,
  cohort).
- `within_cohort_urban.csv` — urban-mean, rural-mean, U−R, Welch's t per
  (program, cohort).
- `correlation_table.csv` — Pearson r and p of ideation with `edu_yrs`,
  `employed` (0/1), and `log1p(personal_income)` per (program, wave).  Rows
  with constant input get `note=constant_input`; <30 obs get `note=n<30`.

### Per-survey income variables (used in correlation)

- CFPS 2014: `income` (所有工作总收入)
- CFPS 2020: `emp_income` (税后工资性收入)
- CGSS (all waves): `a8a` / `A8a` (个人去年总收入)
- ACWF 1990: `w151` (urban personal income, monthly) — kept as-is; coverage
  limited
- ACWF 2000: `c18_a` (1999 personal income)
- ACWF 2010: `C18AA` (labour income, main-module variant of the never-married
  supplement `NC9A` which has zero overlap with the ideology sample)

### Per-survey education-to-years mapping

- CFPS 2014/2020: pre-computed years variable `cfps2014eduy_im` /
  `cfps2020eduy_im` (the imputed CFPS-supplied years-of-education).
- CGSS: `a7a` 1..14 ordinal → years via `_CGSS_A7A_YEARS` (0–22).
- ACWF: `b6` / `b4_a` / `B3A` 1..9 ordinal → years via `_ACWF_LEVEL_YEARS`.

### Per-survey employment indicator

- CFPS 2014: `employ2014` (1 = working, 0 = unemployed, 3 = out-of-LF → NaN).
- CFPS 2020: `employ` (same coding).
- CGSS: `a58` / `A58` "work experience and status": 1–3 = currently working,
  4–6 = not currently working.
- ACWF 1990: `b7` is occupation only (no explicit "not employed" code in the
  file).  We treat occupation 10..81 as employed; this means the column is
  effectively constant for the sample and is reported with
  `note=constant_input`.
- ACWF 2000: `c1_a` 1/2 = employed; positives outside that = not employed.
- ACWF 2010: `C1A` 1 = currently doing paid work.

## Provincial map

`scripts/run_map.py` produces three vector PDFs (one per program) using a
public-domain DataV.Aliyun GeoJSON of Chinese provinces
(`figures/_geo/china_provinces.geojson`, ~570 KB).

Province codes are standardized to GB/T 2260 2-digit prefixes (11..65):
- CFPS `provcd14`/`provcd20`: already 2-digit GB.
- ACWF `sheng`: already 2-digit GB.
- CGSS 2010-2017, 2021, 2023: `s41` is a 1..31 sequential index → mapped via
  `_CGSS_SEQ_TO_GB`.
- CGSS 2018: `provinces` is a string name → mapped via `_NAME_TO_GB`.

Province-level means are pooled across waves within each program with sample
weights = N per (program, province, wave).  All three maps share the same
colour scale (5th–95th percentile of all program means) for easy comparison.
A caveat banner is rendered below each map.

## Tested helpers

All helpers (cohort_label, cfps_dedup_keep_latest, urban_indicator, birth_year,
personal_income, education_years, employed_indicator, cleaning_steps_table)
are covered by `tests/test_rq51_helpers.py` (8 unit + integration tests). The
full repo test suite is green (62 tests).

---

## v2 — Statistical upgrade (paper-grade)

The additions below were added in the v2 pass.  Tested helpers:
`outputs/survey_exploration/scripts/descriptive_stats.py` (9 tests), an HC1
robust-SE variant in `stats_helpers.ols_robust` (2 tests), and the
CFPS-2014 aspirational extractors in `rq51_helpers` (2 tests).  Full repo
suite: 79 tests passing.

### Hukou-based urban / rural

The community-type fields used in v1 (`s5`, `urban14`, `type`, `isurban`,
`ch_x`) classify by sampling location, not by the respondent's hukou (户口).
v2 reclassifies using hukou status, the sociology-standard divide:

- 农业户口 → rural (0)
- 非农业户口 → urban (1)
- 居民户口 (post-reform residence registration) → urban (1)
- 蓝印 / 军籍 / 没户口 / 其他 / refused → NaN

Per-survey hukou variable: CFPS `qa301`, CGSS `a18`/`A18`, ACWF 2000 `v5`,
ACWF 2010 `V501`.  ACWF 1990 has no hukou variable on file and uses the
community fallback (`ch_x`); this is flagged in `HUKOU_VARS["fallback"]=True`.

The shift moves the urban share to a much more realistic level (CFPS now
26-28 % urban-hukou, matching well-known agricultural-hukou dominance; CGSS
40-50 %; ACWF 47 %).

### Missingness — proof it is NaN, never 0

`tables/missingness_audit.csv` reports, per (survey, variable):
`n_total`, `n_NaN`, `n_zero`, `n_one`, `mean_nonnull`.  Every variable
distinguishes NaN (refused / DK / N-A / out-of-range) from real zero (e.g.
non-earner with literal RMB 0 income).  Locked by four defensive tests in
`tests/test_rq51_helpers.py`:

- `test_employed_indicator_keeps_acwf_1990_outside_set_as_nan`
- `test_income_missing_codes_are_nan_not_zero_cfps`
- `test_urban_indicator_negative_codes_become_nan`
- `test_education_years_returns_nan_for_unknown_levels`

### Education: highest level → years (continuous)

Following standard sociological practice, every survey's education variable is
mapped from highest-completed level (categorical) to years (continuous).  CFPS
uses the survey's own imputed years variable (`cfps20XXeduy_im`); CGSS uses
the `a7a` 1..14 level to years map (`_CGSS_A7A_YEARS`, 0..22); ACWF uses
`_ACWF_LEVEL_YEARS`.

### Occupation: ISEI (continuous)

Following standard practice (Ganzeboom & Treiman 1996), we use **ISEI**
(International Socio-Economic Index of Occupations) as the continuous
occupation measure, not categorical job-type codes.

- **CFPS 2020** — `qea203code_isei` is directly on file (range 16–90).
- **CFPS 2014** — has no direct ISEI.  Per the user's reference
  implementation in `reference/stata_convert.do`, we filter to the
  in-high-school subsample (kr1==4) and map `ks801code` (occupational
  aspiration, 1..29) → ISCO-88 4-digit codes (verbatim from the dofile) →
  ISEI (embedded Ganzeboom values for the 22 ISCO codes referenced).  This
  yields `isei_aspiration` for **728 high schoolers** — a youth-aspiration
  measure, *not* current-job ISEI.  Education aspiration `edu_aspiration`
  follows the same dofile: qc201 1..9 → years.
- **CGSS, ACWF** — have ISCO-88 / ISCO-08 4-digit codes on file but require
  the Ganzeboom translation table to obtain ISEI.  Deferred — `isei_current`
  is NaN for these surveys and a row showing 100 % missingness appears in
  Table 1.

### Paper-grade Table 1 (per survey-year)

`tables/descriptives_{dataset}_{year}.csv` — one Table-1 per survey-year with
variable name, explanation, n (non-missing), mean, sd, min, max, n_missing,
missing %.  Variables: ideation, female, birth year, urban (hukou),
education years, employed, ISEI current, ISEI aspiration, edu aspiration,
income, log(1+income).  A combined long-format
`tables/descriptives_long.csv` (143 rows) supports cross-survey comparison.

### Cohort trend with bootstrap 95 % CI and LOESS smooth

`tables/cohort_trend_bootstrap.csv` — for every (program, cohort), the
mean ideation index and the **percentile bootstrap 95 % CI** (n_boot = 1000,
per-group reproducible seed).  `figures/cohort_trend_bootstrap.pdf` overlays:

- the cohort means with shaded 95 % CI ribbons (one ribbon per program), and
- a **LOESS smooth** (statsmodels `lowess`, frac = 0.3) of ideation on the
  continuous birth-year axis, drawn as a dashed line per program.

### Effect-size tables and forest plots

For both **gender** and **urban-rural**, per (program, cohort):

- Welch's t-test on independent samples (handles unequal variance / N)
- exact two-sided p-value
- **Cohen's d** = (mean_a − mean_b) / pooled_sd
- **Hedges' g** (small-sample-corrected d)
- 95 % CI of the mean difference

`tables/effect_sizes_gender.csv` and `tables/effect_sizes_urban.csv`.
`figures/gender_gap_forest.pdf` and `figures/urban_gap_forest.pdf` plot
Cohen's d with 95 % CI bars per (program, cohort), with significance stars
(`*` p<.05, `**` p<.01, `***` p<.001).

### Correlation heatmap (Fisher-z CI)

`tables/correlation_table_v2.csv` — per (program, wave) Pearson r with the
**Fisher's-z 95 % CI** and exact p-value, for ideation vs each of edu_yrs,
log_income, employed, female, urban.  `figures/correlation_heatmap.pdf`
shows the r values as a (survey × variable) heat map with cell annotations.

### OLS with cohort + wave fixed effects (per program)

`tables/ols_models.csv` — one regression per program, ideation ∼ female +
urban + edu_yrs + log_income + employed + cohort dummies (1930-1949 base)
+ wave dummies.  Both **classical** and **HC1 heteroskedasticity-robust**
SEs (and the corresponding t / p) are reported side by side.
`tables/ols_meta.csv` has N and df per program.
`figures/ols_coefplot.pdf` shows all coefficients with 95 % CI (HC1).

Additional OLS specifications:

- `tables/ols_cfps2020_with_isei.csv` — adds current-job `isei_current`
  to the CFPS 2020 regression (single-wave; N ≈ 1,000).
- `tables/ols_cfps2014_youth_aspiration.csv` — CFPS 2014 kr1==4 subsample:
  ideation ∼ female + urban + isei_aspiration + edu_aspiration (N ≈ 687).
