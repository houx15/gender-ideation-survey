# analysis_021 — CGSS replication of the cohort × gender divergence (SPEC 5.1)

**Research question:** Does the CFPS finding (analysis_002) — younger cohorts less
traditional, with a gender-gap crossover where younger women diverge from younger men —
replicate across CGSS's eight waves (2010–2023), which give far more cohort/temporal power?

**Analysis type:** Measurement / individual practice; pooled cross-sectional replication.

**Data / sample:** CGSS 2010, 2012, 2013, 2015, 2017, 2018, 2021, 2023 (the a421–a425
ideation battery; CGSS 2011 excluded — no module). Respondents with ≥1 valid item, known
gender, and birth year 1920–2007. Pooled N = 86,318.

**Model:** `ideation ~ decade_c + female + decade_c×female + wave fixed effects`, where
`decade_c = (birth_year − 1970)/10`. A negative `decade×female` interaction = the gender gap
widens (women relatively more egalitarian) in younger cohorts.
