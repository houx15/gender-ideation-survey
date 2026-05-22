# analysis_001 — Interpretation note

## What the result says (RQ 5.1)
1. **A comparable battery exists in every target survey-year except CGSS 2011**,
   which carries no gender-ideation module. CGSS 2023 asked the battery as a
   **split-ballot sub-module** (~38% system-missing; effective N≈7,000).
2. **A mean index is defensible but modest in reliability.** Cronbach's alpha:
   ACWF 2000 = 0.71 (best), ACWF/CGSS mostly 0.56–0.66, **CFPS = 0.37 (2014) / 0.51 (2020)**.
   The CFPS battery (4 items, one reverse-coded housework item) is the weakest;
   treat the CFPS index cautiously and prefer single-item analyses there.
3. **Validation:** our recoded national means reproduce
   `surveys/processed/gender_ideation_by_year.csv` exactly (diff = 0.0000, N matches),
   confirming the recoding matches the established methodology.

## Main descriptive facts
- **Women are less traditional than men** in 12 of 13 survey-years (mean female−male
  gap ≈ −0.02 to −0.05 on the 0–1 scale). The lone reversal is **CFPS 2014 (+0.011)**.
- **Within CGSS, the gender gap widens over time** (−0.011 in 2010 → −0.054 in 2023),
  and overall traditionalism trends **downward** (CGSS mean 0.446 → 0.378).
- ACWF and CFPS levels are not directly comparable to CGSS (different items).

## Threats / caveats
- Low alpha (esp. CFPS) → index is a coarse summary; single items may behave differently.
- No design weights yet → these are sample, not population, estimates.
- CGSS 2023 split-ballot → 2023 sample is a sub-sample; trend endpoint is less certain.
- Cross-survey level comparisons are invalid; only trends/gaps within a survey hold.

## Next steps
- analysis_002: birth-cohort trends (is the secular decline cohort- or period-driven?).
- Dimensionality check (family-role vs leadership vs housework sub-scales).
- Add design weights and re-estimate national means + gaps.
- Decide per-RQ whether to use index vs single items (CFPS likely single-item).
