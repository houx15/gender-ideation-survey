#!/usr/bin/env python3
"""
cgss_outcomes.py — CGSS outcome-variable coding helpers (analysis_036).

Coding decisions follow the real value labels read from CGSS 2010-2023 .dta
files and are locked by tests/test_cgss_outcomes.py.

a69 marital status: 1=未婚, 2=同居, 3=初婚有配偶, 4=再婚有配偶, 5=分居未离婚,
6=离婚, 7=丧偶.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

EVER_MARRIED_CODES = {3, 4, 5, 6, 7}   # has entered a registered marriage
NOT_EVER_CODES = {1, 2}                # never married (or cohabiting only)


def ever_married_cgss(s: pd.Series) -> pd.Series:
    """1 if respondent has ever been in a registered marriage; 0 if not; missing -> NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin(EVER_MARRIED_CODES)] = 1.0
    out[s.isin(NOT_EVER_CODES)] = 0.0
    return out


def currently_married_cgss(s: pd.Series) -> pd.Series:
    """1 if currently in a registered marriage ({3,4,5}); else 0; missing -> NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin({3, 4, 5})] = 1.0
    out[s.isin({1, 2, 6, 7})] = 0.0
    return out


def mgmt_activity_cgss(s: pd.Series) -> pd.Series:
    """1 if respondent currently manages others (a59f ∈ {1,2}); 0 if not ({3,4});
    98/99/other -> NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin({1, 2})] = 1.0
    out[s.isin({3, 4})] = 0.0
    return out


def soe_indicator_cgss(s: pd.Series) -> pd.Series:
    """1 if respondent's current employer is state-sector (a59k ∈ {1=国有, 2=集体}),
    a rough proxy for 编制 (in-establishment). 0 for private/foreign/other; NaN
    for unknown.

    State-sector employment in CGSS overstates true 编制 (which is more restrictive)
    but is the cleanest available proxy in CGSS' work-unit ownership variable.
    """
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin({1, 2})] = 1.0
    out[s.isin({3, 4, 5, 6})] = 0.0
    return out


def marriage_sat_cgss(s: pd.Series) -> pd.Series:
    """CGSS d31 marriage satisfaction.  Raw codes: 1=非常满意 ... 5=非常不满意.
    Returned REVERSED so higher = more satisfied (matches CFPS qm801 convention
    in analysis_026).  98/99/other -> NaN."""
    s = pd.to_numeric(s, errors="coerce")
    valid = s.isin({1, 2, 3, 4, 5})
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[valid] = (6 - s[valid]).astype("float64")
    return out


def ideal_children_cgss(s: pd.Series) -> pd.Series:
    """CGSS a371 ideal children count if no policy constraint.  Clip to [0, 10];
    99 sentinel and negatives -> NaN."""
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s.between(0, 10))


def num_children_cgss(sons: pd.Series, daughters: pd.Series) -> pd.Series:
    """Sum of cleaned son count + daughter count (a681 + a682).  Each component
    clipped to [0, 15]; sum then re-clipped to [0, 15].  NaN if either side is
    missing/sentinel."""
    sons_c = pd.to_numeric(sons, errors="coerce").where(lambda x: x.between(0, 15))
    daus_c = pd.to_numeric(daughters, errors="coerce").where(lambda x: x.between(0, 15))
    total = sons_c + daus_c
    return total.where(total.between(0, 15))


# CGSS personal income (a8a): sentinels include 9999996/97/98/99.  Treat
# anything >= 9_999_996 as missing.
def personal_income_cgss(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.where((s >= 0) & (s < 9_999_996))


def weekly_hours_cgss(s: pd.Series) -> pd.Series:
    """CGSS weekly work hours.  Valid 0..168.  Sentinels 998/999/9998/9999/negative
    -> NaN."""
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s.between(0, 168))


def age_first_marriage_cgss(marry_year: pd.Series, birth_year: pd.Series,
                            lo: int = 15, hi: int = 50) -> pd.Series:
    """Age at first marriage = a70 - birth_year, clipped to [lo, hi].
    marry_year ∈ {0, 9999, large sentinels} -> NaN.  birth_year outside
    plausible 1900..2010 -> NaN."""
    my = pd.to_numeric(marry_year, errors="coerce").where(lambda x: x.between(1940, 2024))
    by = pd.to_numeric(birth_year, errors="coerce").where(lambda x: x.between(1900, 2010))
    age = my - by
    return age.where(age.between(lo, hi))
