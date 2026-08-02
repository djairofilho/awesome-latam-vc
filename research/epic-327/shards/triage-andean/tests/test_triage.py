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


if __name__ == "__main__":
    unittest.main()
