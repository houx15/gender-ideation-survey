"""Characterization tests locking the documented gender-ideation recoding.

These pin the behavior described in surveys/processed/methodology.md so later
refactors and new analyses can't silently change the index convention
([0,1], 1 = most traditional).
"""
import math
import numpy as np
import pandas as pd
import pytest

import ideation_lib as L


# ---------- normalize_item ----------

def test_traditional_item_agree_high_maps_strong_agree_to_one():
    # CFPS-style: scale 1..5, agree_code=5, traditional item.
    s = pd.Series([1, 3, 5])
    out = L.normalize_item(s, scale_max=5, agree_code=5, direction="traditional")
    assert list(out) == [0.0, 0.5, 1.0]


def test_progressive_item_agree_high_maps_strong_agree_to_zero():
    # CFPS-style progressive item (e.g., men share housework): agreeing => egalitarian.
    s = pd.Series([1, 3, 5])
    out = L.normalize_item(s, scale_max=5, agree_code=5, direction="progressive")
    assert list(out) == [1.0, 0.5, 0.0]


def test_traditional_item_agree_low_maps_strong_agree_to_one():
    # ACWF-style: scale 1..5, agree_code=1 (raw 1 = strongly agree), traditional item.
    s = pd.Series([1, 3, 5])
    out = L.normalize_item(s, scale_max=5, agree_code=1, direction="traditional")
    assert list(out) == [1.0, 0.5, 0.0]


def test_four_point_scale_traditional_agree_low():
    # ACWF 2000/2010: scale 1..4, agree_code=1, traditional.
    s = pd.Series([1, 2, 3, 4])
    out = L.normalize_item(s, scale_max=4, agree_code=1, direction="traditional")
    assert list(out) == [1.0, pytest.approx(2 / 3), pytest.approx(1 / 3), 0.0]


def test_out_of_range_values_become_nan():
    # missing codes outside [1, scale_max] must be NaN, not scored.
    s = pd.Series([-8, -1, 0, 1, 5, 8, 99])
    out = L.normalize_item(s, scale_max=5, agree_code=5, direction="traditional")
    assert [math.isnan(x) for x in out] == [True, True, True, False, False, True, True]
    assert out[3] == 0.0 and out[4] == 1.0


# ---------- cronbach_alpha ----------

def test_cronbach_alpha_identical_items_is_one():
    # perfectly correlated items -> alpha = 1.
    base = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    df = pd.DataFrame({"a": base, "b": base, "c": base})
    assert L.cronbach_alpha(df) == pytest.approx(1.0, abs=1e-9)


def test_cronbach_alpha_too_few_items_is_nan():
    df = pd.DataFrame({"a": [0.1, 0.2, 0.3]})
    assert math.isnan(L.cronbach_alpha(df))
