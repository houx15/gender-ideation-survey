#!/usr/bin/env python3
"""
03_ideation_audit.py

Detailed variable audit of the CORE comparable gender-ideation battery in each
survey-year. For every item it extracts, straight from the .dta:
  - variable label
  - value labels (the real ones in the file)
  - raw value distribution (including missing codes)
  - valid N and missing %
  - coded direction (traditional vs progressive) per processed/methodology.md

Outputs (SPEC sections 4.2, 9):
  - 02_variable_candidates.csv
  - 03_value_label_audit.csv
  - 04_missing_value_report.csv

Raw data is never modified; we only read the needed columns.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs" / "survey_exploration"

# direction: "traditional" = agreeing is traditional; "progressive" = agreeing is egalitarian.
# scale_max: top valid Likert code. valid range assumed [1, scale_max].
# agree_pole: which raw code means "strongly agree" (for interpreting direction).
CONFIG = [
    # dataset, year, file, gender_var, scale_max, agree_code, items{var:(short, direction)}
    dict(dataset="ACWF", year="1990",
         file="surveys/中国妇女地位调查/1990/w1990_fixed.dta",
         gender_var="b3", scale_max=5, agree_code=1,
         items={
             "w611": ("men-society/women-family", "traditional"),
             "w612": ("men-innately-more-capable", "traditional"),
             "w613": ("women-avoid-surpassing-husband", "traditional"),
             "w614": ("wife-supports-husband-success", "traditional"),
             "w615": ("child-takes-mother-surname", "progressive"),
             "w616": ("women-not-half-the-sky", "traditional"),
             "w617": ("men-handle-external-affairs", "traditional"),
             "w618": ("widow-remarry-leave-property", "traditional"),
         }),
    dict(dataset="ACWF", year="2000",
         file="surveys/中国妇女地位调查/2000/w2000.dta",
         gender_var="v2", scale_max=4, agree_code=1,
         items={
             "i3_a": ("men-society/women-family", "traditional"),
             "i3_b": ("men-innately-more-capable", "traditional"),
             "i3_c": ("marry-well-over-work", "traditional"),
             "i3_d": ("woman-needs-children", "traditional"),
             "i3_e": ("women-avoid-surpassing-husband", "traditional"),
             "i3_g": ("women-looks-over-ability", "traditional"),
             "i3_h": ("30pct-women-leaders", "progressive"),
             "i3_i": ("men-share-half-housework", "progressive"),
         }),
    dict(dataset="ACWF", year="2010",
         file="surveys/中国妇女地位调查/2010/w2010.DTA",
         gender_var="A1", scale_max=4, agree_code=1,
         items={
             "J2A": ("women-no-less-capable", "progressive"),
             "J2B": ("men-society/women-family", "traditional"),
             "J2C": ("breadwinning-mens-job", "traditional"),
             "J2D": ("husband-career-more-important", "traditional"),
             "J2E": ("men-share-housework", "progressive"),
             "J2F": ("boys-be-boys-girls-be-girls", "traditional"),
             "J2G": ("marry-well-over-work", "traditional"),
             "J2H": ("equal-leadership", "progressive"),
             "J2I": ("actively-promote-equality", "progressive"),
         }),
    dict(dataset="CFPS", year="2014",
         file="surveys/CFPS/cfps2014_adult.dta",
         gender_var="cfps_gender", scale_max=5, agree_code=5,
         items={
             "qm1101": ("men-career/women-family", "traditional"),
             "qm1102": ("marry-well-over-work", "traditional"),
             "qm1103": ("woman-needs-children", "traditional"),
             "qm1104": ("men-share-half-housework", "progressive"),
         }),
    dict(dataset="CFPS", year="2020",
         file="surveys/CFPS/cfps2020_adult.dta",
         gender_var="gender", scale_max=5, agree_code=5,
         items={
             "qm1101": ("men-career/women-family", "traditional"),
             "qm1102": ("marry-well-over-work", "traditional"),
             "qm1103": ("woman-needs-children", "traditional"),
             "qm1104": ("men-share-half-housework", "progressive"),
         }),
]

# CGSS: same five items across years; 2021 uses A42_n + A2. 2011 has no module.
CGSS_ITEMS_STD = {
    "a421": ("men-career/women-family", "traditional"),
    "a422": ("men-innately-more-capable", "traditional"),
    "a423": ("marry-well-over-work", "traditional"),
    "a424": ("fire-women-first", "traditional"),
    "a425": ("equal-housework-split", "progressive"),
}
CGSS_ITEMS_2021 = {
    "A42_1": ("men-career/women-family", "traditional"),
    "A42_2": ("men-innately-more-capable", "traditional"),
    "A42_3": ("marry-well-over-work", "traditional"),
    "A42_4": ("fire-women-first", "traditional"),
    "A42_5": ("equal-housework-split", "progressive"),
}
for y in ["2010", "2012", "2013", "2015", "2017", "2018", "2023"]:
    CONFIG.append(dict(dataset="CGSS", year=y,
                       file=f"surveys/CGSS/{y}/CGSS{y}.dta",
                       gender_var="a2", scale_max=5, agree_code=5,
                       items=dict(CGSS_ITEMS_STD)))
CONFIG.append(dict(dataset="CGSS", year="2021",
                   file="surveys/CGSS/2021/CGSS2021.dta",
                   gender_var="A2", scale_max=5, agree_code=5,
                   items=dict(CGSS_ITEMS_2021)))


def main() -> int:
    cand_rows, vlab_rows, miss_rows = [], [], []

    for cfg in CONFIG:
        path = ROOT / cfg["file"]
        items = cfg["items"]
        usecols = list(items.keys()) + [cfg["gender_var"]]
        try:
            df, meta = pyreadstat.read_dta(str(path), usecols=usecols)
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {cfg['dataset']} {cfg['year']}: {e}")
            continue
        var_labels = dict(zip(meta.column_names, meta.column_labels))
        val_labels = meta.variable_value_labels or {}
        n_total = len(df)
        scale_max = cfg["scale_max"]

        for var, (short, direction) in items.items():
            if var not in df.columns:
                cand_rows.append(dict(dataset=cfg["dataset"], year=cfg["year"],
                                      file=cfg["file"], variable=var, short=short,
                                      found=False))
                continue
            col = df[var]
            valid = col.where(col.between(1, scale_max))
            n_valid = int(valid.notna().sum())
            n_missing = n_total - n_valid

            cand_rows.append(dict(
                dataset=cfg["dataset"], year=cfg["year"], file=cfg["file"],
                variable=var, short=short, found=True,
                variable_label=var_labels.get(var, ""),
                conceptual_domain="gender_ideology",
                measurement_level="Likert",
                scale_max=scale_max, agree_code=cfg["agree_code"],
                direction=direction,
                analytic_coding="recode to [0,1], higher=more traditional",
                n_total=n_total, n_valid=n_valid,
                pct_valid=round(100 * n_valid / n_total, 1),
                mean_raw=round(float(valid.mean()), 3) if n_valid else None,
            ))

            # value-label audit: dump the real labels in the file
            vl = val_labels.get(var, {})
            for value, label in sorted(vl.items(), key=lambda kv: (isinstance(kv[0], str), kv[0])):
                count = int((col == value).sum())
                vlab_rows.append(dict(
                    dataset=cfg["dataset"], year=cfg["year"], variable=var,
                    short=short, value=value, value_label=label, count=count,
                    is_valid=bool(isinstance(value, (int, float)) and 1 <= value <= scale_max),
                ))

            # missing report: any raw value outside [1, scale_max]
            counts = col.value_counts(dropna=False)
            for value, count in counts.items():
                is_missing = pd.isna(value) or not (1 <= value <= scale_max)
                if is_missing:
                    miss_rows.append(dict(
                        dataset=cfg["dataset"], year=cfg["year"], variable=var,
                        short=short, missing_code=("NaN" if pd.isna(value) else value),
                        label=val_labels.get(var, {}).get(value, ""),
                        count=int(count),
                        pct=round(100 * int(count) / n_total, 2),
                    ))
        print(f"  audited {cfg['dataset']} {cfg['year']}: "
              f"{sum(1 for v in items if v in df.columns)}/{len(items)} items found, N={n_total}")

    cand = pd.DataFrame(cand_rows)
    vlab = pd.DataFrame(vlab_rows)
    miss = pd.DataFrame(miss_rows)
    cand.to_csv(OUT / "02_variable_candidates.csv", index=False)
    vlab.to_csv(OUT / "03_value_label_audit.csv", index=False)
    miss.to_csv(OUT / "04_missing_value_report.csv", index=False)
    print(f"\nWrote 02_variable_candidates.csv ({len(cand)} rows)")
    print(f"Wrote 03_value_label_audit.csv ({len(vlab)} rows)")
    print(f"Wrote 04_missing_value_report.csv ({len(miss)} rows)")

    # quick console summary of valid coverage
    print("\n=== item coverage (valid %) ===")
    found = cand[cand.found == True]  # noqa: E712
    summary = found.groupby(["dataset", "year"]).agg(
        items=("variable", "count"),
        min_pct_valid=("pct_valid", "min"),
        max_pct_valid=("pct_valid", "max"),
        N=("n_total", "first"),
    )
    print(summary.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
