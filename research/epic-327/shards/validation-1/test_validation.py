from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("validation_1_validator", HERE / "validate.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ValidationOneTest(unittest.TestCase):
    def test_shard_is_complete_and_reconciled(self) -> None:
        self.assertEqual([], VALIDATOR.validate())


if __name__ == "__main__":
    unittest.main()
