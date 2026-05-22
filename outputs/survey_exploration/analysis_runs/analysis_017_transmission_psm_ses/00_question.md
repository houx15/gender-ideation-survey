# analysis_017 — Transmission PSM + family SES proxy (CFPS 2014, SPEC 5.7)

**Research question:** Does the parent→child ideation transmission survive controlling for
family socioeconomic status (the main confounder still missing from analysis_016)?

**Data boundary (important):** there is **no CFPS family file** in the data (only the adult
files), and CFPS 2020 has **no personal-total-income variable**, so household income is
unavailable. The best in-survey SES proxy is the **parents' personal total income**
(`p_income`, CFPS 2014), attached via the parent links. ~47% of values are legitimate
zeros (non-earners: homemakers, students, elderly), which are kept; negatives → missing.

**Analysis type:** Intergenerational reproduction; PSM with bootstrap; CFPS 2014.

**Design:** Treatment = traditional parent (top tertile of parent-mean ideation) vs
egalitarian (bottom tertile). Outcome = child ideation index. Match covariates build up
from parent education + urban/rural + child age/sex (analysis_016) to **+ parent mean
log-income**. Bootstrap SEs (n=300).
