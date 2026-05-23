"""Tests for cfps_panel.py — the CFPS 2014↔2020 ideation-change panel builder.

We test the pure transformations only (no .dta I/O); the loader functions
themselves are exercised by the analysis run script.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import cfps_panel as P


# ---------------------------------------------------------------------------
# clean_marital_status
# ---------------------------------------------------------------------------
def test_clean_marital_status_keeps_valid_codes():
    s = pd.Series([1, 2, 3, 4, 5])
    out = P.clean_marital_status(s)
    # 1=never, 2=married, 3=cohab, 4=divorced, 5=widowed
    assert out.tolist() == [1, 2, 3, 4, 5]


def test_clean_marital_status_drops_missing_codes_to_nan():
    s = pd.Series([-10, -9, -8, -2, -1, 0, 6, 7, np.nan])
    out = P.clean_marital_status(s)
    assert out.isna().all(), f"expected all NaN, got {out.tolist()}"


def test_clean_marital_status_does_not_zero_out_missing():
    """CRITICAL: missingness must be NaN, never 0 — else OLS models include them."""
    s = pd.Series([-9, -8, -1, np.nan, 2])
    out = P.clean_marital_status(s)
    assert out.iloc[:4].isna().all()
    assert (out == 0).sum() == 0  # never silently 0


# ---------------------------------------------------------------------------
# clean_employed
# ---------------------------------------------------------------------------
def test_clean_employed_maps_codes():
    # 0 失业 / 2 失业 -> 0; 1 在业 -> 1; 3 退出LF / 8 / 9 -> NaN
    s = pd.Series([0, 1, 2, 3, 8, 9])
    out = P.clean_employed(s)
    assert out.iloc[0] == 0
    assert out.iloc[1] == 1
    assert out.iloc[2] == 0
    assert out.iloc[3:].isna().all()


def test_clean_employed_negative_sentinels_become_nan():
    s = pd.Series([-10, -9, -8, -2, -1])
    assert P.clean_employed(s).isna().all()


# ---------------------------------------------------------------------------
# count_children_2014 / count_children_2020
# ---------------------------------------------------------------------------
def test_count_children_2014_counts_nonnull_pid_c_columns():
    df = pd.DataFrame({
        "pid_c1": [101, 102, np.nan],
        "pid_c2": [201, np.nan, np.nan],
        "pid_c3": [np.nan, np.nan, np.nan],
    })
    out = P.count_children_2014(df)
    assert out.tolist() == [2, 1, 0]


def test_count_children_2014_negative_sentinels_are_not_children():
    """pid_c columns sometimes carry -8 etc. as sentinels — must not count."""
    df = pd.DataFrame({
        "pid_c1": [101, -8, -1],
        "pid_c2": [-9, 202, np.nan],
    })
    out = P.count_children_2014(df)
    assert out.tolist() == [1, 1, 0]


def test_count_children_2020_uses_qf1_columns():
    df = pd.DataFrame({
        "qf1_a_1": [1, 2, np.nan],
        "qf1_a_2": [3, np.nan, np.nan],
        "qf1_a_3": [np.nan, np.nan, np.nan],
    })
    out = P.count_children_2020(df)
    assert out.tolist() == [2, 1, 0]


def test_count_children_2020_negative_sentinels_are_not_children():
    df = pd.DataFrame({
        "qf1_a_1": [1, -8, -1],
        "qf1_a_2": [-9, 2, np.nan],
    })
    out = P.count_children_2020(df)
    assert out.tolist() == [1, 1, 0]


# ---------------------------------------------------------------------------
# count_household_2014
# ---------------------------------------------------------------------------
def test_count_household_2014_counts_nonnull_pid_a_columns_plus_self():
    df = pd.DataFrame({
        "pid_a_1": [101, np.nan, np.nan],
        "pid_a_2": [102, 201, np.nan],
        "pid_a_3": [-8, np.nan, np.nan],   # sentinel does not count
    })
    out = P.count_household_2014(df)
    # +1 for the respondent themselves
    assert out.tolist() == [3, 2, 1]


def test_clean_household_2020_handles_sentinels():
    s = pd.Series([-10, -9, -8, -2, -1, 1, 4, 10])
    out = P.clean_household_2020(s)
    assert out.iloc[:5].isna().all()
    assert out.tolist()[5:] == [1.0, 4.0, 10.0]


# ---------------------------------------------------------------------------
# direction classifier
# ---------------------------------------------------------------------------
def test_classify_direction_uses_epsilon():
    delta = pd.Series([-0.20, -0.005, 0.0, 0.005, 0.20])
    out = P.classify_direction(delta, eps=0.05)
    assert out.tolist() == ["progressive", "stable", "stable", "stable", "traditional"]


def test_classify_direction_nan_passthrough():
    delta = pd.Series([np.nan, 0.10, -0.10])
    out = P.classify_direction(delta, eps=0.05)
    # NaN in -> NaN out
    assert pd.isna(out.iloc[0])
    assert out.iloc[1:].tolist() == ["traditional", "progressive"]


# ---------------------------------------------------------------------------
# transition encoder
# ---------------------------------------------------------------------------
def test_marital_transition_strings():
    a = pd.Series([1, 2, 2, 5])
    b = pd.Series([2, 4, 2, 5])
    out = P.marital_transition(a, b)
    # 1->2: entered_marriage; 2->4: divorced; 2->2: stable_married; 5->5: stable_widowed
    assert out.tolist() == [
        "entered_marriage", "divorced", "stable_married", "stable_widowed",
    ]


def test_marital_transition_handles_nan():
    a = pd.Series([1, np.nan, 2])
    b = pd.Series([np.nan, 2, np.nan])
    out = P.marital_transition(a, b)
    assert all(pd.isna(out))


# ---------------------------------------------------------------------------
# numeric delta helper
# ---------------------------------------------------------------------------
def test_numeric_delta_basic():
    a = pd.Series([0.5, 0.3, np.nan, 0.8])
    b = pd.Series([0.7, 0.1, 0.4, np.nan])
    out = P.numeric_delta(a, b)
    np.testing.assert_allclose(out.iloc[:2].values, [0.2, -0.2])
    assert pd.isna(out.iloc[2])
    assert pd.isna(out.iloc[3])
