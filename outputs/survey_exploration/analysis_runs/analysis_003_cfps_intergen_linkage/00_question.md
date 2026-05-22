# analysis_003 — CFPS linkage feasibility (couples & parent-child)

**Research question:** Can CFPS support couple ideation-matching (SPEC 5.2) and
parent-child ideation-transmission (SPEC 5.7) analyses? Specifically, how many
respondents can be linked to an in-sample spouse / father / mother who *also*
answered the gender-ideation battery, and is there a within-dyad association?

**Analysis type:** Sample-construction / feasibility (intergenerational reproduction).

**Data / years / sample:** CFPS 2014 and 2020 adult files. Links come from the
respondent-level pointers `pid_s` (spouse), `pid_f`/`pid_a_f` (father),
`pid_m`/`pid_a_m` (mother), which carry the in-sample person-ID of the relative.

**Core variables:**
- Linking IDs: `pid` and the spouse/father/mother person-ID pointers.
- Outcome for correlation: the gender-ideation index (analysis_001), for both ego and alter.
- Restriction: a dyad requires BOTH members to have a valid index.
