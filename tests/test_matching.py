"""Tests for propensity-score matching (estimating a gender gap across all families).

DGP: treatment (e.g. being a daughter) is confounded with a covariate x, and the
outcome depends on both. Naive treated-minus-control is biased; PSM matching on x
should recover the true treatment effect.
"""
import numpy as np
import pandas as pd

import matching as M


def _confounded(effect, seed):
    rng = np.random.default_rng(seed)
    n = 4000
    x = rng.normal(size=n)
    p = 1 / (1 + np.exp(-1.2 * x))           # treatment more likely at high x
    treat = (rng.uniform(size=n) < p).astype(float)
    y = effect * treat + 2.0 * x + rng.normal(scale=1.0, size=n)
    return pd.DataFrame({"treat": treat, "x": x, "y": y})


def test_psm_recovers_true_effect_under_confounding():
    df = _confounded(effect=1.0, seed=0)
    naive = df.loc[df.treat == 1, "y"].mean() - df.loc[df.treat == 0, "y"].mean()
    res = M.psm_att(df, "treat", "y", ["x"])
    assert naive > 1.3                       # naive estimate is biased upward
    assert 0.75 <= res["att"] <= 1.25        # PSM recovers ~1.0
    assert res["p"] < 1e-3                    # and it's significant


def test_psm_no_effect_is_not_significant():
    df = _confounded(effect=0.0, seed=1)
    res = M.psm_att(df, "treat", "y", ["x"])
    assert abs(res["att"]) < 0.25
    assert res["p"] > 0.05


def test_psm_reports_counts_and_keys():
    df = _confounded(effect=0.5, seed=2)
    res = M.psm_att(df, "treat", "y", ["x"])
    for k in ("att", "se", "t", "p", "n_treated", "n_control"):
        assert k in res
    assert res["n_treated"] > 0 and res["n_control"] > 0


def test_psm_bootstrap_recovers_effect_with_positive_se():
    df = _confounded(effect=1.0, seed=3)
    res = M.psm_att_boot(df, "treat", "y", ["x"], n_boot=80, seed=0)
    assert 0.7 <= res["att"] <= 1.3
    assert res["boot_se"] > 0
    assert res["p"] < 0.05
    assert res["ci_lo"] < res["att"] < res["ci_hi"]


def test_psm_bootstrap_no_effect_ci_contains_zero():
    df = _confounded(effect=0.0, seed=4)
    res = M.psm_att_boot(df, "treat", "y", ["x"], n_boot=80, seed=0)
    assert res["ci_lo"] <= 0.0 <= res["ci_hi"]
    assert res["p"] > 0.05
