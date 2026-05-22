# analysis_016 — Transmission PSM, enhanced (CFPS, SPEC 5.7)

**Research question:** Is the parent→child ideation transmission robust to richer matching,
a formative-age restriction, and honest (bootstrap) inference — using survey data only?

**Analysis type:** Intergenerational reproduction; PSM with bootstrap.

**Improvements over analysis_015 (the requested next steps):**
- **Formative window:** restrict children to **age 16–30** (closest to the socialization period).
- **Richer match:** parent mean education + child **urban/rural** + child age + child sex.
- **Bootstrap SEs:** `matching.psm_att_boot` replaces the optimistic paired-t p-value from
  matching-with-replacement.

**Data / sample:** CFPS 2014 & 2020 children linked to both parents. Treatment = traditional
parent (top tertile of parent-mean ideation) vs egalitarian (bottom tertile). Outcome =
child ideation index ([0,1], 1 = most traditional).

No provincial / contextual ideology climate used (survey data only, per request).
