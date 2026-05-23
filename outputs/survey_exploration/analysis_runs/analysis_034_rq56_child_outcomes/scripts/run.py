#!/usr/bin/env python3
"""analysis_034 — RQ 5.6 parent ideation → adult child outcomes (deep).

For each (outcome, wave, sex_stratum):
  OLS-HC1: outcome ~ mother_id + father_id + child_female
                   + mother_id × child_female + father_id × child_female
                   + child controls + parent controls

Outcomes:
  family:    currently_married, housework_hours, marriage_sat,
             ideal_children (2014 only)
  work:      employed, log_wage_year, mgmt, isei (2020 only)
             (wage / mgmt / isei conditioned on employed == 1)
  education: edu_yrs

Frames: 2014 cross, 2020 cross (no lagged — dyad panel too small).
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
TABLES = RUN / "tables"
FIGS = RUN / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L           # noqa: E402
import cfps_panel as P             # noqa: E402
import cfps_outcomes as C          # noqa: E402
import stats_helpers as ST         # noqa: E402

import pyreadstat                  # noqa: E402

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


def _read_famconf(wave: str) -> pd.DataFrame:
    if wave == "2014":
        df, _ = pyreadstat.read_dta(
            str(L.ROOT / "surveys" / "CFPS" / "cfps2014_famconf.dta"),
            usecols=["pid", "pid_f", "pid_m", "fid14"])
        df = df.rename(columns={"pid_f": "father_pid",
                                  "pid_m": "mother_pid",
                                  "fid14": "fid"})
    else:
        df, _ = pyreadstat.read_dta(
            str(L.ROOT / "surveys" / "CFPS" / "cfps2020_famconf.dta"),
            usecols=["pid", "pid_a_f", "pid_a_m", "fid20"])
        df = df.rename(columns={"pid_a_f": "father_pid",
                                  "pid_a_m": "mother_pid",
                                  "fid20": "fid"})
    df = df.drop_duplicates(subset=["pid"], keep="first")
    df["father_pid"] = df["father_pid"].where(df["father_pid"] > 0)
    df["mother_pid"] = df["mother_pid"].where(df["mother_pid"] > 0)
    return df


def load_dyads(wave: str) -> pd.DataFrame:
    """Adult-respondent (child) frame with own outcomes + attached parent vars."""
    cfg = L.SURVEYS[("CFPS", wave)]
    extras = ["pid", "qea0",
              "cfps_birthy" if wave == "2014" else "ibirthy",
              cfg["gender_var"],
              "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im",
              "income" if wave == "2014" else "emp_income",
              "qa301",
              "qq9010" if wave == "2014" else "qq9010n",
              "qm801",
              "qm501" if wave == "2014" else "qg11",  # placeholder
              "employ2014" if wave == "2014" else "employ",
              "p_wage" if wave == "2014" else "emp_income",
              "qg14", "qg303code_isei" if wave == "2020" else "qg14"]
    extras = list(dict.fromkeys([c for c in extras if c not in cfg["items"]]))
    # 2020 needs an extra column; 2014 doesn't have ISEI / qg303code_isei
    if wave == "2020":
        extras = list(dict.fromkeys(extras + ["qg303code_isei"]))
    df, _m, _n, idx = L.load_recoded("CFPS", wave, extra_cols=extras)
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    yr = int(wave)
    birthy_col = "cfps_birthy" if wave == "2014" else "ibirthy"
    edu_col    = "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im"
    inc_col    = "income" if wave == "2014" else "emp_income"
    hw_col     = "qq9010" if wave == "2014" else "qq9010n"
    emp_col    = "employ2014" if wave == "2014" else "employ"
    wage_col   = "p_wage" if wave == "2014" else "emp_income"
    df["birthy"]  = pd.to_numeric(df[birthy_col], errors="coerce").where(
        lambda x: x.between(1920, 2010))
    df["age"]     = yr - df["birthy"]
    df["edu_yrs"] = pd.to_numeric(df[edu_col], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"]  = P._to_numeric_nan_sentinels(df[inc_col]).where(lambda x: x >= 0)
    df["log_income"]    = np.log1p(df["income"])
    df["currently_married"] = C.currently_married(df["qea0"])
    df["housework_hours"]   = C.housework_hours_daily(df[hw_col])
    df["marriage_sat"]      = C.clean_continuous(
        pd.to_numeric(df["qm801"], errors="coerce"), lo=1, hi=5)
    df["ideal_children"]    = (C.ideal_children_count(df["qm501"]) if wave == "2014"
                                else pd.Series(np.nan, index=df.index))
    df["employed"]          = C.employed(df[emp_col])
    df["log_wage_year"]     = np.log1p(C.clean_continuous(
        pd.to_numeric(df[wage_col], errors="coerce"), 0, 10_000_000))
    df["mgmt"]              = C.yes_no(pd.to_numeric(df["qg14"], errors="coerce"))
    df["isei"]              = (C.clean_continuous(
        pd.to_numeric(df["qg303code_isei"], errors="coerce"), 10, 90)
        if wave == "2020" else pd.Series(np.nan, index=df.index))
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0,
                            np.where(hk.isin([3, 7]), 1.0, np.nan))
    # parent attach
    fam = _read_famconf(wave)
    df = df.merge(fam, on="pid", how="left")
    lookup = df.set_index("pid")[["ideation", "edu_yrs", "log_income", "age"]]
    for parent, ptr in [("mother", "mother_pid"), ("father", "father_pid")]:
        for v in ["ideation", "edu_yrs", "log_income", "age"]:
            df[f"{parent}_{v}"] = df[ptr].map(lookup[v])
    df["parent_avg_age"]    = df[["mother_age", "father_age"]].mean(axis=1)
    df["parent_avg_edu"]    = df[["mother_edu_yrs", "father_edu_yrs"]].mean(axis=1)
    df["parent_log_income"] = df[["mother_log_income", "father_log_income"]].mean(axis=1)
    return df


OUTCOMES = {
    "currently_married": dict(continuous=False, employed_only=False, label="P(currently married)"),
    "housework_hours":   dict(continuous=True,  employed_only=False, label="Housework hr/day"),
    "marriage_sat":      dict(continuous=True,  employed_only=False, label="Marriage satisfaction (1-5)"),
    "ideal_children":    dict(continuous=True,  employed_only=False, label="Ideal children num (2014 only)"),
    "employed":          dict(continuous=False, employed_only=False, label="P(employed)"),
    "log_wage_year":     dict(continuous=True,  employed_only=True,  label="log(yearly wage + 1)"),
    "mgmt":              dict(continuous=False, employed_only=True,  label="P(management role)"),
    "isei":              dict(continuous=True,  employed_only=True,  label="ISEI prestige (2020 only)"),
    "edu_yrs":           dict(continuous=True,  employed_only=False, label="Years of education"),
}

CHILD_CONTROLS = ["age_c", "age_c2", "urban"]
PARENT_CONTROLS = ["parent_avg_age", "parent_avg_edu", "parent_log_income"]


def fit_outcome(df: pd.DataFrame, outcome: str, wave: str) -> pd.DataFrame:
    spec = OUTCOMES[outcome]
    if outcome not in df.columns or df[outcome].notna().sum() < 100:
        return pd.DataFrame()
    d = df.copy()
    if spec["employed_only"]:
        d = d[d["employed"] == 1]
    d["age_c"]  = (d["age"] - 35) / 10
    d["age_c2"] = d["age_c"] ** 2
    needed = [outcome, "mother_ideation", "father_ideation", "female"] + \
             CHILD_CONTROLS + PARENT_CONTROLS
    d = d.dropna(subset=needed)
    if len(d) < 100:
        return pd.DataFrame()
    rows = []
    for stratum, mask in [
        ("all", pd.Series(True, index=d.index)),
        ("male", d["female"] == 0),
        ("female", d["female"] == 1),
    ]:
        sub = d.loc[mask].copy()
        X = pd.DataFrame({
            "const":           1.0,
            "mother_ideation": sub["mother_ideation"].astype(float),
            "father_ideation": sub["father_ideation"].astype(float),
            "child_female":    sub["female"].astype(float),
            "age_c":           sub["age_c"].astype(float),
            "age_c2":          sub["age_c2"].astype(float),
            "urban":           sub["urban"].astype(float),
            "parent_avg_age":  sub["parent_avg_age"].astype(float),
            "parent_avg_edu":  sub["parent_avg_edu"].astype(float),
            "parent_log_income": sub["parent_log_income"].astype(float),
        })
        if stratum == "all":
            X["mother_id_x_female"] = X["mother_ideation"] * X["child_female"]
            X["father_id_x_female"] = X["father_ideation"] * X["child_female"]
        else:
            X = X.drop(columns=["child_female"])
        Xk = X.loc[:, [c for c in X.columns
                        if c == "const" or X[c].nunique(dropna=False) > 1]]
        if len(sub) < (Xk.shape[1] + 5):
            continue
        try:
            r = ST.ols_robust(Xk, sub[outcome].to_numpy(), kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"],
                                          r["t"], r["p"]):
            rows.append(dict(wave=wave, outcome=outcome, stratum=stratum,
                             n=int(r["n"]), term=term,
                             coef=round(float(coef), 5),
                             se=round(float(se), 5),
                             t=round(float(t), 3),
                             p=round(float(p), 5)))
    return pd.DataFrame(rows)


def descriptive(df: pd.DataFrame, wave: str) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        if outcome not in df.columns or df[outcome].notna().sum() < 50:
            continue
        d = df.copy()
        if OUTCOMES[outcome]["employed_only"]:
            d = d[d["employed"] == 1]
        for who in ("mother", "father"):
            col = f"{who}_ideation"
            if d[col].notna().sum() < 50:
                continue
            q = d[col].quantile([1 / 3, 2 / 3]).values
            d["__t"] = pd.cut(d[col], [-np.inf, q[0], q[1], np.inf],
                                labels=["low", "mid", "high"])
            for t in ("low", "mid", "high"):
                for sex_name, sex_val in [("daughter", 1), ("son", 0)]:
                    sub = d.loc[(d["__t"] == t) & (d["female"] == sex_val), outcome]
                    if sub.notna().sum() < 20:
                        continue
                    rows.append(dict(wave=wave, outcome=outcome, parent=who,
                                     parent_id_tertile=t, child=sex_name,
                                     n=int(sub.notna().sum()),
                                     mean=round(float(sub.mean()), 4),
                                     sd=round(float(sub.std(ddof=1)), 4)))
    return pd.DataFrame(rows)


def fig_summary_forest(results: pd.DataFrame, out_pdf: Path):
    sub = results[results["term"].isin(["mother_ideation", "father_ideation"])
                   & (results["stratum"] != "all")].copy()
    if sub.empty:
        return
    sub["label"] = sub.apply(
        lambda r: f"[{r['wave']}] {r['outcome']} · {r['term']} · {r['stratum']} (n={r['n']})",
        axis=1)
    sub = sub.sort_values(["outcome", "wave", "term", "stratum"])
    rows = list(zip(sub["coef"], sub["se"], sub["label"]))
    fig, ax = plt.subplots(figsize=(8.2, 0.24 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=6.5)
    ax.set_xlabel("OLS β on parent ideation (HC1, 95 % CI; outcome on its own scale)")
    ax.set_title("Parent ideation → adult child outcomes\n(sex-stratified summary)")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_per_outcome_forest(results: pd.DataFrame, outcome: str, out_pdf: Path):
    sub = results[(results["outcome"] == outcome) &
                   (results["term"].isin(["mother_ideation", "father_ideation"]))
                   & (results["stratum"] != "all")].copy()
    if sub.empty:
        return
    sub["label"] = sub.apply(
        lambda r: f"[{r['wave']}] {r['term']} · {r['stratum']} (n={r['n']})", axis=1)
    sub = sub.sort_values(["wave", "term", "stratum"])
    rows = list(zip(sub["coef"], sub["se"], sub["label"]))
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(rows) + 1.4))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=7.5)
    label = OUTCOMES[outcome]["label"]
    ax.set_xlabel(f"OLS β on parent ideation (HC1, 95 % CI)")
    ax.set_title(f"Parent ideation → {label}")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def main() -> int:
    all_results, all_desc, miss_rows = [], [], []
    for wave in ("2014", "2020"):
        print(f"loading {wave} dyads + outcomes …")
        df = load_dyads(wave)
        n_dyad = int(df[["mother_ideation", "father_ideation"]].notna().all(axis=1).sum())
        print(f"  n_adults = {len(df)}; full dyads = {n_dyad}")
        all_desc.append(descriptive(df, wave))
        miss_rows.append(dict(wave=wave, n_adults=len(df),
                              n_dyads=n_dyad,
                              n_employed=int(df["employed"].eq(1).sum())))
        for outcome in OUTCOMES:
            all_results.append(fit_outcome(df, outcome, wave))

    desc_all = pd.concat(all_desc, ignore_index=True)
    desc_all.to_csv(RUN / "01_descriptive_table.csv", index=False)
    res_all = pd.concat([r for r in all_results if not r.empty],
                          ignore_index=True)
    res_all.to_csv(RUN / "04_result_table.csv", index=False)
    pd.DataFrame(miss_rows).to_csv(RUN / "02_missing_table.csv", index=False)
    print("tables written.")

    fig_summary_forest(res_all, FIGS / "summary_forest_parent_to_child.pdf")
    for outcome in OUTCOMES:
        fig_per_outcome_forest(res_all, outcome,
                                 FIGS / f"forest_{outcome}.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
