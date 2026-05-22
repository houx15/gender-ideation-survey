# analysis_005 — CFPS gender ideology & work / leadership (SPEC 5.3)

**Research question:** Is gender ideology associated with labour-force participation,
wages, and holding leadership/management posts — and do these associations differ by
gender (e.g., traditional women less likely employed)?

**Analysis type:** Individual practice (cross-sectional association), gender-moderated.

**Data / years / sample:** CFPS 2014 & 2020 adults with ≥1 valid ideation item.
Wage/management/subordinate models are restricted to the employed.

**Core variables:**
- Explanatory: gender-ideation index ([0,1], 1 = most traditional); gender (female=1);
  interaction `ideation×female`.
- Outcomes: `employed` (employ/employ2014), `log_wage` (p_wage 2014 / emp_income 2020),
  `mgmt` (admin/management post qg14), `has_sub` (direct subordinates qg17).
- Controls: age, age².

**Caveat (time order):** employment and earnings may shape attitudes as much as the
reverse; associations are not causal (SPEC 12.6).
