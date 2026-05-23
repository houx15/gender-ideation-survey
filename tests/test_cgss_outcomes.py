"""Tests for CGSS outcome-coding helpers (analysis_036 replication of 026/027).

Coding decisions encoded here (from the real value labels in CGSS .dta files):

- a69 marital status: 1=未婚, 2=同居, 3=初婚有配偶, 4=再婚有配偶, 5=分居未离婚,
  6=离婚, 7=丧偶.
- ever_married_cgss: respondent has been formally married at least once -> {3,4,5,6,7}=1;
  {1,2}=0 (cohabiting counts as not-yet-formally-married, matching CFPS convention).
- currently_married_cgss: currently in a registered marriage -> {3,4,5}=1; {1,2,6,7}=0.

- a59f management activity: 1=只管别人, 2=既管理又被管理, 3=只受管理, 4=既不管也不被管.
- mgmt_activity_cgss: holds a management role -> {1,2}=1; {3,4}=0; 98/99/NaN = NaN.

- a59k unit ownership: 1=国有, 2=集体, 3=私有, 4=港澳台, 5=外资, 6=其他.
- soe_indicator_cgss (state-sector proxy for 编制): {1,2}=1; {3,4,5,6}=0; 98/99/NaN = NaN.

- d31 marriage satisfaction: 1=非常满意 ... 5=非常不满意.  We REVERSE so that
  higher = more satisfied (1..5 -> 5..1), matching CFPS qm801 direction in
  analysis_026.  98/99 -> NaN.

- a371 ideal children: 0..10 valid; 99 sentinel.  Clip to [0, 10].
- a681/a682 children counts (sons/daughters): 0..15 valid; 99 sentinel; sum
  to num_children.
- a8a personal annual total income: any value >= 9_999_996 is a missing/refuse
  sentinel.  Clip to [0, 9_999_995] then optionally log.
- a53a weekly work hours: 0..168 valid; >= 998 sentinel (998/999 / 9998 etc).
- a70 first-marriage year, with birth-year, gives first marriage age 15..50.
"""
import math
import pandas as pd
import pytest

import cgss_outcomes as G


# -- ever_married / currently_married ------------------------------------- #

def test_ever_married_cgss_codes_3to7_as_married():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7])
    out = G.ever_married_cgss(s)
    assert list(out) == [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0]


def test_ever_married_cgss_missing_is_nan():
    s = pd.Series([0, -1, 98, 99])
    assert all(math.isnan(x) for x in G.ever_married_cgss(s))


def test_currently_married_cgss_only_codes_3_4_5_are_one():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7])
    out = G.currently_married_cgss(s)
    assert list(out) == [0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0]


# -- mgmt_activity --------------------------------------------------------- #

def test_mgmt_activity_codes_1_and_2_are_one():
    s = pd.Series([1, 2, 3, 4])
    out = G.mgmt_activity_cgss(s)
    assert list(out) == [1.0, 1.0, 0.0, 0.0]


def test_mgmt_activity_sentinels_are_nan():
    s = pd.Series([98, 99, -1, 0])
    assert all(math.isnan(x) for x in G.mgmt_activity_cgss(s))


# -- SOE / 编制 ------------------------------------------------------------ #

def test_soe_indicator_state_sector_one():
    s = pd.Series([1, 2, 3, 4, 5, 6])
    out = G.soe_indicator_cgss(s)
    assert list(out) == [1.0, 1.0, 0.0, 0.0, 0.0, 0.0]


def test_soe_indicator_sentinels_nan():
    s = pd.Series([98, 99])
    assert all(math.isnan(x) for x in G.soe_indicator_cgss(s))


# -- marriage satisfaction ------------------------------------------------- #

def test_marriage_sat_reverses_so_higher_is_more_satisfied():
    """d31 raw 1=非常满意 -> reversed 5; raw 5=非常不满意 -> reversed 1."""
    s = pd.Series([1, 2, 3, 4, 5])
    out = G.marriage_sat_cgss(s)
    assert list(out) == [5.0, 4.0, 3.0, 2.0, 1.0]


def test_marriage_sat_sentinels_are_nan():
    s = pd.Series([0, -1, 98, 99])
    assert all(math.isnan(x) for x in G.marriage_sat_cgss(s))


# -- ideal children -------------------------------------------------------- #

def test_ideal_children_clips_to_0_10():
    s = pd.Series([0, 2, 5, 10, 11, 99])
    out = G.ideal_children_cgss(s)
    assert out[0] == 0.0
    assert out[1] == 2.0
    assert out[2] == 5.0
    assert out[3] == 10.0
    assert math.isnan(out[4])  # 11
    assert math.isnan(out[5])  # 99


def test_ideal_children_negative_is_nan():
    s = pd.Series([-1, -8])
    assert all(math.isnan(x) for x in G.ideal_children_cgss(s))


# -- num_children = sons + daughters --------------------------------------- #

def test_num_children_sums_clean_sons_daughters():
    sons = pd.Series([1, 0, 2, 99])
    daus = pd.Series([0, 1, 1, 0])
    out = G.num_children_cgss(sons, daus)
    assert out[0] == 1.0
    assert out[1] == 1.0
    assert out[2] == 3.0
    assert math.isnan(out[3])  # 99 sons -> NaN


def test_num_children_clips_to_0_15():
    sons = pd.Series([0, 7, 7, 0])
    daus = pd.Series([0, 8, 9, 99])
    out = G.num_children_cgss(sons, daus)
    assert out[0] == 0.0
    assert out[1] == 15.0
    assert math.isnan(out[2])  # 16 out of range
    assert math.isnan(out[3])  # 99 daus -> NaN


# -- log personal income --------------------------------------------------- #

def test_personal_income_cgss_strips_sentinels():
    s = pd.Series([0.0, 5000.0, 50_000.0, 9_999_996, 9_999_998, 9_999_999])
    out = G.personal_income_cgss(s)
    assert out[0] == 0.0
    assert out[1] == 5000.0
    assert out[2] == 50_000.0
    assert math.isnan(out[3])
    assert math.isnan(out[4])
    assert math.isnan(out[5])


# -- weekly work hours ----------------------------------------------------- #

def test_weekly_hours_clips_to_0_168():
    s = pd.Series([0, 8, 40, 80, 168, 999, 998, -1])
    out = G.weekly_hours_cgss(s)
    assert list(out[:5]) == [0.0, 8.0, 40.0, 80.0, 168.0]
    assert math.isnan(out[5])  # 999
    assert math.isnan(out[6])  # 998 sentinel
    assert math.isnan(out[7])  # negative


# -- age at first marriage ------------------------------------------------- #

def test_age_first_marriage_cgss_subtracts_birth_year():
    marry = pd.Series([2000, 2010, 1990, 9999, 0])
    born = pd.Series([1980, 1985, 1970, 1990, 1985])
    out = G.age_first_marriage_cgss(marry, born)
    assert out[0] == 20.0
    assert out[1] == 25.0
    assert out[2] == 20.0
    assert math.isnan(out[3])  # year 9999 missing
    assert math.isnan(out[4])  # year 0 (not yet married)


def test_age_first_marriage_cgss_outside_15_50_is_nan():
    marry = pd.Series([2000, 2000])
    born = pd.Series([1990, 1940])
    out = G.age_first_marriage_cgss(marry, born)
    assert out[0] == 10.0 if False else math.isnan(out[0])  # age 10 < 15 -> NaN
    assert math.isnan(out[1])                                 # age 60 > 50 -> NaN
