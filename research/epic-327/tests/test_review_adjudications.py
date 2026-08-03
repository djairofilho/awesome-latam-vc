import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location(
    "prepare_adjudications", EPIC / "review" / "prepare_adjudications.py"
)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class ReviewAdjudicationTests(unittest.TestCase):
    def schema_fixture(self, directory: str) -> Path:
        epic = Path(directory) / "research" / "epic-327"
        schema_dir = epic / "schemas"
        schema_dir.mkdir(parents=True)
        schema_dir.joinpath("adjudication-record.schema.json").write_text(
            (EPIC / "schemas" / "adjudication-record.schema.json").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        return epic

    def test_change_becomes_explicit_hash_bound_adjudication(self):
        with tempfile.TemporaryDirectory() as directory:
            epic = self.schema_fixture(directory)
            change = {
                "schema_version": "1.0",
                "candidate_id": "delta-fund-example",
                "reviewer": "review-0",
                "reviewed_on": "2026-08-02",
                "assignment_sha256": "a" * 64,
                "blind_search_outcome": "contradicted",
                "review_status": "changes_requested",
                "final_decision": "excluded",
                "destination": None,
                "evidence_ids": ["evidence-delta-example-official"],
                "error_codes": ["category_mismatch"],
            }
            changes = Path(directory) / "changes.jsonl"
            changes.write_text(json.dumps(change) + "\n", encoding="utf-8")
            errors, rendered = PREPARE.render(changes, epic)
            self.assertEqual(errors, [])
            row = json.loads(rendered)
            self.assertEqual(row["review_record_sha256"], PREPARE.record_sha256(change))
            self.assertEqual(row["resolution"], "accept_review_change")

    def test_change_without_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            epic = self.schema_fixture(directory)
            change = {
                "candidate_id": "delta-fund-example",
                "review_status": "changes_requested",
                "final_decision": "excluded",
                "destination": None,
                "evidence_ids": [],
            }
            changes = Path(directory) / "changes.jsonl"
            changes.write_text(json.dumps(change) + "\n", encoding="utf-8")
            errors, _ = PREPARE.render(changes, epic)
            self.assertTrue(any("sem evidência oficial" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
