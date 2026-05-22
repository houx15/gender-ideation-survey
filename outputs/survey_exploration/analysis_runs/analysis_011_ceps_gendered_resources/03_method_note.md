# analysis_011 — Method note

## Sample
CEPS 2013–14 baseline student file (19,487) merged 1:1 to the parent file on `ids`.
Per-outcome valid N ≈ 17.6k–19.0k (`02_missing_table.csv`).

## Variables and coding (tested in tests/test_ceps_outcomes.py)
- **female**: a01==2 → 1, a01==1 → 0.
- **parent_expect_college**: `ba18` ∈ {6,7,8,9} (大学专科+) → 1; {1..5} → 0;
  **10 = 无所谓 ("doesn't matter") → NaN** (not treated as the top of the scale).
- **tutoring / own_desk**: CEPS 1=yes/2=no via `yes12`.
- **tutoring_cost**: `ba03` yuan, cleaned to [0, 1e6], `log1p`.
- **hw_help_daily**: `b2201`==4 ("almost every day") → 1, else 0 (over valid 1–4).
- **chore_hours_week**: 5×weekday + 2×weekend daily hours, each from hour+minute via `hours_hm`.
- **has_brother**: any older/younger brother (`b0201`/`b0202` > 0). **only_child**: `b01`.
- Controls: grade9, `steco_3c` (SES 1–3), `stmedu`, `stfedu`.

## Method
LPM for binary outcomes, OLS for log-cost and chore hours. `outcome ~ female + controls`,
then `outcome ~ female × has_brother + controls` among non-only-children. Classical SEs,
no weights (tested `stats_helpers.ols`).

## Interpretation bounds
- Child sex is quasi-random → the `female` main effect is close to causal, **but**
  sex-selective abortion / son-biased stopping rules mean the set of families *with girls*
  (and especially *with a son present*) is selected. So **`has_brother` is endogenous** —
  families that have a son differ in fertility behaviour and son preference. Read the
  interaction as descriptive of son-present households, not a clean causal moderator.
- Between-student (not within-family); CEPS samples ~one child per family.
- 7th/9th graders ~2013–14, disproportionately the one-child-policy generation → many
  only-children (limits the sibling-competition subsample and its representativeness).
- No survey weights.

## Next steps
Add hukou (urban/rural) and region; model chore *and* study time jointly (time budget);
test birth-order; bring the CEPS school context in; compare to CFPS child/roster file.
