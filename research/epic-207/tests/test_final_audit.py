from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


EPIC = Path(__file__).resolve().parents[1]
MODULE_PATH = EPIC / "brazil" / "final-audit" / "build_audit.py"
SPEC = importlib.util.spec_from_file_location("build_final_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class FinalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generated = AUDIT.build_report()
        cls.committed = json.loads(
            AUDIT.REPORT.read_text(encoding="utf-8")
        )

    def test_report_is_deterministic(self) -> None:
        self.assertEqual(self.generated, self.committed)

    def test_reconciles_sources_candidates_and_publication(self) -> None:
        self.assertEqual(
            self.generated["source_coverage"],
            {
                "total": 172,
                "complete": 163,
                "gap_justified": 9,
                "terminal": 172,
            },
        )
        candidates = self.generated["candidate_reconciliation"]
        self.assertEqual(candidates["candidate_rows"], 76)
        self.assertEqual(candidates["canonical_candidates"], 63)
        self.assertEqual(candidates["decision_counts"]["eligible"], 27)
        publication = self.generated["publication"]
        self.assertEqual(publication["batch_count"], 3)
        self.assertEqual(publication["candidate_count"], 27)
        self.assertEqual(publication["profile_file_count"], 81)

    def test_cvm_is_bounded_and_never_used_for_discovery(self) -> None:
        provenance = self.generated["discovery_provenance"]
        self.assertEqual(provenance["reference_count"], 126)
        self.assertEqual(provenance["non_cvm_reference_count"], 126)
        self.assertEqual(provenance["cvm_reference_count"], 0)
        cvm = self.generated["cvm_use"]
        self.assertEqual(cvm["consulted_candidate_count"], 2)
        self.assertLessEqual(cvm["query_rate"], 0.10)
        self.assertFalse(cvm["eligibility_use"])

    def test_every_integrity_gate_is_true(self) -> None:
        failed = [
            name
            for name, passed in self.generated["integrity"].items()
            if not passed
        ]
        self.assertEqual(failed, [])

    def test_routing_requires_revalidation(self) -> None:
        routing = self.generated["routing"]
        self.assertEqual(
            {
                key: value["target_issue"]
                for key, value in routing.items()
            },
            {
                "routed_accelerators": 62,
                "routed_angel_networks": 63,
                "routed_funding_platforms": 64,
            },
        )
        self.assertTrue(
            all(
                not value["automatic_eligibility"]
                for value in routing.values()
            )
        )

    def test_scope_does_not_claim_totality(self) -> None:
        scope = self.generated["scope_statement"].lower()
        self.assertIn("cobertura auditada", scope)
        self.assertIn("não prova totalidade", scope)


if __name__ == "__main__":
    unittest.main()
