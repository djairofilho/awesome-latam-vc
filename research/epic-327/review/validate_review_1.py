#!/usr/bin/env python3
"""Validate the complete review-1 result without modifying repository files."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


EPIC = Path(__file__).resolve().parents[1]
REVIEW = EPIC / "review"
ASSIGNMENTS = REVIEW / "assignments" / "review-1.jsonl"
RESULTS = REVIEW / "results" / "review-1.jsonl"
EVIDENCE = REVIEW / "evidence" / "review-1.jsonl"
PREPARE_SPEC = importlib.util.spec_from_file_location(
    "review_prepare", REVIEW / "prepare.py"
)
PREPARE = importlib.util.module_from_spec(PREPARE_SPEC)
PREPARE_SPEC.loader.exec_module(PREPARE)


def canonical_line(record: dict) -> str:
    return PREPARE.canonical_line(record) + "\n"


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate() -> list[str]:
    errors: list[str] = []
    assignments = load_jsonl(ASSIGNMENTS)
    results = load_jsonl(RESULTS)
    evidence = load_jsonl(EVIDENCE)

    review_schema = json.loads(
        (EPIC / "schemas" / "review-record.schema.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (EPIC / "schemas" / "official-evidence-record.schema.json").read_text(
            encoding="utf-8"
        )
    )
    checker = FormatChecker()
    for label, rows, schema in (
        ("result", results, review_schema),
        ("evidence", evidence, evidence_schema),
    ):
        validator = Draft202012Validator(schema, format_checker=checker)
        for row in rows:
            for issue in validator.iter_errors(row):
                errors.append(
                    f"{label}:{row.get('candidate_id', '<unknown>')}: {issue.message}"
                )

    assignment_by_id = {row["candidate_id"]: row for row in assignments}
    result_by_id = {row["candidate_id"]: row for row in results}
    if len(assignment_by_id) != len(assignments):
        errors.append("assignments contain duplicate candidate IDs")
    if len(result_by_id) != len(results):
        errors.append("results contain duplicate candidate IDs")
    if set(result_by_id) != set(assignment_by_id):
        errors.append("result candidate IDs do not exactly cover assignments")

    for candidate_id, result in result_by_id.items():
        assignment = assignment_by_id.get(candidate_id)
        if assignment is None:
            continue
        expected_hash = PREPARE.record_sha256(assignment)
        if result["assignment_sha256"] != expected_hash:
            errors.append(f"{candidate_id}: assignment hash mismatch")
        if result["reviewer"] != assignment["reviewer"]:
            errors.append(f"{candidate_id}: reviewer mismatch")
        if (
            result["review_status"] == "changes_requested"
            and result["blind_search_outcome"] != "contradicted"
        ):
            errors.append(f"{candidate_id}: requested changes without contradiction")
        if (
            result["review_status"] == "changes_requested"
            and result["blind_search_outcome"] != "blocked"
            and not result["evidence_ids"]
        ):
            errors.append(f"{candidate_id}: requested changes without evidence")

    evidence_by_id: dict[str, dict] = {}
    for path in EPIC.rglob("official-evidence.jsonl"):
        for row in load_jsonl(path):
            evidence_by_id.setdefault(row["evidence_id"], row)
    for row in evidence:
        if row["evidence_id"] in evidence_by_id:
            errors.append(f"{row['evidence_id']}: duplicate evidence ID")
        evidence_by_id[row["evidence_id"]] = row
    for result in results:
        for evidence_id in result["evidence_ids"]:
            item = evidence_by_id.get(evidence_id)
            if item is None:
                errors.append(
                    f"{result['candidate_id']}: missing evidence {evidence_id}"
                )
            elif item["candidate_id"] != result["candidate_id"]:
                errors.append(
                    f"{result['candidate_id']}: foreign evidence {evidence_id}"
                )

    expected_results = "".join(
        canonical_line(row) for row in sorted(results, key=lambda row: row["candidate_id"])
    )
    expected_evidence = "".join(
        canonical_line(row) for row in sorted(evidence, key=lambda row: row["evidence_id"])
    )
    if RESULTS.read_text(encoding="utf-8") != expected_results:
        errors.append("results are not canonical or sorted")
    if EVIDENCE.read_text(encoding="utf-8") != expected_evidence:
        errors.append("evidence is not canonical or sorted")
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        raise SystemExit("\n".join(failures))
    print("review-1 validation passed")
