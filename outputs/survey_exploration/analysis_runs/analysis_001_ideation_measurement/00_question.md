# analysis_001 — Gender-ideation measurement

**Research question (SPEC 5.1):** How is gender ideation measured in each survey,
is a single mean index defensible, and how does it distribute by gender and year?

**Analysis type:** Measurement exploration.

**Data / years / sample:**
- ACWF 1990, 2000, 2010 (main individual files)
- CFPS 2014, 2020 (adult files)
- CGSS 2010, 2012, 2013, 2015, 2017, 2018, 2021, 2023 (CGSS 2011 excluded — no ideation module)
- Sample = all respondents with ≥1 valid item on the core battery.

**Core variables:**
- Explanatory/构造: the core comparable gender-ideation battery per survey
  (ACWF w6xx / i3_x / J2x; CFPS qm1101–qm1104; CGSS a421–a425 / A42_1–A42_5).
- Grouping: gender (standardized female=1/male=0), survey year.

**Index convention:** each item normalized to [0,1], 1 = most traditional;
respondent index = mean of valid normalized items (matches
`surveys/processed/methodology.md`).
