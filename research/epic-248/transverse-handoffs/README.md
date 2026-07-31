# Cross-market fund handoffs

Cutoff: `2026-07-30`.

This directory reconciles three fund candidates routed from the Uruguay re-audit
to their actual base markets under epic #248. It is an audited handoff batch,
not a new claim of completeness for Argentina or Brazil.

All three candidates are proposed as eligible:

- Beta Impacto, based in Argentina;
- Primary X, the A3 Mercados CVC based in Argentina;
- SaaSholic, based in São Paulo, Brazil.

The audit uses 12 non-regulatory public sources. No regulator was consulted
because no material identity divergence remained after official and
institutional reconciliation. Regulatory data did not drive discovery or
eligibility.

Beta Impacto has one explicit evidence limitation: its current official pages
describe direct investment, portfolio operations and founder access, but do not
expose portfolio company names as machine-readable text. Independent review
must challenge that limitation before freeze.

`review-request.json` is the pre-freeze gate. Publication remains blocked until
an independent integrator approves the evidence and records zero open critical
or high findings.
