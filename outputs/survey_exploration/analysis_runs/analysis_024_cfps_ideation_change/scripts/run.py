#!/usr/bin/env python3
"""analysis_024 — CFPS 2014↔2020 ideation-change panel.

Two exploratory questions:
  (A) WHO changes — by gender, cohort, urban/rural, education, income.
  (B) WHAT predicts change — marital transitions, employment change,
      childbirth, household-size change.

Outputs (paths relative to this analysis_run):
  tables/panel_overview.csv         (N counts, Δ summary)
  tables/who_changes.csv            (group means + bootstrap CIs + Cohen's d)
  tables/marital_transition_means.csv
  tables/life_event_means.csv
  tables/ols_delta_ideation.csv     (classical + HC1 SEs)
  tables/ols_meta.csv               (sample sizes)
  figures/delta_ideation_hist.pdf
  figures/who_changes_forest.pdf
  figures/life_event_forest.pdf
  figures/ols_coefplot.pdf
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# vector PDF (project convention — same as analysis_023)
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = ROOT / "outputs" / "survey_exploration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cfps_panel as CP             # noqa: E402
import descriptive_stats as DS      # noqa: E402
import stats_helpers as SH          # noqa: E402

HERE = Path(__file__).resolve().parents[1]
TBL = HERE / "tables"
FIG = HERE / "figures"
TBL.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# 1. Build panel
# ---------------------------------------------------------------------------
def step_panel() -> pd.DataFrame:
    p = CP.build_panel()

    valid = p.dropna(subset=["delta_ideation"])
    n_valid = max(len(valid), 1)
    overview = pd.DataFrame({
        "metric": [
            "pids_in_both_waves",
            "pids_with_delta_ideation",
            "mean_delta",
            "sd_delta",
            "n_progressive",
            "n_stable",
            "n_traditional",
            "share_progressive",
            "share_stable",
            "share_traditional",
            "share_changed_any_direction",
        ],
        "value": [
            int(len(p)),
            int(p["delta_ideation"].notna().sum()),
            float(p["delta_ideation"].mean()),
            float(p["delta_ideation"].std()),
            int((p["direction"] == "progressive").sum()),
            int((p["direction"] == "stable").sum()),
            int((p["direction"] == "traditional").sum()),
            float((valid["direction"] == "progressive").sum() / n_valid),
            float((valid["direction"] == "stable").sum() / n_valid),
            float((valid["direction"] == "traditional").sum() / n_valid),
            float(((valid["direction"] == "progressive").sum()
                  + (valid["direction"] == "traditional").sum()) / n_valid),
        ],
    })
    overview.to_csv(TBL / "panel_overview.csv", index=False)
    p.to_parquet(TBL / "panel.parquet", index=False)
    return p


# ---------------------------------------------------------------------------
# 2. Distribution figure
# ---------------------------------------------------------------------------
def step_distribution(p: pd.DataFrame) -> None:
    d = p["delta_ideation"].dropna()
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.hist(d, bins=np.linspace(-1, 1, 41), color="#5577aa", edgecolor="white")
    ax.axvline(0, color="black", lw=0.8)
    ax.axvline(d.mean(), color="firebrick", lw=1.2, ls="--",
               label=f"mean = {d.mean():+.3f}")
    ax.set_xlabel("Δ gender-ideation index (2020 − 2014)\n"
                  "more negative = more progressive shift")
    ax.set_ylabel("respondents")
    ax.set_title(f"Distribution of Δideation, CFPS 2014→2020 (N = {len(d):,})")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "delta_ideation_hist.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Who changes — group means + CI + Cohen's d
# ---------------------------------------------------------------------------
def _group_summary(p: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    sub = p.dropna(subset=["delta_ideation", group_col])
    for g, gdf in sub.groupby(group_col):
        d = gdf["delta_ideation"].to_numpy()
        ci = DS.bootstrap_mean_ci(d, n_boot=1000, seed=0)
        rows.append({
            "group_var": group_col,
            "group": g,
            "n": len(d),
            "mean_delta": float(d.mean()),
            "se": float(d.std(ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan"),
            "ci_lo": ci["ci_lo"],
            "ci_hi": ci["ci_hi"],
            "share_progressive": float((gdf["direction"] == "progressive").mean()),
            "share_traditional": float((gdf["direction"] == "traditional").mean()),
            "share_stable": float((gdf["direction"] == "stable").mean()),
        })
    return pd.DataFrame(rows)


def step_who_changes(p: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for col in ["female", "cohort", "urban_2014"]:
        parts.append(_group_summary(p, col))
    out = pd.concat(parts, ignore_index=True)

    # Effect sizes for the binary splits.
    es_rows = []
    for col, label in [("female", "female_vs_male"), ("urban_2014", "urban_vs_rural")]:
        a = p.loc[(p[col] == 0) & p["delta_ideation"].notna(), "delta_ideation"]
        b = p.loc[(p[col] == 1) & p["delta_ideation"].notna(), "delta_ideation"]
        if len(a) > 1 and len(b) > 1:
            cd = DS.cohen_d(a.values, b.values)
            hg = DS.hedges_g(a.values, b.values)
            w = DS.welch_ci_diff(b.values, a.values)
            es_rows.append({
                "comparison": label,
                "n_group0": len(a),
                "n_group1": len(b),
                "mean_group0": float(a.mean()),
                "mean_group1": float(b.mean()),
                "cohen_d": cd,
                "hedges_g": hg,
                "welch_diff": w["diff"],
                "welch_se": w["se"],
                "welch_t": w["t"],
                "welch_df": w["df"],
                "welch_p": w["p"],
                "ci_lo": w["ci_lo"],
                "ci_hi": w["ci_hi"],
            })
    pd.DataFrame(es_rows).to_csv(TBL / "effect_sizes_who.csv", index=False)
    out.to_csv(TBL / "who_changes.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 4. Forest plot of group means
# ---------------------------------------------------------------------------
def step_forest_who(who: pd.DataFrame) -> None:
    # Build a single forest with three blocks (gender / cohort / urban).
    blocks = [
        ("Gender", "female",
         {0.0: "Male", 1.0: "Female"}),
        ("Cohort", "cohort", None),
        ("Hukou", "urban_2014",
         {0.0: "Rural hukou", 1.0: "Urban hukou"}),
    ]
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    y = 0
    yticks, ylabels = [], []
    for title, var, lab_map in blocks:
        ax.text(-0.18, y + 0.5, title, fontsize=10, fontweight="bold",
                transform=ax.get_yaxis_transform(), va="center", ha="right")
        sub = who[who.group_var == var]
        # consistent ordering
        if var == "cohort":
            order = ["1930-1949", "1950-1959", "1960-1969",
                     "1970-1979", "1980-1989", "1990-2005"]
            sub = sub.set_index("group").reindex([g for g in order if g in set(sub.group)]).reset_index()
        for _, r in sub.iterrows():
            ax.errorbar(r["mean_delta"], y, xerr=[[r["mean_delta"] - r["ci_lo"]],
                                                  [r["ci_hi"] - r["mean_delta"]]],
                        fmt="o", color="#264478", capsize=3)
            label = lab_map.get(r["group"], str(r["group"])) if lab_map else str(r["group"])
            yticks.append(y)
            ylabels.append(f"{label}  (n={int(r['n']):,})")
            y -= 1
        y -= 0.5   # spacing between blocks

    ax.axvline(0, color="black", lw=0.6)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()
    ax.set_xlabel("Δ gender-ideation index (95% bootstrap CI)")
    ax.set_title("Who shifted ideology, CFPS 2014→2020")
    fig.tight_layout()
    fig.savefig(FIG / "who_changes_forest.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Life-event means
# ---------------------------------------------------------------------------
EVENTS = [
    ("had_new_child",    "Had a new child (2014→2020)"),
    ("entered_marriage", "Entered marriage"),
    ("divorced",         "Got divorced"),
    ("widowed",          "Lost spouse to death"),
    ("lost_job",         "Lost / left job (1→0)"),
    ("entered_work",     "Entered work (0→1)"),
]

SEX_STRATA = [
    ("all",    None),
    ("male",   0.0),
    ("female", 1.0),
]


def _life_event_one(p: pd.DataFrame, col: str, label: str,
                    denom: str) -> dict | None:
    """One Welch contrast.  `denom` ∈ {"all", "at_risk"}."""
    if denom == "at_risk":
        try:
            mask = CP.at_risk_for_event(p, col)
        except ValueError:
            return None
        pool = p[mask]
    else:
        pool = p
    sub = pool.dropna(subset=["delta_ideation", col])
    a = sub.loc[sub[col] == 0, "delta_ideation"].to_numpy()
    b = sub.loc[sub[col] == 1, "delta_ideation"].to_numpy()
    if len(a) < 2 or len(b) < 2:
        return None
    ci_a = DS.bootstrap_mean_ci(a, n_boot=1000, seed=0)
    ci_b = DS.bootstrap_mean_ci(b, n_boot=1000, seed=1)
    w = DS.welch_ci_diff(b, a)
    return {
        "event": col, "label": label, "denom": denom,
        "n_no": len(a), "n_yes": len(b),
        "mean_no": float(a.mean()), "mean_yes": float(b.mean()),
        "ci_no_lo": ci_a["ci_lo"],  "ci_no_hi": ci_a["ci_hi"],
        "ci_yes_lo": ci_b["ci_lo"], "ci_yes_hi": ci_b["ci_hi"],
        "diff": w["diff"], "diff_se": w["se"],
        "welch_t": w["t"], "welch_p": w["p"],
        "cohen_d": DS.cohen_d(a, b),
        "hedges_g": DS.hedges_g(a, b),
    }


def step_life_events(p: pd.DataFrame) -> dict[tuple[str, str], pd.DataFrame]:
    """One row per (event, denom) × sex stratum.  Save three CSVs and
    return a dict keyed by (stratum, denom) for downstream plotting."""
    out_by_strat: dict[tuple[str, str], pd.DataFrame] = {}
    for stratum_name, sex_val in SEX_STRATA:
        sub = p if sex_val is None else p[p["female"] == sex_val]
        for denom in ("all", "at_risk"):
            rows = []
            for col, label in EVENTS:
                r = _life_event_one(sub, col, label, denom)
                if r is not None:
                    r["sex_stratum"] = stratum_name
                    rows.append(r)
            df = pd.DataFrame(rows)
            out_by_strat[(stratum_name, denom)] = df
        # Save one combined CSV per sex stratum (both denominators stacked)
        combined = pd.concat([out_by_strat[(stratum_name, d)] for d in ("all", "at_risk")],
                             ignore_index=True)
        combined.to_csv(TBL / f"life_event_means_{stratum_name}.csv", index=False)
    return out_by_strat


def step_life_event_forest(by_strat: dict[tuple[str, str], pd.DataFrame]) -> None:
    """Two-panel figure (denominators) × three sex-stratum colours."""
    colours = {"all": "#264478", "male": "#117755", "female": "#aa4422"}
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
    for ax, denom, title in zip(
            axes, ("all", "at_risk"),
            ("Denominator: whole panel",
             "Denominator: at-risk subsample (2014 = '0' state)"),
    ):
        # event ordering: same on both panels
        events = [c for c, _ in EVENTS]
        offsets = {"all": 0.0, "male": -0.25, "female": +0.25}
        for stratum in ("all", "male", "female"):
            sub = by_strat[(stratum, denom)]
            if sub.empty:
                continue
            # align rows to the events list order
            sub = sub.set_index("event").reindex(events).reset_index()
            y = np.arange(len(events))[::-1] + offsets[stratum]
            ax.errorbar(sub["diff"], y, xerr=1.96 * sub["diff_se"],
                        fmt="o", color=colours[stratum], capsize=3,
                        label=f"{stratum} (n_yes range {int(sub['n_yes'].min()):,}–{int(sub['n_yes'].max()):,})")
            # annotate sample size for yes group
            for yi, (_, r) in zip(y, sub.iterrows()):
                if pd.notna(r["diff"]):
                    ax.text(r["diff"], yi, f"  n={int(r['n_yes']):,}",
                            color=colours[stratum], fontsize=7, va="center")
        ax.axvline(0, color="black", lw=0.6)
        labels = [next(l for c, l in EVENTS if c == e) for e in events]
        ax.set_yticks(np.arange(len(events))[::-1])
        ax.set_yticklabels(labels)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Δideation contrast (event − no event), 95% CI")
        ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Life-event associations with Δideation, CFPS 2014→2020 — by sex × denominator",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(FIG / "life_event_forest.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 6. Marital-transition table
# ---------------------------------------------------------------------------
def step_marital_table(p: pd.DataFrame) -> None:
    rows = []
    sub = p.dropna(subset=["delta_ideation", "marital_transition"])
    for tr, gdf in sub.groupby("marital_transition"):
        d = gdf["delta_ideation"].to_numpy()
        ci = DS.bootstrap_mean_ci(d, n_boot=1000, seed=0)
        rows.append({
            "marital_transition": tr,
            "n": len(d),
            "mean_delta": float(d.mean()),
            "ci_lo": ci["ci_lo"],
            "ci_hi": ci["ci_hi"],
            "share_progressive": float((gdf["direction"] == "progressive").mean()),
            "share_traditional": float((gdf["direction"] == "traditional").mean()),
        })
    out = pd.DataFrame(rows).sort_values("mean_delta")
    out.to_csv(TBL / "marital_transition_means.csv", index=False)


# ---------------------------------------------------------------------------
# 7. OLS Δideation ~ events + controls
# ---------------------------------------------------------------------------
def _ols_one(p: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, int]:
    sub = p.dropna(subset=["delta_ideation"] + cols)
    Xdf = sub[cols].astype(float).copy()
    Xdf.insert(0, "const", 1.0)
    y = sub["delta_ideation"].to_numpy()
    cl  = SH.ols(Xdf, y)
    hc1 = SH.ols_robust(Xdf, y, kind="HC1")
    out = pd.DataFrame({
        "term": cl["term"],
        "coef": cl["coef"],
        "se_classical": cl["se"], "t_classical": cl["t"], "p_classical": cl["p"],
        "se_hc1": hc1["se"],      "t_hc1": hc1["t"],      "p_hc1": hc1["p"],
    })
    return out, len(sub)


def step_ols(p: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Run the OLS three times: pooled, men-only, women-only.

    Female is dropped from the within-sex specifications.
    """
    base_cols = ["urban_2014", "age_2014", "had_new_child", "lost_job",
                 "entered_work", "entered_marriage", "divorced", "widowed",
                 "delta_household_n", "delta_edu_yrs", "ideation_2014"]
    cols_pooled = ["female"] + base_cols
    out_meta = []
    coefs_by = {}
    for label, sub, cols in [
        ("all",    p,                cols_pooled),
        ("male",   p[p["female"] == 0], base_cols),
        ("female", p[p["female"] == 1], base_cols),
    ]:
        df, n = _ols_one(sub, cols)
        df["sex_stratum"] = label
        df.to_csv(TBL / f"ols_delta_ideation_{label}.csv", index=False)
        out_meta.append({"sex_stratum": label, "n": n, "k": len(cols) + 1})
        coefs_by[label] = df
    pd.DataFrame(out_meta).to_csv(TBL / "ols_meta.csv", index=False)
    return coefs_by


def step_ols_coefplot(coefs_by: dict[str, pd.DataFrame]) -> None:
    pretty = {
        "female":           "Female",
        "urban_2014":       "Urban hukou (2014)",
        "age_2014":         "Age at 2014",
        "had_new_child":    "Had a new child",
        "lost_job":         "Lost / left job",
        "entered_work":     "Entered work",
        "entered_marriage": "Entered marriage",
        "divorced":         "Got divorced",
        "widowed":          "Widowed",
        "delta_household_n":"Δ household size",
        "delta_edu_yrs":    "Δ education years",
        "ideation_2014":    "Baseline ideation (2014)",
    }
    order = ["urban_2014", "age_2014", "had_new_child", "entered_marriage",
             "divorced", "widowed", "lost_job", "entered_work",
             "delta_household_n", "delta_edu_yrs", "ideation_2014", "female"]
    colours = {"all": "#264478", "male": "#117755", "female": "#aa4422"}
    offsets = {"all": 0.0, "male": -0.25, "female": +0.25}
    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    for stratum, df in coefs_by.items():
        df = df.set_index("term").reindex(order).reset_index().dropna(subset=["coef"])
        y = np.arange(len(df))[::-1] + offsets[stratum]
        ax.errorbar(df["coef"], y, xerr=1.96 * df["se_hc1"],
                    fmt="o", color=colours[stratum], capsize=3,
                    label=stratum)
    ax.axvline(0, color="black", lw=0.6)
    labels = [pretty.get(t, t) for t in order]
    ax.set_yticks(np.arange(len(order))[::-1])
    ax.set_yticklabels(labels)
    ax.set_xlabel("OLS coefficient on Δideation (HC1 95% CI)")
    ax.set_title("Predictors of Δgender-ideation, by sex stratum")
    ax.legend(frameon=False, loc="lower right", title="sample")
    fig.tight_layout()
    fig.savefig(FIG / "ols_coefplot.pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    p = step_panel()
    step_distribution(p)
    who = step_who_changes(p)
    step_forest_who(who)
    by_strat = step_life_events(p)
    step_life_event_forest(by_strat)
    step_marital_table(p)
    coefs_by = step_ols(p)
    step_ols_coefplot(coefs_by)
    print(f"DONE   N panel = {len(p):,}   N with Δideation = {p['delta_ideation'].notna().sum():,}")


if __name__ == "__main__":
    main()
