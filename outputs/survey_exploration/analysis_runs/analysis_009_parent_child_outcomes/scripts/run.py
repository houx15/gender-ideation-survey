#!/usr/bin/env python3
"""
analysis_009 — Parent ideology & child OUTCOMES / gendered resource allocation
(SPEC 5.5 + 5.6).

Key question: do more traditional parents invest less in DAUGHTERS' education
relative to sons? Tested as a parent_ideation × child_female interaction on the
child's completed years of schooling.

Models (per wave), child = adult respondent linked to both parents:
  A. child_eduy ~ mother_ideation + father_ideation + child_female + age + age^2
  B. + mother_ideation:child_female + father_ideation:child_female
     -> negative interaction = traditional parents penalize daughters' schooling.

Reuses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents, stats_helpers.
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
WAVE = {
    "2014": dict(pid="pid", f="pid_f", m="pid_m", age="cfps2014_age", eduy="cfps2014eduy"),
    "2020": dict(pid="pid", f="pid_a_f", m="pid_a_m", age="age", eduy="cfps2020eduy"),
}


def add_model(res, year, name, X, y):
    r = ST.ols(X, y)
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(year=year, model=name, n=r["n"], term=term,
                        coef=round(c, 4), se=round(se, 4), t=round(t, 2)))
    return r


def main() -> int:
    desc, miss, res = [], [], []
    for year, w in WAVE.items():
        df, _m, _norm, idx = L.load_recoded(
            "CFPS", year, extra_cols=[w["pid"], w["f"], w["m"], w["age"], w["eduy"]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["parent_link_idx"] = df[idx]
        df = K.attach_parents(df, w["pid"], w["f"], w["m"], value_cols=["parent_link_idx"])
        df = df.rename(columns={"father_parent_link_idx": "father_ideation",
                                "mother_parent_link_idx": "mother_ideation"})
        df["child_eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["age_c"] = (df["age"] - 30) / 10
        df["age_c2"] = df["age_c"] ** 2

        both = df.dropna(subset=["child_eduy", "mother_ideation", "father_ideation",
                                 "female", "age"]).copy()
        both["parent_mean_ideation"] = both[["mother_ideation", "father_ideation"]].mean(axis=1)
        miss.append(dict(year=year, n_both_parents_index=int(
            df.dropna(subset=["mother_ideation", "father_ideation"]).shape[0]),
            n_analysis=len(both),
            pct_child_eduy=round(100 * df.dropna(subset=["mother_ideation", "father_ideation"])
                                 ["child_eduy"].notna().mean(), 1)))

        # descriptive: child eduy by parent-ideation tertile x child gender
        q = both["parent_mean_ideation"].quantile([1 / 3, 2 / 3]).values
        both["pidx_t"] = pd.cut(both["parent_mean_ideation"],
                                [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])
        for (t, fem), g in both.dropna(subset=["pidx_t"]).groupby(["pidx_t", "female"], observed=True):
            desc.append(dict(year=year, parent_ideation_tertile=t,
                             child=("daughter" if fem == 1 else "son"), n=len(g),
                             mean_child_eduy=round(float(g["child_eduy"].mean()), 2)))

        XA = pd.DataFrame({"const": 1.0, "mother_ideation": both["mother_ideation"],
                           "father_ideation": both["father_ideation"],
                           "child_female": both["female"],
                           "age_c": both["age_c"], "age_c2": both["age_c2"]})
        add_model(res, year, "A: child_eduy ~ parents", XA, both["child_eduy"].to_numpy())

        XB = pd.DataFrame({"const": 1.0, "mother_ideation": both["mother_ideation"],
                           "father_ideation": both["father_ideation"],
                           "child_female": both["female"],
                           "mother_x_daughter": both["mother_ideation"] * both["female"],
                           "father_x_daughter": both["father_ideation"] * both["female"],
                           "age_c": both["age_c"], "age_c2": both["age_c2"]})
        rB = add_model(res, year, "B: + gendered allocation", XB, both["child_eduy"].to_numpy())
        mxd = rB["coef"][rB["term"].index("mother_x_daughter")]
        fxd = rB["coef"][rB["term"].index("father_x_daughter")]
        print(f"CFPS {year}: N={len(both)} | mother_x_daughter={mxd:+.3f} "
              f"father_x_daughter={fxd:+.3f} (neg = daughters penalized)")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    print("Wrote analysis_009 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
