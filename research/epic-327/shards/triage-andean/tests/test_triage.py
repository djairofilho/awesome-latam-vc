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


if __name__ == "__main__":
    unittest.main()
