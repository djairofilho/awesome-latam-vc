#!/usr/bin/env python3
"""Build or validate deterministic publication batches from the #337 freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
DEFAULT_MANIFEST = EPIC / "review" / "freeze-manifest.json"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "publication-plan.json"
INPUT_SCHEMA = EPIC / "schemas" / "publication-freeze-manifest.schema.json"
PLAN_SCHEMA = EPIC / "schemas" / "publication-plan.schema.json"
BATCH_LIMIT = 10


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_records(records: list[dict[str, Any]]) -> str:
    return "".join(
        canonical_json(record) + "\n"
        for record in sorted(records, key=lambda row: row["candidate_id"])
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def duplicate_values(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: raiz deve ser objeto JSON")
    return value


def schema_errors(value: dict[str, Any], schema_path: Path, label: str) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return sorted(
        f"{label}: {finding.message}"
        for finding in validator.iter_errors(value)
    )


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors = schema_errors(manifest, INPUT_SCHEMA, "manifest")
    records = manifest.get("eligible_records")
    if not isinstance(records, list):
        return errors

    if manifest.get("eligible_count") != len(records):
        errors.append("manifest: eligible_count diverge de eligible_records")
    candidate_ids = [
        record.get("candidate_id")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("candidate_id"), str)
    ]
    review_ids = [
        record.get("review_record_id")
        for record in records
        if isinstance(record, dict) and isinstance(record.get("review_record_id"), str)
    ]
    duplicate_candidates = duplicate_values(candidate_ids)
    duplicate_reviews = duplicate_values(review_ids)
    if duplicate_candidates:
        errors.append(f"manifest: candidate_id duplicado: {duplicate_candidates}")
    if duplicate_reviews:
        errors.append(f"manifest: review_record_id duplicado: {duplicate_reviews}")
    ineligible = sorted(
        record.get("candidate_id", "<unknown>")
        for record in records
        if isinstance(record, dict) and record.get("decision") != "eligible"
    )
    if ineligible:
        errors.append(f"manifest: eligible_records contém inelegíveis: {ineligible}")
    if (
        isinstance(manifest.get("cutoff_date"), str)
        and isinstance(manifest.get("frozen_on"), str)
        and manifest["frozen_on"] < manifest["cutoff_date"]
    ):
        errors.append("manifest: frozen_on é anterior a cutoff_date")
    return sorted(set(errors))


def manifest_label(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def member(record: dict[str, Any]) -> dict[str, Any]:
    result = dict(record)
    result["record_sha256"] = sha256_text(canonical_json(record))
    return result


def build_plan(
    manifest: dict[str, Any], manifest_bytes: bytes, source_manifest: str
) -> dict[str, Any]:
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("\n".join(errors))

    records = sorted(manifest["eligible_records"], key=lambda row: row["candidate_id"])
    batches = []
    for offset in range(0, len(records), BATCH_LIMIT):
        ordinal = offset // BATCH_LIMIT + 1
        suffix = f"{ordinal:03d}"
        candidates = [member(record) for record in records[offset : offset + BATCH_LIMIT]]
        batches.append(
            {
                "batch_id": f"publication-batch-{suffix}",
                "ordinal": ordinal,
                "branch": f"feat/issue-338-batch-{suffix}",
                "worktree": f".worktrees/issue-338-batch-{suffix}",
                "candidate_count": len(candidates),
                "candidates": candidates,
            }
        )

    return {
        "schema_version": "1.0",
        "issue": 338,
        "source_manifest": source_manifest,
        "source_manifest_sha256": sha256_bytes(manifest_bytes),
        "source_decisions_sha256": manifest["source_decisions_sha256"],
        "review_records_sha256": manifest["review_records_sha256"],
        "eligible_records_sha256": sha256_text(canonical_records(records)),
        "cutoff_date": manifest["cutoff_date"],
        "batch_size_limit": BATCH_LIMIT,
        "batch_count_formula": "ceil(eligible_count / 10)",
        "eligible_count": len(records),
        "batch_count": math.ceil(len(records) / BATCH_LIMIT),
        "batches": batches,
        "audit": {
            "covered_candidate_count": len(records),
            "duplicate_candidate_ids": [],
            "duplicate_review_record_ids": [],
            "ineligible_batch_members": [],
            "unplanned_candidate_ids": [],
            "batch_size_limit_respected": True,
        },
    }


def validate_plan(
    manifest: dict[str, Any], manifest_bytes: bytes, plan: dict[str, Any]
) -> list[str]:
    errors = validate_manifest(manifest)
    errors.extend(schema_errors(plan, PLAN_SCHEMA, "plan"))
    batches = plan.get("batches")
    if not isinstance(batches, list):
        return sorted(set(errors))

    members = [
        candidate
        for batch in batches
        if isinstance(batch, dict) and isinstance(batch.get("candidates"), list)
        for candidate in batch["candidates"]
        if isinstance(candidate, dict)
    ]
    ids = [row.get("candidate_id") for row in members if isinstance(row.get("candidate_id"), str)]
    duplicate_ids = duplicate_values(ids)
    if duplicate_ids:
        errors.append(f"plan: candidatos duplicados entre lotes: {duplicate_ids}")
    ineligible = sorted(
        row.get("candidate_id", "<unknown>")
        for row in members
        if row.get("decision") != "eligible"
    )
    if ineligible:
        errors.append(f"plan: membros inelegíveis: {ineligible}")
    expected_ids = {
        row["candidate_id"]
        for row in manifest.get("eligible_records", [])
        if isinstance(row, dict) and isinstance(row.get("candidate_id"), str)
    }
    if set(ids) != expected_ids:
        errors.append(
            "plan: cobertura inexata; "
            f"ausentes={sorted(expected_ids - set(ids))}, extras={sorted(set(ids) - expected_ids)}"
        )
    if any(
        not isinstance(batch, dict)
        or batch.get("candidate_count") != len(batch.get("candidates", []))
        or len(batch.get("candidates", [])) > BATCH_LIMIT
        for batch in batches
    ):
        errors.append("plan: contagem de lote divergente ou limite excedido")

    if not errors:
        expected = build_plan(manifest, manifest_bytes, plan.get("source_manifest", ""))
        if plan != expected:
            errors.append("plan: conteúdo diverge do plano determinístico esperado")
    return sorted(set(errors))


def render(plan: dict[str, Any]) -> str:
    return json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not args.manifest.is_file():
        print(f"Manifesto congelado ausente: {args.manifest}", file=sys.stderr)
        return 1
    try:
        manifest_bytes = args.manifest.read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        plan = build_plan(manifest, manifest_bytes, manifest_label(args.manifest))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Planejamento de publicação falhou: {exc}", file=sys.stderr)
        return 1

    rendered = render(plan)
    if args.check:
        if not args.output.is_file():
            print(f"Plano ausente: {args.output}", file=sys.stderr)
            return 1
        existing = load_json(args.output)
        errors = validate_plan(manifest, manifest_bytes, existing)
        if errors or args.output.read_text(encoding="utf-8") != rendered:
            for error in errors or ["plan: serialização não canônica ou desatualizada"]:
                print(error, file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Plano validado: {plan['eligible_count']} elegíveis em {plan['batch_count']} lotes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
