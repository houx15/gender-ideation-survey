#!/usr/bin/env python3
"""
analysis_001 — gender-ideation MEASUREMENT (RQ 5.1).

Question: How is gender ideation measured in each survey, is a mean index
defensible (internal consistency), and how does it distribute by gender and year?

Outputs in the run folder:
  01_descriptive_table.csv  — N, mean/sd/min/max of the index, by dataset-year and by gender
  02_missing_table.csv      — valid-item coverage and respondents with >=1 valid item
  04_result_table.csv       — Cronbach's alpha + mean inter-item correlation per survey-year
  cross_check.csv           — our index mean vs surveys/processed parquet (sanity check)
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
SCRIPTS = HERE.parents[3] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import ideation_lib as L  # noqa: E402

RUN = HERE.parents[1]
ROOT = L.ROOT


def main() -> int:
    desc_rows, miss_rows, res_rows = [], [], []
    index_means = {}

    for (dataset, year), cfg in L.SURVEYS.items():
        df, _meta, norm_cols, idx = L.load_recoded(dataset, year)
        n_total = len(df)
        has_any = df["n_valid_items"] >= 1
        sub = df[has_any]
        index_means[(dataset, year)] = sub[idx].mean()

        # descriptive: overall + by gender
        def block(frame, group):
            s = frame[idx]
            return dict(dataset=dataset, year=year, group=group, n=int(s.notna().sum()),
                        mean=round(float(s.mean()), 4) if s.notna().any() else None,
                        sd=round(float(s.std()), 4) if s.notna().any() else None,
                        min=round(float(s.min()), 4) if s.notna().any() else None,
                        max=round(float(s.max()), 4) if s.notna().any() else None)
        desc_rows.append(block(sub, "all"))
        if sub["female"].notna().any():
            desc_rows.append(block(sub[sub["female"] == 1], "female"))
            desc_rows.append(block(sub[sub["female"] == 0], "male"))

        # missing/coverage
        miss_rows.append(dict(
            dataset=dataset, year=year, n_total=n_total,
            n_items=len(norm_cols),
            n_any_valid=int(has_any.sum()),
            pct_any_valid=round(100 * has_any.mean(), 1),
            n_all_valid=int((df["n_valid_items"] == len(norm_cols)).sum()),
            pct_all_valid=round(100 * (df["n_valid_items"] == len(norm_cols)).mean(), 1),
            mean_valid_items=round(float(df["n_valid_items"].mean()), 2),
        ))

        # internal consistency on normalized items
        item_df = df[norm_cols]
        alpha = L.cronbach_alpha(item_df)
        corr = item_df.corr()
        iu = corr.where(~np.eye(len(corr), dtype=bool))
        mean_r = float(np.nanmean(iu.values))
        res_rows.append(dict(
            dataset=dataset, year=year, n_items=len(norm_cols),
            n_complete=int(item_df.dropna().shape[0]),
            cronbach_alpha=round(alpha, 3),
            mean_inter_item_r=round(mean_r, 3),
            min_inter_item_r=round(float(np.nanmin(iu.values)), 3),
            max_inter_item_r=round(float(np.nanmax(iu.values)), 3),
        ))
        print(f"  {dataset} {year}: alpha={alpha:.3f}, mean r={mean_r:.3f}, "
              f"index mean={sub[idx].mean():.3f}, N={int(has_any.sum())}")

    pd.DataFrame(desc_rows).to_csv(RUN / "01_descriptive_table.csv", index=False)
    pd.DataFrame(miss_rows).to_csv(RUN / "02_missing_table.csv", index=False)
    pd.DataFrame(res_rows).to_csv(RUN / "04_result_table.csv", index=False)

    # cross-check vs processed parquet (national means per dataset-year)
    cross = []
    pq = ROOT / "surveys" / "processed" / "gender_ideation_by_year.csv"
    if pq.exists():
        ref = pd.read_csv(pq)
        print("\n  cross-check columns:", list(ref.columns))
        ref.to_csv(RUN / "processed_by_year_reference.csv", index=False)
        for (dataset, year), m in index_means.items():
            cross.append(dict(dataset=dataset, year=year, our_index_mean=round(float(m), 4)))
        pd.DataFrame(cross).to_csv(RUN / "cross_check.csv", index=False)
    print("\nWrote analysis_001 tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
