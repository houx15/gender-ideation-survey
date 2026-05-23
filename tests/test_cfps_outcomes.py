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


# ---- first-marriage age (SPEC 5.2, analysis_026) ----
# Computed as qea205y (marriage year) - birth_year.
# - qea2071 == 1 restricts to *first* marriage where available.
# - Filter plausible range [15, 50]; ages outside -> NaN.
# - Missing in either input -> NaN.

def test_first_marriage_age_subtracts_birth_year():
    marry_y = pd.Series([1990, 2005, 2018])
    birthy = pd.Series([1965, 1980, 1995])
    out = C.first_marriage_age(marry_y, birthy)
    assert list(out) == [25.0, 25.0, 23.0]


def test_first_marriage_age_filters_implausible_ages():
    marry_y = pd.Series([1990, 2005, 2010])      # ages would be 60 / 5 / 30
    birthy = pd.Series([1930, 2000, 1980])
    out = C.first_marriage_age(marry_y, birthy)
    assert math.isnan(out[0])                    # 60 -> NaN (too old for first marr)
    assert math.isnan(out[1])                    # 5  -> NaN (too young)
    assert out[2] == 30.0


def test_first_marriage_age_missing_inputs_are_nan():
    marry_y = pd.Series([float("nan"), 2005, -8])
    birthy = pd.Series([1980, float("nan"), 1980])
    out = C.first_marriage_age(marry_y, birthy)
    assert all(math.isnan(x) for x in out)


def test_first_marriage_age_filters_negative_sentinel_marry_year():
    marry_y = pd.Series([-9, -1, 1995])
    birthy = pd.Series([1970, 1970, 1970])
    out = C.first_marriage_age(marry_y, birthy)
    assert math.isnan(out[0])
    assert math.isnan(out[1])
    assert out[2] == 25.0


# ---- housework_hours_daily ----
def test_housework_hours_daily_clips_to_valid_day():
    s = pd.Series([0, 1.5, 12, 24])
    out = C.housework_hours_daily(s)
    assert list(out) == [0.0, 1.5, 12.0, 24.0]


def test_housework_hours_daily_drops_out_of_range_and_sentinels():
    s = pd.Series([-8, -1, 25, 100])
    out = C.housework_hours_daily(s)
    assert all(math.isnan(x) for x in out)


# ---- ideal_children_count ----
def test_ideal_children_count_keeps_zero_to_ten():
    s = pd.Series([0, 1, 2, 3, 10])
    out = C.ideal_children_count(s)
    assert list(out) == [0.0, 1.0, 2.0, 3.0, 10.0]


def test_ideal_children_count_drops_sentinels_and_implausible():
    s = pd.Series([-8, -1, 11, 99])
    out = C.ideal_children_count(s)
    assert all(math.isnan(x) for x in out)


# ---- promotion_indicator (qg15, analysis_027 / SPEC 5.3) ----
# Codes (both waves):
#   1 = 行政职务晋升 (admin), 2 = 技术职称晋升 (technical), 3 = 两项都有 (both)
#       -> all three -> 1 (got a promotion)
#   78 = 两项都没有 (neither), 79 = 这份工作无更高等级可供晋升 (no upward room)
#       -> both -> 0 (no promotion)
#   negatives (-8/-1/-2/-9/-10) -> NaN

def test_promotion_indicator_codes_promoted_as_one():
    s = pd.Series([1, 2, 3])
    out = C.promotion_indicator(s)
    assert list(out) == [1.0, 1.0, 1.0]


def test_promotion_indicator_no_promotion_codes_as_zero():
    s = pd.Series([78, 79])
    out = C.promotion_indicator(s)
    assert list(out) == [0.0, 0.0]


def test_promotion_indicator_missing_codes_are_nan():
    s = pd.Series([-8, -1, -2, -9, -10])
    out = C.promotion_indicator(s)
    assert all(math.isnan(x) for x in out)


def test_promotion_indicator_unknown_values_are_nan():
    s = pd.Series([0, 4, 5, 100])
    out = C.promotion_indicator(s)
    assert all(math.isnan(x) for x in out)
