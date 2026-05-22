#!/usr/bin/env python3
"""
analysis_019 — Population-weighted estimates (CFPS, SPEC 5.1-5.7).

Every estimate so far has been unweighted (sample, not population). Here we apply CFPS
national cross-section weights to the headline quantities and compare weighted vs
unweighted:
  - national mean ideation,
  - the gender gap (ideation ~ female),
  - transmission (child_ideation ~ parent_mean + age + female), in the linked child sample.

Weighted models use WLS with robust (sandwich) SEs (correct for survey weights).

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents,
stats_helpers.ols / wls.
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
    "2014": dict(wt="rswt_natcs14", age="cfps2014_age", f="pid_f", m="pid_m"),
    "2020": dict(wt="rswt_natcs20n", age="age", f="pid_a_f", m="pid_a_m"),
}


def wmean(x, w):
    d = pd.DataFrame({"x": x, "w": w}).dropna()
    d = d[d["w"] > 0]
    return float(np.average(d["x"], weights=d["w"]))


def main() -> int:
    levels, gaps, trans = [], [], []
    for year, w in WAVE.items():
        df, _m, _n, idx = L.load_recoded(
            "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["wt"]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["wt"] = C.clean_continuous(df[w["wt"]], 1e-9, 1e12)
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)

        # national mean ideation: unweighted vs weighted
        levels.append(dict(year=year, n=int(df[idx].notna().sum()),
                           mean_unweighted=round(float(df[idx].mean()), 4),
                           mean_weighted=round(wmean(df[idx], df["wt"]), 4)))

        # gender gap: ideation ~ female
        g = df.dropna(subset=[idx, "female"])
        Xg = pd.DataFrame({"const": 1.0, "female": g["female"]})
        ou = ST.ols(Xg, g[idx].to_numpy())
        ow = ST.wls(Xg, g[idx].to_numpy(), g["wt"].to_numpy())
        gaps.append(dict(year=year, n=ou["n"],
                         female_unweighted=round(ou["coef"][1], 4), p_unw=round(ou["p"][1], 4),
                         female_weighted=round(ow["coef"][1], 4), p_wt=round(ow["p"][1], 4)))

        # transmission: child_ideation ~ parent_mean + age + female (linked children)
        df["child_ideation"] = df[idx]
        d = K.attach_parents(df, "pid", w["f"], w["m"], ["child_ideation"])
        d = d.rename(columns={"father_child_ideation": "father_ideation",
                              "mother_child_ideation": "mother_ideation"})
        d["parent_mean"] = d[["mother_ideation", "father_ideation"]].mean(axis=1)
        d["age_c"] = (d["age"] - 30) / 10
        d = d.dropna(subset=["child_ideation", "parent_mean", "female", "age", "wt"])
        Xt = pd.DataFrame({"const": 1.0, "parent_mean": d["parent_mean"],
                           "female": d["female"], "age_c": d["age_c"]})
        tu = ST.ols(Xt, d["child_ideation"].to_numpy())
        tw = ST.wls(Xt, d["child_ideation"].to_numpy(), d["wt"].to_numpy())
        trans.append(dict(year=year, n=tu["n"],
                          parent_mean_unweighted=round(tu["coef"][1], 4), p_unw=round(tu["p"][1], 6),
                          parent_mean_weighted=round(tw["coef"][1], 4), p_wt=round(tw["p"][1], 6)))
        print(f"CFPS {year}: mean ideation unw={df[idx].mean():.3f} wt={wmean(df[idx], df['wt']):.3f} | "
              f"transmission parent_mean unw={tu['coef'][1]:.3f} wt={tw['coef'][1]:.3f}")

    pd.DataFrame(levels).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(gaps).to_csv(RUN / "gender_gap_weighted.csv", index=False)
    pd.DataFrame(trans).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note="CFPS national cross-section weights (rswt_natcs14 / rswt_natcs20n). "
                            "Weighted models = WLS with robust sandwich SEs.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\nLEVELS:\n", pd.DataFrame(levels).to_string(index=False))
    print("\nGENDER GAP:\n", pd.DataFrame(gaps).to_string(index=False))
    print("\nTRANSMISSION:\n", pd.DataFrame(trans).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
