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
def step_life_events(p: pd.DataFrame) -> pd.DataFrame:
    events = [
        ("had_new_child",       "Had a new child (2014→2020)"),
        ("entered_marriage",    "Entered marriage"),
        ("divorced",            "Got divorced"),
        ("widowed",             "Lost spouse to death"),
        ("lost_job",            "Lost / left job (1→0)"),
        ("entered_work",        "Entered work (0→1)"),
    ]
    rows = []
    for col, label in events:
        sub = p.dropna(subset=["delta_ideation", col])
        a = sub.loc[sub[col] == 0, "delta_ideation"].to_numpy()
        b = sub.loc[sub[col] == 1, "delta_ideation"].to_numpy()
        if len(a) > 1 and len(b) > 1:
            ci_a = DS.bootstrap_mean_ci(a, n_boot=1000, seed=0)
            ci_b = DS.bootstrap_mean_ci(b, n_boot=1000, seed=1)
            w = DS.welch_ci_diff(b, a)
            rows.append({
                "event": col,
                "label": label,
                "n_no":  len(a),
                "n_yes": len(b),
                "mean_no":  float(a.mean()),
                "mean_yes": float(b.mean()),
                "ci_no_lo": ci_a["ci_lo"],   "ci_no_hi": ci_a["ci_hi"],
                "ci_yes_lo": ci_b["ci_lo"],  "ci_yes_hi": ci_b["ci_hi"],
                "diff": w["diff"],
                "diff_se": w["se"],
                "welch_t": w["t"],
                "welch_p": w["p"],
                "cohen_d": DS.cohen_d(a, b),
                "hedges_g": DS.hedges_g(a, b),
            })
    out = pd.DataFrame(rows)
    out.to_csv(TBL / "life_event_means.csv", index=False)
    return out


def step_life_event_forest(le: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    y = np.arange(len(le))[::-1]
    ax.errorbar(le["diff"], y,
                xerr=1.96 * le["diff_se"], fmt="o",
                color="#264478", capsize=3)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.label}  (n_yes={int(r.n_yes):,})" for _, r in le.iterrows()])
    ax.set_xlabel("Δideation contrast: event vs no event (95% CI, Welch)\n"
                  "negative = event associated with progressive shift")
    ax.set_title("Life-event associations with Δideation, CFPS 2014→2020")
    fig.tight_layout()
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
def step_ols(p: pd.DataFrame) -> pd.DataFrame:
    rhs = ["female", "urban_2014", "had_new_child", "lost_job",
           "entered_work", "entered_marriage", "divorced", "widowed",
           "delta_household_n", "delta_edu_yrs", "ideation_2014"]
    age_2014 = 2014 - p["birthy_2014"]
    df = p[["delta_ideation"] + rhs].copy()
    df["age_2014"] = age_2014
    cols = ["female", "urban_2014", "age_2014", "had_new_child", "lost_job",
            "entered_work", "entered_marriage", "divorced", "widowed",
            "delta_household_n", "delta_edu_yrs", "ideation_2014"]
    sub = df.dropna(subset=["delta_ideation"] + cols)
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
    out.to_csv(TBL / "ols_delta_ideation.csv", index=False)
    pd.DataFrame([{"n": len(sub), "df": len(sub) - len(cl["term"])}]
                 ).to_csv(TBL / "ols_meta.csv", index=False)
    return out


def step_ols_coefplot(coefs: pd.DataFrame) -> None:
    # drop intercept and baseline-ideation (its sign is mechanical reversion).
    plot = coefs[~coefs.term.isin(["const"])].copy()
    plot = plot.sort_values("coef")
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
    labels = [pretty.get(t, t) for t in plot.term]
    y = np.arange(len(plot))[::-1]
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    ax.errorbar(plot["coef"], y,
                xerr=1.96 * plot["se_hc1"], fmt="o",
                color="#264478", capsize=3, label="HC1 SE")
    ax.axvline(0, color="black", lw=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("OLS coefficient on Δideation (HC1 95% CI)")
    ax.set_title("Predictors of Δgender-ideation, CFPS 2014→2020")
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
    le = step_life_events(p)
    step_life_event_forest(le)
    step_marital_table(p)
    coefs = step_ols(p)
    step_ols_coefplot(coefs)
    print(f"DONE   N panel = {len(p):,}   N with Δideation = {p['delta_ideation'].notna().sum():,}")


if __name__ == "__main__":
    main()
