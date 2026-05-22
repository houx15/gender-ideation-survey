# analysis_010 — Method note

## Design (the two fixes)
1. **Household matching → within-family contrast.** For one-son-one-daughter families
   (`cfps_linkage.one_son_one_daughter_diff`, tested), the daughter-minus-son education
   gap differences out *every* family-level factor — parent ideology level, SES, region,
   household structure. We then regress that gap on the family's parent ideology to ask
   whether the within-family gap tilts toward sons as parents get more traditional.
2. **Life stage.** All naive models are also run on **age ≥ 25** (schooling plausibly
   complete). The within-family design is run all-ages and with **both siblings ≥ 25**.

## Variables and coding
- child years of schooling: `cfps20XXeduy`, `clean_continuous` to [0,22].
- `mother_pi`/`father_pi`/`parent_mean`: ideation index [0,1], 1 = most traditional.
- family = `pid_f` + "_" + `pid_m`; one-son-one-daughter = exactly one female and one male child.
- Part B model: `eduy_diff (daughter−son) ~ parent_mean_ideology + age_gap`.
  Negative `parent_mean_ideology` ⇒ traditional parents favour the son.

## Method
OLS (tested `stats_helpers.ols`), classical SEs, no weights.

## Interpretation bounds — selection still matters
- The within-family design removes **family-level** confounds but **not** selection on the
  *contrast*: which sons vs daughters remain linked/co-resident may differ systematically
  (e.g. unmarried daughters stay home). So even this is not a clean causal estimate.
- The ≥25 within-family subsets are **small** (107 / 189 families) → underpowered; read as
  suggestive.
- CFPS adult-file linkage is co-residence-biased; the adult "child" is not the same as a
  child observed *during* schooling (the right frame for investment is CEPS / a children file).

## Next steps
Use a CFPS **children/roster file** (or CEPS) to observe investment *during* schooling
(expenditure, tutoring, expectations) rather than completed attainment in selected adults;
larger sibling samples via more waves; family fixed effects on enrolment for in-school kids.
