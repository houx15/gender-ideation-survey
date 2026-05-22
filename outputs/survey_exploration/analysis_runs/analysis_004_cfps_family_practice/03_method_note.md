# analysis_004 — Method note

## Sample
CFPS 2014 (N=31,554) and 2020 (N=22,692) adults with ≥1 valid ideation item.
Coverage of each outcome is in `02_missing_table.csv` (housework 2020 ≈ 73%,
others >99%). Models listwise-delete missing rows (handled in `stats_helpers.ols`).

## Variables and coding (tested in tests/test_cfps_outcomes.py)
- **ideation index**: `ideation_lib`, [0,1], 1 = most traditional.
- **currently_married**: `qea0`==2 → 1; {1,3,4,5} → 0; codes ≤0 → NaN.
- **housework_hrs**: `qq9010` (2014) / `qq9010n` (2020), kept to [0,24]; the
  workday/restday splits (qq9011/qq9012) are mostly not-applicable, so the single
  daily-hours item is used.
- **ideal_children**: `qm501` (2014), kept to [0,10]. This is a *fertility intention*,
  not realized parity (the adult file carries no living-children count — that needs
  the family roster).
- **female**: 1 = woman (CFPS raw 0).
- Controls: `age_c=(age−40)/10`, `age_c2` (LPM only).

## Methods
- `currently_married`: linear probability model (LPM) — coefficient = percentage-point
  change per unit of the [0,1] index.
- `housework_hrs`, `ideal_children`: OLS. Housework includes `ideation×female` to test
  whether ideology maps into housework differently by gender.
- Couples: descriptive |gap|, Pearson correlation, and four combination cells via a
  median split of the index.
- Classical SEs; no survey weights (sample, not population, estimates).

## Interpretation bounds
- Cross-sectional → associational only; reverse causation plausible (marriage/housework
  may shape attitudes as much as the reverse).
- LPM can yield out-of-[0,1] fitted values; used here for interpretable marginal effects.
- CFPS index reliability is modest (analysis_001) → magnitudes are indicative.
- Couple links skew co-resident; spouse pointer available 2014 only here.

## Next steps
Logit robustness for binary outcomes; survey weights + robust/clustered SEs; bring in
the roster for realized parity and for 2020 couple links; event-history for marriage timing.
