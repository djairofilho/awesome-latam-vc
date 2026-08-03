# Epic 327 final audit

Status: **pass**

Cutoff: `2026-08-02`

## Summary

- Candidate universe: 1088
- Review assignments/results: 1073/1073
- Final terminal decisions: 1088
- Critical/high findings: 0/0

## Gates

| Gate | Status |
| --- | --- |
| baseline_intake_hashes | pass |
| candidate_terminal_ledger | pass |
| mandatory_review_and_sample | pass |
| official_validation_integrity | pass |
| review_and_adjudication_integrity | pass |
| freeze_and_publication_plan | pass |
| publication_surfaces | pass |
| order_and_determinism | pass |
| utf8_and_mojibake | pass |
| cutoff_and_limitations | pass |

## Terminal decisions

| Decision | Count |
| --- | ---: |
| duplicate | 15 |
| eligible | 1 |
| excluded | 14 |
| identity_conflict | 592 |
| inactive | 2 |
| insufficient_evidence | 339 |
| routed_accelerators | 10 |
| routed_angel_networks | 4 |
| routed_funding_platforms | 2 |
| routed_other | 10 |
| unresolved | 99 |

## Findings

No findings.

## Limitations

- The audited universe is the frozen 1,088-candidate intake queue, not a claim of market totality.
- The source intake preserved 741 unparsed rows outside the candidate ledger.
- The audit performs no live HTTP checks; it validates frozen official-source evidence and publication artifacts.
- Identity-conflict and unresolved records use destination_kind manual_review; their original destination may be null or manual_identity_review.
- routed_other destinations are abstract terminal ecosystem handoffs accepted by the schema; they are not required to be physical paths and do not represent pending fund publication.
- Eligibility and recency are evaluated at the 2026-08-02 cutoff.

The machine-readable report and terminal ledger are `audit-report.json` and `final-decisions.jsonl`.
