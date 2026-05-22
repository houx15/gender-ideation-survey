#!/usr/bin/env python3
"""
analysis_013 — Parent ideology & gendered allocation: robustness ladder (CFPS, SPEC 5.5).

Extends analysis_012 along three rungs of increasing sample / decreasing within-family
control, all reporting p-values:

  Rung 2 (within-family, EXPANDED): all mixed-gender families (not only one-son-one-
          daughter) -> mean(daughters) - mean(sons) gap, regressed on parent ideology.
  Rung 3 (ALL families, PSM): match daughters to sons on (age, parent ideology) across
          the whole sample; ATT of being a daughter on education / housework. Then
          STRATIFY by parent ideology (traditional vs egalitarian families) to see whether
          the daughter gap is concentrated in traditional families.

(Rung 1, strict one-son-one-daughter, is analysis_012.)

Uses tested helpers: ideation_lib, cfps_outcomes, cfps_linkage.family_gender_gap,
stats_helpers.ols (now with p), matching.psm_att.
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
import matching as MM             # noqa: E402

RUN = HERE.parents[1]
WAVE = {
    "2014": dict(f="pid_f", m="pid_m", age="cfps2014_age", eduy="cfps2014eduy", hw="qq9010"),
    "2020": dict(f="pid_a_f", m="pid_a_m", age="age", eduy="cfps2020eduy", hw="qq9010n"),
}


def child_frame(year):
    w = WAVE[year]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", year, extra_cols=["pid", w["f"], w["m"], w["age"], w["eduy"], w["hw"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df["pi"] = df[idx]
    df = K.attach_parents(df, "pid", w["f"], w["m"], ["pi"])
    df = df.dropna(subset=["mother_pi", "father_pi", "female"]).copy()
    df["eduy"] = C.clean_continuous(df[w["eduy"]], 0, 22)
    df["age"] = C.clean_continuous(df[w["age"]], 16, 99)
    df["hw"] = C.clean_continuous(df[w["hw"]], 0, 24)
    df["parent_mean"] = df[["mother_pi", "father_pi"]].mean(axis=1)
    df["fam"] = df[w["f"]].astype(str) + "_" + df[w["m"]].astype(str)
    return df


def gap_rung2(res, year, df, outcome, amin):
    sub = df[df["age"] >= amin].dropna(subset=[outcome, "age", "parent_mean"])
    gaps = K.family_gender_gap(sub, "fam", "female", [outcome, "age"])
    gaps = gaps.dropna(subset=[f"{outcome}_gap", "age_gap"])
    pm = sub.groupby("fam")["parent_mean"].first()
    gaps["parent_mean"] = gaps["fam"].map(pm)
    if len(gaps) < 30:
        return
    X = pd.DataFrame({"const": 1.0, "parent_mean_ideology": gaps["parent_mean"],
                      "age_gap": gaps["age_gap"]})
    r = ST.ols(X, gaps[f"{outcome}_gap"].to_numpy())
    for term, c, se, t, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"]):
        res.append(dict(year=year, rung="2 within-family (all mixed-gender)",
                        outcome=f"{outcome}_gap(daughter-son)", n_families=r["n"],
                        term=term, coef=round(c, 4), se=round(se, 4),
                        t=round(t, 2), p=round(p, 4)))
    print(f"  R2 CFPS {year} {outcome} (age>={amin}): N_fam={r['n']}, "
          f"parent_ideology coef={r['coef'][1]:+.3f} p={r['p'][1]:.3f}")


def psm_rung3(res, year, df, outcome, amin, covars):
    d = df[df["age"] >= amin].dropna(subset=[outcome, "female"] + covars).copy()
    d["treat"] = d["female"]
    # overall ATT
    a = MM.psm_att(d, "treat", outcome, covars)
    res.append(dict(year=year, rung="3 PSM all families", outcome=outcome,
                    stratum="all", n_treated=a["n_treated"], att=round(a["att"], 4),
                    se=round(a["se"], 4), t=round(a["t"], 2), p=round(a["p"], 4)))
    # stratify by parent ideology (median split within wave)
    med = d["parent_mean"].median()
    for lab, mask in [("traditional", d["parent_mean"] >= med),
                      ("egalitarian", d["parent_mean"] < med)]:
        ds = d[mask]
        if (ds["treat"] == 1).sum() < 50 or (ds["treat"] == 0).sum() < 50:
            continue
        a = MM.psm_att(ds, "treat", outcome, [c for c in covars if c != "parent_mean"])
        res.append(dict(year=year, rung="3 PSM all families", outcome=outcome,
                        stratum=f"{lab}-parents", n_treated=a["n_treated"],
                        att=round(a["att"], 4), se=round(a["se"], 4),
                        t=round(a["t"], 2), p=round(a["p"], 4)))
    print(f"  R3 CFPS {year} {outcome}: overall ATT done + strata")


def interaction_test(resi, year, df, outcome, amin):
    """Formal moderation test: does parent ideology change the daughter-son gap?
    OLS outcome ~ female + parent_mean + female*parent_mean + age (+age^2 for eduy).
    The female_x_parent_mean coefficient (+ p-value) is the moderation effect."""
    d = df[df["age"] >= amin].dropna(subset=[outcome, "female", "parent_mean", "age"]).copy()
    d["age_c"] = (d["age"] - 30) / 10
    cols = {"const": 1.0, "female": d["female"], "parent_mean": d["parent_mean"],
            "female_x_parent_mean": d["female"] * d["parent_mean"], "age_c": d["age_c"]}
    if outcome == "eduy":
        cols["age_c2"] = d["age_c"] ** 2
    r = ST.ols(pd.DataFrame(cols), d[outcome].to_numpy())
    for term, c, se, t, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"]):
        resi.append(dict(year=year, outcome=outcome, n=r["n"], term=term,
                         coef=round(c, 4), se=round(se, 4), t=round(t, 2), p=round(p, 4)))
    j = r["term"].index("female_x_parent_mean")
    print(f"  INT CFPS {year} {outcome}: female*parent_mean={r['coef'][j]:+.3f} "
          f"p={r['p'][j]:.3f}")


def main() -> int:
    res2, res3, resi = [], [], []
    for year in WAVE:
        df = child_frame(year)
        gap_rung2(res2, year, df, "eduy", 25)
        gap_rung2(res2, year, df, "hw", 0)
        psm_rung3(res3, year, df, "eduy", 25, covars=["age", "parent_mean"])
        psm_rung3(res3, year, df, "hw", 0, covars=["age", "parent_mean"])
        interaction_test(resi, year, df, "eduy", 25)
        interaction_test(resi, year, df, "hw", 0)

    pd.DataFrame(res2).to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame(res3).to_csv(RUN / "psm_result_table.csv", index=False)
    pd.DataFrame(resi).to_csv(RUN / "interaction_test_table.csv", index=False)
    print("\nINTERACTION (female x parent_ideology), the moderation test:")
    idf = pd.DataFrame(resi)
    print(idf[idf.term == "female_x_parent_mean"][["year", "outcome", "coef", "se", "t", "p", "n"]].to_string(index=False))
    pd.DataFrame([dict(note="Rung2 = mean(daughters)-mean(sons) per mixed-gender family, "
                            "regressed on parent ideology (p-values reported). "
                            "Rung3 = PSM ATT of being a daughter, overall and by parent-"
                            "ideology stratum. eduy at age>=25; hw all ages.")]
                 ).to_csv(RUN / "02_missing_table.csv", index=False)
    print("\nRUNG 2:\n", pd.DataFrame(res2).to_string(index=False))
    print("\nRUNG 3 (PSM):\n", pd.DataFrame(res3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
