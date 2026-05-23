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
