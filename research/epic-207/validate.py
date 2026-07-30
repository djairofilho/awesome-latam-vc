"""Validate executable research contracts for the Brazil funds re-audit."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from datetime import date
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schemas"
JSONL_SCHEMAS = {
    "source-inventory.jsonl": "source-inventory.schema.json",
    "run-manifest.jsonl": "run-manifest-record.schema.json",
    "candidates.jsonl": "candidate.schema.json",
    "evidence.jsonl": "evidence.schema.json",
    "identity-resolution.jsonl": "identity-resolution.schema.json",
    "coverage-matrix.jsonl": "coverage-matrix.schema.json",
    "cvm-query-log.jsonl": "cvm-query.schema.json",
    "review-sample.jsonl": "review-sample.schema.json",
}
JSON_SCHEMAS = {"audit-report.json": "audit-report.schema.json"}
ID_FIELDS = {
    "source-inventory.jsonl": "source_id",
    "candidates.jsonl": "candidate_id",
    "evidence.jsonl": "evidence_id",
    "identity-resolution.jsonl": "resolution_id",
    "coverage-matrix.jsonl": "coverage_id",
    "cvm-query-log.jsonl": "query_id",
    "review-sample.jsonl": "review_id",
}
ELIGIBLE_CLAIMS = {
    "identity",
    "direct_startup_investment",
    "recurring_vc",
    "activity",
    "brazil_access",
}
CVM_ALLOWED_CLAIMS = {
    "legal_identity",
    "manager_vehicle_relation",
    "regulatory_divergence",
}
HASHED_ARTIFACTS = tuple(
    filename
    for filename in (*JSONL_SCHEMAS, *JSON_SCHEMAS)
    if filename not in {"run-manifest.jsonl", "audit-report.json"}
)
MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "Ãƒ",
    "Ã‚",
    "ï¿½",
    "Ã¢â‚¬",
    "Ã°Å¸",
    "\ufffd",
    "\x07",
)


def read_jsonl(path: Path, *, allow_empty: bool = False) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    if not path.is_file():
        return records, [f"{path.name}: arquivo obrigatório ausente"]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return records, [f"{path.name}: leitura UTF-8 falhou: {exc}"]
    for marker in MOJIBAKE_MARKERS:
        if marker in text:
            errors.append(f"{path.name}: possível mojibake: {marker!r}")
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            if not allow_empty:
                errors.append(f"{path.name}:{line_number}: linha JSONL vazia")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_number}: JSON inválido: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name}:{line_number}: registro deve ser objeto")
            continue
        records.append(value)
    if not records and not allow_empty:
        errors.append(f"{path.name}: arquivo não pode ficar vazio")
    return records, errors


def _schema_validator(filename: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_errors(
    filename: str,
    records: Iterable[dict[str, Any]],
    schema_name: str,
) -> list[str]:
    validator = _schema_validator(schema_name)
    errors: list[str] = []
    for line_number, record in enumerate(records, 1):
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path)
            suffix = f".{location}" if location else ""
            errors.append(f"{filename}:{line_number}{suffix}: {error.message}")
    return errors


def _unique(
    filename: str,
    records: Iterable[dict[str, Any]],
    field: str,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for record in records:
        value = record.get(field)
        if not isinstance(value, str):
            continue
        if value in result:
            errors.append(f"{filename}: {field} duplicado: {value}")
        else:
            result[value] = record
    return result, errors


def _safe_shard_path(value: Any, worker_id: Any) -> bool:
    if not isinstance(value, str) or not isinstance(worker_id, str):
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    expected = PurePosixPath("research", "epic-207", "brazil", "shards", worker_id)
    return path == expected


def _parse_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def _subtract_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_month = divmod(month_index, 12)
    month = zero_month + 1
    day = value.day
    while day > 28:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1
    return date(year, month, day)


def _validate_manifest(
    records: list[dict[str, Any]],
    bundle: Path,
) -> list[str]:
    errors: list[str] = []
    runs = [record for record in records if record.get("record_type") == "run"]
    tasks = [record for record in records if record.get("record_type") == "task"]
    if len(runs) != 1:
        return ["run-manifest.jsonl: deve conter exatamente um registro run"]
    run = runs[0]
    if records[0].get("record_type") != "run":
        errors.append("run-manifest.jsonl: o primeiro registro deve ser run")
    if run.get("task_count") != len(tasks):
        errors.append("run-manifest.jsonl: task_count não coincide com as tarefas")
    task_ids: set[str] = set()
    worker_paths: dict[str, str] = {}
    used_paths: dict[str, str] = {}
    completed_research = Counter()
    for task in tasks:
        task_id = task.get("task_id")
        if task_id in task_ids:
            errors.append(f"run-manifest.jsonl: task_id duplicado: {task_id}")
        task_ids.add(task_id)
        if task.get("run_id") != run.get("run_id"):
            errors.append(f"run-manifest.jsonl: run_id divergente em {task_id}")
        worker = task.get("worker_id")
        shard = task.get("shard_path")
        if not _safe_shard_path(shard, worker):
            errors.append(f"run-manifest.jsonl: shard_path inseguro em {task_id}")
        if worker in worker_paths and worker_paths[worker] != shard:
            errors.append(f"run-manifest.jsonl: worker possui mais de um shard: {worker}")
        worker_paths[worker] = shard
        if shard in used_paths and used_paths[shard] != worker:
            errors.append(f"run-manifest.jsonl: shard compartilhado por workers: {shard}")
        used_paths[shard] = worker
        if task.get("status") == "blocked" and not all(
            task.get(field) for field in ("reason", "owner", "next_action")
        ):
            errors.append(f"run-manifest.jsonl: tarefa bloqueada incompleta: {task_id}")
        if (
            task.get("status") == "done"
            and task.get("phase") in {"discovery", "validation", "adjudication"}
        ):
            completed_research[task.get("research_channel")] += 1
    if run.get("status") in {"completed", "frozen"} and any(
        task.get("status") not in {"done", "blocked"} for task in tasks
    ):
        errors.append("run-manifest.jsonl: run terminal possui tarefa não terminal")
    total_research = sum(completed_research.values())
    if total_research and completed_research["non_cvm"] / total_research < 0.90:
        errors.append("run-manifest.jsonl: non_cvm_task_share abaixo de 90%")
    hashes_declared = (
        run.get("hash_algorithm") is not None
        or run.get("artifact_hashes") is not None
    )
    if run.get("status") == "frozen" or hashes_declared:
        if run.get("hash_algorithm") != "sha256":
            errors.append("run-manifest.jsonl: freeze deve usar sha256")
        hashes = run.get("artifact_hashes")
        if not isinstance(hashes, dict) or set(hashes) != set(HASHED_ARTIFACTS):
            errors.append(
                "run-manifest.jsonl: hashes devem cobrir somente artefatos não circulares"
            )
        else:
            for filename in HASHED_ARTIFACTS:
                path = bundle / filename
                payload = path.read_bytes().replace(b"\r\n", b"\n")
                if hashes.get(filename) != sha256(payload).hexdigest():
                    errors.append(f"run-manifest.jsonl: hash divergente para {filename}")
    return errors


def _validate_relations(
    grouped: dict[str, list[dict[str, Any]]],
    audit: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    candidates, duplicate_errors = _unique(
        "candidates.jsonl", grouped["candidates.jsonl"], "candidate_id"
    )
    sources, source_errors = _unique(
        "source-inventory.jsonl", grouped["source-inventory.jsonl"], "source_id"
    )
    evidence, evidence_errors = _unique(
        "evidence.jsonl", grouped["evidence.jsonl"], "evidence_id"
    )
    resolutions, resolution_errors = _unique(
        "identity-resolution.jsonl",
        grouped["identity-resolution.jsonl"],
        "resolution_id",
    )
    reviews, review_errors = _unique(
        "review-sample.jsonl", grouped["review-sample.jsonl"], "review_id"
    )
    queries, query_errors = _unique(
        "cvm-query-log.jsonl", grouped["cvm-query-log.jsonl"], "query_id"
    )
    errors.extend(
        duplicate_errors
        + source_errors
        + evidence_errors
        + resolution_errors
        + review_errors
        + query_errors
    )
    _ = resolutions, reviews, queries

    evidence_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for item in evidence.values():
        candidate_id = item.get("candidate_id")
        if candidate_id not in candidates:
            errors.append(
                f"evidence.jsonl: evidência referencia candidato inexistente: {candidate_id}"
            )
        evidence_by_candidate.setdefault(str(candidate_id), []).append(item)
        query_id = item.get("cvm_query_id")
        if item.get("source_class") == "cvm" and query_id not in queries:
            errors.append(
                f"evidence.jsonl: consulta CVM órfã em {item.get('evidence_id')}: {query_id}"
            )

    for candidate_id, candidate in candidates.items():
        discovery_ids = candidate.get("discovery_source_ids", [])
        if not discovery_ids:
            errors.append(f"candidates.jsonl: candidato sem origem: {candidate_id}")
        for source_id in discovery_ids:
            source = sources.get(source_id)
            if source is None:
                errors.append(
                    f"candidates.jsonl: fonte órfã em {candidate_id}: {source_id}"
                )
            elif source.get("research_channel") != "non_cvm" or source.get("is_cvm"):
                errors.append(
                    f"candidates.jsonl: origem CVM proibida em {candidate_id}: {source_id}"
                )
        for evidence_id in candidate.get("official_evidence_ids", []):
            if evidence_id not in evidence:
                errors.append(
                    f"candidates.jsonl: evidência órfã em {candidate_id}: {evidence_id}"
                )
        canonical_id = candidate.get("canonical_candidate_id")
        if candidate.get("decision") == "duplicate":
            if not canonical_id and not candidate.get("canonical_profile"):
                errors.append(f"candidates.jsonl: duplicate sem destino: {candidate_id}")
            if canonical_id == candidate_id:
                errors.append(f"candidates.jsonl: duplicate aponta para si: {candidate_id}")
            if canonical_id and canonical_id not in candidates:
                errors.append(
                    f"candidates.jsonl: destino canônico inexistente: {canonical_id}"
                )
        if candidate.get("decision") == "insufficient_evidence" and not all(
            candidate.get(field) for field in ("owner", "next_action")
        ):
            errors.append(
                f"candidates.jsonl: pendência sem owner/next_action: {candidate_id}"
            )
        if candidate.get("decision") == "eligible":
            confirmed: set[str] = set()
            for item in evidence_by_candidate.get(candidate_id, []):
                if item.get("source_class") != "official":
                    continue
                confirmed.update(
                    claim.get("field")
                    for claim in item.get("claims", [])
                    if claim.get("finding") == "confirmed"
                    and claim.get("field") not in CVM_ALLOWED_CLAIMS
                )
            missing = sorted(ELIGIBLE_CLAIMS - confirmed)
            if missing:
                errors.append(
                    f"candidates.jsonl: eligible {candidate_id} sem claims oficiais: {missing}"
                )
            cutoff = _parse_date(candidate.get("cutoff_date"))
            activity = _parse_date(candidate.get("latest_official_activity_on"))
            if cutoff and activity and activity < _subtract_months(cutoff, 24):
                errors.append(
                    f"candidates.jsonl: atividade fora da janela em {candidate_id}"
                )
            activity_evidence_dates = {
                item.get("observed_on")
                for item in evidence_by_candidate.get(candidate_id, [])
                if item.get("source_class") == "official"
                and any(
                    claim.get("field") == "activity"
                    and claim.get("finding") == "confirmed"
                    for claim in item.get("claims", [])
                )
            }
            if candidate.get("latest_official_activity_on") not in activity_evidence_dates:
                errors.append(
                    f"candidates.jsonl: latest_official_activity_on de {candidate_id} "
                    "não coincide com evidência oficial de activity"
                )
    for start_id in candidates:
        seen: set[str] = set()
        current_id: str | None = start_id
        while current_id:
            if current_id in seen:
                errors.append(
                    f"candidates.jsonl: ciclo de identidade canônica iniciado em {start_id}"
                )
                break
            seen.add(current_id)
            current = candidates.get(current_id)
            if current is None:
                break
            current_id = current.get("canonical_candidate_id")

    for resolution in grouped["identity-resolution.jsonl"]:
        for subject_id in resolution.get("subject_ids", []):
            if subject_id not in candidates:
                errors.append(
                    f"identity-resolution.jsonl: subject órfão: {subject_id}"
                )
        canonical_id = resolution.get("canonical_candidate_id")
        if canonical_id and canonical_id not in candidates:
            errors.append(
                f"identity-resolution.jsonl: canonical órfão: {canonical_id}"
            )
        for evidence_id in resolution.get("evidence_ids", []):
            if evidence_id not in evidence:
                errors.append(
                    f"identity-resolution.jsonl: evidência órfã: {evidence_id}"
                )

    for review in grouped["review-sample.jsonl"]:
        if review.get("candidate_id") not in candidates:
            errors.append(
                f"review-sample.jsonl: candidato órfão: {review.get('candidate_id')}"
            )

    consulted: set[str] = set()
    for query in grouped["cvm-query-log.jsonl"]:
        candidate_id = query.get("candidate_id")
        if candidate_id not in candidates:
            errors.append(f"cvm-query-log.jsonl: candidato órfão: {candidate_id}")
            continue
        consulted.add(candidate_id)
        if any(
            claim not in CVM_ALLOWED_CLAIMS for claim in query.get("confirmed_claims", [])
        ):
            errors.append(
                f"cvm-query-log.jsonl: claim fora do escopo CVM: {query.get('query_id')}"
            )
        discovered_on = _parse_date(candidates[candidate_id].get("discovered_on"))
        accessed_on = _parse_date(query.get("accessed_on"))
        if discovered_on and accessed_on and accessed_on < discovered_on:
            errors.append(
                f"cvm-query-log.jsonl: consulta anterior à descoberta: {query.get('query_id')}"
            )
        initial_official = [
            _parse_date(item.get("accessed_on"))
            for item in evidence_by_candidate.get(candidate_id, [])
            if item.get("source_class") == "official"
        ]
        if accessed_on and not any(
            evidence_date is not None and evidence_date <= accessed_on
            for evidence_date in initial_official
        ):
            errors.append(
                f"cvm-query-log.jsonl: consulta sem validação oficial anterior: "
                f"{query.get('query_id')}"
            )
    canonical_count = sum(
        candidate.get("decision") != "duplicate"
        and candidate.get("canonical_candidate_id") is None
        for candidate in candidates.values()
    )
    if len(consulted) > math.floor(canonical_count * 0.10):
        errors.append(
            "cvm-query-log.jsonl: candidatos consultados excedem 10% após deduplicação"
        )

    coverage_keys: set[tuple[str, str]] = set()
    for row in grouped["coverage-matrix.jsonl"]:
        key = (row.get("source_family"), row.get("geography_scope"))
        if key in coverage_keys:
            errors.append(f"coverage-matrix.jsonl: célula duplicada: {key}")
        coverage_keys.add(key)
        for source_id in row.get("source_ids", []):
            if source_id not in sources:
                errors.append(
                    f"coverage-matrix.jsonl: fonte órfã: {source_id}"
                )
        for candidate_id in row.get("candidate_ids", []):
            if candidate_id not in candidates:
                errors.append(
                    f"coverage-matrix.jsonl: candidato órfão: {candidate_id}"
                )
        if row.get("status") == "complete" and row.get("completed_sources") != row.get(
            "planned_sources"
        ):
            errors.append(
                f"coverage-matrix.jsonl: célula completa diverge do plano: {key}"
            )

    if audit.get("canonical_candidate_count") != canonical_count:
        errors.append("audit-report.json: canonical_candidate_count divergente")
    if audit.get("cvm_consulted_candidate_count") != len(consulted):
        errors.append("audit-report.json: cvm_consulted_candidate_count divergente")
    actual_rate = len(consulted) / canonical_count if canonical_count else 0
    if audit.get("cvm_query_rate") != actual_rate:
        errors.append("audit-report.json: cvm_query_rate divergente")
    research_tasks = [
        task
        for task in grouped["run-manifest.jsonl"]
        if task.get("record_type") == "task"
        and task.get("status") == "done"
        and task.get("phase") in {"discovery", "validation", "adjudication"}
    ]
    actual_non_cvm_share = (
        sum(task.get("research_channel") == "non_cvm" for task in research_tasks)
        / len(research_tasks)
        if research_tasks
        else 1
    )
    if audit.get("non_cvm_task_share") != actual_non_cvm_share:
        errors.append("audit-report.json: non_cvm_task_share divergente")
    return errors


def validate_bundle(bundle: Path) -> list[str]:
    errors: list[str] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for filename, schema_name in JSONL_SCHEMAS.items():
        records, read_errors = read_jsonl(
            bundle / filename,
            allow_empty=filename in {"cvm-query-log.jsonl", "identity-resolution.jsonl", "review-sample.jsonl"},
        )
        grouped[filename] = records
        errors.extend(read_errors)
        errors.extend(_schema_errors(filename, records, schema_name))
        field = ID_FIELDS.get(filename)
        if field:
            _, unique_errors = _unique(filename, records, field)
            errors.extend(unique_errors)
    audit_path = bundle / "audit-report.json"
    if not audit_path.is_file():
        errors.append("audit-report.json: arquivo obrigatório ausente")
        audit: dict[str, Any] = {}
    else:
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"audit-report.json: JSON inválido: {exc}")
            audit = {}
        if isinstance(audit, dict):
            errors.extend(
                _schema_errors(
                    "audit-report.json",
                    [audit],
                    JSON_SCHEMAS["audit-report.json"],
                )
            )
        else:
            errors.append("audit-report.json: deve ser objeto")
            audit = {}
    errors.extend(_validate_manifest(grouped["run-manifest.jsonl"], bundle))
    errors.extend(_validate_relations(grouped, audit))
    return sorted(set(errors))


def validate_contract() -> list[str]:
    errors: list[str] = []
    for name in ("templates", "examples"):
        errors.extend(f"{name}/{error}" for error in validate_bundle(ROOT / name))
    return sorted(set(errors))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundles", nargs="*", type=Path)
    args = parser.parse_args(argv)
    bundles = args.bundles or [ROOT / "templates", ROOT / "examples"]
    errors: list[str] = []
    for bundle in bundles:
        errors.extend(f"{bundle}: {error}" for error in validate_bundle(bundle))
    if errors:
        print("Brazil funds re-audit validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Brazil funds re-audit validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
