#!/usr/bin/env python3
"""
analysis_022 — Age at first marriage & gender ideology (CGSS, SPEC 5.2 timing).

The "first marriage / first birth timing" module of the readiness matrix. CGSS records
the first-marriage YEAR (a70); age at first marriage = a70 - birth_year.

CRITICAL time-ordering note: current ideation is measured at the survey, but first marriage
happened in the past (median ~1988). So this is a DESCRIPTIVE association (people who married
later tend to hold more egalitarian views NOW), not a causal ideation->timing effect, and a
proper event-history is NOT identifiable here (the attitude is measured once, post-marriage).

Model (ever-married, pooled CGSS): age_first_marriage ~ ideation + female + ideation*female
+ decade_c + wave FE.

Uses tested helpers: ideation_lib, cfps_outcomes.clean_continuous, stats_helpers.ols.
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
BIRTH = {"2010": "a3a", "2012": "a3a", "2013": "a3a", "2015": "a301",
         "2017": "a31", "2018": "a31", "2021": "A3_1", "2023": "a3a"}
MARR = {y: ("A70" if y == "2021" else "a70") for y in BIRTH}


def tertile(s):
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


def main() -> int:
    frames = []
    for year in BIRTH:
        df, _m, _n, idx = L.load_recoded("CGSS", year, extra_cols=[BIRTH[year], MARR[year]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["birthy"] = C.clean_continuous(df[BIRTH[year]], 1920, 2007)
        df["marry_y"] = C.clean_continuous(df[MARR[year]], 1940, 2023)
        df["ideation"] = df[idx]
        df["wave"] = year
        frames.append(df[["ideation", "female", "birthy", "marry_y", "wave"]])
    d = pd.concat(frames, ignore_index=True)
    d["age_marr"] = d["marry_y"] - d["birthy"]
    d = d.dropna(subset=["ideation", "female", "birthy", "age_marr"])
    d = d[d["age_marr"].between(15, 50)]                 # plausible first-marriage ages
    d["decade_c"] = (d["birthy"] - 1970) / 10

    # descriptive: mean age at first marriage by ideation tertile x gender
    d["idx_t"] = tertile(d["ideation"])
    desc = []
    for (t, fem), g in d.dropna(subset=["idx_t"]).groupby(["idx_t", "female"], observed=True):
        desc.append(dict(ideation_tertile=t, gender=("female" if fem == 1 else "male"),
                         n=len(g), mean_age_first_marriage=round(float(g["age_marr"].mean()), 2)))
    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)

    # model with wave FE
    X = {"const": 1.0, "ideation": d["ideation"], "female": d["female"],
         "ideation_x_female": d["ideation"] * d["female"], "decade_c": d["decade_c"]}
    for wv in sorted(d["wave"].unique())[1:]:
        X[f"wave_{wv}"] = (d["wave"] == wv).astype(float)
    r = ST.ols(pd.DataFrame(X), d["age_marr"].to_numpy())
    res = [dict(term=t, coef=round(c, 4), se=round(se, 4), t=round(tt, 2), p=round(p, 5))
           for t, c, se, tt, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"])
           if not t.startswith("wave_")]
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note=f"Ever-married pooled CGSS, N={r['n']}, wave FE. "
                            "DESCRIPTIVE only: ideation measured post-marriage -> not causal; "
                            "true event-history not identifiable with once-measured attitude.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print(f"Ever-married pooled CGSS N={r['n']}, mean age first marriage={d['age_marr'].mean():.1f}")
    print("\nBY IDEATION TERTILE x GENDER:\n", pd.DataFrame(desc).to_string(index=False))
    print("\nMODEL (wave FE):\n", pd.DataFrame(res).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
