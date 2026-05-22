# analysis_005 — Method note

## Sample
CFPS 2014 (N=31,554) / 2020 (N=22,692) adults with ≥1 valid ideation item.
Employed counts: 22,150 (2014), 16,302 (2020). Wage/management models use the
employed subset; management (qg14) is asked of a smaller employed subset
(~7,540 in 2014, ~8,215 in 2020). See `02_missing_table.csv`.

## Variables and coding (tested in tests/test_cfps_outcomes.py)
- **ideation index**: `ideation_lib`, [0,1], 1 = most traditional.
- **employed**: code 1 → 1; {0,2,3,9} (unemployed / left labour force / non-active) → 0;
  8 and negatives → NaN.
- **log_wage**: `clean_continuous` to [0, 1e7] then `np.log1p`. Wage variable differs by
  wave (`p_wage` 2014, `emp_income` 2020) and sits on **different scales/zero structure** —
  so wage *levels are not comparable across waves*; only within-wave gradients/interactions
  are interpreted.
- **mgmt / has_sub**: `yes_no` (1=是 → 1; {0,5}=否 → 0; 79 not-applicable / negatives → NaN).
- **female**: 1 = woman; controls `age_c=(age−40)/10`, `age_c2`.

## Methods
LPM for binary outcomes (employed, mgmt), OLS for log_wage. Each includes
`ideation×female` to test gender-differentiated associations. Classical SEs, no weights.

## Interpretation bounds
- Cross-sectional → associational; reverse causation plausible.
- Employed-only models (wage, mgmt) condition on a selected sample → selection bias,
  especially as employment itself relates to ideology and gender here.
- 2014 wage scale anomaly → read 2014 wage coefficients as direction/interaction, not magnitude.
- Occupation/industry/sector NOT yet coded (categorical) — a key next step for 5.3.

## Next steps
Heckman/selection-aware wage models; code occupation & sector (qg1401code management
levels, ISCO-style occupation) for a proper leadership/STEM analysis; weights + robust SEs.
