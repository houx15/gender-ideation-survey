#!/usr/bin/env python3
"""
cfps_outcomes.py — CFPS outcome-variable coding helpers (SPEC 5.2-5.6).

Coding decisions are derived from the real value labels in the .dta files and are
locked by tests/test_cfps_outcomes.py. Raw data is never modified; these return
new in-memory Series.

qea0 marital status: 1=never married, 2=married, 3=cohabiting, 4=divorced,
5=widowed; values <= 0 are missing codes.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

EVER_MARRIED_CODES = {2, 4, 5}   # has entered a registered marriage at least once
NOT_EVER_CODES = {1, 3}          # never married / cohabiting only


def ever_married(qea0: pd.Series) -> pd.Series:
    """1 if the respondent has ever been in a registered marriage, else 0; missing -> NaN."""
    out = pd.Series(np.nan, index=qea0.index, dtype="float64")
    out[qea0.isin(EVER_MARRIED_CODES)] = 1.0
    out[qea0.isin(NOT_EVER_CODES)] = 0.0
    return out


def currently_married(qea0: pd.Series) -> pd.Series:
    """1 if currently in a registered marriage (code 2), else 0; missing -> NaN."""
    out = pd.Series(np.nan, index=qea0.index, dtype="float64")
    out[qea0 == 2] = 1.0
    out[qea0.isin({1, 3, 4, 5})] = 0.0
    return out


def clean_continuous(s: pd.Series, lo: float, hi: float) -> pd.Series:
    """Keep values within [lo, hi]; everything else (missing codes, out-of-range) -> NaN."""
    return s.where(s.between(lo, hi))


# CFPS `employ`/`employ2014`: 1=employed; 0/2=unemployed, 3=left labour force,
# 9=not economically active; 8=ambiguous, negatives=missing.
NOT_EMPLOYED_CODES = {0, 2, 3, 9}


def employed(s: pd.Series) -> pd.Series:
    """1 if currently employed (code 1), 0 if non-working ({0,2,3,9}); else NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == 1] = 1.0
    out[s.isin(NOT_EMPLOYED_CODES)] = 0.0
    return out


def yes_no(s: pd.Series) -> pd.Series:
    """CFPS yes/no item: 1=是 -> 1; {0,5}=否 -> 0; not-applicable/missing -> NaN."""
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == 1] = 1.0
    out[s.isin({0, 5})] = 0.0
    return out


# ---- analysis_026 helpers (SPEC 5.2 individual-level family outcomes) ----

def first_marriage_age(marry_year: pd.Series, birth_year: pd.Series,
                       lo: int = 15, hi: int = 50) -> pd.Series:
    """Age at marriage = qea205y - birth_year, kept to [lo, hi].

    qea205y is the marriage-date year; negative sentinels (CFPS -8/-1) and any
    age outside [15, 50] -> NaN. Birth years must also be plausible (>=1900);
    upstream readers already filter birthy to [1920, 2010].
    """
    my = pd.to_numeric(marry_year, errors="coerce").where(lambda x: x.between(1940, 2024))
    by = pd.to_numeric(birth_year, errors="coerce").where(lambda x: x.between(1900, 2010))
    age = my - by
    return age.where(age.between(lo, hi))


def housework_hours_daily(s: pd.Series) -> pd.Series:
    """Daily housework hours (qq9010 / qq9010n), clipped to [0, 24]."""
    return clean_continuous(pd.to_numeric(s, errors="coerce"), lo=0, hi=24)


def ideal_children_count(s: pd.Series) -> pd.Series:
    """Ideal number of children (qm501, 2014 only), kept to [0, 10]."""
    return clean_continuous(pd.to_numeric(s, errors="coerce"), lo=0, hi=10)


# ---- analysis_027 helpers (SPEC 5.3 work / leadership) ----

_PROMOTED_CODES = {1, 2, 3}     # admin / technical / both
_NOT_PROMOTED_CODES = {78, 79}  # neither / no upward room


def promotion_indicator(s: pd.Series) -> pd.Series:
    """qg15 work-promotion: 1/2/3 -> 1; 78/79 -> 0; everything else -> NaN.

    Codes (CFPS 2014 & 2020):
      1 = 行政职务晋升 (admin)
      2 = 技术职称晋升 (technical title)
      3 = 两项都有 (both)
      78 = 两项都没有 (neither)
      79 = 这份工作无更高的职务或等级可供晋升 (no upward room)
      -10/-9/-8/-2/-1 = missing
    """
    s = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s.isin(_PROMOTED_CODES)] = 1.0
    out[s.isin(_NOT_PROMOTED_CODES)] = 0.0
    return out
