# analysis_015 — Interpretation note

## (a) Correlations — transmission is real and significant
`01_descriptive_table.csv` (all p < 0.001):

| Pair | 2014 r | 2020 r |
|------|-------:|-------:|
| parent-mean → child | **0.197** | **0.191** |
| mother → child | 0.142 | 0.147 |
| father → child | 0.165 | 0.149 |
| mother → daughter | 0.154 | 0.152 |
| mother → son | 0.120 | 0.127 |
| father → daughter | 0.149 | 0.147 |
| father → son | 0.163 | 0.128 |

Children's gender ideology is robustly correlated with their parents' (combined parents
r ≈ 0.19–0.20). Same-gender transmission is *slightly* stronger (mother→daughter > mother→son
in both waves), but the differences are small — consistent with analysis_008, where the
gender-interaction terms were not significant.

## (b) PSM — survives matching on parent education
`04_result_table.csv`: effect of having a **traditional** vs **egalitarian** parent on the
child's ideation index (matched on parent education, child age & sex):

| Wave | naive diff | PSM ATT | p |
|------|-----------:|--------:|---|
| 2014 | 0.076 | **+0.0625** | ≪0.001 |
| 2020 | 0.075 | **+0.0409** | ≪0.001 |

The raw gap attenuates after matching (esp. in 2020), so **part of the apparent transmission
runs through parental education** — but a **significant transmission effect remains** net of
it: children of traditional parents are ~0.04–0.06 more traditional (on the 0–1 index) than
comparable children of egalitarian parents.

## Bottom line
Gender-ideology "regeneration" is confirmed: parent and child ideology are significantly
correlated (r ≈ 0.2), and the link is robust to matching on parent education and child
demographics. Both parents transmit, roughly equally, with only a faint same-gender tilt.

## Caveats
Transmission net of parent education ≠ clean causal effect (shared environment, genes,
co-residence selection remain); PSM-with-replacement p-values are optimistic; tertile
dichotomisation. See method note.

## Next steps
Region/SES in the match; family fixed effects; bootstrap SEs; restrict to the 16–30
formative window; link community/provincial ideology climate (SPEC 5.7 环境变量).
