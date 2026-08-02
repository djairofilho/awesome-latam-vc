from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("intake_validator", HERE / "validate.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SouthernConeBrazilIntakeTests(unittest.TestCase):
    def test_intake_is_valid_and_reconciled(self) -> None:
        self.assertEqual([], VALIDATOR.validate())

    def test_raw_occurrence_equation(self) -> None:
        summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
        gaps = json.loads((HERE / "gaps.json").read_text(encoding="utf-8"))
        rows = [
            json.loads(line)
            for line in (HERE / "intake.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        materialized = sum(row["occurrence_count"] for row in rows)
        self.assertEqual(1284, materialized)
        self.assertEqual(343, gaps["unmaterialized_occurrences"])
        self.assertEqual(1627, summary["raw_occurrences"])
        self.assertEqual(summary["raw_occurrences"], materialized + gaps["unmaterialized_occurrences"])

    def test_no_discovery_provenance_is_persisted(self) -> None:
        text = (HERE / "intake.jsonl").read_text(encoding="utf-8")
        for forbidden in ("discovery_reference", "source_url", "\"url\""):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
