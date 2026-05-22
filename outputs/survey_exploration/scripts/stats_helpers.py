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


def ols(X: pd.DataFrame, y) -> dict:
    """Fit y ~ X (X already includes any constant column). Returns term/coef/se/t + n."""
    y = np.asarray(y, dtype="float64")
    Xv = X.to_numpy(dtype="float64")
    ok = np.isfinite(Xv).all(axis=1) & np.isfinite(y)
    Xm, ym = Xv[ok], y[ok]
    n, k = Xm.shape
    beta, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
    resid = ym - Xm @ beta
    sigma2 = (resid @ resid) / (n - k)
    cov = sigma2 * np.linalg.inv(Xm.T @ Xm)
    se = np.sqrt(np.diag(cov))
    return {
        "term": list(X.columns),
        "coef": [float(b) for b in beta],
        "se": [float(s) for s in se],
        "t": [float(b / s) if s else float("nan") for b, s in zip(beta, se)],
        "n": int(n),
    }
