import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SCHEMA_PATH = EPIC / "schemas" / "validation-record.schema.json"


def valid_record():
    evidence_id = "evidence-delta-example-all-gates"
    gate = {"finding": "confirmed", "evidence_ids": [evidence_id]}
    return {
        "schema_version": "1.0",
        "candidate_id": "delta-fund-example-capital",
        "input_sha256": "a" * 64,
        "validation_partition": 0,
        "cutoff_date": "2026-08-02",
        "validated_on": "2026-08-02",
        "validator": "validation-0",
        "gates": {
            "direct_investment": gate,
            "recurrence": gate,
            "recent_activity": {
                **gate,
                "latest_official_activity_on": "2024-08-02",
            },
            "latam_access": gate,
            "identity": gate,
        },
        "decision": "eligible",
        "reason": "Todos os gates foram confirmados.",
        "destination": "funds/",
        "next_action": "independent_review",
        "owner": None,
    }


class ValidationRecordSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(
            cls.schema, format_checker=FormatChecker()
        )

    def messages(self, record):
        return [error.message for error in self.validator.iter_errors(record)]

    def test_accepts_the_five_explicit_gates(self):
        self.assertEqual(self.messages(valid_record()), [])

    def test_rejects_missing_gate_and_unknown_finding(self):
        record = valid_record()
        del record["gates"]["identity"]
        record["gates"]["recurrence"]["finding"] = "unknown"
        messages = self.messages(record)
        self.assertTrue(any("identity" in message for message in messages))
        self.assertTrue(any("not one of" in message for message in messages))

    def test_blocked_gate_requires_attempt_and_forbids_evidence(self):
        record = valid_record()
        record["gates"]["recurrence"] = {
            "finding": "blocked",
            "evidence_ids": ["evidence-delta-example-blocked"],
        }
        messages = self.messages(record)
        self.assertTrue(any("blocking_outcome" in message for message in messages))
        self.assertTrue(any("expected to be empty" in message for message in messages))

    def test_insufficient_evidence_requires_owner_and_follow_up(self):
        record = valid_record()
        record.update(
            {
                "decision": "insufficient_evidence",
                "destination": None,
                "next_action": "independent_review",
                "owner": None,
            }
        )
        messages = self.messages(record)
        self.assertTrue(any("not one of" in message for message in messages))
        self.assertTrue(any("not of type 'string'" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
