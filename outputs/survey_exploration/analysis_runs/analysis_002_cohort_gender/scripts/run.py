#!/usr/bin/env python3
"""
analysis_002 — gender-ideation by BIRTH COHORT and gender, in CFPS 2014 & 2020.

Question (SPEC 5.1 + individual practice context): Is the secular decline in
traditionalism a cohort pattern, and does the gender gap differ across cohorts?
Birth cohort is pre-determined (precedes attitude measurement), so the
time-ordering caveat that plagues education/marriage outcomes does not apply.

Outputs:
  01_descriptive_table.csv — index mean/sd/N by birth-cohort x gender x year
  02_missing_table.csv     — coverage of birth year and index
  04_result_table.csv      — OLS: index ~ cohort + female + cohort:female (per year)
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L  # noqa: E402

RUN = HERE.parents[1]

# birth-year variable per CFPS wave (confirmed from structural audit)
BIRTH = {"2014": "cfps_birthy", "2020": "ibirthy"}
COHORTS = [(1930, 1949), (1950, 1959), (1960, 1969), (1970, 1979),
           (1980, 1989), (1990, 2004)]


def cohort_label(y):
    for lo, hi in COHORTS:
        if lo <= y <= hi:
            return f"{lo}-{hi}"
    return np.nan


def main() -> int:
    desc, miss, res = [], [], []
    for year in ["2014", "2020"]:
        bvar = BIRTH[year]
        df, _m, norm, idx = L.load_recoded("CFPS", year, extra_cols=[bvar])
        df["birthy"] = df[bvar].where(df[bvar].between(1930, 2004))
        df["cohort"] = df["birthy"].apply(cohort_label)
        d = df[(df["n_valid_items"] >= 1) & df["cohort"].notna() & df["female"].notna()].copy()

        miss.append(dict(year=year, n_total=len(df),
                         n_index=int((df["n_valid_items"] >= 1).sum()),
                         n_birthy=int(df["birthy"].notna().sum()),
                         n_analysis=len(d),
                         pct_birthy=round(100 * df["birthy"].notna().mean(), 1)))

        for (coh, fem), g in d.groupby(["cohort", "female"]):
            s = g[idx]
            desc.append(dict(year=year, cohort=coh,
                             gender=("female" if fem == 1 else "male"),
                             n=int(s.notna().sum()), mean=round(float(s.mean()), 4),
                             sd=round(float(s.std()), 4)))

        # OLS with cohort as linear centered decade + female + interaction
        d["cohort_mid"] = d["birthy"].apply(
            lambda y: np.mean([lo for lo, hi in COHORTS if lo <= y <= hi] or [np.nan]))
        d["decade_c"] = (d["birthy"] - 1970) / 10.0
        X = pd.DataFrame({
            "const": 1.0,
            "decade_c": d["decade_c"],
            "female": d["female"],
            "decade_x_female": d["decade_c"] * d["female"],
        })
        y_ = d[idx].values
        ok = X.notna().all(axis=1) & ~np.isnan(y_)
        Xm, ym = X[ok].values, y_[ok]
        beta, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
        resid = ym - Xm @ beta
        n, k = Xm.shape
        sigma2 = (resid @ resid) / (n - k)
        cov = sigma2 * np.linalg.inv(Xm.T @ Xm)
        se = np.sqrt(np.diag(cov))
        for name, b, s in zip(X.columns, beta, se):
            res.append(dict(year=year, model="OLS index~decade*female", n=int(n),
                            term=name, coef=round(float(b), 4), se=round(float(s), 4),
                            t=round(float(b / s), 2)))
        print(f"CFPS {year}: N={n}  decade_c={beta[1]:+.4f}  female={beta[2]:+.4f}  "
              f"decade:female={beta[3]:+.4f}")

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    print("\nWrote analysis_002 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
