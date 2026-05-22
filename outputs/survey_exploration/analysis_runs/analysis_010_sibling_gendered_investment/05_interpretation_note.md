# analysis_010 — Interpretation note

## What the results say
From `04_result_table.csv` / `01_descriptive_table.csv` / `household_structure.csv`.

1. **The naive "daughter advantage" was a selection artifact.** In the naive model the
   `child_female` coefficient *grows* when restricted to age ≥ 25 (2014: +1.0 → **+2.7**;
   2020: +0.5 → +1.7). That is the signature of **co-residence selection** — adult daughters
   who remain linked to parents are a select (more-educated, often unmarried) group. It is
   not evidence that girls are favoured.
2. **Within the family, the daughter–son education gap is roughly flat / slightly
   daughter-favouring** (mean daughter−son = +0.48 to +0.65 years), and **parent ideology
   does not significantly tilt it toward sons**: the `parent_mean_ideology` coefficient on
   the gap is −2.71 (t=−1.6) in 2014 all-ages — the only suggestive case — and is
   non-significant and unstable elsewhere (+0.44, −0.17, −0.47; all |t|<0.3) and in the
   ≥25 subsets.
3. **So there is no robust evidence of gendered *educational* investment** in this CFPS
   linked sample once household structure is matched and life stage is handled.

## How this revises analysis_009
analysis_009's headline (traditional parents → less-educated children of both genders)
survives, but its read on gender must be corrected: the apparent daughter-education pattern
there is **driven by who stays linked to parents**, not by within-household allocation. The
within-family design is the right tool and it finds no significant son-favouring tilt.

## Honest limits
- Within-family removes family-level confounds but not selection on *which* sibling is
  observed; ≥25 sibling samples are small (107/189) and underpowered.
- Completed attainment in selected adults is the wrong frame for "investment" — that should
  be measured *during* schooling.

## Next steps
- Move the gendered-investment question to a frame that observes children **during**
  schooling: a CFPS children/roster file or **CEPS** (education expenditure, tutoring,
  parental expectations), where the life-stage and co-residence problems do not bite.
- Pool more CFPS waves to grow the one-son-one-daughter ≥25 sample.
- Apply the same household-matched logic to the transmission analysis (analysis_008):
  restrict child age and split co-resident vs not.
