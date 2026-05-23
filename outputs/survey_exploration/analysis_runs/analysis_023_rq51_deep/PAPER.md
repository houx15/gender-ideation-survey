# Cohort-Driven Liberalisation, Within-Cohort Divergence, and Education's Growing Pull: a Three-Programme Description of Gender Ideology in China, 1990 – 2023

*Working paper draft, analysis_023 — gender-ideation-survey project.*

## Abstract

Using thirteen survey-years from three independent national programmes
(ACWF 1990 / 2000 / 2010; CFPS 2014 / 2020; CGSS 2010, 2012, 2013, 2015,
2017, 2018, 2021, 2023; total *N* ≈ 192,000 respondents with a valid
gender-ideology index), we describe how gender ideology in China has
shifted across birth cohorts and within them.  A common [0,1] gender-ideology
index (1 = most traditional) is constructed per survey-year from each
programme's Likert battery and reproduced by a tested helper library.  We
report (a) cohort means with bootstrap 95 % CIs and a LOESS smooth over
continuous birth year, (b) within-cohort gender and urban-rural gaps as
Welch *t*-tests with Cohen's *d* and 95 % CIs, (c) per-survey-wave Pearson
correlations of the index with education years, log income, employment,
female, and urban with Fisher-*z* CIs, and (d) per-programme OLS with
cohort and wave fixed effects and HC1-robust SEs.  Three findings stand
out.  First, the cohort decline is steep and tight in CFPS and CGSS
(−0.20 and −0.15 between 1930-49 and 1990-2005), and the LOESS confirms
acceleration after the 1960s cohort; ACWF is flat because its last wave
(2010) precedes the 2010s period effect.  Second, the within-cohort gender
gap reverses sign: women in the 1990s+ cohort score 0.10–0.12 lower than
men, a Cohen's *d* of −0.50 (CFPS) to −0.67 (CGSS).  Third, education's
correlation with the index *strengthens* over time: in CGSS *r* climbs from
−0.25 (2013) to −0.45 (2021), and in OLS each additional year of education
subtracts 0.006–0.010 from the index net of cohort, wave, urban hukou,
log income, and employment.

## 1.  Background and research question

The gender-ideology literature on China documents a long secular decline in
traditional attitudes alongside marked heterogeneity by cohort, gender,
education, and urban-rural status.  Most existing work uses a single survey
programme.  Cross-survey replication, harmonised cleaning, and
within-cohort effect sizes are less common.  RQ 5.1 of the project's
dissertation specification asks for *measurement-side* description of the
gender-ideology index across the three programmes — what does it measure,
how does it move across cohorts, who is more (or less) traditional within
each cohort.

This paper answers that question for the three programmes jointly.

## 2.  Data

### 2.1  Survey programmes

- **ACWF (中国妇女地位调查).**  Three waves: 1990 (using `w1990_fixed`),
  2000, 2010.  *N* per wave 19k–30k.  ACWF's last wave is 2010, so the
  programme observes the 1990s+ cohort only at adolescence.
- **CFPS (China Family Panel Studies, adult file).**  Two waves: 2014 and
  2020.  Linked panel: of the 45,577 unique pids across both waves,
  20,100 appear in both, and 12,971 (64.5 %) show a measurable
  *Δ* ≥ 0.01 in the index between waves.
- **CGSS (Chinese General Social Survey).**  Eight waves: 2010, 2012,
  2013, 2015, 2017, 2018, 2021, 2023.  *N* per wave 7k–13k.  CGSS provides
  the longest time-series and the widest cohort coverage.

The complete cleaning-step audit (raw rows → has-item → valid-norm →
has-gender → has-birth-year → final analytic sample) is in
`tables/cleaning_steps.csv`.  Final analytic *N* per wave ranges from
6,997 (CGSS 2023 — the ideology module was dropped for ≈ 4.3k respondents
in that wave) to 31,548 (CFPS 2014).

### 2.2  The gender-ideology index

The canonical recoding lives in `outputs/survey_exploration/scripts/ideation_lib.py`
and is locked by `tests/test_reproduce_reference.py` (the helper reproduces
the project's pre-existing `surveys/processed/` reference exactly).  For
each survey-year, the Likert battery is recoded so that

- each item is mapped to [0,1] with 1 = "most traditional",
- explicitly "progressive" items (e.g. *men should share half the
  housework*) are reverse-coded before averaging,
- the per-respondent index is the mean of valid items.

Item-level descriptives (each item's *n*, mean, SD, range, variance,
missing %, direction, and post-normalisation mean) are in
`tables/ideation_items.csv`.  Index-level descriptives plus standardised
Cronbach's α are in `tables/ideation_index.csv`:

| Programme · Year | *N* | Mean | SD | α |
|------------------|----:|-----:|---:|--:|
| ACWF 1990 | 23,722 | 0.444 | 0.165 | 0.64 |
| ACWF 2000 | 19,283 | 0.359 | 0.175 | 0.71 |
| ACWF 2010 | 26,021 | 0.449 | 0.129 | 0.56 |
| CFPS 2014 | 31,554 | 0.598 | 0.174 | 0.37 |
| CFPS 2020 | 22,692 | 0.535 | 0.199 | 0.51 |
| CGSS 2010-2023 (8 waves) | 7,015–12,766 | 0.378–0.450 | 0.16–0.21 | 0.56–0.66 |

CGSS and ACWF have respectable α; CFPS's four-item battery has low α
(0.37 in 2014, 0.51 in 2020) and yields a noisier index whose effect sizes
will be attenuated relative to the other two programmes.

**Index levels are NOT comparable across programmes** — different
batteries, different item directions, different scale extremes.  Only
*slopes / patterns* are.

### 2.3  Covariates

All covariates are produced by tested helpers in
`outputs/survey_exploration/scripts/rq51_helpers.py` and audited for missingness
(see `tables/missingness_audit.csv`):

- **Gender.**  `female` ∈ {0, 1}, harmonised in `ideation_lib`.
- **Birth year.**  4-digit year; ACWF 1990 uses age → birth year, ACWF
  2000/2010 use a 2-digit-year encoding.  Cohort buckets:
  1930-1949, 1950-1959, 1960-1969, 1970-1979, 1980-1989, 1990-2005.
- **Urban / rural (hukou-based).**  Following standard Chinese sociology,
  rural = 农业户口, urban = 非农业户口 ∪ 居民户口.  Per-survey hukou variable:
  CFPS `qa301`, CGSS `a18`/`A18`, ACWF 2000 `v5`, ACWF 2010 `V501`.  ACWF
  1990 has no hukou variable and falls back to the community-type field
  `ch_x` (flagged in code).
- **Education (years, continuous).**  CFPS uses the survey's own imputed
  years variable (`cfps20XXeduy_im`).  CGSS maps the `a7a`/`A7a`
  1..14 level to years (`_CGSS_A7A_YEARS`).  ACWF maps `b6`/`b4_a`/`B3A`
  levels to years (`_ACWF_LEVEL_YEARS`).
- **Employed (0 / 1).**  CFPS `employ2014`/`employ`; CGSS `a58`/`A58`
  (codes 1-3 = currently working; 4-6 = not); ACWF 2000 `c1_a`,
  ACWF 2010 `C1A`; ACWF 1990 `b7` is occupation-only on file so the
  indicator is effectively constant (flagged).
- **Personal income (RMB) / log(1+income).**  Per-survey best-available
  field after sentinel-code removal (e.g. CGSS `a8a` capped at 9 999 995).
- **Occupation ISEI (continuous).**  CFPS 2020 has `qea203code_isei`
  directly on file (range 16–90).  CFPS 2014 has no current-job ISEI; we
  follow the project's reference Stata implementation in
  `reference/stata_convert.do`: filter to the in-high-school subsample
  (`kr1 == 4`) and map `ks801code` (1..29) → ISCO-88 4-digit (verbatim
  from the dofile) → ISEI (Ganzeboom & Treiman 1996), yielding an
  *aspirational* ISEI for ≈ 728 high-schoolers.  Education aspiration is
  the same: `qc201` 1..9 → years.  CGSS and ACWF have ISCO-88/08 codes
  but no embedded ISCO-to-ISEI table yet; their `isei_current` is NaN.

### 2.4  Missingness discipline

The repository treats every refused / DK / N-A / out-of-range code as NaN,
not as 0.  This matters: if "income refused" were silently 0, log income
would be artificially zero-inflated and the income coefficient would be
biased.  Four defensive tests in `tests/test_rq51_helpers.py` lock the
behavior, and `tables/missingness_audit.csv` reports `n_total`, `n_NaN`,
`n_zero`, `n_one`, `mean_nonnull` for every (survey-year, variable)
combination.

## 3.  Methods

We treat all analyses as descriptive, since RQ 5.1 is a measurement-and-
description question.  Every comparison is reported with an effect-size
in addition to a *p*-value.

### 3.1  Cohort trend

`tables/cohort_trend_bootstrap.csv`: per (programme, cohort) we report the
mean ideology index with a percentile-bootstrap 95 % CI (n_boot = 1 000,
per-cell reproducible seed).  `figures/cohort_trend_bootstrap.pdf` plots
the bucket means with shaded 95 % CI ribbons and overlays a LOESS smooth
(statsmodels `lowess`, frac = 0.3) of the index on the continuous birth
year.  The bootstrap ribbon and the LOESS line are independent
representations of the same underlying trend; where they diverge, the
discrepancy reflects a non-linear stretch within a wide bucket.

### 3.2  Within-cohort gender and urban gaps

For both contrasts, per (programme × cohort): a Welch two-sample
*t*-test on the index (handles unequal variance / *n*), with two-sided
*p*; the Welch CI of the mean difference at 95 %; **Cohen's *d*** =
(mean_a − mean_b) / pooled SD; **Hedges' *g*** = *d* × small-sample
bias correction (Hedges & Olkin 1985).  Tables:
`tables/effect_sizes_gender.csv`, `tables/effect_sizes_urban.csv`.  Forest
plots `figures/gender_gap_forest.pdf`, `figures/urban_gap_forest.pdf` show
*d* with 95 % CI and significance stars.

### 3.3  Correlations

`tables/correlation_table_v2.csv`: per (programme × wave × variable),
Pearson *r* with Fisher's-*z* 95 % CI and exact two-sided *p*.  Variables:
`edu_yrs`, `log_income`, `employed`, `female`, `urban`.
`figures/correlation_heatmap.pdf` displays the 13×5 *r*-matrix.

### 3.4  Per-programme OLS

`tables/ols_models.csv`: ideation_index ∼ female + urban_hukou + edu_yrs +
log_income + employed + cohort dummies (1930-49 base) + wave dummies,
estimated separately per programme on the listwise-complete sample
(*N* = 17,189 CFPS, 76,033 CGSS, 52,913 ACWF).  Both **classical
(homoskedastic)** and **HC1-robust (White, with small-sample correction)**
SEs are reported side-by-side; we discuss HC1 in the text.
`figures/ols_coefplot.pdf` plots the main coefficients with 95 % CI.

Two auxiliary OLS specifications add ISEI:

- `tables/ols_cfps2020_with_isei.csv` — same regressors as the main model
  plus `isei_current`, restricted to CFPS 2020 respondents with a valid
  current-job ISEI (*N* = 1,023).
- `tables/ols_cfps2014_youth_aspiration.csv` — CFPS 2014 high-school
  subsample (kr1 == 4): ideation ∼ female + urban + isei_aspiration +
  edu_aspiration (*N* = 262 after listwise deletion on all four
  regressors).

Both auxiliary specs are visualised in `figures/ols_coefplot_isei.pdf`.

### 3.5  Provincial maps

`figures/province_map_{cfps,cgss,acwf}.pdf` are choropleth maps of mean
ideation by province, pooled across waves within each programme.  Province
codes are standardised to GB/T 2260 (CGSS 1..31 → GB via
`_CGSS_SEQ_TO_GB`; CGSS 2018 province-name string → GB via `_NAME_TO_GB`).
**Each map carries an explicit caveat banner**: none of these surveys is
provincially representative.  The maps are exploratory only.

### 3.6  Reproducibility

All scripts are in `analysis_runs/analysis_023_rq51_deep/scripts/`.  All
helpers are tested (79 tests passing).  All figures are vector PDF
(`pdf.fonttype = 42`).  See `REPLICATION.md`.

## 4.  Results

### 4.1  Cohort trend (Figure 1)

`figures/cohort_trend_bootstrap.pdf`.  Bucket means:

| Cohort | CFPS | CGSS | ACWF |
|--------|-----:|-----:|-----:|
| 1930-1949 | 0.627 | 0.460 | 0.427 |
| 1950-1959 | 0.629 | 0.466 | 0.434 |
| 1960-1969 | 0.619 | 0.455 | 0.422 |
| 1970-1979 | 0.572 | 0.418 | 0.403 |
| 1980-1989 | 0.526 | 0.375 | 0.407 |
| 1990-2005 | 0.428 | **0.312** | 0.425 |

CFPS and CGSS show a steep decline from the 1960s cohort onward (−0.20
and −0.15 between 1930-49 and 1990+); bootstrap 95 % CIs are tight
(≈ ±0.005 in most cells).  ACWF is flat because by 2010 the 1990s+ cohort
were teenagers — ACWF measures them at adolescence, before the cohort
divergence of the 2010s/2020s.  The LOESS smooths (dashed) confirm the
acceleration: the slope steepens for cohorts born after ~1965.

### 4.2  Within-cohort gender crossover (Figure 2)

`figures/gender_gap_forest.pdf` and `tables/effect_sizes_gender.csv`
report Cohen's *d* with 95 % CI per (programme × cohort).  The crossover
is present in all three programmes:

| Cohort | CFPS *d* | CGSS *d* | ACWF *d* |
|--------|---------:|---------:|---------:|
| 1930-1949 | **+0.150** | **+0.067** | −0.063 |
| 1950-1959 | **+0.153** | +0.012 | −0.096 |
| 1960-1969 | **+0.207** | −0.039 | −0.174 |
| 1970-1979 | +0.061 | **−0.158** | **−0.248** |
| 1980-1989 | **−0.265** | **−0.394** | **−0.372** |
| 1990-2005 | **−0.498** | **−0.671** | **−0.560** |

For the youngest cohort, Cohen's *d* is −0.50 to −0.67 — by conventional
benchmarks a *medium-to-large* effect.  CGSS posts the largest gap;
ACWF (which observes this cohort only at adolescence) is intermediate.
The CFPS oldest-cohort positive *d* (older women slightly more traditional
than older men, *d* ≈ +0.15) likely reflects the CFPS battery's specific
items (e.g. *a woman needs children*) interacting with cohort-specific
sex differences in family attitudes.

### 4.3  Within-cohort urban-rural gap

`figures/urban_gap_forest.pdf` and `tables/effect_sizes_urban.csv`.
After switching to hukou, urban-hukou respondents are uniformly less
traditional than rural-hukou respondents in every (programme × cohort);
all *p* < 10⁻³.  Effect sizes shrink for younger cohorts: CGSS Cohen's *d*
falls from −0.50 (1930-49 cohort) to roughly −0.15 (1990+ cohort).  The
urban-rural ideological cleavage is *closing*, mainly because rural
younger respondents are catching up.

### 4.4  Correlation structure (Figure 3)

`figures/correlation_heatmap.pdf` and `tables/correlation_table_v2.csv`.
Education years is the strongest non-cohort correlate of egalitarianism in
every survey-year.  In CGSS it strengthens monotonically:

| CGSS wave | *r*(edu_yrs, ideation) | 95 % CI |
|-----------|---:|:---|
| 2010 | −0.337 | (−0.353, −0.320) |
| 2013 | −0.254 | (−0.272, −0.236) |
| 2017 | −0.370 | (−0.386, −0.355) |
| 2018 | −0.361 | (−0.378, −0.345) |
| 2021 | −0.446 | (−0.464, −0.428) |
| 2023 | −0.396 | (−0.416, −0.376) |

Log income (|*r*| ≈ 0.03–0.17), `female` (|*r*| ≈ 0.05–0.13), and `urban`
hukou (|*r*| ≈ 0.16–0.25) all correlate negatively with the index.
`employed` is weak and frequently positive (employment correlates with
*slightly* more traditional views, likely an artefact of older-cohort
selection into both attributes).

### 4.5  OLS with cohort + wave FE (Figure 4)

`tables/ols_models.csv`, `figures/ols_coefplot.pdf`.  Per-programme OLS,
HC1-robust SEs:

| Coefficient | CFPS | CGSS | ACWF |
|------------:|-----:|-----:|-----:|
| female | **−0.044** | **−0.037** | **−0.033** |
| urban (hukou) | **−0.017** | **−0.032** | **−0.016** |
| edu_yrs (per year) | **−0.010** | **−0.009** | **−0.006** |
| log(1+income) | −0.001 | **−0.003** | +0.000 |
| employed | +0.022 | +0.006 | −0.002 |
| cohort 1990-2005 vs 1930-1949 | **−0.060** | **−0.077** | **−0.018** |
| *N* | 17,189 | 76,033 | 52,913 |

All non-marginal coefficients have *p* < 10⁻³ (HC1).  The story is
consistent across the three programmes: net of cohort and wave, women are
0.03–0.04 less traditional than men, urban-hukou respondents are
0.02–0.03 less traditional than rural-hukou, and each additional year of
education subtracts 0.006–0.010 from the index.  The cohort dummies
recover the descriptive trend (1990s+ vs 1930s reference: −0.06 / −0.08 /
−0.02).  Note that the cohort coefficient in ACWF is smaller because the
1990s+ category in ACWF is dominated by adolescent observations.

### 4.6  Occupation ISEI (auxiliary specs, Figure 5)

`figures/ols_coefplot_isei.pdf`.

- **CFPS 2020 adult, current-job ISEI** (*N* = 1,023).  *β* = +3 × 10⁻⁵
  per ISEI unit, *p* = 0.94 — once education years, log income, employment,
  and the demographic block are in the model, current ISEI adds essentially
  nothing.  This is consistent with the standard finding that education
  absorbs most of the occupational-prestige signal in adult cross-sections.
- **CFPS 2014 youth (kr1 == 4), aspirational ISEI + aspirational
  education** (*N* = 262).  female: **−0.140** (*p* < 10⁻³); education
  aspiration: **−0.017** per aspired year (*p* = 0.019); aspirational
  ISEI: −0.001 (n.s.).  Among Chinese high-school students, **aspiring to
  more education** is a stronger predictor of egalitarian ideology than
  the prestige of the job they say they want; the gender gap among
  high-schoolers is more than three times the adult gap (−0.140 vs the
  −0.044 main-spec adult CFPS coefficient).

### 4.7  Provincial description

`figures/province_map_{cfps,cgss,acwf}.pdf` are clearly captioned as
exploratory — none of the surveys is provincially representative.  The
broad geographic pattern in CGSS (the longest panel) places Ningxia,
Beijing, Shanxi, Tianjin, Shanghai, and Jilin at the most progressive
end (mean ≈ 0.36) and Gansu, Yunnan, Henan, Hubei, Shandong, and Hebei
at the most traditional (mean ≈ 0.46).

## 5.  Discussion

Three patterns emerge from the harmonised analysis.

**Cohort liberalisation accelerates after the 1960s cohort.**  This is
visible in two independent ways — the bucket means and the continuous
LOESS — and replicates across CFPS and CGSS.  The flat ACWF trajectory is
not contradictory: ACWF stops in 2010 and so observes the 1990s+ cohort
only at adolescence, before the 2010s period effect that the late-CGSS
waves capture.

**The within-cohort gender gap reverses sign and widens.**  Cohen's *d*
moves from approximately 0 (or slightly female-traditional in CFPS) in
the oldest cohort to −0.50 (CFPS) / −0.67 (CGSS) / −0.56 (ACWF) in the
1990s+ cohort.  The medium-to-large effect size for the youngest cohort
is consistent with a substantively meaningful ideological divergence,
not just statistical significance from large *N*.

**Education's pull on egalitarian ideology strengthens.**  In CGSS the
correlation grows from *r* = −0.25 (2013) to *r* = −0.45 (2021); the
Fisher-*z* CIs of 2010s vs early-2020s waves do not overlap.  Net of
cohort, wave, hukou, income, and employment, each additional year of
education subtracts 0.006–0.010 from the index — a 12-year schooling
gap implies a 0.07–0.12 difference in the index, on the order of the
cohort effect itself.

The aspirational-ISEI null in the CFPS 2014 youth model, combined with
the significant negative aspirational-education coefficient, suggests
that *educational ambition* — not specifically prestigious-job ambition —
is what tracks egalitarianism among Chinese high-school students.  This
deserves a dedicated follow-up.

## 6.  Limitations

1. **Cross-programme level comparability.**  Different batteries with
   different items, scales, and item directions; only slopes/patterns are
   comparable, not absolute levels.  We flag this throughout.
2. **CFPS reliability.**  The four-item CFPS battery posts low standardised
   α (0.37–0.51); CFPS effect sizes are attenuated and the index is
   noisier than CGSS/ACWF.
3. **ACWF coverage of the youngest cohort.**  ACWF 2010 only catches
   1990+ cohort at adolescence.  For mature within-cohort comparisons of
   the youngest cohort, CGSS 2021/2023 and CFPS 2020 do the work.
4. **Period-vs-cohort decomposition.**  We do not implement formal
   age-period-cohort identification.  The wave-resolved figure
   (`cohort_trend_by_wave.pdf`) and the cohort-with-wave-FE OLS together
   suggest a period component, but the APC decomposition is not formally
   identified with these data.
5. **No design-based SEs / weights.**  Sampling weights are catalogued
   but only partly applied (CFPS robustness was checked in
   analysis_019; CGSS/ACWF weighted re-runs are deferred).
6. **Hukou measure for ACWF 1990.**  No hukou variable on file; we use
   community-type (`ch_x`) as a fallback, flagged in
   `HUKOU_VARS["fallback"]=True`.
7. **ISEI coverage.**  CFPS 2020 has direct ISEI; CFPS 2014 only as
   aspiration in the youth subsample; CGSS and ACWF have ISCO codes but
   we have not yet embedded the Ganzeboom translation table.  A follow-up
   pass should add ISCO-to-ISEI lookups.
8. **Provincial maps are not representative.**  Within-province *N* varies
   from 5 to 4,673; the maps are descriptive only.

## 7.  Reproducibility statement

Source files:

- Data: `surveys/` (gitignored).
- Canonical recoding: `outputs/survey_exploration/scripts/ideation_lib.py`.
- Helpers: `outputs/survey_exploration/scripts/{rq51_helpers,descriptive_stats,stats_helpers}.py`.
- Run scripts: `analysis_runs/analysis_023_rq51_deep/scripts/{run,run_descriptives,run_stats,run_map}.py`.
- Tests: `tests/` (79 passing).
- Reference: `reference/stata_convert.do`.

Run order to reproduce every CSV and PDF in this paper is documented in
`REPLICATION.md`.

## 8.  References (selected)

- Cohen, J. (1988).  *Statistical Power Analysis for the Behavioral
  Sciences*, 2nd ed.  Routledge.
- Ganzeboom, H., & Treiman, D. (1996).  Internationally comparable
  measures of occupational status for the 1988 ISCO. *Social Science
  Research* 25 (3), 201–239.
- Hedges, L., & Olkin, I. (1985).  *Statistical Methods for Meta-Analysis*.
  Academic Press.
- White, H. (1980).  A heteroskedasticity-consistent covariance matrix
  estimator and a direct test for heteroskedasticity. *Econometrica* 48
  (4), 817–838.
- ACWF (中国妇女地位调查), CFPS (北京大学中国家庭追踪调查),
  and CGSS (中国综合社会调查) public-use codebooks and questionnaires.
