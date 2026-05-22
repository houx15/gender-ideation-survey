# analysis_014 — Gender gap in resources via PSM (CEPS, SPEC 5.5)

**Research question:** Robustly, how much more (or less) of each resource do daughters
get than sons, once we match on observable family characteristics rather than just
adjusting in a regression (analysis_011)?

**Why PSM here:** CEPS samples ~one child per family, so within-family designs do not
apply; PSM matching daughters to sons on observables is the natural "all families"
estimator. Reports the ATT of being a daughter with p-values.

**Data / sample:** CEPS 2013–14 baseline; student × parent merged on `ids` (~18k+ matched
per outcome).

**Treatment:** being a daughter (female=1). **Match covariates:** family economic status,
mother's & father's education, grade, number of siblings.

**Outcomes:** parental college expectation, tutoring participation, log tutoring cost,
own study desk, near-daily homework help, weekly housework hours.
