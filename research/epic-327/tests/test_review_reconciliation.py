import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location(
    "review_reconcile", EPIC / "review" / "reconcile.py"
)
RECONCILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECONCILE)


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RECONCILE.dump_jsonl(rows), encoding="utf-8", newline="\n")


class ReviewReconciliationTests(unittest.TestCase):
    def fixture(self, directory: str) -> tuple[Path, dict]:
        epic = Path(directory) / "research" / "epic-327"
        schema_dir = epic / "schemas"
        schema_dir.mkdir(parents=True)
        for name in ["review-assignment.schema.json", "review-record.schema.json"]:
            schema_dir.joinpath(name).write_text(
                (EPIC / "schemas" / name).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        assignment = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-example",
            "source_kind": "identity_exception",
            "source_worker": "reducer",
            "source_decision": "identity_conflict",
            "review_reason": "all_identity_conflicts",
            "reviewer": "review-0",
            "input_sha256": "a" * 64,
            "blind_queries": ["query one", "query two"],
        }
        write_jsonl(epic / "review" / "assignments" / "review-0.jsonl", [assignment])
        for number in [1, 2]:
            write_jsonl(epic / "review" / "assignments" / f"review-{number}.jsonl", [])
            write_jsonl(epic / "review" / "results" / f"review-{number}.jsonl", [])
        return epic, assignment

    def test_exact_approved_result_reconciles(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, assignment = self.fixture(directory)
            result = {
                "schema_version": "1.0",
                "candidate_id": "delta-fund-example",
                "reviewer": "review-0",
                "reviewed_on": "2026-08-02",
                "assignment_sha256": RECONCILE.record_sha256(assignment),
                "blind_search_outcome": "no_additional_evidence",
                "review_status": "approved",
                "final_decision": "identity_conflict",
                "destination": "manual_identity_review",
                "evidence_ids": [],
                "error_codes": [],
            }
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            errors, outputs = RECONCILE.build(epic)
            self.assertEqual(errors, [])
            self.assertEqual(json.loads(outputs["review-summary.json"])["result_records"], 1)

    def test_assignment_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, _ = self.fixture(directory)
            result = {
                "schema_version": "1.0",
                "candidate_id": "delta-fund-example",
                "reviewer": "review-0",
                "reviewed_on": "2026-08-02",
                "assignment_sha256": "b" * 64,
                "blind_search_outcome": "no_additional_evidence",
                "review_status": "approved",
                "final_decision": "identity_conflict",
                "destination": "manual_identity_review",
                "evidence_ids": [],
                "error_codes": [],
            }
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [result])
            errors, _ = RECONCILE.build(epic)
            self.assertTrue(any("hash da atribuição diverge" in error for error in errors))

    def test_missing_result_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            epic, _ = self.fixture(directory)
            write_jsonl(epic / "review" / "results" / "review-0.jsonl", [])
            errors, _ = RECONCILE.build(epic)
            self.assertTrue(any("resultados ausentes" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
