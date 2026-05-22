# analysis_013 — Parent ideology & gendered allocation: robustness ladder (CFPS, SPEC 5.5)

**Research question:** Does parental gender ideology produce son-favouring allocation —
less education / more housework for daughters — estimated with more power and proper
significance tests than the strict one-son-one-daughter design (analysis_012)?

**Three rungs (increasing sample, decreasing within-family control):**
- **Rung 1** (analysis_012): strict one-son-one-daughter difference.
- **Rung 2** (here): *all mixed-gender families* — mean(daughters) − mean(sons) gap,
  regressed on parent ideology.
- **Rung 3** (here): *all families* — PSM matching daughters to sons on (age, parent
  ideology); ATT of being a daughter, overall and stratified by parent ideology.
- **Formal moderation test** (here): OLS `outcome ~ female × parent_ideology + age`, whose
  `female×parent_ideology` coefficient + p-value is the direct test of whether ideology
  changes the gender gap.

**Data:** CFPS 2014 & 2020 children linked to both parents. Outcomes: years of schooling
(investment, age ≥ 25) and housework hours (demand). All tests report p-values.
