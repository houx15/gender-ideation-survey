# analysis_008 — Parent → child ideation transmission (SPEC 5.7)

**Research question:** Does a parent's gender ideology predict their adult child's
ideology, does the **mother or the father** transmit more, and are there same-gender
vs cross-gender paths (mother→daughter, father→son, …)?

**Analysis type:** Intergenerational reproduction (cross-sectional, within-wave dyads).

**Data / sample:** CFPS 2014 & 2020. Child = adult respondent (age ≥16, all have the
ideation battery) linked to **both** in-sample parents via `pid_f`/`pid_m`
(2014: `pid_f`/`pid_m`; 2020: `pid_a_f`/`pid_a_m`). N = 5,564 (2014) / 4,120 (2020)
children with both parents measured.

**Core variables:**
- Outcome: child's ideation index ([0,1], 1 = most traditional).
- Explanatory: `mother_ideation`, `father_ideation` (entered together), `child_female`,
  and gender interactions `mother×daughter`, `father×daughter`. Control: child age.

**The test:** mother vs father coefficient (`whose_ideation_comparison.csv`); the
interactions test same- vs cross-gender transmission.
