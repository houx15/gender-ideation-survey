#!/usr/bin/env python3
"""cfps_panel.py — build the CFPS 2014↔2020 ideation-change panel.

Used by analysis_024 (supplementary RQ 5.1: who changes and what predicts it).

Two layers:
  * Pure cleaning / transition helpers — unit tested (test_cfps_panel.py).
  * A loader (build_panel) that joins the recoded CFPS 2014 + 2020 surveys
    on pid and returns one row per pid with baseline characteristics and
    Δ-variables.

Conventions (same as the rest of analysis_023):
  * Missing codes (-1, -2, -8, -9, -10, 0) collapse to NaN. Never silently 0.
  * Ideation: 0 = most progressive, 1 = most traditional. Δ = 2020 − 2014.
  * Direction: "progressive" if Δ ≤ −eps, "traditional" if Δ ≥ +eps, else "stable".
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Iterable

import numpy as np
import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import ideation_lib as L  # noqa: E402

ROOT = L.ROOT

# Marital codes that have substantive meaning. Everything else -> NaN.
_VALID_MARITAL = {1, 2, 3, 4, 5}
_MARITAL_NAME = {
    1: "never_married",
    2: "married",
    3: "cohab",
    4: "divorced",
    5: "widowed",
}

# CFPS missing-code sentinels (same across 2014/2020 modules).
_MISSING = {-10, -9, -8, -2, -1, 0}


# ---------------------------------------------------------------------------
# Pure cleaning helpers (unit-tested).
# ---------------------------------------------------------------------------
def _to_numeric_nan_sentinels(s: pd.Series) -> pd.Series:
    """Coerce to numeric and replace CFPS sentinel codes with NaN."""
    x = pd.to_numeric(s, errors="coerce")
    return x.mask(x.isin(_MISSING))


def clean_marital_status(s: pd.Series) -> pd.Series:
    """Return marital code restricted to {1..5}, else NaN.

    Codes follow CFPS qea0: 1=never married, 2=married (with spouse),
    3=cohabiting, 4=divorced, 5=widowed.
    """
    x = pd.to_numeric(s, errors="coerce")
    return x.where(x.isin(_VALID_MARITAL))


def clean_employed(s: pd.Series) -> pd.Series:
    """Return 0/1 employed indicator. NaN for retired / out-of-LF / refusal.

    CFPS employ codes:
      1 = 在业/有工作  → 1
      0 = 失业;  2 = 失业 (2020 only, both rendered as unemployed) → 0
      3 = 退出劳动力市场; 8 = 无法判断; 9 = 非经济活动人口 → NaN
      negative sentinels → NaN
    """
    x = pd.to_numeric(s, errors="coerce")
    out = pd.Series(np.nan, index=x.index, dtype="float64")
    out[x == 1] = 1.0
    out[x.isin([0, 2])] = 0.0
    return out


def _count_nonmissing_positive(df: pd.DataFrame, cols: Iterable[str]) -> pd.Series:
    """Number of columns whose value is a real (non-sentinel, non-null) positive code."""
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.Series(0, index=df.index, dtype="int64")
    block = df[cols].apply(pd.to_numeric, errors="coerce")
    valid = (block.notna()) & (~block.isin(list(_MISSING))) & (block > 0)
    return valid.sum(axis=1).astype("int64")


def count_children_2014(df: pd.DataFrame) -> pd.Series:
    """Number of CFPS-rostered children at 2014 wave (non-null `pid_c1..pid_c10`)."""
    cols = [f"pid_c{i}" for i in range(1, 11)]
    return _count_nonmissing_positive(df, cols)


def count_children_2020(df: pd.DataFrame) -> pd.Series:
    """Number of CFPS-rostered children at 2020 wave (non-null `qf1_a_1..qf1_a_8`).

    qf1_a_<i> is "relationship with child i" — present only when child i exists.
    """
    cols = [f"qf1_a_{i}" for i in range(1, 9)]
    return _count_nonmissing_positive(df, cols)


def count_household_2014(df: pd.DataFrame) -> pd.Series:
    """CFPS 2014 has no fml_count; count non-null pid_a_1..pid_a_17 + 1 (self)."""
    cols = [f"pid_a_{i}" for i in range(1, 18)]
    base = _count_nonmissing_positive(df, cols)
    return (base + 1).astype("int64")


def clean_household_2020(s: pd.Series) -> pd.Series:
    """CFPS 2020 fml_count — drop sentinel/non-positive codes to NaN."""
    return _to_numeric_nan_sentinels(s).where(lambda x: x > 0)


def classify_direction(delta: pd.Series, eps: float = 0.05) -> pd.Series:
    """Categorise each Δideation as 'progressive' / 'stable' / 'traditional'.

    eps = how much absolute change we treat as a meaningful shift.  0.05 of the
    [0,1] index = one notch on a 4-item battery.
    """
    out = pd.Series(pd.NA, index=delta.index, dtype="object")
    valid = delta.notna()
    out[valid & (delta <= -eps)] = "progressive"
    out[valid & (delta >= eps)] = "traditional"
    out[valid & (delta.abs() < eps)] = "stable"
    return out


def marital_transition(a: pd.Series, b: pd.Series) -> pd.Series:
    """Encode 2014 → 2020 marital transition as a short string label.

    Uses the cleaned codes from `clean_marital_status`.  Returns NaN where
    either endpoint is missing.
    """
    a = clean_marital_status(a)
    b = clean_marital_status(b)
    out = pd.Series(pd.NA, index=a.index, dtype="object")
    both = a.notna() & b.notna()
    a_, b_ = a[both], b[both]

    # stable_* (same code on both ends)
    stable = a_ == b_
    out.loc[a_.index[stable]] = a_[stable].map(lambda v: f"stable_{_MARITAL_NAME[int(v)]}")

    # transitions
    def _set(mask: pd.Series, label: str) -> None:
        out.loc[mask.index[mask]] = label

    # Married-entry: from 1 (never) or 3 (cohab) into 2 (married)
    _set((a_.isin([1, 3])) & (b_ == 2), "entered_marriage")
    # Divorced: any non-divorced → divorced
    _set((a_ != 4) & (b_ == 4), "divorced")
    # Widowed: any non-widow → widow
    _set((a_ != 5) & (b_ == 5), "widowed")
    # Started cohab: 1→3
    _set((a_ == 1) & (b_ == 3), "started_cohab")
    # Remarried: 4 or 5 → 2
    _set((a_.isin([4, 5])) & (b_ == 2), "remarried")
    # Other rarer transitions: catch-all
    remain = both & out.isna()
    if remain.any():
        out.loc[remain] = "other_change"
    return out


def numeric_delta(a: pd.Series, b: pd.Series) -> pd.Series:
    """Return b − a, with NaN propagating from either side."""
    return pd.to_numeric(b, errors="coerce") - pd.to_numeric(a, errors="coerce")


# Per-event at-risk definition.  Each entry maps an event name to a
# predicate over the panel that returns the boolean mask of "people who
# could have transitioned 0→1 between 2014 and 2020".
_AT_RISK = {
    # marital_2014 codes: 1=never, 2=married, 3=cohab, 4=divorced, 5=widow
    "entered_marriage": lambda p: p["marital_2014"].isin([1, 3]),
    "divorced":         lambda p: p["marital_2014"].isin([2, 3]),
    "widowed":          lambda p: p["marital_2014"].isin([2, 3]),
    "lost_job":         lambda p: p["employed_2014"] == 1,
    "entered_work":     lambda p: p["employed_2014"] == 0,
    # Fertility window: women ≤45 in 2014 OR men ≤55 in 2014.  Anyone with
    # female==NaN or age==NaN is dropped from at-risk.
    "had_new_child":    lambda p: (
        ((p["female"] == 1) & (p["age_2014"] <= 45))
        | ((p["female"] == 0) & (p["age_2014"] <= 55))
    ),
}


def at_risk_for_event(panel: pd.DataFrame, event: str) -> pd.Series:
    """Return a boolean mask: True where the respondent could have undergone
    the named 0→1 transition between 2014 and 2020.

    Definitions follow `_AT_RISK`.  Raises ValueError if `event` is unknown.
    """
    if event not in _AT_RISK:
        raise ValueError(f"unknown event {event!r}; "
                         f"known: {sorted(_AT_RISK)}")
    return _AT_RISK[event](panel).fillna(False).astype(bool)


# ---------------------------------------------------------------------------
# Loader: assemble the 2014↔2020 panel keyed by pid.
# ---------------------------------------------------------------------------
def _read_2014() -> pd.DataFrame:
    """Read CFPS 2014 with all variables needed for the panel."""
    cfg = L.SURVEYS[("CFPS", "2014")]
    items = list(cfg["items"])
    cols = (items + [cfg["gender_var"], cfg["province_var"], "pid",
                     "qea0", "employ2014", "cfps_birthy",
                     "cfps2014eduy_im", "income", "qa301"]
            + [f"pid_a_{i}" for i in range(1, 18)]
            + [f"pid_c{i}" for i in range(1, 11)])
    df, _ = pyreadstat.read_dta(str(ROOT / cfg["file"]),
                                usecols=list(dict.fromkeys(cols)))
    # Compute ideation index inline (same recoding as load_recoded).
    norm = []
    for var, (_short, direction) in cfg["items"].items():
        zc = f"{var}_z"
        df[zc] = L.normalize_item(df[var], cfg["scale_max"], cfg["agree_code"], direction)
        norm.append(zc)
    df["ideation_2014"] = df[norm].mean(axis=1)
    df["n_valid_items_2014"] = df[norm].notna().sum(axis=1)
    # gender → female
    gv = cfg["gender_var"]
    df["female"] = (df[gv] == 0).astype("float").where(df[gv].isin([0, 1]))
    df["birthy_2014"] = pd.to_numeric(df["cfps_birthy"], errors="coerce").where(
        lambda x: x.between(1920, 2007)
    )
    df["marital_2014"] = clean_marital_status(df["qea0"])
    df["employed_2014"] = clean_employed(df["employ2014"])
    df["children_n_2014"] = count_children_2014(df)
    df["household_n_2014"] = count_household_2014(df)
    df["edu_yrs_2014"] = pd.to_numeric(df["cfps2014eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22)
    )
    df["income_2014"] = _to_numeric_nan_sentinels(df["income"]).where(lambda x: x >= 0)
    # urban via hukou qa301: 1=农业, 3=非农业, 7=居民 (2020 only), 5=无户口
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    urban = pd.Series(np.nan, index=hk.index, dtype="float64")
    urban[hk == 1] = 0.0
    urban[hk == 3] = 1.0
    df["urban_2014"] = urban
    return df


def _read_2020() -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", "2020")]
    items = list(cfg["items"])
    cols = (items + [cfg["gender_var"], cfg["province_var"], "pid",
                     "qea0", "employ", "ibirthy",
                     "cfps2020eduy_im", "emp_income", "qa301", "fml_count"]
            + [f"qf1_a_{i}" for i in range(1, 9)])
    df, _ = pyreadstat.read_dta(str(ROOT / cfg["file"]),
                                usecols=list(dict.fromkeys(cols)))
    norm = []
    for var, (_short, direction) in cfg["items"].items():
        zc = f"{var}_z"
        df[zc] = L.normalize_item(df[var], cfg["scale_max"], cfg["agree_code"], direction)
        norm.append(zc)
    df["ideation_2020"] = df[norm].mean(axis=1)
    df["n_valid_items_2020"] = df[norm].notna().sum(axis=1)
    gv = cfg["gender_var"]
    df["female_2020"] = (df[gv] == 0).astype("float").where(df[gv].isin([0, 1]))
    df["birthy_2020"] = pd.to_numeric(df["ibirthy"], errors="coerce").where(
        lambda x: x.between(1920, 2010)
    )
    df["marital_2020"] = clean_marital_status(df["qea0"])
    df["employed_2020"] = clean_employed(df["employ"])
    df["children_n_2020"] = count_children_2020(df)
    df["household_n_2020"] = clean_household_2020(df["fml_count"])
    df["edu_yrs_2020"] = pd.to_numeric(df["cfps2020eduy_im"], errors="coerce").where(
        lambda x: x.between(0, 22)
    )
    df["income_2020"] = _to_numeric_nan_sentinels(df["emp_income"]).where(lambda x: x >= 0)
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    urban = pd.Series(np.nan, index=hk.index, dtype="float64")
    urban[hk == 1] = 0.0
    urban[hk.isin([3, 7])] = 1.0
    df["urban_2020"] = urban
    return df


def build_panel() -> pd.DataFrame:
    """Return the per-pid panel of respondents in both CFPS 2014 and 2020.

    Index = pid (int). Columns include baseline characteristics from 2014,
    endpoint ideation/states from 2020, and Δ-variables.
    """
    df14 = _read_2014()
    df20 = _read_2020()

    # CFPS 2014 has some pid duplicates (multi-module joins); keep first row.
    df14 = df14.drop_duplicates(subset=["pid"], keep="first")
    df20 = df20.drop_duplicates(subset=["pid"], keep="first")

    keep14 = ["pid", "ideation_2014", "n_valid_items_2014", "female",
              "birthy_2014", "marital_2014", "employed_2014",
              "children_n_2014", "household_n_2014",
              "edu_yrs_2014", "income_2014", "urban_2014"]
    keep20 = ["pid", "ideation_2020", "n_valid_items_2020", "female_2020",
              "birthy_2020", "marital_2020", "employed_2020",
              "children_n_2020", "household_n_2020",
              "edu_yrs_2020", "income_2020", "urban_2020"]
    p = df14[keep14].merge(df20[keep20], on="pid", how="inner")

    # Δs
    p["delta_ideation"] = numeric_delta(p["ideation_2014"], p["ideation_2020"])
    p["delta_employed"] = numeric_delta(p["employed_2014"], p["employed_2020"])
    p["delta_children_n"] = numeric_delta(p["children_n_2014"], p["children_n_2020"])
    p["delta_household_n"] = numeric_delta(p["household_n_2014"], p["household_n_2020"])
    p["delta_edu_yrs"] = numeric_delta(p["edu_yrs_2014"], p["edu_yrs_2020"])
    p["delta_urban"] = numeric_delta(p["urban_2014"], p["urban_2020"])

    # life events (binary, in 2014..2020 window)
    p["had_new_child"] = (p["delta_children_n"].fillna(0) > 0).astype("float")
    p["had_new_child"] = p["had_new_child"].where(p["delta_children_n"].notna())
    p["lost_job"] = ((p["employed_2014"] == 1) & (p["employed_2020"] == 0)).astype("float")
    p["lost_job"] = p["lost_job"].where(p["employed_2014"].notna() & p["employed_2020"].notna())
    p["entered_work"] = ((p["employed_2014"] == 0) & (p["employed_2020"] == 1)).astype("float")
    p["entered_work"] = p["entered_work"].where(p["employed_2014"].notna() & p["employed_2020"].notna())

    p["marital_transition"] = marital_transition(p["marital_2014"], p["marital_2020"])
    p["entered_marriage"] = (p["marital_transition"] == "entered_marriage").astype("float")
    p["entered_marriage"] = p["entered_marriage"].where(p["marital_transition"].notna())
    p["divorced"] = (p["marital_transition"] == "divorced").astype("float")
    p["divorced"] = p["divorced"].where(p["marital_transition"].notna())
    p["widowed"] = (p["marital_transition"] == "widowed").astype("float")
    p["widowed"] = p["widowed"].where(p["marital_transition"].notna())

    # age at 2014 (handy for at-risk filters and for sex-stratified OLS)
    p["age_2014"] = 2014 - p["birthy_2014"]

    # household-size change buckets (smaller / same / larger)
    def _bucket(x: float) -> str | float:
        if pd.isna(x):
            return np.nan
        if x <= -1:
            return "shrank"
        if x >= 1:
            return "grew"
        return "stable"
    p["household_change_dir"] = p["delta_household_n"].map(_bucket)

    # direction of ideation change
    p["direction"] = classify_direction(p["delta_ideation"], eps=0.05)

    # cohort label at 2014 birth year (consistent with other analyses)
    from rq51_helpers import cohort_label  # local import to avoid cycle
    p["cohort"] = p["birthy_2014"].map(cohort_label)

    return p


if __name__ == "__main__":  # quick smoke test
    p = build_panel()
    print("panel rows:", len(p))
    print("delta_ideation describe:")
    print(p["delta_ideation"].describe())
    print("direction:", p["direction"].value_counts(dropna=False).to_dict())
