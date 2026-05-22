#!/usr/bin/env python3
"""
analysis_012 — Does PARENT gender ideology drive gendered resource allocation? (CFPS, SPEC 5.5)

CEPS has the best resource measures but NO gender-ideology item and no province
identifier (county codes anonymized), so ideology cannot be attached there. CFPS is
the only data with BOTH measured parental ideology AND parent-child links, so the
direct test runs here, within the family:

For one-son-one-daughter families, regress the daughter-minus-son gap on the family's
parent ideology. A son-favouring effect of traditional parents would show as:
  - education gap (daughter - son): NEGATIVE coefficient (daughter gets relatively less)
  - housework gap (daughter - son): POSITIVE coefficient (daughter made to do relatively more)

The within-family difference removes all family-level confounds; parent ideology is the
family-level predictor of the within-family gender gap.

Reuses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.one_son_one_daughter_diff,
stats_helpers. No new production code.
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
    "2014": dict(f="pid_f", m="pid_m", age="cfps2014_age", eduy="cfps2014eduy", hw="qq9010"),
    "2020": dict(f="pid_a_f", m="pid_a_m", age="age", eduy="cfps2020eduy", hw="qq9010n"),
}


def child_frame(year):
    w = WAVE[year]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["eduy"], w["hw"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df["pi"] = df[idx]
    df = K.attach_parents(df, "pid", w["f"], w["m"], ["pi"])
    df = df.dropna(subset=["mother_pi", "father_pi", "female"]).copy()
    df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
    df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
    df["hw"] = C.clean_continuous(df[w["hw"]], 0, 24)
    df["parent_mean"] = df[["mother_pi", "father_pi"]].mean(axis=1)
    df["fam"] = df[w["f"]].astype(str) + "_" + df[w["m"]].astype(str)
    return df


def gap_model(res, desc, year, df, outcome, amin, expect_sign):
    sub = df[df["age"] >= amin].dropna(subset=[outcome, "age"])
    diff = K.one_son_one_daughter_diff(sub, "fam", "female", [outcome, "age"])
    diff = diff.dropna(subset=[f"{outcome}_diff", "age_diff"])
    pm = sub.groupby("fam")["parent_mean"].first()
    diff["parent_mean"] = diff["fam"].map(pm)
    if len(diff) < 30:
        return
    X = pd.DataFrame({"const": 1.0, "parent_mean_ideology": diff["parent_mean"],
                      "age_gap": diff["age_diff"]})
    r = ST.ols(X, diff[f"{outcome}_diff"].to_numpy())
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(year=year, outcome=f"{outcome}_gap(daughter-son)", age_min=amin,
                        n_families=r["n"], term=term, coef=round(c, 4),
                        se=round(se, 4), t=round(t, 2)))
    pi = r["coef"][1]
    desc.append(dict(year=year, outcome=outcome, age_min=amin, n_families=len(diff),
                     mean_gap_daughter_minus_son=round(float(diff[f"{outcome}_diff"].mean()), 3),
                     parent_ideology_coef=round(pi, 3),
                     parent_ideology_t=round(r["t"][1], 2),
                     son_favouring=("yes" if np.sign(pi) == expect_sign else "no/unclear")))
    print(f"CFPS {year} {outcome}_gap (age>={amin}): N_fam={len(diff)}, "
          f"parent_ideology coef={pi:+.3f} (t={r['t'][1]:.2f})")


def main() -> int:
    res, desc = [], []
    for year in WAVE:
        df = child_frame(year)
        # investment: education gap; son-favouring => NEGATIVE parent-ideology coef (-1)
        gap_model(res, desc, year, df, "eduy", 25, expect_sign=-1)
        gap_model(res, desc, year, df, "eduy", 0, expect_sign=-1)
        # demand: housework gap; son-favouring => POSITIVE parent-ideology coef (+1)
        gap_model(res, desc, year, df, "hw", 0, expect_sign=+1)
    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame([dict(note="one-son-one-daughter families; gap = daughter - son; "
                            "parent_mean = mean of both parents' ideation index")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    print("\n", pd.DataFrame(desc).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
