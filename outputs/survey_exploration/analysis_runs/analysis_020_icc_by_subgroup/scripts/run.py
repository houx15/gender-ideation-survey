#!/usr/bin/env python3
"""
analysis_020 — Sibling ICC of ideology by urban/rural and cohort (CFPS, SPEC 5.7).

Extends analysis_018: is gender ideology more family-clustered (siblings more alike) in
rural vs urban families, and in older vs younger sibships (a cohort proxy)? And does the
share explained by the parents' measured ideology differ across these contexts?

Real multi-child families only (>=2 sampled siblings sharing both in-sample parents).
Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents,
stats_helpers.icc_oneway.
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
    "2014": dict(f="pid_f", m="pid_m", age="cfps2014_age", urban="urban14"),
    "2020": dict(f="pid_a_f", m="pid_a_m", age="age", urban="urban20"),
}


def child_frame(year):
    w = WAVE[year]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["urban"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df["child_ideation"] = df[idx]
    df = K.attach_parents(df, "pid", w["f"], w["m"], ["child_ideation"])
    df = df.rename(columns={"father_child_ideation": "father_ideation",
                            "mother_child_ideation": "mother_ideation"})
    df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
    df["urban"] = C.clean_continuous(df[w["urban"]], 0, 1)
    df["parent_mean"] = df[["mother_ideation", "father_ideation"]].mean(axis=1)
    valid = (df[w["f"]] > 0) & (df[w["m"]] > 0) & df["parent_mean"].notna()
    df = df[valid].copy()
    df["fam"] = df[w["f"]].astype("int64").astype(str) + "_" + df[w["m"]].astype("int64").astype(str)
    size = df.groupby("fam")["child_ideation"].transform("size")
    return df[size >= 2].copy()


def resid_icc(d, xcols):
    sub = d.dropna(subset=["child_ideation", "fam"] + xcols).copy()
    X = pd.DataFrame({"const": 1.0, **{c: sub[c] for c in xcols}}).to_numpy(float)
    beta, *_ = np.linalg.lstsq(X, sub["child_ideation"].to_numpy(float), rcond=None)
    sub["r"] = sub["child_ideation"].to_numpy(float) - X @ beta
    return ST.icc_oneway(sub["r"], sub["fam"])


def icc_block(rows, year, d, subgroup):
    if d["fam"].nunique() < 30:
        return
    raw = ST.icc_oneway(d["child_ideation"], d["fam"])
    after_pi = resid_icc(d, ["parent_mean"])
    rows.append(dict(year=year, subgroup=subgroup, n_children=len(d),
                     n_families=d["fam"].nunique(), icc_raw=round(raw, 3),
                     icc_after_parent_ideology=round(after_pi, 3),
                     pct_from_parent_ideology=round(100 * (raw - after_pi) / raw, 1) if raw else None))
    print(f"  {year} {subgroup:18s}: ICC={raw:.3f} (after parent ideology {after_pi:.3f}), "
          f"n_fam={d['fam'].nunique()}")


def main() -> int:
    rows = []
    for year in WAVE:
        df = child_frame(year)
        # family-level urban: majority of the family's children urban
        fam_urban = df.groupby("fam")["urban"].transform("mean")
        # family-level cohort proxy: family's mean child age (median split)
        fam_age = df.groupby("fam")["age"].transform("mean")
        med_age = fam_age.median()

        icc_block(rows, year, df, "all multi-child")
        icc_block(rows, year, df[fam_urban < 0.5], "rural families")
        icc_block(rows, year, df[fam_urban >= 0.5], "urban families")
        icc_block(rows, year, df[fam_age >= med_age], "older sibship")
        icc_block(rows, year, df[fam_age < med_age], "younger sibship")

    pd.DataFrame(rows).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame([dict(note="Sibling ICC of ideation by subgroup; real multi-child families "
                            "(both parents in-sample). 'after parent ideology' = ICC of residuals "
                            "from pooled regression on parent_mean.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\n", pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
