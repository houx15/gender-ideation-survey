#!/usr/bin/env python3
"""
analysis_011 — How do families allocate resources to daughters vs sons? (CEPS, SPEC 5.5)

CEPS observes children DURING schooling (grades 7 & 9) and their parents, so it
avoids the life-stage / co-residence problems that defeated the adult-attainment
approach (analysis_009/010). Child sex is quasi-random, so the gender gap in
parental investment is close to a causal "effect of being a daughter".

Resource outcomes (student + parent files merged on `ids`):
  Investments (expect higher for favoured child):
    - parent_expect_college   (parent ba18: expects college+; student b31 too)
    - tutoring                (parent ba02: attends paid tutoring/interest class)
    - log tutoring cost       (parent ba03, among tutored)
    - own_desk                (student b11: has own study desk)
    - hw_help_daily           (student b2201: parents check homework ~daily)
  Demands (expect higher for daughters under son-preference):
    - chore_hours_week        (student b15g/b16g: housework hours)

Models: outcome ~ female + SES controls; plus female x has_brother (son-preference test).
Uses tested helpers: ceps_outcomes, stats_helpers.
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
import stats_helpers as ST        # noqa: E402

RUN = HERE.parents[1]
ROOT = HERE.parents[5]
STU = ROOT / "surveys/CEPS13-14/CEPS基线调查学生数据.dta"
PAR = ROOT / "surveys/CEPS13-14/CEPS基线调查家长数据.dta"


def clean(s, lo, hi):
    return s.where(s.between(lo, hi))


def add_model(res, name, X, y):
    r = ST.ols(X, y)
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(model=name, n=r["n"], term=term,
                        coef=round(c, 4), se=round(se, 4), t=round(t, 2)))
    return r


def main() -> int:
    stu, _ = pyreadstat.read_dta(str(STU), usecols=[
        "ids", "a01", "b01", "b0201", "b0202", "b0203", "b0204",
        "b11", "b2201", "b15g1", "b15g2", "b16g1", "b16g2",
        "steco_3c", "stmedu", "stfedu", "grade9"])
    par, _ = pyreadstat.read_dta(str(PAR), usecols=["ids", "ba18", "ba02", "ba03"])
    df = stu.merge(par, on="ids", how="inner")

    # ---- code outcomes ----
    df["female"] = E.female(df["a01"])
    df["parent_expect_college"] = E.expect_college_plus(df["ba18"])
    df["tutoring"] = E.yes12(df["ba02"])
    df["tutoring_cost"] = clean(pd.to_numeric(df["ba03"], errors="coerce"), 0, 1e6)
    df["log_tutor_cost"] = np.log1p(df["tutoring_cost"].astype("float64"))
    df["own_desk"] = E.yes12(df["b11"])
    df["hw_help_daily"] = (clean(df["b2201"], 1, 4) == 4).astype("float").where(clean(df["b2201"], 1, 4).notna())
    wk = E.hours_hm(df["b15g1"], df["b15g2"])
    we = E.hours_hm(df["b16g1"], df["b16g2"])
    df["chore_hours_week"] = 5 * wk + 2 * we

    # ---- controls + sibling structure ----
    df["grade9"] = clean(df["grade9"], 0, 1)
    df["ses"] = clean(df["steco_3c"], 1, 3)
    df["medu"] = clean(df["stmedu"], 1, 9)
    df["fedu"] = clean(df["stfedu"], 1, 9)
    older_bro = clean(pd.to_numeric(df["b0201"], errors="coerce"), 0, 20).fillna(0)
    younger_bro = clean(pd.to_numeric(df["b0202"], errors="coerce"), 0, 20).fillna(0)
    n_bro = older_bro + younger_bro
    df["has_brother"] = (n_bro > 0).astype("float")
    df["only_child"] = E.yes12(df["b01"])

    OUT = ["parent_expect_college", "tutoring", "log_tutor_cost", "own_desk",
           "hw_help_daily", "chore_hours_week"]

    # ---- descriptive: mean by gender + gap ----
    desc, miss = [], []
    for o in OUT:
        g = df.dropna(subset=[o, "female"])
        mb = g.loc[g["female"] == 0, o].mean()
        mg = g.loc[g["female"] == 1, o].mean()
        desc.append(dict(outcome=o, n=len(g), mean_boys=round(float(mb), 4),
                         mean_girls=round(float(mg), 4),
                         girl_minus_boy=round(float(mg - mb), 4)))
        miss.append(dict(outcome=o, n_valid=len(g),
                         pct_valid=round(100 * len(g) / len(df), 1)))
    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)

    # ---- models: female + controls; then + female x has_brother ----
    res = []
    ctrl = {"grade9": df["grade9"], "ses": df["ses"], "medu": df["medu"], "fedu": df["fedu"]}
    for o in OUT:
        X = pd.DataFrame({"const": 1.0, "female": df["female"], **ctrl})
        add_model(res, f"{o} ~ female + controls", X, df[o].to_numpy())
        # son-preference: does having a brother widen the girl gap? (non-only-children)
        sub = df[df["only_child"] == 0]
        Xb = pd.DataFrame({"const": 1.0, "female": sub["female"],
                           "has_brother": sub["has_brother"],
                           "female_x_brother": sub["female"] * sub["has_brother"],
                           "grade9": sub["grade9"], "ses": sub["ses"],
                           "medu": sub["medu"], "fedu": sub["fedu"]})
        add_model(res, f"{o} ~ female*has_brother (non-only)", Xb, sub[o].to_numpy())
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)

    print(pd.DataFrame(desc).to_string(index=False))
    print(f"\nN merged = {len(df)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
