#!/usr/bin/env python3
"""
analysis_003 — CFPS within-wave LINKAGE FEASIBILITY for couples and parent-child
ideation analyses (SPEC 5.2 couple matching, 5.7 parent-child transmission).

CFPS gives each respondent the in-sample person-IDs of their father (pid_f),
mother (pid_m) and spouse (pid_s). If those IDs point to other respondents who
ALSO answered the ideation battery, we can build dyads. This run quantifies how
many such dyads exist and reports the raw within-dyad ideation correlation where
they do — establishing whether these analyses are viable before investing in them.

Outputs:
  01_descriptive_table.csv — dyad counts + ideation correlations (per wave, per link)
  02_missing_table.csv     — how link IDs and ideation availability attrit the sample
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

LINKS = {
    "2014": dict(pid="pid", father="pid_f", mother="pid_m", spouse="pid_s",
                 age="cfps2014_age"),
    "2020": dict(pid="pid", father="pid_a_f", mother="pid_a_m", spouse=None,
                 age="age"),
}


def main() -> int:
    desc, miss = [], []
    for year, cols in LINKS.items():
        extra = [c for c in [cols["pid"], cols["father"], cols["mother"],
                             cols["spouse"], cols["age"]] if c]
        df, _m, _norm, idx = L.load_recoded("CFPS", year, extra_cols=extra)
        has_idx = df["n_valid_items"] >= 1

        # map pid -> (index, female) for respondents with a valid index
        pidc = cols["pid"]
        base = df.loc[has_idx, [pidc, idx, "female"]].dropna(subset=[pidc])
        idx_by_pid = base.set_index(pidc)[idx].to_dict()
        fem_by_pid = base.set_index(pidc)["female"].to_dict()

        def valid_pid(series):
            # CFPS uses negatives / 0 as not-applicable; valid links are positive ids present in-sample
            return series.where(series > 0)

        miss_row = dict(year=year, n_total=len(df), n_with_index=int(has_idx.sum()))
        # parent-child + couple dyads
        for link in ["father", "mother", "spouse"]:
            lvar = cols[link]
            if lvar is None or lvar not in df.columns:
                miss_row[f"n_{link}_id"] = "n/a"
                continue
            link_id = valid_pid(df[lvar])
            n_has_link = int(link_id.notna().sum())
            miss_row[f"n_{link}_id"] = n_has_link

            # dyads: ego has index, linked person has index
            sub = df.loc[has_idx & link_id.notna(), [idx, lvar, "female"]].copy()
            sub["alter_index"] = sub[lvar].map(idx_by_pid)
            sub["alter_female"] = sub[lvar].map(fem_by_pid)
            dyad = sub.dropna(subset=[idx, "alter_index"])
            n_dyad = len(dyad)
            r = (round(float(np.corrcoef(dyad[idx], dyad["alter_index"])[0, 1]), 3)
                 if n_dyad >= 30 else None)
            desc.append(dict(year=year, link=link, n_ego_with_link=n_has_link,
                             n_dyad_both_index=n_dyad,
                             ego_mean=round(float(dyad[idx].mean()), 4) if n_dyad else None,
                             alter_mean=round(float(dyad["alter_index"].mean()), 4) if n_dyad else None,
                             within_dyad_r=r))
            print(f"CFPS {year} {link:7s}: ego-with-link={n_has_link:6d}  "
                  f"dyads(both index)={n_dyad:6d}  r={r}")
        miss.append(miss_row)

    pd.DataFrame(desc).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\nWrote analysis_003 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
