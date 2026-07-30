"""Build the adjudicated Brazil funds bundle for issue #220."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable


BRAZIL = Path(__file__).resolve().parent
DISCOVERY_BUILDER = BRAZIL / "build_consolidated.py"
CUTOFF_DATE = "2026-07-30"
VALIDATION_WORKERS = (
    "worker-217-validation",
    "worker-218-validation",
    "worker-219-validation",
)
ADJUDICATION_WORKER = "worker-220-adjudication"
CORE_JSONL = (
    "source-inventory.jsonl",
    "candidates.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "review-sample.jsonl",
)
GENERATED = (
    *CORE_JSONL,
    "run-manifest.jsonl",
    "audit-report.json",
    "adjudication-summary.json",
)
ID_FIELDS = {
    "source-inventory.jsonl": "source_id",
    "candidates.jsonl": "candidate_id",
    "evidence.jsonl": "evidence_id",
    "identity-resolution.jsonl": "resolution_id",
    "cvm-query-log.jsonl": "query_id",
}
EXPECTED_QUERY_CANDIDATES = {
    "fund-br-213-vinci-partners",
    "fund-br-214-jatoba-impacto-amazonia",
}
EXPECTED_DECISIONS = {
    "eligible": 14,
    "duplicate": 11,
    "routed_accelerators": 1,
    "routed_angel_networks": 1,
    "insufficient_evidence": 24,
}
STALE_ACCESS_DATE_ACTIVITY_EVIDENCE = {
    "ev-fund-br-215-accion-ventures",
    "ev-fund-br-215-antler-brazil",
}
RESEARCH_TASKS = (
    (210, "discovery", "allocators", "non_cvm", "worker-210-allocators"),
    (211, "discovery", "rounds", "non_cvm", "worker-211-rounds"),
    (212, "discovery", "launches", "non_cvm", "worker-212-launches"),
    (213, "discovery", "events", "non_cvm", "worker-213-events"),
    (214, "discovery", "sector_maps", "non_cvm", "worker-214-maps"),
    (214, "discovery", "regional_sources", "non_cvm", "worker-214-maps"),
    (215, "discovery", "foreign_access", "non_cvm", "worker-215-foreign-access"),
    (217, "validation", "official_portfolios", "non_cvm", "worker-217-validation"),
    (218, "validation", "official_portfolios", "non_cvm", "worker-218-validation"),
    (219, "validation", "official_portfolios", "non_cvm", "worker-219-validation"),
    (220, "adjudication", "cvm", "cvm", ADJUDICATION_WORKER),
)


def compact_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            raise ValueError(f"{path}:{line_number}: linha JSONL vazia")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: registro deve ser objeto")
        records.append(value)
    return records


def records_from_bytes(content: bytes) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in content.decode("utf-8").splitlines()
        if line
    ]


def load_discovery_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "epic_207_discovery_builder", DISCOVERY_BUILDER
    )
    if spec is None or spec.loader is None:
        raise ValueError("não foi possível carregar build_consolidated.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _index(
    records: Iterable[dict[str, Any]], field: str, label: str
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[field]
        if record_id in result:
            raise ValueError(f"{label}: ID duplicado: {record_id}")
        result[record_id] = record
    return result


def _validation_records(filename: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for worker in VALIDATION_WORKERS:
        path = BRAZIL / "shards" / worker / filename
        if path.is_file():
            records.extend(read_jsonl(path))
    return records


def _adjudication_records(filename: str) -> list[dict[str, Any]]:
    path = BRAZIL / "shards" / ADJUDICATION_WORKER / filename
    if not path.is_file():
        raise ValueError(f"shard de adjudicação ausente: {path}")
    return read_jsonl(path)


def _merge_new(
    base: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    field: str,
    label: str,
) -> list[dict[str, Any]]:
    result = _index(base, field, label)
    for record in additions:
        record_id = record[field]
        if record_id in result:
            raise ValueError(f"{label}: adição colide com ID existente: {record_id}")
        result[record_id] = record
    return [result[record_id] for record_id in sorted(result)]


def _apply_complete_candidate_overlays(
    base: list[dict[str, Any]],
    overlays: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = _index(base, "candidate_id", "candidates.jsonl")
    overlay_index = _index(overlays, "candidate_id", "overlays de candidato")
    if set(overlay_index) != set(result):
        missing = sorted(set(result) - set(overlay_index))
        extra = sorted(set(overlay_index) - set(result))
        raise ValueError(
            "os overlays devem cobrir exatamente os 51 candidatos: "
            f"ausentes={missing}, extras={extra}"
        )
    for candidate_id, overlay in overlay_index.items():
        if overlay["discovered_on"] != result[candidate_id]["discovered_on"]:
            raise ValueError(f"{candidate_id}: discovered_on foi alterado")
        result[candidate_id] = overlay
    return [result[candidate_id] for candidate_id in sorted(result)]


def _apply_resolution_overlays(
    base: list[dict[str, Any]],
    validation_additions: list[dict[str, Any]],
    adjudication_overlays: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = _merge_new(
        base,
        validation_additions,
        "resolution_id",
        "identity-resolution.jsonl",
    )
    result = _index(merged, "resolution_id", "identity-resolution.jsonl")
    expected = {
        "identity-fund-br-vinci-prior-managers",
        "identity-fund-br-jatoba-impacto-amazonia-vehicle",
    }
    actual = {record["resolution_id"] for record in adjudication_overlays}
    if actual != expected:
        raise ValueError(
            "adjudicação deve atualizar somente Vinci e Jatobá: "
            f"esperado={sorted(expected)}, atual={sorted(actual)}"
        )
    for record in adjudication_overlays:
        if record["resolution_id"] not in result:
            raise ValueError(
                "overlay de identidade sem resolução anterior: "
                f"{record['resolution_id']}"
            )
        result[record["resolution_id"]] = record
    return [result[record_id] for record_id in sorted(result)]


def _query_checks(
    queries: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> None:
    query_candidates = {record["candidate_id"] for record in queries}
    if len(queries) != 2 or query_candidates != EXPECTED_QUERY_CANDIDATES:
        raise ValueError(
            "a tarefa CVM deve conter exatamente as consultas de Vinci e Jatobá"
        )
    allowed_claims = {
        "legal_identity",
        "manager_vehicle_relation",
        "regulatory_divergence",
    }
    if any(
        set(record["confirmed_claims"]) - allowed_claims for record in queries
    ):
        raise ValueError("consulta CVM contém claim fora do escopo regulatório")
    cvm_evidence = [
        record for record in evidence if record["source_class"] == "cvm"
    ]
    if {record["candidate_id"] for record in cvm_evidence} != query_candidates:
        raise ValueError("evidência CVM deve cobrir somente Vinci e Jatobá")
    query_ids = {record["query_id"] for record in queries}
    if any(record["cvm_query_id"] not in query_ids for record in cvm_evidence):
        raise ValueError("evidência CVM referencia consulta ausente")


def _correct_stale_access_date_activity(
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = [dict(record) for record in evidence]
    index = _index(result, "evidence_id", "evidence.jsonl")
    for evidence_id in STALE_ACCESS_DATE_ACTIVITY_EVIDENCE:
        record = index[evidence_id]
        if record["published_on"] is not None:
            raise ValueError(
                f"{evidence_id}: correção esperava published_on ausente"
            )
        record["observed_on"] = None
        record["claims"] = [
            {
                **claim,
                "finding": "inconclusive",
            }
            if claim["field"] == "activity"
            else claim
            for claim in record["claims"]
        ]
    return sorted(result, key=lambda record: record["evidence_id"])


def build_coverage(
    discovery_rows: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    queries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_index = _index(sources, "source_id", "source-inventory.jsonl")
    validation_rows = []
    for worker in ("worker-217-validation", "worker-219-validation"):
        validation_rows.extend(
            read_jsonl(BRAZIL / "shards" / worker / "coverage-matrix.jsonl")
        )
    validation_source_ids = sorted(
        {
            source_id
            for row in validation_rows
            for source_id in row["source_ids"]
        }
    )
    validation_candidate_ids = sorted(
        {
            candidate_id
            for row in validation_rows
            for candidate_id in row["candidate_ids"]
        }
    )
    if (
        len(validation_source_ids) != 32
        or len(validation_candidate_ids) != 32
    ):
        raise ValueError(
            "cobertura #217 + #219 deve reduzir para 32 fontes e 32 candidatos"
        )
    missing = set(validation_source_ids) - set(source_index)
    if missing:
        raise ValueError(
            f"cobertura de validação referencia fontes ausentes: {sorted(missing)}"
        )
    cvm_source_ids = sorted(
        source["source_id"]
        for source in sources
        if source["research_channel"] == "cvm"
    )
    rows = [dict(record) for record in discovery_rows]
    rows.extend(
        [
            {
                "schema_version": "1.0",
                "coverage_id": "coverage-fund-br-220-official-validation",
                "issue": 220,
                "source_family": "official_portfolios",
                "geography_scope": "brazil",
                "source_ids": validation_source_ids,
                "planned_sources": 32,
                "completed_sources": 32,
                "candidate_ids": validation_candidate_ids,
                "status": "complete",
                "reason": (
                    "Redução única das passagens oficiais #217 e #219. O "
                    "bloqueio pontual registrado no inventário foi adjudicado "
                    "com fonte oficial alternativa dentro da mesma passagem."
                ),
                "owner": None,
                "next_action": None,
            },
            {
                "schema_version": "1.0",
                "coverage_id": "coverage-fund-br-220-cvm-adjudication",
                "issue": 220,
                "source_family": "cvm",
                "geography_scope": "brazil",
                "source_ids": cvm_source_ids,
                "planned_sources": len(cvm_source_ids),
                "completed_sources": len(cvm_source_ids),
                "candidate_ids": sorted(
                    {record["candidate_id"] for record in queries}
                ),
                "status": "complete",
                "reason": (
                    "Duas consultas direcionadas e concluídas, restritas a "
                    "identidade e relação gestora-veículo."
                ),
                "owner": None,
                "next_action": None,
            },
        ]
    )
    keys = [
        (record["source_family"], record["geography_scope"])
        for record in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError("cobertura reconciliada contém célula duplicada")
    return sorted(rows, key=lambda record: record["coverage_id"])


def _run_manifest(
    artifact_hashes: dict[str, str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "schema_version": "1.0",
            "record_type": "run",
            "run_id": "run-fund-br-207",
            "issues": list(range(210, 221)),
            "contract_issue": 208,
            "cutoff_date": CUTOFF_DATE,
            "created_on": CUTOFF_DATE,
            "status": "completed",
            "task_count": len(RESEARCH_TASKS),
            "coordinator": "worker-220-adjudication",
            "scraping_performed": False,
            "hash_algorithm": "sha256",
            "artifact_hashes": artifact_hashes,
            "notes": (
                "A issue #220 aplicou os 51 overlays de validação e executou "
                "uma tarefa CVM com duas consultas direcionadas. A CVM foi "
                "usada somente para identidade e relação gestora-veículo."
            ),
        }
    ]
    for issue, phase, family, channel, worker in RESEARCH_TASKS:
        suffix = family.replace("_", "-")
        task_id = (
            f"task-fund-br-{issue}-cvm-adjudication"
            if issue == 220
            else f"task-fund-br-{issue}-{phase}-{suffix}"
        )
        rows.append(
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": "run-fund-br-207",
                "task_id": task_id,
                "issue": issue,
                "phase": phase,
                "source_family": family,
                "research_channel": channel,
                "worker_id": worker,
                "shard_path": f"research/epic-207/brazil/shards/{worker}",
                "status": "done",
                "reason": (
                    "Duas consultas específicas de identidade para Vinci e "
                    "Jatobá, ambas descobertas e validadas fora da CVM."
                    if issue == 220
                    else None
                ),
                "owner": worker,
                "next_action": None,
            }
        )
    return rows


def build_artifacts() -> dict[str, bytes]:
    discovery = load_discovery_builder().build_artifacts()
    discovery_sources = records_from_bytes(discovery["source-inventory.jsonl"])
    discovery_candidates = records_from_bytes(discovery["candidates.jsonl"])
    discovery_evidence = records_from_bytes(discovery["evidence.jsonl"])
    discovery_identities = records_from_bytes(
        discovery["identity-resolution.jsonl"]
    )
    discovery_coverage = records_from_bytes(discovery["coverage-matrix.jsonl"])

    candidate_overlays = _validation_records("candidates.jsonl")
    validation_sources = _validation_records("source-inventory.jsonl")
    validation_evidence = _validation_records("evidence.jsonl")
    validation_identities = _validation_records("identity-resolution.jsonl")
    cvm_sources = _adjudication_records("source-inventory.jsonl")
    cvm_evidence = _adjudication_records("evidence.jsonl")
    cvm_queries = _adjudication_records("cvm-query-log.jsonl")
    identity_overlays = _adjudication_records("identity-resolution.jsonl")

    candidates = _apply_complete_candidate_overlays(
        discovery_candidates, candidate_overlays
    )
    sources = _merge_new(
        discovery_sources,
        validation_sources + cvm_sources,
        "source_id",
        "source-inventory.jsonl",
    )
    evidence = _correct_stale_access_date_activity(_merge_new(
        discovery_evidence,
        validation_evidence + cvm_evidence,
        "evidence_id",
        "evidence.jsonl",
    ))
    identities = _apply_resolution_overlays(
        discovery_identities, validation_identities, identity_overlays
    )
    queries = sorted(cvm_queries, key=lambda record: record["query_id"])
    _query_checks(queries, evidence)

    decision_counts = Counter(record["decision"] for record in candidates)
    if dict(decision_counts) != EXPECTED_DECISIONS:
        raise ValueError(
            "contagens de decisão inesperadas: "
            f"esperado={EXPECTED_DECISIONS}, atual={dict(decision_counts)}"
        )
    canonical_count = sum(
        record["decision"] != "duplicate"
        and record["canonical_candidate_id"] is None
        for record in candidates
    )
    if canonical_count != 40:
        raise ValueError(
            f"contagem canônica esperada 40, encontrada {canonical_count}"
        )
    for candidate_id in EXPECTED_QUERY_CANDIDATES:
        if _index(candidates, "candidate_id", "candidates.jsonl")[
            candidate_id
        ]["decision"] != "insufficient_evidence":
            raise ValueError("a CVM não pode alterar elegibilidade")

    coverage = build_coverage(
        discovery_coverage,
        sources,
        queries,
    )
    artifacts: dict[str, bytes] = {
        "source-inventory.jsonl": jsonl_bytes(sources),
        "candidates.jsonl": jsonl_bytes(candidates),
        "evidence.jsonl": jsonl_bytes(evidence),
        "identity-resolution.jsonl": jsonl_bytes(identities),
        "coverage-matrix.jsonl": jsonl_bytes(coverage),
        "cvm-query-log.jsonl": jsonl_bytes(queries),
        "review-sample.jsonl": b"",
    }
    core_hashes = {
        filename: sha256(artifacts[filename]) for filename in CORE_JSONL
    }
    artifacts["run-manifest.jsonl"] = jsonl_bytes(
        _run_manifest(core_hashes)
    )
    research_task_count = len(RESEARCH_TASKS)
    non_cvm_task_count = sum(
        channel == "non_cvm"
        for _, _, _, channel, _ in RESEARCH_TASKS
    )
    audit = {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 220,
        "cutoff_date": CUTOFF_DATE,
        "status": "complete",
        "canonical_candidate_count": canonical_count,
        "cvm_consulted_candidate_count": len(EXPECTED_QUERY_CANDIDATES),
        "cvm_query_rate": len(EXPECTED_QUERY_CANDIDATES) / canonical_count,
        "non_cvm_task_share": non_cvm_task_count / research_task_count,
        "decision_counts": dict(sorted(decision_counts.items())),
        "limitations": [
            (
                "A cobertura é auditada nas fontes e no recorte registrados; "
                "não representa prova de totalidade de fundos brasileiros."
            ),
            (
                "As consultas CVM de Vinci e Jatobá confirmam somente identidade "
                "jurídica e relação gestora-veículo."
            ),
            (
                "CVM não foi usada para comprovar tese, recorrência, atividade "
                "recente, acesso ao Brasil ou elegibilidade."
            ),
            (
                "Vinci Partners permanece identidade genérica insuficiente para "
                "selecionar uma única gestora ou estratégia publicável."
            ),
        ],
        "generated_on": CUTOFF_DATE,
    }
    artifacts["audit-report.json"] = json_bytes(audit)
    summary = {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 220,
        "cutoff_date": CUTOFF_DATE,
        "input_workers": [*VALIDATION_WORKERS, ADJUDICATION_WORKER],
        "candidate_overlay_count": len(candidate_overlays),
        "canonical_candidate_count": canonical_count,
        "decision_counts": dict(sorted(decision_counts.items())),
        "artifact_counts": {
            "sources": len(sources),
            "candidate_rows": len(candidates),
            "evidence": len(evidence),
            "identity_resolutions": len(identities),
            "coverage_cells": len(coverage),
            "cvm_queries": len(queries),
        },
        "cvm": {
            "task_count": 1,
            "consulted_candidate_ids": sorted(EXPECTED_QUERY_CANDIDATES),
            "consulted_candidate_count": len(EXPECTED_QUERY_CANDIDATES),
            "query_rate": len(EXPECTED_QUERY_CANDIDATES) / canonical_count,
            "eligibility_use": False,
        },
        "research_tasks": {
            "total": research_task_count,
            "non_cvm": non_cvm_task_count,
            "cvm": research_task_count - non_cvm_task_count,
            "non_cvm_share": non_cvm_task_count / research_task_count,
        },
        "core_artifact_hashes": core_hashes,
        "generated_on": CUTOFF_DATE,
    }
    artifacts["adjudication-summary.json"] = json_bytes(summary)
    return artifacts


def write_or_check(artifacts: dict[str, bytes], check: bool) -> int:
    mismatches: list[str] = []
    for relative in GENERATED:
        expected = artifacts[relative]
        path = BRAZIL / relative
        if check:
            if not path.is_file():
                mismatches.append(f"ausente: {relative}")
            elif path.read_bytes() != expected:
                mismatches.append(f"divergente: {relative}")
        else:
            path.write_bytes(expected)
    if check and mismatches:
        raise ValueError(
            "artefatos adjudicados divergentes: " + ", ".join(mismatches)
        )
    return len(artifacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Falha quando qualquer artefato difere da geração determinística.",
    )
    args = parser.parse_args()
    artifacts = build_artifacts()
    count = write_or_check(artifacts, args.check)
    action = "verificados" if args.check else "gerados"
    print(f"Artefatos adjudicados {action}: {count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
