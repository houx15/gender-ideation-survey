#!/usr/bin/env python3
"""
analysis_014 — Gender gap in resources via PSM (CEPS, SPEC 5.5).

Robustifies the regression gender gaps of analysis_011 by matching daughters to sons
on observables (family SES, parents' education, grade, sibling structure) and estimating
the ATT of being a daughter on each resource outcome, with p-values. CEPS samples ~one
child per family, so within-family designs do not apply here — PSM is the right tool.

Outcomes: parent college expectation, tutoring, log tutoring cost, own desk,
near-daily homework help, weekly housework hours.

Uses tested helpers: ceps_outcomes, matching.psm_att.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ceps_outcomes as E         # noqa: E402
import matching as MM             # noqa: E402

RUN = HERE.parents[1]
ROOT = HERE.parents[5]
STU = ROOT / "surveys/CEPS13-14/CEPS基线调查学生数据.dta"
PAR = ROOT / "surveys/CEPS13-14/CEPS基线调查家长数据.dta"


def clean(s, lo, hi):
    return pd.to_numeric(s, errors="coerce").where(lambda x: x.between(lo, hi))


def main() -> int:
    stu, _ = pyreadstat.read_dta(str(STU), usecols=[
        "ids", "a01", "b01", "b0201", "b0202", "b0203", "b0204",
        "b11", "b2201", "b15g1", "b15g2", "b16g1", "b16g2",
        "steco_3c", "stmedu", "stfedu", "grade9"])
    par, _ = pyreadstat.read_dta(str(PAR), usecols=["ids", "ba18", "ba02", "ba03"])
    df = stu.merge(par, on="ids", how="inner")

    df["female"] = E.female(df["a01"])
    df["parent_expect_college"] = E.expect_college_plus(df["ba18"])
    df["tutoring"] = E.yes12(df["ba02"])
    df["log_tutor_cost"] = np.log1p(clean(df["ba03"], 0, 1e6).astype("float64"))
    df["own_desk"] = E.yes12(df["b11"])
    hwk = clean(df["b2201"], 1, 4)
    df["hw_help_daily"] = (hwk == 4).astype("float").where(hwk.notna())
    df["chore_hours_week"] = 5 * E.hours_hm(df["b15g1"], df["b15g2"]) + 2 * E.hours_hm(df["b16g1"], df["b16g2"])

    # match covariates
    df["ses"] = clean(df["steco_3c"], 1, 3)
    df["medu"] = clean(df["stmedu"], 1, 9)
    df["fedu"] = clean(df["stfedu"], 1, 9)
    df["grade9"] = clean(df["grade9"], 0, 1)
    df["n_sib"] = (clean(df["b0201"], 0, 20).fillna(0) + clean(df["b0202"], 0, 20).fillna(0)
                   + clean(df["b0203"], 0, 20).fillna(0) + clean(df["b0204"], 0, 20).fillna(0))
    covars = ["ses", "medu", "fedu", "grade9", "n_sib"]

    OUT = ["parent_expect_college", "tutoring", "log_tutor_cost", "own_desk",
           "hw_help_daily", "chore_hours_week"]
    rows = []
    for o in OUT:
        d = df[["female", o] + covars].dropna().copy()
        d["treat"] = d["female"]
        # naive (unmatched) difference for comparison
        naive = d.loc[d.treat == 1, o].mean() - d.loc[d.treat == 0, o].mean()
        a = MM.psm_att(d, "treat", o, covars)
        rows.append(dict(outcome=o, n_treated=a["n_treated"], n_control=a["n_control"],
                         naive_girl_minus_boy=round(float(naive), 4),
                         psm_att=round(a["att"], 4), se=round(a["se"], 4),
                         t=round(a["t"], 2), p=round(a["p"], 4),
                         sig=("yes" if a["p"] < 0.05 else "no")))
        print(f"  {o:24s} naive={naive:+.3f}  PSM ATT={a['att']:+.4f}  p={a['p']:.4f}")
    pd.DataFrame(rows).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note="PSM ATT of being a daughter on each resource; matched on "
                            "SES, parents' education, grade, number of siblings. "
                            "Positive = girls get more; for chores positive = girls do more.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print()
    print(pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
