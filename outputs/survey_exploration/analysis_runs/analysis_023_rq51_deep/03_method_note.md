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
