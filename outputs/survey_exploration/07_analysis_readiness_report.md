# 07 — Analysis readiness report

Per-module feasibility after the inventory, ideation audit, structural audit, and
three analysis runs. Evidence lives in `00`–`06`, `tables/`, and `analysis_runs/`.

## Feasibility matrix (SPEC 10)

| Module | Feasible | Data | Key variables | N | Main limitation | Next step |
|--------|----------|------|---------------|---|-----------------|-----------|
| **Gender-ideation measurement** | **yes** | ACWF, CFPS, CGSS | core battery → [0,1] index | 7k–40k/wave | CFPS α low (0.37/0.51); cross-survey levels not comparable | factor/IRT; sub-scales |
| **Individual practice — cohort/gender** | **yes** | CFPS (CGSS extendable) | index, birth year, gender | 31k/23k | 2 waves → no APC separation; no weights | replicate in CGSS; add weights |
| **Couple ideation matching** | **yes** | CFPS 2014 | `pid_s`, both indices | 21.7k dyads | 2020 spouse link unresolved; co-residence | difference/distance/типology; 2020 roster |
| **First marriage / first birth timing** | **partial** | CFPS, CGSS | marriage status, `a70` 1st-marriage yr, fertility | large | person-year files not built; timing vs attitude ordering | build event-history structure |
| **Work / leadership outcomes** | **partial** | CFPS, CGSS | employment, occupation, `领导/干部`, income | large | vars uncoded (occupation/sector are categorical); ordering | code occupation/sector; LFP & leadership models |
| **Education / science outcomes** | **partial** | CFPS, CGSS, **CEPS** | edu attainment, edu expectation, science/math (CEPS) | large | adult edu precedes attitude (ordering); CEPS has no ideology battery | CEPS for youth science; bring ideology from family/region |
| **Parent → child transmission** | **yes** | CFPS 2014/2020 | `pid_f`/`pid_m`, both indices | 5–7k dyads/parent | co-residence bias; not causal | child age≥16 + same-wave; mother vs father paths |
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
