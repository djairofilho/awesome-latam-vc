from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


AUDIT_PATH = Path(__file__).resolve().parents[1] / "audit.py"
SPEC = importlib.util.spec_from_file_location("epic_327_final_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class FinalAuditRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.decisions = audit.audit_repository(audit.REPO)

    def test_current_repository_passes_every_gate(self) -> None:
        self.assertEqual("pass", self.report["status"])
        self.assertEqual([], self.report["findings"])
        self.assertTrue(all(row["status"] == "pass" for row in self.report["gates"]))

    def test_terminal_ledger_has_expected_dynamic_review_counts(self) -> None:
        self.assertEqual(1088, len(self.decisions))
        self.assertEqual(1073, self.report["counts"]["review_assignments"])
        self.assertEqual(1073, self.report["counts"]["review_results"])
        self.assertEqual(
            {
                "duplicate": 15,
                "eligible": 1,
                "excluded": 14,
                "identity_conflict": 592,
                "inactive": 2,
                "insufficient_evidence": 339,
                "routed_accelerators": 10,
                "routed_angel_networks": 4,
                "routed_funding_platforms": 2,
                "routed_other": 10,
                "unresolved": 99,
            },
            dict(Counter(row["decision"] for row in self.decisions)),
        )

    def test_final_ledger_is_sorted_and_unique(self) -> None:
        ids = [row["candidate_id"] for row in self.decisions]
        self.assertEqual(sorted(ids), ids)
        self.assertEqual(len(ids), len(set(ids)))
        manual = [
            row
            for row in self.decisions
            if row["decision"] in {"identity_conflict", "unresolved"}
        ]
        self.assertEqual(691, len(manual))
        self.assertTrue(all(row["destination_kind"] == "manual_review" for row in manual))
        self.assertEqual(358, sum(row["destination"] is None for row in manual))

    def test_generated_artifacts_are_deterministic_and_current(self) -> None:
        first = audit.build_outputs(audit.REPO)
        second = audit.build_outputs(audit.REPO)
        self.assertEqual(first, second)
        for relative, rendered in first.items():
            self.assertEqual(
                rendered,
                (audit.HERE / relative).read_text(encoding="utf-8"),
                relative,
            )
        parsed = json.loads(first["audit-report.json"])
        self.assertFalse(parsed["provenance"]["network_access"])


class FinalDecisionPrecedenceTests(unittest.TestCase):
    def test_adjudication_overrides_review_and_review_overrides_origin(self) -> None:
        candidates = {
            "delta-fund-a": {
                "candidate_id": "delta-fund-a",
                "status": "duplicate",
                "canonical_profile": "funds/a.md",
            },
            "delta-fund-b": {
                "candidate_id": "delta-fund-b",
                "status": "identity_conflict",
            },
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "status": "unresolved",
            },
        }
        reviews = {
            "delta-fund-b": {
                "candidate_id": "delta-fund-b",
                "final_decision": "insufficient_evidence",
                "destination": None,
            },
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "final_decision": "excluded",
                "destination": None,
            },
        }
        adjudications = {
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "final_decision": "eligible",
                "destination": "funds/",
            }
        }
        rows, unresolved = audit.resolve_final_decisions(
            candidates, {}, reviews, adjudications, "2026-08-02"
        )
        self.assertEqual([], unresolved)
        self.assertEqual(
            ["duplicate", "insufficient_evidence", "eligible"],
            [row["decision"] for row in rows],
        )
        self.assertEqual(
            ["origin", "review", "adjudication"],
            [row["source"] for row in rows],
        )
        self.assertEqual(
            ["canonical_duplicate", "evidence_follow_up", "fund_publication"],
            [row["destination_kind"] for row in rows],
        )


class CoverageGateTests(unittest.TestCase):
    def test_positive_coverage_includes_mandatory_records_and_twenty_percent(self) -> None:
        origins = {
            "eligible": "eligible",
            "conflict": "identity_conflict",
            "route": "routed_accelerators",
            **{f"excluded-{number}": "excluded" for number in range(5)},
        }
        assignments = {
            key: {"candidate_id": key, "review_reason": reason}
            for key, reason in (
                ("eligible", "all_eligible"),
                ("conflict", "all_identity_conflicts"),
                ("route", "all_routed"),
                ("excluded-0", "deterministic_exclusion_sample"),
            )
        }
        self.assertEqual([], audit.coverage_findings(origins, assignments))

    def test_negative_coverage_reports_missing_mandatory_record(self) -> None:
        findings = audit.coverage_findings(
            {"route": "routed_angel_networks"}, {}
        )
        self.assertEqual("mandatory_review_coverage", findings[0]["code"])
        self.assertEqual("high", findings[0]["severity"])
        self.assertEqual(["route"], findings[0]["details"]["candidate_ids"])

    def test_negative_coverage_rejects_sample_below_twenty_percent(self) -> None:
        origins = {f"candidate-{number}": "unresolved" for number in range(6)}
        assignments = {
            "candidate-0": {
                "candidate_id": "candidate-0",
                "review_reason": "deterministic_exclusion_sample",
            }
        }
        findings = audit.coverage_findings(origins, assignments)
        sample = next(
            row for row in findings if row["code"] == "exclusion_sample_coverage"
        )
        self.assertEqual(2, sample["details"]["minimum"])
        self.assertEqual(1, sample["details"]["selected"])


if __name__ == "__main__":
    unittest.main()
