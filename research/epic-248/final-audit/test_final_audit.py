import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("audit.py")
SPEC = importlib.util.spec_from_file_location("epic248_final_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Epic248FinalAuditTests(unittest.TestCase):
    def setUp(self):
        self.report = AUDIT.audit()

    def test_aggregate_metrics_match_frozen_geographic_and_handoff_universes(self):
        self.assertEqual("passed", self.report["status"])
        self.assertEqual(214, self.report["core_geographic"]["candidate_count"])
        self.assertEqual(35, self.report["core_geographic"]["eligible_publications"])
        self.assertEqual(217, self.report["combined"]["candidate_count"])
        self.assertEqual(38, self.report["combined"]["eligible_publications"])
        self.assertEqual(12, self.report["combined"]["regulator_queries"])

    def test_publication_is_localized_unique_and_terminal(self):
        self.assertEqual(
            38,
            self.report["publication_integrity"]["unique_eligible_destinations"],
        )
        self.assertEqual(
            114,
            self.report["publication_integrity"]["localized_profiles_checked"],
        )
        self.assertTrue(
            self.report["publication_integrity"]["eligible_published_exactly_once"]
        )
        self.assertTrue(self.report["controls"]["all_candidates_terminal"])
        self.assertTrue(self.report["controls"]["all_planned_sources_terminal"])

    def test_regulatory_policy_and_review_gate_are_reconciled(self):
        core = self.report["core_geographic"]
        self.assertGreaterEqual(core["regulator_source_share_pct"], 5)
        self.assertLessEqual(core["regulator_source_share_pct"], 10)
        self.assertTrue(self.report["controls"]["regulators_used_for_identity_only"])
        self.assertEqual(0, self.report["controls"]["critical_open"])
        self.assertEqual(0, self.report["controls"]["high_open"])


if __name__ == "__main__":
    unittest.main()
