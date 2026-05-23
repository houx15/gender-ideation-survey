#!/usr/bin/env python3
"""analysis_033 — RQ 5.5 parent → child resource allocation (deep).

Two designs:
  A. Child-level OLS: edu_yrs ~ mother_id + father_id + female
                                + mother_id*female + father_id*female
                                + child + parent controls
  B. One-son-one-daughter sibling difference (cleanest):
     Δ_edu (daughter - son) ~ mother_id + father_id, within-family FE
     built-in via differencing.

Frames: 2014 and 2020 cross-sections, separately.
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats as sps

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
import cfps_linkage as K           # noqa: E402
import stats_helpers as ST         # noqa: E402

import pyreadstat                  # noqa: E402

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


def _read_famconf(wave: str) -> pd.DataFrame:
    """Returns pid → parent pid mapping and family id."""
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
    # zero / negative pid means "not in sample"
    df["father_pid"] = df["father_pid"].where(df["father_pid"] > 0)
    df["mother_pid"] = df["mother_pid"].where(df["mother_pid"] > 0)
    return df


def load_dyads(wave: str) -> pd.DataFrame:
    """For each adult respondent (child), attach mother + father ideation
    and education from the adult file."""
    cfg = L.SURVEYS[("CFPS", wave)]
    extras = ["pid", "qea0",
              "cfps_birthy" if wave == "2014" else "ibirthy",
              cfg["gender_var"],
              "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im",
              "income" if wave == "2014" else "emp_income",
              "qa301"]
    df, _m, _n, idx = L.load_recoded(
        "CFPS", wave, extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    birthy_col = "cfps_birthy" if wave == "2014" else "ibirthy"
    edu_col    = "cfps2014eduy_im" if wave == "2014" else "cfps2020eduy_im"
    inc_col    = "income" if wave == "2014" else "emp_income"
    yr         = int(wave)
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

    # Attach parent variables: ideation, edu_yrs, log_income, age
    parents_lookup = df.set_index("pid")[["ideation", "edu_yrs", "log_income", "age"]]
    for parent, ptr in [("mother", "mother_pid"), ("father", "father_pid")]:
        for v in ["ideation", "edu_yrs", "log_income", "age"]:
            df[f"{parent}_{v}"] = df[ptr].map(parents_lookup[v])
    return df


# ------------------------------------------------------------------ #
# A. Child-level OLS
# ------------------------------------------------------------------ #

def part_A_child_ols(df: pd.DataFrame, wave: str) -> pd.DataFrame:
    """OLS-HC1 of child_edu_yrs on parent ideation + interactions + controls."""
    d = df.copy()
    d["child_female"] = d["female"]
    d["age_c"] = (d["age"] - 25) / 10
    d["age_c2"] = d["age_c"] ** 2
    d["parent_avg_age"] = d[["mother_age", "father_age"]].mean(axis=1)
    d["parent_avg_edu"] = d[["mother_edu_yrs", "father_edu_yrs"]].mean(axis=1)
    d["parent_log_income"] = d[["mother_log_income", "father_log_income"]].mean(axis=1)

    base_cols = ["edu_yrs", "child_female", "age_c", "age_c2", "urban",
                 "mother_ideation", "father_ideation",
                 "parent_avg_age", "parent_avg_edu", "parent_log_income"]
    d = d.dropna(subset=base_cols)
    if len(d) < 100:
        return pd.DataFrame()

    rows = []
    for stratum, mask in [
        ("all", pd.Series(True, index=d.index)),
        ("male", d["child_female"] == 0),
        ("female", d["child_female"] == 1),
    ]:
        sub = d.loc[mask].copy()
        # build design
        X = pd.DataFrame({
            "const":            1.0,
            "mother_ideation":  sub["mother_ideation"].astype(float),
            "father_ideation":  sub["father_ideation"].astype(float),
            "child_female":     sub["child_female"].astype(float),
            "age_c":            sub["age_c"].astype(float),
            "age_c2":           sub["age_c2"].astype(float),
            "urban":            sub["urban"].astype(float),
            "parent_avg_age":   sub["parent_avg_age"].astype(float),
            "parent_avg_edu":   sub["parent_avg_edu"].astype(float),
            "parent_log_income": sub["parent_log_income"].astype(float),
        })
        if stratum == "all":
            X["mother_id_x_female"] = X["mother_ideation"] * X["child_female"]
            X["father_id_x_female"] = X["father_ideation"] * X["child_female"]
        else:
            X = X.drop(columns=["child_female"])
        # drop zero-variance cols
        Xk = X.loc[:, [c for c in X.columns
                        if c == "const" or X[c].nunique(dropna=False) > 1]]
        if len(sub) < (Xk.shape[1] + 5):
            continue
        try:
            r = ST.ols_robust(Xk, sub["edu_yrs"].to_numpy(), kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"],
                                          r["t"], r["p"]):
            rows.append(dict(wave=wave, design="A_child_ols", stratum=stratum,
                             n=int(r["n"]), term=term,
                             coef=round(float(coef), 5),
                             se=round(float(se), 5),
                             t=round(float(t), 3),
                             p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# B. One-son-one-daughter sibling difference
# ------------------------------------------------------------------ #

def part_B_sibling_diff(df: pd.DataFrame, wave: str) -> pd.DataFrame:
    """Within-family Δ-edu_yrs (daughter - son) ~ mother_id + father_id.

    Differences out all family-level confounders. Only mother / father
    ideation remain as predictors. Cleanest gendered-allocation test.
    """
    d = df.dropna(subset=["edu_yrs", "fid", "female",
                            "mother_ideation", "father_ideation"]).copy()
    diff = K.one_son_one_daughter_diff(
        d, family_col="fid", female_col="female",
        value_cols=["edu_yrs", "mother_ideation", "father_ideation"])
    if diff.empty:
        return pd.DataFrame()
    # daughter - son for mother/father ideation should be 0 by construction
    # (same parent for both children), so drop them and only keep edu_yrs_diff
    # as outcome plus parent ideology levels from one of the children.
    diff = diff.rename(columns={"edu_yrs_diff": "edu_diff"})
    # join back the parent ideation (constant within family for the parents)
    one_per_family = d.drop_duplicates(subset=["fid"], keep="first")[
        ["fid", "mother_ideation", "father_ideation",
         "mother_edu_yrs", "father_edu_yrs", "urban"]]
    diff = diff.merge(one_per_family, on="fid", how="left")
    diff = diff.dropna(subset=["edu_diff", "mother_ideation", "father_ideation"])
    if len(diff) < 50:
        return pd.DataFrame()

    X = pd.DataFrame({
        "const":            1.0,
        "mother_ideation":  diff["mother_ideation"].astype(float),
        "father_ideation":  diff["father_ideation"].astype(float),
        "mother_edu_yrs":   diff["mother_edu_yrs"].astype(float),
        "father_edu_yrs":   diff["father_edu_yrs"].astype(float),
        "urban":            diff["urban"].astype(float),
    })
    keep = X.notna().all(axis=1)
    Xk = X.loc[keep]
    yk = diff.loc[keep, "edu_diff"].to_numpy()
    if len(Xk) < (Xk.shape[1] + 5):
        return pd.DataFrame()
    try:
        r = ST.ols_robust(Xk, yk, kind="HC1")
    except np.linalg.LinAlgError:
        return pd.DataFrame()
    rows = []
    for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"],
                                      r["t"], r["p"]):
        rows.append(dict(wave=wave, design="B_1s1d_diff", stratum="all",
                         n=int(r["n"]), term=term,
                         coef=round(float(coef), 5),
                         se=round(float(se), 5),
                         t=round(float(t), 3),
                         p=round(float(p), 5)))
    return pd.DataFrame(rows)


def descriptive(df: pd.DataFrame, wave: str) -> pd.DataFrame:
    """Mean child edu_yrs by parent ideation tertile × child sex."""
    rows = []
    d = df.dropna(subset=["edu_yrs", "female", "mother_ideation", "father_ideation"]).copy()
    for who in ("mother", "father"):
        col = f"{who}_ideation"
        q = d[col].quantile([1 / 3, 2 / 3]).values
        d["__t"] = pd.cut(d[col], [-np.inf, q[0], q[1], np.inf],
                            labels=["low", "mid", "high"])
        for t in ("low", "mid", "high"):
            for sex_name, sex_val in [("daughter", 1), ("son", 0)]:
                sub = d.loc[(d["__t"] == t) & (d["female"] == sex_val), "edu_yrs"]
                if len(sub) < 20:
                    continue
                rows.append(dict(wave=wave, parent=who, parent_id_tertile=t,
                                 child=sex_name, n=int(len(sub)),
                                 mean_child_edu=round(float(sub.mean()), 3),
                                 sd_child_edu=round(float(sub.std(ddof=1)), 3)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# Figures
# ------------------------------------------------------------------ #

def fig_edu_by_parent_tertile(desc: pd.DataFrame, out_pdf: Path):
    if desc.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.4), sharey=True)
    for ax, who in zip(axes, ("mother", "father")):
        sub = desc[desc["parent"] == who]
        if sub.empty:
            continue
        for sex_name, color, offset in [("daughter", "#d62728", -0.18),
                                          ("son", "#1f77b4", +0.18)]:
            ssub = sub[sub["child"] == sex_name].set_index("parent_id_tertile")
            xs = np.arange(3)
            order = ["low", "mid", "high"]
            means = [float(ssub.loc[t, "mean_child_edu"]) if t in ssub.index else np.nan
                     for t in order]
            ses = [float(ssub.loc[t, "sd_child_edu"]) / np.sqrt(float(ssub.loc[t, "n"]))
                    if t in ssub.index else 0 for t in order]
            ax.bar(xs + offset, means, width=0.34, color=color,
                   label=sex_name, yerr=ses, capsize=3)
        ax.set_xticks(np.arange(3))
        ax.set_xticklabels(["progressive", "mid", "traditional"])
        ax.set_xlabel(f"{who}'s ideation tertile")
        if who == "mother":
            ax.set_ylabel("Child mean years of education")
        ax.set_title(who.capitalize())
        ax.grid(axis="y", linewidth=0.4, alpha=0.4)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Child education years by parent ideation × child sex", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_pdf); plt.close(fig)


def fig_coef_forest(results: pd.DataFrame, term_filter: list[str],
                      title: str, out_pdf: Path):
    sub = results[results["term"].isin(term_filter)].copy()
    if sub.empty:
        return
    sub = sub.sort_values(["wave", "design", "stratum", "term"])
    sub["label"] = sub.apply(
        lambda r: f"{r['wave']} | {r['design']} | {r['stratum']} | {r['term']} (n={r['n']})",
        axis=1)
    rows = list(zip(sub["coef"], sub["se"], sub["label"]))
    fig, ax = plt.subplots(figsize=(8.0, 0.30 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=7)
    ax.set_xlabel("OLS β (HC1, 95 % CI)")
    ax.set_title(title)
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


# ------------------------------------------------------------------ #
# Driver
# ------------------------------------------------------------------ #

def main() -> int:
    all_results, all_desc = [], []
    for wave in ("2014", "2020"):
        print(f"loading {wave} dyads …")
        df = load_dyads(wave)
        n_with_both = int(df[["mother_ideation", "father_ideation"]].notna().all(axis=1).sum())
        print(f"  n_adults = {len(df)}; both-parent-ideation dyads = {n_with_both}")
        desc = descriptive(df, wave); all_desc.append(desc)
        rowsA = part_A_child_ols(df, wave); all_results.append(rowsA)
        rowsB = part_B_sibling_diff(df, wave); all_results.append(rowsB)
    desc_all = pd.concat(all_desc, ignore_index=True)
    desc_all.to_csv(RUN / "01_descriptive_table.csv", index=False)
    res_all = pd.concat(all_results, ignore_index=True)
    res_all.to_csv(RUN / "04_result_table.csv", index=False)
    # missing
    miss = []
    for wave in ("2014", "2020"):
        df = load_dyads(wave)
        miss.append(dict(wave=wave, n_adults=len(df),
                         n_with_mother_id=int(df["mother_ideation"].notna().sum()),
                         n_with_father_id=int(df["father_ideation"].notna().sum()),
                         n_with_both=int(df[["mother_ideation","father_ideation"]].notna().all(axis=1).sum()),
                         n_with_edu_yrs=int(df["edu_yrs"].notna().sum())))
    pd.DataFrame(miss).to_csv(RUN / "02_missing_table.csv", index=False)
    print("tables written.")

    # figures
    for wave in ("2014", "2020"):
        dsub = desc_all[desc_all["wave"] == wave]
        fig_edu_by_parent_tertile(dsub, FIGS / f"edu_by_parent_tertile_{wave}.pdf")
    fig_coef_forest(res_all,
                     ["mother_ideation", "father_ideation",
                      "mother_id_x_female", "father_id_x_female"],
                     "Parent ideation effects on child edu_yrs (HC1, 95 % CI)",
                     FIGS / "coef_forest_parent_ideation.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
