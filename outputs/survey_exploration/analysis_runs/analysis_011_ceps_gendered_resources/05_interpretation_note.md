# analysis_011 — Interpretation note

## How families allocate resources to daughters vs sons — two layers

### Layer 1: overall (sample is mostly only-children)
With SES controls (`04_result_table.csv`, `female` coefficient):
- **Daughters receive MORE educational investment.** Parents expect college more for girls
  (+0.042, t=8.8), girls are more likely to attend **tutoring** (+0.043, t=6.7) and have
  **more spent** on it (log cost +0.30, t=6.1); they are marginally more likely to have an
  own desk (+0.012).
- **But daughters carry a heavier domestic load and slightly less study supervision.**
  Girls do ~**0.7 more hours of housework/week** (t=4.0); boys get more near-daily homework
  checking (−0.04, t=−6.4).

So the modern (2013–14) pattern is *not* simple son-favouring investment — if anything,
**girls are pushed harder on both schoolwork and chores** ("doing it all"), while boys get
more hands-on academic monitoring.

### Layer 2: son preference appears with sibling competition
The `female × has_brother` interaction (non-only-children) reveals where the classic
son preference still operates:
- **Tutoring spending: the girls' advantage significantly reverses when a brother is present**
  (`female×has_brother` = **−0.33, t=−2.7**); the girl-favouring tutoring gap also weakens
  (−0.026, t=−1.7).
- Girls with a brother tend to do **even more chores** (+0.81, t=1.4, suggestive).
- College *expectations* for girls stay high regardless of brothers (interaction ≈ 0).

**Reading:** in one-child families daughters are invested in heavily; **once she competes
with a brother, monetary educational resources tilt back toward the son and her chore burden
rises.** Son preference survives at the margin of within-household competition, masked in the
averages by the prevalence of only-children.

## Caveats
- `has_brother` is **endogenous** (son-biased stopping → families with a son are selected);
  the interaction is descriptive of son-present households, not a clean causal moderator.
- Between-student, one child per family; one-child-policy cohort; no weights.

## Next steps
Hukou/region and birth-order; joint time-budget (study vs chores); compare with a CFPS
child/roster file; link to community/family gender-ideology climate where available.
