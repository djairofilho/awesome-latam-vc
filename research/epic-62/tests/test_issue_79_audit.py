from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


AUDIT_ROOT = Path(__file__).resolve().parents[1] / "final-audit"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_accelerator_final_audit", AUDIT_ROOT / "build_audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FinalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.report = cls.builder.build_report()

    def test_audit_passes_without_open_findings(self) -> None:
        self.assertEqual("passed", self.report["status"])
        self.assertTrue(all(self.report["checks"].values()))
        self.assertEqual(
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
            self.report["severity_counts"],
        )

    def test_all_input_occurrences_reconcile_to_unique_candidates(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(80, metrics["input_occurrences"])
        self.assertEqual(78, metrics["canonical_candidates"])
        self.assertEqual(2, metrics["merged_duplicate_occurrences"])
        self.assertTrue(self.report["checks"]["candidate_ids_unique"])
        self.assertTrue(self.report["checks"]["all_candidates_decided"])

    def test_coverage_and_tasks_are_closed_with_documented_limits(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(37, metrics["coverage_records"])
        self.assertEqual({"complete": 29, "partial": 8}, metrics["coverage_statuses"])
        self.assertEqual(80, metrics["tasks"])
        self.assertEqual({"blocked": 6, "done": 74}, metrics["task_statuses"])
        self.assertTrue(self.report["checks"]["coverage_closed"])
        self.assertTrue(self.report["checks"]["tasks_closed"])

    def test_independent_review_resolves_boundaries(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(52, metrics["reviewed_candidates"])
        self.assertEqual(3, metrics["resolved_divergences"])
        self.assertTrue(self.report["checks"]["mandatory_review_complete"])
        self.assertTrue(self.report["checks"]["no_open_high_divergence"])
        self.assertTrue(self.report["checks"]["no_silent_cross_catalog_duplicate"])

    def test_publishable_queue_profiles_batches_and_index_are_exact(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(26, metrics["publishable_candidates"])
        self.assertEqual(26, metrics["profiles"])
        self.assertEqual([10, 10, 6], metrics["batch_sizes"])
        for key in (
            "publishable_equals_profiles",
            "batches_cover_publishable_once",
            "batch_paths_match_profiles",
            "profile_files_exact",
            "index_exact_and_unbroken",
        ):
            self.assertTrue(self.report["checks"][key], key)

    def test_hashes_evidence_routes_and_encoding_are_clean(self) -> None:
        for key in (
            "cross_category_routes_resolved",
            "profile_evidence_resolves",
            "all_frozen_hashes_match",
            "utf8_clean",
        ):
            self.assertTrue(self.report["checks"][key], key)
        self.assertTrue(
            all(not failures for failures in self.report["failures"].values())
        )

    def test_committed_report_has_no_drift(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AUDIT_ROOT / "build_audit.py"), "--check"],
            cwd=self.builder.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        committed = json.loads(
            (AUDIT_ROOT / "audit-report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.report, committed)


if __name__ == "__main__":
    unittest.main()
