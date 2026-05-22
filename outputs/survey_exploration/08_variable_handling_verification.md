# 08 — Variable handling verification

Run `scripts/verify_coding.py` to reproduce. It prints raw value distributions (so
special/missing codes are visible) and checks that every coded variable keeps only its
documented valid raw values. **All missing-code checks pass.**

## 1. Missing codes are excluded (no leakage)
The coding uses either a valid-range filter (`clean_continuous`/`.between`) or an explicit
valid-code set, so negative codes (−1 不知道, −2 拒答, −8 不适用, −10 无法判断) and special
codes (78/79 不适用, 98/99) all map to NaN. Verified examples:

| Variable | Raw special codes present | Coded keeps | Result |
|----------|---------------------------|-------------|--------|
| CFPS `qm1101` (Likert) | −2, −1 | 1–5 | OK |
| CFPS `qea0` → currently_married | −1 | 1–5 only | OK |
| CFPS `employ2014` → employed | −8 | 0,1,3 | OK |
| CFPS `qg14` → mgmt | −8 (24,165!), −1 | 0,1 | OK |
| CEPS `ba18` → expect_college_plus | **10 = 无所谓** | 1–9 (10 dropped) | OK |
| CEPS `ba02`/`b11` → yes12 | — | 1,2 | OK |

The `10 = 无所谓` ("doesn't matter") code on the education-expectation item is correctly
treated as missing, **not** as the top of the scale — the specific trap SPEC §12 warns about.

## 2. Continuous variables: fractional values are legitimate
`qq9010` housework hours contains half-hours (0.5, 1.5, 2.5 …). These are valid and
correctly retained by `clean_continuous(0, 24)`; they are not missing codes. (An earlier
integer-only check flagged them as a false positive; the checker now range-validates
continuous variables.)

## 3. Categorical / ordinal handling
- **Nominal categoricals are NEVER entered as continuous regressors.** Province
  (`s41`/`provcd`/`provinces`) is used only for grouping/aggregation; occupation/industry/
  sector codes were not used at all (flagged as needing proper categorical coding before use).
- **Binary (0/1)** variables (female, employed, currently/ever married, tutoring, own_desk,
  mgmt, expect_college_plus, hw_help_daily, has_brother, only_child, grade9) are valid in
  OLS/LPM.
- **Ordinal used as linear controls** — `steco_3c` (SES 1–3) and `stmedu`/`stfedu` (parent
  education 1–9) — is an approximation. Robustness check: the CEPS `own_desk` female
  coefficient is **stable** whether SES/parent-education enter linearly (+0.0137) or as full
  dummies (+0.0100); conclusions do not depend on the linear-ordinal approximation. Likert
  ideation items are averaged into the [0,1] index (ordinal→continuous), per the established
  methodology.

## Bottom line
Missing/special codes are handled correctly everywhere checked; no nominal categorical is
misused as continuous; the only ordinal-as-linear approximations (SES, parent education) are
controls and are robustness-confirmed.
