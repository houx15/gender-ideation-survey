# 03 · Method note — analysis_034

## Sample

Same dyad-construction as `analysis_033`: each adult respondent is
linked to mother + father (also adult respondents) via the
CFPS famconf parent pointers.

| Wave | n_adults | n_full_dyads | n_employed | Source of parent pid |
|---|---|---|---|---|
| 2014 | 31 554 | 5 565 | 22 150 | `pid_f`, `pid_m` |
| 2020 | 22 692 | 4 120 | 16 302 | `pid_a_f`, `pid_a_m` |

After listwise on controls and parent ideation, n per outcome × stratum
falls to 300–2 200 (smaller for sex-stratified + employed-only cells).

## Outcomes

| Outcome | Continuous | Employed-only | Variable | Available |
|---|---|---|---|---|
| `currently_married` | binary | no | `qea0 == 2` | both waves |
| `housework_hours`   | yes | no | `qq9010` / `qq9010n` | both |
| `marriage_sat`      | yes (1–5) | no | `qm801` | both |
| `ideal_children`    | yes | no | `qm501` | 2014 only |
| `employed`          | binary | no | `employ` / `employ2014` | both |
| `log_wage_year`     | yes | yes | log1p(`p_wage`/`emp_income`) | both |
| `mgmt`              | binary | yes | `qg14` | both |
| `isei`              | yes | yes | `qg303code_isei` | 2020 only |
| `edu_yrs`           | yes | no | imputed years | both |

## Methods

For each outcome × wave:
```
outcome ~ mother_ideation + father_ideation + child_female
        + mother_id × child_female + father_id × child_female
        + age_c + age_c2 + urban
        + parent_avg_age + parent_avg_edu + parent_log_income
```

OLS-HC1 robust SEs. The two interactions are the formal gender-
moderation tests. Sex-stratified fits (overall / male child / female
child) also reported.

For employed-only outcomes (wage, mgmt, isei): condition on
`child_employed == 1` before the fit.

## Controls

`age_c = (child_age − 35) / 10`, `age_c²`, `child_urban`,
`parent_avg_age` (mean of mother and father), `parent_avg_edu`,
`parent_log_income`.

## Caveats

* **Cross-sectional**: parent ideology now, child outcomes now. The
  ideology-shapes-trajectory reading is consistent with the cross-
  section direction but not causally identified.
* **Selection on intact dyads**: only families where both parents
  are adult CFPS respondents enter. Single-parent and absent-parent
  child outcomes underrepresented.
* **Multiple-comparisons risk**: 9 outcomes × 2 waves × 3 strata × 2
  parents = 108 ideation-coefficient cells. Many will be significant
  by chance. Treat individual marginal cells with care; the
  collected pattern across cells is what's informative.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` — outcome means by parent tertile × child sex
* `02_missing_table.csv` — per-wave dyad counts
* `04_result_table.csv` — tidy OLS-HC1 across all outcomes / waves / strata
* `figures/summary_forest_parent_to_child.pdf` — all sex-stratified
  parent-ideation coefficients on one chart
* `figures/forest_{outcome}.pdf` — per-outcome focused forest
