# analysis_019 — Interpretation note

## What weighting changes (and doesn't)

**National level (`01_descriptive_table.csv`):** weighted mean ideation is slightly lower
than unweighted (2014: 0.598 → **0.585**; 2020: 0.535 → 0.533) — the sample marginally
overstates traditionalism, but the picture (and the 2014→2020 decline) is unchanged.

**Gender gap (`gender_gap_weighted.csv`):**
- 2014: unweighted female coef +0.011 (the "women slightly more traditional" anomaly) →
  **weighted +0.003, p=0.23 (not significant)**. So that anomaly was a **sampling artifact**;
  in the population there is no significant overall gender gap in 2014.
- 2020: weighted female coef **−0.027 (p<0.001)** — women significantly less traditional,
  robust to weighting.

**Transmission (`04_result_table.csv`):** the parent→child coefficient is essentially
unchanged by weighting — 0.241 → **0.247** (2014), 0.200 → **0.211** (2020), both p≪0.001.
The regeneration finding is a population-level feature, not a sampling artifact.

## Bottom line
Weighting leaves the two structural findings intact — the secular decline in traditionalism
and robust parent→child transmission — while correcting one descriptive detail: the apparent
2014 "women more traditional" gap disappears in the population (the genuine women-less-
traditional gap is the 2020 one, and the within-cohort/within-family divergence shown
elsewhere). The level of traditionalism is marginally lower once weighted.

## Caveats
Weights fix representativeness, not linkage selection in the transmission sample; robust SEs
ignore PSU clustering/stratification (true survey SEs would be a bit wider). See method note.

## Next steps
Full design-based SEs (PSU+strata) if available; weighted PSM and weighted within-family models.
