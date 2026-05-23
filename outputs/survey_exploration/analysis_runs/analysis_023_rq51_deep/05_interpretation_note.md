# analysis_023 — Interpretation note  (RQ 5.1 deep-dive)

## (1) Cleaning yields

`tables/cleaning_steps.csv`.  Most attrition comes from the ideology battery
being a *module* rather than a universal block:

| Program | Raw N | Final analytic N | Attrition |
|---------|------:|-----------------:|----------:|
| ACWF 1990 | 23,740 | 23,722 | 0.08 % |
| ACWF 2000 | 19,449 | 19,283 | 0.85 % |
| ACWF 2010 | 29,693 | 26,021 | 12.4 % |
| CFPS 2014 | 39,768 | 31,548 | 20.7 % (children/proxy/skip) |
| CFPS 2020 | 28,530 | 22,641 | 20.6 % |
| CGSS 2010–2018 | ~10–12 k each | full battery answered by ~97–99 % |
| CGSS 2021 | 8,148 | 8,131 | 0.2 % |
| CGSS 2023 | 11,326 | 6,997 | 38.2 % (ideology module dropped for ~4.3 k respondents) |

Take-away: every CGSS wave except 2023 has near-complete ideology coverage;
CFPS loses ~20 % to skip patterns (mostly under-aged/proxy respondents); ACWF
2010 loses ~12 % primarily because the battery sat in a module not asked of
every respondent.

## (2) Item-level descriptives

`tables/ideation_items.csv` lists every item we use, its short label, raw mean
/ sd / min / max / variance, missing %, the reversed-flag, and the per-item
normalized mean.  `tables/ideation_index.csv` then gives the aggregate index
descriptives plus standardized Cronbach's α:

- **Index range**: 0.0 – 1.0 in every survey (the [0,1] normalization is valid
  end-to-end).
- **Index mean** sits between 0.36 (CGSS 2023 — most progressive average) and
  0.60 (CFPS 2014).  CFPS levels are systematically higher because its 4-item
  battery includes two items (children-needed, men-share-housework) that tilt
  toward "agree".  Levels are NOT comparable across programs — only slopes/
  patterns are.
- **Reliability (α)**: CGSS waves are stable around 0.55–0.66.  ACWF 1990 α =
  0.64 (8 items) is fine.  ACWF 2010 α = 0.56.  **CFPS α is low** (0.37 in
  2014, 0.51 in 2020) — its 4-item battery captures a noisy, multi-dimensional
  attitude.  We still use the mean as a parsimonious index; users should
  treat CFPS effect sizes as somewhat attenuated relative to CGSS/ACWF.

## (3) Cohort time trend

### Figures

- `figures/cohort_trend_pooled.pdf` — three pooled lines (vector PDF).
- `figures/cohort_trend_by_wave.pdf` — wave-resolved version (vector PDF).

### What the pooled chart shows (`tables/cohort_trend_pooled.csv`)

| Cohort | CFPS mean | CGSS mean | ACWF mean |
|--------|----------:|----------:|----------:|
| 1930-1949 | 0.627 | 0.460 | 0.427 |
| 1950-1959 | 0.629 | 0.466 | 0.434 |
| 1960-1969 | 0.619 | 0.455 | 0.422 |
| 1970-1979 | 0.572 | 0.418 | 0.403 |
| 1980-1989 | 0.526 | 0.375 | 0.407 |
| 1990-2005 | 0.428 | **0.312** | 0.425 |

- **CFPS and CGSS show a steep monotonic decline** from the 1960s cohort to
  the 1990s+ cohort: −0.20 in CFPS, −0.15 in CGSS, both extremely tight (SE
  ≈ 0.002–0.005).  Younger Chinese are far less traditional.
- **ACWF is flat** because by 2010 (its latest wave) the 1990s cohort were
  teenagers and the 1980s cohort barely-adults; ACWF picked them up at a life
  stage *before* the cohort divergence had matured.  This is consistent with
  the period mechanism: the *decline* is mostly a 2010s/2020s phenomenon
  captured by CGSS 2017/2018/2021/2023 but not by 2010-era ACWF.

### What the by-wave chart adds

`figures/cohort_trend_by_wave.pdf` shows CGSS 2021 and 2023 measuring the
1990s cohort at ~0.24–0.26 while CGSS 2010 measured them at ~0.37.  The
oldest cohorts barely move between waves.  So the cohort decline is amplified
by a *period* effect for younger respondents — they are sliding further
toward egalitarianism over the 2010s/2020s, while older respondents stay
roughly put.

### CFPS pid dedup report (`tables/cfps_repeat_summary.csv`)

- 68,298 CFPS rows in 2014+2020 collapse to **45,577 unique pids**.
- **20,100 pids appear in both 2014 and 2020.**
- Of those, **12,971 (64.5 %) changed their ideation by ≥ 0.01** between the
  two waves.

> Take-away: we have a non-trivial within-person panel.  ~13 k respondents
> with a measurable Δ ideation across 6 years means a within-person change
> analysis (and an event-study around marriage, childbirth, urban-move, or
> schooling completion) is feasible in CFPS.  This is the strongest unlock in
> this report.

## (4) Within-cohort breakdowns

### Gender gap (F − M)  —  `tables/within_cohort_gender.csv`

| Cohort | CFPS F−M | CGSS F−M | ACWF F−M |
|--------|---------:|---------:|---------:|
| 1930-1949 | **+0.023** (t=4.8) | +0.012 (t=4.1) | −0.011 (t=−3.5) |
| 1950-1959 | +0.023 (t=5.7) | +0.002 (t=0.8) | −0.015 (t=−6.5) |
| 1960-1969 | +0.033 (t=8.7) | −0.006 (t=−2.4) | −0.028 (t=−12.3) |
| 1970-1979 | +0.011 (t=2.4) | −0.028 (t=−10.0) | −0.038 (t=−13.6) |
| 1980-1989 | −0.050 (t=−10.6) | −0.071 (t=−22.3) | −0.053 (t=−12.7) |
| 1990-2005 | **−0.097** (t=−20.3) | **−0.120** (t=−30.1) | −0.075 (t=−7.6) |

The **crossover** seen in analysis_002/021 is **robust across all three
programs**: older women are slightly *more* traditional than men (or
indistinguishable); from the 1980s cohort onward women are clearly more
egalitarian than men, and the gap widens monotonically.  The 1990s+ female
ideology runs 0.10–0.12 below male ideology in both CFPS and CGSS.

### Urban / rural gap (U − R)  —  `tables/within_cohort_urban.csv`

| Cohort | CFPS U−R | CGSS U−R | ACWF U−R |
|--------|---------:|---------:|---------:|
| 1930-1949 | −0.034 (t=−7.0) | −0.083 (t=−26.4) | −0.064 (t=−21.2) |
| 1950-1959 | −0.027 (t=−6.6) | −0.068 (t=−23.3) | −0.050 (t=−21.5) |
| 1960-1969 | −0.030 (t=−7.7) | −0.070 (t=−24.6) | −0.039 (t=−17.3) |
| 1970-1979 | −0.046 (t=−9.9) | −0.074 (t=−22.7) | −0.036 (t=−12.8) |
| 1980-1989 | −0.054 (t=−11.2) | −0.060 (t=−15.1) | −0.024 (t=−5.7) |
| 1990-2005 | −0.052 (t=−10.2) | −0.041 (t=−7.7) | −0.034 (t=−3.4) |

Urban residents are **uniformly less traditional than rural residents in
every cohort × program** (all t-statistics highly significant).  The gap is
largest in CGSS (~0.07) and shrinks somewhat for the youngest cohort —
younger rural respondents are catching up, but a meaningful gap persists.

### Correlations with adult outcomes  —  `tables/correlation_table.csv`

Across every dataset-year, **education years correlate negatively with
ideation** — more education ⇒ less traditional — with r ranging from −0.16
(ACWF 2000) to **−0.45 (CGSS 2021)**, every p ≪ 0.001.  The CGSS coefficient
*grows* in absolute value over time (−0.25 in 2013 → −0.45 in 2021), so the
education–egalitarianism link is strengthening.  Employment is much weaker
(|r| ≈ 0.01–0.08, signs mixed); log personal income is mildly negatively
correlated (|r| ≈ 0.03–0.17).

> Take-away: of the three covariates, education is by far the strongest
> individual-level correlate of egalitarianism, and the link has tightened
> over the last decade.  Income and employment have small marginal roles
> after education.

## (5) Provincial map

`figures/province_map_cfps.pdf`, `figures/province_map_cgss.pdf`,
`figures/province_map_acwf.pdf`.  Pooled-across-waves province means with a
shared colour scale (5th–95th percentile of all program means) and an
explicit caveat banner.  `tables/province_means.csv` has the raw numbers.

Pattern (CGSS pooled, the most-complete program):
- **Most progressive provinces (lowest index)**: Ningxia (0.36), Beijing
  (0.36), Shanxi (0.38), Tianjin, Shanghai, Jilin.
- **Most traditional**: Gansu (0.47), Yunnan (0.46), Henan (0.46), Hubei
  (0.46), Shandong, Hebei.

CFPS pooled flags the same broad story (Tibet/Ningxia/Qinghai most
progressive but with tiny N; Jiangxi/Fujian/Jilin most traditional).
ACWF pooled flags Gansu, Tibet, Qinghai as most traditional and Inner
Mongolia / Yunnan / Liaoning as most progressive.

**These maps are exploratory only.**  None of the surveys are provincially
representative.  Within-province N ranges from 5 (CFPS Tibet) to 4,673 (CGSS
Beijing), and the displayed mean mixes urban/rural and cohort composition.
The caveat is repeated on every map.  See cleaning_steps.csv for per-wave N
and the province_means.csv for per-province N.

## Bottom line for RQ 5.1

1. The [0,1] ideology index reproduces the methodology-document reference
   exactly and has plausible (though low for CFPS) Cronbach α.
2. The pooled cohort decline is **steep and tight in CFPS and CGSS, flat in
   ACWF** — the latter because ACWF stopped in 2010, *before* the 2010s
   period effect on younger cohorts kicked in.
3. CFPS gives us a within-person panel of ~13 k respondents with measurable
   ideology change — this is the principal unlock for any future
   change-over-time / event-study analysis.
4. Within every cohort, women are diverging from men (younger cohorts:
   F < M by 0.10–0.12); urban respondents are systematically less
   traditional than rural (by 0.04–0.08); education has a strong, growing
   negative association with ideation; income/employment are minor.
5. Provincial differences exist but the surveys cannot speak to them with
   anything resembling representative power.
