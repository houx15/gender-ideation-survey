# 00 · Research question — analysis_029

## SPEC anchor

RQ 5.2 family-level (couple analysis): **dyadic effects of gender ideation
on marital matching and within-couple division of labour**.

The user-defined scope, with the new "does ideation drive assortative mating"
question added (2026-05-23):

| Part | Question |
|---|---|
| **A. Assortative mating on ideation** | (1) How correlated are husband's and wife's gender ideation? (2) Conditional on age / cohort / education / urban, *does ideation predict the partner's ideation* — i.e. is there ideology-based assortment? |
| **B. Whose ideology drives the division** | Dyadic OLS on wife's housework / childcare time as a function of **wife's ideation + husband's ideation**, with both spouses' covariates. Same for husband. Tests which spouse's belief drives the division. |
| **C. Marriage satisfaction by gap / typology** | Predict wife's (and husband's) marriage satisfaction by ideation gap `|wife_ideation − husband_ideation|` and by couple typology (concordant-traditional / concordant-progressive / woman-more-progressive / man-more-progressive). |

Couple pairs built from CFPS spouse-pid pointers:

| Wave | Spouse pid var | Source |
|---|---|---|
| 2014 | `pid_s` | `cfps2014_adult.dta` (also in `cfps2014_famconf.dta`) |
| 2020 | `pid_a_s` | `cfps2020_famconf.dta` joined onto `cfps2020_adult.dta` |

Only different-sex couples retained (CFPS gender pointer is binary; same-sex pairs drop out of `build_couples`).

## Methods

### A. Assortative mating

* **Within-couple Pearson r** of ideation, overall and by cohort decade,
  urban / rural, education level.
* **OLS-HC1 of wife_ideation ~ husband_ideation + controls** (and the
  reverse). The slope is the "ideology-based sorting" coefficient; if
  it's positive and significant *after* controlling for the observable
  matching channels (age, education, urban, region), then there is
  residual ideology-based sorting.

### B. Whose ideology drives the division

* **Dyadic OLS** of `wife_housework_hours` (and `husband_housework_hours`)
  on **wife_ideation + husband_ideation + (covariates)**. Standard
  errors with HC1.
* Same for childcare (qq9013, 2020 only).
* Comparing the wife-ideation vs husband-ideation coefficients
  tells us whose belief is more "translating" into the division.

### C. Marriage satisfaction

* **OLS-HC1** of `wife_qm801` and `husband_qm801` on:
  - `gap = |wife_ideation − husband_ideation|`
  - the four couple typologies (concordant-traditional / concordant-
    progressive / woman-more-progressive / man-more-progressive),
    using concordant-progressive as the reference.
* Standard controls.

## Frames

* `2014`: full CFPS 2014 couples
* `2020`: full CFPS 2020 couples (spouse pid joined from `famconf`)

No lagged frame here — couples ARE the object of analysis, and the
panel of *couples* (same dyad surveyed in both waves) is too small for
within-couple change models. Cross-section is the standard couples
design in the literature.

## Controls

For each spouse: `age_c = (age − 40) / 10`, `age_c2`, `edu_yrs`,
`urban` (couple-level: 1 if either spouse has urban hukou),
`log_income`. Couple-level `cohort` (= wife's birth decade).

## Caveats

* **Cross-sectional**: who-married-whom and current-ideology measured
  together. We do not know if matching was on ideology *at marriage*
  or whether shared marriage has reshaped ideology jointly. Both are
  plausible mechanisms.
* **Survivorship**: only intact, mutually-respondent couples enter the
  sample. Divorces selectively exit. This is a "currently married"
  population.
* **Spouse-pid coverage**: not all married adults have the spouse in
  the sample. The couples sample is ~30 % of "ever married"
  respondents per wave.
