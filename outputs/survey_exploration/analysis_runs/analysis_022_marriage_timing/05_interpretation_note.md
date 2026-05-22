# analysis_022 — Interpretation note

## Association: more traditional ⇄ younger first marriage, especially for women
Pooled CGSS ever-married, N=71,560 (`04_result_table.csv`):

- `ideation` = **−1.77 years** (t=−14.7): across the full [0,1] ideation range, more
  traditional men first-married ~1.8 years younger.
- `female` = −1.43 (t=−18.9): women first-married ~1.4 years younger than men.
- **`ideation×female` = −1.34 (t=−8.4)**: the traditional→younger-marriage gradient is
  steeper for women — implied total slope ≈ **−3.1 years** for women vs −1.8 for men.
- `decade_c` = +0.07: later cohorts marry marginally later (small).

Descriptive (`01_descriptive_table.csv`) matches: mean age at first marriage falls from 23.5
(least-traditional women) to 22.0 (most-traditional women), and 25.1 → 24.4 for men.

## What this does and does NOT mean
- **Does:** people who married younger hold more traditional gender views today, and this
  link is stronger among women — consistent with marriage timing and gender ideology being
  bound together in the life course.
- **Does NOT:** show that traditional ideology *causes* earlier marriage. Ideation is measured
  decades after the marriage, so the arrow could run the other way (early marriage / marital
  life entrenching traditional views), or reflect stable selection. The within-cohort
  association is descriptive only.

## Readiness conclusion for the "marriage timing" cell
A genuine **event-history/survival** model of marriage timing is **not identifiable** with
these data: it requires the attitude measured *before* the at-risk period. CGSS/CFPS measure
ideology once, post-marriage for most respondents. This cell should be reported as
**descriptive-only**; causal timing needs a panel with a youth attitude baseline.

## Caveats
Reverse time order (central); ever-married selection; no weights; classical SEs. See method note.

## Next steps
Panel/youth-baseline data for causal timing; weighted + clustered SEs; parallel first-birth
timing if a clean first-birth year is available.
