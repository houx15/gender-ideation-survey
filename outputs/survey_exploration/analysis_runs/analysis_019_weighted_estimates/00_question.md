# analysis_019 — Population-weighted estimates (CFPS)

**Research question:** Do the headline findings hold at the population level once CFPS
national survey weights are applied (every prior estimate was unweighted)?

**Analysis type:** Robustness / population estimates.

**Data / sample:** CFPS 2014 & 2020 adults with ≥1 valid ideation item; national
cross-section weights (`rswt_natcs14`, `rswt_natcs20n`). Transmission uses the
both-parent-linked child sample with the child's weight.

**Quantities (unweighted vs weighted):**
- national mean ideation index,
- gender gap (`ideation ~ female`),
- transmission (`child_ideation ~ parent_mean + age + female`).

Weighted models = **WLS with robust (sandwich) SEs**, the correct inference for sampling weights.
