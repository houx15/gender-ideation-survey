# Gender Ideology, Individual Practice, and Intergenerational Reproduction
## A report on Chinese survey data (CFPS, CGSS, CEPS, ACWF)

Structured by research question (SPEC §5). For each: the relevant experiments, how they were
done, and the results. All 22 analysis runs live in `analysis_runs/`; helper code in `scripts/`
is covered by 54 passing tests (`tests/`). Associations are cross-sectional unless stated.

---

## 0. Setup, data, and the ideology index

**Data.** CFPS adult 2014 (N=39,768) & 2020 (28,530); CGSS 2010–2023 (8 waves with the
ideology battery; 2011 has none, 2023 is a split-ballot sub-module); ACWF 1990/2000/2010;
CEPS 2013–14 (students 19,487 + matched parents). Raw `.dta` are gitignored.

**Ideology index.** Each Likert item is recoded to [0,1] (1 = most traditional); the
respondent score is the mean of valid items. Direction and missing codes were taken from the
actual value labels (verified in `08_variable_handling_verification.md`: e.g. −1/−2/−8 dropped,
CEPS `10=无所谓` dropped rather than scored as the top). The recoding **reproduces the existing
`surveys/processed` reference exactly** (diff = 0.0000), locked by an integration test.

**Methods toolkit (tested):** OLS with p-values, WLS with robust SEs (`stats_helpers`),
propensity-score matching with bootstrap (`matching`), one-way ICC and fixed-effects OLS
(`stats_helpers`), and CFPS dyad builders (`cfps_linkage`).

---

## RQ 5.1 — How is gender ideology measured, and how does it distribute?

### Experiment 1 — Measurement audit (analysis_001)
**How.** For ACWF/CFPS/CGSS each survey-year, computed the [0,1] index, Cronbach's α and mean
inter-item correlation; cross-checked national means against `surveys/processed`.
**Results.** A comparable battery exists in every target survey-year except CGSS 2011.
Reliability is modest: ACWF 2000 α=0.71; ACWF/CGSS mostly 0.56–0.66; **CFPS α=0.37 (2014) /
0.51 (2020)** (only 4 items → use single items there). Women are less traditional than men in
**12 of 13 survey-years**; the CGSS gender gap widens over time.

### Experiment 2 — Birth-cohort gradient, CFPS (analysis_002)
**How.** CFPS 2014 & 2020; OLS `index ~ decade_c + female + decade_c×female + age` (decade_c =
(birth−1970)/10). N≈31.4k/22.6k.
**Results.** Younger cohorts less traditional (decade_c −0.017/−0.031). A **gender-gap
crossover**: F−M = +0.03 in the oldest cohort but **−0.06 (2014) / −0.11 (2020)** in the
1990s+ cohort; decade×female −0.017/−0.033. (This also explained the puzzling positive raw
female coefficient in CFPS-2014 — it is driven by older-cohort women.)

### Experiment 3 — Cohort replication across 8 CGSS waves (analysis_021)
**How.** Pooled CGSS 2010–2023 (N=86,318); OLS `index ~ decade_c + female + decade_c×female +
wave fixed effects`.
**Results.** The crossover replicates with high precision: F−M from **+0.012 (1930s) to
−0.120 (1990s+)**; decade×female = **−0.022 (t=−30.7, p≈0)**. The younger-women divergence
holds across two independent survey programs.

### Experiment 4 — Population weights (analysis_019)
**How.** Applied CFPS national cross-section weights via WLS with robust SEs; compared
weighted vs unweighted mean, gender gap, and transmission.
**Results.** Weighted mean slightly lower (0.598→0.585, 2014). The 2014 "women more
traditional" blip becomes **non-significant when weighted** (+0.011→+0.003, p=0.23) → sampling
artifact. The 2020 women-less-traditional gap (−0.027, p<0.001) and transmission (0.24→0.25)
are unchanged → population-level.

---

## RQ 5.2 — Ideology and family practice (marriage, fertility, housework, couples)

### Experiment 1 — Family-practice associations (analysis_004)
**How.** CFPS 2014/2020 adults. LPM for currently-married; OLS for daily housework hours
(with ideation×female) and ideal children; controls age, age². Couples linked via `pid_s`.
**Results.** More traditional → more likely **currently married** (LPM +0.115/+0.095,
t=10.2/7.6) and **more ideal children** (+0.44, t=17.6). Housework: the **ideation×female**
interaction is large (+1.42/+0.96, t=12.1/5.6) → traditional **women** do much more housework;
men's barely move. Couples are **assortative** (ego–spouse r=0.22; 41.6% both-traditional,
19.3% both-progressive, 39.2% mixed).

### Experiment 2 — Whose ideology drives the division? (analysis_007)
**How.** CFPS 2014 couples (N=10,675) built with `build_couples`; regressed wife's housework,
husband's housework, and wife's share of housework on **both** spouses' ideology + ages.
**Results.** For the **wife's own** housework, *her* ideology dominates (0.97, t=8.1 vs
husband's 0.23) — ~4×. The **husband's** housework responds to neither spouse's ideology
(both n.s.). For the wife's **share**, both matter and the **husband's is slightly larger**
(0.102, t=6.8 vs wife's 0.079, t=4.9). Interpretation: an egalitarian wife isn't enough — the
division shifts only if the **husband** is egalitarian (men's contribution is "sticky").

### Experiment 3 — Marriage timing (analysis_022)
**How.** Pooled CGSS ever-married (N=71,560); age at first marriage = `a70` − birth year;
OLS `age ~ ideation + female + ideation×female + decade_c + wave FE`.
**Results.** More traditional ⇄ **younger first marriage** (ideation −1.77 yr, t=−14.7),
**steeper for women** (×female −1.34 → ~−3 yr for women). **Descriptive only**: ideation is
measured decades after marriage, so causal timing / event-history is **not identifiable**.

---

## RQ 5.3 — Ideology and work / leadership

### Experiment — Labour outcomes (analysis_005)
**How.** CFPS 2014/2020 adults. LPM employed (`employ`), OLS log wage (employed only), LPM
management post (`qg14`, employed only); each with ideation×female + age, age².
**Results.** **Employment:** ideation×female = −0.092/−0.108 (t≈−3.5/−4.0) — traditional
women less likely employed, while traditional men are slightly *more* likely. **Wages
(employed):** ideation×female −2.03/−1.02 (t≈−5.6/−5.9) — a steeper traditional wage penalty
for women (2020 replicates; 2014 magnitude unreliable due to wage scale). **Management:** more
traditional → less likely (−0.070/−0.107). Caveats: cross-sectional; employed-only models are
selected; occupation/sector not yet coded.

---

## RQ 5.4 — Ideology and education

### Experiment — Education gradient (analysis_006)
**How.** CFPS 2014/2020. Because adult schooling is largely complete *before* the attitude is
measured, modeled the temporally sensible direction **education → ideation**: OLS
`index ~ eduy + female + eduy×female + age, age²`.
**Results.** Each year of schooling → less traditional (−0.006/−0.009, men), and
**education de-traditionalizes women faster** (eduy×female −0.003/−0.007 → women's slope
≈ −0.016 in 2020). The gap opens at the top: in 2020, with *no* schooling women≈men
(0.648/0.651), but **college 0.335 vs 0.453** and **postgrad 0.233 vs 0.436**.

---

## RQ 5.5 / 5.6 — Parental ideology, gendered resource allocation, child outcomes

### Experiment 1 — Parent ideology → child education (analysis_009)
**How.** CFPS children linked to both parents; OLS `child_eduy ~ mother + father ideation +
child_female + parent×daughter interactions + age, age²`.
**Results.** Traditional parents → **less-educated children of both genders** (father −1.9/−2.3,
mother −0.8/−2.1, all sig); **no significant daughter-specific penalty** (interactions n.s.).
A positive `child_female` flagged a co-residence selection concern → addressed next.

### Experiment 2 — Household-matched, life-stage-corrected (analysis_010)
**How.** Fixed two flaws: (i) within-family **one-son-one-daughter** difference (differences
out all family factors); (ii) restricted to **age ≥ 25** (completed schooling).
**Results.** The naive "daughter advantage" *grows* at 25+ (child_female → +2.7) → it is
**co-residence selection** (linked adult daughters are selected). Within-family, the daughter−son
education gap is flat/slightly daughter-favouring; parent ideology does **not** significantly
tilt it toward sons. → **No robust gendered educational investment** once household-matched.

### Experiment 3 — Resource allocation in CEPS (analysis_011)
**How.** CEPS students × parents (N=19,487) — investment & demand measured *during* schooling.
LPM/OLS of each outcome on `female` + SES controls; plus `female×has_brother` (non-only-children).
**Results.** Daughters get **more** educational investment (expect college +0.042, tutoring
+0.043, **tutoring spending +0.30**, t≈6–10) but **more chores** (+0.70 hr/wk) and slightly
less homework supervision. **Son preference at the sibling-competition margin:** the girls'
tutoring-spending advantage **reverses when she has a brother** (female×has_brother −0.33,
t=−2.7).

### Experiment 4 — Parent ideology → allocation, within family (analysis_012)
**How.** CFPS one-son-one-daughter families; regressed the daughter−son gap (education,
housework) on parent ideology.
**Results.** Directionally son-favouring (education gap −2.71; housework gap +0.9–1.1) but
**not significant** (underpowered, 107–385 families). CEPS (best resource data) **cannot**
attach ideology (no item; county codes anonymized).

### Experiment 5 — Robustness ladder + moderation test (analysis_013)
**How.** (Rung 2) all mixed-gender families via `family_gender_gap`; (Rung 3) PSM across all
families stratified by parent ideology; **formal** `outcome ~ female×parent_ideology` test, all
with p-values.
**Results.** **Housework moderation is significant**: female×parent_ideology = **+0.67
(p=0.038, 2014) / +1.23 (p=0.022, 2020)** — traditional parents → daughters do significantly
more chores than brothers. **Education moderation** marginal/n.s. (−2.60, p=0.061 / −1.38,
p=0.22). PSM strata: daughter education advantage concentrated in **egalitarian** families
(vanishes in traditional 2020); daughter chore burden heaviest in **traditional** families.

### Experiment 6 — Resource gaps via PSM (analysis_014)
**How.** PSM ATT of being a daughter on each CEPS resource, matching on SES, parent education,
grade, sibship size; with naive comparison.
**Results.** **Educational-investment advantages are robust** to matching (expectations +0.049,
tutoring +0.060, spending +0.345, all p<0.0001). **Chores and own-desk flip sign** when matching
on **sibship size** (chores +0.64→−0.50, p=0.007) → the raw chore gap is largely a
**son-biased-fertility** artifact (girls in larger sibships). Caveat: child sex is quasi-random
so the propensity model is weak; flipped estimates are specification-sensitive.

---

## RQ 5.7 — Parent → child ideology transmission (regeneration)

### Experiment 1 — Linkage feasibility (analysis_003)
**How.** Counted CFPS dyads where ego and the linked spouse/father/mother both have an index.
**Results.** 21,680 couple, 6,316 father–child, 7,191 mother–child dyads (2014); within-dyad
correlations 0.15–0.22. Transmission analyses are feasible.

### Experiment 2 — Transmission regression (analysis_008)
**How.** OLS `child_ideation ~ mother + father ideation + child_female + gender interactions`,
both parents in the same model.
**Results.** Both parents transmit ≈ equally (mother +0.126/father +0.153, 2014; +0.102/+0.116,
2020; all t≥5.8); same-/cross-gender interactions **n.s.**. Daughters less traditional net of
parents (child_female −0.06 → −0.12, growing).

### Experiment 3 — Correlations + PSM (analysis_015)
**How.** Pearson correlations (with p) + PSM (traditional vs egalitarian parent by tertiles),
matched on parent education, child age, sex.
**Results.** parent-mean↔child r = **0.197 (2014) / 0.191 (2020)**, all p<0.001. PSM ATT =
**+0.063 / +0.041** (p≪0.001) — transmission survives matching on parent education.

### Experiment 4 — Formative window + urban/rural + bootstrap (analysis_016)
**How.** Added urban/rural to the match, restricted to **age 16–30**, and used **bootstrap**
SEs (n=300) instead of the optimistic paired-t.
**Results.** ATT ≈ **0.04–0.07** across specs; **bootstrap SEs ~2× the paired-t SEs**
(confirming paired-t was optimistic) but every CI excludes 0 (boot p<0.05, mostly ≪0.001).

### Experiment 5 — Family SES proxy (analysis_017)
**How.** Added parents' personal income (2014 `p_income`; no family file, 2020 lacks income)
to the match.
**Results.** ATT 0.068 → **0.058** (~13% attenuation), still p≪0.001, CI excludes 0 → not an
SES artifact as far as proxied.

### Experiment 6 — Sibling ICC + family FE (analysis_018)
**How.** Real multi-child families (both parents in-sample). One-way **ICC** of child ideology;
ICC of residuals after partialling out parent ideology; **family-FE** `ideation ~ female + age`.
**Results.** Sibling ICC ≈ **0.260 (2014) / 0.196 (2020)** — ideology is strongly
family-clustered — but parents' *measured* ideology explains only **11.4% / 6.4%** of that
resemblance (shared environment dominates). Family-FE: daughters less traditional than their
**own brothers**, **−0.044 → −0.101** (p<0.001), widening.

### Experiment 7 — ICC by subgroup (analysis_020)
**How.** ICC within rural/urban families and older/younger sibships.
**Results.** Clustering everywhere (ICC 0.15–0.30), modestly higher in **rural** families
(2020) and **younger** sibships (2014); parent ideology explains only **3–16%** in every
subgroup (just 2.6% in rural 2020 despite the highest ICC) → community/shared environment is
the dominant channel.

---

## Cross-cutting conclusions
1. **Women's ideology is the more responsive and self-consequential variable** — it moves more
   with education/cohort and predicts women's own housework/labour, while men's behaviour
   barely responds to anyone's ideology.
2. **Ideology bites hardest on the domestic-labour channel** — wives' own chores, and (via the
   significant moderation) daughters' chores — more than on educational investment, where girls
   generally do well.
3. **A widening gender divergence** within cohorts (002/021) *and* within families
   (018: daughters vs own brothers) — younger women pulling away from men.
4. **Reproduction runs mostly through shared environment**; explicit parental attitudes are a
   real but minor channel of sibling resemblance.

## Data boundaries
- **CEPS cannot be linked to ideology** (no parental attitude item; anonymized county codes →
  no province climate merge). **No CFPS family file** → no true household income. **Event-history
  of marriage/fertility timing not identifiable** (attitude measured once, post-event).
  Cross-survey **levels** are not comparable (only trends/slopes/gaps).

## What would unlock more
CFPS **children's questionnaire** (during-childhood resources × parent ideology — the
conclusive 5.5 test); CFPS **family file** (household income); the deferred **provincial ideology
climate**; design-based (PSU/strata) SEs, weights throughout, and occupation/sector coding.
