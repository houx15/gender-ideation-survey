# 09 — Findings summary

A synthesis across the 22 analysis runs (`analysis_runs/analysis_001`–`022`). Everything is
reproducible: tested helper modules in `scripts/` (`ideation_lib`, `cfps_outcomes`,
`ceps_outcomes`, `cfps_linkage`, `matching`, `stats_helpers`) and **54 passing tests**
(`tests/`), including an integration test locking the index to `surveys/processed`. Variable
handling is verified in `08_variable_handling_verification.md`. Unless noted, associations are
cross-sectional (not causal). Provincial ideology climate is intentionally not yet used.

---

## A. Measurement (SPEC 5.1)
- A comparable gender-ideation battery exists in **ACWF, CFPS, CGSS** (not CGSS 2011; CGSS
  2023 is a split-ballot sub-module). Our [0,1] index (1=traditional) **reproduces the
  processed reference exactly** (analysis_001). Internal consistency is modest, weakest in
  CFPS (α 0.37/0.51) — prefer single items there.
- **Secular decline + cohort crossover.** Younger cohorts are less traditional, and a
  gender-gap **crossover** emerges: older cohorts → women ≈/slightly more traditional;
  younger → women markedly less. In CFPS (analysis_002) the 1990s+ cohort F−M ≈ −0.11;
  **replicated across 8 CGSS waves** (analysis_021, N=86,318): F−M from +0.012 (1930s) to
  **−0.120 (1990s+)**, decade×female = −0.022 (t=−30.7). Robust across two survey programs.
- **Weights** (analysis_019) leave levels/trends intact but reveal the 2014 "women more
  traditional" blip was a sampling artifact (n.s. when weighted).

## B. Individual practice
- **Family (5.2, analysis_004):** more traditional → more likely currently married
  (+0.10–0.12), more ideal children (+0.44); **traditional women do much more housework,
  men's unchanged** (ideation×female +1.0–1.4 hrs). Couples are assortative (r=0.22).
- **Whose ideology drives the division? (analysis_007):** the wife's own ideology dominates
  *her own* housework (4× the husband's), but men's housework is sticky to either spouse's
  ideology, so the wife's *share* depends at least as much on the **husband's** ideology.
- **Work/leadership (5.3, analysis_005):** ideation×female is negative for employment and
  wages — **traditional women are less employed and paid less**, while men's outcomes barely
  respond; more traditional → less management.
- **Education (5.4, analysis_006):** more education → less traditional, **more so for women**
  (college/postgrad women far more egalitarian than men; uneducated men/women equal).
- **Marriage timing (analysis_022):** more traditional ⇄ younger first marriage, steeper for
  women — but **descriptive only** (attitude measured post-marriage; event-history not identifiable).

## C. Intergenerational reproduction
- **Linkage feasible in CFPS** (analysis_003): 21.7k couple, 5–7k parent-child dyads.
- **Transmission is real and robust (5.7).** Parent↔child ideation r≈0.19–0.20 (analysis_015);
  PSM of having a traditional vs egalitarian parent gives ATT ≈ 0.04–0.07, robust to richer
  matching (education, urban/rural, **income**), the 16–30 formative window, and **bootstrap**
  inference (analyses 016–017). Bootstrap SEs are ~2× the paired-t SEs (the paired-t was
  optimistic) but the effect survives (CIs exclude 0). Both parents transmit ≈ equally.
- **…but transmission is PARTIAL.** Sibling ICC of ideology ≈ 0.20–0.26 (ideology is strongly
  family-clustered), yet parents' *measured* ideology explains only **6–11%** of that sibling
  resemblance (analysis_018), and 3–16% across rural/urban/cohort subgroups (analysis_020) —
  **shared family/community environment dominates**, especially in rural families.
- **Within-family gender divergence (analysis_018).** Net of all family factors (family FE),
  daughters are less traditional than their **own brothers** (−0.044 in 2014 → **−0.101 in
  2020**) — a widening within-household divergence echoing the cohort crossover.
- **Gendered resource allocation (5.5).** In CEPS (children observed during schooling),
  daughters get **more** educational investment overall (expectations, tutoring, spending;
  robust to PSM, analysis_011/014) but **more chores**; son preference reappears at the margin
  of **sibling competition** (the girls' tutoring-spending advantage reverses when she has a
  brother). The raw chore gap is largely a **son-biased-fertility** artifact (flips when
  matching on sibship size). Linking *parental ideology* to allocation: within-family it points
  son-favouring but only the **housework (demand)** channel is significant (female×parent_ideology
  +0.67/+1.23, p<0.05, analysis_013); education investment is not significantly daughter-penalising
  (analyses 009/010/012).

---

## Cross-cutting themes
1. **Women's ideology is the more *responsive* and more *self-consequential* variable.** It
   moves more with education and cohort, and predicts women's *own* housework and labour
   outcomes — while men's behaviour barely responds to anyone's ideology.
2. **Ideology shapes the *domestic-labour* channel most clearly** — for wives (their own
   chores), and for daughters (parental traditionalism → more chores), more than the
   educational-investment channel (where girls generally do well).
3. **A widening within-cohort and within-family gender divergence**: younger women, and
   daughters vs their own brothers, are pulling away from men in gender ideology.
4. **Reproduction works mostly through shared environment, not explicit parental attitudes** —
   the measured parental index is a real but minor channel of sibling resemblance.

## Data boundaries (what is NOT answerable here)
- **CEPS cannot be linked to ideology** (no parental gender-attitude item; only anonymized
  county codes → no province climate merge). Resource allocation ↔ parental ideology can only
  be tested in CFPS, where during-childhood resources are thin.
- **No CFPS family file** in the data → no true household income (proxied by parents' personal
  income, 2014 only).
- **Event-history of marriage/fertility timing** is not identifiable (attitudes measured once,
  post-event).
- Cross-survey *levels* are not comparable (only trends/slopes/gaps).

## What would unlock more
1. **CFPS children's questionnaire** — per-child education expenditure/expectations/tutoring,
   mergeable to parent ideology: the key for a conclusive gendered-investment × ideology test.
2. **CFPS family file** — true household income for the SES controls.
3. **Provincial ideology climate** (deferred) — build province×year climate from CGSS/ACWF and
   test contextual moderation of family transmission (motivated by the rural shared-environment result).
4. **Design-based SEs** (PSU/strata), survey weights throughout, and occupation/sector coding
   for the work/leadership module.
