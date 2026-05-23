"""Tests for descriptive_stats.py — descriptive rows, effect sizes, CIs."""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "outputs" / "survey_exploration" / "scripts"))
import descriptive_stats as D  # noqa: E402


# ---------- describe_var ---------- #

def test_describe_var_basic():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, np.nan, np.nan])
    r = D.describe_var(s, name="x", explanation="test")
    assert r["name"] == "x"
    assert r["explanation"] == "test"
    assert r["n"] == 4
    assert r["mean"] == pytest.approx(2.5)
    assert r["sd"] == pytest.approx(np.std([1, 2, 3, 4], ddof=1))
    assert r["min"] == 1.0
    assert r["max"] == 4.0
    assert r["n_missing"] == 2
    assert r["missing_pct"] == pytest.approx(100 * 2 / 6)


def test_describe_var_all_missing():
    s = pd.Series([np.nan, np.nan])
    r = D.describe_var(s, name="x")
    assert r["n"] == 0
    assert r["n_missing"] == 2
    assert np.isnan(r["mean"]) and np.isnan(r["sd"])


# ---------- effect sizes ---------- #

def test_cohen_d_known_value():
    # textbook example: a ~ N(0,1) n=50, b ~ N(0.5,1) n=50  -> d ≈ -0.5
    rng = np.random.default_rng(0)
    a = rng.normal(0.0, 1.0, 5000)
    b = rng.normal(0.5, 1.0, 5000)
    d = D.cohen_d(a, b)
    assert d == pytest.approx(-0.5, abs=0.05)


def test_cohen_d_constant_inputs():
    a = np.array([1.0, 1.0, 1.0])
    b = np.array([2.0, 2.0, 2.0])
    # zero pooled SD -> NaN, not crash
    assert np.isnan(D.cohen_d(a, b))


def test_hedges_g_approaches_cohen_d_for_large_n():
    rng = np.random.default_rng(1)
    a = rng.normal(0.0, 1.0, 10000)
    b = rng.normal(0.3, 1.0, 10000)
    d = D.cohen_d(a, b)
    g = D.hedges_g(a, b)
    # correction factor ~ 1 - 3/(4*(n1+n2)-9); negligible at n=20k
    assert abs(d - g) < 0.001


# ---------- Welch confidence interval ---------- #

def test_welch_ci_known_difference():
    # Two normals with known means -> CI brackets the true difference
    rng = np.random.default_rng(2)
    a = rng.normal(0.0, 1.0, 2000)
    b = rng.normal(0.25, 1.0, 2000)
    r = D.welch_ci_diff(a, b, alpha=0.05)
    assert r["diff"] == pytest.approx(np.mean(a) - np.mean(b), abs=1e-9)
    assert r["ci_lo"] < r["diff"] < r["ci_hi"]
    assert r["p"] < 0.001          # large n -> significant
    assert r["df"] > 1000


def test_welch_ci_handles_constant_groups():
    a = np.array([1.0, 1.0, 1.0])
    b = np.array([1.0, 1.0, 1.0])
    r = D.welch_ci_diff(a, b)
    assert r["diff"] == 0.0
    # CI should be (0,0) or NaN; either way p is 1.0 or NaN
    assert np.isnan(r["p"]) or r["p"] == pytest.approx(1.0, abs=1e-9)


# ---------- bootstrap CI of the mean ---------- #

def test_bootstrap_mean_ci_brackets_true_mean():
    rng = np.random.default_rng(3)
    arr = rng.normal(0.7, 1.0, 500)
    r = D.bootstrap_mean_ci(arr, n_boot=1000, seed=0, alpha=0.05)
    assert r["mean"] == pytest.approx(np.mean(arr))
    assert r["ci_lo"] < r["mean"] < r["ci_hi"]
    # interval should contain true mean
    assert r["ci_lo"] < 0.7 < r["ci_hi"]


def test_bootstrap_mean_ci_handles_empty():
    r = D.bootstrap_mean_ci(np.array([]), n_boot=200, seed=0)
    assert np.isnan(r["mean"]) and np.isnan(r["ci_lo"]) and np.isnan(r["ci_hi"])
