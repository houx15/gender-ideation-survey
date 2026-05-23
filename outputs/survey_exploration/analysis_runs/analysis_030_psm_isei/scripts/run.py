#!/usr/bin/env python3
"""analysis_030 — PSM (not DiD) for ISEI prestige | ideation_2014.

Design:
  Treatment: high-ideation tertile (1) vs low-ideation tertile (0) of
             ideation_2014; middle tertile dropped.
  Outcome:   isei_2020 (qg303code_isei, current main job).
  Sample:    CFPS panel members, employed_2020 == 1, ISEI 2020 non-missing.
  Covariates: birthy_2014, edu_yrs_2014, urban_2014, log_income_2014,
              employed_2014.
  Stratum:    overall / male / female.

Mirrors the 025 PSM-DiD template using matching.py + bootstrap inference.
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
        "log_income_2014", "employed_2014"]


def build_panel_with_isei() -> pd.DataFrame:
    p = P.build_panel().copy()
    cfg = L.SURVEYS[("CFPS", "2020")]
    extra, _ = pyreadstat.read_dta(
        str(L.ROOT / cfg["file"]),
        usecols=["pid", "qg303code_isei"])
    extra["isei_2020"] = C.clean_continuous(
        pd.to_numeric(extra["qg303code_isei"], errors="coerce"), 10, 90)
    extra = extra.drop_duplicates(subset=["pid"], keep="first")
    p = p.merge(extra[["pid", "isei_2020"]], on="pid", how="left")
    p["log_income_2014"] = np.log1p(p["income_2014"])
    # binarize ideation 2014: top tertile = 1, bottom = 0, middle = NaN
    q = p["ideation_2014"].quantile([1 / 3, 2 / 3])
    p["treat"] = np.nan
    p.loc[p["ideation_2014"] >= q.iloc[1], "treat"] = 1.0
    p.loc[p["ideation_2014"] <= q.iloc[0], "treat"] = 0.0
    return p


def run_one(p: pd.DataFrame, stratum: str) -> dict:
    """One PSM-ATT estimate for a stratum (overall/male/female)."""
    if stratum == "male":
        d = p[p["female"] == 0].copy()
    elif stratum == "female":
        d = p[p["female"] == 1].copy()
    else:
        d = p.copy()
    d = d[(d["employed_2020"] == 1)]
    d = d.dropna(subset=["treat", "isei_2020"] + COVS)
    if len(d) < 50 or d["treat"].nunique() < 2:
        return {"stratum": stratum, "n_treated": int((d["treat"] == 1).sum()),
                "n_control": int((d["treat"] == 0).sum()), "note": "insufficient"}
    boot = M.psm_att_boot(d, treat_col="treat", outcome_col="isei_2020",
                          covariate_cols=COVS, caliper=0.2, n_boot=300, seed=0)
    point = M.psm_att(d, treat_col="treat", outcome_col="isei_2020",
                      covariate_cols=COVS, caliper=0.2)
    diag  = M.psm_diagnostic(d, treat_col="treat", covariate_cols=COVS,
                              caliper=0.2)
    return {
        "stratum": stratum,
        "n_treated": int(point["n_treated"]),
        "n_control": int(point["n_control"]),
        "att": float(boot["att"]),
        "boot_se": float(boot["boot_se"]),
        "p": float(boot["p"]),
        "ci_lo": float(boot["ci_lo"]),
        "ci_hi": float(boot["ci_hi"]),
        "n_boot": int(boot["n_boot"]),
        "_d": d,
        "_diag": diag,
    }


def balance_table(d: pd.DataFrame, diag: dict, stratum: str) -> pd.DataFrame:
    """SMD pre and post matching, per covariate.

    psm_diagnostic returns indices into the *dropna-cleaned* subframe;
    reconstruct that subframe here so the indexing aligns.
    """
    rows = []
    cleaned = d[["treat"] + COVS].dropna().reset_index(drop=True)
    treated_pre = cleaned[cleaned["treat"] == 1]
    control_pre = cleaned[cleaned["treat"] == 0]
    matched_t = cleaned.iloc[diag["treated_idx"]]
    matched_c = cleaned.iloc[diag["matched_control_idx"]]
    for c in COVS:
        pre = M.standardised_mean_difference(treated_pre[c], control_pre[c])
        post = M.standardised_mean_difference(matched_t[c], matched_c[c])
        rows.append(dict(stratum=stratum, covariate=c,
                         pre_smd=round(float(pre), 4),
                         post_smd=round(float(post), 4)))
    return pd.DataFrame(rows)


def main() -> int:
    print("building panel with ISEI 2020 …")
    p = build_panel_with_isei()
    at_risk = int(((p["employed_2020"] == 1) & p["isei_2020"].notna()).sum())
    print(f"  panel n = {len(p)}; with treat = {int(p['treat'].notna().sum())}; "
          f"employed_2020 == 1 + ISEI nonmissing = {at_risk}")

    results, balance_rows = [], []
    for stratum in ("all", "male", "female"):
        r = run_one(p, stratum)
        if "att" not in r:
            results.append(dict(stratum=stratum, n_treated=r["n_treated"],
                                n_control=r["n_control"], note=r["note"]))
            continue
        results.append({k: v for k, v in r.items()
                         if not k.startswith("_")})
        balance_rows.append(balance_table(r["_d"], r["_diag"], stratum))

    att_tab = pd.DataFrame(results)
    att_tab.to_csv(RUN / "04_result_table.csv", index=False)
    att_tab.to_csv(TABLES / "psm_att.csv", index=False)
    if balance_rows:
        pd.concat(balance_rows, ignore_index=True).to_csv(
            TABLES / "psm_balance.csv", index=False)

    # missing / meta tables for project consistency
    pd.DataFrame([
        dict(item="n_panel", value=len(p)),
        dict(item="n_treat_binarized", value=int(p["treat"].notna().sum())),
        dict(item="n_isei_nonmissing", value=int(p["isei_2020"].notna().sum())),
        dict(item="n_employed_2020", value=int((p["employed_2020"] == 1).sum())),
    ]).to_csv(TABLES / "psm_meta.csv", index=False)
    pd.DataFrame([
        dict(variable="ideation_2014", n_nonmissing=int(p["ideation_2014"].notna().sum()),
             n_total=len(p)),
        dict(variable="treat (top/bot tertile)", n_nonmissing=int(p["treat"].notna().sum()),
             n_total=len(p)),
        dict(variable="isei_2020", n_nonmissing=int(p["isei_2020"].notna().sum()),
             n_total=len(p)),
    ]).to_csv(RUN / "02_missing_table.csv", index=False)
    # descriptives
    rows = []
    for st in ("all", "male", "female"):
        sub = p if st == "all" else p[p["female"] == int(st == "female")]
        rows.append(dict(stratum=st,
                         n=int(len(sub)),
                         mean_isei_high_id=round(float(sub.loc[sub["treat"] == 1, "isei_2020"].mean()), 2),
                         mean_isei_low_id=round(float(sub.loc[sub["treat"] == 0, "isei_2020"].mean()), 2),
                         raw_diff=round(float(sub.loc[sub["treat"] == 1, "isei_2020"].mean()
                                               - sub.loc[sub["treat"] == 0, "isei_2020"].mean()), 2)))
    pd.DataFrame(rows).to_csv(RUN / "01_descriptive_table.csv", index=False)

    print("tables written.")

    # ATT forest
    df_ok = att_tab[att_tab["att"].notna()].copy() if "att" in att_tab.columns else pd.DataFrame()
    if not df_ok.empty:
        fig, ax = plt.subplots(figsize=(5.6, 2.4))
        ys = np.arange(len(df_ok))[::-1]
        ax.errorbar(df_ok["att"], ys, xerr=1.96 * df_ok["boot_se"], fmt="o",
                    color="#222", ecolor="#888", capsize=3)
        ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
        ax.set_yticks(ys); ax.set_yticklabels([f"{r.stratum} (n_T={r.n_treated})"
                                                  for r in df_ok.itertuples()], fontsize=9)
        ax.set_xlabel("PSM ATT on ISEI 2020 (HC=bootstrap, 95 % CI)")
        ax.set_title("Effect of high (vs low) 2014 ideation on 2020 ISEI prestige")
        ax.grid(axis="x", linewidth=0.4, alpha=0.4)
        fig.tight_layout(); fig.savefig(FIGS / "psm_att_forest.pdf"); plt.close(fig)

    # Balance plot
    bal = pd.read_csv(TABLES / "psm_balance.csv") if (TABLES / "psm_balance.csv").exists() else pd.DataFrame()
    if not bal.empty:
        fig, axes = plt.subplots(1, len(bal["stratum"].unique()), figsize=(8.0, 3.4),
                                  sharey=True)
        if len(bal["stratum"].unique()) == 1:
            axes = [axes]
        for ax, st in zip(axes, sorted(bal["stratum"].unique())):
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
        fig.suptitle("PSM balance (SMD pre / post matching) per stratum", fontsize=10)
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        fig.savefig(FIGS / "psm_balance.pdf"); plt.close(fig)
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
