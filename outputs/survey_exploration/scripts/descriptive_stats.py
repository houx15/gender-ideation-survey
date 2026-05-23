#!/usr/bin/env python3
"""descriptive_stats.py — paper-grade descriptive + effect-size helpers.

All functions are pure: they take arrays/Series and return plain dicts (or
floats), no I/O.  Used by analysis_023 for Table 1, Welch tests, Cohen's d,
Hedges' g, and bootstrap CIs of group means.

These are general-purpose; they intentionally avoid any survey-specific config.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# --------------------------------------------------------------------------- #
# Table-1 row.
# --------------------------------------------------------------------------- #

def describe_var(series, name: str | None = None, explanation: str = "") -> dict:
    """Return a dict-of-stats row for one variable.

    Keys: name, explanation, n (non-missing), mean, sd, min, max, n_missing,
    missing_pct.  Empty / all-missing inputs produce NaN for mean/sd/min/max.
    """
    s = pd.Series(series).reset_index(drop=True)
    total = int(len(s))
    s_num = pd.to_numeric(s, errors="coerce")
    n_missing = int(s_num.isna().sum())
    n = total - n_missing
    if n == 0:
        return {"name": name, "explanation": explanation, "n": 0, "mean": np.nan,
                "sd": np.nan, "min": np.nan, "max": np.nan,
                "n_missing": n_missing,
                "missing_pct": (100.0 * n_missing / total) if total else np.nan}
    vals = s_num.dropna()
    return {
        "name": name,
        "explanation": explanation,
        "n": int(n),
        "mean": float(vals.mean()),
        "sd": float(vals.std(ddof=1)) if n > 1 else np.nan,
        "min": float(vals.min()),
        "max": float(vals.max()),
        "n_missing": n_missing,
        "missing_pct": float(100.0 * n_missing / total) if total else np.nan,
    }


def describe_frame(df: pd.DataFrame, varspec: list[tuple[str, str, str]]) -> pd.DataFrame:
    """Build a Table-1 from `df` over a list of (column, display_name, explanation).

    Missing columns are skipped silently (and a row of NaNs would mislead).
    """
    rows = []
    for col, name, expl in varspec:
        if col not in df.columns:
            continue
        rows.append(describe_var(df[col], name=name, explanation=expl))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Effect sizes for two independent samples.
# --------------------------------------------------------------------------- #

def _clean_pair(a, b):
    a = np.asarray(a, dtype="float64")
    b = np.asarray(b, dtype="float64")
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    return a, b


def cohen_d(a, b) -> float:
    """Standardised mean difference (a - b) / pooled_sd.

    Pooled SD uses (n1-1, n2-1) weights (Cohen 1988).  Returns NaN if either
    group has <2 observations or pooled SD is 0.
    """
    a, b = _clean_pair(a, b)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return float("nan")
    s1 = a.var(ddof=1)
    s2 = b.var(ddof=1)
    pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if pooled == 0:
        return float("nan")
    return float((a.mean() - b.mean()) / pooled)


def hedges_g(a, b) -> float:
    """Cohen's d with small-sample bias correction (Hedges & Olkin 1985)."""
    d = cohen_d(a, b)
    if not np.isfinite(d):
        return float("nan")
    a, b = _clean_pair(a, b)
    n = len(a) + len(b)
    correction = 1.0 - (3.0 / (4.0 * n - 9.0))
    return float(d * correction)


def welch_ci_diff(a, b, alpha: float = 0.05) -> dict:
    """Welch's t-test on independent samples, with mean-difference CI.

    Returns dict with diff (a - b), se, t, df, p (two-sided), ci_lo, ci_hi.
    Constant-input case returns diff=0, p=NaN, CI=(NaN,NaN).
    """
    a, b = _clean_pair(a, b)
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        return {"diff": float("nan"), "se": float("nan"), "t": float("nan"),
                "df": float("nan"), "p": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan")}
    m1, m2 = a.mean(), b.mean()
    s1, s2 = a.var(ddof=1), b.var(ddof=1)
    diff = m1 - m2
    se = np.sqrt(s1 / n1 + s2 / n2)
    if se == 0:
        return {"diff": float(diff), "se": 0.0, "t": float("nan"),
                "df": float("nan"), "p": float("nan"),
                "ci_lo": float("nan"), "ci_hi": float("nan")}
    df = (s1 / n1 + s2 / n2) ** 2 / (
        (s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1))
    t = diff / se
    p = 2 * stats.t.sf(abs(t), df)
    crit = stats.t.ppf(1 - alpha / 2, df)
    return {"diff": float(diff), "se": float(se), "t": float(t), "df": float(df),
            "p": float(p), "ci_lo": float(diff - crit * se),
            "ci_hi": float(diff + crit * se)}


# --------------------------------------------------------------------------- #
# Bootstrap CI of a mean (non-parametric percentile interval).
# --------------------------------------------------------------------------- #

def bootstrap_mean_ci(arr, n_boot: int = 1000, seed: int = 0,
                      alpha: float = 0.05) -> dict:
    """Percentile bootstrap CI of the mean.

    Returns dict {mean, ci_lo, ci_hi, n}.  NaN-out if the array is empty.
    """
    a = np.asarray(arr, dtype="float64")
    a = a[np.isfinite(a)]
    n = len(a)
    if n == 0:
        return {"mean": float("nan"), "ci_lo": float("nan"),
                "ci_hi": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    means = a[idx].mean(axis=1)
    lo = float(np.quantile(means, alpha / 2))
    hi = float(np.quantile(means, 1 - alpha / 2))
    return {"mean": float(a.mean()), "ci_lo": lo, "ci_hi": hi, "n": int(n)}
