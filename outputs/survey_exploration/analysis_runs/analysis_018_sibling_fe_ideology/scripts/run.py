#!/usr/bin/env python3
"""
analysis_018 — Sibling resemblance & family fixed effects for ideology (CFPS, SPEC 5.7).

Parent ideology is constant within a sibship, so a family FE cannot estimate the
transmission coefficient. Instead we use the sibling structure two ways:

  (1) SIBLING ICC: how much do siblings resemble each other on the ideation index
      (one-way ICC = family-level share of variance)? Then how much of that resemblance
      does the parents' MEASURED ideology account for (ICC of residuals after removing
      parent_mean, and parent_mean + age + urban)?
  (2) FAMILY FIXED EFFECTS: within sibships, are daughters less traditional than their
      OWN brothers, net of all family-level factors? (fe_ols: ideation ~ female + age).

Multi-child families only (>=2 sampled children sharing both parents).

Uses tested helpers: ideation_lib, cfps_outcomes, stats_helpers.icc_oneway / fe_ols / ols.
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
    # REAL families only: both parents must be in-sample (positive person-ids), else the
    # missing-code pointers (-8/0) would lump unlinked respondents into pseudo-families.
    valid = (df[w["f"]] > 0) & (df[w["m"]] > 0) & df["parent_mean"].notna()
    df = df[valid].copy()
    df["fam"] = df[w["f"]].astype("int64").astype(str) + "_" + df[w["m"]].astype("int64").astype(str)
    return df


def resid_icc(d, xcols):
    """ICC of child_ideation residuals after partialling out xcols (pooled OLS)."""
    sub = d.dropna(subset=["child_ideation", "fam"] + xcols).copy()
    X = pd.DataFrame({"const": 1.0, **{c: sub[c] for c in xcols}})
    beta, *_ = np.linalg.lstsq(X.to_numpy(float), sub["child_ideation"].to_numpy(float), rcond=None)
    sub["resid"] = sub["child_ideation"].to_numpy(float) - X.to_numpy(float) @ beta
    return ST.icc_oneway(sub["resid"], sub["fam"]), len(sub)


def main() -> int:
    icc_rows, fe_rows = [], []
    for year in WAVE:
        df = child_frame(year)
        # multi-child families (>=2 sampled children sharing both parents)
        size = df.groupby("fam")["child_ideation"].transform("size")
        multi = df[(size >= 2) & df["child_ideation"].notna()].copy()
        n_fam = multi["fam"].nunique()

        raw = ST.icc_oneway(multi["child_ideation"], multi["fam"])
        r_pi, n1 = resid_icc(multi, ["parent_mean"])
        r_full, n2 = resid_icc(multi, ["parent_mean", "age", "urban"])
        icc_rows.append(dict(year=year, n_children=len(multi), n_families=n_fam,
                             icc_raw=round(raw, 3),
                             icc_after_parent_ideology=round(r_pi, 3),
                             pct_resemblance_from_parent_ideology=(
                                 round(100 * (raw - r_pi) / raw, 1) if raw else None),
                             icc_after_parent_age_urban=round(r_full, 3)))
        print(f"CFPS {year}: sibling ICC raw={raw:.3f}, after parent ideology={r_pi:.3f} "
              f"(parent ideology explains {100*(raw-r_pi)/raw:.0f}% of sibling resemblance), "
              f"n_fam={n_fam}")

        # family FE: within-sibship daughter-vs-brother ideology gap
        multi["age_c"] = (multi["age"] - 30) / 10
        fe = ST.fe_ols(multi.dropna(subset=["female", "age"]), "fam",
                       "child_ideation", ["female", "age_c"])
        for term, c, se, t, p in zip(fe["term"], fe["coef"], fe["se"], fe["t"], fe["p"]):
            fe_rows.append(dict(year=year, model="family-FE ideation~female+age",
                                n=fe["n"], n_groups=fe["n_groups"], term=term,
                                coef=round(c, 4), se=round(se, 4), t=round(t, 2), p=round(p, 4)))
        jf = fe["term"].index("female")
        print(f"          family-FE female (daughter-vs-own-brother) = {fe['coef'][jf]:+.4f} "
              f"(p={fe['p'][jf]:.3f}, n_groups={fe['n_groups']})")

    pd.DataFrame(icc_rows).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(fe_rows).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note="Multi-child families (>=2 sampled siblings sharing both parents). "
                            "ICC = one-way (sibling resemblance). FE absorbs all family-level "
                            "factors incl. parent ideology; identifies within-sibship gaps only.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\nSIBLING ICC:\n", pd.DataFrame(icc_rows).to_string(index=False))
    print("\nFAMILY FE:\n", pd.DataFrame(fe_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
