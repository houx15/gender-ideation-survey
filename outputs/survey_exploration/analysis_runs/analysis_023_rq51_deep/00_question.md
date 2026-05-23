# analysis_023 — RQ 5.1 deep-dive

For every survey we use to measure gender ideology — ACWF (1990/2000/2010),
CFPS (2014/2020), CGSS (2010-2023, 8 waves) — produce:

1. **Cleaning table** — original N → step-by-step exclusions → final analysis N.
2. **Item + index descriptives** — which items, direction (reversed?), per-item n /
   mean / sd / min / max / missing %; aggregate index descriptives (mean / sd / min /
   max / var / n) after [0,1] normalization where 1 = most traditional.
3. **Cohort time trend** (vector PDF) — three lines (CFPS, CGSS, ACWF), mean ± SE
   per birth-cohort × program.  CFPS is deduplicated by `pid` keeping the latest
   wave; we report (i) how many pids appear in both 2014 and 2020 and (ii) how
   many of those changed their ideation (|Δ| ≥ 0.01).
4. **Within-cohort breakdowns** — gender gap (F−M) by cohort, urban/rural gap by
   cohort, and the correlation of ideation with education (years), employment (0/1)
   and personal income (logged) per dataset.
5. **Provincial map** (vector PDF, separate map per program) — mean ideation by
   province, with the explicit caveat that none of these surveys are provincially
   representative.

Every output goes to `tables/` (CSVs) and `figures/` (PDF vector).  The script
uses only tested helpers in `outputs/survey_exploration/scripts/` so nothing here
is one-off.
