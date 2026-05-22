# analysis_005 — Interpretation note

## What the results say (RQ 5.3) — a gender-differentiated ideology–labour link
From `04_result_table.csv` (cross-sectional, associational).

1. **Employment:** the `ideation×female` interaction is negative and significant
   (**−0.092 in 2014, −0.108 in 2020**, t = −3.5 / −4.0). Reading the slopes:
   - Men: more traditional → slightly *more* likely employed (+0.07/+0.09).
   - Women: net slope ≈ **−0.02**, i.e. traditional women are *less* likely employed.
   This is the classic gendered pattern — ideology pulls men and women in opposite
   directions on labour-force participation.
2. **Wages (employed):** strong negative `ideation×female` (−2.03 in 2014, −1.02 in 2020,
   t = −5.6 / −5.9) — traditional women earn substantially less; the traditional wage
   penalty is far larger for women than men. (2014 wage *magnitude* is unreliable due to
   scale; the sign/interaction is robust and replicates in 2020.)
3. **Management (employed):** more traditional → less likely to hold a management post
   (−0.070 in 2014, −0.107 in 2020); the gender interaction is small/insignificant, so
   this gradient is similar for employed men and women.

## Putting it together
Traditional gender ideology is associated with women being **less in paid work, paid
less when working, and less often in management** — while for men the employment
association runs the opposite way. Consistent with ideology shaping a gendered division
between market and family work (and complements the housework finding in analysis_004).

## Threats / caveats
- Reverse causation (labour-market position may shape attitudes).
- Wage/management models condition on employment, which is itself selected on ideology+gender.
- 2014 wage scale; occupation/sector not yet coded; no weights.

## Next steps
Code occupation/sector and qg1401code management levels; selection-aware wage models;
weights + robust SEs; replicate the employment interaction in CGSS.
