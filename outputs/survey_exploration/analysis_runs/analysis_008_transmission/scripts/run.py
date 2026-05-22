#!/usr/bin/env python3
"""
analysis_008 — Parent -> child ideation TRANSMISSION (SPEC 5.7).

Does a parent's gender ideology predict their (adult, age>=16) child's ideology,
and does the MOTHER or the FATHER transmit more? Are there same-gender vs
cross-gender paths (mother->daughter, father->son, ...)?

Models (per wave):
  A. child_ideation ~ mother_ideation + father_ideation + child_female + age
     -> compare mother vs father coefficient ("whose ideation matters more").
  B. add mother_ideation:child_female and father_ideation:child_female
     -> same-gender vs cross-gender transmission.

Also reports the four raw path correlations by child gender.
Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents, stats_helpers.
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
    "2014": dict(pid="pid", f="pid_f", m="pid_m", age="cfps2014_age"),
    "2020": dict(pid="pid", f="pid_a_f", m="pid_a_m", age="age"),
}


def add_model(res, year, name, X, y):
    r = ST.ols(X, y)
    for term, c, se, t in zip(r["term"], r["coef"], r["se"], r["t"]):
        res.append(dict(year=year, model=name, n=r["n"], term=term,
                        coef=round(c, 4), se=round(se, 4), t=round(t, 2)))
    return r


def main() -> int:
    desc, miss, res, cmp_rows, paths = [], [], [], [], []
    for year, w in WAVE.items():
        df, _m, _norm, idx = L.load_recoded(
            "CFPS", year, extra_cols=[w["pid"], w["f"], w["m"], w["age"]])
        df = df[df["n_valid_items"] >= 1].copy()
        df["child_ideation"] = df[idx]
        df = K.attach_parents(df, w["pid"], w["f"], w["m"],
                              value_cols=["child_ideation"])
        df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
        df["age_c"] = (df["age"] - 30) / 10

        both = df.dropna(subset=["child_ideation", "father_child_ideation",
                                 "mother_child_ideation", "female"]).copy()
        both = both.rename(columns={"father_child_ideation": "father_ideation",
                                    "mother_child_ideation": "mother_ideation"})
        miss.append(dict(year=year, n_children_with_index=len(df),
                         n_father_linked=int(df["father_child_ideation"].notna().sum()),
                         n_mother_linked=int(df["mother_child_ideation"].notna().sum()),
                         n_both_parents=len(both)))

        # four raw path correlations
        for who, col in [("mother", "mother_ideation"), ("father", "father_ideation")]:
            for g, lab in [(1, "daughter"), (0, "son")]:
                sub = both[both["female"] == g]
                r = float(np.corrcoef(sub[col], sub["child_ideation"])[0, 1]) if len(sub) >= 30 else np.nan
                paths.append(dict(year=year, parent=who, child=lab, n=len(sub),
                                  corr=round(r, 3)))

        # Model A: both parents + child gender
        XA = pd.DataFrame({"const": 1.0,
                           "mother_ideation": both["mother_ideation"],
                           "father_ideation": both["father_ideation"],
                           "child_female": both["female"], "age_c": both["age_c"]})
        rA = add_model(res, year, "A: child_ideation ~ mother+father", XA,
                       both["child_ideation"].to_numpy())
        cm = rA["coef"][rA["term"].index("mother_ideation")]
        cf = rA["coef"][rA["term"].index("father_ideation")]
        cmp_rows.append(dict(year=year, mother_coef=round(cm, 4), father_coef=round(cf, 4),
                             larger=("mother" if abs(cm) > abs(cf) else "father")))

        # Model B: gender interactions (same vs cross-gender transmission)
        XB = pd.DataFrame({"const": 1.0,
                           "mother_ideation": both["mother_ideation"],
                           "father_ideation": both["father_ideation"],
                           "child_female": both["female"],
                           "mother_x_daughter": both["mother_ideation"] * both["female"],
                           "father_x_daughter": both["father_ideation"] * both["female"],
                           "age_c": both["age_c"]})
        add_model(res, year, "B: + gender interactions", XB,
                  both["child_ideation"].to_numpy())
        print(f"CFPS {year}: both-parent children N={len(both)} | "
              f"mother={cm:+.3f} father={cf:+.3f}")

    pd.DataFrame(paths).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame(cmp_rows).to_csv(RUN / "whose_ideation_comparison.csv", index=False)
    print("\n", pd.DataFrame(cmp_rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
