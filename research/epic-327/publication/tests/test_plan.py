from __future__ import annotations

import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("publication_planner", HERE / "plan.py")
assert SPEC and SPEC.loader
PLANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLANNER)


def record(number: int) -> dict:
    suffix = f"candidate-{number:03d}"
    return {
        "candidate_id": f"delta-fund-{suffix}",
        "canonical_name": f"Candidate {number:03d}",
        "validation_partition": number % 3,
        "decision": "eligible",
        "decision_evidence_ids": [f"evidence-delta-{suffix}-official"],
        "review_record_id": f"review-{suffix}",
    }


def manifest(count: int) -> dict:
    return {
        "schema_version": "1.0",
        "status": "frozen",
        "cutoff_date": "2026-08-02",
        "frozen_on": "2026-08-03",
        "source_decisions_sha256": "a" * 64,
        "review_records_sha256": "b" * 64,
        "eligible_count": count,
        "eligible_records": [record(number) for number in range(count, 0, -1)],
    }


def encoded(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class PublicationPlannerTests(unittest.TestCase):
    def test_builds_exact_ceil_batches_with_at_most_ten_members(self) -> None:
        frozen = manifest(21)
        plan = PLANNER.build_plan(frozen, encoded(frozen), "synthetic-freeze.json")

        self.assertEqual(21, plan["eligible_count"])
        self.assertEqual(math.ceil(21 / 10), plan["batch_count"])
        self.assertEqual([10, 10, 1], [batch["candidate_count"] for batch in plan["batches"]])
        self.assertEqual([], PLANNER.validate_plan(frozen, encoded(frozen), plan))

    def test_zero_eligible_records_produces_zero_batches(self) -> None:
        frozen = manifest(0)
        plan = PLANNER.build_plan(frozen, encoded(frozen), "empty-freeze.json")

        self.assertEqual(0, plan["batch_count"])
        self.assertEqual([], plan["batches"])
        self.assertEqual([], PLANNER.validate_plan(frozen, encoded(frozen), plan))

    def test_rejects_non_frozen_count_mismatch_duplicates_and_ineligible(self) -> None:
        frozen = manifest(2)
        frozen["status"] = "draft"
        frozen["eligible_count"] = 3
        frozen["eligible_records"][1]["candidate_id"] = frozen["eligible_records"][0]["candidate_id"]
        frozen["eligible_records"][1]["decision"] = "excluded"

        errors = PLANNER.validate_manifest(frozen)

        self.assertTrue(any("frozen" in error for error in errors))
        self.assertTrue(any("eligible_count" in error for error in errors))
        self.assertTrue(any("candidate_id duplicado" in error for error in errors))
        self.assertTrue(any("inelegíveis" in error for error in errors))

    def test_detects_duplicate_ineligible_and_unplanned_batch_members(self) -> None:
        frozen = manifest(11)
        raw = encoded(frozen)
        plan = PLANNER.build_plan(frozen, raw, "synthetic-freeze.json")
        corrupted = copy.deepcopy(plan)
        duplicate = copy.deepcopy(corrupted["batches"][0]["candidates"][0])
        duplicate["decision"] = "excluded"
        corrupted["batches"][1]["candidates"] = [duplicate]
        corrupted["batches"][1]["candidate_count"] = 1

        errors = PLANNER.validate_plan(frozen, raw, corrupted)

        self.assertTrue(any("duplicados" in error for error in errors))
        self.assertTrue(any("inelegíveis" in error for error in errors))
        self.assertTrue(any("cobertura inexata" in error for error in errors))

    def test_manifest_bytes_and_record_content_are_hashed(self) -> None:
        frozen = manifest(1)
        raw = encoded(frozen)
        plan = PLANNER.build_plan(frozen, raw, "synthetic-freeze.json")
        altered_raw = raw + b"\n"

        self.assertNotEqual(
            plan["source_manifest_sha256"],
            PLANNER.build_plan(frozen, altered_raw, "synthetic-freeze.json")["source_manifest_sha256"],
        )
        altered = copy.deepcopy(plan)
        altered["batches"][0]["candidates"][0]["canonical_name"] = "Altered"
        self.assertTrue(PLANNER.validate_plan(frozen, raw, altered))


if __name__ == "__main__":
    unittest.main()
