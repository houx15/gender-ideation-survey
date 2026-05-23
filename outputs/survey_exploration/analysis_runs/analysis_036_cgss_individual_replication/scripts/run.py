#!/usr/bin/env python3
"""
analysis_036 — CGSS replication of individual-level ideation→outcome links from
analysis_026/027/028.

CGSS is a repeated cross-section without household structure, so we can't
replicate the couple (029), parent-child (033/034/035), or panel-PSM-DiD
(025/030/031/032) findings.  We CAN replicate the individual-level ideation
→ outcome correlations, which is the spine of 026/027/028.

Design:
  - Pool 8 CGSS waves (2010, 2012, 2013, 2015, 2017, 2018, 2021, 2023).
  - Outcomes (with their wave coverage in parens):
      family-individual side (026 analogue):
        * ever_married           (all 8)
        * age_at_first_marriage  (all 8)
        * num_children           (7/8; missing 2021)
        * ideal_children         (6/8; missing 2012, 2013)
        * marriage_sat           (3/8; 2015, 2017, 2021 only)
      work side (027 analogue):
        * log_personal_income    (all 8)
        * employed               (all 8)
        * weekly_hours           (all 8, gated by employment)
        * mgmt_activity          (all 8, gated by employment)
        * soe_indicator          (all 8, gated by employment; 编制 proxy)
      education side (028 analogue):
        * edu_yrs                (all 8)

  - Per outcome we fit OLS-HC1 with:
        outcome ~ ideation + female + ideation*female + birth_year_c
                  + urban + (log_income if not outcome) + (edu_yrs if not outcome)
                  + wave dummies (8 waves -> 7 dummies)
    plus sex-stratified replicates dropping female / ideation*female from RHS.

  - Outputs: 04_result_table.csv (every row × coef), forest figure of ideation
    coefficient across outcomes × strata, 02_missing_table with wave coverage.

Uses shared scripts: ideation_lib, cgss_outcomes, rq51_helpers, stats_helpers.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42  # vector pdf with embedded fonts

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L           # noqa: E402
import cgss_outcomes as G          # noqa: E402
import rq51_helpers as H           # noqa: E402
import stats_helpers as ST         # noqa: E402

RUN = HERE.parents[1]
FIGS = RUN / "figures"
TABLES = RUN / "tables"

WAVES = ["2010", "2012", "2013", "2015", "2017", "2018", "2021", "2023"]

# Wave-by-wave column names (some waves capitalize, 2021 differs)
COLMAP = {
    "2010": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal="a371", mar_sat=None),
    "2012": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal=None, mar_sat=None),
    "2013": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal=None, mar_sat=None),
    "2015": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal="a371", mar_sat="d31"),
    "2017": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal="a371", mar_sat="d31"),
    "2018": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal="a371", mar_sat=None),
    "2021": dict(income="A8a", marry_yr="A70", sons=None, daughters=None,
                 hours="A53a", emp="A58", mgmt="A59f", ownership="A59k",
                 marital="A69", ideal="A37_1", mar_sat="D31"),
    "2023": dict(income="a8a", marry_yr="a70", sons="a681", daughters="a682",
                 hours="a53a", emp="a58", mgmt="a59f", ownership="a59k",
                 marital="a69", ideal="a371", mar_sat=None),
}

OUTCOMES_CONT = ["age_first_marriage", "num_children", "ideal_children",
                 "log_income", "weekly_hours", "edu_yrs"]
OUTCOMES_BIN  = ["ever_married", "employed", "mgmt_activity", "soe_indicator"]
OUTCOMES_ORD  = ["marriage_sat"]            # 1..5 Likert (treated as continuous)
OUTCOMES      = OUTCOMES_CONT + OUTCOMES_BIN + OUTCOMES_ORD

EMP_GATED = {"weekly_hours", "mgmt_activity", "soe_indicator"}
MAR_GATED = {"age_first_marriage", "marriage_sat"}


def load_wave(year: str) -> pd.DataFrame:
    cm = COLMAP[year]
    extras = [v for v in cm.values() if v]
    df, _meta, _norms, _idx = L.load_recoded("CGSS", year, extra_cols=extras)
    df = df[df["n_valid_items"] >= 1].copy().reset_index(drop=True)

    # ideation index, gender, birth year, education years, urban (hukou),
    # personal income, employed.  These come from the shared helpers and
    # rq51_helpers; we re-derive ourselves here per-row because rq51 helpers
    # operate on full-file index — re-index by position.
    df["ideation"] = df["ideation_index"]
    df["birthy"] = H.birth_year("CGSS", year).reindex(df.index).astype(float)
    df["edu_yrs"] = H.education_years("CGSS", year).reindex(df.index).astype(float)
    df["urban"]   = H.urban_indicator("CGSS", year).reindex(df.index).astype(float)
    df["log_income_full"] = H.personal_income("CGSS", year).reindex(df.index).astype(float)
    # rq51_helpers.personal_income already returns log income (verify):
    # actually rq51_helpers.personal_income returns RAW income; we log it here.
    df["log_income"] = np.log1p(df["log_income_full"])
    df["employed"]   = H.employed_indicator("CGSS", year).reindex(df.index).astype(float)

    # ever / age at first marriage
    df["ever_married"] = G.ever_married_cgss(df[cm["marital"]])
    df["age_first_marriage"] = G.age_first_marriage_cgss(df[cm["marry_yr"]], df["birthy"])

    # children counts
    if cm["sons"] and cm["daughters"]:
        df["num_children"] = G.num_children_cgss(df[cm["sons"]], df[cm["daughters"]])
    else:
        df["num_children"] = np.nan
    if cm["ideal"]:
        df["ideal_children"] = G.ideal_children_cgss(df[cm["ideal"]])
    else:
        df["ideal_children"] = np.nan

    # marriage satisfaction
    if cm["mar_sat"]:
        df["marriage_sat"] = G.marriage_sat_cgss(df[cm["mar_sat"]])
    else:
        df["marriage_sat"] = np.nan

    # work hours, mgmt, SOE
    df["weekly_hours"]   = G.weekly_hours_cgss(df[cm["hours"]])
    df["mgmt_activity"]  = G.mgmt_activity_cgss(df[cm["mgmt"]])
    df["soe_indicator"]  = G.soe_indicator_cgss(df[cm["ownership"]])

    df["wave"] = year
    df["birth_yr_c"] = (df["birthy"] - 1970) / 10

    keep = ["wave", "ideation", "female", "birthy", "birth_yr_c", "urban",
            "edu_yrs", "log_income", "employed"]
    # `edu_yrs`, `log_income`, `employed` double as outcomes — dedupe by keeping
    # only the first occurrence.
    keep = list(dict.fromkeys(keep + OUTCOMES))
    return df[keep].copy()


def descriptive_table(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for w in WAVES:
        sub = d[d.wave == w]
        for out in OUTCOMES:
            s = sub[out].dropna()
            if len(s):
                rows.append(dict(wave=w, outcome=out, n=len(s),
                                 mean=round(float(s.mean()), 4),
                                 sd=round(float(s.std()), 4)))
            else:
                rows.append(dict(wave=w, outcome=out, n=0, mean=np.nan, sd=np.nan))
    return pd.DataFrame(rows)


def missing_table(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for w in WAVES:
        sub = d[d.wave == w]
        for out in OUTCOMES:
            n_total = len(sub)
            n_have = sub[out].notna().sum()
            rows.append(dict(wave=w, outcome=out,
                             n_total=n_total, n_have=int(n_have),
                             pct_missing=round(100*(1 - n_have/n_total), 1) if n_total else np.nan))
    return pd.DataFrame(rows)


def _waves_with_outcome(d: pd.DataFrame, outcome: str) -> list[str]:
    return [w for w in WAVES if d.loc[d.wave == w, outcome].notna().any()]


def _wave_dummies(d: pd.DataFrame, present_waves: list[str]) -> pd.DataFrame:
    """Drop the first present wave; return dummies for the rest."""
    cols = {}
    for w in present_waves[1:]:
        cols[f"wave_{w}"] = (d["wave"] == w).astype(float)
    return pd.DataFrame(cols, index=d.index)


def _build_design(d: pd.DataFrame, outcome: str, stratum: str,
                  present_waves: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Build (X, y) for one outcome × stratum fit."""
    keep = ["ideation", "female", "birth_yr_c", "urban", "edu_yrs", "log_income"]
    if outcome in EMP_GATED:
        sub = d[(d["employed"] == 1)].copy()
    elif outcome in MAR_GATED:
        sub = d[d["ever_married"] == 1].copy()
    else:
        sub = d.copy()
    sub = sub[sub["wave"].isin(present_waves)].copy()
    if stratum == "male":
        sub = sub[sub["female"] == 0].copy()
    elif stratum == "female":
        sub = sub[sub["female"] == 1].copy()

    y = sub[outcome].astype(float)

    X = pd.DataFrame({"const": 1.0,
                      "ideation": sub["ideation"].astype(float)},
                     index=sub.index)
    if stratum == "all":
        X["female"] = sub["female"].astype(float)
        X["ideation_x_female"] = sub["ideation"].astype(float) * sub["female"].astype(float)
    X["birth_yr_c"] = sub["birth_yr_c"].astype(float)
    X["urban"] = sub["urban"].astype(float)
    # avoid putting the outcome on the RHS
    if outcome != "edu_yrs":
        X["edu_yrs"] = sub["edu_yrs"].astype(float)
    if outcome != "log_income":
        X["log_income"] = sub["log_income"].astype(float)
    # wave fixed effects
    X = pd.concat([X, _wave_dummies(sub, present_waves)], axis=1)

    # zero-variance defensive drop (e.g. all-female stratum has female=1 → drop)
    drop_cols = [c for c in X.columns if c != "const" and X[c].nunique(dropna=True) <= 1]
    X = X.drop(columns=drop_cols)
    return X, y


def fit_one(d: pd.DataFrame, outcome: str, stratum: str,
            present_waves: list[str]) -> list[dict]:
    X, y = _build_design(d, outcome, stratum, present_waves)
    if len(y.dropna()) < 50:
        return [dict(outcome=outcome, stratum=stratum, n=int(y.notna().sum()),
                     term="(insufficient data)", coef=np.nan, se=np.nan,
                     t=np.nan, p=np.nan)]
    try:
        r = ST.ols_robust(X, y.to_numpy(), kind="HC1")
    except Exception as e:
        return [dict(outcome=outcome, stratum=stratum, n=int(y.notna().sum()),
                     term=f"(error: {type(e).__name__})", coef=np.nan,
                     se=np.nan, t=np.nan, p=np.nan)]
    rows = []
    for t, c, se, tv, p in zip(r["term"], r["coef"], r["se"], r["t"], r["p"]):
        if t.startswith("wave_") or t == "const":
            continue
        rows.append(dict(outcome=outcome, stratum=stratum, n=r["n"], term=t,
                         coef=round(float(c), 4), se=round(float(se), 4),
                         t=round(float(tv), 2), p=round(float(p), 5)))
    return rows


def run_models(d: pd.DataFrame) -> pd.DataFrame:
    out_rows = []
    for outcome in OUTCOMES:
        present = _waves_with_outcome(d, outcome)
        if not present:
            continue
        for stratum in ("all", "male", "female"):
            out_rows.extend(fit_one(d, outcome, stratum, present))
    return pd.DataFrame(out_rows)


# ---------------------------------- plotting ------------------------------- #

OUTCOME_LABELS = {
    "ever_married":      "Ever married (1/0)",
    "age_first_marriage": "Age at first marriage (years)",
    "num_children":      "Number of children (sons+daughters)",
    "ideal_children":    "Ideal children if no policy",
    "marriage_sat":      "Marriage satisfaction (1-5, ↑=more)",
    "log_income":        "log(personal income+1)",
    "employed":          "Currently employed (1/0)",
    "weekly_hours":      "Weekly work hours",
    "mgmt_activity":     "Holds mgmt role (1/0)",
    "soe_indicator":     "State-sector employer (1/0)",
    "edu_yrs":           "Years of education",
}

GROUPS = [
    ("Family", ["ever_married", "age_first_marriage", "num_children",
                "ideal_children", "marriage_sat"]),
    ("Work",   ["log_income", "employed", "weekly_hours", "mgmt_activity",
                "soe_indicator"]),
    ("Edu",    ["edu_yrs"]),
]


def fig_summary_forest(res: pd.DataFrame, out_pdf: Path):
    """One forest of the ideation coefficient across outcomes, three strata
    (all / male / female), grouped by outcome family."""
    ideation_rows = res[res["term"] == "ideation"].copy()
    # arrange y positions: stratum × outcome
    fig, ax = plt.subplots(figsize=(8, 0.45 * 3 * len(OUTCOMES) + 1))
    colours = {"all": "#404040", "male": "#1f77b4", "female": "#d62728"}
    y = 0
    yticks, ylabels = [], []
    for group_name, outs in GROUPS:
        ax.text(0.0, y - 0.4, group_name, fontsize=10, fontweight="bold",
                transform=ax.get_yaxis_transform())
        y -= 0.7
        for outcome in outs:
            for stratum in ("all", "male", "female"):
                row = ideation_rows[(ideation_rows.outcome == outcome) &
                                    (ideation_rows.stratum == stratum)]
                if len(row) == 0 or not np.isfinite(row.iloc[0]["coef"]):
                    y -= 1
                    continue
                r = row.iloc[0]
                lo = r["coef"] - 1.96 * r["se"]
                hi = r["coef"] + 1.96 * r["se"]
                ax.plot([lo, hi], [y, y], color=colours[stratum], linewidth=1.2)
                ax.plot([r["coef"]], [y], "o", color=colours[stratum], markersize=4)
                yticks.append(y)
                ylabels.append(f"{OUTCOME_LABELS[outcome]} ({stratum}, n={int(r['n'])})")
                y -= 1
            y -= 0.5
    ax.axvline(0, color="grey", linewidth=0.5)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=8)
    ax.set_xlabel("β (ideation on outcome) ±95% CI — pooled CGSS 2010-2023, OLS-HC1")
    ax.set_title("analysis_036: ideation → individual outcomes, CGSS pooled 8 waves",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_per_group(res: pd.DataFrame, out_dir: Path):
    """One small forest PDF per outcome group, easier to read."""
    ideation_rows = res[res["term"] == "ideation"].copy()
    for group_name, outs in GROUPS:
        fig, ax = plt.subplots(figsize=(6.5, max(2.0, 0.45 * 3 * len(outs))))
        colours = {"all": "#404040", "male": "#1f77b4", "female": "#d62728"}
        y = 0
        yticks, ylabels = [], []
        for outcome in outs:
            for stratum in ("all", "male", "female"):
                row = ideation_rows[(ideation_rows.outcome == outcome) &
                                    (ideation_rows.stratum == stratum)]
                if len(row) == 0 or not np.isfinite(row.iloc[0]["coef"]):
                    y -= 1
                    continue
                r = row.iloc[0]
                lo = r["coef"] - 1.96 * r["se"]
                hi = r["coef"] + 1.96 * r["se"]
                ax.plot([lo, hi], [y, y], color=colours[stratum], linewidth=1.4)
                ax.plot([r["coef"]], [y], "o", color=colours[stratum], markersize=5)
                yticks.append(y)
                ylabels.append(f"{OUTCOME_LABELS[outcome]} · {stratum} (n={int(r['n'])})")
                y -= 1
            y -= 0.5
        ax.axvline(0, color="grey", linewidth=0.5)
        ax.set_yticks(yticks)
        ax.set_yticklabels(ylabels, fontsize=8)
        ax.set_xlabel(f"β (ideation → outcome) ±95% CI — CGSS pooled, {group_name}")
        ax.set_title(f"analysis_036 — {group_name}", fontsize=10)
        fig.tight_layout()
        fig.savefig(out_dir / f"forest_{group_name.lower()}.pdf")
        plt.close(fig)


# ----------------------------------- main --------------------------------- #

def main() -> int:
    frames = []
    for w in WAVES:
        frames.append(load_wave(w))
    d = pd.concat(frames, ignore_index=True)

    # Drop rows with no usable ideation/female/birthy
    d = d.dropna(subset=["ideation", "female", "birthy"]).reset_index(drop=True)

    desc = descriptive_table(d)
    miss = missing_table(d)
    desc.to_csv(RUN / "01_descriptive_table.csv", index=False)
    miss.to_csv(RUN / "02_missing_table.csv", index=False)
    print("=" * 60)
    print(f"CGSS pooled N (ideation+female+birthy non-missing): {len(d):,}")
    print(f"  female fraction: {d['female'].mean():.3f}")
    print(f"  ideation mean: {d['ideation'].mean():.3f}")
    print("=" * 60)
    print("\nWave coverage of outcomes (rows with non-missing outcome):")
    cov = miss.pivot(index="outcome", columns="wave", values="n_have").reindex(OUTCOMES)
    print(cov)

    res = run_models(d)
    res.to_csv(RUN / "04_result_table.csv", index=False)
    print("\nIdeation coefficient × outcome × stratum (selected):")
    sel = res[res["term"] == "ideation"][["outcome", "stratum", "n", "coef", "se", "t", "p"]]
    print(sel.to_string(index=False))

    fig_summary_forest(res, FIGS / "summary_forest_ideation_to_outcome.pdf")
    fig_per_group(res, FIGS)

    print(f"\nFigures: {FIGS}")
    print(f"Tables: 04_result_table.csv, 01_descriptive_table.csv, 02_missing_table.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
