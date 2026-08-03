from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_triage", HERE / "validate_triage.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class TriageTests(unittest.TestCase):
    def test_every_candidate_has_official_domain_or_documented_search(self) -> None:
        triage = VALIDATOR.read_jsonl(HERE / "triage.jsonl")
        self.assertEqual(528, len(triage))
        self.assertTrue(
            all(row["official_domain"] or row["search"]["query"] for row in triage)
        )

    def test_identity_evidence_is_separate_and_schema_valid(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_unresolved_records_do_not_infer_category_or_facts(self) -> None:
        triage = VALIDATOR.read_jsonl(HERE / "triage.jsonl")
        unresolved = [row for row in triage if row["status"] == "identity_unresolved"]
        self.assertTrue(unresolved)
        self.assertTrue(all(row["category"] == "unresolved" for row in unresolved))
        self.assertTrue(all(not row["evidence_ids"] for row in unresolved))

    def test_audited_identity_conflicts_remain_unresolved(self) -> None:
        triage = {
            row["candidate_id"]: row
            for row in VALIDATOR.read_jsonl(HERE / "triage.jsonl")
        }
        evidence = VALIDATOR.read_jsonl(HERE / "official-evidence.jsonl")
        corrected = {
            "delta-fund-bridge-partners",
            "delta-fund-chiron",
            "delta-fund-citius",
            "delta-fund-city-of-knowledge",
            "delta-fund-core-ventures",
            "delta-fund-k50-ventures",
            "delta-fund-upload-ventures",
        }
        self.assertTrue(
            all(triage[candidate_id]["status"] == "identity_unresolved" for candidate_id in corrected)
        )
        self.assertTrue(
            corrected.isdisjoint({row["candidate_id"] for row in evidence})
        )

    def test_enlaces_evidence_claims_only_literal_identity(self) -> None:
        evidence = VALIDATOR.read_jsonl(HERE / "official-evidence.jsonl")
        enlaces = next(
            row for row in evidence if row["candidate_id"] == "delta-fund-enlaces"
        )
        self.assertEqual(["identity"], [claim["field"] for claim in enlaces["claims"]])


if __name__ == "__main__":
    unittest.main()
