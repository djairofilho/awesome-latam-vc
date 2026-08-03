from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("triage_validator", HERE / "validate_triage.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def load_jsonl(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (HERE / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class SouthernConeBrazilTriageTests(unittest.TestCase):
    def test_triage_is_valid(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_every_candidate_has_baseline_identity_or_documented_search(self) -> None:
        records = load_jsonl("triage.jsonl")
        baseline = [row for row in records if row["search"]["outcome"] == "baseline_match"]
        searched = [row for row in records if row["search"]["query"] is not None]
        self.assertEqual(735, len(records))
        self.assertEqual(79, len(baseline))
        self.assertEqual(656, len(searched))
        self.assertEqual(len(records), len(baseline) + len(searched))

    def test_official_evidence_is_separate_and_linked(self) -> None:
        records = load_jsonl("triage.jsonl")
        evidence = load_jsonl("official-evidence.jsonl")
        linked = {
            evidence_id
            for record in records
            for evidence_id in record["evidence_ids"]
        }
        self.assertEqual(240, len(evidence))
        self.assertEqual(linked, {item["evidence_id"] for item in evidence})
        self.assertNotIn("\"results\"", (HERE / "triage.jsonl").read_text(encoding="utf-8"))

    def test_audited_ambiguous_identities_are_not_confirmed(self) -> None:
        records = {row["candidate_id"]: row for row in load_jsonl("triage.jsonl")}
        evidence_candidates = {
            row["candidate_id"] for row in load_jsonl("official-evidence.jsonl")
        }

        bridge = records["delta-fund-bridge-partners"]
        self.assertEqual("identity_collision", bridge["identity"]["status"])
        self.assertEqual([], bridge["evidence_ids"])
        self.assertNotIn("delta-fund-bridge-partners", evidence_candidates)

        for candidate_id in ("delta-fund-k50-ventures", "delta-fund-upload-ventures"):
            self.assertEqual("not_confirmed", records[candidate_id]["identity"]["status"])
            self.assertEqual([], records[candidate_id]["evidence_ids"])

    def test_category_claims_use_singular_vocabulary(self) -> None:
        allowed = {"accelerator", "angel_network", "public_program"}
        categories = {
            claim["value"]
            for row in load_jsonl("official-evidence.jsonl")
            for claim in row["claims"]
            if claim["field"] == "category"
        }
        self.assertTrue(categories)
        self.assertTrue(categories <= allowed)


if __name__ == "__main__":
    unittest.main()
