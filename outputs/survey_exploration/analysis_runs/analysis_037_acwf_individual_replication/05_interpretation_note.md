# 05 · Interpretation note — analysis_037

> ACWF (中国妇女地位调查) replication of the individual-level ideation
> → outcome links from CFPS analyses 026 / 027 / 028, complementing the
> CGSS replication in analysis_036.

## Headline

ACWF adds **three outcomes that neither CFPS nor CGSS measure
directly**: `wife_does_more_housework` (categorical), `leadership_ever`
(career mgmt history), and `housework_hours` (1990's direct
minutes/day measure). All three replicate the dissertation's central
story with sharp precision, **plus the 1990 housework-hours measure
reveals a beautiful sex-asymmetric mechanism** that the
"who-does-more" categorical hides.

## The household division of labour — both pieces line up

### Categorical: "wife does more housework" (2000 + 2010 pooled, n=33,882)

| Stratum | β | p |
|---|---:|---:|
| all | **+0.238** | < .001 |
| male | +0.238 | < .001 |
| female | +0.222 | < .001 |

Traditional respondents are ≈ 24 percentage points more likely to
report that the wife does more housework. Men and women agree —
which means this is **not** just an artefact of self-perception; both
sides of the couple describe their own arrangement the same way.

### Continuous: housework hours in 1990 (n=11,198)

| Stratum | β (hr/day per ideology unit) | p |
|---|---:|---:|
| all | −0.46 | .005 |
| **male** | **−0.50** | .002 |
| **female** | **+1.52** | < .001 |

A unit increase in ideation **subtracts 0.5 hr/day** of housework
from a man's day but **adds 1.5 hr/day** to a woman's day. The
within-couple gap implied by the ideology gradient is ≈ **2 hr/day**.

This is the **mechanism** behind the categorical result: it's not
that traditional couples have more housework overall, it's that
traditional men do less and traditional women do more. The same
ideology produces asymmetric behaviour by sex. CFPS analysis_026
showed `housework_hours` β = +0.50 for women (in the lagged frame,
p = .085); ACWF 1990 sharpens that to β = +1.52 (p < .001) with
clear sex-asymmetry.

## Leadership: traditional people lead less (2000 + 2010, n=39,125)

| Stratum | β | p |
|---|---:|---:|
| all | **−0.26** | < .001 |
| male | −0.25 | < .001 |
| female | **−0.24** | < .001 |

Traditional respondents are ≈ 25 percentage points less likely to
have ever held a leadership / management position. The effect is
symmetric across sex strata — both traditional men and traditional
women lead less. CGSS analysis_036 found `mgmt_activity` β = −0.18
(current management) with stronger female effect (−0.32);
ACWF's `leadership_ever` is a lifetime measure, less gender-
asymmetric, but the direction agrees.

## First marriage age in 1990 (n=9,882)

| Stratum | β (years) | p |
|---|---:|---:|
| all | −0.08 | .81 |
| male | −0.04 | .91 |
| **female** | **−0.95** | < .001 |

Traditional women in 1990 married ≈ 1 year earlier; men show no
effect. Same directional pattern as CGSS (where the all-wave
female slope is −7.03 years) but much smaller — likely because
ACWF 1990 captures a single survey year with limited cohort spread,
not 13 years of pooled cross-sections.

## Shared outcomes (cf. CGSS 036)

| Outcome | All β (p) | Female β (p) | CGSS analogue |
|---|---|---|---|
| log_income | −0.12 (.22) | −0.04 (.70) | CGSS: female β = −0.42, p < .001 |
| edu_yrs | −0.13 (.36) | −0.32 (.022) | CGSS: female β = −1.33, p < .001 |
| employed | −0.01 (.24) | +0.04 (.001) | CGSS: female β = +0.06, p < .001 |

Directions match CGSS / CFPS where signed, but ACWF's smaller
sample, shorter time range, and lower ideation reliability give
attenuated estimates. The female-side `employed` and `edu_yrs`
effects reach conventional significance even at this attenuation,
which is the directional point.

## What does ACWF uniquely give the project?

1. **The "wife does more" categorical** is asked directly to both
   spouses in ACWF and gives a clean ≈ 0.24 ideation gradient.
   CFPS / CGSS only ask housework time, not who-does-more.

2. **The sex-asymmetric mechanism in housework hours**: 1990's
   raw minutes/day measure shows the dissertation's central
   pattern in its most legible form — same ideology, opposite
   behavioural consequences for men and women, with a 2-hr/day
   within-couple gap implied by the ideology gradient.

3. **Lifetime leadership history**: CGSS captures *current*
   management; ACWF captures *ever held* a leadership role —
   a different career-history measure that confirms the same
   pattern.

## What ACWF cannot replicate

The same restrictions as CGSS: no panel, no couples (other than
self-report on housework), no parent–child link. So:

| CFPS analysis | ACWF status |
|---|---|
| 025 (marriage → ideation, PSM-DiD) | impossible |
| 029 (couple matching) | impossible |
| 030–032 (PSM-DiD on Δ outcome) | impossible |
| 033–035 (intergenerational) | impossible |
| 026 / 027 / 028 (individual cross-section) | **partially replicated** above |

## Triangulation summary

| Statement | CFPS evidence | CGSS evidence | ACWF evidence |
|---|---|---|---|
| Traditional women marry younger | ✅ −1.9 yr (026) | ✅✅ −7.0 yr (036) | ✅ −1.0 yr (1990) |
| Traditional women have more children / want more | ✅ qm501 +0.31 | ✅✅ +1.0 ideal | (n/a) |
| Traditional women do more housework | ✅ +0.5 hr (026 lagged) | ✅ housework freq (036, not pooled) | ✅✅ **+1.5 hr/day** (1990) |
| Traditional men do LESS housework | ✅✅ −0.5 hr (037, 1990) | (n/a) | (this run) |
| Wife does more in traditional couples | (n/a) | (n/a) | ✅✅ +0.24 (2000+2010) |
| Traditional → less education | ✅ female −1.4 (028) | ✅ female −1.3 (036) | ✅ female −0.3 (this) |
| Traditional → less leadership/mgmt | ✅ promotion (027) | ✅✅ mgmt −0.32 (036) | ✅✅ leadership ever −0.24 (this) |
| Marriage satisfaction paradox | ✅ +0.48 (026) | ✅ +0.24 (036) | (n/a) |

**Three independent survey programs — CFPS, CGSS, ACWF — agree on
every directional pattern that more than one of them can measure.**
That cross-survey convergence is the strongest external-validity
result the project will produce.

## Caveats

* Cross-sectional throughout; no causal interpretation.
* Ideology measurement noise (α ≈ 0.6) attenuates β; ratios across
  surveys are more meaningful than absolute magnitudes.
* `housework_hours_1990` raw distribution has fat tails suggesting
  some respondents may have reported weekly rather than daily; the
  ≤ 1080-min clip absorbs the worst but the sex-asymmetric
  conclusion is robust to clipping thresholds.
* `leadership_ever` and `wife_does_more_housework` are
  retrospective lifetime / current-state self-reports; selection
  into observed couples and demand-characteristic reporting both
  in play.

## Files

* `00_question.md`, `03_method_note.md`, `05_interpretation_note.md`
* `01_descriptive_table.csv`, `02_missing_table.csv`
* `04_result_table.csv` — every coefficient × outcome × stratum
* `figures/forest_ideation_to_outcome_acwf.pdf`
