#!/usr/bin/env python3
"""
ceps_outcomes.py — CEPS coding helpers for the gendered resource-allocation analysis.

Decisions are read from the real value labels and locked by tests/test_ceps_outcomes.py.
Raw data is never modified.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

# education expectation (ba18/b31): 1..9 ordinal; 10 = 无所谓 ("doesn't matter") = missing.
COLLEGE_PLUS = {6, 7, 8, 9}     # 大学专科 and above
BELOW_COLLEGE = {1, 2, 3, 4, 5}


def female(a01: pd.Series) -> pd.Series:
    """1 if female (a01==2), 0 if male (a01==1), else NaN."""
    out = pd.Series(np.nan, index=a01.index, dtype="float64")
    out[a01 == 2] = 1.0
    out[a01 == 1] = 0.0
    return out


def expect_college_plus(s: pd.Series) -> pd.Series:
    """1 if the (parental/own) education expectation is college or above ({6,7,8,9}),
    0 if below college ({1..5}); 10 ('doesn't matter') and negatives/missing -> NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin(COLLEGE_PLUS)] = 1.0
    out[s.isin(BELOW_COLLEGE)] = 0.0
    return out


def yes12(s: pd.Series) -> pd.Series:
    """CEPS yes/no item: 1=是/有 -> 1, 2=否/没有 -> 0, else NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == 1] = 1.0
    out[s == 2] = 0.0
    return out


def hours_hm(hours: pd.Series, minutes: pd.Series, hmax: float = 24.0) -> pd.Series:
    """Combine an hours column and a minutes column into decimal hours.

    Hours outside [0, hmax] -> NaN (the whole value is missing). Minutes outside
    [0, 59] are treated as 0 (respondents often fill only the hours field).
    """
    h = hours.where(hours.between(0, hmax))
    m = minutes.where(minutes.between(0, 59), other=0.0)
    return h + m / 60.0
