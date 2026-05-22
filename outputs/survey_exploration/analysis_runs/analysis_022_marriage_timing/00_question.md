# analysis_022 — Age at first marriage & gender ideology (CGSS, SPEC 5.2 timing)

**Research question:** Is gender ideology associated with the age at which people first
marry, and does the association differ by gender? (Fills the "first marriage timing" cell
of the readiness matrix.)

**Analysis type:** Individual practice — marriage timing (descriptive association).

**Data / sample:** Pooled CGSS 2010–2023, ever-married respondents with valid first-marriage
year (`a70`/`A70`), birth year, ideation, and gender. Age at first marriage = marriage year −
birth year, restricted to [15, 50]. N = 71,560.

**Model:** `age_first_marriage ~ ideation + female + ideation×female + decade_c + wave FE`.

**CRITICAL caveat (time order):** current ideation is measured at the survey, but first
marriage occurred long before (median ~1988). So this is a **descriptive** association
(people who married younger now hold more traditional views), **not** a causal ideation→timing
effect. A proper event-history/survival model is **not identifiable** here because the
attitude is measured once, after the event.
