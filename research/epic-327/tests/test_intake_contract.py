import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"


class NormalizedIntakeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (EPIC / "schemas" / "normalized-intake-record.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.validator = Draft202012Validator(cls.schema)

    def test_minimal_new_candidate_is_valid(self):
        record = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-exemplo-capital",
            "name": "Exemplo Capital",
            "country_occurrences": {"BR": 2, "CL": 1},
            "occurrence_count": 3,
            "baseline_status": "new",
            "baseline_matches": [],
        }
        self.validator.validate(record)
        self.assertEqual(
            record["occurrence_count"], sum(record["country_occurrences"].values())
        )

    def test_match_requires_canonical_profile(self):
        record = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-exemplo-capital",
            "name": "Exemplo Capital",
            "country_occurrences": {"BR": 1},
            "occurrence_count": 1,
            "baseline_status": "exact_name",
            "baseline_matches": [],
        }
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_discovery_provenance_and_facts_are_rejected(self):
        record = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-exemplo-capital",
            "name": "Exemplo Capital",
            "country_occurrences": {"BR": 1},
            "occurrence_count": 1,
            "baseline_status": "new",
            "baseline_matches": [],
            "discovery_url": "https://example.invalid/list",
            "stage": "seed",
        }
        self.assertTrue(list(self.validator.iter_errors(record)))


if __name__ == "__main__":
    unittest.main()
