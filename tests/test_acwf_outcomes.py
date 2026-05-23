"""Tests for ACWF outcome-coding helpers (analysis_037 replication).

Coding decisions encoded here (from the real value labels in
中国妇女地位调查 .dta files):

- e8_c (2000) / F6B (2010) "夫妻间谁承担家务劳动更多":
  1=丈夫, 2=妻子, 3=差不多, 7=不适用, 8/9 sentinels.
  wife_does_more_housework: 2=1, {1,3}=0; else NaN.

- d4_a (2000) / E6A (2010) "是否担任过领导职务":
  0=否, 1=是, 7=不适用, 9=不回答.
  leadership_ever: 1=1, 0=0; else NaN.

- ACWF 1990 h_work "家务劳动时间" in minutes/day.  Valid 0..1080
  (0..18 hr/day).  Anything else NaN.  Returned in HOURS/day.

- ACWF 1990 w32 "您的初婚年龄" directly in years.  Clip [15, 50];
  0/sentinels NaN.

- ACWF 1990 w35 marital status: 1=未婚, 2=初婚, 3=再婚, 4=离/分,
  5=丧偶.  ever_married_acwf = {2,3,4,5}=1, {1}=0.
"""
import math
import pandas as pd

import acwf_outcomes as A


def test_wife_does_more_housework_code_2_is_one():
    s = pd.Series([1, 2, 3, 7, 8, 9])
    out = A.wife_does_more_housework(s)
    assert out[0] == 0.0
    assert out[1] == 1.0
    assert out[2] == 0.0
    assert math.isnan(out[3])
    assert math.isnan(out[4])
    assert math.isnan(out[5])


def test_leadership_ever_codes_0_1_only():
    s = pd.Series([0, 1, 7, 9])
    out = A.leadership_ever(s)
    assert out[0] == 0.0
    assert out[1] == 1.0
    assert math.isnan(out[2])
    assert math.isnan(out[3])


def test_housework_hours_1990_converts_minutes_to_hours():
    s = pd.Series([0, 60, 120, 1080, 1081, 9999, -1])
    out = A.housework_hours_acwf_1990(s)
    assert out[0] == 0.0
    assert out[1] == 1.0
    assert out[2] == 2.0
    assert out[3] == 18.0
    assert math.isnan(out[4])
    assert math.isnan(out[5])
    assert math.isnan(out[6])


def test_first_marriage_age_1990_clips_15_50():
    s = pd.Series([14, 15, 25, 50, 51, 0, 99])
    out = A.first_marriage_age_acwf_1990(s)
    assert math.isnan(out[0])
    assert out[1] == 15.0
    assert out[2] == 25.0
    assert out[3] == 50.0
    assert math.isnan(out[4])
    assert math.isnan(out[5])
    assert math.isnan(out[6])


def test_ever_married_acwf_1990():
    s = pd.Series([1, 2, 3, 4, 5])
    out = A.ever_married_acwf_1990(s)
    assert list(out) == [0.0, 1.0, 1.0, 1.0, 1.0]


def test_ever_married_acwf_1990_sentinels_nan():
    s = pd.Series([0, 9])
    assert all(math.isnan(x) for x in A.ever_married_acwf_1990(s))
