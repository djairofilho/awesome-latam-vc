"""Regression tests for the Mexico fund re-audit."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("build_mexico", HERE / "build_mexico.py")
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class MexicoAuditTests(unittest.TestCase):
    def test_all_discovery_is_non_regulatory(self) -> None:
        report = json.loads(BUILD.outputs()[HERE / "audit-report.json"])
        self.assertEqual(1.0, report["sources"]["discovery_non_regulatory_share"])
        self.assertEqual(0, report["regulatory"]["queries"])

    def test_decisions_and_batch_reconcile(self) -> None:
        report = json.loads(BUILD.outputs()[HERE / "audit-report.json"])
        self.assertEqual({"duplicate": 2, "eligible": 2, "insufficient_evidence": 4},
                         report["candidates"]["decision_counts"])
        self.assertEqual(2, report["publication"]["candidate_count"])
        self.assertEqual(6, report["publication"]["profile_file_count"])
        self.assertEqual(2, report["review"]["exclusion_sample_reviewed"])
        self.assertEqual(6, report["review"]["exclusion_population"])
        self.assertGreaterEqual(report["review"]["exclusion_sample_rate"], 0.2)
        self.assertEqual(1.0, report["review"]["eligible_coverage"])
        self.assertEqual(0, report["review"]["routed_population"])
        self.assertEqual(0, report["review"]["regulatory_case_population"])

    def test_integrated_profiles_are_current_catalog_guards(self) -> None:
        report = json.loads(BUILD.outputs()[HERE / "audit-report.json"])
        change = report["baseline"]["integrated_change"]
        self.assertEqual("5b3a4e0", change["commit"])
        self.assertEqual("baseline_integrated", change["status"])
        names = {candidate["name"] for candidate in BUILD.CANDIDATES}
        self.assertNotIn("Entrypoint", names)
        self.assertNotIn("Flourish Ventures", names)

    def test_generated_artifacts_are_byte_deterministic(self) -> None:
        self.assertEqual(BUILD.outputs(), BUILD.outputs())


if __name__ == "__main__":
    unittest.main()
