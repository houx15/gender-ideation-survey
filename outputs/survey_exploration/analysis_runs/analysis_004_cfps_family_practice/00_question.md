# analysis_004 — CFPS gender ideology & family practice (SPEC 5.2)

**Research question:** Among CFPS adults, is gender ideology associated with
family-practice outcomes — marriage, fertility intentions, the housework division —
and do couples match on ideology?

**Analysis type:** Individual practice (cross-sectional association) + couple matching.

**Data / years / sample:** CFPS 2014 & 2020 adult files; respondents with ≥1 valid
ideation item. Couple analysis: 2014 respondents linked to an in-sample spouse (`pid_s`).

**Core variables:**
- Explanatory: gender-ideation index ([0,1], 1 = most traditional).
- Outcomes: `currently_married` (qea0=2), daily `housework_hrs` (qq9010/qq9010n),
  `ideal_children` (qm501, 2014 only).
- Moderator: gender (female=1); controls: age, age².
- Couple: |ego − spouse| ideation gap, ego–spouse correlation, combination types
  (median split).

**Caveat (time order):** marriage, housework and fertility intentions are measured
at the same wave as attitudes; associations are **not** causal and direction is
ambiguous (SPEC 12.6–12.7).
