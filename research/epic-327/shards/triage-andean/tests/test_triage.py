from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("andean_triage_validator", HERE / "validate_triage.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class AndeanTriageTest(unittest.TestCase):
    def test_triage_uses_only_official_evidence(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_every_candidate_has_terminal_coverage(self) -> None:
        triage = VALIDATOR.load_jsonl(HERE / "triage.jsonl")
        searches = VALIDATOR.load_jsonl(HERE / "search-log.jsonl")
        resolved = {
            row["candidate_id"]
            for row in triage
            if row["triage_status"] != "unresolved"
        }
        searched = {row["candidate_id"] for row in searches}

        self.assertTrue(resolved.isdisjoint(searched))
        self.assertEqual({row["candidate_id"] for row in triage}, resolved | searched)

    def test_audited_conflicts_have_terminal_searches(self) -> None:
        triage = {
            row["candidate_id"]: row
            for row in VALIDATOR.load_jsonl(HERE / "triage.jsonl")
        }
        evidence = VALIDATOR.load_jsonl(HERE / "official-evidence.jsonl")
        searches = {
            row["candidate_id"]
            for row in VALIDATOR.load_jsonl(HERE / "search-log.jsonl")
        }
        corrected = {
            "delta-fund-bridge-partners",
            "delta-fund-city-of-knowledge",
            "delta-fund-k50-ventures",
            "delta-fund-regen-ventures",
            "delta-fund-strategic-group",
        }
        self.assertTrue(
            all(triage[candidate_id]["triage_status"] == "unresolved" for candidate_id in corrected)
        )
        self.assertTrue(corrected <= searches)
        self.assertTrue(corrected.isdisjoint({row["candidate_id"] for row in evidence}))

        citius = triage["delta-fund-citius"]
        self.assertEqual("official_identity_resolved", citius["triage_status"])
        self.assertEqual("citius.vc", citius["official_domain"])


if __name__ == "__main__":
    unittest.main()
