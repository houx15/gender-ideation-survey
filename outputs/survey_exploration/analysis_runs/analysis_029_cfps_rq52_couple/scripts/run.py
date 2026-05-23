#!/usr/bin/env python3
"""analysis_029 v2 — RQ 5.2 family-level couple analysis (deep).

Four parts:
  A. Ideology-axis homogamy
       - within-couple Pearson r, overall + by cohort / urban / edu
       - OLS-HC1: wife_ideation ~ husband_ideation + couple controls
  A2. (v2 addition) Sociological matching TYPES and ideation
       - Build age / edu / income match types (hyper / homo / hypogamy)
       - LPM-HC1 of each type on wife_ideation and husband_ideation
  B. Whose ideology drives the division
       - dyadic OLS on wife_housework ~ wife_ideation + husband_ideation
         + spouse covariates  (and analog for husband)
       - same for childcare (2020 qq9013)
  C. Marriage satisfaction by ideation gap / typology
       - OLS-HC1: wife/husband qm801 on |wife - husband| ideation gap
       - ideology typology comparison (concordant-prog / concordant-trad
         / W>M / M>W)

Frames: 2014 and 2020 cross-sections (no lagged — couples are the unit).
All HC1; vector PDF figures.
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
import cfps_linkage as K           # noqa: E402
import stats_helpers as ST         # noqa: E402

import pyreadstat                  # noqa: E402

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9


# ------------------------------------------------------------------ #
# 0. Loaders
# ------------------------------------------------------------------ #

def _attach_2020_spouse_pid(df20: pd.DataFrame) -> pd.DataFrame:
    """Merge spouse pid (pid_a_s) from cfps2020_famconf onto adult frame."""
    famconf, _ = pyreadstat.read_dta(
        str(L.ROOT / "surveys" / "CFPS" / "cfps2020_famconf.dta"),
        usecols=["pid", "pid_a_s"])
    famconf = famconf.rename(columns={"pid_a_s": "pid_s"})
    famconf = famconf.drop_duplicates(subset=["pid"], keep="first")
    return df20.merge(famconf, on="pid", how="left")


def _load_adult_with_outcomes(wave: str) -> pd.DataFrame:
    cfg = L.SURVEYS[("CFPS", wave)]
    extras_common = ["pid", "qea0", "qq9010" if wave == "2014" else "qq9010n",
                     "qm801", cfg["gender_var"], "income" if wave == "2014" else "emp_income",
                     "qa301"]
    if wave == "2014":
        extras = extras_common + ["pid_s", "cfps_birthy", "cfps2014eduy_im"]
    else:
        extras = extras_common + ["ibirthy", "cfps2020eduy_im", "qq9013"]
    df, _m, _norm, idx = L.load_recoded(
        "CFPS", wave, extra_cols=[c for c in extras if c not in cfg["items"]])
    df = df[df["n_valid_items"] >= 1].copy()
    df = df.rename(columns={idx: "ideation"})
    if wave == "2014":
        df["birthy"]  = pd.to_numeric(df["cfps_birthy"], errors="coerce").where(
            lambda x: x.between(1920, 2007))
        df["age"]     = 2014 - df["birthy"]
        df["edu_yrs"] = pd.to_numeric(df["cfps2014eduy_im"], errors="coerce").where(
            lambda x: x.between(0, 22))
        df["housework_hours"] = C.housework_hours_daily(df["qq9010"])
        df["childcare_hours"] = np.nan
        df["income"] = P._to_numeric_nan_sentinels(df["income"]).where(lambda x: x >= 0)
    else:
        df = _attach_2020_spouse_pid(df)
        df["birthy"]  = pd.to_numeric(df["ibirthy"], errors="coerce").where(
            lambda x: x.between(1920, 2010))
        df["age"]     = 2020 - df["birthy"]
        df["edu_yrs"] = pd.to_numeric(df["cfps2020eduy_im"], errors="coerce").where(
            lambda x: x.between(0, 22))
        df["housework_hours"] = C.housework_hours_daily(df["qq9010n"])
        df["childcare_hours"] = C.housework_hours_daily(df["qq9013"])
        df["income"] = P._to_numeric_nan_sentinels(df["emp_income"]).where(lambda x: x >= 0)
    df["log_income"] = np.log1p(df["income"])
    df["marriage_sat"] = C.clean_continuous(
        pd.to_numeric(df["qm801"], errors="coerce"), lo=1, hi=5)
    hk = pd.to_numeric(df["qa301"], errors="coerce")
    df["urban"] = np.where(hk == 1, 0.0,
                            np.where(hk == 3, 1.0,
                                      np.where(hk == 7, 1.0, np.nan)))
    return df


def load_couples(wave: str) -> pd.DataFrame:
    """Return one row per heterosexual couple with wife/husband ideation,
    housework, childcare (2020 only), edu, age, log_income, urban, marriage_sat."""
    df = _load_adult_with_outcomes(wave)
    df = df[df["pid_s"].notna() & (df["pid_s"] != 0)].copy()
    couples = K.build_couples(
        df, pid_col="pid", spouse_col="pid_s", female_col="female",
        value_cols=["ideation", "age", "edu_yrs", "log_income", "urban",
                    "housework_hours", "childcare_hours", "marriage_sat",
                    "birthy"])
    couples["gap_ideation"] = (couples["wife_ideation"] - couples["husband_ideation"]).abs()
    couples["wife_more_traditional"] = (couples["wife_ideation"] > couples["husband_ideation"]).astype(float)
    # typology by terciles applied JOINTLY to each spouse:
    return couples


# ------------------------------------------------------------------ #
# 1. Part A — assortative mating
# ------------------------------------------------------------------ #

def part_A_correlations(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    """Within-couple Pearson r of ideation, overall and by cohort / urban / edu."""
    rows = []
    valid = couples.dropna(subset=["wife_ideation", "husband_ideation"])
    rows.append(dict(wave=wave, subgroup="all", n=len(valid),
                     pearson_r=round(float(valid["wife_ideation"].corr(valid["husband_ideation"])), 4)))
    # by wife birth decade
    valid_d = valid.copy()
    valid_d["decade"] = (valid_d["wife_birthy"] // 10 * 10).astype("Int64")
    for decade, g in valid_d.dropna(subset=["decade"]).groupby("decade"):
        if len(g) < 30:
            continue
        rows.append(dict(wave=wave, subgroup=f"wife_birth_decade={int(decade)}",
                         n=len(g),
                         pearson_r=round(float(g["wife_ideation"].corr(g["husband_ideation"])), 4)))
    # by couple-level urban (either spouse urban)
    valid_u = valid.copy()
    valid_u["couple_urban"] = ((valid_u["wife_urban"] == 1) | (valid_u["husband_urban"] == 1)).astype(int)
    for u, g in valid_u.groupby("couple_urban"):
        if len(g) < 30:
            continue
        rows.append(dict(wave=wave, subgroup=f"couple_urban={u}",
                         n=len(g),
                         pearson_r=round(float(g["wife_ideation"].corr(g["husband_ideation"])), 4)))
    # by wife edu category (low / mid / high tertile by edu_yrs)
    if valid["wife_edu_yrs"].notna().sum() > 100:
        q = valid["wife_edu_yrs"].quantile([1/3, 2/3]).values
        valid["wife_edu_t"] = pd.cut(valid["wife_edu_yrs"],
                                      [-np.inf, q[0], q[1], np.inf],
                                      labels=["low", "mid", "high"])
        for t, g in valid.dropna(subset=["wife_edu_t"]).groupby("wife_edu_t", observed=True):
            if len(g) < 30:
                continue
            rows.append(dict(wave=wave, subgroup=f"wife_edu_tertile={t}",
                             n=len(g),
                             pearson_r=round(float(g["wife_ideation"].corr(g["husband_ideation"])), 4)))
    return pd.DataFrame(rows)


def part_A_rank_rank(couples: pd.DataFrame, wave: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """v3 (2026-05-23): rank-rank measures of ideology homogamy.

    For each spouse, compute the sex-specific percentile rank of ideation
    (so the level shift between wives' and husbands' distributions is removed).
    Returns:
      - per-subgroup table of Spearman ρ + rank-rank OLS slope
      - the per-couple frame with rank columns, for use in figures
    """
    valid = couples.dropna(subset=["wife_ideation", "husband_ideation"]).copy()
    if len(valid) < 30:
        return pd.DataFrame(), valid
    valid["wife_rank"]    = valid["wife_ideation"].rank(pct=True)
    valid["husband_rank"] = valid["husband_ideation"].rank(pct=True)
    # rank-rank regression slope (= Spearman ρ when both ranks are uniform)
    summary_rows = []
    def _summarize(g: pd.DataFrame, subgroup: str):
        if len(g) < 30:
            return
        rho = float(g["wife_ideation"].corr(g["husband_ideation"], method="spearman"))
        # rank-rank OLS slope: cov(wife_rank, husband_rank) / var(husband_rank)
        b = float(g["wife_rank"].cov(g["husband_rank"]) / g["husband_rank"].var(ddof=1))
        summary_rows.append(dict(wave=wave, subgroup=subgroup, n=len(g),
                                   spearman_rho=round(rho, 4),
                                   rank_rank_slope=round(b, 4)))
    _summarize(valid, "all")
    # by wife birth decade
    valid["decade"] = (valid["wife_birthy"] // 10 * 10).astype("Int64")
    for decade, g in valid.dropna(subset=["decade"]).groupby("decade"):
        _summarize(g, f"wife_birth_decade={int(decade)}")
    # by couple urban
    valid["couple_urban"] = ((valid["wife_urban"] == 1) | (valid["husband_urban"] == 1)).astype(int)
    for u, g in valid.groupby("couple_urban"):
        _summarize(g, f"couple_urban={u}")
    # by wife edu tertile
    if valid["wife_edu_yrs"].notna().sum() > 100:
        q = valid["wife_edu_yrs"].quantile([1 / 3, 2 / 3]).values
        valid["wife_edu_t"] = pd.cut(valid["wife_edu_yrs"],
                                       [-np.inf, q[0], q[1], np.inf],
                                       labels=["low", "mid", "high"])
        for t, g in valid.dropna(subset=["wife_edu_t"]).groupby("wife_edu_t",
                                                                  observed=True):
            _summarize(g, f"wife_edu_tertile={t}")
    return pd.DataFrame(summary_rows), valid


def part_A_regression(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    """OLS-HC1: wife_ideation ~ husband_ideation + couple controls.

    A significant positive husband_ideation coefficient, after controls,
    is the ideology-based-assortment estimate.
    """
    d = couples.dropna(subset=["wife_ideation", "husband_ideation",
                                "wife_age", "husband_age",
                                "wife_edu_yrs", "husband_edu_yrs",
                                "wife_urban", "husband_urban"]).copy()
    if len(d) < 100:
        return pd.DataFrame()
    d["wife_age_c"]    = (d["wife_age"]    - 40) / 10
    d["husband_age_c"] = (d["husband_age"] - 40) / 10
    d["couple_urban"] = ((d["wife_urban"] == 1) | (d["husband_urban"] == 1)).astype(float)
    rows = []
    for outcome in ["wife_ideation", "husband_ideation"]:
        partner = "husband_ideation" if outcome == "wife_ideation" else "wife_ideation"
        X = pd.DataFrame({
            "const":            1.0,
            partner:            d[partner].astype(float),
            "wife_age_c":       d["wife_age_c"].astype(float),
            "husband_age_c":    d["husband_age_c"].astype(float),
            "wife_edu_yrs":     d["wife_edu_yrs"].astype(float),
            "husband_edu_yrs":  d["husband_edu_yrs"].astype(float),
            "couple_urban":     d["couple_urban"].astype(float),
        })
        y = d[outcome].to_numpy()
        keep = X.notna().all(axis=1)
        Xk, yk = X.loc[keep], y[keep.values]
        try:
            r = ST.ols_robust(Xk, yk, kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, c, se, t, p in zip(r["term"], r["coef"], r["se"],
                                       r["t"], r["p"]):
            rows.append(dict(wave=wave, outcome=outcome, n=int(r["n"]),
                             term=term,
                             coef=round(float(c), 5), se=round(float(se), 5),
                             t=round(float(t), 3), p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 1b. Part A2 — sociological matching types and ideation (v2)
# ------------------------------------------------------------------ #

# Thresholds chosen to align with the marriage-homogamy literature:
#   age:  >=3 yr difference  -> hyper / hypogamy; <3 -> homogamy
#   edu:  >=3 yr difference  -> hyper / hypogamy (~ one schooling level)
#   inc:  log1p_husband_income - log1p_wife_income;
#         |diff| >= log(2) -> primary-earner side; else dual-earner
#         (log(2) ~ 0.69 — husband earns >= 2x wife counts as hypergamy)
#
# Convention: "hypergamy" = woman married UP on this trait (older / more
# educated / higher-earning husband, the patriarchal default).
#             "homogamy" = within threshold.
#             "hypogamy" = woman married DOWN (younger / less-educated /
# lower-earning husband).

_AGE_THRESHOLD = 3.0     # years
_EDU_THRESHOLD = 3.0     # years (~ one schooling level)
_INC_THRESHOLD = np.log(2)


def _age_match_type(couples: pd.DataFrame) -> pd.Series:
    diff = couples["husband_age"] - couples["wife_age"]
    out = pd.Series(np.nan, index=couples.index, dtype="object")
    out[diff >=  _AGE_THRESHOLD] = "hypergamy"   # husband ≥ wife+3 (older husband)
    out[diff.abs() <  _AGE_THRESHOLD] = "homogamy"
    out[diff <= -_AGE_THRESHOLD] = "hypogamy"    # wife ≥ husband+3 (older wife)
    out[diff.isna()] = np.nan
    return out


def _edu_match_type(couples: pd.DataFrame) -> pd.Series:
    diff = couples["husband_edu_yrs"] - couples["wife_edu_yrs"]
    out = pd.Series(np.nan, index=couples.index, dtype="object")
    out[diff >=  _EDU_THRESHOLD] = "hypergamy"   # husband more educated
    out[diff.abs() <  _EDU_THRESHOLD] = "homogamy"
    out[diff <= -_EDU_THRESHOLD] = "hypogamy"    # wife more educated
    out[diff.isna()] = np.nan
    return out


def _income_match_type(couples: pd.DataFrame) -> pd.Series:
    """husband_primary if log1p(h_inc) - log1p(w_inc) >= log(2);
       wife_primary if reverse; dual_earner otherwise.

       Note: log1p(0) = 0 so a wife with no earned income contributes
       husband_primary automatically. Same for a husband with 0 income.
    """
    diff = couples["husband_log_income"] - couples["wife_log_income"]
    out = pd.Series(np.nan, index=couples.index, dtype="object")
    out[diff >=  _INC_THRESHOLD] = "hypergamy"   # husband-primary earner
    out[diff.abs() <  _INC_THRESHOLD] = "homogamy"  # dual-earner-ish
    out[diff <= -_INC_THRESHOLD] = "hypogamy"    # wife-primary earner
    out[diff.isna()] = np.nan
    return out


def part_A2_descriptive(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    """Cross-tab of match type × ideation tertile, for each dimension and
    each spouse (wife and husband ideation tertile)."""
    c = couples.copy()
    c["age_type"]   = _age_match_type(c)
    c["edu_type"]   = _edu_match_type(c)
    c["inc_type"]   = _income_match_type(c)

    def tertile(s):
        q = s.quantile([1 / 3, 2 / 3]).values
        return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])

    c["wife_id_t"]    = tertile(c["wife_ideation"])
    c["husband_id_t"] = tertile(c["husband_ideation"])

    rows = []
    for dim, type_col in [("age", "age_type"), ("edu", "edu_type"), ("inc", "inc_type")]:
        for who, tcol in [("wife", "wife_id_t"), ("husband", "husband_id_t")]:
            sub = c.dropna(subset=[type_col, tcol])
            for tertile_v in ["low", "mid", "high"]:
                g = sub[sub[tcol] == tertile_v]
                total = len(g)
                if total < 30:
                    continue
                for t in ["hypergamy", "homogamy", "hypogamy"]:
                    n = int((g[type_col] == t).sum())
                    rows.append(dict(wave=wave, dimension=dim,
                                     ideation_predictor=who,
                                     ideation_tertile=tertile_v,
                                     match_type=t,
                                     n=n, n_in_tertile=total,
                                     pct=round(100 * n / total, 2)))
    return pd.DataFrame(rows)


def part_A2_regression(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    """LPM-HC1 per type-dummy on wife_ideation and husband_ideation, with
    couple controls. One row per (dimension, type, spouse-predictor, term).
    """
    base_cols = ["wife_ideation", "husband_ideation",
                 "wife_age", "husband_age",
                 "wife_edu_yrs", "husband_edu_yrs",
                 "wife_urban", "husband_urban"]
    c = couples.dropna(subset=base_cols).copy()
    if len(c) < 100:
        return pd.DataFrame()

    c["age_type"]   = _age_match_type(c)
    c["edu_type"]   = _edu_match_type(c)
    c["inc_type"]   = _income_match_type(c)
    c["wife_age_c"]    = (c["wife_age"]    - 40) / 10
    c["husband_age_c"] = (c["husband_age"] - 40) / 10
    c["couple_urban"]  = ((c["wife_urban"] == 1) | (c["husband_urban"] == 1)).astype(float)

    rows = []
    for dim, type_col in [("age", "age_type"), ("edu", "edu_type"), ("inc", "inc_type")]:
        sub = c.dropna(subset=[type_col]).copy()
        if len(sub) < 100:
            continue
        for match_type in ["hypergamy", "homogamy", "hypogamy"]:
            y = (sub[type_col] == match_type).astype(float).to_numpy()
            for predictor in ["wife_ideation", "husband_ideation"]:
                # Note: do NOT control on the partner's ideation here so the
                # estimate is the marginal "does THIS spouse's ideation
                # predict this match type" (the question of interest).
                # For age type we drop the age controls (collinearity with
                # the outcome by construction).
                #   Similarly for edu type we drop edu controls.
                ctrl_age = (dim != "age")
                ctrl_edu = (dim != "edu")
                X_dict = {"const": 1.0, predictor: sub[predictor].astype(float)}
                if ctrl_age:
                    X_dict["wife_age_c"]    = sub["wife_age_c"].astype(float)
                    X_dict["husband_age_c"] = sub["husband_age_c"].astype(float)
                if ctrl_edu:
                    X_dict["wife_edu_yrs"]    = sub["wife_edu_yrs"].astype(float)
                    X_dict["husband_edu_yrs"] = sub["husband_edu_yrs"].astype(float)
                X_dict["couple_urban"] = sub["couple_urban"].astype(float)
                X = pd.DataFrame(X_dict)
                keep = X.notna().all(axis=1) & ~np.isnan(y)
                Xk, yk = X.loc[keep], y[keep.values]
                if len(Xk) < (Xk.shape[1] + 2):
                    continue
                try:
                    r = ST.ols_robust(Xk, yk, kind="HC1")
                except np.linalg.LinAlgError:
                    continue
                for term, coef, se, t, p in zip(r["term"], r["coef"], r["se"],
                                                  r["t"], r["p"]):
                    if term != predictor:
                        continue  # only keep the ideation coefficient
                    rows.append(dict(wave=wave, dimension=dim,
                                     match_type=match_type,
                                     predictor=predictor,
                                     n=int(r["n"]),
                                     coef=round(float(coef), 5),
                                     se=round(float(se), 5),
                                     t=round(float(t), 3),
                                     p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 2. Part B — whose ideology drives the division
# ------------------------------------------------------------------ #

def part_B_dyadic(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    """Dyadic OLS-HC1 on wife/husband housework + childcare, with both
    spouses' ideation on the RHS plus full couple controls.
    """
    base_cols = ["wife_ideation", "husband_ideation",
                 "wife_age", "husband_age",
                 "wife_edu_yrs", "husband_edu_yrs",
                 "wife_urban", "husband_urban",
                 "wife_log_income", "husband_log_income"]
    d = couples.dropna(subset=base_cols).copy()
    d["wife_age_c"]    = (d["wife_age"]    - 40) / 10
    d["husband_age_c"] = (d["husband_age"] - 40) / 10
    d["couple_urban"]  = ((d["wife_urban"] == 1) | (d["husband_urban"] == 1)).astype(float)
    if len(d) < 100:
        return pd.DataFrame()
    rows = []
    outcomes = ["wife_housework_hours", "husband_housework_hours"]
    if wave == "2020":
        outcomes += ["wife_childcare_hours", "husband_childcare_hours"]
    for outcome in outcomes:
        if d[outcome].notna().sum() < 100:
            continue
        X = pd.DataFrame({
            "const":              1.0,
            "wife_ideation":      d["wife_ideation"].astype(float),
            "husband_ideation":   d["husband_ideation"].astype(float),
            "wife_age_c":         d["wife_age_c"].astype(float),
            "husband_age_c":      d["husband_age_c"].astype(float),
            "wife_edu_yrs":       d["wife_edu_yrs"].astype(float),
            "husband_edu_yrs":    d["husband_edu_yrs"].astype(float),
            "wife_log_income":    d["wife_log_income"].astype(float),
            "husband_log_income": d["husband_log_income"].astype(float),
            "couple_urban":       d["couple_urban"].astype(float),
        })
        y = d[outcome].to_numpy()
        keep = X.notna().all(axis=1) & ~np.isnan(y)
        Xk, yk = X.loc[keep], y[keep.values]
        try:
            r = ST.ols_robust(Xk, yk, kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, c, se, t, p in zip(r["term"], r["coef"], r["se"],
                                       r["t"], r["p"]):
            rows.append(dict(wave=wave, outcome=outcome, n=int(r["n"]),
                             term=term,
                             coef=round(float(c), 5), se=round(float(se), 5),
                             t=round(float(t), 3), p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 3. Part C — marriage satisfaction by gap / typology
# ------------------------------------------------------------------ #

def _couple_typology(couples: pd.DataFrame) -> pd.Series:
    """4 buckets vs. median-split on each spouse's ideation:
       both above median   -> concordant_traditional
       both below          -> concordant_progressive
       wife > husband (above median wife) -> woman_more_traditional
       husband > wife (above median husband) -> man_more_traditional
    """
    med_w = couples["wife_ideation"].median()
    med_h = couples["husband_ideation"].median()
    w_high = couples["wife_ideation"] > med_w
    h_high = couples["husband_ideation"] > med_h
    out = pd.Series(np.nan, index=couples.index, dtype="object")
    out[~w_high & ~h_high] = "concordant_progressive"
    out[w_high & h_high]   = "concordant_traditional"
    out[w_high & ~h_high]  = "woman_more_traditional"
    out[~w_high & h_high]  = "man_more_traditional"
    return out


def part_C_satisfaction(couples: pd.DataFrame, wave: str) -> pd.DataFrame:
    d = couples.copy()
    d["typology"] = _couple_typology(d)
    d["wife_age_c"]    = (d["wife_age"]    - 40) / 10
    d["husband_age_c"] = (d["husband_age"] - 40) / 10
    d["couple_urban"]  = ((d["wife_urban"] == 1) | (d["husband_urban"] == 1)).astype(float)
    rows = []
    for outcome in ["wife_marriage_sat", "husband_marriage_sat"]:
        sub = d.dropna(subset=[outcome, "wife_ideation", "husband_ideation",
                                "wife_age", "husband_age",
                                "wife_edu_yrs", "husband_edu_yrs",
                                "gap_ideation", "typology"]).copy()
        if len(sub) < 100:
            continue
        # dummy-encode typology
        for cat in ["concordant_traditional", "woman_more_traditional",
                    "man_more_traditional"]:
            sub[f"typ_{cat}"] = (sub["typology"] == cat).astype(float)
        X = pd.DataFrame({
            "const":            1.0,
            "gap_ideation":     sub["gap_ideation"].astype(float),
            "typ_concordant_traditional": sub["typ_concordant_traditional"].astype(float),
            "typ_woman_more_traditional": sub["typ_woman_more_traditional"].astype(float),
            "typ_man_more_traditional":   sub["typ_man_more_traditional"].astype(float),
            "wife_age_c":       sub["wife_age_c"].astype(float),
            "husband_age_c":    sub["husband_age_c"].astype(float),
            "wife_edu_yrs":     sub["wife_edu_yrs"].astype(float),
            "husband_edu_yrs":  sub["husband_edu_yrs"].astype(float),
            "couple_urban":     sub["couple_urban"].astype(float),
        })
        y = sub[outcome].to_numpy()
        keep = X.notna().all(axis=1)
        Xk, yk = X.loc[keep], y[keep.values]
        try:
            r = ST.ols_robust(Xk, yk, kind="HC1")
        except np.linalg.LinAlgError:
            continue
        for term, c, se, t, p in zip(r["term"], r["coef"], r["se"],
                                       r["t"], r["p"]):
            rows.append(dict(wave=wave, outcome=outcome, n=int(r["n"]),
                             term=term,
                             coef=round(float(c), 5), se=round(float(se), 5),
                             t=round(float(t), 3), p=round(float(p), 5)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ #
# 4. Figures
# ------------------------------------------------------------------ #

def fig_rank_rank_scatter(valid_with_ranks: pd.DataFrame, wave: str,
                            out_pdf: Path):
    """Rank-rank scatter (Chetty-style) of wife vs husband ideology percentile.

    Adds the diagonal (perfect rank assortment) and the OLS slope line.
    """
    d = valid_with_ranks
    if len(d) < 50:
        return
    fig, ax = plt.subplots(figsize=(4.4, 4.4))
    ax.scatter(d["husband_rank"], d["wife_rank"], s=4, alpha=0.25, color="#1f77b4")
    ax.plot([0, 1], [0, 1], "--", color="#888", linewidth=0.7, label="rank diagonal")
    # OLS slope
    b = d["wife_rank"].cov(d["husband_rank"]) / d["husband_rank"].var(ddof=1)
    a = d["wife_rank"].mean() - b * d["husband_rank"].mean()
    xs = np.linspace(0, 1, 100)
    ax.plot(xs, a + b * xs, color="#d62728", linewidth=1.4,
            label=f"rank-rank slope = {b:.3f}")
    rho = d["wife_ideation"].corr(d["husband_ideation"], method="spearman")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Husband ideology percentile")
    ax.set_ylabel("Wife ideology percentile")
    ax.set_title(f"Rank-rank ideology matching — CFPS {wave}\n"
                 f"Spearman ρ = {rho:.3f}  (n = {len(d)})")
    ax.legend(frameon=False, loc="lower right", fontsize=8)
    ax.grid(linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_scatter_couple_ideation(couples: pd.DataFrame, wave: str, out_pdf: Path):
    d = couples.dropna(subset=["wife_ideation", "husband_ideation"])
    if len(d) < 50:
        return
    fig, ax = plt.subplots(figsize=(4.4, 4.4))
    ax.scatter(d["husband_ideation"], d["wife_ideation"],
               s=4, alpha=0.30, color="#1f77b4")
    # 45-degree line
    ax.plot([0, 1], [0, 1], "--", color="#888", linewidth=0.7)
    # OLS slope
    if len(d) >= 10:
        b = d["husband_ideation"].cov(d["wife_ideation"]) / d["husband_ideation"].var(ddof=1)
        a = d["wife_ideation"].mean() - b * d["husband_ideation"].mean()
        xs = np.linspace(0, 1, 100)
        ax.plot(xs, a + b * xs, color="#d62728", linewidth=1.2, label=f"OLS slope = {b:.2f}")
    r = float(d["wife_ideation"].corr(d["husband_ideation"]))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Husband ideation"); ax.set_ylabel("Wife ideation")
    ax.set_title(f"Couple ideation matching — CFPS {wave}\nPearson r = {r:.3f}  (n = {len(d)})")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_dyadic_coef_forest(results: pd.DataFrame, out_pdf: Path, wave: str):
    """For each (outcome, ideation term), show coef ± 1.96·SE."""
    interest = results[results["term"].isin(["wife_ideation", "husband_ideation"])].copy()
    if interest.empty:
        return
    interest["label"] = interest.apply(
        lambda r: f"{r['outcome']} · {r['term']} (n={r['n']})", axis=1)
    interest = interest.sort_values(["outcome", "term"])
    rows = list(zip(interest["coef"], interest["se"], interest["label"]))
    fig, ax = plt.subplots(figsize=(7.0, 0.32 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=8)
    ax.set_xlabel("β on partner-ideation (HC1, 95 % CI)")
    ax.set_title(f"Whose ideology drives the division — CFPS {wave}")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_match_type_by_ideation(couples: pd.DataFrame, wave: str, out_pdf: Path):
    """Stacked-bar of match type composition by ideation tertile, for each
    of (age, edu, income), shown separately for wife's ideation and husband's.
    6 panels (3 dimensions × 2 sex-predictors)."""
    c = couples.copy()
    c["age_type"] = _age_match_type(c)
    c["edu_type"] = _edu_match_type(c)
    c["inc_type"] = _income_match_type(c)

    def tertile(s):
        q = s.quantile([1 / 3, 2 / 3]).values
        return pd.cut(s, [-np.inf, q[0], q[1], np.inf], labels=["low", "mid", "high"])

    c["wife_id_t"]    = tertile(c["wife_ideation"])
    c["husband_id_t"] = tertile(c["husband_ideation"])

    fig, axes = plt.subplots(3, 2, figsize=(8.8, 8.4))
    type_order = ["hypergamy", "homogamy", "hypogamy"]
    type_colors = {"hypergamy": "#d73027", "homogamy": "#999",
                   "hypogamy":  "#1a9850"}
    dim_label = {"age": "Age",
                 "edu": "Education",
                 "inc": "Income"}
    for col, (predictor, tcol) in enumerate([("wife", "wife_id_t"),
                                              ("husband", "husband_id_t")]):
        for row, dim in enumerate(["age", "edu", "inc"]):
            ax = axes[row, col]
            type_col = f"{dim}_type"
            tertiles = ["low", "mid", "high"]
            bottoms = np.zeros(3)
            for t in type_order:
                vals = []
                for ti in tertiles:
                    g = c[(c[tcol] == ti) & c[type_col].notna()]
                    if len(g) == 0:
                        vals.append(0.0)
                    else:
                        vals.append(100 * (g[type_col] == t).mean())
                ax.bar(range(3), vals, bottom=bottoms, color=type_colors[t],
                       label=t, edgecolor="white", linewidth=0.5)
                bottoms += np.array(vals)
            ax.set_xticks(range(3))
            ax.set_xticklabels(["low\n(progr.)", "mid", "high\n(trad.)"], fontsize=8)
            ax.set_ylim(0, 100)
            ax.set_title(f"{dim_label[dim]} match | {predictor}'s ideation",
                         fontsize=9)
            if col == 0:
                ax.set_ylabel("% of couples")
            ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    # one legend
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(f"Sociological matching type composition by ideation tertile — CFPS {wave}",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(out_pdf)
    plt.close(fig)


def fig_match_type_coef_forest(results: pd.DataFrame, wave: str, out_pdf: Path):
    """Combined forest across all dimensions — kept for backward-compat."""
    sub = results[results["wave"] == wave].copy()
    if sub.empty:
        return
    sub["label"] = sub.apply(
        lambda r: f"{r['dimension']} {r['match_type']} | {r['predictor']} (n={r['n']})",
        axis=1)
    sub = sub.sort_values(["dimension", "match_type", "predictor"])
    rows = list(zip(sub["coef"], sub["se"], sub["label"]))
    fig, ax = plt.subplots(figsize=(7.6, 0.30 * len(rows) + 1.6))
    ys = np.arange(len(rows))[::-1]
    coefs = np.array([r[0] for r in rows])
    ses = np.array([r[1] for r in rows])
    ax.errorbar(coefs, ys, xerr=1.96 * ses, fmt="o", color="#222",
                ecolor="#888", capsize=3)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys); ax.set_yticklabels([r[2] for r in rows], fontsize=7.0)
    ax.set_xlabel("LPM β on ideation (HC1, 95 % CI)")
    ax.set_title(f"Does ideation predict mating-type membership? — CFPS {wave}")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


_DIM_LABEL = {"age": "Age", "edu": "Education", "inc": "Income"}


def fig_match_type_per_dimension(results: pd.DataFrame, wave: str,
                                   dim: str, out_pdf: Path):
    """v3 (2026-05-23): per-dimension forest to avoid the combined-plot noise."""
    sub = results[(results["wave"] == wave) &
                   (results["dimension"] == dim)].copy()
    if sub.empty:
        return
    # order: hypergamy / homogamy / hypogamy × predictor
    type_order = ["hypergamy", "homogamy", "hypogamy"]
    sub["match_rank"] = sub["match_type"].map({t: i for i, t in enumerate(type_order)})
    sub = sub.sort_values(["match_rank", "predictor"])
    color_map = {"wife_ideation": "#d62728", "husband_ideation": "#1f77b4"}
    rows = list(zip(sub["coef"], sub["se"], sub["match_type"],
                    sub["predictor"], sub["n"]))
    fig, ax = plt.subplots(figsize=(6.4, 0.45 * len(rows) + 1.4))
    ys = np.arange(len(rows))[::-1]
    for i, (coef, se, mt, pred, n) in enumerate(rows):
        ax.errorbar([coef], [ys[i]], xerr=1.96 * se, fmt="o",
                    color=color_map[pred], ecolor=color_map[pred],
                    capsize=3, markersize=6)
    ax.axvline(0, color="#aaa", linewidth=0.8, linestyle="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{mt} | {pred.replace('_ideation','')} (n={n})"
                         for _, _, mt, pred, n in rows], fontsize=8)
    ax.set_xlabel("LPM β on ideation (HC1, 95 % CI)")
    ax.set_title(f"{_DIM_LABEL[dim]} matching: does ideation predict type?\nCFPS {wave}")
    ax.grid(axis="x", linewidth=0.4, alpha=0.4)
    # legend
    handles = [plt.Line2D([], [], marker="o", color=color_map["wife_ideation"],
                            linestyle="", label="Wife's ideation"),
               plt.Line2D([], [], marker="o", color=color_map["husband_ideation"],
                            linestyle="", label="Husband's ideation")]
    ax.legend(handles=handles, loc="best", frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(out_pdf); plt.close(fig)


def fig_satisfaction_by_typology(couples: pd.DataFrame, wave: str, out_pdf: Path):
    d = couples.copy()
    d["typology"] = _couple_typology(d)
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.6), sharey=True)
    order = ["concordant_progressive", "woman_more_traditional",
             "man_more_traditional", "concordant_traditional"]
    for ax, side, color in zip(axes, ["wife", "husband"], ["#d62728", "#1f77b4"]):
        means, errs, labels = [], [], []
        for t in order:
            sub = d.loc[d["typology"] == t, f"{side}_marriage_sat"].dropna()
            if len(sub) < 20:
                means.append(np.nan); errs.append(0); labels.append(f"{t}\n(n=0)")
                continue
            means.append(sub.mean())
            errs.append(sub.std(ddof=1) / np.sqrt(len(sub)))
            labels.append(f"{t}\n(n={len(sub)})")
        ax.bar(range(len(order)), means, yerr=errs, capsize=3, color=color, alpha=0.85)
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=7.5)
        ax.set_title(f"{side.capitalize()}'s satisfaction")
        ax.set_ylabel("Marriage satisfaction (1-5)" if side == "wife" else "")
        ax.grid(axis="y", linewidth=0.4, alpha=0.4)
    fig.suptitle(f"Marriage satisfaction by couple ideation typology — CFPS {wave}",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_pdf); plt.close(fig)


# ------------------------------------------------------------------ #
# 5. Driver
# ------------------------------------------------------------------ #

def main() -> int:
    couples_by_wave = {}
    for wave in ("2014", "2020"):
        print(f"building couples for {wave} …")
        c = load_couples(wave)
        print(f"  n_couples = {len(c)}")
        couples_by_wave[wave] = c

    # ---- Part A ----
    corr_rows, regA_rows, rankrank_rows = [], [], []
    rank_frames = {}
    for wave, c in couples_by_wave.items():
        corr_rows.append(part_A_correlations(c, wave))
        regA_rows.append(part_A_regression(c, wave))
        rr_summary, rr_frame = part_A_rank_rank(c, wave)
        rankrank_rows.append(rr_summary)
        rank_frames[wave] = rr_frame
    pd.concat(corr_rows, ignore_index=True).to_csv(
        TABLES / "assortative_mating_correlations.csv", index=False)
    pd.concat(regA_rows, ignore_index=True).to_csv(
        TABLES / "assortative_mating_regression.csv", index=False)
    pd.concat(rankrank_rows, ignore_index=True).to_csv(
        TABLES / "assortative_mating_rank_rank.csv", index=False)

    # ---- Part A2 (v2) — sociological match types and ideation ----
    a2_desc_rows, a2_reg_rows = [], []
    for wave, c in couples_by_wave.items():
        a2_desc_rows.append(part_A2_descriptive(c, wave))
        a2_reg_rows.append(part_A2_regression(c, wave))
    partA2_desc = pd.concat(a2_desc_rows, ignore_index=True)
    partA2_reg  = pd.concat(a2_reg_rows,  ignore_index=True)
    partA2_desc.to_csv(TABLES / "mating_types_descriptive.csv", index=False)
    partA2_reg.to_csv(TABLES / "mating_types_regression.csv", index=False)

    # ---- Part B ----
    regB_rows = []
    for wave, c in couples_by_wave.items():
        regB_rows.append(part_B_dyadic(c, wave))
    partB = pd.concat(regB_rows, ignore_index=True)
    partB.to_csv(TABLES / "dyadic_division_regression.csv", index=False)

    # ---- Part C ----
    regC_rows = []
    for wave, c in couples_by_wave.items():
        regC_rows.append(part_C_satisfaction(c, wave))
    pd.concat(regC_rows, ignore_index=True).to_csv(
        TABLES / "marriage_sat_typology_regression.csv", index=False)

    # ---- Descriptive table + missing table ----
    desc_rows = []
    for wave, c in couples_by_wave.items():
        desc_rows.append(dict(wave=wave, n_couples=len(c),
                              n_with_both_ideation=int(c[["wife_ideation",
                                                           "husband_ideation"]].notna().all(axis=1).sum()),
                              wife_mean=round(float(c["wife_ideation"].mean()), 4),
                              husband_mean=round(float(c["husband_ideation"].mean()), 4),
                              pearson_r=round(float(c["wife_ideation"].corr(c["husband_ideation"])), 4)))
    pd.DataFrame(desc_rows).to_csv(RUN / "01_descriptive_table.csv", index=False)

    miss_rows = []
    for wave, c in couples_by_wave.items():
        for var in ["wife_ideation", "husband_ideation",
                    "wife_housework_hours", "husband_housework_hours",
                    "wife_childcare_hours", "husband_childcare_hours",
                    "wife_marriage_sat", "husband_marriage_sat",
                    "wife_edu_yrs", "husband_edu_yrs"]:
            if var not in c.columns:
                continue
            miss_rows.append(dict(wave=wave, variable=var,
                                  n_total=len(c),
                                  n_nonmissing=int(c[var].notna().sum()),
                                  pct_coverage=round(100 * c[var].notna().mean(), 2)))
    pd.DataFrame(miss_rows).to_csv(RUN / "02_missing_table.csv", index=False)

    # Unified result table for 05 references
    all_rows = []
    for kind, df in [("partA_regression",
                       pd.concat(regA_rows, ignore_index=True)),
                      ("partA2_mating_types",
                       partA2_reg),
                      ("partB_dyadic",
                       partB),
                      ("partC_marriage_sat",
                       pd.concat(regC_rows, ignore_index=True))]:
        if df.empty:
            continue
        df = df.copy()
        df["kind"] = kind
        all_rows.append(df)
    if all_rows:
        pd.concat(all_rows, ignore_index=True).to_csv(
            RUN / "04_result_table.csv", index=False)
    print("tables written.")

    # ---- Figures ----
    for wave, c in couples_by_wave.items():
        fig_scatter_couple_ideation(c, wave,
                                     FIGS / f"couple_ideation_scatter_{wave}.pdf")
        fig_rank_rank_scatter(rank_frames[wave], wave,
                               FIGS / f"rank_rank_scatter_{wave}.pdf")
        partB_wave = partB[partB["wave"] == wave]
        fig_dyadic_coef_forest(partB_wave, FIGS / f"dyadic_forest_{wave}.pdf", wave)
        fig_satisfaction_by_typology(c, wave,
                                      FIGS / f"sat_by_typology_{wave}.pdf")
        fig_match_type_by_ideation(c, wave,
                                    FIGS / f"mating_types_stacked_{wave}.pdf")
        # v3 — per-dimension forests + the combined one kept for backward-compat
        fig_match_type_coef_forest(partA2_reg, wave,
                                    FIGS / f"mating_types_forest_{wave}.pdf")
        for dim in ("age", "edu", "inc"):
            fig_match_type_per_dimension(
                partA2_reg, wave, dim,
                FIGS / f"mating_types_forest_{dim}_{wave}.pdf")
    print("figures written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
