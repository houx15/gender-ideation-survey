#!/usr/bin/env python3
"""
02_ideation_discovery.py

Discover candidate gender-ideation items in every survey .dta by keyword-scanning
the variable labels (metadata only, fast). This is the RQ 5.1 question
"which gender-ideation items exist in each survey?" answered empirically rather
than only from survey-config.md.

Writes: tables/ideation_item_discovery.csv
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs" / "survey_exploration"

# Files to scan: main individual-level files per dataset-year.
FILES = {
    ("ACWF", "1990"): "surveys/中国妇女地位调查/1990/w1990_fixed.dta",
    ("ACWF", "2000"): "surveys/中国妇女地位调查/2000/w2000.dta",
    ("ACWF", "2010"): "surveys/中国妇女地位调查/2010/w2010.DTA",
    ("CFPS", "2014"): "surveys/CFPS/cfps2014_adult.dta",
    ("CFPS", "2020"): "surveys/CFPS/cfps2020_adult.dta",
    ("CGSS", "2010"): "surveys/CGSS/2010/CGSS2010.dta",
    ("CGSS", "2011"): "surveys/CGSS/2011/CGSS2011.dta",
    ("CGSS", "2012"): "surveys/CGSS/2012/CGSS2012.dta",
    ("CGSS", "2013"): "surveys/CGSS/2013/CGSS2013.dta",
    ("CGSS", "2015"): "surveys/CGSS/2015/CGSS2015.dta",
    ("CGSS", "2017"): "surveys/CGSS/2017/CGSS2017.dta",
    ("CGSS", "2018"): "surveys/CGSS/2018/CGSS2018.dta",
    ("CGSS", "2021"): "surveys/CGSS/2021/CGSS2021.dta",
    ("CGSS", "2023"): "surveys/CGSS/2023/CGSS2023.dta",
    ("CEPS", "baseline-student"): "surveys/CEPS13-14/CEPS基线调查学生数据.dta",
    ("CEPS", "baseline-parent"): "surveys/CEPS13-14/CEPS基线调查家长数据.dta",
    ("CEPS", "followup-student"): "surveys/CEPS13-14/CEPS追访学生数据.dta",
}

# Keywords that mark a likely gender-ideation / gender-role attitude item.
KEYWORDS = [
    "男人", "女人", "男性", "女性", "男孩", "女孩", "妇女",
    "家务", "嫁", "娶", "丈夫", "妻子", "夫妻", "男女",
    "性别", "重男轻女", "传宗接代", "养家", "事业为", "以家庭为",
    "女子无才", "干得好不如", "半边天", "领导", "当官",
]
# Labels containing these are usually NOT attitude items (filter false positives).
EXCLUDE = ["编号", "id", "ID", "省", "市", "县", "村", "weight", "权数", "权重"]


def main() -> int:
    rows = []
    for (dataset, year), relpath in FILES.items():
        path = ROOT / relpath
        if not path.exists():
            print(f"  MISSING {relpath}")
            continue
        try:
            _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {relpath}: {e}")
            continue
        labels = dict(zip(meta.column_names, meta.column_labels))
        for var, lab in labels.items():
            if not lab:
                continue
            if any(kw in lab for kw in KEYWORDS) and not any(x in lab for x in EXCLUDE):
                rows.append({
                    "dataset": dataset, "year_wave": year, "variable": var,
                    "variable_label": lab,
                    "has_value_labels": var in (meta.variable_value_labels or {}),
                })
        print(f"  scanned {dataset} {year}: {len(meta.column_names)} vars")

    df = pd.DataFrame(rows)
    out = OUT / "tables" / "ideation_item_discovery.csv"
    df.to_csv(out, index=False)
    print(f"\nWrote {out} ({len(df)} candidate items)")
    print("\nPer dataset-year candidate counts:")
    print(df.groupby(["dataset", "year_wave"]).size().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
