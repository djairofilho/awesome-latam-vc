import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("measurement_validate", ROOT / "validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


class MeasurementContractTests(unittest.TestCase):
    def test_bundle_is_valid(self) -> None:
        VALIDATE.main()

    def test_credentials_and_personal_data_are_rejected(self) -> None:
        for key in sorted(VALIDATE.FORBIDDEN_KEYS):
            with self.subTest(key=key):
                with self.assertRaises(AssertionError):
                    VALIDATE.walk({key: "must-not-be-versioned"})


if __name__ == "__main__":
    unittest.main()
