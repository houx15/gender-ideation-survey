#!/usr/bin/env python3
"""
analysis_021 — CGSS replication of the cohort × gender divergence (SPEC 5.1).

Replicates the CFPS finding (analysis_002 — younger cohorts less traditional, and a
gender-gap crossover where younger women diverge from younger men) across CGSS's EIGHT
waves (2010-2023), giving far more temporal/cohort power than CFPS's two waves.

Pooled model: ideation ~ decade_c + female + decade_c*female + wave fixed effects.
A negative decade*female interaction = the gender gap widens (women more egalitarian)
in younger cohorts — the CFPS pattern.

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
COHORTS = [(1930, 1949), (1950, 1959), (1960, 1969), (1970, 1979),
           (1980, 1989), (1990, 2005)]


def cohort_label(y):
    for lo, hi in COHORTS:
        if lo <= y <= hi:
            return f"{lo}-{hi}"
    return np.nan


def main() -> int:
    frames = []
    for year, bv in BIRTH.items():
        df, _m, _n, idx = L.load_recoded("CGSS", year, extra_cols=[bv])
        df = df[df["n_valid_items"] >= 1].copy()
        df["birthy"] = C.clean_continuous(df[bv], 1920, 2007)
        df["ideation"] = df[idx]
        df["wave"] = year
        frames.append(df[["ideation", "female", "birthy", "wave"]])
    d = pd.concat(frames, ignore_index=True)
    d = d.dropna(subset=["ideation", "female", "birthy"])
    d["cohort"] = d["birthy"].apply(cohort_label)
    d["decade_c"] = (d["birthy"] - 1970) / 10

    # descriptive: gender gap by cohort (pooled)
    desc = []
    for coh, g in d.dropna(subset=["cohort"]).groupby("cohort"):
        mf = g.loc[g.female == 1, "ideation"].mean()
        mm = g.loc[g.female == 0, "ideation"].mean()
        desc.append(dict(cohort=coh, n=len(g), mean_female=round(float(mf), 4),
                         mean_male=round(float(mm), 4), F_minus_M=round(float(mf - mm), 4)))
    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)

    # pooled model with wave fixed effects
    X = {"const": 1.0, "decade_c": d["decade_c"], "female": d["female"],
         "decade_x_female": d["decade_c"] * d["female"]}
    for wv in sorted(d["wave"].unique())[1:]:        # wave dummies (drop first)
        X[f"wave_{wv}"] = (d["wave"] == wv).astype(float)
    r = ST.ols(pd.DataFrame(X), d["ideation"].to_numpy())
    res = [dict(term=t, coef=round(c, 4), se=round(se, 4), t=round(tt, 2), p=round(p, 5))
           for t, c, se, tt, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"])
           if not t.startswith("wave_")]
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note=f"Pooled CGSS 2010-2023 (8 waves), N={r['n']}, wave fixed effects "
                            f"included (coefficients suppressed in result table).")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)

    print(f"Pooled CGSS N={r['n']}")
    print("\nGENDER GAP BY COHORT (pooled):\n", pd.DataFrame(desc).to_string(index=False))
    print("\nMODEL (wave FE):\n", pd.DataFrame(res).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
