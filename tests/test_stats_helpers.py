"""Tests for the small OLS helper reused across analysis runs."""
import numpy as np
import pandas as pd
import pytest

import stats_helpers as S


def test_ols_recovers_exact_linear_relationship():
    # y = 2 + 3*x exactly -> intercept 2, slope 3, ~zero residual.
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    X = pd.DataFrame({"const": 1.0, "x": x})
    y = 2 + 3 * x
    res = S.ols(X, y)
    by = dict(zip(res["term"], res["coef"]))
    assert by["const"] == pytest.approx(2.0, abs=1e-9)
    assert by["x"] == pytest.approx(3.0, abs=1e-9)
    assert res["n"] == 5


def test_ols_drops_rows_with_missing():
    x = np.array([0.0, 1.0, 2.0, np.nan, 4.0])
    X = pd.DataFrame({"const": 1.0, "x": x})
    y = np.array([1.0, 2.0, 3.0, 99.0, 5.0])
    res = S.ols(X, y)
    assert res["n"] == 4  # the NaN row is dropped


def test_ols_reports_standard_errors_and_t():
    rng = np.random.default_rng(0)
    x = rng.normal(size=200)
    X = pd.DataFrame({"const": 1.0, "x": x})
    y = 1.0 + 0.5 * x + rng.normal(scale=0.1, size=200)
    res = S.ols(X, y)
    by_se = dict(zip(res["term"], res["se"]))
    by_t = dict(zip(res["term"], res["t"]))
    assert by_se["x"] > 0
    assert by_t["x"] > 5  # strong, precisely-estimated slope
