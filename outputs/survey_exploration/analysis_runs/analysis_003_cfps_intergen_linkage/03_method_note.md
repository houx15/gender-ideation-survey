# analysis_003 — Method note

## Sample / linkage logic
1. Compute the ideation index for every respondent (analysis_001 recoding).
2. Build a lookup `pid → index` over respondents with ≥1 valid item.
3. For each ego, read the relative's in-sample person-ID. CFPS codes
   not-applicable links as ≤0, so a **valid link = a positive ID**. (We additionally
   require that ID to resolve to a respondent who has an index, which is the binding
   constraint for dyad counts.)
4. A dyad enters the correlation only if BOTH ego and alter have a valid index.

## Variables
- `pid` person-ID; `pid_s` spouse (2014 only in adult file), `pid_f`/`pid_a_f` father,
  `pid_m`/`pid_a_m` mother.
- Index = [0,1], 1 = most traditional.

## Method
Counts at each attrition step (`02_missing_table.csv`) plus the raw Pearson
correlation of ego vs alter index within each dyad type (reported only when n ≥ 30).
This is descriptive feasibility, not a transmission model.

## Interpretation bounds
- A positive within-dyad correlation is consistent with transmission/assortative
  mating but also with shared environment and reverse influence; it is NOT a causal
  transmission estimate.
- Spouse link `pid_s` was present in the 2014 adult file but not resolved the same way
  in 2020 here (couple linkage in 2020 needs the family roster / a different pointer —
  flagged as a next step, not a null result).
- Linkage is within-wave and within the adult file; co-resident bias is possible
  (linked relatives are disproportionately co-resident).

## Alternatives / next steps
- Use the CFPS family roster + cross-year IDs (`fid*`) to recover more couple and
  parent-child links, including non-co-resident kin.
- Restrict child to age ≥ 16 and parent to the measured wave for a clean transmission
  sample; estimate mother vs father paths and same-/cross-gender transmission (SPEC 5.7).
- Build couple difference / absolute-distance / combination-type measures (SPEC 5.2).
