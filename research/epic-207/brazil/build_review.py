"""Build the independently reviewed Brazil funds bundle for issue #221."""

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
BASE_BUILDER = BRAZIL / "build_adjudicated.py"
REVIEW_RECORDS = BRAZIL / "shards" / "worker-221-review" / "records.py"
CUTOFF = "2026-07-30"
WORKER = "worker-221-review"
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
    "review-report.json",
)
CORRECTED_ACTIVITY_EVIDENCE = {
    "ev-fund-br-214-parallax-official",
    "ev-fund-br-l4-official",
    "ev-fund-br-214-ipe-investe-official",
    "ev-fund-br-214-jatoba-official",
}
SHA_SAMPLE = (
    "fund-br-nido-vc",
    "fund-br-213-30n-ventures",
    "fund-br-lightspeed",
    "fund-br-sororite-ventures",
    "fund-br-214-lh-invest",
)
INITIAL_BLIND = (
    "fund-br-l4-venture-builder",
    "fund-br-213-quartzo-capital",
    "fund-br-221-hiker-ventures",
    "fund-br-221-grao-vc",
    "fund-br-221-valutia",
    "fund-br-221-blustone-capital",
    "fund-br-221-honey-island-by-4um",
    "fund-br-221-broom-ventures",
    "fund-br-221-venture-hub",
    "fund-br-221-fundepar",
)
FINAL_PASS_FINDINGS = (
    "fund-br-221-positive-ventures",
    "fund-br-221-lightrock",
    "fund-br-221-marcha",
    "fund-br-221-cv-idexo",
    "fund-br-221-link-ventures",
    "fund-br-221-startvc",
    "fund-br-221-3c-invest",
    "fund-br-221-uniangels",
    "fund-br-221-insper-angels",
    "fund-br-221-csn-inova-ventures",
    "fund-br-221-vibra-ventures",
    "fund-br-221-copel-ventures-i",
    "fund-br-221-bb-ventures",
    "fund-br-221-basf-venture-capital",
    "fund-br-221-carbyne-investimentos",
    "fund-br-221-ita-angels",
    "fund-br-221-foks",
)


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256(content: bytes) -> str:
    return hashlib.sha256(content.replace(b"\r\n", b"\n")).hexdigest()


def records_from_bytes(content: bytes) -> list[dict[str, Any]]:
    return [json.loads(line) for line in content.decode("utf-8").splitlines() if line]


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Não foi possível carregar {path.name}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def index(records: Iterable[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[field]
        if record_id in result:
            raise ValueError(f"ID duplicado em {field}: {record_id}")
        result[record_id] = record
    return result


def merge_new(
    base: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    field: str,
) -> list[dict[str, Any]]:
    result = index(base, field)
    for record in additions:
        record_id = record[field]
        if record_id in result:
            raise ValueError(f"Adição colide com registro existente: {record_id}")
        result[record_id] = record
    return [result[key] for key in sorted(result)]


def correct_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = index(records, "candidate_id")
    for candidate_id in (
        "fund-br-210-dna-capital",
        "fund-br-214-jatoba-impacto-amazonia",
        "fund-br-mundi-ventures-latam",
    ):
        rows[candidate_id]["aliases"] = []
    vinci = rows["fund-br-213-vinci-partners"]
    vinci["aliases"] = []
    vinci["manager_id"] = None
    vinci["reason"] = (
        "A plataforma oficial confirma a marca brasileira, mas a CVM distingue duas "
        "gestoras e o candidato genérico não identifica uma única organização, "
        "estratégia ou veículo startup/VC publicável."
    )
    return [rows[key] for key in sorted(rows)]


def correct_evidence(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = index(records, "evidence_id")
    for evidence_id in CORRECTED_ACTIVITY_EVIDENCE:
        item = rows[evidence_id]
        item["observed_on"] = None
        for claim in item["claims"]:
            if claim["field"] == "activity":
                claim["finding"] = "inconclusive"
    agroven = rows["ev-fund-br-214-agroven-official"]
    for claim in agroven["claims"]:
        if claim["field"] == "direct_startup_investment":
            claim["finding"] = "inconclusive"
    agroven["summary"] = (
        "O clube informa que os membros realizam os investimentos, mantém seleção "
        "aberta por formulário e divulga duas teses e várias investidas AgFoodtech."
    )
    return [rows[key] for key in sorted(rows)]


def correct_identities(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = index(records, "resolution_id")
    vinci = rows["identity-fund-br-vinci-prior-managers"]
    vinci["manager_id"] = None
    vinci["reason"] = (
        "A consulta direcionada à CVM confirmou que Vinci Capital Gestora e Vinci "
        "Gestora são organizações distintas. Elas não são aliases entre si e o "
        "candidato genérico Vinci Partners não recebe um manager_id único."
    )
    return [rows[key] for key in sorted(rows)]


def build_coverage(
    base: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = {(item["source_family"], item["geography_scope"]): item for item in base}
    new_sources = [item for item in sources if item["issue"] == 221]
    candidate_by_source = {
        source_id: item["candidate_id"]
        for item in candidates
        for source_id in item["discovery_source_ids"]
    }
    additions: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for source in new_sources:
        geography = (
            "foreign_access_brazil"
            if source["source_family"] == "foreign_access"
            else "brazil"
        )
        additions.setdefault((source["source_family"], geography), []).append(source)
    for key, added_sources in additions.items():
        if key not in rows:
            raise ValueError(f"Célula de cobertura ausente para {key}.")
        row = rows[key]
        added_ids = sorted(item["source_id"] for item in added_sources)
        row["source_ids"] = sorted(set(row["source_ids"]) | set(added_ids))
        row["planned_sources"] += len(added_ids)
        row["completed_sources"] += len(added_ids)
        row["candidate_ids"] = sorted(
            set(row["candidate_ids"])
            | {
                candidate_by_source[source_id]
                for source_id in added_ids
                if source_id in candidate_by_source
            }
        )
    return sorted(rows.values(), key=lambda item: item["coverage_id"])


def review_row(
    candidate: dict[str, Any],
    group: str,
    suffix: str,
    algorithm: str,
    original: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "review_id": f"review-fund-br-221-{suffix}",
        "candidate_id": candidate["candidate_id"],
        "review_group": group,
        "selection_algorithm": algorithm,
        "reviewer": WORKER,
        "reviewed_on": CUTOFF,
        "original_decision": original,
        "final_decision": candidate["decision"],
        "resolved": True,
        "severity": "none" if original == candidate["decision"] else "medium",
        "notes": notes,
    }


def build_reviews(
    original: list[dict[str, Any]],
    final: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    original_index = index(original, "candidate_id")
    final_index = index(final, "candidate_id")
    rows: list[dict[str, Any]] = []
    for item in final:
        if item["decision"] == "eligible":
            original_decision = original_index.get(item["candidate_id"], {}).get(
                "decision", "not_in_issue_220_bundle"
            )
            rows.append(review_row(
                item,
                "eligible",
                f"eligible-{item['candidate_id'].removeprefix('fund-br-')}",
                "100% dos candidatos elegíveis após a reconciliação",
                original_decision,
                "Os cinco claims oficiais e a atividade dentro da janela foram conferidos.",
            ))
    for item in final:
        if item["decision"].startswith("routed_"):
            original_decision = original_index.get(item["candidate_id"], {}).get(
                "decision", "not_in_issue_220_bundle"
            )
            rows.append(review_row(
                item,
                "routed",
                f"routed-{item['candidate_id'].removeprefix('fund-br-')}",
                "100% dos candidatos roteados após a reconciliação",
                original_decision,
                "A natureza da organização e o destino editorial foram confirmados.",
            ))
    for candidate_id in ("fund-br-213-vinci-partners", "fund-br-214-jatoba-impacto-amazonia"):
        item = final_index[candidate_id]
        rows.append(review_row(
            item,
            "cvm_consulted",
            f"cvm-{candidate_id.removeprefix('fund-br-')}",
            "100% dos candidatos consultados na CVM",
            original_index[candidate_id]["decision"],
            "A consulta confirmou somente identidade ou relação gestora-veículo e não alterou a decisão.",
        ))
    for candidate_id in SHA_SAMPLE:
        item = final_index[candidate_id]
        rows.append(review_row(
            item,
            "deterministic_exclusion_sample",
            f"sha-{candidate_id.removeprefix('fund-br-')}",
            "cinco menores SHA-256 de candidate_id entre os 24 insufficient_evidence originais",
            original_index[candidate_id]["decision"],
            "A insuficiência de evidência foi confirmada.",
        ))
    for candidate_id in (*INITIAL_BLIND, *FINAL_PASS_FINDINGS):
        item = final_index[candidate_id]
        original_decision = original_index.get(candidate_id, {}).get(
            "decision", "not_in_issue_220_bundle"
        )
        rows.append(review_row(
            item,
            "blind_search",
            f"blind-{candidate_id.removeprefix('fund-br-')}",
            "achado de busca cega ou passagem final independente",
            original_decision,
            "A identidade, a evidência e a decisão foram reconciliadas no bundle final.",
        ))
    return sorted(rows, key=lambda item: item["review_id"])


def run_manifest(
    base: list[dict[str, Any]],
    hashes: dict[str, str],
) -> list[dict[str, Any]]:
    rows = [dict(item) for item in base]
    run = rows[0]
    run["issues"] = list(range(210, 222))
    run["coordinator"] = WORKER
    run["task_count"] += 1
    run["artifact_hashes"] = hashes
    run["notes"] = (
        "A issue #221 revisou 100% dos elegíveis e roteados, os dois casos CVM, "
        "uma amostra SHA-256 de cinco insuficientes e achados de buscas cegas. "
        "Nenhuma descoberta teve CVM ou baseline como origem."
    )
    rows.append({
        "schema_version": "1.0",
        "record_type": "task",
        "run_id": run["run_id"],
        "task_id": "task-fund-br-221-review-final",
        "issue": 221,
        "phase": "review",
        "source_family": "not_applicable",
        "research_channel": "not_applicable",
        "worker_id": WORKER,
        "shard_path": "research/epic-207/brazil/shards/worker-221-review",
        "status": "done",
        "reason": "Revisão independente, busca cega, reconciliação e auditoria final.",
        "owner": WORKER,
        "next_action": None,
    })
    return rows


def review_report(
    original_sources: list[dict[str, Any]],
    original_candidates: list[dict[str, Any]],
    final_candidates: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    source_family = {
        item["source_id"]: item["source_family"]
        for item in original_sources
        if item["issue"] <= 215
    }
    original_family_counts = {
        item["candidate_id"]: len({
            source_family[source_id]
            for source_id in item["discovery_source_ids"]
            if source_id in source_family
        })
        for item in original_candidates
    }
    one_family = sum(count == 1 for count in original_family_counts.values())
    multi_family = sum(count >= 2 for count in original_family_counts.values())
    if (one_family, multi_family) != (44, 7):
        raise ValueError(
            f"Métrica de sobreposição inesperada: {(one_family, multi_family)}"
        )
    single_source = sorted(
        item["candidate_id"]
        for item in original_candidates
        if len(item["discovery_source_ids"]) == 1
    )
    if len(single_source) != 17:
        raise ValueError(f"Esperados 17 casos de fonte única, encontrados {len(single_source)}.")
    final_counts = Counter(item["decision"] for item in final_candidates)
    return {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 221,
        "cutoff_date": CUTOFF,
        "status": "complete",
        "original_bundle": {
            "candidate_rows": 51,
            "canonical_candidates": 40,
            "decision_counts": dict(sorted(Counter(item["decision"] for item in original_candidates).items())),
        },
        "final_bundle": {
            "candidate_rows": len(final_candidates),
            "canonical_candidates": sum(
                item["decision"] != "duplicate"
                and item["canonical_candidate_id"] is None
                for item in final_candidates
            ),
            "decision_counts": dict(sorted(final_counts.items())),
        },
        "review_coverage": {
            "original_eligible_confirmed": 14,
            "final_eligible_reviewed": final_counts["eligible"],
            "final_routed_reviewed": sum(
                decision.startswith("routed_") and count
                for decision, count in final_counts.items()
            ),
            "cvm_cases_reviewed": 2,
            "sha_insufficient_sample_reviewed": len(SHA_SAMPLE),
            "review_rows": len(reviews),
        },
        "source_overlap": {
            "population": 51,
            "one_discovery_family": one_family,
            "two_or_more_discovery_families": multi_family,
        },
        "single_source_reviews": {
            "count": len(single_source),
            "candidate_ids": single_source,
            "review_result": "Os 17 casos foram relidos; a condição de fonte única permanece explicitada como limitação, sem uso indevido de review_group.",
        },
        "cumulative_discovery_curve": [
            {"pass": 1, "candidates": 7, "eligible": 1},
            {"pass": 2, "candidates": 19, "eligible": 5},
            {"pass": 3, "candidates": 25, "eligible": 8},
            {"pass": 4, "candidates": 40, "eligible": 9},
            {"pass": 5, "candidates": 48, "eligible": 11},
            {"pass": 6, "candidates": 51, "eligible": 14},
        ],
        "confirmed_routes": {
            "fund-br-214-agroven": "epic-63-angel-networks",
            "fund-br-214-ipe-investe": "epic-62-accelerators",
        },
        "cvm_review": {
            "candidate_ids": [
                "fund-br-213-vinci-partners",
                "fund-br-214-jatoba-impacto-amazonia",
            ],
            "decision_changes": 0,
            "eligibility_use": False,
        },
        "sha_sample": {
            "algorithm": "cinco menores SHA-256 de candidate_id entre os 24 insufficient_evidence originais",
            "candidate_ids": list(SHA_SAMPLE),
            "confirmed": len(SHA_SAMPLE),
        },
        "blind_findings": {
            "initial": list(INITIAL_BLIND),
            "final_pass": list(FINAL_PASS_FINDINGS),
        },
        "saturation_passes": [
            {
                "name": "spin-offs e licenciamento acadêmico",
                "source_ids": [
                    "src-fund-br-221-saturation-ctit-spin-offs",
                    "src-fund-br-221-saturation-unicamp-kasco",
                ],
                "documents_reviewed": 2,
                "candidate_yield": 0,
                "eligible_yield": 0,
            },
            {
                "name": "prêmios de inovação e programas de fornecedores",
                "source_ids": [
                    "src-fund-br-221-saturation-petrobras-supplier-award",
                    "src-fund-br-221-saturation-fieb-veracel-suppliers",
                ],
                "documents_reviewed": 2,
                "candidate_yield": 0,
                "eligible_yield": 0,
            },
            {
                "name": "CVCs, redes e programas em fontes corporativas e universitárias",
                "source_ids": [
                    "src-fund-br-221-basf-vc-brazil",
                    "src-fund-br-221-carbyne-fucape",
                    "src-fund-br-221-ita-angels-insper",
                    "src-fund-br-221-foks-insper-demoday",
                ],
                "documents_reviewed": 4,
                "candidate_yield": 4,
                "eligible_yield": 1,
            },
        ],
        "corrections": {
            "vinci_generic_manager_removed": True,
            "vehicle_names_removed_from_aliases": [
                "fund-br-210-dna-capital",
                "fund-br-214-jatoba-impacto-amazonia",
                "fund-br-mundi-ventures-latam",
            ],
            "undated_activity_downgraded": sorted(CORRECTED_ACTIVITY_EVIDENCE),
            "agroven_direct_claim_aligned_to_member_investment": True,
        },
        "generated_on": CUTOFF,
    }


def build_artifacts() -> dict[str, bytes]:
    base_module = load_module(BASE_BUILDER, "epic_207_adjudicated_builder")
    additions = load_module(REVIEW_RECORDS, "epic_207_review_records")
    base = base_module.build_artifacts()
    original_sources = records_from_bytes(base["source-inventory.jsonl"])
    original_candidates = records_from_bytes(base["candidates.jsonl"])
    original_evidence = records_from_bytes(base["evidence.jsonl"])
    original_identities = records_from_bytes(base["identity-resolution.jsonl"])
    original_coverage = records_from_bytes(base["coverage-matrix.jsonl"])
    queries = records_from_bytes(base["cvm-query-log.jsonl"])
    base_manifest = records_from_bytes(base["run-manifest.jsonl"])

    sources = merge_new(original_sources, additions.source_records(), "source_id")
    candidates = correct_candidates(
        merge_new(original_candidates, additions.candidate_records(), "candidate_id")
    )
    evidence = correct_evidence(
        merge_new(original_evidence, additions.evidence_records(), "evidence_id")
    )
    identities = correct_identities(
        merge_new(
            original_identities,
            additions.identity_records(),
            "resolution_id",
        )
    )
    coverage = build_coverage(original_coverage, sources, candidates)
    reviews = build_reviews(original_candidates, candidates)
    report = review_report(
        original_sources,
        original_candidates,
        candidates,
        reviews,
    )
    canonical_count = report["final_bundle"]["canonical_candidates"]
    decision_counts = report["final_bundle"]["decision_counts"]
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
    artifacts["run-manifest.jsonl"] = jsonl_bytes(run_manifest(base_manifest, hashes))
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
        "issue": 221,
        "cutoff_date": CUTOFF,
        "status": "complete",
        "canonical_candidate_count": canonical_count,
        "cvm_consulted_candidate_count": len(queries),
        "cvm_query_rate": len(queries) / canonical_count,
        "non_cvm_task_share": non_cvm_share,
        "decision_counts": decision_counts,
        "limitations": [
            "A cobertura representa as fontes e o recorte registrados, não prova totalidade do universo brasileiro.",
            "A CVM foi usada somente nos dois casos herdados de identidade e relação gestora-veículo.",
            "Os 17 candidatos originais com uma única fonte de descoberta foram relidos e permanecem explicitados no relatório auxiliar.",
            "Broom Ventures, Venture Hub e Link Ventures permanecem insuficientes até que novas fontes oficiais resolvam as lacunas registradas.",
        ],
        "generated_on": CUTOFF,
    })
    artifacts["review-report.json"] = json_bytes(report)
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
        raise ValueError("Artefatos de revisão divergentes: " + ", ".join(mismatches))
    return len(artifacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    count = write_or_check(build_artifacts(), args.check)
    print(f"Artefatos de revisão {'verificados' if args.check else 'gerados'}: {count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
