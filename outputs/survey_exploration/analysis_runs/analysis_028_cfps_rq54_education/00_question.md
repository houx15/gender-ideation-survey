# 00 · Research question — analysis_028

## SPEC anchor

RQ 5.4: **Does gender ideation associate with or predict years of education?**

The methodological challenge is flagged in SPEC §5.4.4: adult final
education is almost always set *before* any 2014 ideation measurement, so
the cross-section ideation → edu_yrs slope is **reverse-causal by
construction** for most respondents.

Design for this run handles that explicitly:

| Frame | n | What it estimates | Causal frame |
|---|---|---|---|
| **A. 2014 cross-section, full adult sample** | ~31.5 k | ideation_2014 ↔ edu_yrs_2014 | descriptive only |
| **B. 2020 cross-section, full adult sample** | ~22.7 k | ideation_2020 ↔ edu_yrs_2020 | descriptive only |
| **C. Young-cohort cross-section (birthy ≥ 1990)** | ~5 k in 2014, ~3 k in 2020 | ideation ↔ edu_yrs for those still potentially in school | weaker reverse-causal pressure |
| **D. Young-cohort lagged Δ** (birthy ≥ 1990, panel) | ~1.5 k | ideation_2014 → Δ_edu_yrs (2014 → 2020) | directional: ideation measured before some of the later schooling |

For (D), only those whose `edu_yrs` *changed* between 2014 and 2020
contribute substantive variation; the rest are flat at Δ = 0. The fit is
on the panel (`ideation_2014 → edu_yrs_2020 + edu_yrs_2014` so the
β is on the change).

## Outcomes

| Outcome | Variable | Coding |
|---|---|---|
| **edu_yrs** | `cfps20{14,20}eduy_im` | imputed years of education, [0, 22] |
| **edu_level** (descriptive) | `cfps2014edu` (2014) / `w01` (2020) | unified ordinal 0..7 (illiterate / primary / junior / senior / college / bachelor / masters / PhD) |

Coding for `edu_level` (descriptive table only — *not* a regression outcome):

| Unified level | 2014 `cfps2014edu` | 2020 `w01` |
|---|---|---|
| 0  illiterate / no school | 1, 9 | 0, 10, 1, 2 |
| 1  primary               | 2     | 3 |
| 2  junior high           | 3     | 4 |
| 3  senior high / vocat.  | 4     | 5 |
| 4  college (大专)         | 5     | 6 |
| 5  bachelor              | 6     | 7 |
| 6  masters               | 7     | 8 |
| 7  PhD                   | 8     | 9 |

## Stratification

Overall / male / female on every frame.

## Methods

* **Welch's t and Cohen's d** between top vs bottom ideation tertile.
* **OLS-HC1** on edu_yrs (continuous outcome).
* **By-cohort descriptives** (birthy decade × ideation tertile × sex)
  to make the time-ordering issue visible.

## Controls

Per project convention: `female` (overall fits only), `age_c = (age − 40)/10`,
`age_c2`, `urban` (hukou), `log_income`. NO `edu_yrs` control here
(it's the outcome).

## Caveats

* **The dominant signal in (A) and (B) is reverse-causal**: adults who
  finished more schooling *then* became more progressive — not the other
  way around. (A) / (B) coefficients are reported but should be read as
  associational only.
* **The young-cohort frame (C / D)** has a much-weakened reverse-causal
  pressure, but is still cross-sectional in (C) and on a small panel
  in (D). Read as "ideation at age ≤ 24 in 2014 associates with future
  schooling done between 2014 and 2020", not as a strict causal claim.

## Files

* `scripts/run.py`, `01_*`, `02_*`, `03_method_note.md`, `04_*`,
  `05_interpretation_note.md`, `tables/welch_tertile_diffs.csv`,
  `figures/*.pdf` (vector, `pdf.fonttype=42`).
