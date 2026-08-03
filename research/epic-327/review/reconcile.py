#!/usr/bin/env python3
"""Validate and reconcile independent-review results for epic #327."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "review"


def canonical_line(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha256(record: dict) -> str:
    return hashlib.sha256(canonical_line(record).encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: JSON inválido: {exc}") from exc
    return rows


def dump_jsonl(rows: list[dict]) -> str:
    return "".join(canonical_line(row) + "\n" for row in rows)


def evidence_index(
    epic: Path, validator: Draft202012Validator
) -> tuple[dict[str, dict], list[str]]:
    index: dict[str, dict] = {}
    errors = []
    paths = sorted(epic.glob("shards/*/*evidence*.jsonl"))
    paths += sorted((epic / "review" / "evidence").glob("*.jsonl"))
    for path in paths:
        try:
            rows = load_jsonl(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        for number, row in enumerate(rows, 1):
            for error in validator.iter_errors(row):
                errors.append(f"{path}:{number}: {error.message}")
            evidence_id = row.get("evidence_id")
            if not evidence_id:
                errors.append(f"{path}: evidência sem evidence_id")
            elif evidence_id in index and index[evidence_id] != row:
                errors.append(f"{evidence_id}: conteúdo de evidência conflitante")
            else:
                index[evidence_id] = row
    return index, errors


def build(epic: Path = EPIC) -> tuple[list[str], dict[str, str]]:
    errors = []
    assignment_schema_path = epic / "schemas" / "review-assignment.schema.json"
    result_schema_path = epic / "schemas" / "review-record.schema.json"
    evidence_schema_path = epic / "schemas" / "official-evidence-record.schema.json"
    try:
        assignment_schema = json.loads(assignment_schema_path.read_text(encoding="utf-8"))
        result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))
        evidence_schema = json.loads(evidence_schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)], {}
    assignment_validator = Draft202012Validator(
        assignment_schema, format_checker=FormatChecker()
    )
    result_validator = Draft202012Validator(result_schema, format_checker=FormatChecker())
    evidence_validator = Draft202012Validator(
        evidence_schema, format_checker=FormatChecker()
    )
    evidence, evidence_errors = evidence_index(epic, evidence_validator)
    errors.extend(evidence_errors)

    assignments = {}
    results = {}
    for number in range(3):
        reviewer = f"review-{number}"
        assignment_path = epic / "review" / "assignments" / f"{reviewer}.jsonl"
        result_path = epic / "review" / "results" / f"{reviewer}.jsonl"
        if not assignment_path.exists():
            errors.append(f"{assignment_path}: atribuições ausentes")
            continue
        if not result_path.exists():
            errors.append(f"{result_path}: resultados ausentes")
            continue
        try:
            assignment_rows = load_jsonl(assignment_path)
            result_rows = load_jsonl(result_path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        for index, row in enumerate(assignment_rows, 1):
            for error in assignment_validator.iter_errors(row):
                errors.append(f"{assignment_path}:{index}: {error.message}")
            candidate_id = row.get("candidate_id")
            if candidate_id in assignments:
                errors.append(f"{candidate_id}: atribuição duplicada")
            assignments[candidate_id] = row
        for index, row in enumerate(result_rows, 1):
            for error in result_validator.iter_errors(row):
                errors.append(f"{result_path}:{index}: {error.message}")
            candidate_id = row.get("candidate_id")
            if candidate_id in results:
                errors.append(f"{candidate_id}: resultado duplicado")
            results[candidate_id] = row
            assignment = assignments.get(candidate_id)
            if not assignment:
                errors.append(f"{candidate_id}: resultado sem atribuição")
                continue
            if row.get("reviewer") != assignment.get("reviewer"):
                errors.append(f"{candidate_id}: revisor diverge da atribuição")
            if row.get("assignment_sha256") != record_sha256(assignment):
                errors.append(f"{candidate_id}: hash da atribuição diverge")
            if row.get("review_status") == "approved" and row.get(
                "final_decision"
            ) != assignment.get("source_decision"):
                errors.append(f"{candidate_id}: aprovação altera a decisão de origem")
            if (
                row.get("review_status") == "changes_requested"
                and row.get("blind_search_outcome") != "blocked"
                and not row.get("evidence_ids")
            ):
                errors.append(f"{candidate_id}: mudança sem evidência oficial")
            for evidence_id in row.get("evidence_ids", []):
                evidence_row = evidence.get(evidence_id)
                if not evidence_row:
                    errors.append(f"{candidate_id}: evidência ausente {evidence_id}")
                elif evidence_row.get("candidate_id") != candidate_id:
                    errors.append(f"{candidate_id}: evidência pertence a outro candidato")

    missing = sorted(set(assignments) - set(results))
    unexpected = sorted(set(results) - set(assignments))
    if missing:
        errors.append(f"resultados ausentes: {len(missing)}")
    if unexpected:
        errors.append(f"resultados inesperados: {len(unexpected)}")

    changes = sorted(
        (row for row in results.values() if row.get("review_status") == "changes_requested"),
        key=lambda row: row["candidate_id"],
    )
    summary = {
        "schema_version": "1.0",
        "assignment_records": len(assignments),
        "result_records": len(results),
        "review_status_counts": dict(
            sorted(Counter(row.get("review_status") for row in results.values()).items())
        ),
        "final_decision_counts": dict(
            sorted(Counter(row.get("final_decision") for row in results.values()).items())
        ),
        "changes_requested": len(changes),
        "assignments_sha256": hashlib.sha256(
            dump_jsonl(sorted(assignments.values(), key=lambda row: row["candidate_id"])).encode(
                "utf-8"
            )
        ).hexdigest(),
        "results_sha256": hashlib.sha256(
            dump_jsonl(sorted(results.values(), key=lambda row: row["candidate_id"])).encode(
                "utf-8"
            )
        ).hexdigest(),
    }
    outputs = {
        "review-summary.json": json.dumps(
            summary, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        "changes-requested.jsonl": dump_jsonl(changes),
    }
    return sorted(set(errors)), outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()
    errors, outputs = build()
    if errors:
        print("Reconciliação de revisão falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    for relative, rendered in outputs.items():
        path = HERE / relative
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                print(f"{path}: ausente ou desatualizado", file=sys.stderr)
                return 1
        else:
            path.write_text(rendered, encoding="utf-8", newline="\n")
    summary = json.loads(outputs["review-summary.json"])
    if args.require_clean and summary["changes_requested"]:
        print(
            f"Revisão possui {summary['changes_requested']} mudanças não adjudicadas.",
            file=sys.stderr,
        )
        return 1
    print(f"Revisão reconciliada: {summary['result_records']} resultados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
