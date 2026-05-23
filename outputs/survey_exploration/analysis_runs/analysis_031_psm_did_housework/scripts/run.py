#!/usr/bin/env python3
"""analysis_031 — PSM-DiD for Δhousework | ideation_2014.

Design:
  Treatment: high-ideation (top tertile) vs low-ideation (bottom) of
             ideation_2014; middle dropped.
  Outcome:   delta_housework = housework_2020 - housework_2014
             (genuine PSM-DiD since housework is in both waves).
  Sample:    CFPS panel with both housework values non-missing.
  Covariates: birthy_2014, edu_yrs_2014, urban_2014, log_income_2014,
              employed_2014, marital_2014, children_n_2014.
  Stratum:    overall / male / female.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve()
RUN = HERE.parents[1]
TABLES = RUN / "tables"
FIGS = RUN / "figures"
TABLES.mkdir(parents=True, exist_ok=True)
FIGS.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE.parents[3] / "scripts"))
import ideation_lib as L           # noqa: E402
import cfps_panel as P             # noqa: E402
import cfps_outcomes as C          # noqa: E402
import matching as M               # noqa: E402

import pyreadstat                  # noqa: E402

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


COVS = ["birthy_2014", "edu_yrs_2014", "urban_2014",
        "log_income_2014", "employed_2014",
        "marital_2014", "children_n_2014"]


def build_panel_with_housework() -> pd.DataFrame:
    p = P.build_panel().copy()
    cfg14 = L.SURVEYS[("CFPS", "2014")]
    cfg20 = L.SURVEYS[("CFPS", "2020")]
    e14, _ = pyreadstat.read_dta(str(L.ROOT / cfg14["file"]),
                                  usecols=["pid", "qq9010"])
    e20, _ = pyreadstat.read_dta(str(L.ROOT / cfg20["file"]),
                                  usecols=["pid", "qq9010n"])
    e14["housework_2014"] = C.housework_hours_daily(e14["qq9010"])
    e20["housework_2020"] = C.housework_hours_daily(e20["qq9010n"])
    e14 = e14.drop_duplicates(subset=["pid"], keep="first")
    e20 = e20.drop_duplicates(subset=["pid"], keep="first")
    p = p.merge(e14[["pid", "housework_2014"]], on="pid", how="left")
    p = p.merge(e20[["pid", "housework_2020"]], on="pid", how="left")
    p["delta_housework"] = p["housework_2020"] - p["housework_2014"]
    p["log_income_2014"] = np.log1p(p["income_2014"])
    # binarize ideation
    q = p["ideation_2014"].quantile([1 / 3, 2 / 3])
    p["treat"] = np.nan
    p.loc[p["ideation_2014"] >= q.iloc[1], "treat"] = 1.0
    p.loc[p["ideation_2014"] <= q.iloc[0], "treat"] = 0.0
    return p


def run_one(p: pd.DataFrame, stratum: str) -> dict:
    if stratum == "male":
        d = p[p["female"] == 0].copy()
    elif stratum == "female":
        d = p[p["female"] == 1].copy()
    else:
        d = p.copy()
    d = d.dropna(subset=["treat", "delta_housework"] + COVS)
    if len(d) < 50 or d["treat"].nunique() < 2:
        return {"stratum": stratum, "n_treated": int((d["treat"] == 1).sum()),
                "n_control": int((d["treat"] == 0).sum()), "note": "insufficient"}
    boot = M.psm_att_boot(d, treat_col="treat", outcome_col="delta_housework",
                          covariate_cols=COVS, caliper=0.2, n_boot=300, seed=0)
    point = M.psm_att(d, treat_col="treat", outcome_col="delta_housework",
                      covariate_cols=COVS, caliper=0.2)
    diag  = M.psm_diagnostic(d, treat_col="treat", covariate_cols=COVS,
                              caliper=0.2)
    return {"stratum": stratum,
            "n_treated": int(point["n_treated"]),
            "n_control": int(point["n_control"]),
            "att": float(boot["att"]),
            "boot_se": float(boot["boot_se"]),
            "p": float(boot["p"]),
            "ci_lo": float(boot["ci_lo"]),
            "ci_hi": float(boot["ci_hi"]),
            "n_boot": int(boot["n_boot"]),
            "_d": d, "_diag": diag}


def balance_table(d, diag, stratum):
    cleaned = d[["treat"] + COVS].dropna().reset_index(drop=True)
    treated_pre = cleaned[cleaned["treat"] == 1]
    control_pre = cleaned[cleaned["treat"] == 0]
    matched_t = cleaned.iloc[diag["treated_idx"]]
    matched_c = cleaned.iloc[diag["matched_control_idx"]]
    rows = []
    for c in COVS:
        rows.append(dict(stratum=stratum, covariate=c,
                         pre_smd=round(float(M.standardised_mean_difference(treated_pre[c], control_pre[c])), 4),
                         post_smd=round(float(M.standardised_mean_difference(matched_t[c], matched_c[c])), 4)))
    return pd.DataFrame(rows)


def main() -> int:
    print("building panel with housework + Δ …")
    p = build_panel_with_housework()
    at_risk = int(p["delta_housework"].notna().sum())
    print(f"  panel n = {len(p)}; Δhousework non-missing = {at_risk}; "
          f"treat non-missing = {int(p['treat'].notna().sum())}")

    results, balance_rows = [], []
    for st in ("all", "male", "female"):
        r = run_one(p, st)
        if "att" not in r:
            results.append(dict(stratum=st, n_treated=r["n_treated"],
                                n_control=r["n_control"], note=r["note"]))
            continue
        results.append({k: v for k, v in r.items() if not k.startswith("_")})
        balance_rows.append(balance_table(r["_d"], r["_diag"], st))

    att_tab = pd.DataFrame(results)
    att_tab.to_csv(RUN / "04_result_table.csv", index=False)
    att_tab.to_csv(TABLES / "psm_att.csv", index=False)
    if balance_rows:
        pd.concat(balance_rows, ignore_index=True).to_csv(
            TABLES / "psm_balance.csv", index=False)

    pd.DataFrame([
        dict(item="n_panel", value=len(p)),
        dict(item="n_treat_binarized", value=int(p["treat"].notna().sum())),
        dict(item="n_delta_housework", value=at_risk),
    ]).to_csv(TABLES / "psm_meta.csv", index=False)
    pd.DataFrame([
        dict(variable="ideation_2014", n_nonmissing=int(p["ideation_2014"].notna().sum()),
             n_total=len(p)),
        dict(variable="treat (top/bot tertile)", n_nonmissing=int(p["treat"].notna().sum()),
             n_total=len(p)),
        dict(variable="housework_2014", n_nonmissing=int(p["housework_2014"].notna().sum()),
             n_total=len(p)),
        dict(variable="housework_2020", n_nonmissing=int(p["housework_2020"].notna().sum()),
             n_total=len(p)),
        dict(variable="delta_housework", n_nonmissing=at_risk, n_total=len(p)),
    ]).to_csv(RUN / "02_missing_table.csv", index=False)
    rows = []
    for st in ("all", "male", "female"):
        sub = p if st == "all" else p[p["female"] == int(st == "female")]
        rows.append(dict(stratum=st,
                         n=int(len(sub)),
                         mean_dhw_high_id=round(float(sub.loc[sub["treat"] == 1, "delta_housework"].mean()), 3),
                         mean_dhw_low_id=round(float(sub.loc[sub["treat"] == 0, "delta_housework"].mean()), 3),
                         raw_diff=round(float(sub.loc[sub["treat"] == 1, "delta_housework"].mean()
                                               - sub.loc[sub["treat"] == 0, "delta_housework"].mean()), 3)))
    pd.DataFrame(rows).to_csv(RUN / "01_descriptive_table.csv", index=False)

    print("tables written.")

    # Forest + balance figures
    df_ok = att_tab[att_tab["att"].notna()].copy() if "att" in att_tab.columns else pd.DataFrame()
    if not df_ok.empty:
        fig, ax = plt.subplots(figsize=(5.6, 2.4))
        ys = np.arange(len(df_ok))[::-1]
        ax.errorbar(df_ok["att"], ys, xerr=1.96 * df_ok["boot_se"], fmt="o",
                    color="#222", ecolor="#888", capsize=3)
        ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
        ax.set_yticks(ys); ax.set_yticklabels([f"{r.stratum} (n_T={r.n_treated})"
                                                  for r in df_ok.itertuples()], fontsize=9)
        ax.set_xlabel("PSM-DiD ATT on Δ-housework (hr/day, bootstrap 95 % CI)")
        ax.set_title("Effect of high (vs low) 2014 ideation on Δ-housework 2014→2020")
        ax.grid(axis="x", linewidth=0.4, alpha=0.4)
        fig.tight_layout(); fig.savefig(FIGS / "psm_att_forest.pdf"); plt.close(fig)
    bal = pd.read_csv(TABLES / "psm_balance.csv") if (TABLES / "psm_balance.csv").exists() else pd.DataFrame()
    if not bal.empty:
        strata = sorted(bal["stratum"].unique())
        fig, axes = plt.subplots(1, len(strata), figsize=(9.5, 3.4), sharey=True)
        if len(strata) == 1:
            axes = [axes]
        for ax, st in zip(axes, strata):
            sub = bal[bal["stratum"] == st]
            ys = np.arange(len(sub))[::-1]
            ax.scatter(sub["pre_smd"], ys, color="#d62728", label="pre", s=24)
            ax.scatter(sub["post_smd"], ys, color="#1f77b4", label="post", s=24)
            for y, pre, post in zip(ys, sub["pre_smd"], sub["post_smd"]):
                ax.plot([pre, post], [y, y], color="#888", linewidth=0.6)
            ax.axvline(0, color="#aaa", linewidth=0.5)
            ax.axvspan(-0.1, 0.1, color="#dfe", alpha=0.5)
            ax.set_yticks(ys); ax.set_yticklabels(sub["covariate"].tolist(), fontsize=8)
            ax.set_xlabel("SMD")
            ax.set_title(st)
            ax.grid(axis="x", linewidth=0.3, alpha=0.4)
            if ax is axes[0]:
                ax.legend(frameon=False, fontsize=8, loc="lower right")
        fig.suptitle("PSM-DiD balance (SMD pre/post) per stratum", fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(FIGS / "psm_balance.pdf"); plt.close(fig)
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
