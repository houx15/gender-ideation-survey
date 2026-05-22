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


# ---- employment / yes-no helpers (SPEC 5.3) ----
# employ: 1 = employed; 0/2 = unemployed, 3 = left labour force, 9 = not economically
# active -> 0; 8 (ambiguous) and negatives -> NaN.

def test_employed_one_for_working_zero_for_non_working():
    s = pd.Series([1, 0, 2, 3, 9])
    out = C.employed(s)
    assert list(out) == [1.0, 0.0, 0.0, 0.0, 0.0]


def test_employed_ambiguous_and_missing_are_nan():
    s = pd.Series([8, -8, -1])
    assert all(math.isnan(x) for x in C.employed(s))


# yes_no: qg14/qg17 style -> 1=是 ->1 ; 0=否 / 5=否 ->0 ; 79/-8/.. -> NaN

def test_yes_no_maps_yes_to_one_no_to_zero():
    s = pd.Series([1, 0, 5])
    assert list(C.yes_no(s)) == [1.0, 0.0, 0.0]


def test_yes_no_not_applicable_and_missing_are_nan():
    s = pd.Series([79, -8, -2])
    assert all(math.isnan(x) for x in C.yes_no(s))
