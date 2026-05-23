#!/usr/bin/env python3
"""analysis_023 — statistical-upgrade pass.

Adds on top of run.py:
  - tables/cohort_trend_bootstrap.csv   : cohort means with bootstrap 95% CI
  - tables/effect_sizes_gender.csv      : Welch t / p / Cohen's d / Hedges' g /
                                          95% CI per (program, cohort)
  - tables/effect_sizes_urban.csv       : same for urban vs rural
  - tables/correlation_table_v2.csv     : pooled Pearson r with 95% CI and p
  - tables/ols_models.csv               : OLS with cohort+wave FE per program,
                                          classical + HC1 robust SEs

  - figures/cohort_trend_bootstrap.pdf  : bootstrap 95% CI ribbons + means
                                          + LOESS smooth of ideation on birthy
  - figures/gender_gap_forest.pdf       : Cohen's d with 95% CI per (program,
                                          cohort), forest layout
  - figures/urban_gap_forest.pdf        : same for urban-rural
  - figures/correlation_heatmap.pdf     : (program × wave) by variable
  - figures/ols_coefplot.pdf            : OLS coefficients with 95% CI

All figures are vector PDF (pdf.fonttype=42).
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sp_stats

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
TABLES = RUN / "tables"
FIGS = RUN / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L                # noqa: E402
import rq51_helpers as H                # noqa: E402
import descriptive_stats as DS          # noqa: E402
import stats_helpers as ST              # noqa: E402

PROGRAMS = ["CFPS", "CGSS", "ACWF"]
PROGRAM_COLOR = {"CFPS": "#1f77b4", "CGSS": "#d62728", "ACWF": "#2ca02c"}
COHORTS_ORDER = [f"{lo}-{hi}" for lo, hi in H.COHORTS]


# --------------------------------------------------------------------------- #
# Build pooled panel (with CFPS dedup, identical to run.py).
# --------------------------------------------------------------------------- #

def _attach_context(dataset, year):
    df, _m, _n, idx = L.load_recoded(dataset, year)
    df = df.reset_index(drop=True)
    df["ideation"] = df[idx]
    df["birthy"] = H.birth_year(dataset, year).reset_index(drop=True)
    df["urban"] = H.urban_indicator(dataset, year).reset_index(drop=True)
    df["edu_yrs"] = H.education_years(dataset, year).reset_index(drop=True)
    df["employed"] = H.employed_indicator(dataset, year).reset_index(drop=True)
    df["isei_current"] = H.occupation_isei(dataset, year).reset_index(drop=True)
    if dataset == "CFPS" and year == "2014":
        df["isei_aspiration"] = H.cfps2014_aspiration_isei().reset_index(drop=True)
        df["edu_aspiration"] = H.cfps2014_aspiration_edu_years().reset_index(drop=True)
    else:
        df["isei_aspiration"] = np.nan
        df["edu_aspiration"] = np.nan
    df["income"] = H.personal_income(dataset, year).reset_index(drop=True)
    df["log_income"] = np.log1p(df["income"])
    df["program"] = dataset
    df["wave"] = year
    df["cohort"] = df["birthy"].apply(H.cohort_label)
    return df


def pooled_panel() -> pd.DataFrame:
    frames = []
    for (dataset, year) in L.SURVEYS:
        d = _attach_context(dataset, year)
        if dataset == "CFPS":
            import pyreadstat
            pid_df, _ = pyreadstat.read_dta(
                str(L.ROOT / L.SURVEYS[(dataset, year)]["file"]), usecols=["pid"])
            d["pid"] = pid_df["pid"].reset_index(drop=True)
        keep = ["program", "wave", "cohort", "birthy", "female", "urban",
                "edu_yrs", "employed", "isei_current", "isei_aspiration",
                "edu_aspiration", "income", "log_income", "ideation"]
        if "pid" in d.columns:
            keep.append("pid")
        frames.append(d[[c for c in keep if c in d.columns]])
    pooled = pd.concat(frames, ignore_index=True, sort=False)
    # CFPS dedup keeping latest wave
    is_cfps = pooled["program"] == "CFPS"
    cfps = pooled.loc[is_cfps & pooled["pid"].notna()].copy()
    other = pooled.loc[~is_cfps].copy()
    cfps_dedup, _ = H.cfps_dedup_keep_latest(
        cfps, "pid", "wave", "ideation", change_eps=0.01)
    return pd.concat([cfps_dedup, other], ignore_index=True, sort=False)


# --------------------------------------------------------------------------- #
# (1) Bootstrap-CI cohort trend + LOESS smooth.
# --------------------------------------------------------------------------- #

def bootstrap_cohort_table(pooled: pd.DataFrame, n_boot: int = 1000,
                           seed: int = 0) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)
    for (program, cohort), g in pooled.dropna(subset=["cohort", "ideation"]).groupby(
            ["program", "cohort"], observed=True):
        x = g["ideation"].to_numpy()
        # use a per-group seed so the script is fully reproducible regardless of
        # iteration order
        seed_g = int(rng.integers(0, 2**31 - 1))
        r = DS.bootstrap_mean_ci(x, n_boot=n_boot, seed=seed_g, alpha=0.05)
        rows.append(dict(program=program, cohort=cohort,
                         n=r["n"], mean=r["mean"],
                         ci_lo=r["ci_lo"], ci_hi=r["ci_hi"]))
    return pd.DataFrame(rows).sort_values(["program", "cohort"])


def plot_cohort_bootstrap(boot: pd.DataFrame, pooled: pd.DataFrame, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                                "svg.fonttype": "none"})
    import matplotlib.pyplot as plt
    from statsmodels.nonparametric.smoothers_lowess import lowess

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    x_pos = {c: i for i, c in enumerate(COHORTS_ORDER)}
    for program in PROGRAMS:
        d = boot[boot.program == program].set_index("cohort").reindex(
            COHORTS_ORDER).reset_index()
        xs = np.array([x_pos[c] for c in d["cohort"]])
        color = PROGRAM_COLOR[program]
        ax.fill_between(xs, d["ci_lo"], d["ci_hi"], color=color, alpha=0.18)
        ax.plot(xs, d["mean"], marker="o", lw=2.2, color=color, label=f"{program}")

    # LOESS smooths of ideation on continuous birth year
    for program in PROGRAMS:
        sub = pooled[(pooled.program == program) &
                     pooled["birthy"].notna() &
                     pooled["ideation"].notna()].copy()
        if len(sub) < 200:
            continue
        smoothed = lowess(sub["ideation"].to_numpy(),
                          sub["birthy"].to_numpy(),
                          frac=0.3, return_sorted=True)
        # map birth year to the cohort axis (linearly between 1930 and 2005)
        x_map = (smoothed[:, 0] - 1930) / (2005 - 1930) * (len(COHORTS_ORDER) - 1)
        ax.plot(x_map, smoothed[:, 1], "--", color=PROGRAM_COLOR[program],
                alpha=0.55, lw=1.4)

    ax.set_xticks(list(x_pos.values()))
    ax.set_xticklabels(list(x_pos.keys()), rotation=15)
    ax.set_xlabel("Birth cohort")
    ax.set_ylabel("Mean gender-ideation index (1 = most traditional)")
    ax.set_title("Cohort trend — points + bootstrap 95% CI ribbons + LOESS smooth (dashed)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# (2) Effect sizes — gender and urban — per (program, cohort).
# --------------------------------------------------------------------------- #

def _effect_table(pooled: pd.DataFrame, contrast: str) -> pd.DataFrame:
    """contrast in {'gender','urban'}. Returns Welch + Cohen's d + Hedges' g + CI."""
    rows = []
    if contrast == "gender":
        grp_a_col, grp_b_col, grp_a_val, grp_b_val = "female", "female", 1.0, 0.0
        contrast_lbl = "F - M"
    else:
        grp_a_col, grp_b_col, grp_a_val, grp_b_val = "urban", "urban", 1.0, 0.0
        contrast_lbl = "U - R"

    for (program, cohort), g in pooled.dropna(subset=["cohort", grp_a_col,
                                                      "ideation"]).groupby(
            ["program", "cohort"], observed=True):
        a = g.loc[g[grp_a_col] == grp_a_val, "ideation"].to_numpy()
        b = g.loc[g[grp_b_col] == grp_b_val, "ideation"].to_numpy()
        if len(a) < 2 or len(b) < 2:
            continue
        w = DS.welch_ci_diff(a, b, alpha=0.05)
        d = DS.cohen_d(a, b)
        gh = DS.hedges_g(a, b)
        rows.append(dict(program=program, cohort=cohort,
                         contrast=contrast_lbl,
                         n_a=int(len(a)), n_b=int(len(b)),
                         mean_a=float(np.mean(a)),
                         mean_b=float(np.mean(b)),
                         diff=w["diff"], welch_t=w["t"], welch_df=w["df"],
                         p=w["p"], ci95_lo=w["ci_lo"], ci95_hi=w["ci_hi"],
                         cohens_d=d, hedges_g=gh))
    return pd.DataFrame(rows)


def plot_forest(eff: pd.DataFrame, title: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                                "svg.fonttype": "none"})
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.4, 6.5))
    y_lbls, y_vals = [], []
    yi = 0
    for program in PROGRAMS:
        for cohort in COHORTS_ORDER:
            r = eff[(eff.program == program) & (eff.cohort == cohort)]
            if r.empty:
                continue
            r = r.iloc[0]
            color = PROGRAM_COLOR[program]
            # 95% CI of Cohen's d via Welch's CI on the difference (rescaled by pooled SD)
            # We re-derive pooled SD from the diff / Cohen's d link:
            #   d = diff / pooled_sd  =>  pooled_sd = diff / d
            if r["cohens_d"] and np.isfinite(r["cohens_d"]) and r["cohens_d"] != 0:
                pooled_sd = r["diff"] / r["cohens_d"]
                d_lo = r["ci95_lo"] / pooled_sd
                d_hi = r["ci95_hi"] / pooled_sd
            else:
                d_lo = d_hi = np.nan
            ax.errorbar(r["cohens_d"], yi, xerr=[[r["cohens_d"] - d_lo],
                                                 [d_hi - r["cohens_d"]]],
                        fmt="o", color=color, capsize=3, lw=1.5)
            star = ""
            if r["p"] < 0.001:
                star = " ***"
            elif r["p"] < 0.01:
                star = " **"
            elif r["p"] < 0.05:
                star = " *"
            y_lbls.append(f"{program}  {cohort}{star}")
            y_vals.append(yi)
            yi += 1
        yi += 0.7   # gap between programs

    ax.axvline(0, color="grey", lw=1, ls="--")
    ax.set_yticks(y_vals)
    ax.set_yticklabels(y_lbls, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Cohen's d   (95 % CI; * p<.05, ** p<.01, *** p<.001)")
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# (3) Pooled Pearson correlations with CI; heatmap.
# --------------------------------------------------------------------------- #

def _r_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Fisher's z 95% CI for Pearson r."""
    if not np.isfinite(r) or n < 4:
        return float("nan"), float("nan")
    z = 0.5 * np.log((1 + r) / (1 - r))
    se = 1.0 / np.sqrt(n - 3)
    zcrit = sp_stats.norm.ppf(1 - alpha / 2)
    lo = np.tanh(z - zcrit * se)
    hi = np.tanh(z + zcrit * se)
    return float(lo), float(hi)


def correlation_table_v2(pooled: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for program in PROGRAMS:
        for var in ["edu_yrs", "log_income", "employed", "female", "urban"]:
            for wave in sorted(pooled.loc[pooled.program == program, "wave"].unique()):
                sub = pooled[(pooled.program == program) & (pooled.wave == wave)]
                x = pd.to_numeric(sub[var], errors="coerce")
                y = pd.to_numeric(sub["ideation"], errors="coerce")
                both = pd.concat([x, y], axis=1).dropna()
                if len(both) < 30 or both.iloc[:, 0].nunique() < 2 \
                        or both.iloc[:, 1].nunique() < 2:
                    rows.append(dict(program=program, wave=wave, variable=var,
                                     n=len(both), pearson_r=np.nan,
                                     ci_lo=np.nan, ci_hi=np.nan, p=np.nan))
                    continue
                r, p = sp_stats.pearsonr(both.iloc[:, 0], both.iloc[:, 1])
                lo, hi = _r_ci(r, len(both))
                rows.append(dict(program=program, wave=wave, variable=var,
                                 n=int(len(both)),
                                 pearson_r=float(r), ci_lo=lo, ci_hi=hi,
                                 p=float(p)))
    return pd.DataFrame(rows)


def plot_correlation_heatmap(corr: pd.DataFrame, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                                "svg.fonttype": "none"})
    import matplotlib.pyplot as plt

    pivot = corr.pivot_table(index=["program", "wave"], columns="variable",
                             values="pearson_r")
    # consistent variable order
    var_order = ["edu_yrs", "log_income", "employed", "female", "urban"]
    pivot = pivot[[c for c in var_order if c in pivot.columns]]
    pivot = pivot.sort_index()

    fig, ax = plt.subplots(figsize=(6.5, 7.2))
    im = ax.imshow(pivot.values, cmap="RdBu_r", vmin=-0.5, vmax=0.5,
                   aspect="auto")
    ax.set_xticks(range(pivot.shape[1]))
    ax.set_xticklabels(pivot.columns, rotation=20, ha="right")
    ax.set_yticks(range(pivot.shape[0]))
    ax.set_yticklabels([f"{p} {w}" for p, w in pivot.index], fontsize=9)
    # annotate cells
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:+.2f}", ha="center", va="center",
                        fontsize=8, color="white" if abs(v) > 0.25 else "black")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02,
                 label="Pearson r with ideation")
    ax.set_title("Correlations of covariates with ideation index, by survey × wave")
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# (4) OLS with cohort + wave FE per program; classical + HC1 robust SEs.
# --------------------------------------------------------------------------- #

def build_ols_per_program(pooled: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """One regression per program, returning a coefficient table + meta list.

    Model:  ideation ~ female + urban + edu_yrs + log_income + employed
                       + cohort dummies + wave dummies
    Reference cohort = 1930-1949, reference wave = first wave per program.
    """
    out_rows = []
    meta_rows = []
    cohort_dummies = COHORTS_ORDER[1:]    # drop the first one as reference
    for program in PROGRAMS:
        sub = pooled[pooled.program == program].copy()
        sub = sub.dropna(subset=["ideation", "female", "urban", "edu_yrs",
                                 "log_income", "employed", "cohort", "wave"])
        if len(sub) < 100:
            continue
        # build design
        X = pd.DataFrame({
            "const": 1.0,
            "female": sub["female"].astype(float),
            "urban": sub["urban"].astype(float),
            "edu_yrs": sub["edu_yrs"].astype(float),
            "log_income": sub["log_income"].astype(float),
            "employed": sub["employed"].astype(float),
        }, index=sub.index)
        for c in cohort_dummies:
            X[f"cohort_{c}"] = (sub["cohort"] == c).astype(float)
        waves_sorted = sorted(sub["wave"].unique())
        for w in waves_sorted[1:]:
            X[f"wave_{w}"] = (sub["wave"] == w).astype(float)
        y = sub["ideation"].to_numpy()
        cl = ST.ols(X, y)
        rb = ST.ols_robust(X, y, kind="HC1")
        for t, c, se, t_, p, se_r, t_r, p_r in zip(
                cl["term"], cl["coef"], cl["se"], cl["t"], cl["p"],
                rb["se"], rb["t"], rb["p"]):
            out_rows.append(dict(
                program=program, term=t, coef=float(c),
                se_classical=float(se), t_classical=float(t_), p_classical=float(p),
                se_hc1=float(se_r), t_hc1=float(t_r), p_hc1=float(p_r)))
        meta_rows.append(dict(program=program, n=cl["n"], df=cl["df"]))
    return pd.DataFrame(out_rows), meta_rows


def plot_ols_coefs(coefs: pd.DataFrame, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42,
                                "svg.fonttype": "none"})
    import matplotlib.pyplot as plt

    # which terms to show (drop const, wave dummies)
    keep_terms = ["female", "urban", "edu_yrs", "log_income", "employed",
                  "cohort_1950-1959", "cohort_1960-1969", "cohort_1970-1979",
                  "cohort_1980-1989", "cohort_1990-2005"]
    sub = coefs[coefs.term.isin(keep_terms)].copy()
    # 95% CI from robust SE: coef ± 1.96 * se_hc1
    sub["ci_lo"] = sub["coef"] - 1.96 * sub["se_hc1"]
    sub["ci_hi"] = sub["coef"] + 1.96 * sub["se_hc1"]

    fig, ax = plt.subplots(figsize=(8.0, 7.5))
    y_lbls, y_vals = [], []
    yi = 0
    for term in keep_terms:
        for program in PROGRAMS:
            r = sub[(sub.term == term) & (sub.program == program)]
            if r.empty:
                continue
            r = r.iloc[0]
            ax.errorbar(r["coef"], yi, xerr=[[r["coef"] - r["ci_lo"]],
                                              [r["ci_hi"] - r["coef"]]],
                        fmt="o", color=PROGRAM_COLOR[program], capsize=3, lw=1.5)
            star = "***" if r["p_hc1"] < 0.001 else ("**" if r["p_hc1"] < 0.01 else
                   ("*" if r["p_hc1"] < 0.05 else ""))
            y_lbls.append(f"{term}  ({program}) {star}")
            y_vals.append(yi)
            yi += 1
        yi += 0.6
    ax.axvline(0, color="grey", lw=1, ls="--")
    ax.set_yticks(y_vals)
    ax.set_yticklabels(y_lbls, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("OLS coefficient on ideation index  (95 % CI, HC1 robust SE)")
    ax.set_title("Per-program OLS: ideation ~ covariates + cohort & wave FE")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, format="pdf")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main() -> int:
    print("assembling pooled panel ...", flush=True)
    pooled = pooled_panel()
    print(f"  N rows = {len(pooled)}")

    print("(1) bootstrap-CI cohort table + plot ...", flush=True)
    boot = bootstrap_cohort_table(pooled, n_boot=1000, seed=2026)
    boot.to_csv(TABLES / "cohort_trend_bootstrap.csv", index=False,
                float_format="%.5f")
    plot_cohort_bootstrap(boot, pooled, FIGS / "cohort_trend_bootstrap.pdf")

    print("(2) effect sizes (gender) ...", flush=True)
    gender_eff = _effect_table(pooled, "gender")
    gender_eff.to_csv(TABLES / "effect_sizes_gender.csv", index=False,
                      float_format="%.5f")
    plot_forest(gender_eff,
                title="Gender gap by cohort  —  Cohen's d (F − M) on ideation",
                path=FIGS / "gender_gap_forest.pdf")

    print("(2) effect sizes (urban-rural) ...", flush=True)
    urban_eff = _effect_table(pooled, "urban")
    urban_eff.to_csv(TABLES / "effect_sizes_urban.csv", index=False,
                     float_format="%.5f")
    plot_forest(urban_eff,
                title="Urban-rural gap by cohort  —  Cohen's d (U − R) on ideation",
                path=FIGS / "urban_gap_forest.pdf")

    print("(3) correlations + heatmap ...", flush=True)
    corr = correlation_table_v2(pooled)
    corr.to_csv(TABLES / "correlation_table_v2.csv", index=False,
                float_format="%.5f")
    plot_correlation_heatmap(corr, FIGS / "correlation_heatmap.pdf")

    print("(4) OLS per program + coefplot ...", flush=True)
    ols_coefs, ols_meta = build_ols_per_program(pooled)
    ols_coefs.to_csv(TABLES / "ols_models.csv", index=False, float_format="%.5f")
    pd.DataFrame(ols_meta).to_csv(TABLES / "ols_meta.csv", index=False)
    plot_ols_coefs(ols_coefs, FIGS / "ols_coefplot.pdf")

    # --- (4b) CFPS 2020 adult OLS with current-job ISEI ---
    print("(4b) CFPS 2020 OLS with current-job ISEI ...", flush=True)
    cf20 = pooled[(pooled.program == "CFPS") & (pooled.wave == "2020")].dropna(
        subset=["ideation", "female", "urban", "edu_yrs", "log_income",
                "employed", "isei_current", "cohort"])
    if len(cf20) > 100:
        cohort_dummies = COHORTS_ORDER[1:]
        X = pd.DataFrame({"const": 1.0,
                          "female": cf20["female"].astype(float),
                          "urban": cf20["urban"].astype(float),
                          "edu_yrs": cf20["edu_yrs"].astype(float),
                          "log_income": cf20["log_income"].astype(float),
                          "employed": cf20["employed"].astype(float),
                          "isei_current": cf20["isei_current"].astype(float)},
                         index=cf20.index)
        for c in cohort_dummies:
            X[f"cohort_{c}"] = (cf20["cohort"] == c).astype(float)
        cl = ST.ols(X, cf20["ideation"].to_numpy())
        rb = ST.ols_robust(X, cf20["ideation"].to_numpy(), kind="HC1")
        rows = [dict(term=t, coef=c, se_classical=se_c, t_classical=t_c,
                     p_classical=p_c, se_hc1=se_r, t_hc1=t_r, p_hc1=p_r)
                for t, c, se_c, t_c, p_c, se_r, t_r, p_r in zip(
                cl["term"], cl["coef"], cl["se"], cl["t"], cl["p"],
                rb["se"], rb["t"], rb["p"])]
        pd.DataFrame(rows).to_csv(TABLES / "ols_cfps2020_with_isei.csv",
                                  index=False, float_format="%.5f")
        print(f"    CFPS 2020 + current ISEI N = {cl['n']}, df = {cl['df']}")

    # --- (4c) CFPS 2014 YOUTH (kr1==4) — aspirational ISEI + edu aspiration ---
    print("(4c) CFPS 2014 youth aspiration OLS ...", flush=True)
    cf14y = pooled[(pooled.program == "CFPS") & (pooled.wave == "2014") &
                   pooled["isei_aspiration"].notna()].dropna(
        subset=["ideation", "female", "urban", "isei_aspiration",
                "edu_aspiration"])
    if len(cf14y) > 50:
        X = pd.DataFrame({
            "const": 1.0,
            "female": cf14y["female"].astype(float),
            "urban": cf14y["urban"].astype(float),
            "isei_aspiration": cf14y["isei_aspiration"].astype(float),
            "edu_aspiration": cf14y["edu_aspiration"].astype(float),
        }, index=cf14y.index)
        cl = ST.ols(X, cf14y["ideation"].to_numpy())
        rb = ST.ols_robust(X, cf14y["ideation"].to_numpy(), kind="HC1")
        rows = [dict(term=t, coef=c, se_classical=se_c, t_classical=t_c,
                     p_classical=p_c, se_hc1=se_r, t_hc1=t_r, p_hc1=p_r)
                for t, c, se_c, t_c, p_c, se_r, t_r, p_r in zip(
                cl["term"], cl["coef"], cl["se"], cl["t"], cl["p"],
                rb["se"], rb["t"], rb["p"])]
        pd.DataFrame(rows).to_csv(TABLES / "ols_cfps2014_youth_aspiration.csv",
                                  index=False, float_format="%.5f")
        print(f"    CFPS 2014 youth (kr1==4) aspiration N = {cl['n']}, df = {cl['df']}")
        print(pd.DataFrame(rows).to_string(index=False))

    print("\n--- gender effect sizes (head) ---")
    print(gender_eff.head(8).to_string(index=False))
    print("\n--- OLS coefs ---")
    print(ols_coefs[ols_coefs.term.isin(
        ["female", "urban", "edu_yrs", "log_income", "employed"])
    ].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
