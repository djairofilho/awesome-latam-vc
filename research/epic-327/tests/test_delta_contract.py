from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("delta_validator", HERE / "validate.py")
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def schema(name: str) -> dict:
    return json.loads((HERE / "schemas" / name).read_text(encoding="utf-8"))


class DeltaContractTests(unittest.TestCase):
    def test_contract_and_frozen_baseline_validate(self) -> None:
        self.assertEqual([], VALIDATOR.validate_contract())

    def test_discovery_record_cannot_import_factual_fields(self) -> None:
        record = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-example",
            "discovered_name": "Example Ventures",
            "country_hints": ["BR"],
            "discovery_reference": "private-row-1",
            "discovered_on": "2026-08-02",
            "evidence_role": "lead_only",
            "description": "A third-party description must not enter the queue contract.",
        }
        errors = list(
            Draft202012Validator(
                schema("discovery-record.schema.json"), format_checker=FormatChecker()
            ).iter_errors(record)
        )
        self.assertTrue(any("Additional properties" in error.message for error in errors))

    def test_official_evidence_and_decision_are_separate_valid_records(self) -> None:
        evidence = {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-example-identity",
            "candidate_id": "delta-fund-example",
            "official_url": "https://example.com/about",
            "source_title": "About Example Ventures",
            "accessed_on": "2026-08-02",
            "source_kind": "official_identity",
            "claims": [{"field": "identity", "value": "Example Ventures", "support": "Official about page"}],
        }
        decision = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-example",
            "decision": "eligible",
            "reason": "All eligibility gates have official evidence.",
            "evidence_ids": ["evidence-delta-example-identity"],
            "destination": "funds/brazil/example-ventures.md",
            "review": {"status": "approved", "reviewer": "reviewer-2", "reviewed_on": "2026-08-02", "independent": True},
        }
        for name, record in (
            ("official-evidence-record.schema.json", evidence),
            ("decision-record.schema.json", decision),
        ):
            Draft202012Validator(schema(name), format_checker=FormatChecker()).validate(record)

    def test_writer_paths_worktrees_and_branches_are_exclusive(self) -> None:
        topology = json.loads((HERE / "workers" / "topology.json").read_text(encoding="utf-8"))
        workers = topology["workers"]
        self.assertEqual(6, len(workers))
        for field in ("write_prefix", "worktree", "branch"):
            values = [worker[field] for worker in workers]
            self.assertEqual(len(values), len(set(values)), field)
        self.assertEqual(
            [0, 1, 2],
            sorted(worker["partition"] for worker in workers if worker["phase"] == "validation"),
        )


if __name__ == "__main__":
    unittest.main()
