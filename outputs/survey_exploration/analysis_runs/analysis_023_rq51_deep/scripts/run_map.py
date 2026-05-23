#!/usr/bin/env python3
"""analysis_023 — provincial choropleth maps.

ONE map per survey program (CFPS, CGSS, ACWF) at the province level, with a
caveat banner.  Output: vector PDF.  Province codes are standardized to GB/T
2260 2-digit prefixes (11..65) which match the GeoJSON `adcode/10000`.

The GeoJSON lives in figures/_geo/china_provinces.geojson (DataV.Aliyun).
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
FIGS = RUN / "figures"
TABLES = RUN / "tables"
GEO = FIGS / "_geo" / "china_provinces.geojson"

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L  # noqa: E402

# CGSS sequential 1..31 -> standard GB2260 2-digit province code.
_CGSS_SEQ_TO_GB = {
    1: 11, 2: 12, 3: 13, 4: 14, 5: 15,
    6: 21, 7: 22, 8: 23,
    9: 31, 10: 32, 11: 33, 12: 34, 13: 35, 14: 36, 15: 37,
    16: 41, 17: 42, 18: 43, 19: 44, 20: 45, 21: 46,
    22: 50, 23: 51, 24: 52, 25: 53, 26: 54,
    27: 61, 28: 62, 29: 63, 30: 64, 31: 65,
}

# CGSS 2018 stores province names; map to GB.
_NAME_TO_GB = {
    "北京市": 11, "天津市": 12, "河北省": 13, "山西省": 14, "内蒙古自治区": 15,
    "辽宁省": 21, "吉林省": 22, "黑龙江省": 23,
    "上海市": 31, "江苏省": 32, "浙江省": 33, "安徽省": 34, "福建省": 35,
    "江西省": 36, "山东省": 37,
    "河南省": 41, "湖北省": 42, "湖南省": 43, "广东省": 44,
    "广西壮族自治区": 45, "海南省": 46,
    "重庆市": 50, "四川省": 51, "贵州省": 52, "云南省": 53, "西藏自治区": 54,
    "陕西省": 61, "甘肃省": 62, "青海省": 63, "宁夏回族自治区": 64,
    "新疆维吾尔自治区": 65,
}


def standardized_province(dataset: str, year: str, raw_series: pd.Series) -> pd.Series:
    """Convert each survey's province coding to GB2260 2-digit codes (11..65)."""
    s = pd.to_numeric(raw_series, errors="coerce") if dataset != "CGSS" or year != "2018" \
        else None

    if dataset == "CFPS":
        # provcd14/20: already GB2260 2-digit (e.g. 11, 12, ..., 65)
        s = s.where(s.between(11, 65))
        return s.astype("float64")

    if dataset == "ACWF":
        # sheng: GB2260 2-digit
        s = s.where(s.between(11, 65))
        return s.astype("float64")

    if dataset == "CGSS":
        if year == "2018":
            return raw_series.map(_NAME_TO_GB).astype("float64")
        s = s.where(s.between(1, 31))
        return s.map(_CGSS_SEQ_TO_GB).astype("float64")

    return pd.Series(np.nan, index=raw_series.index, dtype="float64")


def province_means_by_program() -> pd.DataFrame:
    """Pool waves within each program; return mean & N per (program, province)."""
    rows = []
    for (dataset, year), cfg in L.SURVEYS.items():
        df, _m, _n, idx = L.load_recoded(dataset, year)
        df["prov_gb"] = standardized_province(dataset, year, df[cfg["province_var"]])
        for prov, g in df.dropna(subset=["prov_gb", idx]).groupby("prov_gb"):
            rows.append(dict(program=dataset, wave=year,
                             prov_gb=int(prov),
                             n=int(len(g)),
                             mean=float(g[idx].mean())))
    long = pd.DataFrame(rows)
    # pooled per (program, province)
    pooled = (long.groupby(["program", "prov_gb"], as_index=False)
                  .apply(lambda g: pd.Series({
                      "n": int(g["n"].sum()),
                      "mean": float((g["mean"] * g["n"]).sum() / g["n"].sum())}),
                         include_groups=False)
                  .reset_index(drop=True))
    return pooled


def plot_program_map(geojson_path: Path, program_df: pd.DataFrame, program: str,
                     out_path: Path, vmin: float, vmax: float) -> None:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["pdf.fonttype"] = 42
    matplotlib.rcParams["ps.fonttype"] = 42
    matplotlib.rcParams["svg.fonttype"] = "none"
    import matplotlib.pyplot as plt
    import geopandas as gpd

    gdf = gpd.read_file(geojson_path)
    # Drop the "100000_JD" pseudo-feature (dotted-line border for sea claims).
    ad = pd.to_numeric(gdf["adcode"], errors="coerce")
    gdf = gdf.loc[ad.notna()].copy()
    gdf["prov_gb"] = (ad[ad.notna()].astype(int) // 10000).astype(int).values
    merged = gdf.merge(program_df[program_df.program == program][["prov_gb", "mean", "n"]],
                       on="prov_gb", how="left")

    fig, ax = plt.subplots(figsize=(9, 7))
    merged.plot(column="mean", ax=ax, cmap="RdYlBu_r", vmin=vmin, vmax=vmax,
                edgecolor="white", linewidth=0.3,
                missing_kwds={"color": "lightgrey", "edgecolor": "white",
                              "label": "no data"})
    ax.set_axis_off()
    ax.set_title(f"{program} — mean gender-ideation index by province\n"
                 f"(1 = most traditional; pooled across waves)",
                 fontsize=12)
    # colorbar
    sm = plt.cm.ScalarMappable(cmap="RdYlBu_r",
                               norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02, shrink=0.7)
    cbar.set_label("mean ideation (1 = traditional)")

    # caveat box
    caveat = ("Caveat: this map is NOT provincially representative. "
              "Within-province samples vary widely, some provinces have few or no\n"
              "respondents (shown in grey), and the displayed mean mixes urban / rural / "
              "cohort composition. Treat as an exploratory descriptive only.")
    fig.text(0.5, 0.04, caveat, ha="center", fontsize=8, color="dimgrey",
             style="italic", wrap=True)
    fig.tight_layout()
    fig.savefig(out_path, format="pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    print("computing province means ...", flush=True)
    prov = province_means_by_program()
    prov.to_csv(TABLES / "province_means.csv", index=False)

    # Shared color scale: 1st–99th percentile of all program means.
    vmin = float(np.nanpercentile(prov["mean"], 5))
    vmax = float(np.nanpercentile(prov["mean"], 95))

    for program in ["CFPS", "CGSS", "ACWF"]:
        out = FIGS / f"province_map_{program.lower()}.pdf"
        print(f"drawing {out.name} ...", flush=True)
        plot_program_map(GEO, prov, program, out, vmin, vmax)

    print("\nProvince means summary (top + bottom 5 per program):")
    for program in ["CFPS", "CGSS", "ACWF"]:
        sub = prov[prov.program == program].sort_values("mean")
        print(f"\n{program}: most progressive 3 / most traditional 3 (pooled)")
        print(sub.head(3).to_string(index=False))
        print(" ...")
        print(sub.tail(3).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
