# analysis_004 — Interpretation note

## What the results say (RQ 5.2) — supports an ideology–practice link
All from `04_result_table.csv` / `couple_table.csv`; cross-sectional associations.

1. **Marriage:** more traditional ideology is associated with being currently married —
   LPM coefficient **+0.115 (2014)** and **+0.095 (2020)** per full index unit
   (t = 10.2, 7.6). A one-tertile shift toward traditional ≈ a few points higher
   marriage probability, net of age.
2. **Fertility intentions (2014):** more traditional → **more ideal children**
   (+0.44 child per index unit, t = 17.6). Strong and clear.
3. **Housework — the gendered finding:** the `ideation × female` interaction is large
   and positive (**+1.42 hrs in 2014, +0.96 in 2020**, t = 12.1 / 5.6). Implied total
   ideation slope is ≈ **+1.3–1.4 hrs/day for women** but ≈ 0 (2014) to +0.45 (2020)
   for men. Traditional gender ideology translates into **much more housework for women
   and little change for men** — ideology is enacted asymmetrically.
4. **Couples are assortative on ideology:** 21,680 spouse dyads, ego–spouse r = 0.22,
   mean |gap| = 0.15; **41.6% both-traditional, 19.3% both-progressive, 39.2% mixed**.

## Threats / caveats
- Reverse causation: being married / doing housework may shape attitudes too.
- `ideal_children` is an intention, not realized fertility.
- No weights; modest CFPS index reliability.
- Couple cell percentages depend on the median split; the continuous gap is the
  more robust summary.

## Next steps
- Marriage *timing* (event-history) and realized parity (roster) to sharpen the
  marriage/fertility story.
- Relate couple ideology gap/combination to housework division and fertility (dyadic models).
- Logit + weights robustness; replicate housework interaction in CGSS time-use items.
