#!/usr/bin/env python3
"""analysis_026 v2 — RQ 5.2 individual-level family outcomes (deep, enriched).

v1 outcomes (CFPS):
  - currently_married   (qea0 == 2)
  - first_marriage_age  (qea205y - birthy)        retrospective
  - ideal_children      (qm501, 2014 only)
  - housework_hours     (qq9010 / qq9010n)        hours/day

v2 additions (user-supplied list, 2026-05-23):
  - ideal_marriage_age  (qka201,  2020 only)      理想结婚年龄
  - birth_intention_2y  (qka205,  2020 only)      未来两年生育意愿 (binary)
  - marriage_sat        (qm801,   both waves)     婚姻满意度 (Likert 1-5)
  - cohab_experience    (eeb501,  both waves)     同居经历 (binary)
  - childcare_hours     (qq9013,  2020 only)      照顾孩子时长 (hours/day)

Each outcome estimated:
  (A) 2014 cross-section (where available)
  (B) 2020 cross-section (where available)
  (C) lagged panel: ideation_2014 -> outcome_2020 (where both waves exist)

Each fit stratified to (overall, male, female).

Methods:
  - Welch's t-test on outcome by top vs bottom ideation tertile, per sex stratum.
  - OLS (continuous) / LPM (binary) with HC1 robust SEs.
  - Lagged-continuous fit puts outcome_2014 on RHS so the coefficient on
    ideation_2014 is interpreted as predicting the *change*.
  - Controls: female (overall only), age_c=(age-40)/10, age_c2, urban (hukou),
    edu_yrs, log_income.

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
from matplotlib.backends.backend_pdf import PdfPages
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

# matplotlib defaults
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


# ------------------------------------------------------------------ #
# 0. Loaders for the three "frames"
# ------------------------------------------------------------------ #

def load_2014_cross() -> pd.DataFrame:
    """Full 2014 adult cross-section with ideation index + outcome variables."""
    cfg = L.SURVEYS[("CFPS", "2014")]
    extras = ["qea0", "qea205y", "qea2071", "qm501", "qq9010",
              "qm801", "eeb501",
              "cfps_birthy", "cfps2014eduy_im", "income", "qa301",
              "employ2014", cfg["gender_var"], "pid"]
    df, _meta, norm_cols, idx = L.load_recoded(
        "CFPS", "2014", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"] = pd.to_numeric(df["cfps_birthy"], errors="coerce").where(
        lambda x: x.between(1920, 2007))
    df["age"] = 2014 - df["birthy"]
    df["currently_married"] = C.currently_married(df["qea0"])
    # restrict first-marriage age to first-marriage subset where flagged.
    is_first = (pd.to_numeric(df["qea2071"], errors="coerce") == 1)
    df["first_marriage_age"] = C.first_marriage_age(df["qea205y"], df["birthy"])
    df.loc[~is_first & df["qea2071"].notna(), "first_marriage_age"] = np.nan
    df["ideal_children"] = C.ideal_children_count(df["qm501"])
    df["housework_hours"] = C.housework_hours_daily(df["qq9010"])
    # v2 additions available in 2014: qm801 (1-5 Likert), eeb501 (yes/no).
    df["marriage_sat"] = C.clean_continuous(
        pd.to_numeric(df["qm801"], errors="coerce"), lo=1, hi=5)
    df["cohab_experience"] = C.yes_no(pd.to_numeric(df["eeb501"], errors="coerce"))
    # v2 additions NOT available in 2014: keep as NaN columns so downstream
    # generic loops can address them uniformly.
    df["ideal_marriage_age"] = np.nan
    df["birth_intention_2y"] = np.nan
    df["childcare_hours"]    = np.nan
    df["edu_yrs"] = pd.to_numeric(df["cfps2014eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"] = P._to_numeric_nan_sentinels(df["income"]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk == 3, 1.0, np.nan))
    return df


def load_2020_cross() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2020")]
    extras = ["qea0", "qea205y", "qea2071", "qq9010n",
              "qka201", "qka205", "qm801", "eeb501", "qq9013",
              "ibirthy", "cfps2020eduy_im", "emp_income", "qa301",
              "employ", cfg["gender_var"], "pid"]
    df, _meta, norm_cols, idx = L.load_recoded(
        "CFPS", "2020", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"] = pd.to_numeric(df["ibirthy"], errors="coerce").where(
        lambda x: x.between(1920, 2010))
    df["age"] = 2020 - df["birthy"]
    df["currently_married"] = C.currently_married(df["qea0"])
    is_first = (pd.to_numeric(df["qea2071"], errors="coerce") == 1)
    df["first_marriage_age"] = C.first_marriage_age(df["qea205y"], df["birthy"])
    df.loc[~is_first & df["qea2071"].notna(), "first_marriage_age"] = np.nan
    df["ideal_children"] = pd.Series(np.nan, index=df.index)  # not asked in 2020
    df["housework_hours"] = C.housework_hours_daily(df["qq9010n"])
    # v2 additions
    df["ideal_marriage_age"] = C.clean_continuous(
        pd.to_numeric(df["qka201"], errors="coerce"), lo=15, hi=50)
    df["birth_intention_2y"] = C.yes_no(pd.to_numeric(df["qka205"], errors="coerce"))
    df["marriage_sat"] = C.clean_continuous(
        pd.to_numeric(df["qm801"], errors="coerce"), lo=1, hi=5)
    df["cohab_experience"] = C.yes_no(pd.to_numeric(df["eeb501"], errors="coerce"))
    df["childcare_hours"] = C.housework_hours_daily(df["qq9013"])
    df["edu_yrs"] = pd.to_numeric(df["cfps2020eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"] = P._to_numeric_nan_sentinels(df["emp_income"]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk.isin([3, 7]), 1.0, np.nan))
    return df


def load_panel() -> pd.DataFrame:
    """Lagged frame: panel members, with 2014 covariates + 2020 outcomes.

    For v2, also attaches qm801 (婚姻满意度) and eeb501 (同居经历) on both waves
    (so lagged frame has these two new outcomes), and qq9013 + qka201 + qka205
    on 2020 only.
    """
    p = P.build_panel().copy()
    cfg20 = L.SURVEYS[("CFPS", "2020")]
    cfg14 = L.SURVEYS[("CFPS", "2014")]
    # 2020 extras
    extra20, _ = pyreadstat.read_dta(
        str(L.ROOT / cfg20["file"]),
        usecols=["pid", "qq9010n", "qq9013", "qm801", "eeb501",
                 "qka201", "qka205"])
    extra20["housework_2020"]          = C.housework_hours_daily(extra20["qq9010n"])
    extra20["childcare_hours_2020"]    = C.housework_hours_daily(extra20["qq9013"])
    extra20["marriage_sat_2020"]       = C.clean_continuous(
        pd.to_numeric(extra20["qm801"], errors="coerce"), lo=1, hi=5)
    extra20["cohab_experience_2020"]   = C.yes_no(
        pd.to_numeric(extra20["eeb501"], errors="coerce"))
    extra20["ideal_marriage_age_2020"] = C.clean_continuous(
        pd.to_numeric(extra20["qka201"], errors="coerce"), lo=15, hi=50)
    extra20["birth_intention_2y_2020"] = C.yes_no(
        pd.to_numeric(extra20["qka205"], errors="coerce"))
    extra20 = extra20.drop_duplicates(subset=["pid"], keep="first")
    # 2014 extras
    extra14, _ = pyreadstat.read_dta(
        str(L.ROOT / cfg14["file"]),
        usecols=["pid", "qq9010", "qm501", "qm801", "eeb501"])
    extra14["housework_2014"]        = C.housework_hours_daily(extra14["qq9010"])
    extra14["ideal_children_2014"]   = C.ideal_children_count(extra14["qm501"])
    extra14["marriage_sat_2014"]     = C.clean_continuous(
        pd.to_numeric(extra14["qm801"], errors="coerce"), lo=1, hi=5)
    extra14["cohab_experience_2014"] = C.yes_no(
        pd.to_numeric(extra14["eeb501"], errors="coerce"))
    extra14 = extra14.drop_duplicates(subset=["pid"], keep="first")
    p = p.merge(extra20[["pid", "housework_2020", "childcare_hours_2020",
                         "marriage_sat_2020", "cohab_experience_2020",
                         "ideal_marriage_age_2020", "birth_intention_2y_2020"]],
                on="pid", how="left")
    p = p.merge(extra14[["pid", "housework_2014", "ideal_children_2014",
                         "marriage_sat_2014", "cohab_experience_2014"]],
                on="pid", how="left")
    # Derived: currently_married_2020 = (marital_2020==1).
    p["currently_married_2020"] = (p["marital_2020"] == 1).astype("float")
    p.loc[p["marital_2020"].isna(), "currently_married_2020"] = np.nan
    p["currently_married_2014"] = (p["marital_2014"] == 1).astype("float")
    p.loc[p["marital_2014"].isna(), "currently_married_2014"] = np.nan
    p["log_income_2014"] = np.log1p(p["income_2014"])
    return p


# ------------------------------------------------------------------ #
# 1. Welch / Cohen's d / risk-difference helpers
# ------------------------------------------------------------------ #

def welch(y: pd.Series, group: pd.Series, hi="high", lo="low") -> dict:
    """Welch's t and Cohen's d for hi - lo difference on y."""
    a = y[group == hi].dropna().to_numpy()
    b = y[group == lo].dropna().to_numpy()
    if len(a) < 2 or len(b) < 2:
        return dict(n_hi=len(a), n_lo=len(b), diff=np.nan, t=np.nan, p=np.nan,
                    d=np.nan)
    t, p = sps.ttest_ind(a, b, equal_var=False)
    pooled_sd = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                        / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / pooled_sd if pooled_sd > 0 else np.nan
    return dict(n_hi=int(len(a)), n_lo=int(len(b)),
                diff=float(a.mean() - b.mean()),
                t=float(t), p=float(p), d=float(d))


def tertile(s: pd.Series) -> pd.Series:
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


# ------------------------------------------------------------------ #
# 2. Descriptive table  -> 01_descriptive_table.csv
# ------------------------------------------------------------------ #

def descriptive_table(df14: pd.DataFrame, df20: pd.DataFrame,
                      panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    spec = [
        ("2014_cross", df14, "ideation",
         ["currently_married", "first_marriage_age", "ideal_children",
          "housework_hours", "marriage_sat", "cohab_experience"],
         "female"),
        ("2020_cross", df20, "ideation",
         ["currently_married", "first_marriage_age", "housework_hours",
          "ideal_marriage_age", "birth_intention_2y", "marriage_sat",
          "cohab_experience", "childcare_hours"],
         "female"),
        ("panel_2014_baseline", panel, "ideation_2014",
         ["currently_married_2020", "housework_2020", "marriage_sat_2020",
          "cohab_experience_2020", "childcare_hours_2020",
          "birth_intention_2y_2020"],
         "female"),
    ]
    for tag, df, idcol, outcomes, fcol in spec:
        d = df.copy()
        d["__t"] = tertile(d[idcol])
        for outcome in outcomes:
            for stratum_name, mask in [("all", pd.Series(True, index=d.index)),
                                       ("male", d[fcol] == 0),
                                       ("female", d[fcol] == 1)]:
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


# ------------------------------------------------------------------ #
# 3. Coverage table -> 02_missing_table.csv
# ------------------------------------------------------------------ #

def missing_table(df14: pd.DataFrame, df20: pd.DataFrame,
                  panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for tag, df, cols in [
        ("2014_cross", df14, ["currently_married", "first_marriage_age",
                              "ideal_children", "housework_hours",
                              "marriage_sat", "cohab_experience"]),
        ("2020_cross", df20, ["currently_married", "first_marriage_age",
                              "housework_hours", "ideal_marriage_age",
                              "birth_intention_2y", "marriage_sat",
                              "cohab_experience", "childcare_hours"]),
        ("panel", panel, ["currently_married_2020", "housework_2020",
                          "marriage_sat_2020", "cohab_experience_2020",
                          "childcare_hours_2020", "birth_intention_2y_2020"]),
    ]:
        for c in cols:
            s = df[c]
            rows.append(dict(frame=tag, variable=c, n_total=len(df),
                             n_nonmissing=int(s.notna().sum()),
                             pct_coverage=round(100 * s.notna().mean(), 2)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 4. OLS / LPM fits with HC1
# ------------------------------------------------------------------ #

CONTROLS_CROSS = ["female", "age_c", "age_c2", "urban", "edu_yrs", "log_income"]
CONTROLS_LAGGED = ["female", "age_c14", "age_c14_2", "urban_2014",
                   "edu_yrs_2014", "log_income_2014"]


def _design_cross(df: pd.DataFrame, idcol: str, fcol: str, controls: list[str],
                  interact: bool = False) -> pd.DataFrame:
    d = df.copy()
    d["age_c"] = (d["age"] - 40) / 10
    d["age_c2"] = d["age_c"] ** 2
    d = d.rename(columns={idcol: "ideation"})
    if fcol != "female":
        d["female"] = d[fcol]
    X = pd.DataFrame({
        "const": 1.0,
        "ideation": d["ideation"].astype(float),
    })
    for c in controls:
        if c == "female":
            X["female"] = d["female"].astype(float)
        else:
            X[c] = d[c].astype(float)
    if interact:
        X["ideation_x_female"] = X["ideation"] * X["female"]
    return X, d


def _design_lagged(panel: pd.DataFrame, controls: list[str],
                   interact: bool, baseline_outcome_col: str | None) -> pd.DataFrame:
    d = panel.copy()
    d["age_c14"] = (d["age_2014"] - 40) / 10
    d["age_c14_2"] = d["age_c14"] ** 2
    d["log_income_2014"] = np.log1p(d["income_2014"])
    X = pd.DataFrame({"const": 1.0,
                      "ideation": d["ideation_2014"].astype(float)})
    for c in controls:
        if c == "female":
            X["female"] = d["female"].astype(float)
        else:
            X[c] = d[c].astype(float)
    if interact:
        X["ideation_x_female"] = X["ideation"] * X["female"]
    if baseline_outcome_col is not None and baseline_outcome_col in d.columns:
        X[baseline_outcome_col] = d[baseline_outcome_col].astype(float)
    return X, d


def fit_outcome(X: pd.DataFrame, y: pd.Series, stratum_mask: pd.Series) -> dict:
    """OLS with HC1 robust SEs, returning tidy dict of coefficients.

    Defensively drops zero-variance columns (other than const) before fitting;
    these would otherwise make X.T @ X singular when a stratum subsetted away
    all variation (e.g. urban==0 throughout, or a baseline outcome that is
    NaN-aligned identically with another control).
    """
    keep = stratum_mask & y.notna() & X.notna().all(axis=1)
    Xk = X.loc[keep].copy()
    yk = y.loc[keep].to_numpy()
    # drop zero-variance regressors except the constant
    drop_cols = []
    for c in Xk.columns:
        if c == "const":
            continue
        if Xk[c].nunique(dropna=False) <= 1:
            drop_cols.append(c)
    if drop_cols:
        Xk = Xk.drop(columns=drop_cols)
    if len(Xk) < (Xk.shape[1] + 2):
        return {"n": int(len(Xk)), "results": []}
    try:
        r = ST.ols_robust(Xk, yk, kind="HC1")
    except np.linalg.LinAlgError:
        return {"n": int(len(Xk)), "results": [],
                "r2": float("nan"), "note": "singular"}
    results = []
    for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"]):
        results.append(dict(term=term, coef=float(coef), se=float(se),
                            t=float(t), p=float(p)))
    return {"n": int(r["n"]), "results": results, "r2": float(r.get("r2", np.nan))}


# ------------------------------------------------------------------ #
# 5. Build the full result table
# ------------------------------------------------------------------ #

OUTCOMES_CROSS = {
    "currently_married":  dict(continuous=False, lo=0,  hi=1,  label="Currently married"),
    "first_marriage_age": dict(continuous=True,  lo=15, hi=50, label="Age at first marriage (descriptive)"),
    "ideal_children":     dict(continuous=True,  lo=0,  hi=10, label="Ideal children num (2014 only)"),
    "housework_hours":    dict(continuous=True,  lo=0,  hi=24, label="Housework hours / day"),
    # v2 additions
    "ideal_marriage_age": dict(continuous=True,  lo=15, hi=50, label="Ideal marriage age (2020 only)"),
    "birth_intention_2y": dict(continuous=False, lo=0,  hi=1,  label="Plans a child in next 2 yr (2020 only)"),
    "marriage_sat":       dict(continuous=True,  lo=1,  hi=5,  label="Marriage satisfaction (1-5)"),
    "cohab_experience":   dict(continuous=False, lo=0,  hi=1,  label="Cohabitation experience"),
    "childcare_hours":    dict(continuous=True,  lo=0,  hi=24, label="Childcare hours / day (2020 only)"),
}
OUTCOMES_LAGGED = {
    "currently_married_2020": dict(continuous=False, baseline="currently_married_2014",
                                   label="Currently married 2020"),
    "housework_2020":         dict(continuous=True,  baseline="housework_2014",
                                   label="Housework hours / day 2020"),
    # v2 additions where both waves exist
    "marriage_sat_2020":      dict(continuous=True,  baseline="marriage_sat_2014",
                                   label="Marriage satisfaction 2020 (1-5)"),
    "cohab_experience_2020":  dict(continuous=False, baseline="cohab_experience_2014",
                                   label="Cohabitation experience 2020"),
}


def fit_all(df14: pd.DataFrame, df20: pd.DataFrame,
            panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows_main = []
    rows_welch = []
    cross_frames = [("2014_cross", df14, "ideation", "female"),
                    ("2020_cross", df20, "ideation", "female")]
    for tag, df, idcol, fcol in cross_frames:
        for outcome, spec in OUTCOMES_CROSS.items():
            if outcome not in df.columns or df[outcome].notna().sum() < 50:
                continue
            X, d = _design_cross(df, idcol=idcol, fcol=fcol,
                                 controls=CONTROLS_CROSS, interact=True)
            y = d[outcome]
            # Welch per sex stratum
            d["__t"] = tertile(d[idcol])
            for stratum_name, mask in [
                ("all", pd.Series(True, index=d.index)),
                ("male", d[fcol] == 0),
                ("female", d[fcol] == 1),
            ]:
                w = welch(d.loc[mask, outcome], d.loc[mask, "__t"])
                rows_welch.append(dict(frame=tag, outcome=outcome,
                                       stratum=stratum_name, **w))
                # OLS per stratum: drop interaction term inside strata
                Xs = (X.drop(columns=[c for c in ("ideation_x_female", "female") if c in X.columns])
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
        X, d = _design_lagged(panel, controls=CONTROLS_LAGGED, interact=True,
                              baseline_outcome_col=baseline)
        y = d[outcome]
        d["__t"] = tertile(d["ideation_2014"])
        for stratum_name, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d["female"] == 0),
            ("female", d["female"] == 1),
        ]:
            w = welch(d.loc[mask, outcome], d.loc[mask, "__t"])
            rows_welch.append(dict(frame="lagged_2014to2020", outcome=outcome,
                                   stratum=stratum_name, **w))
            Xs = X.drop(columns=["ideation_x_female"]) if stratum_name != "all" else X
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

def fig_outcome_by_tertile(df: pd.DataFrame, idcol: str, fcol: str,
                            outcome: str, label: str, out_pdf: Path,
                            tag: str):
    """Per-tertile mean ± SE bar chart, side-by-side male/female."""
    d = df.copy()
    d["__t"] = tertile(d[idcol])
    fig, ax = plt.subplots(figsize=(5.0, 3.6))
    width = 0.36
    x = np.arange(3)
    male_means, male_se = [], []
    fem_means, fem_se = [], []
    for t in ["low", "mid", "high"]:
        m = d.loc[(d[fcol] == 0) & (d["__t"] == t), outcome].dropna()
        f = d.loc[(d[fcol] == 1) & (d["__t"] == t), outcome].dropna()
        male_means.append(m.mean()); male_se.append(m.std(ddof=1) / np.sqrt(len(m)) if len(m) > 1 else 0)
        fem_means.append(f.mean()); fem_se.append(f.std(ddof=1) / np.sqrt(len(f)) if len(f) > 1 else 0)
    ax.bar(x - width / 2, male_means, width=width, color="#1f77b4", label="Male",
           yerr=male_se, capsize=3)
    ax.bar(x + width / 2, fem_means, width=width, color="#d62728", label="Female",
           yerr=fem_se, capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["Low ideation\n(progressive)", "Mid", "High\n(traditional)"])
    ax.set_ylabel(label)
    ax.set_title(f"{label}\n({tag}, by ideation tertile × sex)")
    ax.legend(frameon=False)
    ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_coef_forest(results: pd.DataFrame, term: str, frame: str,
                    title: str, out_pdf: Path):
    """Forest plot of a single coefficient across outcomes × sex strata."""
    sub = results[(results["frame"] == frame) & (results["term"] == term)].copy()
    if sub.empty:
        return
    sub = sub.sort_values(["outcome", "stratum"])
    rows = []
    y_labels = []
    for _, r in sub.iterrows():
        rows.append((r["coef"], r["se"]))
        y_labels.append(f"{r['outcome']} · {r['stratum']} (n={r['n']})")
    fig, ax = plt.subplots(figsize=(6.5, 0.32 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys)
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.set_xlabel(f"OLS β on {term}  (HC1, 95 % CI)")
    ax.set_title(title)
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_summary_forest_all(results: pd.DataFrame, out_pdf: Path):
    """One big forest: the ideation coefficient across all (frame × outcome × stratum)."""
    sub = results[results["term"] == "ideation"].copy()
    if sub.empty:
        return
    sub["key"] = sub.apply(lambda r: f"[{r['frame']}] {r['outcome']} · {r['stratum']}", axis=1)
    sub = sub.sort_values(["frame", "outcome", "stratum"]).reset_index(drop=True)
    rows = list(zip(sub["coef"], sub["se"], sub["key"], sub["n"]))
    fig, ax = plt.subplots(figsize=(7.5, 0.30 * len(rows) + 1.8))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{r[2]} (n={r[3]})" for r in rows], fontsize=7.5)
    ax.set_xlabel("OLS β on ideation (HC1, 95 % CI) — outcome on its own scale")
    ax.set_title("RQ 5.2 individual — ideation coefficient across all fits")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_marriage_age_descriptive(df14: pd.DataFrame, out_pdf: Path):
    """Mean age at first marriage by birth-cohort decade × ideation tertile × sex."""
    d = df14.dropna(subset=["first_marriage_age", "birthy", "ideation", "female"]).copy()
    d["decade"] = (d["birthy"] // 10 * 10).astype(int)
    d["__t"] = tertile(d["ideation"])
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), sharey=True)
    for ax, fem, sex_name in zip(axes, [0, 1], ["Male", "Female"]):
        for t, color in zip(["low", "mid", "high"], ["#1a9850", "#999", "#d73027"]):
            sub = d[(d["female"] == fem) & (d["__t"] == t)]
            means = sub.groupby("decade")["first_marriage_age"].mean()
            counts = sub.groupby("decade").size()
            ok = counts > 30
            ax.plot(means.index[ok], means.values[ok], "-o", color=color,
                    label=f"{t} ideation", markersize=4)
        ax.set_title(f"{sex_name} (CFPS 2014)")
        ax.set_xlabel("Birth decade")
        if fem == 0:
            ax.set_ylabel("Mean age at first marriage")
        ax.grid(axis="y", linewidth=0.4, alpha=0.4)
        ax.legend(frameon=False, fontsize=7)
    fig.suptitle("Age at first marriage by birth decade × ideation tertile × sex",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_pdf)
    plt.close(fig)


# ------------------------------------------------------------------ #
# 7. Driver
# ------------------------------------------------------------------ #

def main() -> int:
    print("loading 2014 cross-section …")
    df14 = load_2014_cross()
    print(f"  n = {len(df14)}")
    print("loading 2020 cross-section …")
    df20 = load_2020_cross()
    print(f"  n = {len(df20)}")
    print("loading panel (lagged) …")
    panel = load_panel()
    print(f"  n = {len(panel)}")

    # tables
    desc = descriptive_table(df14, df20, panel)
    desc.to_csv(RUN / "01_descriptive_table.csv", index=False)
    miss = missing_table(df14, df20, panel)
    miss.to_csv(RUN / "02_missing_table.csv", index=False)
    main_tab, welch_tab = fit_all(df14, df20, panel)
    main_tab.to_csv(RUN / "04_result_table.csv", index=False)
    welch_tab.to_csv(TABLES / "welch_tertile_diffs.csv", index=False)
    print("tables written.")

    # figures
    fig_outcome_by_tertile(df14, "ideation", "female", "housework_hours",
                           "Housework hours / day",
                           FIGS / "housework_by_tertile_2014.pdf", "CFPS 2014")
    fig_outcome_by_tertile(df20, "ideation", "female", "housework_hours",
                           "Housework hours / day",
                           FIGS / "housework_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df14, "ideation", "female", "ideal_children",
                           "Ideal children",
                           FIGS / "ideal_children_by_tertile_2014.pdf", "CFPS 2014")
    # v2 additions
    fig_outcome_by_tertile(df20, "ideation", "female", "ideal_marriage_age",
                           "Ideal marriage age",
                           FIGS / "ideal_marriage_age_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df20, "ideation", "female", "birth_intention_2y",
                           "P(plans child within 2 yr)",
                           FIGS / "birth_intention_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df14, "ideation", "female", "marriage_sat",
                           "Marriage satisfaction (1-5)",
                           FIGS / "marriage_sat_by_tertile_2014.pdf", "CFPS 2014")
    fig_outcome_by_tertile(df20, "ideation", "female", "marriage_sat",
                           "Marriage satisfaction (1-5)",
                           FIGS / "marriage_sat_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df20, "ideation", "female", "cohab_experience",
                           "P(cohabitation experience)",
                           FIGS / "cohab_experience_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df20, "ideation", "female", "childcare_hours",
                           "Childcare hours / day",
                           FIGS / "childcare_by_tertile_2020.pdf", "CFPS 2020")
    fig_outcome_by_tertile(df14, "ideation", "female", "currently_married",
                           "P(currently married)",
                           FIGS / "currently_married_by_tertile_2014.pdf", "CFPS 2014")
    fig_outcome_by_tertile(df20, "ideation", "female", "currently_married",
                           "P(currently married)",
                           FIGS / "currently_married_by_tertile_2020.pdf", "CFPS 2020")
    fig_marriage_age_descriptive(df14, FIGS / "first_marriage_age_2014_descriptive.pdf")

    # coefficient forests
    fig_coef_forest(main_tab, "ideation", "2014_cross",
                    "OLS β on ideation — CFPS 2014 cross-section",
                    FIGS / "coef_forest_ideation_2014.pdf")
    fig_coef_forest(main_tab, "ideation", "2020_cross",
                    "OLS β on ideation — CFPS 2020 cross-section",
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

    fig_summary_forest_all(main_tab, FIGS / "summary_forest_all.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
