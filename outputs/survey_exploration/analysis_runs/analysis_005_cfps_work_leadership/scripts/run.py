#!/usr/bin/env python3
"""
analysis_005 — CFPS gender ideology & WORK / LEADERSHIP (SPEC 5.3).

Cross-sectional associations between the gender-ideation index and:
  - being employed                       (LPM, with gender interaction)
  - log wage income (employed only)      (OLS)
  - holding an admin/management post qg14 (LPM, employed only)
  - having direct subordinates qg17       (LPM, employed only)

Key question: does ideology relate to labour outcomes *differently by gender*
(e.g., traditional women less likely employed)? -> ideation×female interaction.

Uses tested helpers: ideation_lib, cfps_outcomes, stats_helpers.
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
    "2014": dict(age="cfps2014_age", employ="employ2014", wage="p_wage",
                 mgmt="qg14", sub="qg17"),
    "2020": dict(age="age", employ="employ", wage="emp_income",
                 mgmt="qg14", sub="qg17"),
}


def tertile(s):
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


def add_model(res, year, name, X, y):
    r = ST.ols(X, y)
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(year=year, model=name, n=r["n"], term=term,
                        coef=round(c, 4), se=round(se, 4), t=round(t, 2)))


def main() -> int:
    desc, miss, res = [], [], []
    for year, w in WAVE.items():
        extra = [w["age"], w["employ"], w["wage"], w["mgmt"], w["sub"]]
        df, _m, _norm, idx = L.load_recoded("CFPS", year, extra_cols=extra)
        df = df[df["n_valid_items"] >= 1].copy()

        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["employed"] = C.employed(df[w["employ"]])
        df["log_wage"] = np.log1p(C.clean_continuous(df[w["wage"]], 0, 1e7))
        df["mgmt"] = C.yes_no(df[w["mgmt"]])
        df["has_sub"] = C.yes_no(df[w["sub"]])
        df["age_c"] = (df["age"] - 40) / 10
        df["age_c2"] = df["age_c"] ** 2

        miss.append(dict(year=year, n_index=len(df),
                         pct_employed_var=round(100 * df["employed"].notna().mean(), 1),
                         n_employed=int((df["employed"] == 1).sum()),
                         pct_wage_amg_emp=round(100 * df.loc[df["employed"] == 1, "log_wage"].notna().mean(), 1),
                         pct_mgmt_amg_emp=round(100 * df.loc[df["employed"] == 1, "mgmt"].notna().mean(), 1)))

        # descriptive by ideation tertile x gender
        df["idx_t"] = tertile(df[idx])
        emp = df[df["employed"] == 1]
        for (t, fem), g in df.dropna(subset=["idx_t", "female"]).groupby(["idx_t", "female"], observed=True):
            ge = g[g["employed"] == 1]
            desc.append(dict(year=year, ideation_tertile=t,
                             gender=("female" if fem == 1 else "male"), n=len(g),
                             pct_employed=round(100 * g["employed"].mean(), 1),
                             mean_log_wage=round(float(ge["log_wage"].mean()), 3) if len(ge) else None,
                             pct_mgmt=round(100 * ge["mgmt"].mean(), 1) if ge["mgmt"].notna().any() else None))

        # models
        Xemp = pd.DataFrame({"const": 1.0, "ideation": df[idx], "female": df["female"],
                             "ideation_x_female": df[idx] * df["female"],
                             "age_c": df["age_c"], "age_c2": df["age_c2"]})
        add_model(res, year, "LPM employed", Xemp, df["employed"].to_numpy())

        Xw = pd.DataFrame({"const": 1.0, "ideation": emp[idx], "female": emp["female"],
                           "ideation_x_female": emp[idx] * emp["female"],
                           "age_c": emp["age_c"], "age_c2": emp["age_c2"]})
        add_model(res, year, "OLS log_wage (employed)", Xw, emp["log_wage"].to_numpy())

        Xm = pd.DataFrame({"const": 1.0, "ideation": emp[idx], "female": emp["female"],
                           "ideation_x_female": emp[idx] * emp["female"], "age_c": emp["age_c"]})
        add_model(res, year, "LPM mgmt (employed)", Xm, emp["mgmt"].to_numpy())
        print(f"CFPS {year}: N={len(df)}, employed={int((df['employed']==1).sum())}")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    print("Wrote analysis_005 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
