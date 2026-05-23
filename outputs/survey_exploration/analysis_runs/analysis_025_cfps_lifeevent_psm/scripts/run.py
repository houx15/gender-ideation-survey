#!/usr/bin/env python3
"""analysis_025 — PSM-DiD on CFPS life events.

For each binary event × sex stratum, estimate the average treatment
effect on the treated (ATT) of the event on Δideation, after matching
treated units to controls on baseline 2014 characteristics.  Matching
restricts the control pool to the relevant at-risk subsample (e.g. for
`entered_marriage`, controls must have been never-married or cohab in
2014), so the comparison is "what would Δideation look like for an
event-1 person if they had instead remained event-0".

This is PSM with Δideation as the outcome, which makes it a PSM-DiD:
time-invariant per-person heterogeneity is absorbed by the Δ, and
observable baseline differences between treated and control are
absorbed by the matching.

Outputs:
  tables/psm_att.csv        — ATT, bootstrap SE, 95% CI per fit
  tables/psm_balance.csv    — SMD pre/post matching, per covariate per fit
  tables/psm_meta.csv       — sample sizes
  figures/psm_att_forest.pdf — ATT forest, events × sex
  figures/psm_balance.pdf    — pre/post SMD diagnostic plot
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = ROOT / "outputs" / "survey_exploration" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import cfps_panel as CP      # noqa: E402
import matching as PSM       # noqa: E402

HERE = Path(__file__).resolve().parents[1]
TBL = HERE / "tables"
FIG = HERE / "figures"
TBL.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Treatment / control / covariate specifications per event.
# ---------------------------------------------------------------------------

# Common baseline covariates (kept short to preserve sample size).
BASE_COVS = ["ideation_2014", "birthy_2014", "edu_yrs_2014",
             "income_2014_log", "urban_2014"]

# Per-event configuration: how to define the at-risk pool, the treatment
# indicator within that pool, and any event-specific extra covariates.
SPECS = {
    "entered_marriage": {
        "label": "Entered marriage",
        # At-risk: marital_2014 ∈ {1, 3} (never-married or cohab)
        "at_risk": lambda p: p["marital_2014"].isin([1, 3]),
        "treat":   lambda p: (p["entered_marriage"] == 1).astype("float64"),
        "extra_covs": ["marital_2014"],  # 1=never vs 3=cohab matter
    },
    "had_new_child": {
        "label": "Had a new child (rostered)",
        # At-risk: fertile-age window
        "at_risk": lambda p: (
            ((p["female"] == 1) & (p["age_2014"] <= 45)) |
            ((p["female"] == 0) & (p["age_2014"] <= 55))
        ),
        "treat":   lambda p: (p["had_new_child"] == 1).astype("float64"),
        "extra_covs": ["children_n_2014"],
    },
    "divorced": {
        "label": "Got divorced",
        "at_risk": lambda p: p["marital_2014"].isin([2, 3]),
        "treat":   lambda p: (p["divorced"] == 1).astype("float64"),
        "extra_covs": ["marital_2014"],
    },
    "widowed": {
        "label": "Widowed",
        "at_risk": lambda p: p["marital_2014"].isin([2, 3]),
        "treat":   lambda p: (p["widowed"] == 1).astype("float64"),
        "extra_covs": ["marital_2014"],
    },
    "lost_job": {
        "label": "Lost / left job",
        "at_risk": lambda p: p["employed_2014"] == 1,
        "treat":   lambda p: (p["lost_job"] == 1).astype("float64"),
        "extra_covs": [],
    },
    "entered_work": {
        "label": "Entered work",
        "at_risk": lambda p: p["employed_2014"] == 0,
        "treat":   lambda p: (p["entered_work"] == 1).astype("float64"),
        "extra_covs": [],
    },
}

SEX_STRATA = [("male", 0.0), ("female", 1.0)]


def _prepare(p: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns the propensity model uses."""
    out = p.copy()
    out["age_2014"] = 2014 - out["birthy_2014"]
    # log income (income_2014 + 1, then log10)
    out["income_2014_log"] = np.log10(out["income_2014"].clip(lower=0) + 1)
    return out


def _smd_table(pre_df: pd.DataFrame, post_df: pd.DataFrame,
               treat_col: str, covs: list[str]) -> pd.DataFrame:
    """SMD per covariate, pre-match and post-match.

    pre_df:  the at-risk pool before matching (treated + all eligible controls).
    post_df: a DataFrame of length 2 * n_matched, alternating treated/control.
    """
    rows = []
    pre_t  = pre_df[pre_df[treat_col] == 1]
    pre_c  = pre_df[pre_df[treat_col] == 0]
    post_t = post_df[post_df[treat_col] == 1]
    post_c = post_df[post_df[treat_col] == 0]
    for cv in covs:
        rows.append({
            "covariate": cv,
            "smd_pre":  PSM.standardised_mean_difference(pre_t[cv], pre_c[cv]),
            "smd_post": PSM.standardised_mean_difference(post_t[cv], post_c[cv]),
            "n_treated_pre":  int(pre_t[cv].notna().sum()),
            "n_control_pre":  int(pre_c[cv].notna().sum()),
            "n_treated_post": int(post_t[cv].notna().sum()),
            "n_control_post": int(post_c[cv].notna().sum()),
        })
    return pd.DataFrame(rows)


def _run_one(p: pd.DataFrame, event: str, sex_name: str, sex_val: float,
             n_boot: int = 300) -> tuple[dict, pd.DataFrame]:
    """One ATT fit + balance table."""
    spec = SPECS[event]
    mask = (p["female"] == sex_val) & spec["at_risk"](p)
    pool = p[mask].copy()
    pool["treat"] = spec["treat"](pool)
    covs = BASE_COVS + spec["extra_covs"]
    work = pool[["treat", "delta_ideation"] + covs].dropna()

    n_treated = int((work["treat"] == 1).sum())
    n_control = int((work["treat"] == 0).sum())
    if n_treated < 10 or n_control < 10:
        return ({
            "event": event, "sex": sex_name, "label": spec["label"],
            "n_treated": n_treated, "n_control": n_control,
            "att": float("nan"), "boot_se": float("nan"), "p": float("nan"),
            "ci_lo": float("nan"), "ci_hi": float("nan"),
            "n_boot": 0, "note": "insufficient sample",
        }, pd.DataFrame())

    res = PSM.psm_att_boot(work, "treat", "delta_ideation",
                           covs, n_boot=n_boot, seed=0)
    diag = PSM.psm_diagnostic(work, "treat", covs)

    # Build post-match comparison frame (parallel treated/control rows).
    d = work.dropna().reset_index(drop=True)
    post_df = pd.concat([
        d.iloc[diag["treated_idx"]].assign(_role="treated"),
        d.iloc[diag["matched_control_idx"]].assign(_role="control"),
    ], ignore_index=True)
    bal = _smd_table(work, post_df, "treat", covs)
    bal.insert(0, "event", event)
    bal.insert(1, "sex", sex_name)

    summary = {
        "event": event, "sex": sex_name, "label": spec["label"],
        "n_treated": n_treated, "n_control": n_control,
        "att": res["att"], "boot_se": res["boot_se"],
        "p": res["p"], "ci_lo": res["ci_lo"], "ci_hi": res["ci_hi"],
        "n_boot": res["n_boot"], "note": "",
    }
    return summary, bal


def main(n_boot: int = 300) -> None:
    panel_path = (ROOT / "outputs" / "survey_exploration" / "analysis_runs" /
                  "analysis_024_cfps_ideation_change" / "tables" / "panel.parquet")
    p = pd.read_parquet(panel_path)
    p = _prepare(p)

    att_rows, bal_frames = [], []
    for event in SPECS:
        for sex_name, sex_val in SEX_STRATA:
            summary, bal = _run_one(p, event, sex_name, sex_val,
                                    n_boot=n_boot)
            att_rows.append(summary)
            if not bal.empty:
                bal_frames.append(bal)
            print(f"  {event:18s} {sex_name:6s}  "
                  f"n_t={summary['n_treated']:5d}  "
                  f"ATT={summary['att']:+.4f}  "
                  f"SE={summary['boot_se']:.4f}  "
                  f"p={summary['p']:.3g}")

    att_df = pd.DataFrame(att_rows)
    att_df.to_csv(TBL / "psm_att.csv", index=False)

    bal_df = pd.concat(bal_frames, ignore_index=True) if bal_frames else pd.DataFrame()
    bal_df.to_csv(TBL / "psm_balance.csv", index=False)

    pd.DataFrame([{
        "n_panel": int(len(p)),
        "n_with_delta": int(p["delta_ideation"].notna().sum()),
        "n_fits": int(len(att_df)),
        "n_boot": int(n_boot),
    }]).to_csv(TBL / "psm_meta.csv", index=False)

    _att_forest(att_df)
    if not bal_df.empty:
        _balance_plot(bal_df)
    print(f"DONE  fits = {len(att_df)}  bootstrap rounds = {n_boot}")


def _att_forest(att: pd.DataFrame) -> None:
    """Forest of ATTs, events on Y, male/female overlaid."""
    events = list(SPECS.keys())
    label_of = {k: v["label"] for k, v in SPECS.items()}
    sex_colours = {"male": "#117755", "female": "#aa4422"}
    sex_marker  = {"male": "o", "female": "s"}

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    y_base = np.arange(len(events))[::-1].astype(float)
    for sex_name in ("male", "female"):
        sub = att[att.sex == sex_name].set_index("event").reindex(events).reset_index()
        ys = y_base + (0.18 if sex_name == "male" else -0.18)
        valid = sub["att"].notna()
        ax.errorbar(sub.loc[valid, "att"], ys[valid.values],
                    xerr=[(sub.loc[valid, "att"] - sub.loc[valid, "ci_lo"]).values,
                          (sub.loc[valid, "ci_hi"] - sub.loc[valid, "att"]).values],
                    fmt=sex_marker[sex_name], color=sex_colours[sex_name],
                    capsize=3, label=sex_name.capitalize())

    ax.axvline(0, color="black", lw=0.6)
    tick_labels = []
    for e in events:
        m = att[(att.event == e) & (att.sex == "male")]
        f = att[(att.event == e) & (att.sex == "female")]
        m_n = int(m["n_treated"].iloc[0]) if not m.empty else 0
        f_n = int(f["n_treated"].iloc[0]) if not f.empty else 0
        tick_labels.append(f"{label_of[e]}\n(M n_treated={m_n:,}; F n_treated={f_n:,})")
    ax.set_yticks(y_base)
    ax.set_yticklabels(tick_labels)
    ax.set_xlabel("PSM-DiD ATT on Δideation (95% bootstrap CI)\n"
                  "negative = event causes a progressive shift (under unconfoundedness)")
    ax.set_title("PSM-DiD ATT, by event × sex — CFPS 2014→2020")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "psm_att_forest.pdf")
    plt.close(fig)


def _balance_plot(bal: pd.DataFrame) -> None:
    """Pre vs post SMDs across all fits, in one balance dotplot."""
    bal = bal.assign(fit=lambda d: d["event"] + " · " + d["sex"])
    fig, ax = plt.subplots(figsize=(7.4, max(4.0, 0.25 * len(bal))))
    y = np.arange(len(bal))[::-1]
    ax.scatter(bal["smd_pre"].abs(), y, marker="o",
               color="#888888", s=25, label="pre-matching |SMD|")
    ax.scatter(bal["smd_post"].abs(), y, marker="s",
               color="#264478", s=25, label="post-matching |SMD|")
    for yi, (_, r) in zip(y, bal.iterrows()):
        ax.plot([abs(r["smd_pre"]), abs(r["smd_post"])], [yi, yi],
                color="0.7", lw=0.8, zorder=0)
    ax.axvline(0.1, color="firebrick", ls="--", lw=0.6,
               label="Cohen 0.1 rule-of-thumb")
    ax.set_yticks(y)
    ax.set_yticklabels(bal["fit"] + " · " + bal["covariate"], fontsize=7)
    ax.set_xlabel("|standardised mean difference| between treated and control")
    ax.set_title("PSM balance diagnostics — covariate × fit")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "psm_balance.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main(n_boot=300)
