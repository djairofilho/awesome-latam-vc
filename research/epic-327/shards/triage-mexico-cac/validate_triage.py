#!/usr/bin/env python3
"""Validate official identity triage for issue #330."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parent
EPIC = HERE.parents[1]
STATUSES = {"duplicate", "routed", "identity_confirmed", "identity_unresolved"}
CATEGORIES = {
    "fund",
    "fund_candidate",
    "accelerator",
    "angel_network",
    "funding_platform",
    "public_program",
    "other",
    "unresolved",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def domain(url: str | None) -> str | None:
    if not url:
        return None
    return (urlsplit(url).hostname or "").casefold().removeprefix("www.") or None


def validate() -> list[str]:
    errors: list[str] = []
    intake = read_jsonl(HERE / "intake.jsonl")
    triage = read_jsonl(HERE / "triage.jsonl")
    evidence = read_jsonl(HERE / "official-evidence.jsonl")
    summary = read_json(HERE / "triage-summary.json")
    schema = read_json(EPIC / "schemas" / "official-evidence-record.schema.json")
    schema_validator = Draft202012Validator(schema, format_checker=FormatChecker())

    intake_ids = {row["candidate_id"] for row in intake}
    triage_ids = [row.get("candidate_id") for row in triage]
    if len(triage_ids) != len(set(triage_ids)):
        errors.append("triage.jsonl: candidate_id duplicado")
    if set(triage_ids) != intake_ids:
        errors.append("triage.jsonl: cobertura difere do intake")

    evidence_by_id = {row.get("evidence_id"): row for row in evidence}
    if len(evidence_by_id) != len(evidence):
        errors.append("official-evidence.jsonl: evidence_id duplicado")
    for line_number, row in enumerate(evidence, start=1):
        for error in schema_validator.iter_errors(row):
            errors.append(f"official-evidence.jsonl:{line_number}: {error.message}")

    for line_number, row in enumerate(triage, start=1):
        if row.get("status") not in STATUSES:
            errors.append(f"triage.jsonl:{line_number}: status inválido")
        if row.get("category") not in CATEGORIES:
            errors.append(f"triage.jsonl:{line_number}: categoria inválida")
        if not row.get("official_domain") and not row.get("search", {}).get("query"):
            errors.append(f"triage.jsonl:{line_number}: sem domínio ou busca documentada")
        if row.get("official_domain") != domain(row.get("official_url")):
            errors.append(f"triage.jsonl:{line_number}: domínio não corresponde à URL")
        evidence_ids = row.get("evidence_ids", [])
        if row.get("official_url") and not evidence_ids:
            errors.append(f"triage.jsonl:{line_number}: identidade oficial sem evidência")
        if any(evidence_id not in evidence_by_id for evidence_id in evidence_ids):
            errors.append(f"triage.jsonl:{line_number}: evidence_id inexistente")
        if row.get("status") == "duplicate" and not row.get("canonical_profile"):
            errors.append(f"triage.jsonl:{line_number}: duplicata sem perfil canônico")
        if row.get("status") == "routed" and not (
            row.get("canonical_profile") or row.get("route_destination")
        ):
            errors.append(f"triage.jsonl:{line_number}: rota sem destino determinístico")
        if row.get("status") == "identity_unresolved" and row.get("category") != "unresolved":
            errors.append(f"triage.jsonl:{line_number}: identidade pendente com categoria inferida")
        if row.get("status") == "identity_confirmed" and row.get("category") != "fund_candidate":
            errors.append(f"triage.jsonl:{line_number}: candidato de fundo com categoria divergente")

    status_counts = dict(sorted(Counter(row["status"] for row in triage).items()))
    category_counts = dict(sorted(Counter(row["category"] for row in triage).items()))
    expected = {
        "candidate_count": len(triage),
        "official_identity_confirmed": sum(bool(row["official_domain"]) for row in triage),
        "official_search_documented": sum(bool(row["search"]["query"]) for row in triage),
        "status_counts": status_counts,
        "category_counts": category_counts,
        "evidence_records": len(evidence),
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"triage-summary.json: {key} divergente")
    if summary.get("activity_validation") != "pending" or summary.get("regional_access_validation") != "pending":
        errors.append("triage-summary.json: validação factual não deve ser inferida na triagem")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação da triagem falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Triagem oficial validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
