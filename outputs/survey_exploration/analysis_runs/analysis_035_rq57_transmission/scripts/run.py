#!/usr/bin/env python3
"""analysis_035 — RQ 5.7 parent → child ideation transmission (deep).

Three parts:
  A. OLS-HC1 of child_ideation on mother_id + father_id + interactions
  B. Within-family ICC of ideation (parent-child)
  C. Mediation decomposition via child_edu_yrs

Frames: 2014 cross, 2020 cross.
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
import stats_helpers as ST         # noqa: E402

import pyreadstat                  # noqa: E402

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


def _read_famconf(wave: str) -> pd.DataFrame:
    if wave == "2014":
        df, _ = pyreadstat.read_dta(
            str(L.ROOT / "surveys" / "CFPS" / "cfps2014_famconf.dta"),
            usecols=["pid", "pid_f", "pid_m", "fid14"])
        df = df.rename(columns={"pid_f": "father_pid",
                                  "pid_m": "mother_pid",
                                  "fid14": "fid"})
    else:
        df, _ = pyreadstat.read_dta(
            str(L.ROOT / "surveys" / "CFPS" / "cfps2020_famconf.dta"),
            usecols=["pid", "pid_a_f", "pid_a_m", "fid20"])
        df = df.rename(columns={"pid_a_f": "father_pid",
                                  "pid_a_m": "mother_pid",
                                  "fid20": "fid"})
    df = df.drop_duplicates(subset=["pid"], keep="first")
    df["father_pid"] = df["father_pid"].where(df["father_pid"] > 0)
    df["mother_pid"] = df["mother_pid"].where(df["mother_pid"] > 0)
    return df


def load_dyads(wave: str) -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", wave)]
    extras = ["pid",
              "cfps_birthy" if wave == "2014" else "ibirthy",
              cfg["gender_var"],
              "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im",
              "income" if wave == "2014" else "emp_income",
              "qa301"]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", wave, extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    yr = int(wave)
    birthy_col = "cfps_birthy" if wave == "2014" else "ibirthy"
    edu_col    = "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im"
    inc_col    = "income" if wave == "2014" else "emp_income"
    df["birthy"]  = pd.to_numeric(df[birthy_col], errors="coerce").where(
        lambda x: x.between(1920, 2010))
    df["age"]     = yr - df["birthy"]
    df["edu_yrs"] = pd.to_numeric(df[edu_col], errors="coerce").where(
        lambda x: x.between(0, 22))
    df["income"]  = P._to_numeric_nan_sentinels(df[inc_col]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0,
                            np.where(hk.isin([3, 7]), 1.0, np.nan))
    fam = _read_famconf(wave)
    df = df.merge(fam, on="pid", how="left")
    lookup = df.set_index("pid")[["ideation", "edu_yrs", "log_income", "age"]]
    for parent, ptr in [("mother", "mother_pid"), ("father", "father_pid")]:
        for v in ["ideation", "edu_yrs", "log_income", "age"]:
            df[f"{parent}_{v}"] = df[ptr].map(lookup[v])
    df["parent_avg_age"]    = df[["mother_age", "father_age"]].mean(axis=1)
    df["parent_avg_edu"]    = df[["mother_edu_yrs", "father_edu_yrs"]].mean(axis=1)
    df["parent_log_income"] = df[["mother_log_income", "father_log_income"]].mean(axis=1)
    return df


# ----------------------------------------------------------------- #
# A. Transmission OLS (with and without edu mediator)
# ----------------------------------------------------------------- #

def part_A_transmission(df: pd.DataFrame, wave: str,
                         include_edu_mediator: bool) -> pd.DataFrame:
    d = df.copy()
    d["age_c"]  = (d["age"] - 35) / 10
    d["age_c2"] = d["age_c"] ** 2
    base_needed = ["ideation", "mother_ideation", "father_ideation",
                   "female", "age_c", "age_c2", "urban",
                   "parent_avg_age", "parent_avg_edu", "parent_log_income"]
    if include_edu_mediator:
        base_needed.append("edu_yrs")
    d = d.dropna(subset=base_needed)
    if len(d) < 100:
        return pd.DataFrame()
    rows = []
    for stratum, mask in [
        ("all", pd.Series(True, index=d.index)),
        ("male", d["female"] == 0),
        ("female", d["female"] == 1),
    ]:
        sub = d.loc[mask].copy()
        X = pd.DataFrame({
            "const":           1.0,
            "mother_ideation": sub["mother_ideation"].astype(float),
            "father_ideation": sub["father_ideation"].astype(float),
            "child_female":    sub["female"].astype(float),
            "age_c":           sub["age_c"].astype(float),
            "age_c2":          sub["age_c2"].astype(float),
            "urban":           sub["urban"].astype(float),
            "parent_avg_age":  sub["parent_avg_age"].astype(float),
            "parent_avg_edu":  sub["parent_avg_edu"].astype(float),
            "parent_log_income": sub["parent_log_income"].astype(float),
        })
        if stratum == "all":
            X["mother_id_x_female"] = X["mother_ideation"] * X["child_female"]
            X["father_id_x_female"] = X["father_ideation"] * X["child_female"]
        else:
            X = X.drop(columns=["child_female"])
        if include_edu_mediator:
            X["child_edu_yrs"] = sub["edu_yrs"].astype(float)
        Xk = X.loc[:, [c for c in X.columns
                        if c == "const" or X[c].nunique(dropna=False) > 1]]
        if len(sub) < (Xk.shape[1] + 5):
            continue
        try:
            r = ST.ols_robust(Xk, sub["ideation"].to_numpy(), kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"],
                                          r["t"], r["p"]):
            rows.append(dict(wave=wave, stratum=stratum,
                             include_edu=include_edu_mediator,
                             n=int(r["n"]), term=term,
                             coef=round(float(coef), 5),
                             se=round(float(se), 5),
                             t=round(float(t), 3),
                             p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- #
# B. Within-family ICC and parent-child Pearson correlations
# ----------------------------------------------------------------- #

def part_B_correlations(df: pd.DataFrame, wave: str) -> pd.DataFrame:
    rows = []
    d = df.dropna(subset=["ideation", "mother_ideation", "father_ideation"])
    for who in ("mother", "father"):
        for stratum, mask in [
            ("all", pd.Series(True, index=d.index)),
            ("male", d["female"] == 0),
            ("female", d["female"] == 1),
        ]:
            sub = d.loc[mask]
            if len(sub) < 30:
                continue
            r_p = float(sub["ideation"].corr(sub[f"{who}_ideation"]))
            r_s = float(sub["ideation"].corr(sub[f"{who}_ideation"], method="spearman"))
            rows.append(dict(wave=wave, parent=who, stratum=stratum, n=len(sub),
                             pearson_r=round(r_p, 4),
                             spearman_r=round(r_s, 4)))
    # By parent-child cohort gap
    d2 = d.copy()
    d2["age_gap"] = d2[f"mother_age"] - d2["age"]
    d2["age_gap_bin"] = pd.cut(d2["age_gap"],
                                  [0, 25, 30, 35, 200],
                                  labels=["≤25", "26-30", "31-35", "36+"])
    for bin_, g in d2.dropna(subset=["age_gap_bin"]).groupby("age_gap_bin",
                                                                observed=True):
        if len(g) < 30:
            continue
        rows.append(dict(wave=wave, parent="mother",
                         stratum=f"mother_child_age_gap={bin_}",
                         n=len(g),
                         pearson_r=round(float(g["ideation"].corr(g["mother_ideation"])), 4),
                         spearman_r=round(float(g["ideation"].corr(g["mother_ideation"], method="spearman")), 4)))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- #
# Figures
# ----------------------------------------------------------------- #

def fig_transmission_forest(res: pd.DataFrame, out_pdf: Path):
    """Forest of mother_id + father_id coefficients across (wave, stratum)
    side-by-side (with vs without edu mediator)."""
    sub = res[res["term"].isin(["mother_ideation", "father_ideation"])].copy()
    if sub.empty:
        return
    sub["med"] = sub["include_edu"].map({True: "+ edu mediator",
                                            False: "no mediator"})
    sub["label"] = sub.apply(
        lambda r: f"[{r['wave']}] {r['term']} · {r['stratum']} · {r['med']} (n={r['n']})",
        axis=1)
    sub = sub.sort_values(["wave", "term", "stratum", "include_edu"])
    rows = list(zip(sub["coef"], sub["se"], sub["label"], sub["include_edu"]))
    fig, ax = plt.subplots(figsize=(8.2, 0.28 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    colors = ["#d62728" if r[3] else "#1f77b4" for r in rows]
    for i, (c, s, color) in enumerate(zip(coefs, ses, colors)):
        ax.errorbar([c], [ys[i]], xerr=1.96 * s, fmt="o", color=color,
                    ecolor=color, capsize=3, markersize=5)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=7)
    ax.set_xlabel("OLS β on parent ideation (HC1, 95 % CI)")
    ax.set_title("Parent → child ideation transmission\nblue = base model, red = adds child_edu_yrs mediator")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_parent_child_scatter(df: pd.DataFrame, wave: str, parent: str,
                                out_pdf: Path):
    d = df.dropna(subset=["ideation", f"{parent}_ideation"])
    if len(d) < 50:
        return
    fig, ax = plt.subplots(figsize=(4.4, 4.4))
    ax.scatter(d[f"{parent}_ideation"], d["ideation"], s=4, alpha=0.25,
               color="#1f77b4")
    ax.plot([0, 1], [0, 1], "--", color="#888", linewidth=0.7)
    b = d["ideation"].cov(d[f"{parent}_ideation"]) / d[f"{parent}_ideation"].var(ddof=1)
    a = d["ideation"].mean() - b * d[f"{parent}_ideation"].mean()
    xs = np.linspace(0, 1, 100)
    ax.plot(xs, a + b * xs, color="#d62728", linewidth=1.4,
            label=f"OLS slope = {b:.3f}")
    r = d["ideation"].corr(d[f"{parent}_ideation"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel(f"{parent.capitalize()} ideation"); ax.set_ylabel("Child ideation")
    ax.set_title(f"Child × {parent} ideation — CFPS {wave}\nPearson r = {r:.3f}  (n = {len(d)})")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.grid(linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def main() -> int:
    all_reg, all_corr, miss_rows = [], [], []
    for wave in ("2014", "2020"):
        print(f"loading {wave} dyads …")
        df = load_dyads(wave)
        n_with_all = int(df[["mother_ideation", "father_ideation", "ideation"]]
                          .notna().all(axis=1).sum())
        print(f"  n_adults = {len(df)}; all three ideation present = {n_with_all}")
        all_reg.append(part_A_transmission(df, wave, include_edu_mediator=False))
        all_reg.append(part_A_transmission(df, wave, include_edu_mediator=True))
        all_corr.append(part_B_correlations(df, wave))
        miss_rows.append(dict(wave=wave, n_adults=len(df),
                              n_with_three_ideation=n_with_all))
        for parent in ("mother", "father"):
            fig_parent_child_scatter(df, wave, parent,
                                     FIGS / f"scatter_{parent}_child_{wave}.pdf")

    reg = pd.concat(all_reg, ignore_index=True)
    reg.to_csv(RUN / "04_result_table.csv", index=False)
    corr = pd.concat(all_corr, ignore_index=True)
    corr.to_csv(TABLES / "parent_child_correlations.csv", index=False)
    pd.DataFrame(miss_rows).to_csv(RUN / "02_missing_table.csv", index=False)

    # Descriptive: mean child ideation by parent tertile × child sex
    desc_rows = []
    for wave in ("2014", "2020"):
        df = load_dyads(wave)
        d = df.dropna(subset=["ideation", "female",
                                "mother_ideation", "father_ideation"])
        for who in ("mother", "father"):
            q = d[f"{who}_ideation"].quantile([1 / 3, 2 / 3]).values
            d["__t"] = pd.cut(d[f"{who}_ideation"], [-np.inf, q[0], q[1], np.inf],
                                labels=["low", "mid", "high"])
            for t in ("low", "mid", "high"):
                for sex_name, sex_val in [("daughter", 1), ("son", 0)]:
                    sub = d.loc[(d["__t"] == t) & (d["female"] == sex_val), "ideation"]
                    if len(sub) < 20:
                        continue
                    desc_rows.append(dict(wave=wave, parent=who,
                                          parent_id_tertile=t, child=sex_name,
                                          n=int(sub.notna().sum()),
                                          mean_child_id=round(float(sub.mean()), 4)))
    pd.DataFrame(desc_rows).to_csv(RUN / "01_descriptive_table.csv", index=False)
    print("tables written.")

    fig_transmission_forest(reg, FIGS / "transmission_forest.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
