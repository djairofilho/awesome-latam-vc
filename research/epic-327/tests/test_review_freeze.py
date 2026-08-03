import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location("review_freeze", EPIC / "review" / "freeze.py")
FREEZE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FREEZE)


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(FREEZE.dump_jsonl(rows), encoding="utf-8", newline="\n")


class FreezeContractTests(unittest.TestCase):
    def fixture(self, directory: str, source_decision: str = "eligible"):
        epic = Path(directory) / "research" / "epic-327"
        schemas = epic / "schemas"
        schemas.mkdir(parents=True)
        for name in (
            "adjudication-record.schema.json",
            "official-evidence-record.schema.json",
            "publication-freeze-manifest.schema.json",
            "review-assignment.schema.json",
            "review-record.schema.json",
        ):
            schemas.joinpath(name).write_text(
                (EPIC / "schemas" / name).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

        candidate_id = "delta-fund-example"
        assignment = {
            "schema_version": "1.0",
            "candidate_id": candidate_id,
            "source_kind": "validation_decision",
            "source_worker": "validation-2",
            "source_decision": source_decision,
            "review_reason": (
                "all_eligible"
                if source_decision == "eligible"
                else "deterministic_exclusion_sample"
            ),
            "reviewer": "review-0",
            "input_sha256": "a" * 64,
            "blind_queries": ["query one", "query two"],
        }
        evidence = {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-example-official",
            "candidate_id": candidate_id,
            "official_url": "https://example.com/",
            "source_title": "Example official site",
            "accessed_on": "2026-08-02",
            "source_kind": "official_identity",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "Example"},
                    "support": "The official site identifies Example.",
                }
            ],
        }
        candidate = {
            "schema_version": "1.0",
            "candidate_id": candidate_id,
            "name": "Example",
            "validation_partition": 2,
        }
        write_jsonl(epic / "consolidation" / "candidates.jsonl", [candidate])
        write_jsonl(epic / "review" / "evidence" / "fixture.jsonl", [evidence])
        write_jsonl(epic / "review" / "assignments" / "review-0.jsonl", [assignment])
        for number in (1, 2):
            write_jsonl(epic / "review" / "assignments" / f"review-{number}.jsonl", [])
            write_jsonl(epic / "review" / "results" / f"review-{number}.jsonl", [])
        return epic, assignment, evidence

    def approved_result(self, assignment: dict) -> dict:
        return {
            "schema_version": "1.0",
            "candidate_id": assignment["candidate_id"],
            "reviewer": "review-0",
            "reviewed_on": "2026-08-02",
            "assignment_sha256": FREEZE.record_sha256(assignment),
            "blind_search_outcome": "confirmed",
            "review_status": "approved",
            "final_decision": assignment["source_decision"],
            "destination": "funds/" if assignment["source_decision"] == "eligible" else None,
            "evidence_ids": ["evidence-delta-example-official"],
            "error_codes": [],
        }

    def changed_result(self, assignment: dict, evidence: bool = True) -> dict:
        return {
            "schema_version": "1.0",
            "candidate_id": assignment["candidate_id"],
            "reviewer": "review-0",
            "reviewed_on": "2026-08-02",
            "assignment_sha256": FREEZE.record_sha256(assignment),
            "blind_search_outcome": "contradicted",
            "review_status": "changes_requested",
            "final_decision": "insufficient_evidence",
            "destination": None,
            "evidence_ids": ["evidence-delta-example-official"] if evidence else [],
            "error_codes": ["unsupported_claim"],
        }

    def adjudication(self, result: dict, decision: str = "insufficient_evidence") -> dict:
        return {
            "schema_version": "1.0",
            "candidate_id": result["candidate_id"],
            "adjudicator": "maintainer",
            "adjudicated_on": "2026-08-02",
            "review_record_sha256": FREEZE.record_sha256(result),
            "resolution": (
                "accept_review_change"
                if decision == result["final_decision"]
                else "override_review_change"
            ),
            "final_decision": decision,
            "destination": "funds/" if decision == "eligible" else None,
            "evidence_ids": ["evidence-delta-example-official"],
            "reason": "Official evidence supports the final adjudicated decision.",
        }

    def test_approved_eligible_builds_planner_compatible_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory)
            result = self.approved_result(assignment)
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])

            errors, manifest = FREEZE.build(epic)
            self.assertEqual(errors, [])
            self.assertIsNotNone(manifest)
            self.assertEqual(manifest["status"], "frozen")
            self.assertEqual(manifest["cutoff_date"], "2026-08-02")
            self.assertEqual(manifest["eligible_count"], 1)
            self.assertEqual(math.ceil(manifest["eligible_count"] / 10), 1)
            self.assertNotIn("batch_count", manifest)
            self.assertEqual(
                manifest["source_decisions_sha256"],
                FREEZE.records_sha256([assignment]),
            )
            schema = json.loads(
                (epic / "schemas" / "publication-freeze-manifest.schema.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                list(
                    Draft202012Validator(
                        schema, format_checker=FormatChecker()
                    ).iter_errors(manifest)
                ),
                [],
            )

    def test_changes_requested_requires_adjudication(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory, "identity_conflict")
            result = self.changed_result(assignment)
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])

            errors, manifest = FREEZE.build(epic)
            self.assertIsNone(manifest)
            self.assertTrue(
                any("changes_requested without adjudication" in error for error in errors)
            )

    def test_valid_adjudication_resolves_change(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory, "identity_conflict")
            result = self.changed_result(assignment)
            adjudication = self.adjudication(result, "eligible")
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            write_jsonl(epic / "review" / "adjudications.jsonl", [adjudication])

            errors, manifest = FREEZE.build(epic)
            self.assertEqual(errors, [])
            self.assertEqual(manifest["eligible_count"], 1)
            self.assertEqual(
                manifest["eligible_records"][0]["review_record_id"],
                "adjudication:delta-fund-example",
            )

    def test_adjudication_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory, "identity_conflict")
            result = self.changed_result(assignment)
            adjudication = self.adjudication(result)
            adjudication["review_record_sha256"] = "b" * 64
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            write_jsonl(epic / "review" / "adjudications.jsonl", [adjudication])

            errors, _ = FREEZE.build(epic)
            self.assertTrue(
                any("adjudication review hash mismatch" in error for error in errors)
            )

    def test_missing_and_duplicate_candidates_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory)
            result = self.approved_result(assignment)
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            write_jsonl(epic / "review" / "assignments" / "review-0.jsonl", [assignment, assignment])
            write_jsonl(epic / "consolidation" / "candidates.jsonl", [])

            errors, _ = FREEZE.build(epic)
            self.assertTrue(any("duplicate candidate_id" in error for error in errors))
            self.assertTrue(any("absent from consolidation" in error for error in errors))

    def test_change_without_official_evidence_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory, "identity_conflict")
            result = self.changed_result(assignment, evidence=False)
            adjudication = self.adjudication(result)
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            write_jsonl(epic / "review" / "adjudications.jsonl", [adjudication])

            errors, _ = FREEZE.build(epic)
            self.assertTrue(
                any("changes_requested has no official evidence" in error for error in errors)
            )

    def test_null_review_decision_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment, _ = self.fixture(directory)
            result = self.approved_result(assignment)
            result["final_decision"] = None
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])

            errors, _ = FREEZE.build(epic)
            self.assertTrue(any("null final decision" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
