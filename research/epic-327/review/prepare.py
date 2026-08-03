#!/usr/bin/env python3
"""Prepare deterministic independent-review assignments for epic #327."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "review"
ROUTED = {
    "routed_accelerators",
    "routed_angel_networks",
    "routed_funding_platforms",
    "routed_public_programs",
    "routed_other",
}
SAMPLE_DECISIONS = {
    "duplicate",
    "inactive",
    "insufficient_evidence",
    "excluded",
    "unresolved",
}


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
    return "".join(canonical_line(record) + "\n" for record in rows)


def deterministic_sample(rows: list[dict], ratio: float = 0.2) -> list[dict]:
    count = math.ceil(len(rows) * ratio)
    ranked = sorted(
        rows,
        key=lambda row: (
            hashlib.sha256((row["candidate_id"] + "#review").encode("utf-8")).hexdigest(),
            row["candidate_id"],
        ),
    )
    return ranked[:count]


def reviewer_for(source_worker: str, candidate_id: str) -> str:
    if source_worker.startswith("validation-"):
        number = int(source_worker.rsplit("-", 1)[1])
        return f"review-{(number + 1) % 3}"
    digest = hashlib.sha256((candidate_id + "#reviewer").encode("utf-8")).hexdigest()
    return f"review-{int(digest, 16) % 3}"


def assignment(source: dict, name: str, reason: str) -> dict:
    source_worker = source["source_worker"]
    candidate_id = source["candidate_id"]
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "source_kind": source["source_kind"],
        "source_worker": source_worker,
        "source_decision": source["source_decision"],
        "review_reason": reason,
        "reviewer": reviewer_for(source_worker, candidate_id),
        "input_sha256": record_sha256(source["record"]),
        "blind_queries": [
            f'"{name}" official investment firm',
            f'"{name}" startup portfolio Latin America',
        ],
    }


def build(epic: Path = EPIC) -> tuple[list[str], dict[str, str]]:
    errors = []
    candidates_path = epic / "consolidation" / "candidates.jsonl"
    exceptions_path = epic / "consolidation" / "exceptions.jsonl"
    decision_paths = [
        epic / "shards" / f"validation-{number}" / "decisions.jsonl"
        for number in range(3)
    ]
    missing = [path for path in [candidates_path, exceptions_path, *decision_paths] if not path.exists()]
    if missing:
        rendered = ", ".join(path.relative_to(epic).as_posix() for path in missing)
        return [f"inputs de revisão ausentes: {rendered}"], {}

    try:
        candidates = load_jsonl(candidates_path)
        exceptions = load_jsonl(exceptions_path)
        decisions_by_worker = {
            f"validation-{number}": load_jsonl(decision_paths[number])
            for number in range(3)
        }
    except (OSError, ValueError) as exc:
        return [str(exc)], {}
    names = {record["candidate_id"]: record["name"] for record in candidates}

    mandatory = []
    strata: dict[str, list[dict]] = defaultdict(list)
    for worker, decisions in decisions_by_worker.items():
        for record in decisions:
            candidate_id = record.get("candidate_id")
            decision = record.get("decision")
            source = {
                "candidate_id": candidate_id,
                "source_kind": "validation_decision",
                "source_worker": worker,
                "source_decision": decision,
                "record": record,
            }
            if decision == "eligible":
                mandatory.append(assignment(source, names[candidate_id], "all_eligible"))
            elif decision in ROUTED:
                mandatory.append(assignment(source, names[candidate_id], "all_routed"))
            elif decision in SAMPLE_DECISIONS:
                strata[f"decision:{decision}"].append(source)
            else:
                errors.append(f"{candidate_id}: decisão não reconhecida para revisão")

    for record in exceptions:
        status = record.get("status")
        source = {
            "candidate_id": record.get("candidate_id"),
            "source_kind": "identity_exception",
            "source_worker": "reducer",
            "source_decision": status,
            "record": record,
        }
        if status == "identity_conflict":
            mandatory.append(
                assignment(source, names[source["candidate_id"]], "all_identity_conflicts")
            )
        elif status == "unresolved":
            strata["exception:unresolved"].append(source)
        else:
            errors.append(f"{source['candidate_id']}: exception status inválido")

    expansion_path = epic / "review" / "sample-expansions.json"
    expanded_strata = set()
    if expansion_path.exists():
        try:
            expansion = json.loads(expansion_path.read_text(encoding="utf-8"))
            expanded_strata = set(expansion.get("expanded_strata", {}))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{expansion_path}: expansão inválida: {exc}")
    unknown_expansions = expanded_strata - set(strata)
    if unknown_expansions:
        errors.append(
            "estratos de expansão desconhecidos: " + ", ".join(sorted(unknown_expansions))
        )

    sampled = []
    sample_summary = {}
    for stratum, rows in sorted(strata.items()):
        expanded = stratum in expanded_strata
        selected = sorted(rows, key=lambda row: row["candidate_id"]) if expanded else deterministic_sample(rows)
        sample_summary[stratum] = {
            "population": len(rows),
            "selected": len(selected),
            "minimum": math.ceil(len(rows) * 0.2),
            "expanded_to_full_review": expanded,
        }
        sampled.extend(
            assignment(source, names[source["candidate_id"]], "deterministic_exclusion_sample")
            for source in selected
        )
    assignments = sorted(mandatory + sampled, key=lambda row: row["candidate_id"])
    if len(assignments) != len({row["candidate_id"] for row in assignments}):
        errors.append("candidato atribuído mais de uma vez à revisão")

    schema = json.loads(
        (epic / "schemas" / "review-assignment.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for index, record in enumerate(assignments, 1):
        for error in validator.iter_errors(record):
            errors.append(f"assignments:{index}: {error.message}")
        if record["source_worker"].startswith("validation-"):
            source_number = int(record["source_worker"].rsplit("-", 1)[1])
            if record["reviewer"] == f"review-{source_number}":
                errors.append(f"{record['candidate_id']}: autor e revisor coincidem")

    outputs = {
        f"assignments/review-{number}.jsonl": dump_jsonl(
            [record for record in assignments if record["reviewer"] == f"review-{number}"]
        )
        for number in range(3)
    }
    summary = {
        "schema_version": "1.0",
        "issue": 337,
        "assignment_records": len(assignments),
        "reason_counts": dict(sorted(Counter(row["review_reason"] for row in assignments).items())),
        "reviewer_counts": dict(sorted(Counter(row["reviewer"] for row in assignments).items())),
        "sample_strata": sample_summary,
    }
    outputs["assignment-summary.json"] = json.dumps(
        summary, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"
    return sorted(set(errors)), outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors, outputs = build()
    if errors:
        print("Preparação da revisão falhou:", file=sys.stderr)
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
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
    print("Atribuições de revisão preparadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
