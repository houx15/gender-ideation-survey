#!/usr/bin/env python3
"""
analysis_004 — CFPS gender ideology & FAMILY PRACTICE (SPEC 5.2).

Associations (cross-sectional, NOT causal) between the gender-ideation index and:
  - currently in a registered marriage   (LPM)
  - daily housework hours                 (OLS, with gender interaction)
  - ideal number of children (2014 only)  (OLS)
And couple matching: spouse-linked ideation distance and combination types.

Uses tested helpers: ideation_lib, cfps_outcomes, stats_helpers.
Outputs: 01_descriptive_table.csv, 02_missing_table.csv, 04_result_table.csv,
         couple_table.csv.
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

WAVE = {
    "2014": dict(age="cfps2014_age", housework="qq9010", ideal="qm501",
                 spouse="pid_s", pid="pid"),
    "2020": dict(age="age", housework="qq9010n", ideal=None,
                 spouse=None, pid="pid"),
}


def tertile(s: pd.Series) -> pd.Series:
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


def main() -> int:
    desc, miss, res, couple = [], [], [], []

    for year, w in WAVE.items():
        extra = [w["age"], w["housework"], "qea0", w["pid"]]
        if w["ideal"]:
            extra.append(w["ideal"])
        if w["spouse"]:
            extra.append(w["spouse"])
        df, _m, _norm, idx = L.load_recoded("CFPS", year, extra_cols=extra)

        df = df[df["n_valid_items"] >= 1].copy()
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["currently_married"] = C.currently_married(df["qea0"])
        df["ever_married"] = C.ever_married(df["qea0"])
        df["housework_hrs"] = C.clean_continuous(df[w["housework"]], 0, 24)
        if w["ideal"]:
            df["ideal_children"] = C.clean_continuous(df[w["ideal"]], 0, 10)

        # ---- missing/coverage ----
        miss.append(dict(year=year, n_index=len(df),
                         pct_age=round(100 * df["age"].notna().mean(), 1),
                         pct_married_var=round(100 * df["currently_married"].notna().mean(), 1),
                         pct_housework=round(100 * df["housework_hrs"].notna().mean(), 1),
                         pct_ideal=(round(100 * df["ideal_children"].notna().mean(), 1)
                                    if w["ideal"] else "n/a")))

        # ---- descriptive: outcomes by ideation tertile x gender ----
        df["idx_tertile"] = tertile(df[idx])
        for (t, fem), g in df.dropna(subset=["idx_tertile", "female"]).groupby(
                ["idx_tertile", "female"], observed=True):
            desc.append(dict(
                year=year, ideation_tertile=t,
                gender=("female" if fem == 1 else "male"), n=len(g),
                pct_currently_married=round(100 * g["currently_married"].mean(), 1),
                mean_housework_hrs=round(float(g["housework_hrs"].mean()), 2),
                mean_ideal_children=(round(float(g["ideal_children"].mean()), 2)
                                     if w["ideal"] else None)))

        # ---- models ----
        d = df.copy()
        d["age_c"] = (d["age"] - 40) / 10
        d["age_c2"] = d["age_c"] ** 2

        # LPM: currently_married ~ ideation + female + age + age^2
        X = pd.DataFrame({"const": 1.0, "ideation": d[idx], "female": d["female"],
                          "age_c": d["age_c"], "age_c2": d["age_c2"]})
        r = ST.ols(X, d["currently_married"].to_numpy())
        for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
            res.append(dict(year=year, model="LPM currently_married", n=r["n"],
                            term=term, coef=round(c, 4), se=round(se, 4), t=round(t, 2)))

        # OLS: housework_hrs ~ ideation*female + age
        X = pd.DataFrame({"const": 1.0, "ideation": d[idx], "female": d["female"],
                          "ideation_x_female": d[idx] * d["female"],
                          "age_c": d["age_c"]})
        r = ST.ols(X, d["housework_hrs"].to_numpy())
        for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
            res.append(dict(year=year, model="OLS housework_hrs", n=r["n"],
                            term=term, coef=round(c, 4), se=round(se, 4), t=round(t, 2)))

        # OLS: ideal_children ~ ideation + female + age (2014)
        if w["ideal"]:
            X = pd.DataFrame({"const": 1.0, "ideation": d[idx], "female": d["female"],
                              "age_c": d["age_c"]})
            r = ST.ols(X, d["ideal_children"].to_numpy())
            for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
                res.append(dict(year=year, model="OLS ideal_children", n=r["n"],
                                term=term, coef=round(c, 4), se=round(se, 4), t=round(t, 2)))

        # ---- couple matching (2014 has in-file spouse pointer) ----
        if w["spouse"]:
            idx_by_pid = df.set_index(w["pid"])[idx].to_dict()
            sp = df[df[w["spouse"]] > 0].copy()
            sp["spouse_idx"] = sp[w["spouse"]].map(idx_by_pid)
            dy = sp.dropna(subset=[idx, "spouse_idx"])
            gap = (dy[idx] - dy["spouse_idx"]).abs()
            med = df[idx].median()
            ego_hi = dy[idx] >= med
            sp_hi = dy["spouse_idx"] >= med
            couple.append(dict(year=year, n_dyads=len(dy),
                               mean_abs_gap=round(float(gap.mean()), 4),
                               median_abs_gap=round(float(gap.median()), 4),
                               corr_ego_spouse=round(float(np.corrcoef(dy[idx], dy["spouse_idx"])[0, 1]), 3),
                               pct_both_traditional=round(100 * float((ego_hi & sp_hi).mean()), 1),
                               pct_both_progressive=round(100 * float((~ego_hi & ~sp_hi).mean()), 1),
                               pct_mixed=round(100 * float((ego_hi ^ sp_hi).mean()), 1)))
        print(f"CFPS {year}: N={len(df)} | married coef, housework coef in result table")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    if couple:
        pd.DataFrame(couple).to_csv(RUN / "couple_table.csv", index=False)
    print("Wrote analysis_004 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
