import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research" / "epic-256" / "bpv"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class BpvPrefreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = read_json(AUDIT / "contract.json")
        cls.sources = read_jsonl(AUDIT / "source-inventory.jsonl")
        cls.candidates = read_jsonl(AUDIT / "candidates.jsonl")
        cls.evidence = read_jsonl(AUDIT / "evidence.jsonl")
        cls.regulator = read_jsonl(AUDIT / "regulator-query-log.jsonl")
        cls.coverage = read_json(AUDIT / "coverage-matrix.json")
        cls.request = read_json(AUDIT / "review-request.json")
        cls.manifest = read_json(AUDIT / "prefreeze-manifest.json")

    def test_contract_and_markets_are_frozen(self):
        self.assertEqual(self.contract["markets"], ["BO", "PY", "VE"])
        self.assertEqual(self.contract["cutoff"], "2026-07-30")
        self.assertEqual(self.contract["publication_batch_limit"], 10)
        self.assertEqual(self.contract["coverage_claim"], "audited_coverage")

    def test_candidate_universe_is_terminal_and_non_regulatory(self):
        self.assertEqual(len(self.candidates), 20)
        self.assertEqual(len({row["candidate_id"] for row in self.candidates}), 20)
        self.assertTrue(all(row["status"] == "terminal" for row in self.candidates))
        self.assertTrue(all(row["discovery_origin"] != "regulatory" for row in self.candidates))
        source_ids = {row["source_id"] for row in self.sources}
        self.assertTrue(all(set(row["discovery_source_ids"]) <= source_ids for row in self.candidates))

    def test_regulator_is_five_percent_and_identity_only(self):
        self.assertEqual(len(self.regulator), 1)
        self.assertEqual(self.coverage["regulatory_case_percent"], 5.0)
        self.assertEqual(self.regulator[0]["effect"], "identity_note_only")
        self.assertIn("not used for discovery or eligibility", self.regulator[0]["result"])

    def test_all_eligible_have_official_evidence(self):
        evidence = {row["candidate_id"]: row for row in self.evidence}
        eligible = [row for row in self.candidates if row["decision"] == "eligible"]
        self.assertEqual(
            [row["candidate_id"] for row in eligible],
            ["py-cibersons", "bo-yango-ventures", "ve-impulsa", "ve-epakon"],
        )
        for row in eligible:
            self.assertEqual(evidence[row["candidate_id"]]["claims"]["official_evidence"], "confirmed")
            self.assertIsNotNone(row["canonical_destination"])

    def test_cibersons_handoff_has_explicit_base_evidence(self):
        cibersons = next(row for row in self.candidates if row["candidate_id"] == "py-cibersons")
        self.assertEqual(cibersons["discovery_origin"], "handoff_audited_non_regulatory")
        base = self.request["base_geography_checks"]["py-cibersons"]
        self.assertEqual(base["proposed_base"], "PY")
        self.assertGreaterEqual(len(base["supporting_sources"]), 3)
        self.assertIn("founder nationality", base["not_inferred_from"])

    def test_routing_and_exclusion_sample(self):
        decisions = {row["candidate_id"]: row["decision"] for row in self.candidates}
        self.assertTrue(all(decisions[candidate] == "routed" for candidate in self.request["routed_to_review"]))
        self.assertTrue(all(decisions[candidate] == "insufficient_evidence" for candidate in self.request["deterministic_exclusion_sample"]))
        self.assertGreaterEqual(
            len(self.request["deterministic_exclusion_sample"]),
            len([row for row in self.candidates if row["decision"] == "insufficient_evidence"]) * 0.2,
        )

    def test_sources_are_complete_or_gap_justified(self):
        self.assertTrue(all(row["status"] in {"complete", "gap_justified"} for row in self.sources))
        self.assertTrue(all(row["url"] and row["family"] and row["scope"] and row["accessed_on"] for row in self.sources))

    def test_prefreeze_cannot_publish(self):
        self.assertEqual(self.request["status"], "pending_independent_review")
        self.assertFalse(self.request["freeze_allowed"])
        self.assertEqual(self.manifest["status"], "awaiting_independent_review")
        self.assertFalse(self.manifest["freeze_allowed"])
        self.assertFalse((AUDIT / "freeze-manifest.json").exists())
        self.assertFalse((AUDIT / "publication-report.json").exists())

    def test_manifest_hashes(self):
        for relative, expected in self.manifest["artifact_hashes"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)

    def test_no_mojibake(self):
        bad = ["Ã", "Â", "�", "^G"]
        for path in AUDIT.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertFalse(any(token in text for token in bad), path)


if __name__ == "__main__":
    unittest.main()
