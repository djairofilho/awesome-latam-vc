import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location("review_prepare", EPIC / "review" / "prepare.py")
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


def write_jsonl(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PREPARE.dump_jsonl(rows), encoding="utf-8", newline="\n")


class ReviewContractTests(unittest.TestCase):
    def test_sample_is_deterministic_and_at_least_twenty_percent(self):
        rows = [{"candidate_id": f"delta-fund-sample-{number}"} for number in range(13)]
        first = PREPARE.deterministic_sample(rows)
        second = PREPARE.deterministic_sample(list(reversed(rows)))
        self.assertEqual(first, second)
        self.assertEqual(len(first), math.ceil(len(rows) * 0.2))

    def test_validation_author_never_reviews_own_record(self):
        for number in range(3):
            reviewer = PREPARE.reviewer_for(
                f"validation-{number}", f"delta-fund-review-{number}"
            )
            self.assertNotEqual(reviewer, f"review-{number}")

    def test_review_schema_requires_errors_for_changes(self):
        schema = json.loads(
            (EPIC / "schemas" / "review-record.schema.json").read_text(encoding="utf-8")
        )
        validator = Draft202012Validator(schema)
        record = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-example",
            "reviewer": "review-0",
            "reviewed_on": "2026-08-02",
            "assignment_sha256": "a" * 64,
            "blind_search_outcome": "contradicted",
            "review_status": "changes_requested",
            "final_decision": "excluded",
            "destination": None,
            "evidence_ids": [],
            "error_codes": [],
        }
        self.assertTrue(list(validator.iter_errors(record)))

    def test_build_has_mandatory_reviews_and_sampled_strata(self):
        with tempfile.TemporaryDirectory() as directory:
            epic = Path(directory) / "research" / "epic-327"
            schema_dir = epic / "schemas"
            schema_dir.mkdir(parents=True)
            schema_dir.joinpath("review-assignment.schema.json").write_text(
                (EPIC / "schemas" / "review-assignment.schema.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            candidates = []
            decisions = {0: [], 1: [], 2: []}
            for number in range(10):
                candidate_id = f"delta-fund-excluded-{number}"
                candidates.append({"candidate_id": candidate_id, "name": f"Excluded {number}"})
                decisions[2].append({"candidate_id": candidate_id, "decision": "excluded"})
            candidates.extend(
                [
                    {"candidate_id": "delta-fund-eligible", "name": "Eligible"},
                    {
                        "candidate_id": "delta-fund-routed-consolidation",
                        "name": "Routed Consolidation",
                        "status": "routed",
                        "category": "angel_network",
                    },
                    {
                        "candidate_id": "delta-fund-routed-validation",
                        "name": "Routed Validation",
                    },
                    {"candidate_id": "delta-fund-conflict", "name": "Conflict"},
                    {"candidate_id": "delta-fund-unresolved", "name": "Unresolved"},
                ]
            )
            decisions[0].append(
                {"candidate_id": "delta-fund-eligible", "decision": "eligible"}
            )
            decisions[1].append(
                {
                    "candidate_id": "delta-fund-routed-validation",
                    "decision": "routed_accelerators",
                }
            )
            write_jsonl(epic / "consolidation" / "candidates.jsonl", candidates)
            write_jsonl(
                epic / "consolidation" / "exceptions.jsonl",
                [
                    {"candidate_id": "delta-fund-conflict", "status": "identity_conflict"},
                    {"candidate_id": "delta-fund-unresolved", "status": "unresolved"},
                ],
            )
            for number in range(3):
                write_jsonl(
                    epic / "shards" / f"validation-{number}" / "decisions.jsonl",
                    decisions[number],
                )

            errors, outputs = PREPARE.build(epic)
            self.assertEqual(errors, [])
            summary = json.loads(outputs["assignment-summary.json"])
            self.assertEqual(summary["reason_counts"]["all_eligible"], 1)
            self.assertEqual(summary["reason_counts"]["all_routed"], 2)
            assignments = []
            for number in range(3):
                assignments.extend(
                    json.loads(line)
                    for line in outputs[
                        f"assignments/review-{number}.jsonl"
                    ].splitlines()
                )
            consolidation_route = next(
                row
                for row in assignments
                if row["candidate_id"] == "delta-fund-routed-consolidation"
            )
            self.assertEqual(consolidation_route["source_kind"], "consolidation_route")
            self.assertEqual(
                consolidation_route["source_decision"], "routed_angel_networks"
            )
            self.assertEqual(summary["reason_counts"]["all_identity_conflicts"], 1)
            self.assertEqual(
                summary["sample_strata"]["decision:excluded"]["selected"], 2
            )
            self.assertEqual(
                summary["sample_strata"]["exception:unresolved"]["selected"], 1
            )

    def test_error_expands_entire_stratum(self):
        with tempfile.TemporaryDirectory() as directory:
            epic = Path(directory) / "research" / "epic-327"
            schema_dir = epic / "schemas"
            schema_dir.mkdir(parents=True)
            schema_dir.joinpath("review-assignment.schema.json").write_text(
                (EPIC / "schemas" / "review-assignment.schema.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            unresolved = [
                {"candidate_id": f"delta-fund-unresolved-{number}", "status": "unresolved"}
                for number in range(9)
            ]
            write_jsonl(
                epic / "consolidation" / "candidates.jsonl",
                [
                    {"candidate_id": row["candidate_id"], "name": f"Unresolved {number}"}
                    for number, row in enumerate(unresolved)
                ],
            )
            write_jsonl(epic / "consolidation" / "exceptions.jsonl", unresolved)
            for number in range(3):
                write_jsonl(
                    epic / "shards" / f"validation-{number}" / "decisions.jsonl", []
                )
            review_dir = epic / "review"
            review_dir.mkdir(parents=True)
            review_dir.joinpath("sample-expansions.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "expanded_strata": {
                            "exception:unresolved": {
                                "trigger_candidates": ["delta-fund-unresolved-0"]
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            errors, outputs = PREPARE.build(epic)
            self.assertEqual(errors, [])
            summary = json.loads(outputs["assignment-summary.json"])
            stratum = summary["sample_strata"]["exception:unresolved"]
            self.assertEqual(stratum["selected"], 9)
            self.assertTrue(stratum["expanded_to_full_review"])


if __name__ == "__main__":
    unittest.main()
