# 06 — Sample construction report

Samples that the current data can support, with the binding IDs and constraints
found in the structural audit (`tables/structural_variable_candidates.csv`) and the
linkage feasibility run (analysis_003).

## Available linking IDs
| Dataset | Person | Family | Parent / child | Spouse | Region |
|---------|--------|--------|----------------|--------|--------|
| CFPS 2014 | `pid` | `fid14` (+fid12/10) | `pid_f`, `pid_m`, child codes | `pid_s` | `provcd14` |
| CFPS 2020 | `pid` | `fid20` (+history) | `pid_a_f`, `pid_a_m`, `xchildpid_a_*` | (roster) | `provcd20` |
| CGSS (all) | (row) | — | parent **education/birth** only (a89/a90), sibling counts (d21_*) | spouse edu/birth | `s41` (2018 `provinces`) |
| ACWF | row | — | child/老年/大学生 separate databases | — | `sheng` |
| CEPS | `ids`/`stuids` | `schids`/`clsids` | student↔parent file merge | — | school region |

Implication: **individual + family-internal (couple, parent-child, sibling) designs
are a CFPS strength**; CGSS/ACWF support individual + retrospective-parent designs only;
CEPS supports student↔parent↔school merges in the education field.

## Samples supported now

### A. Adult individual sample (all surveys)
- Definition: respondents with ≥1 valid ideation item.
- N: CFPS 31.5k (2014)/22.7k (2020); CGSS ~11–13k/wave (2023 ~7k); ACWF 19–26k.
- Use: ideation distribution, gender gaps, cohort trends (analysis_001, 002).
- Limit: no weights applied yet; CGSS 2023 is a sub-module.

### B. Birth-cohort sample (CFPS, extendable to CGSS)
- Definition: A + valid birth year (1930–2004) + known gender. N≈31.4k/22.6k (CFPS).
- Use: cohort gradient & gender-gap crossover (analysis_002). Clean time-ordering.

### C. Couple sample (CFPS 2014)
- Definition: ego linked to in-sample spouse (`pid_s`>0), both with index. **N≈21,680 dyads.**
- Use: couple ideation matching, difference/distance, assortative mating (within-dyad r=0.22).
- Limit: 2020 couple link needs the roster pointer (not yet resolved).

### D. Parent-child sample (CFPS 2014 & 2020)
- Definition: ego linked to in-sample father and/or mother, both with index.
- N: 2014 — 6,316 father / 7,191 mother dyads; 2020 — 5,048 / 5,475.
- Use: transmission (mother vs father paths, same-/cross-gender); within-dyad r≈0.15–0.18.
- Limit: co-residence bias; for clean transmission restrict child age ≥16, parent same wave.

### E. Education-field sample (CEPS)
- Definition: CEPS baseline/followup students (19,487 / 10,750) merged to parent file
  (19,487) and school file via `ids`/`schids`.
- Use: adolescent education expectations, science/math orientation, family environment
  (SPEC 5.4). Note: **CEPS lacks a direct gender-attitude battery** — use it for the
  education/science outcomes, with family/region ideology brought in from elsewhere.

## Samples NOT yet supported / need more work
- Cross-survey individual matching — **prohibited** (no shared person ID; SPEC 12.5).
- Event-history (first marriage/birth timing) — variables exist (CFPS marriage/fertility,
  CGSS `a70` first-marriage year) but person-year files are not yet built.
- Province-ideology context merge — `surveys/processed/gender_ideation_by_province_year.csv`
  + `surveys/provincial/*` exist; join key (province code × year) is ready but unbuilt.

## Required reporting per sample (per SPEC 8) — to attach when each is built
sample definition · inclusion/exclusion · N at each step · key-variable missing % ·
answerable questions · limitations.
