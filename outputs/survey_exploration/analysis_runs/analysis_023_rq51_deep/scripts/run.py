#!/usr/bin/env python3
"""analysis_023 — RQ 5.1 deep-dive.

Builds: cleaning table, item-level + index descriptives, pooled & wave-resolved
cohort trend (PDF), CFPS pid-dedup report, within-cohort gender / urban / corr
breakdowns.  Map output is in scripts/run_map.py (separate to keep dependencies
optional).

Usage:
    python outputs/survey_exploration/analysis_runs/analysis_023_rq51_deep/scripts/run.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
TABLES = RUN / "tables"
FIGS = RUN / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L                # noqa: E402
import rq51_helpers as H                # noqa: E402

PROGRAMS = ["CFPS", "CGSS", "ACWF"]
PROGRAM_COLOR = {"CFPS": "#1f77b4", "CGSS": "#d62728", "ACWF": "#2ca02c"}


# --------------------------------------------------------------------------- #
# (1) cleaning steps per (dataset, year)
# --------------------------------------------------------------------------- #

def build_cleaning_table() -> pd.DataFrame:
    rows = []
    for (dataset, year) in L.SURVEYS:
        for step in H.cleaning_steps_table(dataset, year):
            rows.append(dict(dataset=dataset, year=year, **step))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# (2) item-level and index descriptives
# --------------------------------------------------------------------------- #

def build_item_descriptives() -> tuple[pd.DataFrame, pd.DataFrame]:
    item_rows = []
    index_rows = []
    for (dataset, year), cfg in L.SURVEYS.items():
        df, _meta, norm_cols, idx = L.load_recoded(dataset, year)
        scale_max = cfg["scale_max"]
        for raw_var, (short, direction) in cfg["items"].items():
            raw = df[raw_var]
            raw_in_range = raw.where(raw.between(1, scale_max))
            n = int(raw_in_range.notna().sum())
            miss = float(1 - n / len(df)) if len(df) else float("nan")
            item_rows.append(dict(
                dataset=dataset, year=year, item=raw_var, short=short,
                direction=direction, reversed=("Y" if direction == "progressive" else "N"),
                scale_max=scale_max,
                n=n,
                mean_raw=round(float(raw_in_range.mean()), 4) if n else np.nan,
                sd_raw=round(float(raw_in_range.std(ddof=1)), 4) if n > 1 else np.nan,
                min_raw=int(raw_in_range.min()) if n else np.nan,
                max_raw=int(raw_in_range.max()) if n else np.nan,
                var_raw=round(float(raw_in_range.var(ddof=1)), 4) if n > 1 else np.nan,
                missing_pct=round(miss * 100, 2),
                mean_normalized=round(float(df[f"{raw_var}_z"].mean()), 4),
            ))
        # aggregate index
        ix = df[idx].dropna()
        index_rows.append(dict(
            dataset=dataset, year=year, n=int(len(ix)),
            mean=round(float(ix.mean()), 4),
            sd=round(float(ix.std(ddof=1)), 4),
            min=round(float(ix.min()), 4),
            max=round(float(ix.max()), 4),
            var=round(float(ix.var(ddof=1)), 4),
            alpha=round(float(L.cronbach_alpha(df[norm_cols])), 3),
        ))
    return pd.DataFrame(item_rows), pd.DataFrame(index_rows)


# --------------------------------------------------------------------------- #
# (3) cohort time trend — pooled & by-wave
# --------------------------------------------------------------------------- #

def _attach_context(dataset: str, year: str) -> pd.DataFrame:
    """Load ideation index + birth_year + female + urban + edu + emp + income.

    Aligns by row index (pyreadstat returns rows in the same order each call).
    Adds program/wave/cohort columns.
    """
    df, _m, _n, idx = L.load_recoded(dataset, year)
    df = df.reset_index(drop=True)
    df["birthy"] = H.birth_year(dataset, year).reset_index(drop=True)
    df["urban"] = H.urban_indicator(dataset, year).reset_index(drop=True)
    df["edu_yrs"] = H.education_years(dataset, year).reset_index(drop=True)
    df["employed"] = H.employed_indicator(dataset, year).reset_index(drop=True)
    df["income"] = H.personal_income(dataset, year).reset_index(drop=True)
    df["ideation"] = df[idx]
    df["program"] = dataset
    df["wave"] = year
    df["cohort"] = df["birthy"].apply(H.cohort_label)
    return df


def assemble_pooled_panel() -> tuple[pd.DataFrame, dict]:
    """Stack all surveys into one long frame; also return CFPS dedup info."""
    frames = []
    cfps_pid_frames = []
    for (dataset, year) in L.SURVEYS:
        d = _attach_context(dataset, year)
        # For CFPS we additionally want pid to dedup
        if dataset == "CFPS":
            import pyreadstat
            pid_df, _ = pyreadstat.read_dta(
                str(L.ROOT / L.SURVEYS[(dataset, year)]["file"]),
                usecols=["pid"])
            d["pid"] = pid_df["pid"].reset_index(drop=True)
            cfps_pid_frames.append(d[["pid", "wave", "ideation"]].copy())
        # Common columns
        keep = ["program", "wave", "cohort", "birthy", "female", "urban",
                "edu_yrs", "employed", "income", "ideation"]
        if "pid" in d.columns:
            keep.append("pid")
        frames.append(d[[c for c in keep if c in d.columns]])
    pooled = pd.concat(frames, ignore_index=True, sort=False)

    # CFPS dedup summary across both waves
    if cfps_pid_frames:
        cfps_long = pd.concat(cfps_pid_frames, ignore_index=True)
        _, dedup_summary = H.cfps_dedup_keep_latest(
            cfps_long, pid_col="pid", wave_col="wave",
            value_col="ideation", change_eps=0.01)
    else:
        dedup_summary = {}

    return pooled, dedup_summary


def apply_cfps_dedup(pooled: pd.DataFrame) -> pd.DataFrame:
    """Within the pooled panel, keep only the latest CFPS row per pid.

    Non-CFPS rows are left untouched.
    """
    if "pid" not in pooled.columns:
        return pooled
    is_cfps = pooled["program"] == "CFPS"
    cfps = pooled.loc[is_cfps].copy()
    other = pooled.loc[~is_cfps].copy()
    cfps = cfps.dropna(subset=["pid"])
    cfps_dedup, _ = H.cfps_dedup_keep_latest(
        cfps, pid_col="pid", wave_col="wave",
        value_col="ideation", change_eps=0.01)
    return pd.concat([cfps_dedup, other], ignore_index=True, sort=False)


def cohort_mean_se(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    """mean, sd, se, n of ideation grouped by group_cols (drops NaN cohort)."""
    g = df.dropna(subset=["cohort", "ideation"]).groupby(group_cols, observed=True)
    out = g["ideation"].agg(["mean", "std", "count"]).reset_index()
    out = out.rename(columns={"mean": "mean", "std": "sd", "count": "n"})
    out["se"] = out["sd"] / np.sqrt(out["n"])
    out["mean"] = out["mean"].round(4)
    out["sd"] = out["sd"].round(4)
    out["se"] = out["se"].round(4)
    return out


# --------------------------------------------------------------------------- #
# (4) within-cohort breakdowns + correlations
# --------------------------------------------------------------------------- #

def gender_gap_by_cohort(df: pd.DataFrame) -> pd.DataFrame:
    g = df.dropna(subset=["cohort", "female", "ideation"]).groupby(
        ["program", "cohort", "female"], observed=True)["ideation"].agg(["mean", "std", "count"])
    g = g.reset_index().pivot_table(index=["program", "cohort"],
                                    columns="female", values=["mean", "std", "count"])
    rows = []
    for (program, cohort), r in g.iterrows():
        n_f = float(r.get(("count", 1.0), np.nan))
        n_m = float(r.get(("count", 0.0), np.nan))
        mean_f = float(r.get(("mean", 1.0), np.nan))
        mean_m = float(r.get(("mean", 0.0), np.nan))
        sd_f = float(r.get(("std", 1.0), np.nan))
        sd_m = float(r.get(("std", 0.0), np.nan))
        # Welch's t for F vs M
        if n_f > 1 and n_m > 1:
            se = np.sqrt(sd_f**2 / n_f + sd_m**2 / n_m)
            t = (mean_f - mean_m) / se if se > 0 else np.nan
        else:
            t = np.nan
        rows.append(dict(program=program, cohort=cohort,
                         n_female=int(n_f) if not np.isnan(n_f) else 0,
                         n_male=int(n_m) if not np.isnan(n_m) else 0,
                         mean_female=round(mean_f, 4) if not np.isnan(mean_f) else np.nan,
                         mean_male=round(mean_m, 4) if not np.isnan(mean_m) else np.nan,
                         F_minus_M=round(mean_f - mean_m, 4) if not np.isnan(mean_f - mean_m) else np.nan,
                         welch_t=round(t, 2) if not np.isnan(t) else np.nan))
    return pd.DataFrame(rows)


def urban_gap_by_cohort(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (program, cohort), g in df.dropna(subset=["cohort", "urban", "ideation"]).groupby(
            ["program", "cohort"], observed=True):
        m_u = g.loc[g.urban == 1.0, "ideation"]
        m_r = g.loc[g.urban == 0.0, "ideation"]
        if len(m_u) > 1 and len(m_r) > 1:
            t = (m_u.mean() - m_r.mean()) / np.sqrt(m_u.var(ddof=1) / len(m_u)
                                                    + m_r.var(ddof=1) / len(m_r))
        else:
            t = np.nan
        rows.append(dict(program=program, cohort=cohort,
                         n_urban=len(m_u), n_rural=len(m_r),
                         mean_urban=round(float(m_u.mean()), 4) if len(m_u) else np.nan,
                         mean_rural=round(float(m_r.mean()), 4) if len(m_r) else np.nan,
                         U_minus_R=round(float(m_u.mean() - m_r.mean()), 4)
                                 if len(m_u) and len(m_r) else np.nan,
                         welch_t=round(float(t), 2) if not np.isnan(t) else np.nan))
    return pd.DataFrame(rows)


def correlations_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (program, wave), g in df.groupby(["program", "wave"], observed=True):
        for var in ["edu_yrs", "employed", "income"]:
            x = pd.to_numeric(g[var], errors="coerce")
            y = pd.to_numeric(g["ideation"], errors="coerce")
            if var == "income":
                x = np.log1p(x)
            both = pd.concat([x, y], axis=1).dropna()
            if len(both) < 30:
                rows.append(dict(program=program, wave=wave, variable=var,
                                 n=len(both), pearson_r=np.nan, p=np.nan, note="n<30"))
                continue
            if both.iloc[:, 0].nunique() < 2 or both.iloc[:, 1].nunique() < 2:
                rows.append(dict(program=program, wave=wave, variable=var,
                                 n=int(len(both)), pearson_r=np.nan, p=np.nan,
                                 note="constant_input"))
                continue
            from scipy.stats import pearsonr
            r, p = pearsonr(both.iloc[:, 0], both.iloc[:, 1])
            rows.append(dict(program=program, wave=wave, variable=var,
                             n=int(len(both)),
                             pearson_r=round(float(r), 4),
                             p=float(f"{p:.4g}"),
                             note=""))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# (5) figures
# --------------------------------------------------------------------------- #

def plot_cohort_pooled(df_pooled: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["pdf.fonttype"] = 42  # TrueType -> vector text
    matplotlib.rcParams["ps.fonttype"] = 42
    matplotlib.rcParams["svg.fonttype"] = "none"
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.8))
    cohorts_order = [f"{lo}-{hi}" for lo, hi in H.COHORTS]
    for program in PROGRAMS:
        d = df_pooled[df_pooled.program == program]
        d = d.set_index("cohort").reindex(cohorts_order).reset_index()
        ax.errorbar(d["cohort"], d["mean"], yerr=d["se"], marker="o",
                    color=PROGRAM_COLOR[program], capsize=3, lw=2, label=program)
    ax.set_xlabel("Birth cohort")
    ax.set_ylabel("Mean gender-ideation index  (1 = most traditional)")
    ax.set_title("Gender ideology by cohort — pooled within survey program")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


def plot_cohort_by_wave(df_wave: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["pdf.fonttype"] = 42
    matplotlib.rcParams["ps.fonttype"] = 42
    matplotlib.rcParams["svg.fonttype"] = "none"
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    cohorts_order = [f"{lo}-{hi}" for lo, hi in H.COHORTS]
    x_pos = {c: i for i, c in enumerate(cohorts_order)}
    for program in PROGRAMS:
        sub = df_wave[df_wave.program == program].copy()
        sub = sub.sort_values(["wave", "cohort"])
        for wave, g in sub.groupby("wave"):
            g = g.set_index("cohort").reindex(cohorts_order).reset_index()
            xs = [x_pos[c] + (int(wave) - 2000) * 0.015 for c in g["cohort"]]
            ax.errorbar(xs, g["mean"], yerr=g["se"], marker="o",
                        color=PROGRAM_COLOR[program], capsize=2, lw=0.8,
                        alpha=0.7, label=f"{program} {wave}" if wave == sub["wave"].min() else None)
    ax.set_xticks(list(x_pos.values()))
    ax.set_xticklabels(list(x_pos.keys()))
    ax.set_xlabel("Birth cohort")
    ax.set_ylabel("Mean gender-ideation index  (1 = most traditional)")
    ax.set_title("Gender ideology by cohort × wave — three survey programs")
    ax.grid(axis="y", alpha=0.3)
    # Custom legend: one entry per program
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=PROGRAM_COLOR[p], marker="o", lw=2, label=p)
               for p in PROGRAMS]
    ax.legend(handles=handles, frameon=False)
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    print("(1) cleaning table ...", flush=True)
    cleaning = build_cleaning_table()
    cleaning.to_csv(TABLES / "cleaning_steps.csv", index=False)

    print("(2) item + index descriptives ...", flush=True)
    items, index = build_item_descriptives()
    items.to_csv(TABLES / "ideation_items.csv", index=False)
    index.to_csv(TABLES / "ideation_index.csv", index=False)

    print("(3) assembling pooled panel ...", flush=True)
    pooled, dedup_summary = assemble_pooled_panel()
    pooled = apply_cfps_dedup(pooled)
    pd.DataFrame([dedup_summary]).to_csv(TABLES / "cfps_repeat_summary.csv", index=False)

    print("    cohort × program (pooled across waves) ...", flush=True)
    pooled_cohort = cohort_mean_se(pooled, ["program", "cohort"])
    pooled_cohort.to_csv(TABLES / "cohort_trend_pooled.csv", index=False)

    print("    cohort × program × wave ...", flush=True)
    wave_cohort = cohort_mean_se(pooled, ["program", "wave", "cohort"])
    wave_cohort.to_csv(TABLES / "cohort_trend_by_wave.csv", index=False)

    print("(4) within-cohort gender / urban / corr ...", flush=True)
    gender_gap_by_cohort(pooled).to_csv(TABLES / "within_cohort_gender.csv", index=False)
    urban_gap_by_cohort(pooled).to_csv(TABLES / "within_cohort_urban.csv", index=False)
    correlations_table(pooled).to_csv(TABLES / "correlation_table.csv", index=False)

    print("(5) figures ...", flush=True)
    plot_cohort_pooled(pooled_cohort, FIGS / "cohort_trend_pooled.pdf")
    plot_cohort_by_wave(wave_cohort, FIGS / "cohort_trend_by_wave.pdf")

    # console summary
    print("\nCleaning (first 6 rows):")
    print(cleaning.head(8).to_string(index=False))
    print("\nIndex descriptives:")
    print(index.to_string(index=False))
    print("\nCFPS dedup summary:", dedup_summary)
    print("\nPooled cohort trend:")
    print(pooled_cohort.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
