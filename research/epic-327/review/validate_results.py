#!/usr/bin/env python3
"""Validate one independent-review result shard in isolation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
EPIC = HERE.parent
ASSIGNMENTS = HERE / "assignments" / "review-0.jsonl"
RESULTS = HERE / "results" / "review-0.jsonl"
NEW_EVIDENCE = HERE / "evidence" / "review-0.jsonl"


def load_prepare():
    spec = importlib.util.spec_from_file_location("review_prepare", HERE / "prepare.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8")
    return text, [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    prepare = load_prepare()
    assignments_text, assignments = load_jsonl(ASSIGNMENTS)
    results_text, results = load_jsonl(RESULTS)
    evidence_text, new_evidence = load_jsonl(NEW_EVIDENCE)
    del assignments_text

    review_schema = json.loads(
        (EPIC / "schemas" / "review-record.schema.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (EPIC / "schemas" / "official-evidence-record.schema.json").read_text(encoding="utf-8")
    )
    review_validator = Draft202012Validator(review_schema, format_checker=FormatChecker())
    evidence_validator = Draft202012Validator(evidence_schema, format_checker=FormatChecker())
    errors: list[str] = []

    assignments_by_id = {row["candidate_id"]: row for row in assignments}
    results_by_id = {row["candidate_id"]: row for row in results}
    if set(assignments_by_id) != set(results_by_id):
        errors.append("result candidate IDs do not exactly match review-0 assignments")

    for row in results:
        for error in review_validator.iter_errors(row):
            errors.append(f"{row['candidate_id']}: {error.message}")
        assignment = assignments_by_id.get(row["candidate_id"])
        if assignment and row["assignment_sha256"] != prepare.record_sha256(assignment):
            errors.append(f"{row['candidate_id']}: assignment_sha256 mismatch")
        if assignment and assignment["source_worker"] == "validation-0":
            errors.append(f"{row['candidate_id']}: reviewer cannot review validation-0")
        if row["review_status"] == "changes_requested" and not row["evidence_ids"]:
            errors.append(f"{row['candidate_id']}: changes_requested requires official evidence")

    for row in new_evidence:
        for error in evidence_validator.iter_errors(row):
            errors.append(f"{row['evidence_id']}: {error.message}")

    known_evidence: dict[str, str] = {}
    for path in EPIC.rglob("*.jsonl"):
        if path in {RESULTS, ASSIGNMENTS}:
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if evidence_id := record.get("evidence_id"):
                known_evidence[evidence_id] = record.get("candidate_id")
    for row in results:
        missing = sorted(set(row["evidence_ids"]) - set(known_evidence))
        if missing:
            errors.append(f"{row['candidate_id']}: unknown evidence IDs: {missing}")
        foreign = sorted(
            evidence_id
            for evidence_id in row["evidence_ids"]
            if known_evidence.get(evidence_id) != row["candidate_id"]
        )
        if foreign:
            errors.append(f"{row['candidate_id']}: evidence belongs to another candidate: {foreign}")

    if results_text != prepare.dump_jsonl(sorted(results, key=lambda row: row["candidate_id"])):
        errors.append("review-0 results are not canonical and sorted")
    if evidence_text != prepare.dump_jsonl(sorted(new_evidence, key=lambda row: row["evidence_id"])):
        errors.append("review-0 evidence is not canonical and sorted")

    for candidate_id in ("delta-fund-balderton-capital", "delta-fund-elemental-impact"):
        row = results_by_id.get(candidate_id)
        if not row or row["review_status"] != "changes_requested" or not row["evidence_ids"]:
            errors.append(f"{candidate_id}: required identity correction was not materialized")

    forbidden = "open" + "vc"
    for path in (RESULTS, NEW_EVIDENCE):
        if forbidden in path.read_text(encoding="utf-8").lower():
            errors.append(f"{path.name}: forbidden discovery-provider term found")

    if errors:
        print("\n".join(errors))
        return 1
    print(
        f"review-0 OK: {len(results)} results, {len(new_evidence)} new evidence records, "
        f"{sum(row['review_status'] == 'changes_requested' for row in results)} changes requested"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
