"""Tests for couple construction from CFPS spouse pointers.

build_couples turns a respondent frame (each row carries the in-sample person-id of
their spouse) into one row per couple with wife_<col>/husband_<col> values, assigning
wife/husband by the female flag. It must:
  - emit each couple ONCE (the two reciprocal rows collapse to one),
  - drop egos whose spouse is not in the sample,
  - drop same-sex / ambiguous pairs (can't assign wife vs husband).
"""
import pandas as pd

import cfps_linkage as K


def _frame():
    return pd.DataFrame({
        "pid":      [1, 2, 3, 4, 5],
        "pid_s":    [2, 1, 4, 3, 9],   # 5's spouse (9) is not in sample
        "female":   [1, 0, 1, 0, 1],
        "ideation": [0.8, 0.4, 0.6, 0.2, 0.5],
        "housework": [5.0, 1.0, 3.0, 0.0, 2.0],
    })


def test_build_couples_one_row_per_couple():
    out = K.build_couples(_frame(), "pid", "pid_s", "female", ["ideation", "housework"])
    assert len(out) == 2  # (1,2) and (3,4); pid 5 dropped


def test_build_couples_assigns_wife_and_husband_by_gender():
    out = K.build_couples(_frame(), "pid", "pid_s", "female", ["ideation", "housework"])
    c = out.set_index("wife_pid").loc[1]
    assert c["husband_pid"] == 2
    assert c["wife_ideation"] == 0.8 and c["husband_ideation"] == 0.4
    assert c["wife_housework"] == 5.0 and c["husband_housework"] == 1.0


def test_build_couples_drops_spouse_not_in_sample():
    out = K.build_couples(_frame(), "pid", "pid_s", "female", ["ideation"])
    assert 5 not in set(out["wife_pid"]) and 5 not in set(out["husband_pid"])


def test_build_couples_drops_same_sex_pairs():
    df = pd.DataFrame({
        "pid": [1, 2], "pid_s": [2, 1], "female": [1, 1], "ideation": [0.5, 0.6],
    })
    out = K.build_couples(df, "pid", "pid_s", "female", ["ideation"])
    assert len(out) == 0
