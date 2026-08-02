import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location(
    "delta_consolidation", EPIC / "consolidation" / "reduce.py"
)
REDUCER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REDUCER)


def group(triage, baseline_profiles=()):
    return {
        "names": {"Example Capital"},
        "countries": Counter({"BR": 2}),
        "source_shards": {"triage-southern-cone-brazil"},
        "baseline_profiles": set(baseline_profiles),
        "triage": [triage],
    }


class ConsolidationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(
            (EPIC / "schemas" / "consolidated-candidate.schema.json").read_text(
                encoding="utf-8"
            )
        )
        cls.validator = Draft202012Validator(schema)

    def test_partition_is_deterministic_and_bounded(self):
        candidate_id = "delta-fund-example-capital"
        self.assertEqual(REDUCER.partition(candidate_id), REDUCER.partition(candidate_id))
        self.assertIn(REDUCER.partition(candidate_id), {0, 1, 2})

    def test_baseline_match_is_terminal_duplicate(self):
        record = REDUCER.preliminary(
            "delta-fund-example-capital",
            group(
                {
                    "status": "duplicate",
                    "canonical_profile": "funds/example-capital.md",
                    "evidence_ids": [],
                },
                baseline_profiles={"funds/example-capital.md"},
            ),
        )
        self.assertEqual(record["status"], "duplicate")
        self.assertEqual(record["canonical_profile"], "funds/example-capital.md")
        self.validator.validate(record)

    def test_positive_identity_advances_only_with_domain_and_evidence(self):
        complete = REDUCER.preliminary(
            "delta-fund-example-capital",
            group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "example.com",
                    "evidence_ids": ["evidence-delta-example-capital-identity"],
                }
            ),
        )
        incomplete = REDUCER.preliminary(
            "delta-fund-example-without-evidence",
            group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "example.org",
                    "evidence_ids": [],
                }
            ),
        )
        self.assertEqual(complete["status"], "ready_for_validation")
        self.assertEqual(incomplete["status"], "unresolved")

    def test_route_without_destination_is_conflict(self):
        record = REDUCER.preliminary(
            "delta-fund-example-capital",
            group(
                {
                    "status": "routed",
                    "category": "accelerator",
                    "evidence_ids": ["evidence-delta-example-capital-identity"],
                }
            ),
        )
        self.assertEqual(record["status"], "identity_conflict")
        self.assertIsNone(record["validation_partition"])
        self.validator.validate(record)


if __name__ == "__main__":
    unittest.main()
