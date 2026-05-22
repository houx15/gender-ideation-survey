#!/usr/bin/env python3
"""
verify_coding.py — audit that variable coding handles missing codes and categoricals
correctly across the analyses. Prints raw value distributions (so special codes like
-1/-2/-8/78/79/98/99 are visible) and checks that each coded version only keeps the
documented valid raw values (no missing-code leakage).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cfps_outcomes as C
import ceps_outcomes as E


def show(name, raw, coded, valid):
    """Print raw vs coded and assert no missing code is coded non-NaN.

    `valid` is either a set of allowed discrete codes, or a (lo, hi) tuple for a
    continuous variable (any value in [lo, hi] is legitimate, e.g. half-hours).
    """
    kept = raw[coded.notna()]
    if isinstance(valid, tuple):
        lo, hi = valid
        leaked = sorted(v for v in kept.unique() if not (lo <= v <= hi))
    else:
        leaked = sorted(set(kept.unique()) - set(valid))
    status = "OK" if not leaked else f"!! LEAK: {leaked}"
    rawvals = dict(sorted(raw.value_counts(dropna=False).head(14).items(),
                          key=lambda kv: (pd.isna(kv[0]), kv[0] if not pd.isna(kv[0]) else 0)))
    print(f"\n[{name}] {status}")
    print(f"  raw values (top): {rawvals}")
    print(f"  coded non-NaN n={int(coded.notna().sum())}, "
          f"coded values kept from raw: {sorted(set(kept.unique()))}")
    return not leaked


def main() -> int:
    ok = True
    # ---- CFPS 2014 ----
    df, _ = pyreadstat.read_dta(str(ROOT / "surveys/CFPS/cfps2014_adult.dta"),
                                usecols=["qm1101", "qea0", "employ2014", "qg14",
                                         "cfps2014eduy", "qq9010", "cfps2014_age"])
    print("=" * 70, "\nCFPS 2014")
    ok &= show("qm1101 (Likert 1-5)", df["qm1101"],
               df["qm1101"].where(df["qm1101"].between(1, 5)), [1, 2, 3, 4, 5])
    ok &= show("qea0 -> currently_married", df["qea0"], C.currently_married(df["qea0"]),
               [1, 2, 3, 4, 5])
    ok &= show("employ2014 -> employed", df["employ2014"], C.employed(df["employ2014"]),
               [0, 1, 2, 3, 9])
    ok &= show("qg14 -> yes_no (mgmt)", df["qg14"], C.yes_no(df["qg14"]), [0, 1, 5])
    ok &= show("cfps2014eduy -> clean[0,22] (continuous)", df["cfps2014eduy"],
               C.clean_continuous(df["cfps2014eduy"], 0, 22), (0, 22))
    ok &= show("qq9010 -> housework[0,24] (continuous, half-hours valid)", df["qq9010"],
               C.clean_continuous(df["qq9010"], 0, 24), (0, 24))

    # ---- CEPS ----
    stu, _ = pyreadstat.read_dta(str(ROOT / "surveys/CEPS13-14/CEPS基线调查学生数据.dta"),
                                 usecols=["a01", "b11", "b2201", "steco_3c", "stmedu"])
    par, _ = pyreadstat.read_dta(str(ROOT / "surveys/CEPS13-14/CEPS基线调查家长数据.dta"),
                                 usecols=["ba18", "ba02"])
    print("\n" + "=" * 70, "\nCEPS")
    ok &= show("a01 -> female", stu["a01"], E.female(stu["a01"]), [1, 2])
    ok &= show("ba18 -> expect_college_plus (10=无所谓 must drop)", par["ba18"],
               E.expect_college_plus(par["ba18"]), [1, 2, 3, 4, 5, 6, 7, 8, 9])
    ok &= show("ba02 -> yes12 (tutoring)", par["ba02"], E.yes12(par["ba02"]), [1, 2])
    ok &= show("b2201 -> hw_help (valid 1-4)", stu["b2201"],
               C.clean_continuous(stu["b2201"], 1, 4), [1, 2, 3, 4])

    # ---- categorical-as-continuous audit ----
    print("\n" + "=" * 70, "\nCATEGORICAL / ORDINAL HANDLING AUDIT")
    print("""
  Variables used as CONTINUOUS regressors and why it is defensible:
    - ideation index [0,1]     : mean of Likert items (ordinal->continuous; documented, standard)
    - eduy, age, income(log)   : genuinely continuous
    - housework/chore hours    : continuous
  Binary (0/1) - fine in OLS/LPM:
    - female, employed, currently_married, ever_married, tutoring, own_desk,
      mgmt(qg14), expect_college_plus, hw_help_daily, has_brother, only_child, grade9
  NOMINAL categoricals - NEVER entered as continuous (used only for grouping/aggregation):
    - province (s41/provcd/'provinces'), occupation/sector (NOT used at all)
  ORDINAL used as linear CONTROLS (approximation, flagged) -> robustness re-checked below:
    - steco_3c (SES 1-3), stmedu/stfedu (parent education 1-9)
""")

    # robustness: CEPS gender gap with SES/parent-edu as DUMMIES vs linear
    import stats_helpers as ST
    df2 = stu.copy()
    df2["female"] = E.female(df2["a01"])
    df2["own_desk"] = E.yes12(df2["b11"])
    df2["ses"] = C.clean_continuous(df2["steco_3c"], 1, 3)
    df2["medu"] = C.clean_continuous(df2["stmedu"], 1, 9)
    d = df2.dropna(subset=["female", "own_desk", "ses", "medu"]).copy()
    lin = ST.ols(pd.DataFrame({"const": 1.0, "female": d["female"],
                               "ses": d["ses"], "medu": d["medu"]}), d["own_desk"].to_numpy())
    Xd = {"const": 1.0, "female": d["female"]}
    for v in (2, 3):
        Xd[f"ses_{v}"] = (d["ses"] == v).astype(float)
    for v in range(2, 10):
        Xd[f"medu_{v}"] = (d["medu"] == v).astype(float)
    dum = ST.ols(pd.DataFrame(Xd), d["own_desk"].to_numpy())
    fl = lin["coef"][lin["term"].index("female")]
    fd = dum["coef"][dum["term"].index("female")]
    print(f"  own_desk female coef: linear SES/edu = {fl:+.4f} (p={lin['p'][lin['term'].index('female')]:.4f}); "
          f"dummies = {fd:+.4f} (p={dum['p'][dum['term'].index('female')]:.4f})")
    print(f"  -> female coefficient stable across ordinal-linear vs dummy specs: "
          f"{'YES' if abs(fl - fd) < 0.01 else 'check'}")

    print("\n" + ("ALL MISSING-CODE CHECKS PASSED" if ok else "SOME CHECKS LEAKED — SEE ABOVE"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
