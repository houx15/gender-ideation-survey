#!/usr/bin/env python3
"""
analysis_015 — Gender-ideation transmission: correlations + PSM (CFPS, SPEC 5.7).

Completes the "regeneration" question with (a) basic parent-child ideation correlations
with p-values, and (b) a PSM estimate of the effect of having a TRADITIONAL parent on the
child's ideology, matching children on confounders (parent education, child age & sex).

PSM design: treatment = traditional parent (top tertile of parent-mean ideation) vs
egalitarian (bottom tertile); middle tertile dropped for a clean contrast. Outcome =
child ideation index. Covariates = parent mean education, child age, child female.

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents,
matching.psm_att; correlations via scipy.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L          # noqa: E402
import cfps_outcomes as C         # noqa: E402
import cfps_linkage as K          # noqa: E402
import matching as MM             # noqa: E402

RUN = HERE.parents[1]
WAVE = {
    "2014": dict(f="pid_f", m="pid_m", age="cfps2014_age", eduy="cfps2014eduy"),
    "2020": dict(f="pid_a_f", m="pid_a_m", age="age", eduy="cfps2020eduy"),
}


def corr(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 30:
        return (np.nan, np.nan, len(d))
    r, p = stats.pearsonr(d["x"], d["y"])
    return (round(float(r), 3), float(p), len(d))


def main() -> int:
    cors, psm = [], []
    for year, w in WAVE.items():
        df, _m, _n, idx = L.load_recoded(
            "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["eduy"]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["child_ideation"] = df[idx]
        df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
        df = K.attach_parents(df, "pid", w["f"], w["m"], ["child_ideation", "eduy"])
        df = df.rename(columns={"father_child_ideation": "father_ideation",
                                "mother_child_ideation": "mother_ideation",
                                "father_eduy": "father_eduy", "mother_eduy": "mother_eduy"})
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["parent_mean"] = df[["mother_ideation", "father_ideation"]].mean(axis=1)
        df["parent_mean_edu"] = df[["mother_eduy", "father_eduy"]].mean(axis=1)
        both = df.dropna(subset=["child_ideation", "mother_ideation", "father_ideation", "female"])

        # ---- (a) basic correlations with p-values ----
        for who, col in [("mother", "mother_ideation"), ("father", "father_ideation"),
                         ("parent_mean", "parent_mean")]:
            r, p, n = corr(both[col], both["child_ideation"])
            cors.append(dict(year=year, pair=f"{who}-child", subgroup="all", n=n, r=r, p=round(p, 6)))
        for g, lab in [(1, "daughter"), (0, "son")]:
            sub = both[both["female"] == g]
            for who, col in [("mother", "mother_ideation"), ("father", "father_ideation")]:
                r, p, n = corr(sub[col], sub["child_ideation"])
                cors.append(dict(year=year, pair=f"{who}-{lab}", subgroup=lab, n=n, r=r, p=round(p, 6)))

        # ---- (b) PSM: traditional vs egalitarian parent ----
        d = both.dropna(subset=["parent_mean", "parent_mean_edu", "age"]).copy()
        lo, hi = d["parent_mean"].quantile([1 / 3, 2 / 3]).values
        d = d[(d["parent_mean"] <= lo) | (d["parent_mean"] >= hi)].copy()
        d["treat"] = (d["parent_mean"] >= hi).astype(float)   # 1 = traditional parent
        naive = d.loc[d.treat == 1, "child_ideation"].mean() - d.loc[d.treat == 0, "child_ideation"].mean()
        a = MM.psm_att(d, "treat", "child_ideation",
                       ["parent_mean_edu", "age", "female"])
        psm.append(dict(year=year, contrast="traditional vs egalitarian parent (tertiles)",
                        n_treated=a["n_treated"], naive_diff=round(float(naive), 4),
                        psm_att=round(a["att"], 4), se=round(a["se"], 4),
                        t=round(a["t"], 2), p=round(a["p"], 5)))
        print(f"CFPS {year}: parent_mean-child r reported; "
              f"PSM trad-vs-egal ATT on child ideation = {a['att']:+.4f} (p={a['p']:.4g})")

    pd.DataFrame(cors).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(psm).to_csv(RUN / "04_result_table.csv", index=False)
    print("\nCORRELATIONS (parent-child ideation):")
    print(pd.DataFrame(cors).to_string(index=False))
    print("\nPSM (effect of traditional parent on child ideation):")
    print(pd.DataFrame(psm).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
