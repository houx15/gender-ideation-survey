#!/usr/bin/env python3
"""analysis_023 — Table 1 (descriptive statistics) per (program, year).

For every (program, year) we build a standard sociology-paper Table 1:
variable | explanation | n | mean | sd | min | max | missing %.

Each table is written to tables/descriptives_<program>_<year>.csv, and a long
combined file goes to tables/descriptives_long.csv for cross-table comparisons.

Variables (per survey-year):
  - ideation_index : gender-ideology index, [0,1], 1 = most traditional
  - female         : 1 if female, 0 if male
  - birth_year     : year of birth (4-digit)
  - urban          : 1 urban, 0 rural
  - edu_yrs        : years of completed education (mapped from level codes)
  - employed       : 1 currently employed (per-survey definition)
  - income         : personal annual income, RMB (CFPS14 income; CFPS20
                     emp_income; CGSS a8a; ACWF1990 w151; ACWF2000 c18_a;
                     ACWF2010 C18AA)
  - log_income     : ln(1 + income)
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
TABLES = RUN / "tables"
TABLES.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L              # noqa: E402
import rq51_helpers as H              # noqa: E402
import descriptive_stats as DS        # noqa: E402

VARSPEC = [
    ("ideation",        "Gender-ideology index",       "Mean of valid items, mapped to [0,1]; 1 = most traditional"),
    ("female",          "Female (0/1)",                 "1 if respondent is female, 0 if male"),
    ("birthy",          "Birth year",                   "4-digit year of birth"),
    ("urban",           "Urban hukou (0/1)",            "Hukou: 农业=rural, 非农业 or 居民=urban; see method"),
    ("edu_yrs",         "Education (years, current)",   "Highest completed level mapped to years (continuous)"),
    ("employed",        "Currently employed (0/1)",     "Survey-specific employment indicator; see method note"),
    ("isei_current",    "Occupation ISEI (current)",    "Current-job ISEI; only CFPS 2020 has it directly"),
    ("isei_aspiration", "Occupation ISEI (aspiration)", "CFPS 2014 youth (kr1==4): ks801code→ISCO-88→ISEI"),
    ("edu_aspiration",  "Education aspiration (yrs)",   "CFPS 2014 youth (kr1==4): qc201 level → years"),
    ("income",          "Personal income (RMB)",        "Annual personal income (urban monthly for ACWF 1990)"),
    ("log_income",      "log(1 + income)",              "Natural log of (1+income)"),
]


def build_one(dataset: str, year: str) -> pd.DataFrame:
    df, _m, _n, idx = L.load_recoded(dataset, year)
    df["ideation"] = df[idx]
    df["birthy"] = H.birth_year(dataset, year).reset_index(drop=True)
    df["urban"] = H.urban_indicator(dataset, year).reset_index(drop=True)
    df["edu_yrs"] = H.education_years(dataset, year).reset_index(drop=True)
    df["employed"] = H.employed_indicator(dataset, year).reset_index(drop=True)
    df["isei_current"] = H.occupation_isei(dataset, year).reset_index(drop=True)
    # aspirational measures: CFPS 2014 only (youth subsample kr1==4).
    if dataset == "CFPS" and year == "2014":
        df["isei_aspiration"] = H.cfps2014_aspiration_isei().reset_index(drop=True)
        df["edu_aspiration"] = H.cfps2014_aspiration_edu_years().reset_index(drop=True)
    else:
        df["isei_aspiration"] = np.nan
        df["edu_aspiration"] = np.nan
    df["income"] = H.personal_income(dataset, year).reset_index(drop=True)
    df["log_income"] = np.log1p(df["income"])
    rows = []
    for col, name, expl in VARSPEC:
        r = DS.describe_var(df[col], name=name, explanation=expl)
        r["dataset"] = dataset
        r["year"] = year
        r["column"] = col
        rows.append(r)
    return pd.DataFrame(rows)


def main() -> int:
    long_rows = []
    for (dataset, year) in L.SURVEYS:
        t = build_one(dataset, year)
        out = TABLES / f"descriptives_{dataset.lower()}_{year}.csv"
        # paper-friendly column order
        t = t[["column", "name", "explanation", "n", "mean", "sd", "min", "max",
               "n_missing", "missing_pct", "dataset", "year"]]
        t.to_csv(out, index=False, float_format="%.4f")
        long_rows.append(t.assign(survey_year=f"{dataset} {year}"))
        print(f"-> wrote {out.name}  (N respondents incl missing = "
              f"{t.iloc[0]['n'] + t.iloc[0]['n_missing']})")
    combined = pd.concat(long_rows, ignore_index=True)
    combined.to_csv(TABLES / "descriptives_long.csv", index=False, float_format="%.4f")
    print(f"\nwrote tables/descriptives_long.csv  ({len(combined)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
