#!/usr/bin/env python3
"""Validate validation-0 in isolation while the other epic shards are unfinished."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SHARD = Path(__file__).resolve().parent
EPIC = SHARD.parents[1]


def load_module():
    path = EPIC / "validation" / "reconcile.py"
    spec = importlib.util.spec_from_file_location("epic327_reconcile", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8")
    return text, [json.loads(line) for line in text.splitlines() if line.strip()]


def main() -> int:
    reconcile = load_module()
    candidates_text, candidates = load_jsonl(SHARD / "candidates.jsonl")
    decisions_text, decisions = load_jsonl(SHARD / "decisions.jsonl")
    evidence_text, evidence = load_jsonl(SHARD / "official-evidence.jsonl")
    summary = json.loads((SHARD / "summary.json").read_text(encoding="utf-8"))

    validation_schema = json.loads((EPIC / "schemas" / "validation-record.schema.json").read_text(encoding="utf-8"))
    evidence_schema = json.loads((EPIC / "schemas" / "official-evidence-record.schema.json").read_text(encoding="utf-8"))
    v_validator = Draft202012Validator(validation_schema, format_checker=FormatChecker())
    e_validator = Draft202012Validator(evidence_schema, format_checker=FormatChecker())

    errors: list[str] = []
    for record in decisions:
        errors.extend(f"{record['candidate_id']}: {error.message}" for error in v_validator.iter_errors(record))
    for record in evidence:
        errors.extend(f"{record['evidence_id']}: {error.message}" for error in e_validator.iter_errors(record))

    candidate_by_id = {record["candidate_id"]: record for record in candidates}
    evidence_by_id = {record["evidence_id"]: record for record in evidence}
    if set(candidate_by_id) != {record["candidate_id"] for record in decisions}:
        errors.append("decision candidate IDs do not exactly match the frozen candidate shard")
    for record in decisions:
        candidate = candidate_by_id[record["candidate_id"]]
        if record["input_sha256"] != reconcile.record_sha256(candidate):
            errors.append(f"{record['candidate_id']}: input_sha256 mismatch")
        reconcile.validate_gate_evidence(record, evidence_by_id, errors)
        reconcile.validate_activity(record, evidence_by_id, errors)
        reconcile.validate_decision(record, errors)

    if decisions_text != reconcile.canonical_jsonl(decisions, "candidate_id"):
        errors.append("decisions.jsonl is not canonical or sorted")
    if evidence_text != reconcile.canonical_jsonl(evidence, "evidence_id"):
        errors.append("official-evidence.jsonl is not canonical or sorted")

    expected = reconcile.expected_summary(
        0, candidates_text, decisions_text, evidence_text, decisions, evidence
    )
    if summary != expected:
        errors.append("summary.json does not equal expected_summary")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"validation-0 OK: {len(decisions)} decisions, {len(evidence)} evidence records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
