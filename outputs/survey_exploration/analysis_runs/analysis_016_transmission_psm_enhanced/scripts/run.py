#!/usr/bin/env python3
"""
analysis_016 — Transmission PSM, enhanced (CFPS, SPEC 5.7). Survey data only.

Strengthens analysis_015 along the requested next steps (no provincial climate yet):
  - FORMATIVE WINDOW: restrict children to age 16-30 (closest to the socialization period).
  - RICHER MATCH: parent mean education + child urban/rural + child age + child sex.
  - BOOTSTRAP SEs: replaces the over-optimistic paired-t p-value from matching-with-
    replacement (matching.psm_att_boot).

Treatment = traditional parent (top tertile of parent-mean ideation) vs egalitarian
(bottom tertile). Outcome = child ideation index.

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.attach_parents,
matching.psm_att / psm_att_boot.
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
import matching as MM             # noqa: E402

RUN = HERE.parents[1]
N_BOOT = 300
WAVE = {
    "2014": dict(f="pid_f", m="pid_m", age="cfps2014_age", eduy="cfps2014eduy", urban="urban14"),
    "2020": dict(f="pid_a_f", m="pid_a_m", age="age", eduy="cfps2020eduy", urban="urban20"),
}


def child_frame(year):
    w = WAVE[year]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["eduy"], w["urban"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df["child_ideation"] = df[idx]
    df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
    df = K.attach_parents(df, "pid", w["f"], w["m"], ["child_ideation", "eduy"])
    df = df.rename(columns={"father_child_ideation": "father_ideation",
                            "mother_child_ideation": "mother_ideation"})
    df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
    df["urban"] = C.clean_continuous(df[w["urban"]], 0, 1)
    df["parent_mean"] = df[["mother_ideation", "father_ideation"]].mean(axis=1)
    df["parent_mean_edu"] = df[["mother_eduy", "father_eduy"]].mean(axis=1)
    return df


def run_psm(rows, year, df, window, covars, amin, amax):
    d = df[(df["age"] >= amin) & (df["age"] <= amax)]
    d = d.dropna(subset=["child_ideation", "parent_mean", "female"] + covars).copy()
    lo, hi = d["parent_mean"].quantile([1 / 3, 2 / 3]).values
    d = d[(d["parent_mean"] <= lo) | (d["parent_mean"] >= hi)].copy()
    d["treat"] = (d["parent_mean"] >= hi).astype(float)
    if (d["treat"] == 1).sum() < 50 or (d["treat"] == 0).sum() < 50:
        return
    pt = MM.psm_att(d, "treat", "child_ideation", covars)
    bs = MM.psm_att_boot(d, "treat", "child_ideation", covars, n_boot=N_BOOT, seed=0)
    rows.append(dict(year=year, window=window, covariates="+".join(covars),
                     n_treated=pt["n_treated"], att=round(pt["att"], 4),
                     paired_se=round(pt["se"], 4), paired_p=round(pt["p"], 6),
                     boot_se=round(bs["boot_se"], 4),
                     boot_ci=f"[{bs['ci_lo']:.3f}, {bs['ci_hi']:.3f}]",
                     boot_p=round(bs["p"], 6)))
    print(f"CFPS {year} [{window}]: ATT={pt['att']:+.4f}  boot_se={bs['boot_se']:.4f}  "
          f"boot_p={bs['p']:.3g}  CI=[{bs['ci_lo']:.3f},{bs['ci_hi']:.3f}]")


def main() -> int:
    rows = []
    base = ["parent_mean_edu", "age", "female"]
    rich = ["parent_mean_edu", "urban", "age", "female"]
    for year in WAVE:
        df = child_frame(year)
        run_psm(rows, year, df, "all ages, base covars", base, 16, 99)
        run_psm(rows, year, df, "all ages, +urban", rich, 16, 99)
        run_psm(rows, year, df, "formative 16-30, +urban", rich, 16, 30)
    pd.DataFrame(rows).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note=f"PSM ATT of having a traditional (top-tertile) vs egalitarian "
                            f"(bottom-tertile) parent on child ideation. Bootstrap n={N_BOOT}. "
                            f"Survey data only (no provincial climate).")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\n", pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
