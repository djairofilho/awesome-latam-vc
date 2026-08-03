#!/usr/bin/env python3
"""Adjudicate independent reviews and build the deterministic #337 freeze manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "review"
CUTOFF_DATE = "2026-08-02"
FROZEN_ON = "2026-08-02"
DEFAULT_ADJUDICATIONS = HERE / "adjudications.jsonl"
DEFAULT_MANIFEST = HERE / "freeze-manifest.json"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def dump_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def record_sha256(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(record).encode("utf-8")).hexdigest()


def records_sha256(rows: list[dict[str, Any]]) -> str:
    return hashlib.sha256(dump_jsonl(rows).encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{number}: JSONL record must be an object")
        rows.append(value)
    return rows


def schema_validator(epic: Path, name: str) -> Draft202012Validator:
    schema = load_json(epic / "schemas" / name)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_rows(
    rows: list[dict[str, Any]],
    validator: Draft202012Validator,
    path: Path,
    errors: list[str],
) -> None:
    for number, row in enumerate(rows, 1):
        for finding in validator.iter_errors(row):
            errors.append(f"{path}:{number}: {finding.message}")


def index_unique(
    rows: list[dict[str, Any]],
    key: str,
    label: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str):
            continue
        if value in index:
            errors.append(f"{label}: duplicate {key} {value}")
        else:
            index[value] = row
    return index


def evidence_index(
    epic: Path,
    validator: Draft202012Validator,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    paths = sorted(epic.glob("shards/*/*evidence*.jsonl"))
    paths += sorted((epic / "review" / "evidence").glob("*.jsonl"))
    for path in paths:
        try:
            found = load_jsonl(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        validate_rows(found, validator, path, errors)
        rows.extend(found)
    return index_unique(rows, "evidence_id", "evidence", errors)


def validate_evidence_ids(
    candidate_id: str,
    evidence_ids: Any,
    evidence: dict[str, dict[str, Any]],
    label: str,
    errors: list[str],
) -> list[str]:
    if not isinstance(evidence_ids, list):
        return []
    validated = []
    for evidence_id in evidence_ids:
        item = evidence.get(evidence_id)
        if item is None:
            errors.append(f"{candidate_id}: {label} references missing evidence {evidence_id}")
        elif item.get("candidate_id") != candidate_id:
            errors.append(f"{candidate_id}: {label} evidence belongs to another candidate")
        else:
            validated.append(evidence_id)
    return sorted(set(validated))


def read_review_inputs(
    epic: Path,
    errors: list[str],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    assignment_validator = schema_validator(epic, "review-assignment.schema.json")
    result_validator = schema_validator(epic, "review-record.schema.json")
    assignment_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    for number in range(3):
        assignment_path = epic / "review" / "assignments" / f"review-{number}.jsonl"
        result_path = epic / "review" / "results" / f"review-{number}.jsonl"
        for path, target, validator in (
            (assignment_path, assignment_rows, assignment_validator),
            (result_path, result_rows, result_validator),
        ):
            if not path.exists():
                errors.append(f"{path}: required review input is missing")
                continue
            try:
                rows = load_jsonl(path)
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
                continue
            validate_rows(rows, validator, path, errors)
            target.extend(rows)

    assignments = index_unique(assignment_rows, "candidate_id", "assignments", errors)
    results = index_unique(result_rows, "candidate_id", "results", errors)
    missing = sorted(set(assignments) - set(results))
    unexpected = sorted(set(results) - set(assignments))
    if missing:
        errors.append(f"review results missing for candidates: {missing}")
    if unexpected:
        errors.append(f"review results without assignment: {unexpected}")
    return assignment_rows, result_rows, assignments, results


def build(
    epic: Path = EPIC,
    adjudications_path: Path | None = None,
) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    adjudications_path = adjudications_path or epic / "review" / "adjudications.jsonl"
    try:
        assignment_rows, result_rows, assignments, results = read_review_inputs(epic, errors)
        adjudication_validator = schema_validator(epic, "adjudication-record.schema.json")
        evidence_validator = schema_validator(epic, "official-evidence-record.schema.json")
        manifest_validator = schema_validator(
            epic, "publication-freeze-manifest.schema.json"
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)], None

    if adjudications_path.exists():
        try:
            adjudication_rows = load_jsonl(adjudications_path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            adjudication_rows = []
    else:
        adjudication_rows = []
    validate_rows(
        adjudication_rows, adjudication_validator, adjudications_path, errors
    )
    adjudications = index_unique(
        adjudication_rows, "candidate_id", "adjudications", errors
    )
    evidence = evidence_index(epic, evidence_validator, errors)

    changes = {
        candidate_id
        for candidate_id, row in results.items()
        if row.get("review_status") == "changes_requested"
    }
    missing_adjudications = sorted(changes - set(adjudications))
    unexpected_adjudications = sorted(set(adjudications) - changes)
    if missing_adjudications:
        errors.append(
            f"changes_requested without adjudication: {missing_adjudications}"
        )
    if unexpected_adjudications:
        errors.append(
            f"adjudications without changes_requested: {unexpected_adjudications}"
        )

    final: dict[str, dict[str, Any]] = {}
    for candidate_id, result in results.items():
        assignment = assignments.get(candidate_id)
        if assignment is None:
            continue
        if result.get("assignment_sha256") != record_sha256(assignment):
            errors.append(f"{candidate_id}: assignment hash mismatch")
        if result.get("reviewer") != assignment.get("reviewer"):
            errors.append(f"{candidate_id}: reviewer does not match assignment")
        if result.get("final_decision") is None:
            errors.append(f"{candidate_id}: review has null final decision")
        result_evidence = validate_evidence_ids(
            candidate_id,
            result.get("evidence_ids"),
            evidence,
            "review",
            errors,
        )

        if result.get("review_status") == "approved":
            if result.get("final_decision") != assignment.get("source_decision"):
                errors.append(f"{candidate_id}: approved review changes source decision")
            final[candidate_id] = {
                "decision": result.get("final_decision"),
                "destination": result.get("destination"),
                "evidence_ids": result_evidence,
                "review_record_id": f"review:{result.get('reviewer')}:{candidate_id}",
            }
            continue

        if result.get("review_status") != "changes_requested":
            continue
        if result.get("blind_search_outcome") != "blocked" and not result_evidence:
            errors.append(f"{candidate_id}: changes_requested has no official evidence")
        adjudication = adjudications.get(candidate_id)
        if adjudication is None:
            continue
        if adjudication.get("review_record_sha256") != record_sha256(result):
            errors.append(f"{candidate_id}: adjudication review hash mismatch")
        if adjudication.get("final_decision") is None:
            errors.append(f"{candidate_id}: adjudication has null final decision")
        adjudication_evidence = validate_evidence_ids(
            candidate_id,
            adjudication.get("evidence_ids"),
            evidence,
            "adjudication",
            errors,
        )
        if not adjudication_evidence:
            errors.append(f"{candidate_id}: adjudication has no official evidence")
        if adjudication.get("resolution") == "accept_review_change":
            if adjudication.get("final_decision") != result.get("final_decision"):
                errors.append(f"{candidate_id}: accepted change alters review decision")
            if adjudication.get("destination") != result.get("destination"):
                errors.append(f"{candidate_id}: accepted change alters review destination")
        final[candidate_id] = {
            "decision": adjudication.get("final_decision"),
            "destination": adjudication.get("destination"),
            "evidence_ids": adjudication_evidence,
            "review_record_id": f"adjudication:{candidate_id}",
        }

    missing_final = sorted(set(assignments) - set(final))
    if missing_final:
        errors.append(f"candidates without final decision: {missing_final}")
    null_final = sorted(
        candidate_id
        for candidate_id, row in final.items()
        if row.get("decision") is None
    )
    if null_final:
        errors.append(f"null final decisions: {null_final}")

    candidates_path = epic / "consolidation" / "candidates.jsonl"
    try:
        candidate_rows = load_jsonl(candidates_path)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        candidate_rows = []
    candidates = index_unique(candidate_rows, "candidate_id", "candidates", errors)
    absent_candidates = sorted(set(assignments) - set(candidates))
    if absent_candidates:
        errors.append(f"assigned candidates absent from consolidation: {absent_candidates}")

    eligible_records = []
    for candidate_id, row in sorted(final.items()):
        if row.get("decision") != "eligible":
            continue
        candidate = candidates.get(candidate_id)
        if candidate is None:
            continue
        evidence_ids = row.get("evidence_ids", [])
        if not evidence_ids:
            errors.append(f"{candidate_id}: eligible final decision has no official evidence")
            continue
        partition = candidate.get("validation_partition")
        if not isinstance(partition, int):
            errors.append(f"{candidate_id}: eligible candidate has no validation partition")
            continue
        eligible_records.append(
            {
                "candidate_id": candidate_id,
                "canonical_name": candidate.get("name"),
                "validation_partition": partition,
                "decision": "eligible",
                "decision_evidence_ids": evidence_ids,
                "review_record_id": row["review_record_id"],
            }
        )

    assignment_hash_rows = sorted(
        assignment_rows, key=lambda row: row.get("candidate_id", "")
    )
    review_hash_rows = sorted(
        [
            {"record_kind": "review", "record": row}
            for row in result_rows
        ]
        + [
            {"record_kind": "adjudication", "record": row}
            for row in adjudication_rows
        ],
        key=lambda row: (
            row["record"].get("candidate_id", ""),
            row["record_kind"],
        ),
    )
    manifest = {
        "schema_version": "1.0",
        "status": "frozen",
        "cutoff_date": CUTOFF_DATE,
        "frozen_on": FROZEN_ON,
        "source_decisions_sha256": records_sha256(assignment_hash_rows),
        "review_records_sha256": records_sha256(review_hash_rows),
        "eligible_count": len(eligible_records),
        "eligible_records": eligible_records,
    }
    for finding in manifest_validator.iter_errors(manifest):
        errors.append(f"freeze-manifest: {finding.message}")

    if manifest["eligible_count"] != len(manifest["eligible_records"]):
        errors.append("freeze-manifest: eligible_count mismatch")
    duplicate_review_ids = [
        value
        for value, count in Counter(
            row["review_record_id"] for row in eligible_records
        ).items()
        if count > 1
    ]
    if duplicate_review_ids:
        errors.append(f"freeze-manifest: duplicate review record IDs {duplicate_review_ids}")

    if errors:
        return sorted(set(errors)), None
    return [], manifest


def render_manifest(manifest: dict[str, Any]) -> str:
    return json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudications", type=Path, default=DEFAULT_ADJUDICATIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors, manifest = build(EPIC, args.adjudications)
    if errors:
        print("Freeze construction failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert manifest is not None
    rendered = render_manifest(manifest)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"{args.output}: missing or stale", file=sys.stderr)
            return 1
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(
        f"Freeze manifest ready: {manifest['eligible_count']} eligible records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
