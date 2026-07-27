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
        "build_angel_final_audit", AUDIT_ROOT / "build_audit.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AngelFinalAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.report = cls.builder.build_report()

    def test_audit_passes_without_open_findings(self):
        self.assertEqual("passed", self.report["status"])
        self.assertTrue(all(self.report["checks"].values()))
        self.assertEqual(
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
            self.report["severity_counts"],
        )

    def test_all_44_candidates_have_one_final_decision(self):
        metrics = self.report["metrics"]
        self.assertEqual(44, metrics["candidates"])
        self.assertEqual(44, sum(metrics["decision_counts"].values()))
        self.assertEqual(
            {
                "duplicado": 2,
                "elegível": 11,
                "encaminhado-para-aceleradoras": 2,
                "encaminhado-para-funds": 4,
                "encaminhado-para-plataformas": 5,
                "encaminhado-para-programas-públicos": 1,
                "evidência-insuficiente": 16,
                "excluído": 1,
                "inativo": 2,
            },
            metrics["decision_counts"],
        )

    def test_eleven_eligible_profiles_reconcile_five_plus_six(self):
        metrics = self.report["metrics"]
        self.assertEqual(11, metrics["eligible"])
        self.assertEqual(11, metrics["profiles"])
        self.assertEqual(5, metrics["preserved_profiles"])
        self.assertEqual(6, metrics["new_profiles"])
        for key in (
            "eligible_queue_exact",
            "publication_split_exact",
            "profiles_exact",
            "no_individual_investor_published",
        ):
            self.assertTrue(self.report["checks"][key], key)

    def test_coverage_and_frozen_tasks_are_closed(self):
        metrics = self.report["metrics"]
        self.assertEqual(42, metrics["coverage_rows"])
        self.assertEqual(
            {"concluída": 32, "não aplicável": 1, "parcial": 9},
            metrics["coverage_statuses"],
        )
        self.assertEqual(6, metrics["runs"])
        self.assertEqual(47, metrics["tasks"])
        self.assertEqual({"blocked": 1, "done": 46}, metrics["task_statuses"])
        self.assertTrue(self.report["checks"]["coverage_unique_and_closed"])
        self.assertTrue(self.report["checks"]["runs_and_tasks_closed"])

    def test_identity_transfers_and_actors_are_resolved(self):
        metrics = self.report["metrics"]
        self.assertEqual(7, metrics["identity_resolutions"])
        self.assertEqual(12, metrics["identity_subjects"])
        self.assertEqual(12, metrics["outgoing_category_transfers"])
        self.assertTrue(self.report["checks"]["identities_resolved"])
        self.assertTrue(self.report["checks"]["transfers_resolved"])
        self.assertTrue(self.report["checks"]["actors_separated_for_eligible"])

    def test_hashes_indexes_links_sources_and_encoding_are_clean(self):
        for key in (
            "candidate_references_resolve",
            "indexes_exact",
            "no_broken_index_links",
            "official_links_embedded",
            "all_frozen_hashes_match",
            "utf8_clean",
        ):
            self.assertTrue(self.report["checks"][key], key)
        self.assertTrue(
            all(not failures for failures in self.report["failures"].values())
        )

    def test_pad_udep_is_excluded_and_high_divergence_is_closed(self):
        self.assertTrue(all(self.report["pad_checks"].values()))
        self.assertTrue(self.report["checks"]["pad_excluded"])
        self.assertTrue(self.report["checks"]["independent_review_complete"])
        self.assertTrue(self.report["checks"]["no_high_divergence_open"])

    def test_committed_report_is_deterministic_and_has_no_drift(self):
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
