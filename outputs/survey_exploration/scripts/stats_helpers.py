#!/usr/bin/env python3
"""
stats_helpers.py — minimal OLS used across analysis runs.

Classical (homoskedastic) standard errors. Listwise-deletes rows with any NaN in
X or y. Returns a dict of parallel lists so results serialize straight to CSV.
Locked by tests/test_stats_helpers.py.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats


def wls(X: pd.DataFrame, y, w) -> dict:
    """Weighted least squares with robust (sandwich) SEs — for survey weights.

    Point estimates: beta = (X'WX)^-1 X'W y. Inference: heteroskedasticity-robust
    sandwich V = (X'WX)^-1 (X' W diag(e^2) W X) (X'WX)^-1, the correct estimator for
    sampling weights. Weights are normalized to mean 1 (point estimates are scale-free;
    this keeps SEs interpretable). Rows with NaN in X/y/w or w<=0 are dropped.
    """
    y = np.asarray(y, dtype="float64")
    w = np.asarray(w, dtype="float64")
    Xv = X.to_numpy(dtype="float64")
    ok = np.isfinite(Xv).all(axis=1) & np.isfinite(y) & np.isfinite(w) & (w > 0)
    Xm, ym, wm = Xv[ok], y[ok], w[ok]
    wm = wm / wm.mean()
    n, k = Xm.shape
    XtW = Xm.T * wm
    bread = np.linalg.inv(XtW @ Xm)
    beta = bread @ (XtW @ ym)
    e = ym - Xm @ beta
    meat = (Xm * (wm * e)[:, None]).T @ (Xm * (wm * e)[:, None])
    V = bread @ meat @ bread
    se = np.sqrt(np.diag(V))
    tvals = [float(b / s) if s else float("nan") for b, s in zip(beta, se)]
    pvals = [float(2 * stats.norm.sf(abs(t))) if np.isfinite(t) else float("nan") for t in tvals]
    return {"term": list(X.columns), "coef": [float(b) for b in beta],
            "se": [float(s) for s in se], "t": tvals, "p": pvals, "n": int(n)}


def icc_oneway(value: pd.Series, group: pd.Series) -> float:
    """One-way random-effects ICC (ANOVA estimator) on groups with >=2 members.

    Measures how much of the variance is BETWEEN groups (e.g. how much siblings resemble
    each other). ICC=1 when members are identical within group; ~0 when groups don't differ.
    """
    d = pd.DataFrame({"v": value, "g": group}).dropna()
    sizes = d.groupby("g")["v"].transform("size")
    d = d[sizes >= 2]                       # ICC informed only by multi-member groups
    if d["g"].nunique() < 2:
        return float("nan")
    grand = d["v"].mean()
    gmean = d.groupby("g")["v"].transform("mean")
    n_i = d.groupby("g")["v"].size().to_numpy(dtype="float64")
    k = len(n_i)
    N = len(d)
    ssb = float((d.groupby("g")["v"].mean().to_numpy() - grand) @
                ((d.groupby("g")["v"].mean().to_numpy() - grand) * n_i))
    ssw = float(((d["v"] - gmean) ** 2).sum())
    msb = ssb / (k - 1)
    msw = ssw / (N - k)
    n0 = (N - (n_i ** 2).sum() / N) / (k - 1)
    denom = msb + (n0 - 1) * msw
    return float((msb - msw) / denom) if denom else float("nan")


def fe_ols(df: pd.DataFrame, group_col: str, y_col: str, x_cols: list[str]) -> dict:
    """Fixed-effects (within) OLS: demean y and X by group, regress through the origin.

    Absorbs all group-level (e.g. family-level) variation, so coefficients are identified
    only from WITHIN-group variation in X. Degrees of freedom account for the absorbed
    group means: df = N - n_groups - len(x_cols). Returns term/coef/se/t/p + n + n_groups.
    """
    d = df[[group_col, y_col] + x_cols].dropna().copy()
    g = d[group_col]
    yd = d[y_col] - d[y_col].groupby(g).transform("mean")
    Xd = np.column_stack([(d[c] - d[c].groupby(g).transform("mean")).to_numpy() for c in x_cols])
    yv = yd.to_numpy(dtype="float64")
    n = len(d)
    n_groups = g.nunique()
    k = len(x_cols)
    beta, *_ = np.linalg.lstsq(Xd, yv, rcond=None)
    resid = yv - Xd @ beta
    dfree = n - n_groups - k
    sigma2 = (resid @ resid) / dfree
    cov = sigma2 * np.linalg.inv(Xd.T @ Xd)
    se = np.sqrt(np.diag(cov))
    tvals = [float(b / s) if s else float("nan") for b, s in zip(beta, se)]
    pvals = [float(2 * stats.t.sf(abs(t), dfree)) if np.isfinite(t) else float("nan")
             for t in tvals]
    return {"term": list(x_cols), "coef": [float(b) for b in beta],
            "se": [float(s) for s in se], "t": tvals, "p": pvals,
            "n": int(n), "n_groups": int(n_groups), "df": int(dfree)}


def ols(X: pd.DataFrame, y) -> dict:
    """Fit y ~ X (X already includes any constant column).

    Returns term/coef/se/t/p + n + df. p is the two-sided p-value from the
    t-distribution with (n - k) degrees of freedom; classical (homoskedastic) SEs.
    """
    y = np.asarray(y, dtype="float64")
    Xv = X.to_numpy(dtype="float64")
    ok = np.isfinite(Xv).all(axis=1) & np.isfinite(y)
    Xm, ym = Xv[ok], y[ok]
    n, k = Xm.shape
    df = n - k
    beta, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
    resid = ym - Xm @ beta
    sigma2 = (resid @ resid) / df
    cov = sigma2 * np.linalg.inv(Xm.T @ Xm)
    se = np.sqrt(np.diag(cov))
    tvals = [float(b / s) if s else float("nan") for b, s in zip(beta, se)]
    pvals = [float(2 * stats.t.sf(abs(t), df)) if np.isfinite(t) else float("nan")
             for t in tvals]
    return {
        "term": list(X.columns),
        "coef": [float(b) for b in beta],
        "se": [float(s) for s in se],
        "t": tvals,
        "p": pvals,
        "n": int(n),
        "df": int(df),
    }


def ols_robust(X: pd.DataFrame, y, kind: str = "HC1") -> dict:
    """Fit y ~ X (X already includes const) and return heteroskedasticity-robust SEs.

    kind:
      "HC0"  White (1980): cov = (X'X)^-1 X' diag(e^2) X (X'X)^-1
      "HC1"  Stata default: HC0 scaled by n / (n - k)   (small-sample correction)

    Same listwise-deletion + return shape as ols(); only the SEs/t/p change.
    """
    if kind not in ("HC0", "HC1"):
        raise ValueError(f"unknown robust kind: {kind!r}")
    y = np.asarray(y, dtype="float64")
    Xv = X.to_numpy(dtype="float64")
    ok = np.isfinite(Xv).all(axis=1) & np.isfinite(y)
    Xm, ym = Xv[ok], y[ok]
    n, k = Xm.shape
    df = n - k
    XtX_inv = np.linalg.inv(Xm.T @ Xm)
    beta = XtX_inv @ Xm.T @ ym
    resid = ym - Xm @ beta
    meat = Xm.T @ (resid[:, None] * resid[:, None] * Xm)   # X' diag(e^2) X
    cov = XtX_inv @ meat @ XtX_inv
    if kind == "HC1":
        cov *= n / df
    se = np.sqrt(np.diag(cov))
    tvals = [float(b / s) if s else float("nan") for b, s in zip(beta, se)]
    pvals = [float(2 * stats.t.sf(abs(t), df)) if np.isfinite(t) else float("nan")
             for t in tvals]
    return {
        "term": list(X.columns),
        "coef": [float(b) for b in beta],
        "se": [float(s) for s in se],
        "t": tvals,
        "p": pvals,
        "n": int(n),
        "df": int(df),
        "se_kind": kind,
    }
