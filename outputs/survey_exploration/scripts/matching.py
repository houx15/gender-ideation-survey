#!/usr/bin/env python3
"""
matching.py — propensity-score matching for the gender-gap-in-resources question.

Estimates the average treatment effect on the treated (ATT) of a binary "treatment"
(e.g. being a daughter) on an outcome, by nearest-neighbour matching on the estimated
propensity score. Classical paired inference on the matched differences.

Locked by tests/test_matching.py. Raw data is never modified.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def psm_att(df: pd.DataFrame, treat_col: str, outcome_col: str,
            covariate_cols: list[str], caliper: float | None = None) -> dict:
    """Nearest-neighbour PSM estimate of the ATT.

    - Fits a logistic propensity model treat ~ covariates (standardized).
    - Matches each treated unit to the nearest control by |propensity| (with replacement).
    - Optional caliper (in propensity units) drops poorly-matched treated units.
    - Returns att, se, t, p (paired t-test on matched differences) and counts.
    Rows with any NaN in treat/outcome/covariates are dropped first.
    """
    cols = [treat_col, outcome_col] + covariate_cols
    d = df[cols].dropna()
    t = d[treat_col].to_numpy(dtype="float64")
    y = d[outcome_col].to_numpy(dtype="float64")
    Xc = StandardScaler().fit_transform(d[covariate_cols].to_numpy(dtype="float64"))

    ps = LogisticRegression(max_iter=1000).fit(Xc, t).predict_proba(Xc)[:, 1]
    ps_t, ps_c = ps[t == 1], ps[t == 0]
    y_t, y_c = y[t == 1], y[t == 0]

    diffs = []
    for i, p_i in enumerate(ps_t):
        j = int(np.argmin(np.abs(ps_c - p_i)))
        if caliper is not None and abs(ps_c[j] - p_i) > caliper:
            continue
        diffs.append(y_t[i] - y_c[j])
    diffs = np.asarray(diffs, dtype="float64")

    att = float(diffs.mean())
    se = float(diffs.std(ddof=1) / np.sqrt(len(diffs)))
    tval = att / se if se else float("nan")
    pval = float(2 * stats.t.sf(abs(tval), len(diffs) - 1)) if se else float("nan")
    return {
        "att": att, "se": se, "t": float(tval), "p": pval,
        "n_treated": int(len(diffs)), "n_control": int((t == 0).sum()),
    }
