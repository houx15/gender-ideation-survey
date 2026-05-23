#!/usr/bin/env python3
"""
acwf_outcomes.py — ACWF (中国妇女地位调查) outcome-variable coding helpers
for analysis_037.

Locked by tests/test_acwf_outcomes.py.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def wife_does_more_housework(s: pd.Series) -> pd.Series:
    """ACWF "夫妻间谁承担家务劳动更多" (e8_c in 2000 / F6B in 2010).
    1=丈夫, 2=妻子, 3=差不多, 7=不适用, 8/9 sentinels.  Return 1 iff wife
    does more (code 2); 0 if husband or similar ({1,3}); else NaN.
    """
    s = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == 2] = 1.0
    out[s.isin({1, 3})] = 0.0
    return out


def leadership_ever(s: pd.Series) -> pd.Series:
    """ACWF "是否担任过领导职务" (d4_a in 2000 / E6A in 2010).
    0=否, 1=是, 7=不适用, 9=不回答.  Return 0/1/NaN.
    """
    s = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == 1] = 1.0
    out[s == 0] = 0.0
    return out


def housework_hours_acwf_1990(s: pd.Series) -> pd.Series:
    """ACWF 1990 `h_work` housework MINUTES per day.  Returned in HOURS/day.
    Clip raw to [0, 1080] minutes (≤ 18 h/day); else NaN.
    """
    s = pd.to_numeric(s, errors="coerce")
    cleaned = s.where(s.between(0, 1080))
    return cleaned / 60.0


def first_marriage_age_acwf_1990(s: pd.Series, lo: int = 15, hi: int = 50) -> pd.Series:
    """ACWF 1990 `w32` self-reported age at first marriage.  Clip to [lo, hi]."""
    s = pd.to_numeric(s, errors="coerce")
    return s.where(s.between(lo, hi))


def ever_married_acwf_1990(s: pd.Series) -> pd.Series:
    """ACWF 1990 `w35` current marital status.
    1=未婚, 2=有配偶(初婚), 3=有配偶(再婚), 4=离婚/分居, 5=丧偶.
    Ever-married: {2,3,4,5}=1; {1}=0; else NaN.
    """
    s = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin({2, 3, 4, 5})] = 1.0
    out[s == 1] = 0.0
    return out
