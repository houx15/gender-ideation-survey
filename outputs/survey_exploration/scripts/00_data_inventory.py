#!/usr/bin/env python3
"""
00_data_inventory.py

Recursively scan the surveys/ folder and build:
  - 00_data_inventory.csv   : one row per data file (.dta/.DTA/.csv/.parquet/.xls)
  - 01_codebook_inventory.csv: one row per codebook/questionnaire/doc/pdf

Uses pyreadstat metadata-only reads so it stays fast on the large CFPS/CGSS/ACWF
.dta files (it does NOT load the data matrix, only the header + label tables).

Per SPEC.md sections 4.1 and 9. Raw data is never modified.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[3]          # repo root
SURVEYS = ROOT / "surveys"
OUT = ROOT / "outputs" / "survey_exploration"

DATA_EXTS = {".dta", ".csv", ".parquet", ".xls", ".xlsx"}
DOC_EXTS = {".doc", ".docx", ".pdf", ".md", ".txt", ".json", ".xls", ".xlsx"}

YEAR_RE = re.compile(r"(19|20)\d{2}")


def detect_dataset(path: Path) -> str:
    """Map a path to a dataset family from its location under surveys/."""
    parts = [p.lower() for p in path.parts]
    s = "/".join(parts)
    if "cfps" in s:
        return "CFPS"
    if "cgss" in s:
        return "CGSS"
    if "ceps" in s:
        return "CEPS"
    if "妇女" in "/".join(path.parts) or "acwf" in s:
        return "ACWF (中国妇女地位调查)"
    if "provincial" in s:
        return "Provincial"
    if "processed" in s:
        return "Processed"
    return "Unknown"


def detect_year(path: Path) -> str:
    """Best-effort year/wave from the filename or parent folder."""
    for cand in [path.name, path.parent.name]:
        m = YEAR_RE.search(cand)
        if m:
            return m.group(0)
    return ""


def read_dta_meta(path: Path) -> dict:
    """Metadata-only read of a Stata file."""
    try:
        _, meta = pyreadstat.read_dta(str(path), metadataonly=True)
        n_value_label_sets = len(meta.value_labels) if meta.value_labels else 0
        n_var_labels = sum(1 for v in meta.column_labels if v)
        return {
            "rows": meta.number_rows,
            "cols": meta.number_columns,
            "n_var_labels": n_var_labels,
            "has_var_labels": n_var_labels > 0,
            "n_value_label_sets": n_value_label_sets,
            "has_value_labels": n_value_label_sets > 0,
            "encoding": meta.file_encoding,
            "read_error": "",
        }
    except Exception as e:  # noqa: BLE001 - we want to log any failure, not crash the scan
        return {
            "rows": "", "cols": "", "n_var_labels": "", "has_var_labels": "",
            "n_value_label_sets": "", "has_value_labels": "", "encoding": "",
            "read_error": f"{type(e).__name__}: {e}",
        }


def read_tabular_meta(path: Path) -> dict:
    """Shape for csv/parquet/xls without committing to a full parse where avoidable."""
    base = {"n_var_labels": "", "has_var_labels": "", "n_value_label_sets": "",
            "has_value_labels": "", "encoding": "", "read_error": ""}
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path, nrows=5)
            n = sum(1 for _ in open(path, encoding="utf-8", errors="replace")) - 1
            base.update(rows=n, cols=df.shape[1])
        elif path.suffix.lower() == ".parquet":
            import pyarrow.parquet as pq
            pf = pq.ParquetFile(path)
            base.update(rows=pf.metadata.num_rows, cols=pf.metadata.num_columns)
        elif path.suffix.lower() in {".xls", ".xlsx"}:
            df = pd.read_excel(path, nrows=5)
            base.update(rows="(see file)", cols=df.shape[1])
        return base
    except Exception as e:  # noqa: BLE001
        base.update(rows="", cols="", read_error=f"{type(e).__name__}: {e}")
        return base


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data_rows: list[dict] = []
    doc_rows: list[dict] = []

    for dirpath, _dirnames, filenames in os.walk(SURVEYS):
        for fn in filenames:
            if fn.startswith(".") or fn == ".DS_Store":
                continue
            p = Path(dirpath) / fn
            ext = p.suffix.lower()
            rel = p.relative_to(ROOT)
            size_mb = round(p.stat().st_size / 1e6, 2)
            dataset = detect_dataset(p)
            year = detect_year(p)

            if ext == ".dta":
                meta = read_dta_meta(p)
                data_rows.append({
                    "dataset": dataset, "year_wave": year, "file": str(rel),
                    "format": "stata", "size_mb": size_mb, **meta,
                })
            elif ext in {".csv", ".parquet"}:
                meta = read_tabular_meta(p)
                data_rows.append({
                    "dataset": dataset, "year_wave": year, "file": str(rel),
                    "format": ext.lstrip("."), "size_mb": size_mb, **meta,
                })
            elif ext in {".xls", ".xlsx"}:
                # Excel files in provincial/ are data; elsewhere likely reference.
                meta = read_tabular_meta(p)
                row = {"dataset": dataset, "year_wave": year, "file": str(rel),
                       "format": ext.lstrip("."), "size_mb": size_mb, **meta}
                data_rows.append(row)
                doc_rows.append({"dataset": dataset, "year_wave": year,
                                 "file": str(rel), "format": ext.lstrip("."),
                                 "size_mb": size_mb, "readable": "tabular"})
            elif ext in {".doc", ".docx", ".pdf", ".md", ".txt", ".json"}:
                doc_rows.append({
                    "dataset": dataset, "year_wave": year, "file": str(rel),
                    "format": ext.lstrip("."), "size_mb": size_mb,
                    "readable": "yes" if ext in {".md", ".txt", ".json"} else "binary",
                })
            # ignore .zip and unknown extensions for now (logged below)

    data_df = pd.DataFrame(data_rows).sort_values(["dataset", "year_wave", "file"])
    doc_df = pd.DataFrame(doc_rows).sort_values(["dataset", "year_wave", "file"])

    data_path = OUT / "00_data_inventory.csv"
    doc_path = OUT / "01_codebook_inventory.csv"
    data_df.to_csv(data_path, index=False)
    doc_df.to_csv(doc_path, index=False)

    print(f"Wrote {data_path} ({len(data_df)} data files)")
    print(f"Wrote {doc_path} ({len(doc_df)} codebook/doc files)")
    print()
    print("=== DATA FILES (dataset, year, rows x cols, labels) ===")
    for _, r in data_df.iterrows():
        labels = ""
        if r.get("has_var_labels") != "":
            labels = f" | varlabels={r['has_var_labels']} vallabels={r['has_value_labels']}"
        err = f"  !! {r['read_error']}" if r.get("read_error") else ""
        print(f"  [{r['dataset']:<26}] {r['year_wave']:<5} {str(r['rows']):>8} x {str(r['cols']):>4}  "
              f"{r['file']}{labels}{err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
