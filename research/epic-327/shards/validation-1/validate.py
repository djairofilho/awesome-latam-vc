#!/usr/bin/env python3
"""Valida o shard validation-1 sem depender dos outros dois shards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parent
EPIC = HERE.parents[1]
sys.path.insert(0, str(EPIC / "validation"))

from reconcile import (  # noqa: E402
    CUTOFF_DATE,
    canonical_jsonl,
    expected_summary,
    load_json,
    load_jsonl,
    partition,
    record_sha256,
    unique_index,
    validate_activity,
    validate_decision,
    validate_gate_evidence,
)


def validate() -> list[str]:
    errors: list[str] = []
    candidates_path = HERE / "candidates.jsonl"
    decisions_path = HERE / "decisions.jsonl"
    evidence_path = HERE / "official-evidence.jsonl"
    candidates_text = candidates_path.read_text(encoding="utf-8")
    decisions_text = decisions_path.read_text(encoding="utf-8")
    evidence_text = evidence_path.read_text(encoding="utf-8")
    candidates = load_jsonl(candidates_path)
    decisions = load_jsonl(decisions_path)
    evidence = load_jsonl(evidence_path)
    summary = load_json(HERE / "summary.json")

    if decisions_text != canonical_jsonl(decisions, "candidate_id"):
        errors.append("decisions.jsonl não é canônico")
    if evidence_text != canonical_jsonl(evidence, "evidence_id"):
        errors.append("official-evidence.jsonl não é canônico")

    candidate_index = unique_index(candidates, "candidate_id", "candidates", errors)
    decision_index = unique_index(decisions, "candidate_id", "decisions", errors)
    evidence_index = unique_index(evidence, "evidence_id", "evidence", errors)
    if set(candidate_index) != set(decision_index):
        errors.append("decisões não reconciliam exatamente com a entrada")

    decision_schema = json.loads(
        (EPIC / "schemas" / "validation-record.schema.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (EPIC / "schemas" / "official-evidence-record.schema.json").read_text(encoding="utf-8")
    )
    decision_validator = Draft202012Validator(decision_schema, format_checker=FormatChecker())
    evidence_validator = Draft202012Validator(evidence_schema, format_checker=FormatChecker())

    for item in evidence:
        for finding in evidence_validator.iter_errors(item):
            errors.append(f"{item.get('evidence_id')}: {finding.message}")

    referenced: set[str] = set()
    for candidate_id, record in decision_index.items():
        for finding in decision_validator.iter_errors(record):
            errors.append(f"{candidate_id}: {finding.message}")
        candidate = candidate_index.get(candidate_id)
        if candidate and record.get("input_sha256") != record_sha256(candidate):
            errors.append(f"{candidate_id}: input_sha256 divergente")
        if record.get("validation_partition") != 1 or partition(candidate_id) != 1:
            errors.append(f"{candidate_id}: partição divergente")
        if record.get("validator") != "validation-1" or record.get("cutoff_date") != CUTOFF_DATE:
            errors.append(f"{candidate_id}: ownership ou corte divergente")
        validate_gate_evidence(record, evidence_index, errors)
        validate_activity(record, evidence_index, errors)
        validate_decision(record, errors)
        for gate in record.get("gates", {}).values():
            referenced.update(gate.get("evidence_ids", []))

    orphaned = set(evidence_index) - referenced
    if orphaned:
        errors.append(f"evidências órfãs: {sorted(orphaned)}")
    expected = expected_summary(
        1, candidates_text, decisions_text, evidence_text, decisions, evidence
    )
    if summary != expected:
        errors.append("summary.json divergente")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação local do shard 1 falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Shard validation-1 validado com 43 decisões oficiais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
