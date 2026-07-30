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
        allowed = {"eligible", "insufficient_evidence", "routed", "duplicate"}
        self.assertTrue(all(row["decision"] in allowed for row in rows("candidates.jsonl")))

    def test_freeze_and_publication_are_blocked(self):
        request = json.loads((AUDIT / "review-request.json").read_text(encoding="utf-8"))
        self.assertEqual("awaiting_integrator_review", request["status"])
        self.assertFalse(request["freeze_allowed"])
        self.assertFalse((AUDIT / "freeze-manifest.json").exists())
        self.assertFalse((AUDIT / "publication").exists())

    def test_only_expected_eligible(self):
        eligible = [row["candidate_id"] for row in rows("candidates.jsonl") if row["decision"] == "eligible"]
        self.assertEqual(["pe-impaqto-capital"], eligible)

    def test_new_artifacts_have_no_mojibake(self):
        for path in list(AUDIT.rglob("*.json")) + list(AUDIT.rglob("*.jsonl")):
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in ("Ã", "Â", "�")), path)


if __name__ == "__main__":
    unittest.main()
