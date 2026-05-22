#!/usr/bin/env python3
"""
ideation_lib.py — canonical config + recoding for the core gender-ideation battery.

Shared by all analysis_runs so the index is computed identically everywhere.
Index convention (matches surveys/processed/methodology.md):
    0 = most progressive/egalitarian, 1 = most traditional.
Each item is normalized to [0,1] then averaged over valid items per respondent.

Raw data is never modified; recoding happens in memory only.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]

# (dataset, year) -> dict(file, gender_var, province_var, scale_max, agree_code, items)
# items: var -> (short, direction)  direction in {"traditional","progressive"}
SURVEYS = {
    ("ACWF", "1990"): dict(
        file="surveys/中国妇女地位调查/1990/w1990_fixed.dta",
        gender_var="b3", province_var="sheng", scale_max=5, agree_code=1,
        items={"w611": ("men-society/women-family", "traditional"),
               "w612": ("men-innately-more-capable", "traditional"),
               "w613": ("women-avoid-surpassing-husband", "traditional"),
               "w614": ("wife-supports-husband-success", "traditional"),
               "w615": ("child-takes-mother-surname", "progressive"),
               "w616": ("women-not-half-the-sky", "traditional"),
               "w617": ("men-handle-external-affairs", "traditional"),
               "w618": ("widow-remarry-leave-property", "traditional")}),
    ("ACWF", "2000"): dict(
        file="surveys/中国妇女地位调查/2000/w2000.dta",
        gender_var="v2", province_var="sheng", scale_max=4, agree_code=1,
        items={"i3_a": ("men-society/women-family", "traditional"),
               "i3_b": ("men-innately-more-capable", "traditional"),
               "i3_c": ("marry-well-over-work", "traditional"),
               "i3_d": ("woman-needs-children", "traditional"),
               "i3_e": ("women-avoid-surpassing-husband", "traditional"),
               "i3_g": ("women-looks-over-ability", "traditional"),
               "i3_h": ("30pct-women-leaders", "progressive"),
               "i3_i": ("men-share-half-housework", "progressive")}),
    ("ACWF", "2010"): dict(
        file="surveys/中国妇女地位调查/2010/w2010.DTA",
        gender_var="A1", province_var="sheng", scale_max=4, agree_code=1,
        items={"J2A": ("women-no-less-capable", "progressive"),
               "J2B": ("men-society/women-family", "traditional"),
               "J2C": ("breadwinning-mens-job", "traditional"),
               "J2D": ("husband-career-more-important", "traditional"),
               "J2E": ("men-share-housework", "progressive"),
               "J2F": ("boys-be-boys-girls-be-girls", "traditional"),
               "J2G": ("marry-well-over-work", "traditional"),
               "J2H": ("equal-leadership", "progressive"),
               "J2I": ("actively-promote-equality", "progressive")}),
    ("CFPS", "2014"): dict(
        file="surveys/CFPS/cfps2014_adult.dta",
        gender_var="cfps_gender", province_var="provcd14", scale_max=5, agree_code=5,
        items={"qm1101": ("men-career/women-family", "traditional"),
               "qm1102": ("marry-well-over-work", "traditional"),
               "qm1103": ("woman-needs-children", "traditional"),
               "qm1104": ("men-share-half-housework", "progressive")}),
    ("CFPS", "2020"): dict(
        file="surveys/CFPS/cfps2020_adult.dta",
        gender_var="gender", province_var="provcd20", scale_max=5, agree_code=5,
        items={"qm1101": ("men-career/women-family", "traditional"),
               "qm1102": ("marry-well-over-work", "traditional"),
               "qm1103": ("woman-needs-children", "traditional"),
               "qm1104": ("men-share-half-housework", "progressive")}),
}

_CGSS_STD = {"a421": ("men-career/women-family", "traditional"),
             "a422": ("men-innately-more-capable", "traditional"),
             "a423": ("marry-well-over-work", "traditional"),
             "a424": ("fire-women-first", "traditional"),
             "a425": ("equal-housework-split", "progressive")}
_CGSS_2021 = {"A42_1": ("men-career/women-family", "traditional"),
              "A42_2": ("men-innately-more-capable", "traditional"),
              "A42_3": ("marry-well-over-work", "traditional"),
              "A42_4": ("fire-women-first", "traditional"),
              "A42_5": ("equal-housework-split", "progressive")}
# Province variable name differs by year: 2018 uses 'provinces' (name), others 's41' (code).
_CGSS_PROV = {"2010": "s41", "2012": "s41", "2013": "s41", "2015": "s41",
              "2017": "s41", "2018": "provinces", "2023": "s41"}
for _y in ["2010", "2012", "2013", "2015", "2017", "2018", "2023"]:
    SURVEYS[("CGSS", _y)] = dict(file=f"surveys/CGSS/{_y}/CGSS{_y}.dta",
                                 gender_var="a2", province_var=_CGSS_PROV[_y],
                                 scale_max=5, agree_code=5, items=dict(_CGSS_STD))
SURVEYS[("CGSS", "2021")] = dict(file="surveys/CGSS/2021/CGSS2021.dta",
                                 gender_var="A2", province_var="s41",
                                 scale_max=5, agree_code=5, items=dict(_CGSS_2021))


def normalize_item(series: pd.Series, scale_max: int, agree_code: int, direction: str) -> pd.Series:
    """Map a raw Likert item to [0,1] where 1 = most traditional.

    Values outside [1, scale_max] -> NaN (missing). Logic:
      - agree_code tells us whether raw 1 or raw scale_max means 'strongly agree'.
      - traditional item: agreeing => traditional => 1.
      - progressive item: agreeing => egalitarian => 0.
    """
    s = series.where(series.between(1, scale_max))
    # fraction agreeing, on a 0..1 scale, oriented so that higher = more agreement
    if agree_code == scale_max:           # high code = agree (CFPS, CGSS)
        agree_frac = (s - 1) / (scale_max - 1)
    else:                                 # low code = agree (ACWF)
        agree_frac = (scale_max - s) / (scale_max - 1)
    return agree_frac if direction == "traditional" else (1 - agree_frac)


def load_recoded(dataset: str, year: str, extra_cols: list[str] | None = None):
    """Return (df, meta, item_norm_cols, index_col_name).

    df contains: raw items, gender (std 'female' 0/1 where known), province_raw,
    normalized item columns (suffix _z), and 'ideation_index'.
    """
    cfg = SURVEYS[(dataset, year)]
    items = cfg["items"]
    cols = list(items) + [cfg["gender_var"], cfg["province_var"]] + (extra_cols or [])
    cols = [c for c in dict.fromkeys(cols)]  # dedupe, keep order
    df, meta = pyreadstat.read_dta(str(ROOT / cfg["file"]), usecols=cols)

    norm_cols = []
    for var, (_short, direction) in items.items():
        zc = f"{var}_z"
        df[zc] = normalize_item(df[var], cfg["scale_max"], cfg["agree_code"], direction)
        norm_cols.append(zc)
    df["ideation_index"] = df[norm_cols].mean(axis=1)  # mean of valid items
    df["n_valid_items"] = df[norm_cols].notna().sum(axis=1)

    # standardize gender to female=1/male=0 where the coding is known
    gv = cfg["gender_var"]
    if dataset == "CFPS":          # 0=female,1=male  -> female=1
        df["female"] = (df[gv] == 0).astype("float").where(df[gv].isin([0, 1]))
    elif dataset in ("CGSS", "ACWF") and year != "1990":  # 1=male,2=female
        df["female"] = (df[gv] == 2).astype("float").where(df[gv].isin([1, 2]))
    elif dataset == "ACWF" and year == "1990":            # b3: 1=male,2=female
        df["female"] = (df[gv] == 2).astype("float").where(df[gv].isin([1, 2]))
    else:
        df["female"] = pd.NA
    df["province_raw"] = df[cfg["province_var"]]
    return df, meta, norm_cols, "ideation_index"


def cronbach_alpha(item_df: pd.DataFrame) -> float:
    """Standardized Cronbach's alpha on complete cases of the given items."""
    d = item_df.dropna()
    k = d.shape[1]
    if k < 2 or len(d) < 2:
        return float("nan")
    item_var = d.var(axis=0, ddof=1).sum()
    total_var = d.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_var / total_var)
