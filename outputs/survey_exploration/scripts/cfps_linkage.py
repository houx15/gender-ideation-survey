#!/usr/bin/env python3
"""
cfps_linkage.py — build dyads from CFPS in-sample person-id pointers.

CFPS stores, on each respondent, the person-id of their spouse / father / mother
(when that relative is also a respondent). These helpers turn those pointers into
analysis-ready dyads. Logic is locked by tests/test_cfps_linkage.py.

Raw data is never modified; helpers return new frames.
"""
from __future__ import annotations
import pandas as pd


def build_couples(df: pd.DataFrame, pid_col: str, spouse_col: str,
                  female_col: str, value_cols: list[str]) -> pd.DataFrame:
    """One row per couple with wife_<col>/husband_<col> values.

    - keeps each couple once (reciprocal rows collapse),
    - drops egos whose spouse is absent from the sample,
    - drops same-sex / ambiguous pairs (can't assign wife vs husband).
    """
    pid_to_row = df.set_index(pid_col)
    pids = set(pid_to_row.index)

    seen: set[frozenset] = set()
    rows = []
    linked = df[df[spouse_col].isin(pids) & (df[spouse_col] != df[pid_col])]
    for _, ego in linked.iterrows():
        ego_pid, sp_pid = ego[pid_col], ego[spouse_col]
        key = frozenset((ego_pid, sp_pid))
        if key in seen:
            continue
        seen.add(key)
        partner = pid_to_row.loc[sp_pid]
        members = [(ego_pid, ego), (sp_pid, partner)]
        wives = [(p, r) for p, r in members if r[female_col] == 1]
        husbands = [(p, r) for p, r in members if r[female_col] == 0]
        if len(wives) != 1 or len(husbands) != 1:
            continue  # same-sex or unknown gender
        wpid, wrow = wives[0]
        hpid, hrow = husbands[0]
        rec = {"wife_pid": wpid, "husband_pid": hpid}
        for c in value_cols:
            rec[f"wife_{c}"] = wrow[c]
            rec[f"husband_{c}"] = hrow[c]
        rows.append(rec)
    return pd.DataFrame(rows)


def attach_parents(df: pd.DataFrame, pid_col: str, father_col: str,
                   mother_col: str, value_cols: list[str]) -> pd.DataFrame:
    """Add father_<col>/mother_<col> to each ego (child) row by following the
    in-sample parent pointers. Pointers that are <=0 or not present in the sample
    yield NaN. All ego rows are kept.
    """
    out = df.copy()
    lookup = {c: df.set_index(pid_col)[c] for c in value_cols}
    for parent, ptr in (("father", father_col), ("mother", mother_col)):
        valid_ptr = out[ptr].where(out[ptr] > 0)
        for c in value_cols:
            out[f"{parent}_{c}"] = valid_ptr.map(lookup[c])
    return out
