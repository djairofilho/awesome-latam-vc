import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/epic-258/latin-caribbean"


def jsonl(name):
    return [
        json.loads(line)
        for line in (AUDIT / name).read_text(encoding="utf-8").splitlines()
        if line
    ]


class LatinCaribbeanAuditTest(unittest.TestCase):
    def test_every_candidate_has_a_terminal_decision_and_known_source(self):
        candidates = jsonl("candidates.jsonl")
        source_ids = {row["source_id"] for row in jsonl("source-inventory.jsonl")}
        terminal = {"eligible", "duplicate", "routed", "excluded", "insufficient_evidence"}
        self.assertEqual(53, len(candidates))
        self.assertTrue(all(row["decision"] in terminal for row in candidates))
        self.assertTrue(all(row["reason"] for row in candidates))
        self.assertTrue(all(set(row["discovery_source_ids"]) <= source_ids for row in candidates))

    def test_blind_search_is_isolated_and_fully_reconciled(self):
        blind = json.loads((AUDIT / "blind-search.json").read_text(encoding="utf-8"))
        candidates = jsonl("candidates.jsonl")
        blind_candidates = [
            row for row in candidates if "src-258-blind-review" in row["discovery_source_ids"]
        ]
        evidence_ids = {row["candidate_id"] for row in jsonl("evidence.jsonl")}
        self.assertFalse(blind["candidate_list_visible_before_search"])
        self.assertEqual(29, blind["canonical_leads_returned"])
        self.assertEqual(29, len(blind_candidates))
        self.assertTrue(all(row["candidate_id"] in evidence_ids for row in blind_candidates))

    def test_regulators_are_identity_only_and_not_quota_filling(self):
        candidates = jsonl("candidates.jsonl")
        queries = [
            row for row in jsonl("regulator-query-log.jsonl")
            if row["record_type"] == "query"
        ]
        self.assertEqual(2, len(queries))
        self.assertTrue(all(row["purpose"] in {"identity", "divergence"} for row in queries))
        self.assertTrue(all(not row["used_for_eligibility"] for row in queries))
        self.assertAlmostEqual(2 / len(candidates), 0.0377, places=4)
        curve = json.loads((AUDIT / "discovery-curve.json").read_text(encoding="utf-8"))
        self.assertIn("no artificial regulator queries", curve["regulator_target_status"])

    def test_proposed_publication_is_one_bounded_batch(self):
        review = json.loads((AUDIT / "review-request.json").read_text(encoding="utf-8"))
        proposed = review["proposed_freeze"]
        self.assertEqual(1, proposed["publication_batch_count"])
        self.assertLessEqual(proposed["publication_action_count"], 10)
        self.assertEqual(6, proposed["publication_action_count"])

    def test_no_mojibake(self):
        bad = ("Ã", "Â", "�", "\x07")
        paths = (
            list(AUDIT.rglob("*.json"))
            + list(AUDIT.rglob("*.jsonl"))
            + list(AUDIT.rglob("*.md"))
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in bad), path)


if __name__ == "__main__":
    unittest.main()
