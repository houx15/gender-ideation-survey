#!/usr/bin/env python3
"""analysis_028 — RQ 5.4 education outcomes (deep, time-order-aware).

Outcomes:
  - edu_yrs       (cfps2014eduy_im / cfps2020eduy_im, [0,22])
  - edu_level     (descriptive only; from cfps2014edu / w01)

Frames:
  (A) 2014 cross, full adults                                  reverse-causal
  (B) 2020 cross, full adults                                  reverse-causal
  (C) young-cohort cross (birthy >= 1990) in each wave         weak r-c
  (D) young-cohort lagged delta (panel, birthy >= 1990)        directional

Stratified overall / male / female; HC1 robust SEs; controls female, age_c,
age_c2, urban, log_income.  No edu_yrs control (it's the outcome).
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

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


# ------------------------------------------------------------------ #
# 0. Edu-level unifier (descriptive only)
# ------------------------------------------------------------------ #

# Unified ordinal: 0=illiterate, 1=primary, 2=junior, 3=senior,
# 4=college (大专), 5=bachelor, 6=masters, 7=PhD.

_EDU_LEVEL_2014 = {1: 0, 9: 0,   # 文盲 + 不必读书 -> illiterate
                   2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
_EDU_LEVEL_2020 = {0: 0, 10: 0, 1: 0, 2: 0,   # 文盲 + 没上过学 + 托儿所 + 幼儿园
                   3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7}


def unify_edu_level(s: pd.Series, wave: str) -> pd.Series:
    """Map CFPS edu code to unified 0..7 ordinal; missing -> NaN."""
    table = _EDU_LEVEL_2014 if wave == "2014" else _EDU_LEVEL_2020
    s = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    for raw, unified in table.items():
        out[s == raw] = float(unified)
    return out


# ------------------------------------------------------------------ #
# 1. Loaders
# ------------------------------------------------------------------ #

def load_2014() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2014")]
    extras = ["cfps2014eduy_im", "cfps2014edu", "income", "qa301",
              "cfps_birthy", cfg["gender_var"], "pid"]
    df, _m, _norm, idx = L.load_recoded(
        "CFPS", "2014", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"]    = pd.to_numeric(df["cfps_birthy"], errors="coerce").where(
        lambda x: x.between(1920, 2007))
    df["age"]       = 2014 - df["birthy"]
    df["edu_yrs"]   = pd.to_numeric(df["cfps2014eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["edu_level"] = unify_edu_level(df["cfps2014edu"], "2014")
    df["income"]      = P._to_numeric_nan_sentinels(df["income"]).where(lambda x: x >= 0)
    df["log_income"]  = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk == 3, 1.0, np.nan))
    return df


def load_2020() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2020")]
    extras = ["cfps2020eduy_im", "w01", "emp_income", "qa301",
              "ibirthy", cfg["gender_var"], "pid"]
    df, _m, _norm, idx = L.load_recoded(
        "CFPS", "2020", extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    df["birthy"]    = pd.to_numeric(df["ibirthy"], errors="coerce").where(
        lambda x: x.between(1920, 2010))
    df["age"]       = 2020 - df["birthy"]
    df["edu_yrs"]   = pd.to_numeric(df["cfps2020eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["edu_level"] = unify_edu_level(df["w01"], "2020")
    df["income"]      = P._to_numeric_nan_sentinels(df["emp_income"]).where(lambda x: x >= 0)
    df["log_income"]  = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0, np.where(hk.isin([3, 7]), 1.0, np.nan))
    return df


def load_panel() -> pd.DataFrame:
    p = P.build_panel().copy()
    p["log_income_2014"] = np.log1p(p["income_2014"])
    return p


# ------------------------------------------------------------------ #
# 2. Welch + tertile + OLS helpers
# ------------------------------------------------------------------ #

def welch(y, group, hi="high", lo="low"):
    a = y[group == hi].dropna().to_numpy()
    b = y[group == lo].dropna().to_numpy()
    if len(a) < 2 or len(b) < 2:
        return dict(n_hi=len(a), n_lo=len(b), diff=np.nan, t=np.nan, p=np.nan, d=np.nan)
    t, p = sps.ttest_ind(a, b, equal_var=False)
    pooled = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                     / (len(a) + len(b) - 2))
    d = (a.mean() - b.mean()) / pooled if pooled > 0 else np.nan
    return dict(n_hi=int(len(a)), n_lo=int(len(b)),
                diff=float(a.mean() - b.mean()),
                t=float(t), p=float(p), d=float(d))


def tertile(s):
    q = s.quantile([1 / 3, 2 / 3]).values
    return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])


CONTROLS = ["female", "age_c", "age_c2", "urban", "log_income"]


def fit_ols(df, idcol, fcol, controls, interact, mask, baseline=None):
    d = df.copy()
    d["age_c"] = (d["age"] - 40) / 10 if "age" in d.columns else (d["age_2014"] - 40) / 10
    d["age_c2"] = d["age_c"] ** 2
    d = d.rename(columns={idcol: "ideation"})
    if fcol != "female":
        d["female"] = d[fcol]
    X = pd.DataFrame({"const": 1.0, "ideation": d["ideation"].astype(float)})
    for c in controls:
        X[c] = d[c].astype(float)
    if interact:
        X["ideation_x_female"] = X["ideation"] * X["female"]
    if baseline is not None and baseline in d.columns:
        X[baseline] = d[baseline].astype(float)
    y = d["edu_yrs_outcome"] if "edu_yrs_outcome" in d.columns else d["edu_yrs"]
    keep = mask & y.notna() & X.notna().all(axis=1)
    Xk = X.loc[keep]
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
# 3. Driver
# ------------------------------------------------------------------ #

def descriptive_table(df14, df20, panel):
    rows = []
    # Cross-section: full + young cohort, each wave
    for tag, df, idcol, ycol in [
        ("2014_cross",       df14, "ideation", None),
        ("2020_cross",       df20, "ideation", None),
        ("2014_young_cohort", df14[df14["birthy"] >= 1990], "ideation", None),
        ("2020_young_cohort", df20[df20["birthy"] >= 1990], "ideation", None),
    ]:
        d = df.copy()
        if "edu_yrs" not in d.columns:
            continue
        d["__t"] = tertile(d[idcol])
        for stratum_name, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d["female"] == 0),
            ("female", d["female"] == 1),
        ]:
            for t in ["low", "mid", "high"]:
                sub = d.loc[mask & (d["__t"] == t), "edu_yrs"]
                rows.append(dict(frame=tag, outcome="edu_yrs",
                                 stratum=stratum_name, ideation_tertile=t,
                                 n=int(sub.notna().sum()),
                                 mean=round(float(sub.mean()), 3) if sub.notna().any() else np.nan,
                                 sd=round(float(sub.std(ddof=1)), 3) if sub.notna().sum() > 1 else np.nan))
    # Edu-level cross-tab
    return pd.DataFrame(rows)


def cohort_table(df14, df20):
    rows = []
    for tag, df in [("2014_cross", df14), ("2020_cross", df20)]:
        d = df.copy()
        d["decade"] = (d["birthy"] // 10 * 10).astype("Int64")
        d["__t"] = tertile(d["ideation"])
        for fem in [0, 1]:
            for decade, g_d in d[d["female"] == fem].dropna(subset=["edu_yrs", "decade", "__t"]).groupby("decade"):
                for t in ["low", "mid", "high"]:
                    sub = g_d.loc[g_d["__t"] == t, "edu_yrs"]
                    if sub.notna().sum() < 20:
                        continue
                    rows.append(dict(frame=tag, decade=int(decade),
                                     female=int(fem), tertile=t, n=int(len(sub)),
                                     mean_edu_yrs=round(float(sub.mean()), 3)))
    return pd.DataFrame(rows)


def fit_all(df14, df20, panel):
    rows_main, rows_welch = [], []
    # (A) 2014 cross, (B) 2020 cross — full adults
    for tag, df, idcol, fcol in [
        ("2014_cross", df14, "ideation", "female"),
        ("2020_cross", df20, "ideation", "female"),
    ]:
        d = df.copy()
        d["__t"] = tertile(d[idcol])
        for stratum_name, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d[fcol] == 0),
            ("female", d[fcol] == 1),
        ]:
            w = welch(d.loc[mask, "edu_yrs"], d.loc[mask, "__t"])
            rows_welch.append(dict(frame=tag, outcome="edu_yrs",
                                   stratum=stratum_name, **w))
            controls_here = CONTROLS if stratum_name == "all" else \
                [c for c in CONTROLS if c != "female"]
            fit = fit_ols(df, idcol=idcol, fcol=fcol, controls=controls_here,
                          interact=(stratum_name == "all"), mask=mask)
            for r in fit["results"]:
                rows_main.append(dict(frame=tag, outcome="edu_yrs",
                                      stratum=stratum_name, n=fit["n"],
                                      term=r["term"], coef=round(r["coef"], 5),
                                      se=round(r["se"], 5), t=round(r["t"], 3),
                                      p=round(r["p"], 5)))
    # (C) Young cohort cross (birthy >= 1990)
    for tag, df in [("2014_young_cohort", df14[df14["birthy"] >= 1990].copy()),
                    ("2020_young_cohort", df20[df20["birthy"] >= 1990].copy())]:
        if len(df) < 100:
            continue
        d = df.copy()
        d["__t"] = tertile(d["ideation"])
        for stratum_name, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d["female"] == 0),
            ("female", d["female"] == 1),
        ]:
            w = welch(d.loc[mask, "edu_yrs"], d.loc[mask, "__t"])
            rows_welch.append(dict(frame=tag, outcome="edu_yrs",
                                   stratum=stratum_name, **w))
            controls_here = CONTROLS if stratum_name == "all" else \
                [c for c in CONTROLS if c != "female"]
            fit = fit_ols(df, idcol="ideation", fcol="female",
                          controls=controls_here,
                          interact=(stratum_name == "all"), mask=mask)
            for r in fit["results"]:
                rows_main.append(dict(frame=tag, outcome="edu_yrs",
                                      stratum=stratum_name, n=fit["n"],
                                      term=r["term"], coef=round(r["coef"], 5),
                                      se=round(r["se"], 5), t=round(r["t"], 3),
                                      p=round(r["p"], 5)))
    # (D) Young cohort lagged delta
    young = panel[panel["birthy_2014"] >= 1990].copy()
    young = young.rename(columns={"ideation_2014": "ideation",
                                   "edu_yrs_2020": "edu_yrs"})
    young["age"] = young["age_2014"]
    young["female"] = young["female"]
    young["log_income"] = young["log_income_2014"]
    young["urban"] = young["urban_2014"]
    if len(young) > 50:
        d = young.copy()
        d["__t"] = tertile(d["ideation"])
        for stratum_name, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d["female"] == 0),
            ("female", d["female"] == 1),
        ]:
            w = welch(d.loc[mask, "edu_yrs"], d.loc[mask, "__t"])
            rows_welch.append(dict(frame="lagged_young_cohort_delta",
                                   outcome="edu_yrs_2020", stratum=stratum_name, **w))
            controls_here = CONTROLS if stratum_name == "all" else \
                [c for c in CONTROLS if c != "female"]
            fit = fit_ols(d, idcol="ideation", fcol="female",
                          controls=controls_here,
                          interact=(stratum_name == "all"), mask=mask,
                          baseline="edu_yrs_2014")
            for r in fit["results"]:
                rows_main.append(dict(frame="lagged_young_cohort_delta",
                                      outcome="edu_yrs_2020", stratum=stratum_name,
                                      n=fit["n"], term=r["term"],
                                      coef=round(r["coef"], 5),
                                      se=round(r["se"], 5), t=round(r["t"], 3),
                                      p=round(r["p"], 5)))
    return pd.DataFrame(rows_main), pd.DataFrame(rows_welch)


# ------------------------------------------------------------------ #
# 4. Figures
# ------------------------------------------------------------------ #

def fig_edu_by_tertile_sex(df, label_tag, out_pdf):
    d = df.copy()
    d["__t"] = tertile(d["ideation"])
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    width = 0.36
    x = np.arange(3)
    male_means, male_se = [], []
    fem_means, fem_se = [], []
    for t in ["low", "mid", "high"]:
        m = d.loc[(d["female"] == 0) & (d["__t"] == t), "edu_yrs"].dropna()
        f = d.loc[(d["female"] == 1) & (d["__t"] == t), "edu_yrs"].dropna()
        male_means.append(m.mean()); male_se.append(m.std(ddof=1) / np.sqrt(len(m)) if len(m) > 1 else 0)
        fem_means.append(f.mean()); fem_se.append(f.std(ddof=1) / np.sqrt(len(f)) if len(f) > 1 else 0)
    ax.bar(x - width / 2, male_means, width=width, color="#1f77b4", label="Male",
           yerr=male_se, capsize=3)
    ax.bar(x + width / 2, fem_means, width=width, color="#d62728", label="Female",
           yerr=fem_se, capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["Low (progressive)", "Mid", "High (traditional)"])
    ax.set_ylabel("Years of education")
    ax.set_title(f"Education years by ideation tertile × sex\n({label_tag})")
    ax.legend(frameon=False)
    ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_edu_by_cohort(df, label_tag, out_pdf, split_fn=None,
                       split_label="tertile"):
    """Mean edu_yrs by birth decade × ideation split × sex, with 95 % CI bands.

    The reverse-causality story (older cohorts: less edu AND more traditional)
    becomes visible. CIs are mean ± 1.96 · SE.

    `split_fn` is a callable from ideation Series -> categorical Series with
    levels low / mid / high. Defaults to empirical terciles. Can pass a
    fixed-cutoff variant.
    """
    if split_fn is None:
        split_fn = tertile
    d = df.dropna(subset=["edu_yrs", "birthy", "ideation", "female"]).copy()
    d["decade"] = (d["birthy"] // 10 * 10).astype(int)
    d["__t"] = split_fn(d["ideation"])
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), sharey=True)
    for ax, fem, name in zip(axes, [0, 1], ["Male", "Female"]):
        for t, color in zip(["low", "mid", "high"], ["#1a9850", "#999", "#d73027"]):
            sub = d[(d["female"] == fem) & (d["__t"] == t)]
            grouped = sub.groupby("decade")["edu_yrs"]
            means = grouped.mean()
            counts = grouped.size()
            sds = grouped.std(ddof=1)
            ok = counts > 30
            xs = means.index[ok]
            ys = means.values[ok]
            ses = (sds.values / np.sqrt(counts.values))[ok.values]
            lo = ys - 1.96 * ses
            hi = ys + 1.96 * ses
            ax.fill_between(xs, lo, hi, color=color, alpha=0.18, linewidth=0)
            ax.plot(xs, ys, "-o", color=color, label=f"{t}", markersize=4)
        ax.set_title(f"{name}")
        ax.set_xlabel("Birth decade")
        if fem == 0:
            ax.set_ylabel("Mean years of education")
        ax.grid(axis="y", linewidth=0.4, alpha=0.4)
        ax.legend(frameon=False, fontsize=7, title=f"Ideation {split_label}")
    fig.suptitle(f"Edu years by birth decade × ideation {split_label} × sex ({label_tag})\n"
                 f"95 % CI bands (mean ± 1.96·SE)",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out_pdf)
    plt.close(fig)


def _fixed_cutoff(s: pd.Series) -> pd.Series:
    """Alternative to empirical terciles: fixed cutoffs on [0, 1] index.

    low: < 0.4    mid: 0.4–0.7    high: > 0.7

    Substantively interpretable (a "low" person disagrees with most
    traditional items), comparable across waves and across sex strata.
    """
    return pd.cut(s, [-np.inf, 0.4, 0.7, np.inf],
                  labels=["low", "mid", "high"])


def fig_coef_forest(results, term, frames, out_pdf, title):
    sub = results[(results["term"] == term) & (results["frame"].isin(frames))].copy()
    if sub.empty:
        return
    sub = sub.sort_values(["frame", "stratum"])
    rows = list(zip(sub["coef"], sub["se"],
                    [f"[{r['frame']}] {r['stratum']} (n={r['n']})" for _, r in sub.iterrows()]))
    fig, ax = plt.subplots(figsize=(7.0, 0.30 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=7.5)
    ax.set_xlabel(f"β on {term}  (HC1, 95 % CI)")
    ax.set_title(title)
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


# ------------------------------------------------------------------ #
# 5. Driver
# ------------------------------------------------------------------ #

def main() -> int:
    print("loading 2014 …")
    df14 = load_2014()
    print(f"  n = {len(df14)}")
    print("loading 2020 …")
    df20 = load_2020()
    print(f"  n = {len(df20)}")
    print("loading panel …")
    panel = load_panel()
    print(f"  n = {len(panel)}")

    desc = descriptive_table(df14, df20, panel)
    desc.to_csv(RUN / "01_descriptive_table.csv", index=False)
    cohort = cohort_table(df14, df20)
    cohort.to_csv(TABLES / "edu_by_cohort.csv", index=False)
    miss = pd.DataFrame([
        dict(frame="2014_cross", variable="edu_yrs", n_total=len(df14),
             n_nonmissing=int(df14["edu_yrs"].notna().sum()),
             pct_coverage=round(100 * df14["edu_yrs"].notna().mean(), 2)),
        dict(frame="2014_cross", variable="edu_level", n_total=len(df14),
             n_nonmissing=int(df14["edu_level"].notna().sum()),
             pct_coverage=round(100 * df14["edu_level"].notna().mean(), 2)),
        dict(frame="2020_cross", variable="edu_yrs", n_total=len(df20),
             n_nonmissing=int(df20["edu_yrs"].notna().sum()),
             pct_coverage=round(100 * df20["edu_yrs"].notna().mean(), 2)),
        dict(frame="2020_cross", variable="edu_level", n_total=len(df20),
             n_nonmissing=int(df20["edu_level"].notna().sum()),
             pct_coverage=round(100 * df20["edu_level"].notna().mean(), 2)),
        dict(frame="2014_young_cohort", variable="edu_yrs",
             n_total=int((df14["birthy"] >= 1990).sum()),
             n_nonmissing=int(df14.loc[df14["birthy"] >= 1990, "edu_yrs"].notna().sum()),
             pct_coverage=round(100 * df14.loc[df14["birthy"] >= 1990, "edu_yrs"].notna().mean(), 2)),
        dict(frame="2020_young_cohort", variable="edu_yrs",
             n_total=int((df20["birthy"] >= 1990).sum()),
             n_nonmissing=int(df20.loc[df20["birthy"] >= 1990, "edu_yrs"].notna().sum()),
             pct_coverage=round(100 * df20.loc[df20["birthy"] >= 1990, "edu_yrs"].notna().mean(), 2)),
        dict(frame="lagged_young_cohort", variable="edu_yrs_2020 (panel, birthy>=1990)",
             n_total=int((panel["birthy_2014"] >= 1990).sum()),
             n_nonmissing=int(panel.loc[panel["birthy_2014"] >= 1990, "edu_yrs_2020"].notna().sum()),
             pct_coverage=round(100 * panel.loc[panel["birthy_2014"] >= 1990, "edu_yrs_2020"].notna().mean(), 2)),
    ])
    miss.to_csv(RUN / "02_missing_table.csv", index=False)

    main_tab, welch_tab = fit_all(df14, df20, panel)
    main_tab.to_csv(RUN / "04_result_table.csv", index=False)
    welch_tab.to_csv(TABLES / "welch_tertile_diffs.csv", index=False)
    print("tables written.")

    # Figures
    fig_edu_by_tertile_sex(df14, "CFPS 2014 full sample",
                            FIGS / "edu_yrs_by_tertile_2014.pdf")
    fig_edu_by_tertile_sex(df20, "CFPS 2020 full sample",
                            FIGS / "edu_yrs_by_tertile_2020.pdf")
    fig_edu_by_tertile_sex(df14[df14["birthy"] >= 1990],
                            "CFPS 2014 young cohort (birthy ≥ 1990)",
                            FIGS / "edu_yrs_by_tertile_2014_young.pdf")
    fig_edu_by_tertile_sex(df20[df20["birthy"] >= 1990],
                            "CFPS 2020 young cohort (birthy ≥ 1990)",
                            FIGS / "edu_yrs_by_tertile_2020_young.pdf")
    # default split = empirical tertiles, with CI bands (v2)
    fig_edu_by_cohort(df14, "CFPS 2014",
                       FIGS / "edu_yrs_by_cohort_2014.pdf")
    fig_edu_by_cohort(df20, "CFPS 2020",
                       FIGS / "edu_yrs_by_cohort_2020.pdf")
    # v2 sensitivity: fixed-cutoff split (< .4 / .4-.7 / > .7 on the index)
    fig_edu_by_cohort(df14, "CFPS 2014",
                       FIGS / "edu_yrs_by_cohort_2014_fixedcutoff.pdf",
                       split_fn=_fixed_cutoff,
                       split_label="fixed-cutoff (<.4 / .4-.7 / >.7)")
    fig_edu_by_cohort(df20, "CFPS 2020",
                       FIGS / "edu_yrs_by_cohort_2020_fixedcutoff.pdf",
                       split_fn=_fixed_cutoff,
                       split_label="fixed-cutoff (<.4 / .4-.7 / >.7)")

    fig_coef_forest(main_tab, "ideation",
                    ["2014_cross", "2020_cross",
                     "2014_young_cohort", "2020_young_cohort",
                     "lagged_young_cohort_delta"],
                    FIGS / "coef_forest_ideation_all_frames.pdf",
                    "OLS β on ideation across all 028 frames (HC1, 95 % CI)")
    fig_coef_forest(main_tab, "ideation_x_female",
                    ["2014_cross", "2020_cross",
                     "2014_young_cohort", "2020_young_cohort",
                     "lagged_young_cohort_delta"],
                    FIGS / "coef_forest_interaction_all_frames.pdf",
                    "Gender-moderation: β on ideation × female (HC1, 95 % CI)")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
