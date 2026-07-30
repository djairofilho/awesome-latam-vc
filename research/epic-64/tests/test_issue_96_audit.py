from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "final-audit"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_platform_final_audit", ROOT / "build_audit.py"
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

    def test_all_candidates_have_one_destination(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(39, metrics["candidates"])
        self.assertEqual(39, sum(metrics["decision_counts"].values()))
        self.assertTrue(self.report["checks"]["candidate_ids_unique"])
        self.assertTrue(self.report["checks"]["all_candidates_decided"])

    def test_eligible_queue_and_profiles_reconcile_exactly(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(9, metrics["eligible"])
        self.assertEqual(9, metrics["published"])
        self.assertEqual(30, metrics["not_published"])
        self.assertTrue(
            self.report["checks"]["eligible_published_exactly_once"]
        )
        self.assertTrue(self.report["checks"]["noneligible_not_published"])

    def test_coverage_and_tasks_are_closed(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(20, metrics["countries"])
        self.assertEqual(80, metrics["coverage_cells"])
        self.assertEqual(93, metrics["tasks"])
        self.assertTrue(self.report["checks"]["coverage_cells_complete"])
        self.assertTrue(self.report["checks"]["coverage_statuses_closed"])
        self.assertEqual({"blocked": 35, "done": 58}, metrics["task_statuses"])
        self.assertTrue(self.report["checks"]["all_tasks_closed"])

    def test_captable_boundary_case_is_fully_revalidated(self) -> None:
        self.assertTrue(all(self.report["captable_checks"].values()))

    def test_hashes_links_evidence_and_encoding_are_clean(self) -> None:
        for key in (
            "all_frozen_hashes_match",
            "all_indexes_exact",
            "no_broken_index_links",
            "all_candidate_evidence_resolves",
            "all_official_evidence_urls_valid",
            "utf8_clean",
        ):
            self.assertTrue(self.report["checks"][key], key)
        self.assertTrue(
            all(not failures for failures in self.report["failures"].values())
        )

    def test_global_index_projection_allows_unrelated_fund_rows_only(self) -> None:
        for filename, expected in self.builder.GLOBAL_INDEX_PROJECTIONS.items():
            self.assertEqual(
                expected,
                self.builder.global_index_projection(
                    (self.builder.ROOT / filename).read_text(encoding="utf-8")
                ),
            )
            self.assertNotEqual(
                expected,
                self.builder.global_index_projection(
                    "\n".join((*expected[:2], expected[2] + " alterada", expected[3]))
                ),
            )
            self.assertNotEqual(
                expected,
                self.builder.global_index_projection(
                    "\n".join(reversed(expected))
                ),
            )

    def test_category_routes_and_review_are_closed(self) -> None:
        metrics = self.report["metrics"]
        self.assertEqual(3, metrics["incoming_category_transfers"])
        self.assertEqual(6, metrics["outgoing_category_transfers"])
        self.assertTrue(self.report["checks"]["incoming_routes_adjudicated"])
        self.assertTrue(self.report["checks"]["outgoing_routes_resolved"])
        self.assertTrue(self.report["checks"]["independent_review_complete"])
        self.assertTrue(self.report["checks"]["no_high_divergence_open"])

    def test_committed_report_has_no_drift(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_audit.py"), "--check"],
            cwd=self.builder.ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        committed = json.loads(
            (ROOT / "audit-report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.report, committed)


if __name__ == "__main__":
    unittest.main()
