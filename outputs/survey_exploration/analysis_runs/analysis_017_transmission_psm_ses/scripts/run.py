#!/usr/bin/env python3
"""
analysis_017 — Transmission PSM + family SES proxy (CFPS 2014, SPEC 5.7).

Requested next step: add family SES to the transmission match. There is NO CFPS family
file in the data (only adult files) and 2020 has no personal-total-income variable, so
household income is unavailable. The best available proxy is the PARENTS' personal total
income (`p_income`, CFPS 2014), attached via the parent links. We add parent mean
log-income to the richest match and check whether the transmission ATT survives.

Treatment = traditional parent (top tertile of parent-mean ideation) vs egalitarian
(bottom tertile). Outcome = child ideation. Bootstrap inference.

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


def child_frame():
    df, _m, _n, idx = L.load_recoded(
        "CFPS", "2014",
        extra_cols=["pid", "pid_f", "pid_m", "cfps2014_age", "cfps2014eduy",
                    "urban14", "p_income"])
    df = df[df["n_valid_items"] >= 1].copy()
    df["child_ideation"] = df[idx]
    df["eduy"] = C.clean_continuous(df["cfps2014eduy"], 0, 22)
    df["inc"] = C.clean_continuous(df["p_income"], 0, 1e7)   # keep legit zeros, drop negatives
    df = K.attach_parents(df, "pid", "pid_f", "pid_m", ["child_ideation", "eduy", "inc"])
    df = df.rename(columns={"father_child_ideation": "father_ideation",
                            "mother_child_ideation": "mother_ideation"})
    df["age"] = C.clean_continuous(df["cfps2014_age"], 16, 99)
    df["urban"] = C.clean_continuous(df["urban14"], 0, 1)
    df["parent_mean"] = df[["mother_ideation", "father_ideation"]].mean(axis=1)
    df["parent_mean_edu"] = df[["mother_eduy", "father_eduy"]].mean(axis=1)
    df["parent_log_income"] = np.log1p(df[["mother_inc", "father_inc"]].mean(axis=1))
    return df


def run(rows, df, label, covars, amin, amax):
    d = df[(df["age"] >= amin) & (df["age"] <= amax)]
    d = d.dropna(subset=["child_ideation", "parent_mean", "female"] + covars).copy()
    lo, hi = d["parent_mean"].quantile([1 / 3, 2 / 3]).values
    d = d[(d["parent_mean"] <= lo) | (d["parent_mean"] >= hi)].copy()
    d["treat"] = (d["parent_mean"] >= hi).astype(float)
    if (d["treat"] == 1).sum() < 50 or (d["treat"] == 0).sum() < 50:
        return
    pt = MM.psm_att(d, "treat", "child_ideation", covars)
    bs = MM.psm_att_boot(d, "treat", "child_ideation", covars, n_boot=N_BOOT, seed=0)
    rows.append(dict(spec=label, n_treated=pt["n_treated"], att=round(pt["att"], 4),
                     boot_se=round(bs["boot_se"], 4),
                     boot_ci=f"[{bs['ci_lo']:.3f}, {bs['ci_hi']:.3f}]",
                     boot_p=round(bs["p"], 6)))
    print(f"  {label}: ATT={pt['att']:+.4f}  boot_se={bs['boot_se']:.4f}  "
          f"boot_p={bs['p']:.3g}  CI=[{bs['ci_lo']:.3f},{bs['ci_hi']:.3f}]  n_t={pt['n_treated']}")


def main() -> int:
    df = child_frame()
    edu_urban = ["parent_mean_edu", "urban", "age", "female"]
    plus_inc = edu_urban + ["parent_log_income"]
    rows = []
    print("CFPS 2014 transmission ATT (traditional vs egalitarian parent):")
    run(rows, df, "edu+urban (no income)", edu_urban, 16, 99)
    run(rows, df, "edu+urban+INCOME", plus_inc, 16, 99)
    run(rows, df, "edu+urban+INCOME, formative 16-30", plus_inc, 16, 30)
    pd.DataFrame(rows).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame([dict(note="CFPS 2014 only. Family income unavailable (no CFPS family file; "
                            "2020 has no personal-total-income var). SES proxied by parents' "
                            "personal total income (p_income, ~47% legitimate zeros = non-earners). "
                            f"Bootstrap n={N_BOOT}.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\n", pd.DataFrame(rows).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
