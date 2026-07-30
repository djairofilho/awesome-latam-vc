import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/epic-254/uruguay"


def jsonl(name):
    return [
        json.loads(line)
        for line in (AUDIT / name).read_text(encoding="utf-8").splitlines()
        if line
    ]


class UruguayAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(AUDIT / "build.py")], check=True)

    def test_discovery_is_non_regulatory(self):
        candidates = jsonl("candidates.jsonl")
        self.assertEqual(36, len(candidates))
        self.assertTrue(all(row["discovery_origin"] == "non_regulatory" for row in candidates))
        self.assertTrue(all(row["discovery_source_ids"] for row in candidates))

    def test_regulator_is_selective_and_identity_only(self):
        candidates = jsonl("candidates.jsonl")
        queries = jsonl("regulatory-query-log.jsonl")
        share = 100 * len(queries) / len(candidates)
        self.assertGreaterEqual(share, 5)
        self.assertLessEqual(share, 10)
        self.assertTrue(all(not row["used_for_discovery"] for row in queries))
        self.assertTrue(all(not row["used_for_eligibility"] for row in queries))
        self.assertEqual({"identity_only", "divergence_only"}, {row["effect"] for row in queries})

    def test_every_candidate_has_evidence_and_terminal_decision(self):
        candidates = jsonl("candidates.jsonl")
        evidence = jsonl("evidence.jsonl")
        source_ids = {row["source_id"] for row in jsonl("source-inventory.jsonl")}
        self.assertEqual(len(candidates), len(evidence))
        self.assertEqual(
            {row["candidate_id"] for row in candidates},
            {row["candidate_id"] for row in evidence},
        )
        self.assertTrue(all(row["reason"] for row in candidates))
        self.assertTrue(all(set(row["discovery_source_ids"]) <= source_ids for row in candidates))
        self.assertTrue(
            all(row["decision"] in {"eligible", "duplicate", "routed", "insufficient_evidence"} for row in candidates)
        )

    def test_uruguay_base_is_confirmed_for_every_eligible(self):
        evidence = {row["candidate_id"]: row for row in jsonl("evidence.jsonl")}
        eligible = [row for row in jsonl("candidates.jsonl") if row["decision"] == "eligible"]
        self.assertEqual(5, len(eligible))
        self.assertTrue(all(evidence[row["candidate_id"]]["gates"]["uruguay_base"] == "confirmed" for row in eligible))

    def test_review_sample_is_deterministic_and_at_least_twenty_percent(self):
        review = json.loads((AUDIT / "review.json").read_text(encoding="utf-8"))
        self.assertEqual("approved", review["status"])
        self.assertEqual("integrator", review["reviewer"])
        self.assertTrue(review["review_reconciled"])
        self.assertEqual(0, review["critical_or_high_findings_open"])
        self.assertGreaterEqual(len(review["exclusion_sample"]) / review["exclusion_population"], 0.2)
        self.assertIn("SHA-256", review["exclusion_sample_rule"])

    def test_blind_search_and_saturation_are_recorded(self):
        coverage = json.loads((AUDIT / "coverage-matrix.json").read_text(encoding="utf-8"))
        self.assertTrue(coverage["blind_search"]["candidate_list_withheld"])
        self.assertGreaterEqual(len(coverage["blind_search"]["families"]), 2)
        self.assertEqual(0, coverage["marginal_passes"][-1]["new_canonical_candidates"])

    def test_every_planned_source_has_owner_and_terminal_state(self):
        sources = jsonl("source-inventory.jsonl")
        self.assertTrue(all(row["owner"] for row in sources))
        self.assertTrue(all(row["result"] in {"complete", "gap_justified"} for row in sources))

    def test_frozen_batch_has_complete_translations(self):
        freeze = json.loads((AUDIT / "freeze-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("frozen", freeze["status"])
        batch = freeze["publication_batches"][0]
        self.assertEqual(5, batch["candidate_count"])
        self.assertEqual(15, batch["profile_file_count"])
        for item in batch["candidates"]:
            destination = Path(item["destination"])
            paths = [
                ROOT / destination,
                ROOT / "translations/es" / destination,
                ROOT / "translations/pt-BR" / destination,
            ]
            for path in paths:
                self.assertTrue(path.is_file(), path)
                self.assertIn("\n## ", path.read_text(encoding="utf-8"))

    def test_no_mojibake(self):
        bad = ("Ã", "Â", "�", "\x07")
        freeze = json.loads((AUDIT / "freeze-manifest.json").read_text(encoding="utf-8"))
        profile_paths = []
        for item in freeze["publication_batches"][0]["candidates"]:
            destination = Path(item["destination"])
            profile_paths += [
                ROOT / destination,
                ROOT / "translations/es" / destination,
                ROOT / "translations/pt-BR" / destination,
            ]
        for path in list(AUDIT.rglob("*.json")) + list(AUDIT.rglob("*.jsonl")) + list(AUDIT.rglob("*.md")) + profile_paths:
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in bad), path)


if __name__ == "__main__":
    unittest.main()
