#!/usr/bin/env python3
"""
analysis_037 — ACWF (中国妇女地位调查) replication of individual-level
ideation→outcome links, complementing analysis_036 (CGSS replication).

ACWF is a repeated cross-section of 3 waves (1990 / 2000 / 2010) with NO
panel pid and NO household structure.  Only individual-level cross-
sectional correlations can be replicated.

What ACWF contributes uniquely (not in CFPS or CGSS):

  * `wife_does_more_housework` (e8_c 2000 / F6B 2010) — categorical
    "who does more housework in the couple"; not directly available in
    CFPS or CGSS.  Pooled 2000 + 2010.
  * `leadership_ever` (d4_a 2000 / E6A 2010) — "have you ever held a
    leadership/management position?".  Pooled 2000 + 2010.
  * `housework_hours_1990` (h_work, minutes/day -> hours/day) — direct
    housework time measure in 1990 only.
  * `first_marriage_age_1990` (w32 direct in years) — 1990 only.

ACWF also has the shared individual-level outcomes already exposed in
rq51_helpers (edu_yrs, log_income, employed); we re-fit those here too,
as a within-program check of analysis_023's findings.

Design parallels analysis_036:

  outcome ~ ideation + female + ideation × female
          + birth_year_c + urban (hukou) + edu_yrs (if not LHS)
          + log_income (if not LHS) + wave dummies

OLS-HC1 robust SEs.  Stratified by sex (all / male / female).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["pdf.fonttype"] = 42

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L           # noqa: E402
import acwf_outcomes as A          # noqa: E402
import rq51_helpers as H           # noqa: E402
import stats_helpers as ST         # noqa: E402

RUN = HERE.parents[1]
FIGS = RUN / "figures"

WAVES = ["1990", "2000", "2010"]

# Variable name per wave for each outcome (None if not in this wave)
COLMAP = {
    "1990": dict(wife_more=None, leadership=None,
                 housework_mins="h_work", marry_age="w32", marital="w35"),
    "2000": dict(wife_more="e8_c", leadership="d4_a",
                 housework_mins=None, marry_age=None, marital="e1"),
    "2010": dict(wife_more="F6B", leadership="E6A",
                 housework_mins=None, marry_age=None, marital=None),
}

OUTCOMES = [
    "wife_does_more_housework",   # 2000+2010
    "leadership_ever",            # 2000+2010
    "housework_hours_1990",       # 1990 only
    "first_marriage_age_1990",    # 1990 only
    "log_income",                 # all 3
    "edu_yrs",                    # all 3
    "employed",                   # all 3
]


def load_wave(year: str) -> pd.DataFrame:
    cm = COLMAP[year]
    extras = [v for v in cm.values() if v]
    df, _meta, _norms, _idx = L.load_recoded("ACWF", year, extra_cols=extras)
    df = df[df["n_valid_items"] >= 1].copy().reset_index(drop=True)
    df["ideation"] = df["ideation_index"]
    df["birthy"] = H.birth_year("ACWF", year).reindex(df.index).astype(float)
    df["edu_yrs"] = H.education_years("ACWF", year).reindex(df.index).astype(float)
    df["urban"] = H.urban_indicator("ACWF", year).reindex(df.index).astype(float)
    income_raw = H.personal_income("ACWF", year).reindex(df.index).astype(float)
    df["log_income"] = np.log1p(income_raw)
    df["employed"] = H.employed_indicator("ACWF", year).reindex(df.index).astype(float)

    # outcomes
    df["wife_does_more_housework"] = (
        A.wife_does_more_housework(df[cm["wife_more"]]) if cm["wife_more"] else np.nan
    )
    df["leadership_ever"] = (
        A.leadership_ever(df[cm["leadership"]]) if cm["leadership"] else np.nan
    )
    df["housework_hours_1990"] = (
        A.housework_hours_acwf_1990(df[cm["housework_mins"]])
        if cm["housework_mins"] else np.nan
    )
    df["first_marriage_age_1990"] = (
        A.first_marriage_age_acwf_1990(df[cm["marry_age"]]) if cm["marry_age"] else np.nan
    )

    df["wave"] = year
    df["birth_yr_c"] = (df["birthy"] - 1960) / 10   # centered around 1960 (ACWF mid-age cohort)

    keep = ["wave", "ideation", "female", "birthy", "birth_yr_c", "urban",
            "edu_yrs", "log_income", "employed"]
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
    cols = {}
    for w in present_waves[1:]:
        cols[f"wave_{w}"] = (d["wave"] == w).astype(float)
    return pd.DataFrame(cols, index=d.index)


def _build_design(d: pd.DataFrame, outcome: str, stratum: str,
                  present_waves: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    sub = d[d["wave"].isin(present_waves)].copy()
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
    if outcome != "edu_yrs":
        X["edu_yrs"] = sub["edu_yrs"].astype(float)
    if outcome != "log_income":
        X["log_income"] = sub["log_income"].astype(float)
    X = pd.concat([X, _wave_dummies(sub, present_waves)], axis=1)
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
    rows = []
    for outcome in OUTCOMES:
        present = _waves_with_outcome(d, outcome)
        if not present:
            continue
        for stratum in ("all", "male", "female"):
            rows.extend(fit_one(d, outcome, stratum, present))
    return pd.DataFrame(rows)


OUTCOME_LABELS = {
    "wife_does_more_housework": "Wife does more housework (1/0)",
    "leadership_ever":           "Ever held leadership (1/0)",
    "housework_hours_1990":     "Housework hours/day (1990 only)",
    "first_marriage_age_1990":  "Age at first marriage (1990 only)",
    "log_income":                "log(personal income+1)",
    "edu_yrs":                   "Years of education",
    "employed":                  "Currently employed (1/0)",
}


def fig_forest(res: pd.DataFrame, out_pdf: Path):
    ideation_rows = res[res["term"] == "ideation"].copy()
    fig, ax = plt.subplots(figsize=(7.5, 0.45 * 3 * len(OUTCOMES) + 1))
    colours = {"all": "#404040", "male": "#1f77b4", "female": "#d62728"}
    y = 0
    yticks, ylabels = [], []
    for outcome in OUTCOMES:
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
    ax.set_xlabel("β (ideation → outcome) ±95% CI — ACWF pooled, OLS-HC1")
    ax.set_title("analysis_037 — ACWF ideation → individual outcomes", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_pdf)
    plt.close(fig)


def main() -> int:
    frames = []
    for w in WAVES:
        frames.append(load_wave(w))
    d = pd.concat(frames, ignore_index=True)
    d = d.dropna(subset=["ideation", "female", "birthy"]).reset_index(drop=True)

    desc = descriptive_table(d)
    miss = missing_table(d)
    desc.to_csv(RUN / "01_descriptive_table.csv", index=False)
    miss.to_csv(RUN / "02_missing_table.csv", index=False)

    print("=" * 60)
    print(f"ACWF pooled N (ideation+female+birthy): {len(d):,}")
    print(f"  female fraction: {d['female'].mean():.3f}")
    print(f"  ideation mean: {d['ideation'].mean():.3f}")
    print("=" * 60)
    print("\nWave coverage:")
    print(miss.pivot(index="outcome", columns="wave", values="n_have").reindex(OUTCOMES))

    res = run_models(d)
    res.to_csv(RUN / "04_result_table.csv", index=False)
    print("\nIdeation coefficient × outcome × stratum:")
    sel = res[res["term"] == "ideation"][["outcome", "stratum", "n", "coef", "se", "t", "p"]]
    print(sel.to_string(index=False))

    fig_forest(res, FIGS / "forest_ideation_to_outcome_acwf.pdf")
    print(f"\nFigure: {FIGS}/forest_ideation_to_outcome_acwf.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
