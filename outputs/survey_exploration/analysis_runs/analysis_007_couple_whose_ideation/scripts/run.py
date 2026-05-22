#!/usr/bin/env python3
"""
analysis_007 — Whose ideation matters more in the family? (couple-level, CFPS 2014)

Tests the hypothesis that the WIFE's gender ideology is the more consequential one
for the household division of labour. For each married couple we put BOTH spouses'
ideation in the same model predicting the housework division, and compare the
wife-ideation vs husband-ideation coefficients.

Outcomes:
  - wife_housework_hrs        ~ wife_ideation + husband_ideation + ages
  - husband_housework_hrs     ~ wife_ideation + husband_ideation + ages
  - wife_share = wife/(wife+husband) housework ~ wife_ideation + husband_ideation + ages

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.build_couples, stats_helpers.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L          # noqa: E402
import cfps_outcomes as C         # noqa: E402
import cfps_linkage as K          # noqa: E402
import stats_helpers as ST        # noqa: E402

RUN = HERE.parents[1]


def add_model(res, name, X, y):
    r = ST.ols(X, y)
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(model=name, n=r["n"], term=term,
                        coef=round(c, 4), se=round(se, 4), t=round(t, 2)))
    return r


def main() -> int:
    df, _m, _norm, idx = L.load_recoded(
        "CFPS", "2014", extra_cols=["pid", "pid_s", "qq9010", "cfps2014_age"])
    df = df[df["n_valid_items"] >= 1].copy()
    df["hw"] = C.clean_continuous(df["qq9010"], 0, 24)
    df["age"] = C.clean_continuous(df["cfps2014_age"], 16, 99)

    couples = K.build_couples(df, "pid", "pid_s", "female",
                              value_cols=[idx, "hw", "age"])
    # rename the index column produced by build_couples (wife_<idx>, husband_<idx>)
    couples = couples.rename(columns={f"wife_{idx}": "wife_ideation",
                                      f"husband_{idx}": "husband_ideation"})

    # complete cases for the division
    c = couples.dropna(subset=["wife_ideation", "husband_ideation",
                               "wife_hw", "husband_hw"]).copy()
    c = c[(c["wife_hw"] + c["husband_hw"]) > 0]
    c["wife_share"] = c["wife_hw"] / (c["wife_hw"] + c["husband_hw"])
    c["wife_age_c"] = (c["wife_age"] - 40) / 10
    c["husband_age_c"] = (c["husband_age"] - 40) / 10

    # ---- descriptive ----
    desc = [dict(
        n_couples_linked=len(couples),
        n_couples_complete=len(c),
        mean_wife_ideation=round(float(c["wife_ideation"].mean()), 4),
        mean_husband_ideation=round(float(c["husband_ideation"].mean()), 4),
        mean_wife_hw=round(float(c["wife_hw"].mean()), 2),
        mean_husband_hw=round(float(c["husband_hw"].mean()), 2),
        mean_wife_share=round(float(c["wife_share"].mean()), 3),
        corr_spouse_ideation=round(float(np.corrcoef(c["wife_ideation"], c["husband_ideation"])[0, 1]), 3),
    )]
    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame([dict(n_couples_linked=len(couples), n_complete=len(c),
                       note="complete = both ideation + both housework valid, sum>0")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)

    # ---- models ----
    res = []
    base = {"const": 1.0, "wife_ideation": c["wife_ideation"],
            "husband_ideation": c["husband_ideation"],
            "wife_age_c": c["wife_age_c"], "husband_age_c": c["husband_age_c"]}
    rw = add_model(res, "wife_housework_hrs", pd.DataFrame(base), c["wife_hw"].to_numpy())
    rh = add_model(res, "husband_housework_hrs", pd.DataFrame(base), c["husband_hw"].to_numpy())
    rs = add_model(res, "wife_share", pd.DataFrame(base), c["wife_share"].to_numpy())
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)

    # ---- the headline comparison ----
    def coef(r, term):
        return r["coef"][r["term"].index(term)]
    cmp_rows = []
    for name, r in [("wife_housework_hrs", rw), ("husband_housework_hrs", rh),
                    ("wife_share", rs)]:
        w, h = coef(r, "wife_ideation"), coef(r, "husband_ideation")
        cmp_rows.append(dict(outcome=name, wife_ideation_coef=round(w, 4),
                             husband_ideation_coef=round(h, 4),
                             ratio_wife_to_husband=(round(w / h, 2) if h else None),
                             larger=("wife" if abs(w) > abs(h) else "husband")))
    pd.DataFrame(cmp_rows).to_csv(RUN / "whose_ideation_comparison.csv", index=False)
    print(pd.DataFrame(cmp_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
