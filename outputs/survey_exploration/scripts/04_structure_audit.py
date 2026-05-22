#!/usr/bin/env python3
"""
04_structure_audit.py

Catalogue the ID / weight / region / outcome variables needed for the
individual-practice and intergenerational analyses (SPEC 4.1, 5.2-5.7, 8).

Strategy: keyword-scan variable labels AND variable names (metadata only) in the
main individual files of each survey, tag each hit with a conceptual domain, and
write tables/structural_variable_candidates.csv.

This is a discovery aid, not a final coding decision — every candidate must still
be confirmed against value labels before use.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "outputs" / "survey_exploration"

FILES = {
    ("CFPS", "2014"): "surveys/CFPS/cfps2014_adult.dta",
    ("CFPS", "2020"): "surveys/CFPS/cfps2020_adult.dta",
    ("CGSS", "2017"): "surveys/CGSS/2017/CGSS2017.dta",
    ("CGSS", "2021"): "surveys/CGSS/2021/CGSS2021.dta",
    ("ACWF", "2010"): "surveys/中国妇女地位调查/2010/w2010.DTA",
    ("CEPS", "baseline-student"): "surveys/CEPS13-14/CEPS基线调查学生数据.dta",
    ("CEPS", "baseline-parent"): "surveys/CEPS13-14/CEPS基线调查家长数据.dta",
}

# domain -> (label keywords, name keywords)
DOMAINS = {
    "id_person":     (["个人编码", "个人id", "受访者编码", "学生编号", "本人编码"], ["pid", "id_", "_id", "ids", "stuid", "iid"]),
    "id_family":     (["家庭编码", "家庭样本", "户编码", "家庭id"], ["fid", "famid", "hhid"]),
    "id_parent_child": (["父亲编码", "母亲编码", "子女编码", "配偶编码", "父母编码"], ["pid_f", "pid_m", "fid_", "mother", "father"]),
    "weight":        ["权数", "权重", "weight", "抽样权"],
    "region":        ["省", "城乡", "户口", "居住地", "城镇", "农村", "区县"],
    "birth_age":     ["出生年", "出生日期", "年龄", "出生"],
    "education":     ["教育", "学历", "受教育", "文化程度", "上过学", "学校", "念书", "上学"],
    "edu_expect":    ["期望", "希望你", "读到", "最高学历期望", "教育期望"],
    "marriage":      ["婚姻", "结婚", "初婚", "配偶", "已婚", "未婚", "离婚"],
    "fertility":     ["生育", "孩子数", "子女数", "生孩子", "怀孕", "孩子个数", "活产"],
    "employment":    ["工作", "就业", "职业", "单位", "在业", "雇佣", "劳动"],
    "leadership":    ["领导", "负责人", "管理", "干部", "晋升", "职务"],
    "income":        ["收入", "工资", "挣钱", "薪"],
    "housework":     ["家务", "照料", "照顾", "做饭", "家庭杂事"],
    "science_math":  ["数学", "科学", "理科", "成绩", "学科", "兴趣"],
}


def matches(text: str, name: str, spec) -> bool:
    if isinstance(spec, tuple):
        lab_kw, name_kw = spec
        return any(k.lower() in (text or "").lower() for k in lab_kw) or \
               any(k.lower() in (name or "").lower() for k in name_kw)
    return any(k.lower() in (text or "").lower() for k in spec)


def main() -> int:
    rows = []
    for (dataset, wave), rel in FILES.items():
        path = ROOT / rel
        if not path.exists():
            print(f"  MISSING {rel}")
            continue
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        labels = dict(zip(meta.column_names, meta.column_labels))
        vvl = meta.variable_value_labels or {}
        for var, lab in labels.items():
            for domain, spec in DOMAINS.items():
                if matches(lab or "", var, spec):
                    rows.append(dict(dataset=dataset, wave=wave, domain=domain,
                                     variable=var, variable_label=lab or "",
                                     has_value_labels=var in vvl))
        print(f"  scanned {dataset} {wave}: {len(meta.column_names)} vars")

    df = pd.DataFrame(rows)
    out = OUT / "tables" / "structural_variable_candidates.csv"
    df.to_csv(out, index=False)
    print(f"\nWrote {out} ({len(df)} candidate hits)")
    print("\nHits per dataset x domain:")
    print(df.pivot_table(index="domain", columns=["dataset", "wave"],
                         values="variable", aggfunc="count", fill_value=0).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
