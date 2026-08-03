import importlib.util
import json
import unittest
from pathlib import Path


EPIC = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_review_2", EPIC / "review" / "validate_review_2.py"
)
REVIEW = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(REVIEW)


class Review2Tests(unittest.TestCase):
    def test_committed_artifacts_validate(self):
        self.assertEqual(REVIEW.validate(), [])

    def test_assignments_are_complete_and_unique(self):
        assignments = REVIEW.load_jsonl(REVIEW.ASSIGNMENTS)
        results = REVIEW.load_jsonl(REVIEW.RESULTS)
        self.assertEqual(len(assignments), 377)
        self.assertEqual(len(results), 377)
        self.assertEqual(
            {record["candidate_id"] for record in assignments},
            {record["candidate_id"] for record in results},
        )

    def test_only_two_source_decisions_change(self):
        assignments = {
            row["candidate_id"]: row for row in REVIEW.load_jsonl(REVIEW.ASSIGNMENTS)
        }
        results = REVIEW.load_jsonl(REVIEW.RESULTS)
        changed = {
            row["candidate_id"]
            for row in results
            if row["final_decision"] != assignments[row["candidate_id"]]["source_decision"]
        }
        self.assertEqual(
            changed,
            {"delta-fund-dao-capital", "delta-fund-magic-fund"},
        )

    def test_summary_hashes_cover_committed_files(self):
        summary = json.loads(REVIEW.SUMMARY.read_text(encoding="utf-8"))
        self.assertTrue(summary["complete"])
        self.assertEqual(
            summary["results_file_sha256"],
            REVIEW.content_sha256(REVIEW.RESULTS.read_text(encoding="utf-8")),
        )
        self.assertEqual(
            summary["evidence_file_sha256"],
            REVIEW.content_sha256(REVIEW.EVIDENCE.read_text(encoding="utf-8")),
        )


if __name__ == "__main__":
    unittest.main()
