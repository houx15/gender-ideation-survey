# analysis_006 — Interpretation note

## What the results say (RQ 5.4)
1. **Education is strongly associated with less traditional ideology.** Each year of
   schooling lowers the index by **−0.006 (2014) / −0.009 (2020)** for men (t ≈ −19, −21).
2. **Education de-traditionalizes women faster than men.** The `eduy×female` interaction
   is negative (**−0.003 in 2014, −0.007 in 2020**, t = −7.9, −13.1), so the per-year
   slope for women is ≈ −0.009 (2014) and **−0.016 (2020)** — almost double the male slope.
3. **The gap opens at the top of the education distribution** (`01_descriptive_table.csv`,
   2020): with *no* schooling women ≈ men (0.648 vs 0.651), but at **college 0.335 vs 0.453**
   and **postgrad 0.233 vs 0.436**. Uneducated men and women are equally traditional;
   highly educated women are far more egalitarian than highly educated men.

## How this connects to the project's theme
This mirrors the cohort crossover (analysis_002): **women's ideology is the more
*responsive* variable** — it moves more with education and birth cohort than men's does.
Combined with analysis_004/005 (women's ideology, not men's, predicts their housework and
labour outcomes), it points toward the hypothesis that **within families women's ideology
may be the more consequential one** — tested directly next (couple & parent-child models).

## Threats / caveats
- Observational; education is selected on background and ability.
- Linear `eduy` understates the college-concentrated divergence (see descriptives).
- No weights; CFPS index reliability modest.

## Next steps
CGSS replication; parental-background controls; CEPS for adolescents (attitudes and
schooling measured close in time, avoiding the adult time-order issue).
