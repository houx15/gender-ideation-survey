"""Tests for CFPS outcome-coding helpers (family-practice analysis, SPEC 5.2).

Coding decisions encoded here (from the real value labels):
- qea0 marital status: 1=never married, 2=married, 3=cohabiting,
  4=divorced, 5=widowed; <=0 = missing.
- ever_married: entered formal marriage at least once -> {2,4,5}=1; {1,3}=0; missing=NaN.
  (cohabiting counts as not-yet-formally-married.)
- currently_married: in a registered marriage now -> 2=1; {1,3,4,5}=0; missing=NaN.
- clean_continuous: keep values within [lo, hi]; everything else (e.g. -8) -> NaN.
"""
import math
import pandas as pd

import cfps_outcomes as C


def test_ever_married_classifies_marriage_history():
    s = pd.Series([1, 2, 3, 4, 5])
    out = C.ever_married(s)
    assert list(out) == [0.0, 1.0, 0.0, 1.0, 1.0]


def test_ever_married_missing_codes_are_nan():
    s = pd.Series([-8, -1, 0])
    out = C.ever_married(s)
    assert all(math.isnan(x) for x in out)


def test_currently_married_only_registered_marriage_is_one():
    s = pd.Series([1, 2, 3, 4, 5])
    out = C.currently_married(s)
    assert list(out) == [0.0, 1.0, 0.0, 0.0, 0.0]


def test_currently_married_missing_is_nan():
    s = pd.Series([-8, 0])
    assert all(math.isnan(x) for x in C.currently_married(s))


def test_clean_continuous_keeps_in_range_nans_rest():
    s = pd.Series([-8, 0, 2, 24, 25])
    out = C.clean_continuous(s, lo=0, hi=24)
    assert out[0] != out[0]          # -8 -> NaN
    assert list(out[1:4]) == [0.0, 2.0, 24.0]
    assert math.isnan(out[4])        # 25 -> NaN


def test_clean_continuous_default_lower_bound_excludes_negatives():
    s = pd.Series([-1, -2, 5])
    out = C.clean_continuous(s, lo=0, hi=100)
    assert math.isnan(out[0]) and math.isnan(out[1])
    assert out[2] == 5.0
