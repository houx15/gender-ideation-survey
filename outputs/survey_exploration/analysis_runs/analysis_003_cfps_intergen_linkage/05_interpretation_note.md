# analysis_003 — Interpretation note

## What the result says
**Both couple-matching and parent-child transmission analyses are feasible in CFPS**,
with large linked samples (`01_descriptive_table.csv`):

| Wave | Link | Dyads (both have index) | Within-dyad r |
|------|------|------------------------:|--------------:|
| 2014 | spouse | 21,680 | 0.22 |
| 2014 | father–child | 6,316 | 0.18 |
| 2014 | mother–child | 7,191 | 0.15 |
| 2020 | father–child | 5,048 | 0.16 |
| 2020 | mother–child | 5,475 | 0.16 |

## Main facts
1. **Couples** are the largest linkable set (~21.7k dyads in 2014) and show the
   strongest concordance (r = 0.22) — assortative mating on gender ideology is visible.
2. **Parent-child** dyads number 5–7k per parent per wave — ample for transmission models.
   Within-dyad correlations are positive (~0.15–0.18), consistent with intergenerational
   transmission worth modelling.
3. Father and mother links are similarly abundant, so **mother-vs-father path comparison
   (SPEC 5.7) is supported**.

## Threats / caveats
- Positive correlation ≠ causal transmission (shared environment, reverse influence).
- Co-residence bias: linkable kin skew toward co-resident, possibly inflating concordance.
- 2020 spouse link not resolved here (needs roster pointer); 2020 couple N is TBD, not zero.

## Next steps (high value for the dissertation)
1. Build the clean transmission sample: child age ≥ 16, parent measured same wave;
   estimate `child_index ~ mother_index + father_index (+ child female + interactions)`.
2. Add sibling structure (multi-child families) for within-family / fixed-effects designs.
3. Construct couple difference / distance / combination-type variables and relate them to
   housework division and fertility intentions (SPEC 5.2).
