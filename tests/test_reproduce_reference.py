"""Integration test: the recoded index must reproduce surveys/processed.

This locks the invariant that ideation_lib + the analysis pipeline match the
established methodology (surveys/processed/gender_ideation_by_year.csv).
Reads the real, gitignored .dta files, so it is marked `integration`.
"""
from pathlib import Path
import pandas as pd
import pytest

import ideation_lib as L

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "surveys" / "processed" / "gender_ideation_by_year.csv"


@pytest.mark.integration
@pytest.mark.skipif(not REF.exists(), reason="processed reference not present")
def test_index_reproduces_processed_by_year():
    ref = pd.read_csv(REF)
    ref["dataset"] = ref["dataset"].str.upper()
    ref_map = {(r.dataset, str(r.year)): r.gender_ideation_mean for r in ref.itertuples()}

    checked = 0
    for (dataset, year), _cfg in L.SURVEYS.items():
        key = (dataset.upper(), year)
        if key not in ref_map:
            continue
        df, _m, _norm, idx = L.load_recoded(dataset, year)
        ours = df.loc[df["n_valid_items"] >= 1, idx].mean()
        assert ours == pytest.approx(ref_map[key], abs=5e-4), f"{key}: {ours} vs {ref_map[key]}"
        checked += 1
    assert checked >= 10  # all ACWF/CFPS/CGSS reference rows covered
