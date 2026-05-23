# 05 · Interpretation note — analysis_029 (v3)

## v3 update (2026-05-23)

Three focused additions on top of v2:

1. **Per-dimension match-type forests**. The combined `mating_types_forest_*`
   plots were noisy (3 dims × 3 types × 2 predictors × 2 waves = 36 rows on
   one chart). v3 adds three per-dimension PDFs per wave (`age`, `edu`,
   `inc`), 12 rows each, with wife- and husband-ideation predictors
   colour-coded.
2. **Rank-rank ideology matching**. Added `tables/assortative_mating_rank_rank.csv`
   and `figures/rank_rank_scatter_{2014,2020}.pdf`. For each spouse, the
   percentile rank of ideation is computed (sex-pooled within wave), then:
   - **Spearman ρ**: 0.234 (2014), 0.242 (2020) — essentially identical to
     the Pearson r (0.225 / 0.237), meaning the joint ideation distribution
     is roughly symmetric and the linear correlation is not hiding a
     nonlinearity.
   - **Rank-rank OLS slope**: 0.233 (2014), 0.242 (2020). Reading: a 10
     percentile-rank shift in the husband's ideation associates with a 2.3
     percentile-rank shift in the wife's, scale-free.
   - Subgroup pattern matches the Pearson r breakdown: weaker matching
     in younger cohorts, in mid-edu couples (2020), and in rural couples.

The rank-rank result *confirms* the v1 Pearson finding rather than
revising it — useful as a robustness check, but doesn't change the
substantive conclusion.



> RQ 5.2 family-level couple analysis. Deep-dive replacement for
> `analysis_007_couple_whose_ideation`. v1 covered ideology-axis
> homogamy; v2 (2026-05-23) adds Part A2 — sociological matching types
> (age / edu / income hyper-/homo-/hypogamy) and whether ideation
> predicts the *type* of marriage.

## v2 headline (Part A2 — does ideation predict mating type?)

Yes, especially on the **education** axis, and especially driven by the
**wife's** own ideation.

| Match type | 2014 β (wife ideation) | 2020 β (wife ideation) |
|---|---|---|
| **Edu hypergamy** (husband more educated) | **+0.220** (p < .001) | **+0.288** (p < .001) |
| Edu homogamy                              | **−0.098** (p = .001) | **−0.127** (p < .001) |
| Edu hypogamy (wife more educated)         | **−0.122** (p < .001) | **−0.161** (p < .001) |
| **Income hypergamy** (husband-primary)    | +0.086 n.s.            | **+0.248** (p < .001) |
| Income homogamy (dual earners)            | −0.021 n.s.            | **−0.209** (p = .002) |
| Income hypogamy (wife-primary)            | −0.065 (p = .076)      | −0.039 n.s.            |
| Age hypergamy (older husband)             | **−0.084** (p = .005)  | −0.008 n.s.            |
| Age homogamy                              | **+0.063** (p = .036)  | −0.008 n.s.            |
| Age hypogamy (older wife)                 | +0.021 (p = .088)      | +0.017 n.s.            |

Substantively:

1. **Education matching is the cleanest story.** Holding the husband's
   ideation, couple age structure, urban hukou fixed, a full-range
   ideation shift toward traditional (0 → 1 on the index) raises a
   woman's probability of being in an educationally-hypergamous couple
   (husband ≥ 3 more years of schooling) by **22 pp in 2014 and 29 pp
   in 2020**, and pulls down her membership in both homogamy
   (−10 / −13 pp) and hypogamy (−12 / −16 pp). The husband-side
   coefficient is much smaller (−0.09 in 2014, ~zero in 2020), so
   it's predominantly the wife's ideation that channels couples into
   the patriarchal-default education arrangement.

2. **Income hypergamy gained an ideation gradient between waves.**
   In 2014, with limited income data (n = 1 634 couples with both
   spouses' income), the ideation gradient on income matching was
   not statistically significant. By 2020 (n = 1 796), the wife's
   ideation strongly predicts income hypergamy (β = +0.25, p < .001):
   traditional women are 25 pp more likely to be in a husband-primary-
   earner couple, and 21 pp less likely in a dual-earner couple. The
   husband's ideation also adds a small effect (+0.13 on hypergamy,
   p = .044).

3. **Age matching is the weakest signal.** In 2014, traditional women
   were *less* likely in age hypergamy (β = −0.084, p = .005) and
   more likely in age homogamy (β = +0.063, p = .036) — an unexpected
   inverted pattern. In 2020 the gradient flips to the husband side:
   traditional men more likely in age hypergamy (β = +0.08, p = .019),
   less likely in homogamy. Possible explanations:
   * Age hypergamy is so common (~35 % of all couples) and so
     structurally determined by remarriage demographics that ideation
     adds little variance.
   * The within-cohort age sorting may be saturated; ideation acts on
     the *kind* of age gap rather than its existence.

4. **The "patriarchal default" composite**: traditional women, holding
   constant the husband's ideation, are concentrated in couples that
   are simultaneously education-hypergamous AND (by 2020) income-
   hypergamous. This is the modal social-conservative arrangement.
   Modern Chinese marriage is moving away from this pattern (national
   educational expansion of women has made education hypogamy mechanically
   more common — see the descriptive table below), but among holders
   of traditional gender ideology, the old pattern persists.

### What the descriptive cross-tab shows

Take the education dimension, wife's ideation tertile, CFPS 2020:

| Wife ideation tertile | % edu hypergamy | % edu homogamy | % edu hypogamy |
|---|---|---|---|
| Low (progressive)     | 27.9 % | 52.0 % | 20.1 % |
| Mid                   | 40.0 % | 45.2 % | 14.8 % |
| **High (traditional)** | **50.1 %** | 40.9 % | 9.1 % |

50 % of the most-traditional women are in educationally-hypergamous
couples vs. only 28 % of the most-progressive women. The flip side:
20 % of progressive women are in hypogamous couples (more-educated wife
than husband) vs. only 9 % of traditional women.

This is one of the most substantively striking gradients in the entire
project: gender ideology is **strongly tied to the conservative
education-matching pattern**, especially on the female side.

## v1 + v2 figures

The 6 figures from v1 (couple-ideation scatter, dyadic forests,
satisfaction-by-typology, ×2 waves) are unchanged. v2 adds **4 new
figures**:

* `mating_types_stacked_{2014,2020}.pdf` — 3×2 panel of stacked-bar
  type composition by ideation tertile × predictor-spouse.
* `mating_types_forest_{2014,2020}.pdf` — LPM β forest, ideation on
  each (dimension × match_type × predictor).

## Headline

Three clean findings:

1. **Couples sort on ideology.** Within-couple Pearson r of ideation is
   **0.22 (2014)** and **0.24 (2020)** — substantial, in line with the
   homogamy literature for political/value attitudes. Conditional on
   age, education, and urban hukou, **a 0.10 shift in the husband's
   ideation associates with a 0.018 shift in the wife's** (β = 0.176,
   p < .001; 2014). The 2020 slope is smaller (β = 0.121) but
   equally tight. *Ideology-based residual sorting is real and
   robust across both waves*.

2. **Each spouse's own ideology drives their own housework.** In the
   dyadic OLS of wife's housework on *both* spouses' ideation:
   - **Wife's own ideation: β = +0.79 (2014, p < .001); +0.66 (2020, p = .034)**
   - Husband's ideation: β = +0.27 (2014, n.s.); +0.20 (2020, n.s.)
   
   And mirror-image for husband's housework:
   - **Husband's own ideation: β = −0.43 (2014, p = .005); +0.17 (2020, n.s.)**
   - Wife's ideation: β = +0.05 (2014, n.s.); −0.18 (2020, n.s.)
   
   So the housework division is driven by **individual belief**, not by
   negotiation with the partner's belief. The wife's hours respond
   ~3× more strongly to her own ideation than to her husband's.

3. **Concordant-traditional couples are the most-satisfied — both
   spouses.** Using concordant-progressive as the reference, in 2014:
   - **Concordant-traditional**: wife sat +0.20, husband sat +0.19 (both p < .001)
   - **Woman-more-traditional**: wife sat +0.11 (p < .001), husband sat n.s.
   - **Man-more-traditional**: wife sat n.s. (−0.04), husband sat +0.08 (p < .001)
   
   2020 shows the same picture, with one new finding: **man-more-traditional
   couples in 2020, the wife's satisfaction is significantly lower
   (β = −0.08, p = .049)**. That is, modern Chinese women who end up
   in mismatched couples where the man is more traditional than they
   are pay a satisfaction cost; no such cost in 2014.

## Outcome-by-outcome readings

### A. Assortative mating

**Raw Pearson r** is 0.22–0.24, stable across waves. Breaking it down:

| Subgroup | 2014 r | 2020 r |
|---|---|---|
| Overall | 0.225 | 0.237 |
| Wife born 1940s | 0.235 | 0.297 |
| Wife born 1970s | 0.176 | 0.172 |
| Wife born 1980s | 0.213 | 0.138 |
| Wife born 1990s | 0.149 | 0.225 |
| Couple urban (either spouse) | 0.223 | 0.233 |
| Couple rural          | 0.206 | 0.199 |
| Wife edu = low tertile | 0.200 | 0.146 |
| Wife edu = mid tertile | 0.195 | 0.087 |
| Wife edu = high tertile | 0.203 | 0.209 |

Two patterns worth noting:
* The within-couple ideology correlation is **fairly stable across
  urban / rural and education tertiles**, suggesting the homogamy is
  on the ideology axis itself, not just a by-product of sorting on
  other observable matching channels.
* The 2020 wave shows weaker assortment among mid-education couples
  (r = 0.09) — possibly an artefact of a tighter education-ideation
  link in that wave, or a real change in matching patterns; would
  need replication to interpret.

**Regression** (after controlling for both spouses' age, education,
urban): partner ideation still predicts own ideation:
- 2014: wife β on husband = **+0.176**; husband β on wife = **+0.200** (both p < .001, n = 10 809)
- 2020: wife β on husband = **+0.121**; husband β on wife = **+0.123** (both p < .001, n = 6 389)

Reading: a 1-SD shift in the husband's ideation (~0.20 on the index)
associates with a ~0.035 shift in the wife's ideation after stripping
out observable matching channels. **There is real ideology-axis
sorting, not just by-product of demographic sorting.** The 2020 slope
is ~30 % smaller than 2014; *if* this is a true longitudinal change,
it suggests assortment on ideology has weakened slightly. With only
two waves we can't separate this from sampling variability.

### B. Whose ideology drives the housework division

Centerpiece of the run. Dyadic OLS with both spouses' ideation on the
RHS:

**Wife's housework hours, 2014 (n = 1 633)**:
- **wife_ideation β = +0.79 (p < .001)**
- husband_ideation β = +0.27 (n.s.)

**Husband's housework hours, 2014 (n = 1 633)**:
- wife_ideation β = +0.05 (n.s.)
- **husband_ideation β = −0.43 (p = .005)**

**Wife's housework hours, 2020 (n = 928)**:
- **wife_ideation β = +0.66 (p = .034)**
- husband_ideation β = +0.20 (n.s.)

**Husband's housework hours, 2020 (n = 1 038)**:
- wife_ideation β = −0.18 (n.s.)
- husband_ideation β = +0.17 (n.s.)

The diagonal coefficients (your own ideology → your own housework) are
the significant ones; the off-diagonal coefficients (your partner's
ideology → your housework) are not. This is the **individual-belief
translation pattern**: each spouse's housework reflects their own
held belief, not a negotiated compromise with the partner.

The magnitudes are large: a wife at the most-traditional ideology
extreme does ~0.79 more hours/day of housework than an equivalent wife
at the most-progressive end (CFPS 2014). A husband at the most-
traditional end does ~0.43 *fewer* hours/day. The two diagonals
together produce a roughly **1.2 hour/day** widening of the gendered
housework gap from concordant-progressive to concordant-traditional
couples (subject to caveat that the dyadic n is much smaller than the
overall couples).

**Childcare (2020 only, qq9013)**: all coefficients n.s., though the
husband_childcare β on husband_ideation = +0.57 (p = .071, marginal).
Childcare gradient looks smaller and noisier than housework — possibly
because childcare time is more structurally determined (presence and
age of children).

### C. Marriage satisfaction by typology

Using `concordant_progressive` as reference (both spouses below median
ideation), differences in `qm801` (1–5 Likert):

**Wife's marriage satisfaction**:
| Typology | 2014 β | 2020 β |
|---|---|---|
| concordant_traditional | **+0.20** (p < .001) | **+0.17** (p < .001) |
| woman_more_traditional | **+0.11** (p < .001) | **+0.14** (p < .001) |
| man_more_traditional | −0.04 (n.s.) | **−0.08** (p = .049) |

**Husband's marriage satisfaction**:
| Typology | 2014 β | 2020 β |
|---|---|---|
| concordant_traditional | **+0.19** (p < .001) | **+0.06** (p = .03) |
| woman_more_traditional | +0.03 (n.s.) | −0.01 (n.s.) |
| man_more_traditional | **+0.08** (p = .001) | +0.00 (n.s.) |

Patterns:
1. **Both spouses are most satisfied in concordant-traditional couples,
   both waves.** This is the modal "expected" arrangement in the
   broader cultural context.
2. **Concordant-progressive (reference) is the least-satisfied cell**
   — that's by construction the reference, so the way to read this is:
   if you're in this cell, you're missing the satisfaction bump that
   comes with shared ideology, regardless of which direction.
3. **Woman-more-traditional**: she's happier (got the role she wanted);
   he's not different. The wife's "alignment dividend".
4. **Man-more-traditional**: 2014 husband happier (+0.08); 2020 wife
   *less* satisfied (−0.08). The 2020 finding suggests modern Chinese
   women in this mismatched cell pay a satisfaction cost — perhaps
   because they expected to choose their partner's egalitarianism and
   ended up with someone more traditional than they are.

The **`gap_ideation`** coefficient (absolute distance between spouses)
is mostly null, except marginally for husbands in 2020 (β = +0.13,
p = .055) — bigger gap → slightly *more* satisfied husband. This is
surprising and worth replication. It might reflect husbands being
relatively happy regardless of how aligned they are, but it doesn't
fit a strong-prior theory.

## What this analysis *does* support

1. **Assortative mating on ideology is real and substantive.** Pearson
   r ≈ 0.22–0.24; conditional residual slope ≈ 0.12–0.20. People sort
   on ideology axis itself, not just on demographics.
2. **Individual-belief model of housework**: each spouse's own
   ideation drives their own housework hours; the partner's ideation
   barely moves it. Decision-making does not appear to be a household-
   level negotiation on these data, at least not for housework time.
3. **The "concordant-traditional happy couple" is real.** Both spouses
   are most satisfied in the concordant-traditional cell, in both
   waves. Concordant-progressive (the reference) is the worst-off cell
   on average.
4. **2020-specific finding**: women in man-more-traditional couples
   are now significantly less satisfied — first sign of a satisfaction
   gradient for "I got more traditional than I am".

## Caveats

* **Cross-sectional**: matching at marriage cannot be separated from
  joint attitudinal adjustment over the relationship.
* **Selection on intact couples**: divorces drop out. People in
  worse-matched couples may have left the sample.
* **Marriage-satisfaction is self-report and culturally floored at
  the high end** — mean is 4.0 (1–5) in both waves with most mass
  at 4 / 5. Effect sizes look modest on this scale (a 0.20 difference
  is ~ 0.2 Likert points on a 4-mean), but on a population basis these
  are meaningful contrasts.
* **Childcare null results** may reflect the small sample (n ≈ 700)
  and the strong structural-determination of childcare time.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv` (per-wave counts + raw r)
* `02_missing_table.csv`
* `04_result_table.csv` (unified Part A + B + C)
* `tables/assortative_mating_correlations.csv`
* `tables/assortative_mating_regression.csv`
* `tables/dyadic_division_regression.csv`
* `tables/marriage_sat_typology_regression.csv`
* `figures/couple_ideation_scatter_{2014,2020}.pdf` — joint distribution + OLS line
* `figures/dyadic_forest_{2014,2020}.pdf` — wife/husband ideation β across outcomes
* `figures/sat_by_typology_{2014,2020}.pdf` — satisfaction bar charts
