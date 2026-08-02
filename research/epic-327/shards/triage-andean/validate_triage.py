#!/usr/bin/env python3
"""Validate official identity triage without mutating any artifact."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
EPIC = HERE.parents[1]
TRIAGE_KEYS = {
    "schema_version",
    "candidate_id",
    "triage_status",
    "official_domain",
    "category_hint",
    "canonical_profile",
    "evidence_ids",
    "next_action",
}
TRIAGE_STATUSES = {
    "baseline_duplicate",
    "official_duplicate",
    "official_identity_resolved",
    "official_route_resolved",
    "unresolved",
}
SEARCH_KEYS = {
    "schema_version",
    "candidate_id",
    "searched_on",
    "queries",
    "terminal_result",
}
SUMMARY_KEYS = {
    "schema_version",
    "worker_id",
    "candidate_count",
    "evidence_record_count",
    "search_record_count",
    "covered_candidate_count",
    "uncovered_candidate_count",
    "coverage_counts",
    "status_counts",
    "official_sources_only",
    "eligibility_decisions_made",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalized_host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def validate() -> list[str]:
    errors: list[str] = []
    intake = load_jsonl(HERE / "intake.jsonl")
    triage = load_jsonl(HERE / "triage.jsonl")
    evidence = load_jsonl(HERE / "official-evidence.jsonl")
    searches = load_jsonl(HERE / "search-log.jsonl")
    summary = load_json(HERE / "triage-summary.json")
    evidence_schema = load_json(EPIC / "schemas" / "official-evidence-record.schema.json")
    evidence_validator = Draft202012Validator(evidence_schema)

    intake_by_id = {row["candidate_id"]: row for row in intake}
    triage_by_id = {row.get("candidate_id"): row for row in triage}
    if len(triage_by_id) != len(triage):
        errors.append("triage.jsonl: candidate_id duplicado")
    if set(triage_by_id) != set(intake_by_id):
        errors.append("triage.jsonl: cobertura não corresponde ao intake")
    if [row.get("candidate_id") for row in triage] != sorted(triage_by_id):
        errors.append("triage.jsonl: candidate_id fora de ordem")

    evidence_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(evidence, start=1):
        for finding in evidence_validator.iter_errors(row):
            errors.append(f"official-evidence.jsonl:{index}: {finding.message}")
        evidence_id = row.get("evidence_id")
        if evidence_id in evidence_by_id:
            errors.append(f"official-evidence.jsonl:{index}: evidence_id duplicado")
        evidence_by_id[evidence_id] = row
    linked_evidence: set[str] = set()
    status_counts: Counter[str] = Counter()
    for index, row in enumerate(triage, start=1):
        if set(row) != TRIAGE_KEYS:
            errors.append(f"triage.jsonl:{index}: chaves divergentes")
            continue
        status = row["triage_status"]
        if status not in TRIAGE_STATUSES:
            errors.append(f"triage.jsonl:{index}: status inválido")
            continue
        status_counts[status] += 1
        intake_row = intake_by_id.get(row["candidate_id"])
        ids = row["evidence_ids"]
        if len(ids) != len(set(ids)) or any(item not in evidence_by_id for item in ids):
            errors.append(f"triage.jsonl:{index}: evidence_ids inválidos")
        linked_evidence.update(ids)
        for evidence_id in ids:
            if evidence_by_id[evidence_id]["candidate_id"] != row["candidate_id"]:
                errors.append(f"triage.jsonl:{index}: evidência ligada a outro candidato")

        if status == "baseline_duplicate":
            expected = intake_row["baseline_matches"] if intake_row else []
            if len(expected) != 1 or row["canonical_profile"] != expected[0]:
                errors.append(f"triage.jsonl:{index}: duplicata do baseline divergente")
            if ids or row["official_domain"] is not None:
                errors.append(f"triage.jsonl:{index}: duplicata do baseline deve reutilizar apenas o baseline")
        elif status == "official_duplicate":
            if not ids or not row["canonical_profile"] or not row["official_domain"]:
                errors.append(f"triage.jsonl:{index}: duplicata oficial incompleta")
        elif status == "official_route_resolved":
            if not ids or not row["official_domain"] or not row["category_hint"]:
                errors.append(f"triage.jsonl:{index}: rota oficial incompleta")
        elif status == "official_identity_resolved":
            if not ids or not row["official_domain"] or row["canonical_profile"] is not None:
                errors.append(f"triage.jsonl:{index}: identidade oficial incompleta")
        elif status == "unresolved":
            if ids or any(row[key] is not None for key in ("official_domain", "category_hint", "canonical_profile")):
                errors.append(f"triage.jsonl:{index}: candidato não resolvido contém fatos")

        if ids:
            expected_domains = {
                normalized_host(evidence_by_id[evidence_id]["official_url"])
                for evidence_id in ids
            }
            if row["official_domain"] not in expected_domains:
                errors.append(f"triage.jsonl:{index}: domínio não deriva da evidência oficial")

    if set(evidence_by_id) != linked_evidence:
        errors.append("official-evidence.jsonl: existe evidência órfã")

    search_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(searches, start=1):
        if set(row) != SEARCH_KEYS:
            errors.append(f"search-log.jsonl:{index}: chaves divergentes")
            continue
        candidate_id = row["candidate_id"]
        if candidate_id in search_by_id:
            errors.append(f"search-log.jsonl:{index}: candidate_id duplicado")
        search_by_id[candidate_id] = row
        if row["schema_version"] != "1.0" or row["searched_on"] != "2026-08-02":
            errors.append(f"search-log.jsonl:{index}: metadados divergentes")
        queries = row["queries"]
        if not isinstance(queries, list) or not queries or any(
            not isinstance(query, str) or not query.strip() for query in queries
        ):
            errors.append(f"search-log.jsonl:{index}: consultas inválidas")
        if row["terminal_result"] != "no_unambiguous_official_identity":
            errors.append(f"search-log.jsonl:{index}: resultado terminal inválido")
    if [row.get("candidate_id") for row in searches] != sorted(search_by_id):
        errors.append("search-log.jsonl: candidate_id fora de ordem")

    unresolved_ids = {
        row["candidate_id"] for row in triage if row["triage_status"] == "unresolved"
    }
    resolved_ids = set(triage_by_id) - unresolved_ids
    if set(search_by_id) != unresolved_ids:
        errors.append("search-log.jsonl: buscas não correspondem aos candidatos não resolvidos")
    covered_ids = resolved_ids | set(search_by_id)
    uncovered_ids = set(triage_by_id) - covered_ids
    if set(summary) != SUMMARY_KEYS:
        errors.append("triage-summary.json: chaves divergentes")
    if summary.get("worker_id") != "triage-andean":
        errors.append("triage-summary.json: worker_id divergente")
    if summary.get("candidate_count") != len(triage):
        errors.append("triage-summary.json: candidate_count divergente")
    if summary.get("evidence_record_count") != len(evidence):
        errors.append("triage-summary.json: evidence_record_count divergente")
    if summary.get("search_record_count") != len(searches):
        errors.append("triage-summary.json: search_record_count divergente")
    if summary.get("covered_candidate_count") != len(covered_ids):
        errors.append("triage-summary.json: covered_candidate_count divergente")
    if summary.get("uncovered_candidate_count") != len(uncovered_ids):
        errors.append("triage-summary.json: uncovered_candidate_count divergente")
    expected_coverage_counts = {
        "resolved_by_baseline_or_official": len(resolved_ids),
        "documented_terminal_search": len(search_by_id),
    }
    if summary.get("coverage_counts") != expected_coverage_counts:
        errors.append("triage-summary.json: coverage_counts divergente")
    if summary.get("status_counts") != dict(sorted(status_counts.items())):
        errors.append("triage-summary.json: status_counts divergente")
    if summary.get("official_sources_only") is not True:
        errors.append("triage-summary.json: fontes oficiais não garantidas")
    if summary.get("eligibility_decisions_made") != 0:
        errors.append("triage-summary.json: triagem antecipou elegibilidade")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação da triagem andina falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Triagem andina validada com evidências exclusivamente oficiais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
