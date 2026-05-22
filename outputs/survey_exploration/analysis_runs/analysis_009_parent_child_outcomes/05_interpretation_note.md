# analysis_009 — Interpretation note

> **Update:** the gender read below is revised by **analysis_010**, which matches
> household structure (within-family one-son-one-daughter design) and restricts to
> completed-schooling ages. There, the apparent daughter-education pattern is shown to
> be **co-residence selection**, and parent ideology does **not** significantly tilt the
> within-family gap toward sons. The "less-educated children of both genders" finding
> stands; the gender-specific read does not. Prefer analysis_010 for the investment question.

## What the results say (RQ 5.5 / 5.6)
From `04_result_table.csv` / `01_descriptive_table.csv` (5,343 / 3,980 children).

1. **Traditional parents have less-educated children — of both genders.**
   `child_eduy` falls with parental traditionalism: father −1.89, mother −0.81 (2014);
   father −2.27, mother −2.07 (2020); all significant. In 2014 the **father's** ideology
   is the stronger predictor of child schooling; by 2020 mother and father are comparable.
2. **No significant evidence of a daughter-specific penalty.** The gendered-allocation
   interactions `mother×daughter` / `father×daughter` are not significant in either wave
   (|t| ≤ 1.1). Across parent-ideation tertiles, the daughter–son schooling gap is roughly
   constant (descriptive table) — traditional parents lower schooling similarly for both.
3. **A daughter education *advantage* appears (child_female +0.8)** — but this is most
   likely a **co-residence selection artifact**: co-resident adult daughters are a select
   group (daughters usually marry out). It should not be read as girls being favoured.

## How this bears on "whose ideology / who is affected"
- Parental gender ideology clearly **reproduces across generations through child education**,
  not just through transmitted attitudes (analysis_008).
- We do **not** find that the daughter penalty operates through *this* linked sample's
  schooling — but co-residence selection makes this the weakest test in the set; the
  within-family sibling design is the right way to settle it.

## Threats / caveats
- Co-residence selection (esp. daughters) — the central caveat.
- Time-ordering (schooling completed before attitude measured).
- No weights; classical SEs; CFPS index reliability modest.

## Next steps
One-son-one-daughter within-family comparison (differences out family selection);
restrict to younger/in-school children; CEPS for education expenditure & expectations
measured during schooling (SPEC 5.4/5.5).
