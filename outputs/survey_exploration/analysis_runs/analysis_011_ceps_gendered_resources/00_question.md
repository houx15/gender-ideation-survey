# analysis_011 — How do families allocate resources to daughters vs sons? (CEPS, SPEC 5.5)

**Research question:** Do families invest differently in daughters and sons, and demand
different chore burdens? Where does son preference show up?

**Why CEPS:** it observes children **during schooling** (grades 7 & 9) with a matched
parent questionnaire — so it measures investment *as it happens*, avoiding the life-stage
and co-residence problems that defeated the adult-attainment approach (analysis_009/010).
Child sex is quasi-random, so a gender gap in investment is close to a causal "effect of
being a daughter" (subject to sex-selective fertility caveats).

**Analysis type:** Gendered resource allocation (between-student, with sibling-structure test).

**Data / sample:** CEPS 2013–14 baseline; student file merged to parent file on `ids`
(N = 19,487).

**Resource outcomes:**
- *Investments:* parental college expectation (`ba18`), paid tutoring (`ba02`), tutoring
  spending (`ba03`, log), own study desk (`b11`), near-daily homework help (`b2201`).
- *Demands:* weekly housework hours (`b15g`/`b16g`).

**Predictor:** `female` (a01==2). **Controls:** grade, family economic status (`steco_3c`),
parents' education (`stmedu`/`stfedu`). **Son-preference test:** `female × has_brother`
among non-only-children.
