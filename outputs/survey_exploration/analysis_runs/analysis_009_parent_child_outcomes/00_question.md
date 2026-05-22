# analysis_009 — Parent ideology & child outcomes / gendered allocation (SPEC 5.5+5.6)

**Research question:** Do more traditional parents have children with less education,
and do they invest **less in daughters relative to sons** (gendered resource allocation)?

**Analysis type:** Intergenerational reproduction (cross-sectional, within-wave dyads).

**Data / sample:** CFPS 2014 & 2020. Child = adult respondent linked to **both** parents
(`pid_f`/`pid_m`; 2020 `pid_a_f`/`pid_a_m`), with both parents' ideation and the child's
years of schooling valid. N = 5,343 (2014) / 3,980 (2020).

**Core variables:**
- Outcome: child's completed years of schooling (`cfps20XXeduy`).
- Explanatory: `mother_ideation`, `father_ideation`, `child_female`, and the gendered-
  allocation interactions `mother×daughter`, `father×daughter`. Controls: child age, age².

**The test:** negative `parent×daughter` interactions would indicate traditional parents
penalize daughters' schooling relative to sons.

**Caveats:** time-ordering (child schooling largely completed before parent ideology is
measured) and **co-residence selection** (linked adult children — especially co-resident
daughters — are a selected group).
