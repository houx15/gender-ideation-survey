# analysis_002 — Interpretation note

## What the result says
Strongly supports a **cohort gradient** in gender ideology, and reveals a
**gender-gap crossover** by cohort.

1. **Later cohorts are less traditional.** Per decade of later birth the index falls
   −0.017 (2014) and −0.031 (2020); both far exceed their standard errors
   (see `04_result_table.csv`).
2. **The gender gap crosses over by cohort** (`01_descriptive_table.csv`):
   - Pre-1980 cohorts: **women slightly MORE traditional** than men (F−M ≈ +0.01 to +0.04).
   - 1980s and 1990s+ cohorts: **women markedly LESS traditional** (F−M = −0.06 in 2014,
     down to **−0.11 in the 1990–2004 cohort in 2020**).
   - The negative `decade_c:female` interaction (−0.017 in 2014, −0.033 in 2020) captures this.

## Why this matters
It explains the analysis_001 anomaly where CFPS-2014 women looked *slightly more*
traditional overall: that average is dominated by older-cohort women. Once cohort is
held constant, **young women are the most egalitarian group and are diverging fastest
from young men** — a widening within-cohort gender divergence between 2014 and 2020.

## Threats / caveats
- Two waves only → cannot disentangle age, period, and cohort.
- No weights; classical SEs.
- Modest CFPS index reliability → treat magnitudes as indicative.
- Survival/selection in the oldest cohort (1930–49) may bias that cell.

## Next steps
- Replicate the cohort gradient and crossover in CGSS (8 waves → better APC leverage).
- Add survey weights and robust SEs.
- Probe mechanism: is young-women divergence concentrated in the housework/career items
  vs the "marry well"/"need children" items? (item-level cohort models).
