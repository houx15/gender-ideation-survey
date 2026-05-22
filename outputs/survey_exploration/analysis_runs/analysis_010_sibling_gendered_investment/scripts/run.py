#!/usr/bin/env python3
"""
analysis_010 — Gendered educational investment, done properly (SPEC 5.5).

Fixes two flaws in analysis_009 raised in review:
  (1) HOUSEHOLD STRUCTURE not matched -> use a within-family design: among
      one-son-one-daughter families, compare the daughter to HER OWN brother
      (differences out parent ideology, SES, region, household structure).
  (2) LIFE STAGE / education censoring -> restrict to completed-schooling ages
      (age >= 25); a 16-year-old's low years-of-schooling means "still in school",
      not under-investment.

Parts:
  A. Re-estimate the naive parent-ideology model on age>=25 only.
  B. Within-family: edu_gap (daughter - son) ~ parent_mean_ideology + age_gap,
     for one-son-one-daughter families (all ages, then both >=25 robustness).
  + household-structure descriptives.

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage (attach_parents,
one_son_one_daughter_diff), stats_helpers.
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


def child_frame(year):
    w = WAVE[year]
    df, _m, _n, idx = L.load_recoded("CFPS", year,
                                     extra_cols=[w["pid"], w["f"], w["m"], w["age"], w["eduy"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df["pi"] = df[idx]
    df = K.attach_parents(df, w["pid"], w["f"], w["m"], ["pi"])
    df = df.dropna(subset=["mother_pi", "father_pi", "female"]).copy()
    df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
    df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
    df["parent_mean"] = df[["mother_pi", "father_pi"]].mean(axis=1)
    df["fam"] = df[w["f"]].astype(str) + "_" + df[w["m"]].astype(str)
    return df.dropna(subset=["eduy", "age"])


def main() -> int:
    desc, miss, res, struct = [], [], [], []
    for year in WAVE:
        df = child_frame(year)

        # ---- household-structure descriptives ----
        g = df.groupby("fam")["female"].agg(["size", "sum"])
        struct.append(dict(year=year, n_children=len(df), n_families=len(g),
                           n_singleton_fam=int((g["size"] == 1).sum()),
                           n_multi_fam=int((g["size"] >= 2).sum()),
                           n_one_son_one_daughter=int(((g["size"] == 2) & (g["sum"] == 1)).sum())))

        # ---- A. naive model, completed-schooling ages only ----
        for amin in (0, 25):
            d = df[df["age"] >= amin].copy()
            d["age_c"] = (d["age"] - 30) / 10
            X = pd.DataFrame({"const": 1.0, "mother_pi": d["mother_pi"],
                              "father_pi": d["father_pi"], "child_female": d["female"],
                              "mother_x_daughter": d["mother_pi"] * d["female"],
                              "father_x_daughter": d["father_pi"] * d["female"],
                              "age_c": d["age_c"], "age_c2": ((d["age"] - 30) / 10) ** 2})
            add_model(res, year, f"A naive child_eduy (age>={amin})", X, d["eduy"].to_numpy())

        # ---- B. within-family one-son-one-daughter difference ----
        for amin, tag in ((0, "all-ages"), (25, "both>=25")):
            sub = df[df["age"] >= amin]
            diff = K.one_son_one_daughter_diff(sub, "fam", "female", ["eduy", "age", "parent_mean"])
            # keep only families that still have BOTH a son and a daughter after the age filter
            diff = diff.dropna(subset=["eduy_diff", "age_diff"])
            # parent_mean_diff is ~0 (same parents); recover the family parent_mean level
            pm = sub.groupby("fam")["parent_mean"].first()
            diff["parent_mean"] = diff["fam"].map(pm)
            if len(diff) < 30:
                miss.append(dict(year=year, design=f"OSOD {tag}", n_families=len(diff),
                                 note="too few for model"))
                continue
            X = pd.DataFrame({"const": 1.0, "parent_mean_ideology": diff["parent_mean"],
                              "age_gap": diff["age_diff"]})
            r = add_model(res, year, f"B within-family edu_gap(daughter-son) [{tag}]",
                          X, diff["eduy_diff"].to_numpy())
            desc.append(dict(year=year, design=f"OSOD {tag}", n_families=len(diff),
                             mean_edu_gap_daughter_minus_son=round(float(diff["eduy_diff"].mean()), 3),
                             parent_ideology_coef=round(r["coef"][1], 3),
                             parent_ideology_t=round(r["t"][1], 2)))
            miss.append(dict(year=year, design=f"OSOD {tag}", n_families=len(diff), note="ok"))
            print(f"CFPS {year} OSOD {tag}: N_fam={len(diff)}, "
                  f"mean gap(d-s)={diff['eduy_diff'].mean():+.2f}, "
                  f"parent_ideology coef={r['coef'][1]:+.3f} (t={r['t'][1]:.2f})")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame(struct).to_csv(RUN / "household_structure.csv", index=False)
    print("\n", pd.DataFrame(struct).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
