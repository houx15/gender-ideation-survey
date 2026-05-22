# 07 — Analysis readiness report

Per-module feasibility after the inventory, ideation audit, structural audit, and
**nine analysis runs** (analysis_001–009). Evidence lives in `00`–`06`, `tables/`,
and `analysis_runs/`. CFPS section-5 questions (5.1–5.7) are now answered; the
findings are summarised at the end of this file.

## Feasibility matrix (SPEC 10)

| Module | Feasible | Data | Key variables | N | Main limitation | Next step |
|--------|----------|------|---------------|---|-----------------|-----------|
| **Gender-ideation measurement** | **yes** | ACWF, CFPS, CGSS | core battery → [0,1] index | 7k–40k/wave | CFPS α low (0.37/0.51); cross-survey levels not comparable | factor/IRT; sub-scales |
| **Individual practice — cohort/gender** | **yes** | CFPS (CGSS extendable) | index, birth year, gender | 31k/23k | 2 waves → no APC separation; no weights | replicate in CGSS; add weights |
| **Couple ideation matching** | **yes** | CFPS 2014 | `pid_s`, both indices | 21.7k dyads | 2020 spouse link unresolved; co-residence | difference/distance/типology; 2020 roster |
| **First marriage / first birth timing** | **partial** | CFPS, CGSS | marriage status, `a70` 1st-marriage yr, fertility | large | person-year files not built; timing vs attitude ordering | build event-history structure |
| **Work / leadership outcomes** | **yes (done, CFPS)** | CFPS, CGSS | employment, income, mgmt qg14 | 22k/16k employed | occupation/sector still uncoded; 2014 wage scale | analysis_005; code occupation/sector next |
| **Education / science outcomes** | **yes (done, CFPS)** | CFPS, CGSS, **CEPS** | eduy; expectation/science (CEPS) | 30k/21k | adult edu precedes attitude (ordering); CEPS no ideology battery | analysis_006; CEPS for youth science |
| **Parent → child transmission** | **yes (done)** | CFPS 2014/2020 | `pid_f`/`pid_m`, both indices | 5.6k/4.1k both-parent | co-residence bias; not causal | analysis_008; formal mother=father test |
| **Parent ideology → child outcomes** | **yes (done)** | CFPS 2014/2020 | parent indices, child eduy | 5.3k/4.0k | co-residence selection (esp. daughters) | analysis_009; sibling within-family design |
| **Sibling comparison** | **partial** | CFPS | `fid*`, within-family child set, sibling structure | TBD | sibling roster not yet assembled | build multi-child family sample |
| **Family fixed effects** | **partial** | CFPS | `fid*`, ≥2 members with index | TBD | needs ≥2 measured kin per family | assemble family-clustered file |
| **Region/ideology context** | **partial** | processed + provincial | province×year ideology, GDP/edu/emp | 31 prov | join not built; some CSVs GBK-encoded | merge on province×year |
| **CGSS 2011 / cross-survey person match** | **no** | — | — | — | no module / no shared ID (SPEC 12.5) | do not attempt |

## What a user can see now (SPEC 13)
1. **Inventory** — `00_data_inventory.csv` (49 data files) + `01_codebook_inventory.csv`
   (39 docs): every dataset, year, rows×cols, label availability.
2. **Which ideation items exist** — `tables/ideation_item_discovery.csv` (532 candidates)
   and the curated core battery in `02_variable_candidates.csv`.
3. **Labels / values / direction / missing per item** — `03_value_label_audit.csv`,
   `04_missing_value_report.csv`, `05_measurement_decisions.md`.
4. **Individual-practice support** — analysis_001 (measurement), analysis_002 (cohort/gender).
5. **Couple / parent-child / sibling / FE support** — analysis_003 + `06_sample_construction_report.md`.
6. **Descriptive table + method note for every run** — in each `analysis_runs/*` folder.
7. **What's feasible vs supplementary vs unsupported** — this matrix.

## Headline empirical findings so far
- Recoded index **reproduces the existing processed reference exactly** (validation).
- **Women less traditional than men in 12/13 survey-years**; CGSS gender gap widens over time.
- **Cohort gradient + crossover (CFPS):** older cohorts → women slightly more traditional;
  1980s+ cohorts → women markedly less traditional (1990–2004: F−M = −0.11 in 2020).
- **Intergenerational analyses are viable in CFPS:** 21.7k couple, 6–7k parent-child dyads,
  positive within-dyad ideology correlations (0.15–0.22).

## What the user should supply next to deepen the work
1. CFPS family **roster / child pointers** documentation to maximise couple (2020) and
   sibling links.
2. Confirmation of preferred **survey weights** per dataset (candidates catalogued).
3. Codebooks for **occupation/industry/sector** coding (CFPS/CGSS) to build work/leadership
   and STEM-proxy variables.
4. Decision on **index vs single-item** reporting per RQ (esp. CFPS).
5. **CFPS children's questionnaire** (per-child education expenditure, expectations,
   tutoring). This is the key unlock for *parent-ideology → gendered resource allocation*:
   CEPS has the resource measures but **no ideology item and no province** (county codes
   anonymized), while CFPS has parental ideology but no during-childhood resource data in
   the adult file. A survey carrying **both** is required for a conclusive 5.5 test.

## Completed analysis runs (analysis_001–009) and headline findings

All runs are reproducible (tested helpers in `scripts/`: `ideation_lib`, `cfps_outcomes`,
`cfps_linkage`, `stats_helpers`; `tests/` has 28 passing tests incl. an integration test
locking the index to `surveys/processed`). All associations are cross-sectional unless noted.

| Run | RQ | Headline |
|-----|----|----------|
| 001 measurement | 5.1 | Index reproduces processed reference exactly; CFPS α low (0.37/0.51); women less traditional than men in 12/13 survey-years |
| 002 cohort/gender | 5.1 | Younger cohorts less traditional; gender-gap crossover (1990s+ women far less traditional) |
| 003 linkage | 5.2/5.7 | 21.7k couple, 6–7k parent-child dyads with both indices → feasible |
| 004 family practice | 5.2 | Traditional → more married (+0.10–0.12), more ideal children (+0.44); traditional women do more housework, men's unchanged; couples assortative (r=0.22) |
| 005 work/leadership | 5.3 | ideation×female negative: traditional women less employed & paid less; traditional → less management |
| 006 education | 5.4 | Education → less traditional, more so for women (college/postgrad women far more egalitarian than men) |
| 007 couple "whose matters" | 5.2 | Wife's own ideology dominates HER housework (4× husband's), but men's housework sticky → wife's *share* depends ≥ as much on husband |
| 008 transmission | 5.7 | Both parents transmit ≈ equally (father slightly larger); same/cross-gender ns; daughters less traditional net of parents |
| 009 child outcomes | 5.5/5.6 | Traditional parents → less-educated children (both genders); no significant daughter-specific penalty (co-residence selection caveat) |
| 010 sibling investment | 5.5 | Within-family (one-son-one-daughter) + age≥25: naive "daughter advantage" is co-residence selection; no significant son-favouring education tilt |
| 011 CEPS resources | 5.5 | Girls get MORE educational investment overall but more chores; the girls' tutoring-spending advantage reverses when a brother is present (son preference at sibling-competition margin) |
| 012 ideology→allocation | 5.5 | Within-family, traditional parents point son-favouring (less edu, more chores for daughters) but NOT significant (underpowered); CEPS resources can't be linked to ideology |
| 013 allocation robustness (CFPS) | 5.5 | Expanded within-family + PSM + p-values: **female×parent_ideology on housework significant** (p=0.04/0.02) — traditional parents → daughters do more chores; education moderation marginal/ns; daughter education advantage concentrated in egalitarian families |
| 014 CEPS resources PSM | 5.5 | Girls' educational-investment advantage (expectations/tutoring/spend) robust to matching (p<0.0001); raw chore & desk gaps flip sign when matching on sibship size → confounded by son-biased fertility |
| 015 transmission corr+PSM | 5.7 | Parent↔child ideation r≈0.19–0.20 (p<0.001); PSM (traditional vs egalitarian parent, matched on parent education + child age/sex) ATT +0.063/+0.041, ≪0.001 → transmission robust to matching |
| 016 transmission PSM enhanced | 5.7 | Formative window 16–30 + urban/rural match + **bootstrap SEs**: ATT ≈0.04–0.07, bootstrap p<0.05 everywhere (CIs exclude 0); bootstrap SE ~2× paired-t (confirms paired-t was optimistic), but effect robust |
| 017 transmission + SES proxy | 5.7 | Adding parent income (2014; no family file, 2020 lacks income) modestly attenuates ATT 0.068→0.058 (still p≪0.001, CI excludes 0); transmission not an SES artifact as far as proxied (edu+urban+income) |
| 018 sibling ICC + family FE | 5.7 | Sibling ICC of ideology ≈0.20–0.26 (family-clustered), but parents' measured ideology explains only 6–11% of it (shared environment dominates); family-FE: daughters less traditional than own brothers (−0.044→−0.101, p<0.001, widening) |
| 019 population weights | 5.1/5.7 | CFPS weights (WLS, robust SEs): weighted mean ideation slightly lower; 2014 "women more traditional" gap → n.s. (sampling artifact); 2020 women-less-traditional & transmission unchanged → population-robust |

**Variable handling verified** (`08_variable_handling_verification.md`, `scripts/verify_coding.py`):
missing/special codes excluded everywhere; nominal categoricals never used as continuous;
ordinal SES/parent-education-as-linear controls robustness-confirmed.

### Cross-cutting theme — "does women's ideology matter more in the family?"
A woman's ideology is highly **self-consequential** (drives her own housework and labour-force
outcomes; analysis_004/005/007), and is the more **responsive** variable (moves more with
education and cohort; analysis_002/006). But for **shaping others** — the household division
(needs an egalitarian husband; 007) and children's beliefs (both parents transmit; 008) — it
is *not* uniquely powerful. The asymmetry is the finding.

### Top next steps
Survey weights + robust SEs throughout; formal coefficient-equality tests (wife=husband,
mother=father); occupation/sector coding for 5.3; within-family sibling design for 5.5;
CGSS replication of cohort/education/housework; CEPS for the adolescent education/science field.
