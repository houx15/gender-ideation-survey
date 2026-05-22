# analysis_009 — Method note

## Sample
Adult children linked to both parents via `cfps_linkage.attach_parents` (tested), with
both parents' ideation index and the child's years of schooling valid.
N = 5,343 (2014) / 3,980 (2020). See `02_missing_table.csv`.

## Variables and coding
- **child_eduy**: `cfps20XXeduy`, `clean_continuous` to [0,22].
- **mother_ideation / father_ideation**: `ideation_lib` index [0,1], 1 = most traditional.
- **child_female**: 1 = daughter. **parent_mean_ideation** = mean of both parents (descriptive split).
- Controls: `age_c=(age−30)/10`, `age_c2`.

## Method
OLS (tested `stats_helpers.ols`), classical SEs, no weights. Model A: parents + child
gender. Model B: adds `mother×daughter`, `father×daughter` to test gendered allocation.

## Interpretation bounds (read these before the result)
- **Co-residence selection is severe here.** CFPS links adult children to parents largely
  when they co-reside. In China daughters typically marry out, so co-resident adult
  daughters are a *selected* (often younger/unmarried/more-educated) group — this almost
  certainly drives the positive `child_female` (daughter education advantage) and can mask
  or distort any true daughter penalty. The interaction test is therefore conservative and
  possibly biased.
- **Time-ordering:** child schooling is largely completed before the parent's attitude is
  measured; parent ideology now is at best a proxy for ideology during the child's schooling.
- No weights; modest CFPS index reliability.

## Next steps
Restrict to younger children still in/near schooling and to families observed before the
child left home; bring siblings in for within-family (one-son-one-daughter) comparison,
which differences out family-level selection (SPEC 5.5); use education *expenditure* /
*expectations* (CEPS) where measured during schooling.
