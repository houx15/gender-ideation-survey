# analysis_021 — Interpretation note

## The CFPS cohort crossover replicates cleanly in CGSS (8 waves, N=86,318)

**Gender gap by cohort (pooled, `01_descriptive_table.csv`):**

| Cohort | F − M |
|--------|------:|
| 1930–49 | +0.012 |
| 1950–59 | +0.002 |
| 1960–69 | −0.006 |
| 1970–79 | −0.028 |
| 1980–89 | −0.071 |
| 1990–2005 | **−0.120** |

The crossover is unmistakable: in the oldest cohort women are slightly *more* traditional
than men; from the 1960s cohort the sign flips, and by the 1990s+ cohort women are far more
egalitarian (gap −0.12) — the same shape found in CFPS (analysis_002), now across eight waves.

**Pooled model with wave fixed effects (`04_result_table.csv`):**
- `decade_c` = −0.0126 (t=−24.5): each decade of later birth ⇒ less traditional.
- `female` = −0.033 (t=−26.5): women less traditional at the 1970 reference.
- **`decade×female` = −0.0219 (t=−30.7, p≈0)**: the gender gap widens strongly with each
  younger cohort — the divergence is large, monotonic, and extremely precisely estimated.

## Bottom line
The cohort gradient and the widening within-cohort gender divergence are **not a CFPS
artifact** — they replicate with high precision across CGSS's eight waves. Younger Chinese
women are pulling away from younger men in gender ideology, robustly across two independent
survey programs.

## Caveats
Pooled cross-sections (no clean APC separation); no weights; classical SEs ignore clustering;
CGSS levels not comparable to CFPS (only slopes/patterns are). See method note.

## Next steps
Formal APC; weighted + clustered SEs; urban/rural split; (later) link to provincial climate.
