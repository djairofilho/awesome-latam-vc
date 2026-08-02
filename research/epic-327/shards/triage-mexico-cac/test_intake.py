from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validate_intake", HERE / "validate_intake.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class IntakeTests(unittest.TestCase):
    def test_intake_is_reconciled_and_valid(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_summary_accounts_for_every_investor_occurrence(self) -> None:
        summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
        gaps = json.loads((HERE / "gaps.json").read_text(encoding="utf-8"))
        intake = VALIDATOR.read_jsonl(HERE / "intake.jsonl")
        materialized = sum(row["occurrence_count"] for row in intake)
        self.assertEqual(summary["raw_occurrences"], materialized + gaps["unparsed_rows"])
        self.assertEqual(62, summary["pages_processed"])

    def test_intake_contains_only_minimum_normalized_fields(self) -> None:
        intake = VALIDATOR.read_jsonl(HERE / "intake.jsonl")
        allowed = VALIDATOR.EXPECTED_FIELDS | VALIDATOR.OPTIONAL_FIELDS
        self.assertTrue(all(set(row) <= allowed for row in intake))
        self.assertTrue(all("..." not in row["name"] for row in intake))


if __name__ == "__main__":
    unittest.main()
