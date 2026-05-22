# analysis_006 — CFPS gender ideology & education (SPEC 5.4)

**Research question:** Is education associated with gender ideology, and does its
association differ by gender (does schooling make women less traditional faster
than men)?

**Analysis type:** Individual practice / measurement context (cross-sectional),
gender-moderated.

**Time-ordering (important):** for adults, educational attainment is largely
**completed before** the attitude is measured. So the temporally sensible direction
is **education → ideation** (schooling shaping attitudes), not the reverse. We model
the ideation index as the outcome of years of schooling.

**Data / years / sample:** CFPS 2014 & 2020 adults with ≥1 valid ideation item and
valid years of schooling.

**Core variables:**
- Outcome: gender-ideation index ([0,1], 1 = most traditional).
- Explanatory: `eduy` (years of schooling), gender (female=1), `eduy×female`.
- Controls: age, age².
