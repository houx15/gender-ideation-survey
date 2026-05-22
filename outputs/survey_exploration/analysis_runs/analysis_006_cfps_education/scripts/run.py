#!/usr/bin/env python3
"""
analysis_006 — CFPS gender ideology & EDUCATION (SPEC 5.4).

Time-ordering: adult educational attainment is largely COMPLETED before the
attitude is measured, so the temporally defensible direction is
education -> ideation (schooling shaping attitudes), NOT ideation -> education.
We therefore model the ideation index as the OUTCOME of years of schooling, and
test whether education's association with egalitarianism differs by gender.

Model: ideation ~ eduy + female + eduy:female + age + age^2.
Reuses tested helpers (ideation_lib, cfps_outcomes.clean_continuous, stats_helpers).
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
import stats_helpers as ST        # noqa: E402

RUN = HERE.parents[1]
WAVE = {"2014": dict(age="cfps2014_age", eduy="cfps2014eduy"),
        "2020": dict(age="age", eduy="cfps2020eduy")}
EDU_BINS = [-0.1, 0, 6, 9, 12, 16, 25]
EDU_LABELS = ["none", "primary", "lower-sec", "upper-sec", "college", "postgrad"]


def main() -> int:
    desc, miss, res = [], [], []
    for year, w in WAVE.items():
        df, _m, _norm, idx = L.load_recoded("CFPS", year, extra_cols=[w["age"], w["eduy"]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["age_c"] = (df["age"] - 40) / 10
        df["age_c2"] = df["age_c"] ** 2
        df["edu_grp"] = pd.cut(df["eduy"], EDU_BINS, labels=EDU_LABELS)

        miss.append(dict(year=year, n_index=len(df),
                         pct_eduy=round(100 * df["eduy"].notna().mean(), 1),
                         mean_eduy=round(float(df["eduy"].mean()), 2)))

        for (grp, fem), g in df.dropna(subset=["edu_grp", "female"]).groupby(
                ["edu_grp", "female"], observed=True):
            desc.append(dict(year=year, edu_group=grp,
                             gender=("female" if fem == 1 else "male"),
                             n=len(g), mean_ideation=round(float(g[idx].mean()), 4)))

        X = pd.DataFrame({"const": 1.0, "eduy": df["eduy"], "female": df["female"],
                          "eduy_x_female": df["eduy"] * df["female"],
                          "age_c": df["age_c"], "age_c2": df["age_c2"]})
        r = ST.ols(X, df[idx].to_numpy())
        for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
            res.append(dict(year=year, model="OLS ideation ~ eduy*female", n=r["n"],
                            term=term, coef=round(c, 5), se=round(se, 5), t=round(t, 2)))
        print(f"CFPS {year}: N={r['n']}, eduy coef={r['coef'][1]:+.4f}, "
              f"eduy:female={r['coef'][3]:+.4f}")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    print("Wrote analysis_006 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
