#!/usr/bin/env python3
"""Validate the Southern Cone and Brazil identity triage."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
ALLOWED_OUTCOMES = {
    "baseline_match",
    "official_domain_confirmed",
    "identity_collision",
    "no_official_domain_confirmed",
}
ALLOWED_STATUS = {
    "baseline_match",
    "official_domain_confirmed",
    "identity_collision",
    "not_confirmed",
}
ALLOWED_ROUTES = {
    "duplicate_baseline",
    "official_identity_validation",
    "research_official_identity",
    "resolve_identity_collision",
    "routed_accelerators",
    "routed_angel_networks",
    "routed_funding_platforms",
    "routed_public_programs",
}
ALLOWED_CLAIMS = {"identity", "category"}


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalized_host(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def validate() -> list[str]:
    errors: list[str] = []
    intake = load_jsonl(HERE / "intake.jsonl")
    triage = load_jsonl(HERE / "triage.jsonl")
    evidence = load_jsonl(HERE / "official-evidence.jsonl")
    summary = json.loads((HERE / "triage-summary.json").read_text(encoding="utf-8"))

    intake_by_id = {row["candidate_id"]: row for row in intake}
    triage_by_id = {row["candidate_id"]: row for row in triage}
    if len(intake_by_id) != len(intake) or len(triage_by_id) != len(triage):
        errors.append("candidate_id duplicado")
    if set(intake_by_id) != set(triage_by_id):
        errors.append("cobertura da triagem divergente do intake")

    evidence_by_id: dict[str, dict] = {}
    for index, record in enumerate(evidence, start=1):
        required = {
            "schema_version",
            "evidence_id",
            "candidate_id",
            "official_url",
            "source_title",
            "accessed_on",
            "source_kind",
            "claims",
        }
        if set(record) != required:
            errors.append(f"official-evidence.jsonl:{index}: campos divergentes")
        evidence_id = record.get("evidence_id", "")
        if evidence_id in evidence_by_id:
            errors.append(f"official-evidence.jsonl:{index}: evidence_id duplicado")
        evidence_by_id[evidence_id] = record
        if record.get("schema_version") != "1.0":
            errors.append(f"official-evidence.jsonl:{index}: versão inválida")
        if not re.fullmatch(r"evidence-delta-[a-z0-9-]+", evidence_id):
            errors.append(f"official-evidence.jsonl:{index}: evidence_id inválido")
        if record.get("candidate_id") not in intake_by_id:
            errors.append(f"official-evidence.jsonl:{index}: candidato ausente")
        if record.get("source_kind") != "official_identity":
            errors.append(f"official-evidence.jsonl:{index}: tipo de fonte inválido")
        if record.get("accessed_on") != "2026-08-02":
            errors.append(f"official-evidence.jsonl:{index}: data divergente")
        if not normalized_host(record.get("official_url", "")):
            errors.append(f"official-evidence.jsonl:{index}: URL oficial inválida")
        claims = record.get("claims", [])
        if not claims or any(
            set(claim) != {"field", "value", "support"}
            or claim.get("field") not in ALLOWED_CLAIMS
            or not claim.get("support")
            for claim in claims
        ):
            errors.append(f"official-evidence.jsonl:{index}: claims inválidos")

    counts = {outcome: 0 for outcome in ALLOWED_OUTCOMES}
    routes: dict[str, int] = {}
    partitions = {"0": 0, "1": 0, "2": 0}
    for index, record in enumerate(triage, start=1):
        if set(record) != {
            "schema_version",
            "candidate_id",
            "name",
            "search",
            "identity",
            "category_route",
            "evidence_ids",
            "validation_partition",
        }:
            errors.append(f"triage.jsonl:{index}: campos divergentes")
        if record.get("schema_version") != "1.0":
            errors.append(f"triage.jsonl:{index}: versão inválida")
        candidate_id = record.get("candidate_id", "")
        source = intake_by_id.get(candidate_id, {})
        if record.get("name") != source.get("name"):
            errors.append(f"triage.jsonl:{index}: nome divergente")
        search = record.get("search", {})
        outcome = search.get("outcome")
        if set(search) != {"searched_on", "query", "outcome"}:
            errors.append(f"triage.jsonl:{index}: busca inválida")
        if search.get("searched_on") != "2026-08-02" or outcome not in ALLOWED_OUTCOMES:
            errors.append(f"triage.jsonl:{index}: resultado de busca inválido")
        counts[outcome] = counts.get(outcome, 0) + 1
        if outcome == "baseline_match" and search.get("query") is not None:
            errors.append(f"triage.jsonl:{index}: match de baseline com busca")
        if outcome != "baseline_match" and not search.get("query"):
            errors.append(f"triage.jsonl:{index}: busca não documentada")
        identity = record.get("identity", {})
        if set(identity) - {"status", "official_domain", "canonical_profile"}:
            errors.append(f"triage.jsonl:{index}: identidade com campos adicionais")
        if identity.get("status") not in ALLOWED_STATUS:
            errors.append(f"triage.jsonl:{index}: status de identidade inválido")
        if outcome == "official_domain_confirmed":
            if not identity.get("official_domain") or len(record.get("evidence_ids", [])) != 1:
                errors.append(f"triage.jsonl:{index}: domínio confirmado incompleto")
        elif identity.get("official_domain") is not None and outcome != "baseline_match":
            errors.append(f"triage.jsonl:{index}: domínio sem confirmação")
        if outcome == "baseline_match":
            if source.get("baseline_status") not in {"exact_name", "alias", "identity_collision"}:
                errors.append(f"triage.jsonl:{index}: baseline_status divergente")
            if identity.get("canonical_profile") not in source.get("baseline_matches", []):
                errors.append(f"triage.jsonl:{index}: perfil canônico divergente")
        for evidence_id in record.get("evidence_ids", []):
            item = evidence_by_id.get(evidence_id)
            if not item or item.get("candidate_id") != candidate_id:
                errors.append(f"triage.jsonl:{index}: evidência não vinculada")
            elif normalized_host(item["official_url"]) != identity.get("official_domain"):
                errors.append(f"triage.jsonl:{index}: domínio da evidência divergente")
        route = record.get("category_route")
        if route not in ALLOWED_ROUTES:
            errors.append(f"triage.jsonl:{index}: rota inválida")
        routes[route] = routes.get(route, 0) + 1
        expected_partition = int(hashlib.sha256(candidate_id.encode()).hexdigest(), 16) % 3
        partition = record.get("validation_partition")
        if partition != expected_partition:
            errors.append(f"triage.jsonl:{index}: partição divergente")
        partitions[str(partition)] = partitions.get(str(partition), 0) + 1

    if set(evidence_by_id) != {
        evidence_id
        for record in triage
        for evidence_id in record.get("evidence_ids", [])
    }:
        errors.append("evidências órfãs ou ausentes")

    expected_summary = {
        "candidates_total": len(triage),
        "baseline_matches": counts["baseline_match"],
        "searches_documented": len(triage) - counts["baseline_match"],
        "search_failures": 0,
        "official_domains_confirmed": counts["official_domain_confirmed"],
        "identity_collisions": counts["identity_collision"],
        "searches_without_confirmation": counts["no_official_domain_confirmed"],
        "official_evidence_records": len(evidence),
        "category_routes": routes,
        "validation_partitions": partitions,
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"triage-summary.json: {key} divergente")

    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação da triagem sul e Brasil falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Triagem sul e Brasil validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
