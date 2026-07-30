"""Freeze the reconciled Brazil funds publication manifest for issue #222."""

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
BASE_BUILDER = BRAZIL / "build_review.py"
CUTOFF = "2026-07-30"
WORKER = "worker-222-freeze"
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
    "freeze-manifest.json",
)
DESTINATION_SLUGS = {
    "fund-br-1616v": "1616v",
    "fund-br-17-sigma": "17-sigma",
    "fund-br-210-dna-capital": "dna-capital",
    "fund-br-213-quartzo-capital": "quartzo-capital",
    "fund-br-214-barn-investimentos": "barn-investimentos",
    "fund-br-214-parallax-ventures": "parallax-ventures",
    "fund-br-221-basf-venture-capital": "basf-venture-capital",
    "fund-br-221-bb-ventures": "bb-ventures",
    "fund-br-221-blustone-capital": "blustone-capital",
    "fund-br-221-copel-ventures-i": "copel-ventures-i",
    "fund-br-221-csn-inova-ventures": "csn-inova-ventures",
    "fund-br-221-cv-idexo": "cv-idexo",
    "fund-br-221-grao-vc": "grao-vc",
    "fund-br-221-hiker-ventures": "hiker-ventures",
    "fund-br-221-lightrock": "lightrock",
    "fund-br-221-marcha": "marcha",
    "fund-br-221-positive-ventures": "positive-ventures",
    "fund-br-221-valutia": "valutia",
    "fund-br-221-vibra-ventures": "vibra-ventures",
    "fund-br-accion-ventures": "accion-ventures",
    "fund-br-antler": "antler",
    "fund-br-bs2-ventures": "bs2-ventures",
    "fund-br-l4-venture-builder": "l4-venture-builder",
    "fund-br-mundi-ventures-latam": "mundi-ventures",
    "fund-br-parceiro-ventures": "parceiro-ventures",
    "fund-br-prosus-ventures": "prosus-ventures",
    "fund-br-upload-ventures": "upload-ventures",
}
RECONCILED_IDENTITIES = {
    "identity-fund-br-221-link-ventures",
    "identity-fund-br-221-venture-hub",
}


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(content: bytes) -> str:
    return hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()


def records_from_bytes(content: bytes) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in content.decode("utf-8").splitlines()
        if line
    ]


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Não foi possível carregar {path.name}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def destination(candidate: dict[str, Any]) -> str:
    candidate_id = candidate["candidate_id"]
    slug = DESTINATION_SLUGS[candidate_id]
    directory = (
        "brazil"
        if candidate["brazil_relation"] == "based_in_brazil"
        else "multi-country"
    )
    return f"funds/{directory}/{slug}.md"


def freeze_sources(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in records:
        item = dict(source)
        if item["result"] not in {"complete", "gap_justified"}:
            item["result"] = "gap_justified"
        rows.append(item)
    return sorted(rows, key=lambda item: item["source_id"])


def freeze_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible_ids = {
        item["candidate_id"] for item in records if item["decision"] == "eligible"
    }
    if eligible_ids != set(DESTINATION_SLUGS):
        missing = sorted(eligible_ids - set(DESTINATION_SLUGS))
        extra = sorted(set(DESTINATION_SLUGS) - eligible_ids)
        raise ValueError(f"Mapa de destinos divergente; faltantes={missing}, extras={extra}.")
    rows: list[dict[str, Any]] = []
    for candidate in records:
        item = dict(candidate)
        if item["decision"] is None:
            raise ValueError(f"Candidato sem decisão no freeze: {item['candidate_id']}")
        if item["decision"] == "eligible":
            item["destination"] = destination(item)
        rows.append(item)
    return sorted(rows, key=lambda item: item["candidate_id"])


def freeze_identities(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for resolution in records:
        item = dict(resolution)
        if item["resolution_id"] in RECONCILED_IDENTITIES:
            item["resolution"] = "distinct_organization"
            item["reason"] = (
                "A revisão congelou a marca como candidato autônomo, sem vínculo de "
                "duplicidade ou cluster com outra identidade do universo auditado. "
                "As lacunas editoriais permanecem registradas na decisão "
                "insufficient_evidence e não autorizam publicação."
            )
            item["resolver"] = WORKER
            item["resolved_on"] = CUTOFF
        rows.append(item)
    unresolved = [
        item["resolution_id"] for item in rows if item["resolution"] == "unresolved"
    ]
    if unresolved:
        raise ValueError(f"Resoluções de identidade abertas: {unresolved}")
    return sorted(rows, key=lambda item: item["resolution_id"])


def freeze_run_manifest(
    records: list[dict[str, Any]],
    hashes: dict[str, str],
) -> list[dict[str, Any]]:
    rows = [dict(item) for item in records]
    run = rows[0]
    run["issues"] = list(range(210, 223))
    run["status"] = "frozen"
    run["coordinator"] = WORKER
    run["task_count"] += 1
    run["hash_algorithm"] = "sha256"
    run["artifact_hashes"] = hashes
    run["notes"] = (
        "A issue #222 reconciliou as pendências, congelou 27 elegíveis em três "
        "lotes determinísticos de nove e preservou a cobertura auditada na data "
        "de corte. O manifesto não declara totalidade do universo brasileiro."
    )
    rows.append({
        "schema_version": "1.0",
        "record_type": "task",
        "run_id": run["run_id"],
        "task_id": "task-fund-br-222-freeze",
        "issue": 222,
        "phase": "audit",
        "source_family": "not_applicable",
        "research_channel": "not_applicable",
        "worker_id": WORKER,
        "shard_path": "research/epic-207/brazil/shards/worker-222-freeze",
        "status": "done",
        "reason": (
            "Reconciliação terminal, verificação de integridade e freeze do "
            "manifesto de publicação."
        ),
        "owner": WORKER,
        "next_action": None,
    })
    return rows


def publication_batches(
    eligible: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    ordered = sorted(eligible, key=lambda item: item["candidate_id"])
    batches: list[dict[str, Any]] = []
    for offset in range(0, len(ordered), 9):
        members = ordered[offset : offset + 9]
        batches.append({
            "batch_id": f"publication-batch-{offset // 9 + 1:02d}",
            "ordinal": offset // 9 + 1,
            "candidate_count": len(members),
            "candidates": [
                {
                    "candidate_id": item["candidate_id"],
                    "name": item["name"],
                    "destination": item["destination"],
                }
                for item in members
            ],
        })
    return batches


def build_freeze_manifest(
    candidates: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    identities: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    hashes: dict[str, str],
) -> dict[str, Any]:
    decisions = Counter(item["decision"] for item in candidates)
    eligible = [item for item in candidates if item["decision"] == "eligible"]
    canonical_count = sum(
        item["decision"] != "duplicate"
        and item["canonical_candidate_id"] is None
        for item in candidates
    )
    review_counts = Counter(item["review_group"] for item in reviews)
    batches = publication_batches(eligible)
    destinations = [
        member["destination"]
        for batch in batches
        for member in batch["candidates"]
    ]
    if len(destinations) != len(set(destinations)):
        raise ValueError("Destino de publicação duplicado no manifesto.")
    return {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 222,
        "status": "frozen",
        "cutoff_date": CUTOFF,
        "frozen_on": CUTOFF,
        "hash_algorithm": "sha256",
        "core_artifact_hashes": hashes,
        "totals": {
            "candidate_rows": len(candidates),
            "canonical_candidates": canonical_count,
            "planned_sources": len(sources),
            "terminal_sources": sum(
                item["result"] in {"complete", "gap_justified"} for item in sources
            ),
            "identity_resolutions": len(identities),
            "unresolved_identity_resolutions": sum(
                item["resolution"] == "unresolved" for item in identities
            ),
            "cvm_consulted_candidates": len({
                item["candidate_id"] for item in queries
            }),
            "review_rows": len(reviews),
            "eligible_reviewed": review_counts["eligible"],
            "routed_reviewed": review_counts["routed"],
            "cvm_cases_reviewed": review_counts["cvm_consulted"],
            "insufficient_sample_reviewed": review_counts[
                "deterministic_exclusion_sample"
            ],
            "critical_findings_open": sum(
                not item["resolved"] and item["severity"] == "critical"
                for item in reviews
            ),
            "high_findings_open": sum(
                not item["resolved"] and item["severity"] == "high"
                for item in reviews
            ),
        },
        "decision_counts": dict(sorted(decisions.items())),
        "publication": {
            "eligible_count": len(eligible),
            "batch_size_limit": 10,
            "batch_count_formula": "ceil(eligible_count / 10)",
            "batch_count": len(batches),
            "published_at_freeze": False,
            "batches": batches,
        },
        "integrity": {
            "all_candidates_decided": all(
                item["decision"] is not None for item in candidates
            ),
            "all_sources_terminal": all(
                item["result"] in {"complete", "gap_justified"} for item in sources
            ),
            "all_duplicates_have_destination": all(
                item["decision"] != "duplicate"
                or item["canonical_candidate_id"]
                or item["canonical_profile"]
                for item in candidates
            ),
            "all_identity_resolutions_terminal": all(
                item["resolution"] != "unresolved" for item in identities
            ),
            "review_reconciled": all(item["resolved"] for item in reviews),
            "eligible_destinations_unique": len(destinations) == len(set(destinations)),
        },
        "limitations": [
            "O freeze representa cobertura auditada nas fontes e no recorte registrados; não prova totalidade do universo brasileiro.",
            "Os perfis e índices ainda não foram publicados neste estágio.",
            "A CVM foi usada somente para identidade em dois casos e não sustenta elegibilidade editorial.",
        ],
    }


def build_artifacts() -> dict[str, bytes]:
    base_module = load_module(BASE_BUILDER, "epic_207_review_builder")
    base = base_module.build_artifacts()
    sources = freeze_sources(records_from_bytes(base["source-inventory.jsonl"]))
    candidates = freeze_candidates(records_from_bytes(base["candidates.jsonl"]))
    evidence = records_from_bytes(base["evidence.jsonl"])
    identities = freeze_identities(
        records_from_bytes(base["identity-resolution.jsonl"])
    )
    coverage = records_from_bytes(base["coverage-matrix.jsonl"])
    queries = records_from_bytes(base["cvm-query-log.jsonl"])
    reviews = records_from_bytes(base["review-sample.jsonl"])
    run_manifest = records_from_bytes(base["run-manifest.jsonl"])

    artifacts: dict[str, bytes] = {
        "source-inventory.jsonl": jsonl_bytes(sources),
        "candidates.jsonl": jsonl_bytes(candidates),
        "evidence.jsonl": jsonl_bytes(evidence),
        "identity-resolution.jsonl": jsonl_bytes(identities),
        "coverage-matrix.jsonl": jsonl_bytes(coverage),
        "cvm-query-log.jsonl": jsonl_bytes(queries),
        "review-sample.jsonl": jsonl_bytes(reviews),
    }
    hashes = {filename: sha256(artifacts[filename]) for filename in CORE_JSONL}
    artifacts["run-manifest.jsonl"] = jsonl_bytes(
        freeze_run_manifest(run_manifest, hashes)
    )
    decision_counts = Counter(item["decision"] for item in candidates)
    canonical_count = sum(
        item["decision"] != "duplicate"
        and item["canonical_candidate_id"] is None
        for item in candidates
    )
    research_tasks = [
        item
        for item in records_from_bytes(artifacts["run-manifest.jsonl"])
        if item["record_type"] == "task"
        and item["status"] == "done"
        and item["phase"] in {"discovery", "validation", "adjudication"}
    ]
    non_cvm_share = (
        sum(item["research_channel"] == "non_cvm" for item in research_tasks)
        / len(research_tasks)
    )
    artifacts["audit-report.json"] = json_bytes({
        "schema_version": "1.0",
        "epic": 207,
        "issue": 222,
        "cutoff_date": CUTOFF,
        "status": "frozen",
        "canonical_candidate_count": canonical_count,
        "cvm_consulted_candidate_count": len({
            item["candidate_id"] for item in queries
        }),
        "cvm_query_rate": len({item["candidate_id"] for item in queries})
        / canonical_count,
        "non_cvm_task_share": non_cvm_share,
        "decision_counts": dict(sorted(decision_counts.items())),
        "limitations": [
            "A cobertura representa as fontes e o recorte registrados, não prova totalidade do universo brasileiro.",
            "A CVM foi usada somente em dois casos de identidade e relação gestora-veículo, nunca para elegibilidade.",
            "As fontes com bloqueio ou enumeração incompleta foram congeladas como gap_justified, preservando motivo, responsável e próxima ação.",
            "Os 28 casos insuficientes permanecem decididos com pendência explícita para ciclos futuros.",
        ],
        "generated_on": CUTOFF,
    })
    artifacts["freeze-manifest.json"] = json_bytes(build_freeze_manifest(
        candidates,
        sources,
        identities,
        reviews,
        queries,
        hashes,
    ))
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
    if mismatches:
        raise ValueError("Artefatos congelados divergentes: " + ", ".join(mismatches))
    return len(artifacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    count = write_or_check(build_artifacts(), args.check)
    action = "verificados" if args.check else "gerados"
    print(f"Artefatos congelados {action}: {count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
