# 00 · Research question — analysis_026

## SPEC anchor

RQ 5.2 (individual level): **how does gender ideation associate with or predict
individual-level family practice in CFPS?**

The user-defined scope for this run (deeper / academic-level version of
`analysis_004_cfps_family_practice`):

| Outcome (family field) | 2014 var | 2020 var | Notes |
|---|---|---|---|
| Currently married | `qea0==2` | `qea0==2` | binary; cross-section + lagged |
| Age at first marriage | `qea205y - cfps_birthy` | `qea205y - ibirthy` | retrospective; descriptive only |
| Ideal children num | `qm501` | not asked | 2014 cross-section only |
| Housework hours / day | `qq9010` | `qq9010n` | continuous; cross-section + lagged + Δ |

## Design

Each outcome is estimated under **two predictor conventions side-by-side**,
chosen to match the time-ordering they can actually support:

* **Cross-sectional** (`ideation_t ↔ outcome_t`): largest n, descriptive
  only; reverse causation is on the table.
* **Lagged panel** (`ideation_2014 → outcome_2020 | controls_2014`):
  restricted to the ~12 k CFPS panel, but ideation is measured strictly
  before the outcome → defensibly directional.

Each fit is **stratified to overall / male / female** (matching the
`analysis_023 / 025` pattern). The interaction `ideation × female` is
estimated in the overall fit to formally test gender-moderation.

## Methods

* **Welch's t-test** between high- vs low-tertile ideation on each outcome,
  reported per sex.
* **OLS with HC1 robust SEs** (continuous outcomes) and **LPM with HC1**
  (binary), controls: `age_c = (age − 40) / 10`, `age_c²`, `urban`,
  `edu_yrs`, `log_income`. Lagged fits use 2014 covariates and (for
  continuous outcomes) include `outcome_2014` on the RHS so the
  coefficient is on the change.
* **Effect-size accompaniments**: Cohen's d (continuous) and risk
  difference / odds ratio (binary).

## Caveats

* Marriage and current housework are partly *upstream* of attitudes —
  the lagged frame restricts to outcomes measured **after** ideation
  2014, but the retrospective marriage-age outcome remains descriptive
  ("married earlier ↔ holds more traditional views now") not causal
  (see analysis_022 framing).
* Ideal-children num is only asked in 2014, so it has no lagged version.
* Housework time has a strongly gendered floor (most men report < 1 h),
  so OLS on raw hours is reported alongside `log1p(hours)` as a
  sensitivity check.

## Files

* `scripts/run.py` — the full pipeline.
* `tables/` — descriptive, fit-by-fit, and ideation × female forest data.
* `figures/` — PDFs (`pdf.fonttype=42`) for each outcome and stratification.
* `01_descriptive_table.csv` — tertile × sex means / proportions.
* `02_missing_table.csv` — per-outcome coverage.
* `03_method_note.md` — methods detail.
* `04_result_table.csv` — tidy regression summary.
* `05_interpretation_note.md` — substantive reading.
