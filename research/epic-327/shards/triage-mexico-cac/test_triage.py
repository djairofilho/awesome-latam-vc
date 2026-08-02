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


if __name__ == "__main__":
    unittest.main()
