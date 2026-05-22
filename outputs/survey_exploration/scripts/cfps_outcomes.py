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
