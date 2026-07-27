#!/usr/bin/env python3
"""Build the deterministic independent-review artifacts for issue #77."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CONSOLIDATION = ROOT / "research" / "epic-62" / "consolidation"
REVIEW = Path(__file__).resolve().parent


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def normalized_sha256(path: Path) -> str:
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def confirmed_claims(evidence_rows: list[dict]) -> set[str]:
    return {
        claim["field"]
        for evidence in evidence_rows
        if evidence["source_type"] == "official"
        for claim in evidence["claims"]
        if claim["finding"] == "confirmed"
    }


def main() -> None:
    manifest_path = REVIEW / "review-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    category = json.loads(
        (CONSOLIDATION / "category-resolutions.json").read_text(encoding="utf-8")
    )

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    evidence_by_candidate: dict[str, list[dict]] = {}
    for row in evidence:
        evidence_by_candidate.setdefault(row["candidate_id"], []).append(row)

    review_evidence = [
        {
            "schema_version": "1.0",
            "evidence_id": "ev-accel-review-founder-institute-vehicle",
            "candidate_id": "accel-foreign-founder-institute-latam",
            "entity_id": "fi.co#founder-capital",
            "url": "https://fi.co/core/14694",
            "title": "Founder Institute Core Program",
            "publisher": "Founder Institute",
            "source_type": "official",
            "published_on": None,
            "accessed_on": "2026-07-27",
            "claims": [
                {"field": "investment_vehicle", "finding": "confirmed"},
                {"field": "program_identity", "finding": "confirmed"},
            ],
            "locator": "Seções Founder Capital e A Network Invested in Your Success.",
            "summary": "A página separa o programa Core do fundo global Founder Capital, que realiza os primeiros cheques em participantes promissores.",
        },
        {
            "schema_version": "1.0",
            "evidence_id": "ev-accel-review-inovativa-recurrence",
            "candidate_id": "accel-inovativa-brasil",
            "entity_id": "inovativa.online#inovativa-brasil",
            "url": "https://www.gov.br/mdic/pt-br/acesso-a-informacao/perguntas-frequentes-faq/secretaria-de-desenvolvimento-industrial-inovacao-comercio-e-servicos/quem-pode-se-inscrever-e",
            "title": "Quem pode se inscrever nos programas InovAtiva",
            "publisher": "Ministério do Desenvolvimento, Indústria, Comércio e Serviços",
            "source_type": "official",
            "published_on": "2024-12-17",
            "accessed_on": "2026-07-27",
            "claims": [
                {"field": "structured_program", "finding": "confirmed"},
                {"field": "activity", "finding": "confirmed"},
                {"field": "external_access", "finding": "confirmed"},
                {"field": "latam_access", "finding": "confirmed"},
                {"field": "application_route", "finding": "confirmed"},
            ],
            "locator": "Resposta sobre ciclos, formulário e startups aceitas.",
            "summary": "O MDIC documenta ciclos geralmente em fevereiro e julho e inscrições para projetos e startups de todo o Brasil; a fonte permanece válida dentro da janela de 24 meses.",
        },
        {
            "schema_version": "1.0",
            "evidence_id": "ev-accel-review-ventiur-calendar",
            "candidate_id": "accel-ventiur-acelera-impacto",
            "entity_id": "ventiur.net#acelera-impacto",
            "url": "https://conteudo.ventiur.net/acelera-impacto",
            "title": "Acelera Impacto",
            "publisher": "Ventiur",
            "source_type": "official",
            "published_on": None,
            "accessed_on": "2026-07-27",
            "claims": [
                {"field": "operator_identity", "finding": "confirmed"},
                {"field": "program_identity", "finding": "confirmed"},
                {"field": "structured_program", "finding": "confirmed"},
                {"field": "activity", "finding": "confirmed"},
                {"field": "external_access", "finding": "confirmed"},
                {"field": "latam_access", "finding": "confirmed"},
                {"field": "application_route", "finding": "confirmed"},
                {"field": "duration", "finding": "confirmed"},
                {"field": "investment_vehicle", "finding": "confirmed"},
            ],
            "locator": "Seções O que é, Etapas do Programa e Próximas datas.",
            "summary": "A fonte oficial publica seleção externa, nove meses de aceleração e cronograma de março a outubro de 2025, dentro da janela de atividade do contrato.",
        },
    ]
    for row in review_evidence:
        evidence_by_candidate.setdefault(row["candidate_id"], []).append(row)

    required_ids = set()
    for values in manifest["mandatory_groups"].values():
        required_ids.update(values)
    required_ids.update(
        item["candidate_id"] for item in manifest["excluded_sample"]["selected"]
    )

    cross_by_candidate: dict[str, list[dict]] = {}
    for row in category["cross_category_resolutions"]:
        cross_by_candidate.setdefault(row["candidate_id"], []).append(row)
    vehicle_by_candidate: dict[str, list[dict]] = {}
    for row in category["vehicle_resolutions"]:
        vehicle_by_candidate.setdefault(row["candidate_id"], []).append(row)

    extra_relationships = {
        "accel-foreign-founder-institute-latam": [
            {
                "catalog": "funds",
                "destination": "funds/:fi.co#founder-capital",
                "status": "fila-canônica",
                "relationship": "programa-e-veículo-distintos",
            }
        ],
        "accel-mxcac-honduras-digital": [
            {
                "catalog": "epic-63",
                "destination": "research/epic-63/mexico-cac/candidates.jsonl#ang-hondurasdigitalchallenge-com",
                "status": "materializado",
                "relationship": "encaminhamento-de-fronteira-divergente",
            }
        ],
        "accel-ventiur-acelera-impacto": [
            {
                "catalog": "epic-64",
                "destination": "research/epic-64/brazil/candidates.jsonl#plat-ventiur",
                "status": "materializado",
                "relationship": "operadora-e-programa-distintos",
            }
        ],
    }

    divergences = [
        {
            "schema_version": "1.0",
            "divergence_id": "div-issue77-founder-institute-vehicle",
            "candidate_id": "accel-foreign-founder-institute-latam",
            "severity": "medium",
            "finding": "A consolidação manteve o programa elegível, mas não registrou o fundo Founder Capital como veículo separado.",
            "resolution": "Manter a elegibilidade do programa e criar encaminhamento de backlog funds/:fi.co#founder-capital sem contar o aporte duas vezes.",
            "resolved_decision": "elegível",
            "evidence_ids": ["ev-accel-review-founder-institute-vehicle"],
            "status": "resolved",
        },
        {
            "schema_version": "1.0",
            "divergence_id": "div-issue77-honduras-digital-boundary",
            "candidate_id": "accel-mxcac-honduras-digital",
            "severity": "medium",
            "finding": "A epic #63 encaminha o Startup Challenge para aceleradoras, enquanto a consolidação da epic #62 o exclui.",
            "resolution": "Manter excluído na epic #62. A fonte descreve desafio por edição, e o contrato #68 exclui desafio pontual; o encaminhamento da epic #63 é descoberta de fronteira, não decisão de elegibilidade.",
            "resolved_decision": "excluído",
            "evidence_ids": ["ev-accel-mxcac-honduras-digital"],
            "status": "resolved",
        },
        {
            "schema_version": "1.0",
            "divergence_id": "div-issue77-ventiur-activity",
            "candidate_id": "accel-ventiur-acelera-impacto",
            "severity": "high",
            "finding": "A consolidação afirmou que a página não publicava data, mas a fonte oficial contém cronograma explícito de março a outubro de 2025.",
            "resolution": "Reabrir evidência-insuficiente e decidir elegível; programa, seleção externa, acesso brasileiro e atividade dentro de 24 meses estão confirmados.",
            "resolved_decision": "elegível",
            "evidence_ids": ["ev-accel-review-ventiur-calendar"],
            "status": "resolved",
        },
    ]
    divergence_by_candidate: dict[str, list[str]] = {}
    for row in divergences:
        divergence_by_candidate.setdefault(row["candidate_id"], []).append(
            row["divergence_id"]
        )

    results = []
    for candidate_id in sorted(required_ids):
        candidate = candidate_by_id[candidate_id]
        candidate_evidence = evidence_by_candidate.get(candidate_id, [])
        official = [
            row for row in candidate_evidence if row["source_type"] == "official"
        ]
        claims = confirmed_claims(candidate_evidence)
        original = candidate["decision"]
        resolved = (
            "elegível"
            if candidate_id == "accel-ventiur-acelera-impacto"
            else original
        )
        groups = sorted(
            group
            for group, values in manifest["mandatory_groups"].items()
            if candidate_id in values
        )
        if any(
            item["candidate_id"] == candidate_id
            for item in manifest["excluded_sample"]["selected"]
        ):
            groups.append("excluded_sample")

        if resolved == "elegível":
            category_check = (
                "confirmed" if "structured_program" in claims else "insufficient"
            )
            activity_check = "confirmed" if "activity" in claims else "insufficient"
            access_check = (
                "confirmed"
                if {"external_access", "latam_access"}.issubset(claims)
                else "insufficient"
            )
        else:
            category_check = "confirmed" if official else "insufficient"
            activity_check = (
                "confirmed"
                if candidate["activity_status"] == "active"
                else "not_required"
            )
            access_check = (
                "confirmed"
                if candidate["latam_access"] == "confirmed"
                else "not_required"
            )

        relationships = []
        for row in cross_by_candidate.get(candidate_id, []):
            destination = row["canonical_destination"]
            catalog = (
                "funds"
                if destination.startswith("funds/")
                else "epic-65"
                if "epic-65" in destination
                else "other"
            )
            relationships.append(
                {
                    "catalog": catalog,
                    "destination": destination,
                    "status": row["destination_status"],
                    "relationship": row["relationship"],
                }
            )
        for row in vehicle_by_candidate.get(candidate_id, []):
            relationships.append(
                {
                    "catalog": "funds",
                    "destination": row["canonical_destination"],
                    "status": row["destination_status"],
                    "relationship": row["relationship"],
                }
            )
        relationships.extend(extra_relationships.get(candidate_id, []))
        relationships = sorted(
            {
                json.dumps(row, ensure_ascii=False, sort_keys=True): row
                for row in relationships
            }.values(),
            key=lambda row: (
                row["catalog"],
                row["destination"],
                row["relationship"],
            ),
        )

        outcome = "confirmed"
        if candidate_id == "accel-ventiur-acelera-impacto":
            outcome = "reopened"
        elif candidate_id in {
            "accel-foreign-founder-institute-latam",
            "accel-mxcac-honduras-digital",
        }:
            outcome = "confirmed_with_resolution"
        elif candidate_id == "accel-inovativa-brasil":
            outcome = "confirmed_with_additional_evidence"

        results.append(
            {
                "schema_version": "1.0",
                "candidate_id": candidate_id,
                "name": candidate["name"],
                "reviewed_groups": groups,
                "original_decision": original,
                "resolved_decision": resolved,
                "outcome": outcome,
                "official_evidence_ids": sorted(
                    row["evidence_id"] for row in official
                ),
                "checks": {
                    "official_category": category_check,
                    "recent_activity": activity_check,
                    "external_latam_access": access_check,
                    "funds_epics_63_64_65": "checked",
                },
                "catalog_relationships": relationships,
                "divergence_ids": sorted(
                    divergence_by_candidate.get(candidate_id, [])
                ),
                "reviewed_on": "2026-07-27",
            }
        )

    publishable_ids = sorted(
        row["candidate_id"]
        for row in results
        if row["resolved_decision"] == "elegível"
    )
    publishable = {
        "schema_version": "1.0",
        "issue": 77,
        "contract_issue": 68,
        "cutoff_date": "2026-07-27",
        "status": "frozen",
        "candidate_count": len(publishable_ids),
        "candidate_ids": publishable_ids,
        "profiles_created": 0,
        "notes": "Manifesto de IDs aprovados para uma etapa posterior de publicação. Esta revisão não criou perfis.",
    }
    cross_catalog = {
        "schema_version": "1.0",
        "issue": 77,
        "catalogs_checked": ["funds", "epic-63", "epic-64", "epic-65"],
        "reviewed_candidates": len(results),
        "relationships": sum(
            len(row["catalog_relationships"]) for row in results
        ),
        "materialized_destinations": sorted(
            {
                rel["destination"]
                for row in results
                for rel in row["catalog_relationships"]
                if rel["status"] == "materializado"
            }
        ),
        "queued_destinations": sorted(
            {
                rel["destination"]
                for row in results
                for rel in row["catalog_relationships"]
                if rel["status"] in {"fila-canônica", "não-publicado"}
            }
        ),
        "resolved_boundary_divergences": [
            "div-issue77-honduras-digital-boundary"
        ],
        "silent_duplicates": [],
    }

    write_json(REVIEW / "review-evidence.json", review_evidence)
    write_json(REVIEW / "review-results.json", results)
    write_json(REVIEW / "divergences.json", divergences)
    write_json(REVIEW / "publishable-manifest.json", publishable)
    write_json(REVIEW / "cross-catalog-checks.json", cross_catalog)

    output_paths = [
        REVIEW / "cross-catalog-checks.json",
        REVIEW / "divergences.json",
        REVIEW / "publishable-manifest.json",
        REVIEW / "review-evidence.json",
        REVIEW / "review-results.json",
    ]
    manifest["status"] = "complete"
    manifest["resolved_counts"] = {
        "reviewed_unique_candidates": len(results),
        "confirmed": sum(row["outcome"] == "confirmed" for row in results),
        "confirmed_with_additional_evidence": sum(
            row["outcome"] == "confirmed_with_additional_evidence"
            for row in results
        ),
        "confirmed_with_resolution": sum(
            row["outcome"] == "confirmed_with_resolution" for row in results
        ),
        "reopened": sum(row["outcome"] == "reopened" for row in results),
        "resolved_divergences": len(divergences),
        "publishable_candidates": len(publishable_ids),
    }
    manifest["output_hashes"] = {
        path.name: normalized_sha256(path) for path in output_paths
    }
    manifest["notes"] = (
        "Revisão independente concluída. Uma decisão foi reaberta, três "
        "divergências foram resolvidas e nenhum perfil foi criado."
    )
    write_json(manifest_path, manifest)


if __name__ == "__main__":
    main()
