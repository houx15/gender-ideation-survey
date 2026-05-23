#!/usr/bin/env python3
"""rq51_helpers.py — helpers for the RQ 5.1 deep-dive (analysis_023).

Provides:
  - cohort_label / cfps_dedup_keep_latest        (pure, unit-tested)
  - cleaning_steps_table(dataset, year)          (raw N -> final N record)
  - urban_indicator(dataset, year)               (0/1 urban; NaN for missing)
  - birth_year(dataset, year)                    (standardized 4-digit birth year)
  - personal_income(dataset, year)               (best-available; NaN for missing codes)
  - education_years(dataset, year)               (best-available; NaN missing)
  - employed_indicator(dataset, year)            (0/1 currently employed; NaN otherwise)

Per-survey config tables (URBAN_VARS, BIRTH_VARS, INCOME_VARS, EDU_VARS, EMP_VARS)
are explicit so every loader is grep-able.  All loads use ideation_lib.load_recoded
where possible so the ideation index is computed consistently.
"""
from __future__ import annotations

from pathlib import Path
import math
import sys
from typing import Iterable

import numpy as np
import pandas as pd
import pyreadstat

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))
import ideation_lib as L  # noqa: E402

ROOT = L.ROOT

# ---------------------------------------------------------------------------
# Cohort buckets — same as analysis_021/022 so figures align across reports.
# ---------------------------------------------------------------------------
COHORTS: list[tuple[int, int]] = [
    (1930, 1949), (1950, 1959), (1960, 1969),
    (1970, 1979), (1980, 1989), (1990, 2005),
]


def cohort_label(year) -> str | float:
    """Return the cohort bucket label for a given birth year, else NaN."""
    if year is None or (isinstance(year, float) and math.isnan(year)):
        return float("nan")
    try:
        y = int(year)
    except (TypeError, ValueError):
        return float("nan")
    for lo, hi in COHORTS:
        if lo <= y <= hi:
            return f"{lo}-{hi}"
    return float("nan")


# ---------------------------------------------------------------------------
# Per-survey variable maps.
# ---------------------------------------------------------------------------

# urban indicator: (var, urban_code, rural_code)
URBAN_VARS: dict[tuple[str, str], tuple[str, int, int]] = {
    ("CFPS", "2014"): ("urban14", 1, 0),
    ("CFPS", "2020"): ("urban20", 1, 0),
    ("CGSS", "2010"): ("s5", 1, 2),
    ("CGSS", "2012"): ("s5a", 1, 2),
    ("CGSS", "2013"): ("s5a", 1, 2),
    ("CGSS", "2015"): ("s1", 1, 2),
    ("CGSS", "2017"): ("isurban", 1, 2),
    ("CGSS", "2018"): ("type", 1, 2),
    ("CGSS", "2021"): ("isurban", 1, 2),
    ("CGSS", "2023"): ("isurban", 1, 2),
    ("ACWF", "1990"): ("ch_x", 1, 2),    # 城乡
    ("ACWF", "2000"): ("c_n", 1, 2),     # 城乡分组
    ("ACWF", "2010"): ("ChengX", 1, 2),  # 城乡
}

# birth year variable + (lo, hi) plausible range.
BIRTH_VARS: dict[tuple[str, str], tuple[str, int, int]] = {
    ("CFPS", "2014"): ("cfps_birthy", 1920, 2007),
    ("CFPS", "2020"): ("ibirthy", 1920, 2010),
    ("CGSS", "2010"): ("a3a", 1920, 2007),
    ("CGSS", "2012"): ("a3a", 1920, 2007),
    ("CGSS", "2013"): ("a3a", 1920, 2007),
    ("CGSS", "2015"): ("a301", 1920, 2007),
    ("CGSS", "2017"): ("a31", 1920, 2007),
    ("CGSS", "2018"): ("a31", 1920, 2007),
    ("CGSS", "2021"): ("A3_1", 1920, 2010),
    ("CGSS", "2023"): ("a3a", 1920, 2010),
    # ACWF 1990: no explicit birth year. b4 is age at survey; derive at load time.
    ("ACWF", "1990"): ("b4", 0, 110),
    # ACWF 2000/2010 use last-2-digits of birth year (e.g. 36 -> 1936). Converted in birth_year.
    ("ACWF", "2000"): ("a2_1", 0, 96),
    ("ACWF", "2010"): ("A2A", 0, 96),
}

# Personal income (annual or imputed monthly).
INCOME_VARS: dict[tuple[str, str], tuple[str, int, int]] = {
    ("CFPS", "2014"): ("income", 0, 10_000_000),
    ("CFPS", "2020"): ("emp_income", 0, 10_000_000),
    ("CGSS", "2010"): ("a8a", 0, 100_000_000),
    ("CGSS", "2012"): ("a8a", 0, 100_000_000),
    ("CGSS", "2013"): ("a8a", 0, 100_000_000),
    ("CGSS", "2015"): ("a8a", 0, 100_000_000),
    ("CGSS", "2017"): ("a8a", 0, 100_000_000),
    ("CGSS", "2018"): ("a8a", 0, 100_000_000),
    ("CGSS", "2021"): ("A8a", 0, 100_000_000),
    ("CGSS", "2023"): ("a8a", 0, 100_000_000),
    # ACWF 1990: w151 monthly urban; w16 annual rural -> combine to "annualized RMB".
    ("ACWF", "1990"): ("w151", 0, 10_000_000),
    ("ACWF", "2000"): ("c18_a", 0, 10_000_000),
    # ACWF 2010: NC9A is in the never-married supplement (zero overlap with the
    # ideology module).  C18AA = labour income from the main module aligns with
    # the ideology sample; we use it as personal income.
    ("ACWF", "2010"): ("C18AA", 0, 10_000_000),
}

# Education years (preferred) or highest-level mapped to years.
# We use direct year variables when available; otherwise we map levels -> years.
EDU_VARS: dict[tuple[str, str], dict] = {
    ("CFPS", "2014"): {"kind": "years", "var": "cfps2014eduy_im", "lo": 0, "hi": 22},
    ("CFPS", "2020"): {"kind": "years", "var": "cfps2020eduy_im", "lo": 0, "hi": 22},
    # CGSS a7a 1-13 highest edu level -> years map applied below
    ("CGSS", "2010"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2012"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2013"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2015"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2017"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2018"): {"kind": "cgss_a7a", "var": "a7a"},
    ("CGSS", "2021"): {"kind": "cgss_a7a", "var": "A7a"},
    ("CGSS", "2023"): {"kind": "cgss_a7a", "var": "a7a"},
    ("ACWF", "1990"): {"kind": "acwf_level", "var": "b6"},
    ("ACWF", "2000"): {"kind": "acwf_level", "var": "b4_a"},
    ("ACWF", "2010"): {"kind": "acwf_level", "var": "B3A"},
}

# Currently employed indicator. We accept presence of `yes` codes per-survey.
EMP_VARS: dict[tuple[str, str], dict] = {
    ("CFPS", "2014"): {"var": "employ2014", "yes": [1]},  # employ2014 (0=失业,1=有工作,3=退出LF)
    ("CFPS", "2020"): {"var": "employ", "yes": [1]},      # employ (0=失业,1=有工作,3=退出LF)
    # CGSS a58 "your work experience and status": 1=currently non-ag, 2=farming +
    # previously non-ag, 3=currently farming only, 4=no work (only farmed),
    # 5=no work (was non-ag), 6=never worked.  Codes 1-3 = currently employed.
    ("CGSS", "2010"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2012"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2013"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2015"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2017"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2018"): {"var": "a58", "yes": [1, 2, 3]},
    ("CGSS", "2021"): {"var": "A58", "yes": [1, 2, 3]},
    ("CGSS", "2023"): {"var": "a58", "yes": [1, 2, 3]},
    # ACWF 1990 b7 is occupation (codes 10..80 = various jobs incl. 60农林牧渔, 70工人;
    # 90=不在业, 91=学生, 92=家务, 93=待升学, 94=待业, 95=离退休, 96=丧失劳动力, 97=其他).
    # Treat 10..81 as employed; 90,92,94,95,96 as not employed; 91,93,97,0 as NaN.
    ("ACWF", "1990"): {"var": "b7", "yes": list(range(10, 82))},
    ("ACWF", "2000"): {"var": "c1_a", "yes": [1, 2]},
    ("ACWF", "2010"): {"var": "C1A", "yes": [1]},
}

# CGSS a7a coding (1..14) -> years (rough). 1=未受教育, 14=研究生.
_CGSS_A7A_YEARS = {1: 0, 2: 3, 3: 3, 4: 6, 5: 9, 6: 12, 7: 12, 8: 12,
                   9: 12, 10: 15, 11: 16, 12: 16, 13: 19, 14: 22}
# ACWF 1990 b6 / 2000 b4_a / 2010 B3A levels share similar shape; use a fallback
# linear mapping (verified by spot-check in 02_ideation_discovery + codebooks).
_ACWF_LEVEL_YEARS = {1: 0, 2: 3, 3: 6, 4: 9, 5: 12, 6: 14, 7: 16, 8: 19, 9: 22}


# ---------------------------------------------------------------------------
# CFPS dedup helper (pure function).
# ---------------------------------------------------------------------------

def cfps_dedup_keep_latest(df: pd.DataFrame, pid_col: str, wave_col: str,
                           value_col: str, change_eps: float = 0.01
                           ) -> tuple[pd.DataFrame, dict]:
    """Deduplicate CFPS rows by pid, keeping the latest wave.

    Also counts how many pids appear in more than one wave, and of those, how
    many had a measurable change (>= change_eps in absolute index difference).
    """
    work = df.dropna(subset=[pid_col]).copy()
    work["_wave"] = pd.to_numeric(work[wave_col], errors="coerce")
    # how many pids in each wave
    waves_per_pid = work.groupby(pid_col)["_wave"].nunique()
    n_in_both = int((waves_per_pid > 1).sum())

    # for change calc, need both waves to have a measurable value
    if n_in_both:
        wide = (work[[pid_col, "_wave", value_col]]
                .dropna(subset=[value_col])
                .drop_duplicates([pid_col, "_wave"])
                .pivot(index=pid_col, columns="_wave", values=value_col))
        if wide.shape[1] >= 2:
            both = wide.dropna(how="any")
            spans = both.max(axis=1) - both.min(axis=1)
            n_changed = int((spans.abs() >= change_eps).sum())
        else:
            n_changed = 0
    else:
        n_changed = 0

    # keep latest wave per pid
    work_sorted = work.sort_values([pid_col, "_wave"])
    deduped = work_sorted.drop_duplicates(subset=[pid_col], keep="last").drop(columns=["_wave"])
    return deduped, {
        "n_rows_input": int(len(df)),
        "n_rows_deduped": int(len(deduped)),
        "n_unique_pids": int(work[pid_col].nunique()),
        "n_pids_in_both_waves": n_in_both,
        "n_pids_changed": n_changed,
        "change_eps": change_eps,
    }


# ---------------------------------------------------------------------------
# Cleaning-steps audit: how many rows are dropped at each step.
# ---------------------------------------------------------------------------

def cleaning_steps_table(dataset: str, year: str) -> list[dict]:
    """Return the row counts at each cleaning step.

    Steps:
      1. raw_rows                            (entire .dta file)
      2. has_any_item_value                  (>= 1 non-missing raw item)
      3. has_one_valid_normalized_item       (>= 1 item maps into [0,1])
      4. has_gender                          (female in {0,1})
      5. has_birth_year                      (birthy in range)
      6. all_three                           (intersection)

    Counts come from the same load_recoded pipeline used in analyses, so the
    "valid for analysis" sample is exactly what each subsequent figure uses.
    """
    cfg = L.SURVEYS[(dataset, year)]
    raw_path = ROOT / cfg["file"]
    df_raw, _ = pyreadstat.read_dta(str(raw_path), metadataonly=True)
    raw_n = int(df_raw.metadata_container.number_rows) if hasattr(df_raw, "metadata_container") else None
    if raw_n is None:
        # pyreadstat: metadata.number_rows lives on the meta object
        _, meta = pyreadstat.read_dta(str(raw_path), metadataonly=True)
        raw_n = int(meta.number_rows)

    by_var, by_lo, by_hi = BIRTH_VARS[(dataset, year)]
    extra = [by_var]
    df, _meta, norm_cols, idx = L.load_recoded(dataset, year, extra_cols=extra)

    raw_items = list(cfg["items"])
    has_raw = df[raw_items].notna().any(axis=1)
    has_valid = df["n_valid_items"] >= 1
    has_gender = df["female"].isin([0.0, 1.0])
    by = pd.to_numeric(df[by_var], errors="coerce")
    has_by = by.between(by_lo, by_hi)
    all_three = has_valid & has_gender & has_by

    return [
        {"step": "raw_rows",                  "n": raw_n},
        {"step": "has_any_item_value",        "n": int(has_raw.sum())},
        {"step": "has_one_valid_norm_item",   "n": int(has_valid.sum())},
        {"step": "has_gender",                "n": int(has_gender.sum())},
        {"step": "has_birth_year",            "n": int(has_by.sum())},
        {"step": "final_analysis_sample",     "n": int(all_three.sum())},
    ]


# ---------------------------------------------------------------------------
# Per-survey extractors (each returns a pandas Series aligned to the load_recoded
# row order so it can be concatenated with the ideation_index frame).
# ---------------------------------------------------------------------------

def _read_extra(dataset: str, year: str, extra_vars: Iterable[str]) -> pd.DataFrame:
    """Load just the requested raw columns (no recoding)."""
    cfg = L.SURVEYS[(dataset, year)]
    df, _ = pyreadstat.read_dta(str(ROOT / cfg["file"]),
                                usecols=list(dict.fromkeys(extra_vars)))
    return df


def urban_indicator(dataset: str, year: str) -> pd.Series:
    var, urban_code, rural_code = URBAN_VARS[(dataset, year)]
    df = _read_extra(dataset, year, [var])
    s = pd.to_numeric(df[var], errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    out[s == urban_code] = 1.0
    out[s == rural_code] = 0.0
    return out


def birth_year(dataset: str, year: str) -> pd.Series:
    var, lo, hi = BIRTH_VARS[(dataset, year)]
    df = _read_extra(dataset, year, [var])
    s = pd.to_numeric(df[var], errors="coerce")
    if dataset == "ACWF" and year == "1990":
        # b4 is age in 1990; convert to birth year.
        age = s.where(s.between(1, 110))
        return (1990 - age).astype("float64")
    if dataset == "ACWF" and year in ("2000", "2010"):
        # last-2-digit year encoding; 97=不适用 in 2010.
        s2 = s.where(s.between(lo, hi))
        return s2.add(1900).astype("float64")
    return s.where(s.between(lo, hi))


def personal_income(dataset: str, year: str) -> pd.Series:
    var, lo, hi = INCOME_VARS[(dataset, year)]
    df = _read_extra(dataset, year, [var])
    s = pd.to_numeric(df[var], errors="coerce")
    return s.where(s.between(lo, hi))


def education_years(dataset: str, year: str) -> pd.Series:
    cfg = EDU_VARS[(dataset, year)]
    df = _read_extra(dataset, year, [cfg["var"]])
    s = pd.to_numeric(df[cfg["var"]], errors="coerce")
    if cfg["kind"] == "years":
        return s.where(s.between(cfg["lo"], cfg["hi"]))
    if cfg["kind"] == "level":
        # CFPS 2020 qea0: 1..8 codes -> years (rough; codebook in 05_measurement_decisions)
        cfps20_map = {1: 0, 2: 3, 3: 6, 4: 9, 5: 12, 6: 15, 7: 16, 8: 19}
        return s.map(cfps20_map).astype("float64")
    if cfg["kind"] == "cgss_a7a":
        return s.map(_CGSS_A7A_YEARS).astype("float64")
    if cfg["kind"] == "acwf_level":
        return s.map(_ACWF_LEVEL_YEARS).astype("float64")
    return pd.Series(np.nan, index=s.index, dtype="float64")


def employed_indicator(dataset: str, year: str) -> pd.Series:
    """Return 1 if currently employed, 0 if labour-force-eligible but not employed.

    "Out of labour force" / refusal / missing -> NaN.  Codes are per-survey.
    """
    cfg = EMP_VARS[(dataset, year)]
    df = _read_extra(dataset, year, [cfg["var"]])
    s = pd.to_numeric(df[cfg["var"]], errors="coerce")
    out = pd.Series(np.nan, index=s.index, dtype="float64")
    yes = set(cfg["yes"])
    if dataset == "CFPS":
        # employ2014/employ: 0=失业 1=有工作 3=退出LF, negatives=missing
        out[s == 1] = 1.0
        out[s == 0] = 0.0
    elif dataset == "CGSS":
        # a58: 1-3 currently working; 4-6 not currently working.
        out[s.isin(yes)] = 1.0
        out[s.isin([4, 5, 6])] = 0.0
    elif dataset == "ACWF" and year == "1990":
        # occupational codes 10..81 -> employed; 90,92,94,95,96 -> not employed;
        # 0/91/93/97 stay NaN (no answer / student / waiting / other).
        out[s.isin(yes)] = 1.0
        out[s.isin([90, 92, 94, 95, 96])] = 0.0
    elif dataset == "ACWF":
        out[s.isin(yes)] = 1.0
        out[(s > 0) & ~s.isin(yes)] = 0.0
    return out
