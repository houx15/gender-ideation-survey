"""Tests for CEPS resource-allocation coding helpers (SPEC 5.5).

Coding decisions from the real value labels:
- a01 gender: 1=男, 2=女 -> female = (a01==2).
- education expectation (ba18/b31): ordinal 1..9 (1=stop now ... 7=BA, 8=master, 9=PhD);
  **10 = 无所谓 ("doesn't matter") must be MISSING, not the top of the scale.**
  expect_college_plus = 1 for {6,7,8,9}, 0 for {1..5}, NaN for 10/negatives/missing.
- CEPS yes/no items use 1=yes, 2=no (unlike CFPS) -> yes12.
- time-use items come as separate hour + minute columns -> hours_hm.
"""
import math
import numpy as np
import pandas as pd

import ceps_outcomes as E


def test_female_codes_two_as_one():
    s = pd.Series([1, 2, 1, 2])
    assert list(E.female(s)) == [0.0, 1.0, 0.0, 1.0]


def test_female_missing_is_nan():
    s = pd.Series([-9, 0, 3])
    assert all(math.isnan(x) for x in E.female(s))


def test_expect_college_plus_splits_at_college():
    s = pd.Series([1, 5, 6, 7, 8, 9])
    assert list(E.expect_college_plus(s)) == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0]


def test_expect_college_plus_dont_care_code_is_nan():
    # 10 = "doesn't matter" must NOT count as highest expectation.
    s = pd.Series([10, -9, -1])
    assert all(math.isnan(x) for x in E.expect_college_plus(s))


def test_yes12_maps_one_yes_two_no():
    s = pd.Series([1, 2])
    assert list(E.yes12(s)) == [1.0, 0.0]


def test_yes12_other_codes_nan():
    s = pd.Series([-9, 3, 0])
    assert all(math.isnan(x) for x in E.yes12(s))


def test_hours_hm_combines_hours_and_minutes():
    h = pd.Series([1.0, 2.0])
    m = pd.Series([30.0, 0.0])
    assert list(E.hours_hm(h, m)) == [1.5, 2.0]


def test_hours_hm_invalid_minutes_treated_as_zero_when_hours_valid():
    h = pd.Series([2.0])
    m = pd.Series([-9.0])
    assert list(E.hours_hm(h, m)) == [2.0]


def test_hours_hm_invalid_hours_is_nan():
    h = pd.Series([-9.0])
    m = pd.Series([30.0])
    assert math.isnan(E.hours_hm(h, m)[0])
