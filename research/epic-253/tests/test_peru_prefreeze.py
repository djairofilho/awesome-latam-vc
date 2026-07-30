import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/epic-253/peru"


def rows(name):
    return [json.loads(line) for line in (AUDIT / name).read_text(encoding="utf-8").splitlines() if line]


class PeruPrefreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(AUDIT / "build_prefreeze.py")], check=True)

    def test_discovery_is_non_regulatory(self):
        self.assertTrue(all(row["discovery_origin"] == "non_regulatory" for row in rows("candidates.jsonl")))

    def test_regulator_target(self):
        candidates = rows("candidates.jsonl")
        regulators = [row for row in rows("source-inventory.jsonl") if row["family"] == "regulator_identity"]
        ratio = 100 * len(regulators) / len(candidates)
        self.assertGreaterEqual(ratio, 5)
        self.assertLessEqual(ratio, 10)

    def test_every_candidate_has_decision(self):
        allowed = {"eligible", "insufficient_evidence", "routed", "routed_cross_market", "duplicate"}
        self.assertTrue(all(row["decision"] in allowed for row in rows("candidates.jsonl")))

    def test_review_is_reconciled_and_freeze_exists(self):
        review = json.loads((AUDIT / "review.json").read_text(encoding="utf-8"))
        self.assertEqual("approved", review["status"])
        self.assertTrue(review["freeze_allowed"])
        self.assertTrue(review["review_reconciled"])
        self.assertTrue((AUDIT / "freeze-manifest.json").exists())
        self.assertFalse((AUDIT / "publication").exists())

    def test_no_local_eligible_and_impaqto_is_routed(self):
        eligible = [row["candidate_id"] for row in rows("candidates.jsonl") if row["decision"] == "eligible"]
        self.assertEqual([], eligible)
        impaqto = next(row for row in rows("candidates.jsonl") if row["candidate_id"] == "pe-impaqto-capital")
        self.assertEqual("routed_cross_market", impaqto["decision"])
        self.assertIn("#255", impaqto["canonical_destination"])

    def test_terminal_counts(self):
        counts = {}
        for row in rows("candidates.jsonl"):
            counts[row["decision"]] = counts.get(row["decision"], 0) + 1
        self.assertEqual(2, counts["insufficient_evidence"])
        self.assertEqual(4, counts["routed"])
        self.assertEqual(1, counts["routed_cross_market"])
        self.assertEqual(8, counts["duplicate"])

    def test_new_artifacts_have_no_mojibake(self):
        for path in list(AUDIT.rglob("*.json")) + list(AUDIT.rglob("*.jsonl")):
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in ("Ã", "Â", "�")), path)


if __name__ == "__main__":
    unittest.main()
