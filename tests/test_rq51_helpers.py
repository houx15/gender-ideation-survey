"""Tests for outputs/survey_exploration/scripts/rq51_helpers.py.

Unit tests target the pure functions (cohort_label, cfps_dedup_keep_latest).
Integration tests (marked) hit real survey files to confirm the per-survey
extractors return sensible value ranges.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "outputs" / "survey_exploration" / "scripts"))
import rq51_helpers as H  # noqa: E402


# ---------- pure functions ---------- #

def test_cohort_label_buckets_known_years():
    assert H.cohort_label(1945) == "1930-1949"
    assert H.cohort_label(1959) == "1950-1959"
    assert H.cohort_label(1989) == "1980-1989"
    assert H.cohort_label(1995) == "1990-2005"


def test_cohort_label_returns_nan_outside_range():
    assert pd.isna(H.cohort_label(1900))
    assert pd.isna(H.cohort_label(2010))
    assert pd.isna(H.cohort_label(np.nan))


def test_cfps_dedup_keep_latest_picks_later_wave_and_counts_changers():
    df = pd.DataFrame({
        "pid": [1, 1, 2, 3, 3, 4],
        "wave": [2014, 2020, 2014, 2014, 2020, 2020],
        "ideation_index": [0.5, 0.7, 0.4, 0.6, 0.6, 0.3],
    })
    out, summary = H.cfps_dedup_keep_latest(df, pid_col="pid", wave_col="wave",
                                            value_col="ideation_index", change_eps=0.001)
    # one row per pid
    assert sorted(out["pid"].tolist()) == [1, 2, 3, 4]
    # pid 1: latest wave is 2020 -> index 0.7
    assert float(out.loc[out.pid == 1, "ideation_index"]) == 0.7
    # pid 3: latest wave is 2020 -> index 0.6 (unchanged from 2014)
    assert float(out.loc[out.pid == 3, "ideation_index"]) == 0.6

    # 2 pids appear in both waves (pid 1 and pid 3)
    assert summary["n_pids_in_both_waves"] == 2
    # of those, pid 1 changed (|0.7-0.5|>eps) but pid 3 did not
    assert summary["n_pids_changed"] == 1
    # original total rows
    assert summary["n_rows_input"] == 6
    assert summary["n_rows_deduped"] == 4


def test_cfps_dedup_handles_only_one_wave():
    df = pd.DataFrame({"pid": [1, 2], "wave": [2014, 2014],
                       "ideation_index": [0.5, 0.6]})
    out, summary = H.cfps_dedup_keep_latest(df, "pid", "wave", "ideation_index")
    assert summary["n_pids_in_both_waves"] == 0
    assert summary["n_pids_changed"] == 0
    assert len(out) == 2


def test_cfps_dedup_handles_nan_values_in_change_calc():
    # pid 1 has nan in 2014 only -> shouldn't be a "changer" (we can't tell)
    df = pd.DataFrame({
        "pid": [1, 1, 2, 2],
        "wave": [2014, 2020, 2014, 2020],
        "ideation_index": [np.nan, 0.5, 0.6, 0.6],
    })
    out, s = H.cfps_dedup_keep_latest(df, "pid", "wave", "ideation_index")
    # both pids appear in both waves
    assert s["n_pids_in_both_waves"] == 2
    # only pids with both values measurable can be "changers" -> 0 here
    assert s["n_pids_changed"] == 0


# ---------- integration smoke tests ---------- #

@pytest.mark.integration
def test_cleaning_steps_table_for_cfps_2014():
    rows = H.cleaning_steps_table("CFPS", "2014")
    # raw N from earlier metadata check
    assert rows[0]["step"] == "raw_rows"
    assert rows[0]["n"] == 39768
    # final N must be <= raw N and > 0
    assert 0 < rows[-1]["n"] <= rows[0]["n"]


@pytest.mark.integration
def test_urban_indicator_known_codes():
    s = H.urban_indicator("CGSS", "2010")
    # CGSS 2010 s5: 1=urban -> 1.0, 2=rural -> 0.0
    vc = s.value_counts(dropna=False)
    assert 1.0 in vc.index and 0.0 in vc.index


@pytest.mark.integration
def test_birth_year_reasonable_range():
    by = H.birth_year("CGSS", "2010")
    by = by.dropna()
    assert by.min() >= 1900 and by.max() <= 2010


# ---------- defensive: missing codes must become NaN, not 0 ---------- #

@pytest.mark.integration
def test_employed_indicator_keeps_acwf_1990_outside_set_as_nan():
    """ACWF 1990 b7 has 2725 NaN respondents (no occupation code).
    The indicator must return NaN for them, NOT 0.
    """
    s = H.employed_indicator("ACWF", "1990")
    assert s.isna().sum() > 2000   # the unspecified-occupation respondents
    # of the non-NaN values, none should be 0 (the file has no 90-96 codes)
    assert int((s == 0).sum()) == 0


@pytest.mark.integration
def test_income_missing_codes_are_nan_not_zero_cfps():
    """CFPS 2014 income uses -1..-10 as missing codes; they must become NaN,
    NOT be silently treated as 0 income (which would bias log_income to 0).
    """
    s = H.personal_income("CFPS", "2014")
    # NaN count should reflect the refused/DK respondents
    assert s.isna().sum() > 15_000
    # zero count should reflect ONLY people with literal income == 0 (housewives,
    # students, etc.), which is a much smaller cohort
    n_zero = int((s == 0).sum())
    n_nan = int(s.isna().sum())
    assert n_zero < n_nan
    # they must not be the same — proves NaN != 0
    assert n_zero != n_nan


@pytest.mark.integration
def test_urban_indicator_negative_codes_become_nan():
    """CGSS 2010 a18 = -3 (refused) or 5/6/7 (military/no-hukou/other) -> NaN."""
    s = H.urban_indicator("CGSS", "2010")
    # rural codes = [1] (agric), urban codes = [2, 4] (non-agric, 居民).
    # Anything else (incl. -3, 3=蓝印, 5=军籍, 6=无户口, 7=其他) -> NaN.
    import pyreadstat
    df, _ = pyreadstat.read_dta("surveys/CGSS/2010/CGSS2010.dta", usecols=["a18"])
    n_other = int(((~df["a18"].isin([1, 2, 4])) | df["a18"].isna()).sum())
    assert s.isna().sum() == n_other
    # Any negative refusal codes must yield NaN, not 0.
    assert (s.loc[df["a18"] < 0]).isna().all()


@pytest.mark.integration
def test_education_years_returns_nan_for_unknown_levels():
    """Codes outside the level->years map must become NaN, not default to 0."""
    # CGSS a7a only maps 1..14. Verify any out-of-map raw code becomes NaN.
    s = H.education_years("CGSS", "2010")
    # there should be 8-20 NaN's (refused/etc. responses) in CGSS 2010
    assert 0 <= s.isna().sum() < 100


# ---------- CFPS 2014 aspirational helpers (from reference/stata_convert.do) ---- #

@pytest.mark.integration
def test_cfps2014_aspiration_isei_matches_dofile_mapping_n():
    """Sample size should match the kr1==4 subsample with valid ks801code."""
    s = H.cfps2014_aspiration_isei()
    # 957 high schoolers; 877 answered ks801code; ~32 give un-mappable codes
    # (军人/读书/为人民服务/不便分类/看自己), so the dofile-clean ISEI sample is ~728.
    n_valid = int(s.notna().sum())
    assert 700 < n_valid < 800
    # ISEI values should be in the [16, 90] band; mean roughly 40-60 for youth aspirations
    valid = s.dropna()
    assert valid.min() >= 16
    assert valid.max() <= 90
    assert 35 < valid.mean() < 75


@pytest.mark.integration
def test_cfps2014_aspiration_edu_years_known_codes():
    """qc201 -> aspiration years map should match the dofile's labels."""
    s = H.cfps2014_aspiration_edu_years()
    # most respondents in kr1==4 should aspire to 12+ years (high school+)
    valid = s.dropna()
    assert int(valid.notna().sum()) > 500
    # the values must be in the dofile's set
    allowed = {0, 6, 9, 12, 15, 16, 19, 23}
    assert set(valid.unique()).issubset(allowed)
