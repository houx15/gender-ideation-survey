#!/usr/bin/env python3
"""analysis_027 — RQ 5.3 work / leadership outcomes (deep, dual-frame).

Outcomes (CFPS):
  - employed        (employ / employ2014)        binary, full sample
  - log_wage_month  (log1p qg11)                 main monthly wage, employed only
  - log_wage_year   (log1p emp_income / p_wage)  yearly total, employed only
  - mgmt            (qg14)                       binary, employed only
  - promotion       (qg15 -> {1,2,3}=1; {78,79}=0)  binary, employed only
  - has_sub         (qg17)                       binary, employed only
  - bianzhi         (qg2032, 2020 only)          binary, employed only
  - isei            (qg303code_isei, 2020 only)  continuous prestige, employed only

Each estimated:
  (A) 2014 cross-section
  (B) 2020 cross-section
  (C) lagged panel: ideation_2014 -> outcome_2020 (+ outcome_2014 if available)

Stratified overall / male / female; HC1 robust SEs everywhere.
Controls: female (overall), age_c=(age-40)/10, age_c2, urban (hukou),
edu_yrs, log_income (per-wave).

Wage / mgmt / promotion / sub / bianzhi / isei models condition on
`employed == 1` (selection caveat in 03_method_note).

All tables CSV, all figures vector PDF (pdf.fonttype=42).
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sps

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


# ------------------------------------------------------------------ #
# 0. Loaders
# ------------------------------------------------------------------ #

def load_2014_cross() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2014")]
    extras = ["employ2014", "qg11", "p_wage",
              "qg14", "qg15", "qg17", "income", "qa301",
              "cfps_birthy", "cfps2014eduy_im", cfg["gender_var"], "pid"]
    df, _meta, norm_cols, idx = L.load_recoded(
        "CFPS", "2014", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"] = pd.to_numeric(df["cfps_birthy"], errors="coerce").where(
        lambda x: x.between(1920, 2007))
    df["age"] = 2014 - df["birthy"]
    df["employed"]       = C.employed(df["employ2014"])
    df["log_wage_month"] = np.log1p(C.clean_continuous(
        pd.to_numeric(df["qg11"], errors="coerce"), 0, 1_000_000))
    df["log_wage_year"]  = np.log1p(C.clean_continuous(
        pd.to_numeric(df["p_wage"], errors="coerce"), 0, 10_000_000))
    df["mgmt"]           = C.yes_no(pd.to_numeric(df["qg14"], errors="coerce"))
    df["promotion"]      = C.promotion_indicator(df["qg15"])
    df["has_sub"]        = C.yes_no(pd.to_numeric(df["qg17"], errors="coerce"))
    df["bianzhi"]        = np.nan
    df["isei"]           = np.nan
    df["edu_yrs"] = pd.to_numeric(df["cfps2014eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"]    = P._to_numeric_nan_sentinels(df["income"]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk == 3, 1.0, np.nan))
    return df


def load_2020_cross() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2020")]
    extras = ["employ", "qg11", "emp_income",
              "qg14", "qg15", "qg17", "qg2032",
              "qg303code_isei",
              "ibirthy", "cfps2020eduy_im", "qa301", cfg["gender_var"], "pid"]
    df, _meta, norm_cols, idx = L.load_recoded(
        "CFPS", "2020", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"] = pd.to_numeric(df["ibirthy"], errors="coerce").where(
        lambda x: x.between(1920, 2010))
    df["age"] = 2020 - df["birthy"]
    df["employed"]       = C.employed(df["employ"])
    df["log_wage_month"] = np.log1p(C.clean_continuous(
        pd.to_numeric(df["qg11"], errors="coerce"), 0, 1_000_000))
    df["log_wage_year"]  = np.log1p(C.clean_continuous(
        pd.to_numeric(df["emp_income"], errors="coerce"), 0, 10_000_000))
    df["mgmt"]           = C.yes_no(pd.to_numeric(df["qg14"], errors="coerce"))
    df["promotion"]      = C.promotion_indicator(df["qg15"])
    df["has_sub"]        = C.yes_no(pd.to_numeric(df["qg17"], errors="coerce"))
    df["bianzhi"]        = C.yes_no(pd.to_numeric(df["qg2032"], errors="coerce"))
    df["isei"]           = C.clean_continuous(
        pd.to_numeric(df["qg303code_isei"], errors="coerce"), 10, 90)
    df["edu_yrs"] = pd.to_numeric(df["cfps2020eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"]    = P._to_numeric_nan_sentinels(df["emp_income"]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk.isin([3, 7]), 1.0, np.nan))
    return df


def load_panel() -> pd.DataFrame:
    """Lagged frame: panel members + 2020 outcomes + 2014 baseline outcomes."""
    p = P.build_panel().copy()
    cfg14 = L.SURVEYS[("CFPS", "2014")]
    cfg20 = L.SURVEYS[("CFPS", "2020")]
    extra14, _ = pyreadstat.read_dta(
        str(L.ROOT / cfg14["file"]),
        usecols=["pid", "qg11", "p_wage", "qg14", "qg15", "qg17"])
    extra14["log_wage_month_2014"] = np.log1p(C.clean_continuous(
        pd.to_numeric(extra14["qg11"], errors="coerce"), 0, 1_000_000))
    extra14["log_wage_year_2014"]  = np.log1p(C.clean_continuous(
        pd.to_numeric(extra14["p_wage"], errors="coerce"), 0, 10_000_000))
    extra14["mgmt_2014"]      = C.yes_no(pd.to_numeric(extra14["qg14"], errors="coerce"))
    extra14["promotion_2014"] = C.promotion_indicator(extra14["qg15"])
    extra14["has_sub_2014"]   = C.yes_no(pd.to_numeric(extra14["qg17"], errors="coerce"))
    extra14 = extra14.drop_duplicates(subset=["pid"], keep="first")
    extra20, _ = pyreadstat.read_dta(
        str(L.ROOT / cfg20["file"]),
        usecols=["pid", "qg11", "emp_income", "qg14", "qg15", "qg17",
                 "qg2032", "qg303code_isei"])
    extra20["log_wage_month_2020"] = np.log1p(C.clean_continuous(
        pd.to_numeric(extra20["qg11"], errors="coerce"), 0, 1_000_000))
    extra20["log_wage_year_2020"]  = np.log1p(C.clean_continuous(
        pd.to_numeric(extra20["emp_income"], errors="coerce"), 0, 10_000_000))
    extra20["mgmt_2020"]      = C.yes_no(pd.to_numeric(extra20["qg14"], errors="coerce"))
    extra20["promotion_2020"] = C.promotion_indicator(extra20["qg15"])
    extra20["has_sub_2020"]   = C.yes_no(pd.to_numeric(extra20["qg17"], errors="coerce"))
    extra20["bianzhi_2020"]   = C.yes_no(pd.to_numeric(extra20["qg2032"], errors="coerce"))
    extra20["isei_2020"]      = C.clean_continuous(
        pd.to_numeric(extra20["qg303code_isei"], errors="coerce"), 10, 90)
    extra20 = extra20.drop_duplicates(subset=["pid"], keep="first")
    p = p.merge(extra14[["pid", "log_wage_month_2014", "log_wage_year_2014",
                          "mgmt_2014", "promotion_2014", "has_sub_2014"]],
                on="pid", how="left")
    p = p.merge(extra20[["pid", "log_wage_month_2020", "log_wage_year_2020",
                          "mgmt_2020", "promotion_2020", "has_sub_2020",
                          "bianzhi_2020", "isei_2020"]], on="pid", how="left")
    # employed_2014/2020 already in panel as 0/1.
    p["log_income_2014"] = np.log1p(p["income_2014"])
    return p


# ------------------------------------------------------------------ #
# 1. Welch / tertile helpers (copied conventions from 026)
# ------------------------------------------------------------------ #

def welch(y: pd.Series, group: pd.Series, hi="high", lo="low") -> dict:
    a = y[group == hi].dropna().to_numpy()
    b = y[group == lo].dropna().to_numpy()
    if len(a) < 2 or len(b) < 2:
        return dict(n_hi=len(a), n_lo=len(b), diff=np.nan, t=np.nan, p=np.nan,
                    d=np.nan)
    t, p = sps.ttest_ind(a, b, equal_var=False)
    pooled = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                     / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan
    return dict(n_hi=int(len(a)), n_lo=int(len(b)),
                diff=float(a.mean() - b.mean()),
                t=float(t), p=float(p), d=float(d))


def tertile(s: pd.Series) -> pd.Series:
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


# ------------------------------------------------------------------ #
# 2. Outcome spec
# ------------------------------------------------------------------ #

# Outcomes that require employed == 1
EMPLOYED_ONLY = {"log_wage_month", "log_wage_year", "mgmt", "promotion",
                 "has_sub", "bianzhi", "isei"}

OUTCOMES_CROSS = {
    "employed":       dict(label="Employed", continuous=False),
    "log_wage_month": dict(label="log(monthly wage + 1)", continuous=True),
    "log_wage_year":  dict(label="log(yearly wage + 1)",  continuous=True),
    "mgmt":           dict(label="Management role",       continuous=False),
    "promotion":      dict(label="Promotion (qg15 1/2/3)", continuous=False),
    "has_sub":        dict(label="Has subordinate",        continuous=False),
    "bianzhi":        dict(label="Has bianzhi (2020 only)", continuous=False),
    "isei":           dict(label="Occupation ISEI (2020 only)", continuous=True),
}

OUTCOMES_LAGGED = {
    "employed_2020":        dict(baseline="employed_2014",  continuous=False),
    "log_wage_month_2020":  dict(baseline="log_wage_month_2014",  continuous=True),
    "log_wage_year_2020":   dict(baseline="log_wage_year_2014",   continuous=True),
    "mgmt_2020":            dict(baseline="mgmt_2014",      continuous=False),
    "promotion_2020":       dict(baseline="promotion_2014", continuous=False),
    "has_sub_2020":         dict(baseline="has_sub_2014",   continuous=False),
    "bianzhi_2020":         dict(baseline=None,             continuous=False),
    "isei_2020":            dict(baseline=None,             continuous=True),
}


# ------------------------------------------------------------------ #
# 3. Tables: descriptive + missing
# ------------------------------------------------------------------ #

def descriptive_table(df14, df20, panel) -> pd.DataFrame:
    rows = []
    for tag, df, idcol, outcomes in [
        ("2014_cross", df14, "ideation", list(OUTCOMES_CROSS)),
        ("2020_cross", df20, "ideation", list(OUTCOMES_CROSS)),
        ("panel_2014_baseline", panel, "ideation_2014",
         list(OUTCOMES_LAGGED.keys())),
    ]:
        d = df.copy()
        d["__t"] = tertile(d[idcol])
        for outcome in outcomes:
            if outcome not in d.columns:
                continue
            # Restrict to employed where required
            base_mask = pd.Series(True, index=d.index)
            if outcome.replace("_2020", "") in EMPLOYED_ONLY:
                emp_col = ("employed_2020" if "_2020" in outcome and "employed_2020" in d.columns
                           else "employed" if "employed" in d.columns
                           else None)
                if emp_col is not None:
                    base_mask = (d[emp_col] == 1)
            for stratum_name, mask in [
                ("all", base_mask),
                ("male", base_mask & (d["female"] == 0)),
                ("female", base_mask & (d["female"] == 1)),
            ]:
                g = d.loc[mask].dropna(subset=[outcome, "__t"])
                for t in ["low", "mid", "high"]:
                    sub = g.loc[g["__t"] == t, outcome]
                    rows.append(dict(
                        frame=tag, outcome=outcome, stratum=stratum_name,
                        ideation_tertile=t,
                        n=int(sub.notna().sum()),
                        mean=round(float(sub.mean()), 4) if sub.notna().any() else np.nan,
                        sd=round(float(sub.std(ddof=1)), 4) if sub.notna().sum() > 1 else np.nan,
                    ))
    return pd.DataFrame(rows)


def missing_table(df14, df20, panel) -> pd.DataFrame:
    rows = []
    for tag, df, cols in [
        ("2014_cross", df14, list(OUTCOMES_CROSS)),
        ("2020_cross", df20, list(OUTCOMES_CROSS)),
        ("panel", panel, list(OUTCOMES_LAGGED.keys())),
    ]:
        for c in cols:
            if c not in df.columns:
                continue
            s = df[c]
            rows.append(dict(frame=tag, variable=c, n_total=len(df),
                             n_nonmissing=int(s.notna().sum()),
                             pct_coverage=round(100 * s.notna().mean(), 2)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 4. OLS / LPM machinery (copied from 026)
# ------------------------------------------------------------------ #

CONTROLS_CROSS = ["female", "age_c", "age_c2", "urban", "edu_yrs", "log_income"]
CONTROLS_LAGGED = ["female", "age_c14", "age_c14_2", "urban_2014",
                   "edu_yrs_2014", "log_income_2014"]

# Drop log_income from controls for outcomes that *are* wages — they're
# near-perfectly collinear with total income in CFPS (wages are most of income
# for most respondents).
WAGE_OUTCOMES = {"log_wage_month", "log_wage_year",
                 "log_wage_month_2020", "log_wage_year_2020"}


def _controls_for_outcome(controls: list[str], outcome: str) -> list[str]:
    if outcome in WAGE_OUTCOMES:
        return [c for c in controls if not c.startswith("log_income")]
    return controls


def _design_cross(df, idcol, fcol, controls, interact):
    d = df.copy()
    d["age_c"] = (d["age"] - 40) / 10
    d["age_c2"] = d["age_c"] ** 2
    d = d.rename(columns={idcol: "ideation"})
    if fcol != "female":
        d["female"] = d[fcol]
    X = pd.DataFrame({"const": 1.0, "ideation": d["ideation"].astype(float)})
    for c in controls:
        X[c] = d[c].astype(float)
    if interact:
        X["ideation_x_female"] = X["ideation"] * X["female"]
    return X, d


def _design_lagged(panel, controls, interact, baseline_outcome_col):
    d = panel.copy()
    d["age_c14"] = (d["age_2014"] - 40) / 10
    d["age_c14_2"] = d["age_c14"] ** 2
    X = pd.DataFrame({"const": 1.0, "ideation": d["ideation_2014"].astype(float)})
    for c in controls:
        X[c] = d[c].astype(float)
    if interact:
        X["ideation_x_female"] = X["ideation"] * X["female"]
    if baseline_outcome_col is not None and baseline_outcome_col in d.columns:
        X[baseline_outcome_col] = d[baseline_outcome_col].astype(float)
    return X, d


def fit_outcome(X, y, stratum_mask):
    keep = stratum_mask & y.notna() & X.notna().all(axis=1)
    Xk = X.loc[keep].copy()
    yk = y.loc[keep].to_numpy()
    drop_cols = [c for c in Xk.columns if c != "const" and Xk[c].nunique(dropna=False) <= 1]
    if drop_cols:
        Xk = Xk.drop(columns=drop_cols)
    if len(Xk) < (Xk.shape[1] + 2):
        return {"n": int(len(Xk)), "results": []}
    try:
        r = ST.ols_robust(Xk, yk, kind="HC1")
    except np.linalg.LinAlgError:
        return {"n": int(len(Xk)), "results": [], "note": "singular"}
    return {"n": int(r["n"]),
            "results": [dict(term=t, coef=float(c), se=float(s), t=float(tt), p=float(p))
                        for t, c, s, tt, p in
                        zip(r["term"], r["coef"], r["se"], r["t"], r["p"])]}


# ------------------------------------------------------------------ #
# 5. Driver fits
# ------------------------------------------------------------------ #

def fit_all(df14, df20, panel) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows_main, rows_welch = [], []
    cross_frames = [("2014_cross", df14, "ideation", "female"),
                    ("2020_cross", df20, "ideation", "female")]
    for tag, df, idcol, fcol in cross_frames:
        for outcome, spec in OUTCOMES_CROSS.items():
            if outcome not in df.columns or df[outcome].notna().sum() < 50:
                continue
            # At-risk pool for employed-only outcomes
            base_mask = (df["employed"] == 1) if outcome in EMPLOYED_ONLY else \
                        pd.Series(True, index=df.index)
            X, d = _design_cross(df, idcol=idcol, fcol=fcol,
                                 controls=_controls_for_outcome(CONTROLS_CROSS, outcome),
                                 interact=True)
            y = d[outcome]
            d["__t"] = tertile(d[idcol])
            for stratum_name, mask in [
                ("all", base_mask),
                ("male", base_mask & (d[fcol] == 0)),
                ("female", base_mask & (d[fcol] == 1)),
            ]:
                w = welch(d.loc[mask, outcome], d.loc[mask, "__t"])
                rows_welch.append(dict(frame=tag, outcome=outcome,
                                       stratum=stratum_name, **w))
                Xs = (X.drop(columns=[c for c in ("ideation_x_female", "female")
                                       if c in X.columns])
                      if stratum_name != "all" else X)
                fit = fit_outcome(Xs, y, mask)
                for r in fit["results"]:
                    rows_main.append(dict(frame=tag, outcome=outcome,
                                          stratum=stratum_name, n=fit["n"],
                                          term=r["term"], coef=round(r["coef"], 5),
                                          se=round(r["se"], 5), t=round(r["t"], 3),
                                          p=round(r["p"], 5)))
    # Lagged
    for outcome, spec in OUTCOMES_LAGGED.items():
        if outcome not in panel.columns or panel[outcome].notna().sum() < 50:
            continue
        baseline = spec.get("baseline")
        base_mask = (panel["employed_2020"] == 1) if \
            outcome.replace("_2020", "") in EMPLOYED_ONLY else \
            pd.Series(True, index=panel.index)
        X, d = _design_lagged(panel,
                              controls=_controls_for_outcome(CONTROLS_LAGGED, outcome),
                              interact=True, baseline_outcome_col=baseline)
        y = d[outcome]
        d["__t"] = tertile(d["ideation_2014"])
        for stratum_name, mask in [
            ("all", base_mask),
            ("male", base_mask & (d["female"] == 0)),
            ("female", base_mask & (d["female"] == 1)),
        ]:
            w = welch(d.loc[mask, outcome], d.loc[mask, "__t"])
            rows_welch.append(dict(frame="lagged_2014to2020", outcome=outcome,
                                   stratum=stratum_name, **w))
            Xs = (X.drop(columns=[c for c in ("ideation_x_female", "female")
                                   if c in X.columns])
                  if stratum_name != "all" else X)
            fit = fit_outcome(Xs, y, mask)
            for r in fit["results"]:
                rows_main.append(dict(frame="lagged_2014to2020", outcome=outcome,
                                      stratum=stratum_name, n=fit["n"],
                                      term=r["term"], coef=round(r["coef"], 5),
                                      se=round(r["se"], 5), t=round(r["t"], 3),
                                      p=round(r["p"], 5)))
    return pd.DataFrame(rows_main), pd.DataFrame(rows_welch)


# ------------------------------------------------------------------ #
# 6. Figures
# ------------------------------------------------------------------ #

def fig_outcome_by_tertile(df, idcol, fcol, outcome, label, out_pdf, tag,
                            base_mask=None):
    d = df.copy()
    if base_mask is not None:
        d = d.loc[base_mask]
    d["__t"] = tertile(d[idcol])
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    width = 0.36
    x = np.arange(3)
    male_means, male_se = [], []
    fem_means, fem_se = [], []
    for t in ["low", "mid", "high"]:
        m = d.loc[(d[fcol] == 0) & (d["__t"] == t), outcome].dropna()
        f = d.loc[(d[fcol] == 1) & (d["__t"] == t), outcome].dropna()
        male_means.append(m.mean()); male_se.append(m.std(ddof=1)/np.sqrt(len(m)) if len(m) > 1 else 0)
        fem_means.append(f.mean()); fem_se.append(f.std(ddof=1)/np.sqrt(len(f)) if len(f) > 1 else 0)
    ax.bar(x - width/2, male_means, width=width, color="#1f77b4", label="Male",
           yerr=male_se, capsize=3)
    ax.bar(x + width/2, fem_means, width=width, color="#d62728", label="Female",
           yerr=fem_se, capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["Low (progressive)", "Mid", "High (traditional)"])
    ax.set_ylabel(label)
    ax.set_title(f"{label}\n({tag}, ideation tertile × sex)")
    ax.legend(frameon=False)
    ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_coef_forest(results, term, frame, title, out_pdf):
    sub = results[(results["frame"] == frame) & (results["term"] == term)].copy()
    if sub.empty:
        return
    sub = sub.sort_values(["outcome", "stratum"])
    rows = list(zip(sub["coef"], sub["se"],
                    [f"{r['outcome']} · {r['stratum']} (n={r['n']})" for _, r in sub.iterrows()]))
    fig, ax = plt.subplots(figsize=(7.0, 0.30 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[2] for r in rows], fontsize=7.5)
    ax.set_xlabel(f"β on {term}  (HC1, 95 % CI)")
    ax.set_title(title)
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


# ------------------------------------------------------------------ #
# 7. Driver
# ------------------------------------------------------------------ #

def main() -> int:
    print("loading 2014 cross-section …")
    df14 = load_2014_cross()
    print(f"  n = {len(df14)}; employed = {int(df14['employed'].eq(1).sum())}")
    print("loading 2020 cross-section …")
    df20 = load_2020_cross()
    print(f"  n = {len(df20)}; employed = {int(df20['employed'].eq(1).sum())}")
    print("loading panel (lagged) …")
    panel = load_panel()
    print(f"  n = {len(panel)}")

    desc = descriptive_table(df14, df20, panel)
    desc.to_csv(RUN / "01_descriptive_table.csv", index=False)
    miss = missing_table(df14, df20, panel)
    miss.to_csv(RUN / "02_missing_table.csv", index=False)
    main_tab, welch_tab = fit_all(df14, df20, panel)
    main_tab.to_csv(RUN / "04_result_table.csv", index=False)
    welch_tab.to_csv(TABLES / "welch_tertile_diffs.csv", index=False)
    print("tables written.")

    # Figures: by-tertile for each outcome; conditioned on employed where needed
    figures_spec = [
        ("employed",       df14, "CFPS 2014", None),
        ("employed",       df20, "CFPS 2020", None),
        ("log_wage_month", df14, "CFPS 2014 (employed)", df14["employed"] == 1),
        ("log_wage_month", df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("log_wage_year",  df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("mgmt",           df14, "CFPS 2014 (employed)", df14["employed"] == 1),
        ("mgmt",           df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("promotion",      df14, "CFPS 2014 (employed)", df14["employed"] == 1),
        ("promotion",      df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("has_sub",        df14, "CFPS 2014 (employed)", df14["employed"] == 1),
        ("has_sub",        df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("bianzhi",        df20, "CFPS 2020 (employed)", df20["employed"] == 1),
        ("isei",           df20, "CFPS 2020 (employed)", df20["employed"] == 1),
    ]
    for outcome, df, tag, mask in figures_spec:
        if outcome not in df.columns or df[outcome].notna().sum() < 50:
            continue
        slug = tag.split()[1].lower().replace("(", "").replace(")", "")  # 2014/2020
        fig_outcome_by_tertile(df, "ideation", "female", outcome,
                               OUTCOMES_CROSS[outcome]["label"],
                               FIGS / f"{outcome}_by_tertile_{slug}.pdf", tag, mask)

    fig_coef_forest(main_tab, "ideation", "2014_cross",
                    "OLS β on ideation — CFPS 2014",
                    FIGS / "coef_forest_ideation_2014.pdf")
    fig_coef_forest(main_tab, "ideation", "2020_cross",
                    "OLS β on ideation — CFPS 2020",
                    FIGS / "coef_forest_ideation_2020.pdf")
    fig_coef_forest(main_tab, "ideation", "lagged_2014to2020",
                    "OLS β on ideation_2014 — CFPS lagged 2014→2020",
                    FIGS / "coef_forest_ideation_lagged.pdf")
    fig_coef_forest(main_tab, "ideation_x_female", "2014_cross",
                    "Gender-moderation: β on ideation×female (CFPS 2014)",
                    FIGS / "coef_forest_interaction_2014.pdf")
    fig_coef_forest(main_tab, "ideation_x_female", "2020_cross",
                    "Gender-moderation: β on ideation×female (CFPS 2020)",
                    FIGS / "coef_forest_interaction_2020.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
