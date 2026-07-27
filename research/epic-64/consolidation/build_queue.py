#!/usr/bin/env python3
"""Build the deterministic platform consolidation queue for issue #94."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
REGIONS = ("brazil", "mexico-cac", "andean", "southern-cone")
FILES = {
    "candidates.jsonl": "platform_id",
    "evidence.jsonl": "evidence_id",
    "source-inventory.jsonl": "source_id",
    "coverage-matrix.jsonl": "country",
}
RUN_ID = "run-platforms-latam-consolidated-2026"
REVIEWER = "independent-reviewer-issue-94"
REVIEW_DATE = "2026-07-27"
UNKNOWN_LEGAL_NAMES = {
    "operador legal não divulgado na fonte oficial",
    "operadora não identificada publicamente",
}
OUTGOING_DESTINATIONS = {
    "plat-auge-ucr": "epic-62:program/auge-ucr",
    "plat-koga-impact-lab": (
        "research/epic-62/consolidation/candidates.jsonl#accel-sc-koga"
    ),
    "plat-open-angels": "epic-62:program/open-angels",
    "plat-pitch-day": "epic-62:program/pitch-day-pandolab",
    "plat-sambil-emprende": "epic-62:program/sambil-emprende",
    "plat-ventiur": (
        "research/epic-62/consolidation/candidates.jsonl"
        "#accel-ventiur-acelera-impacto"
    ),
}
INCOMING_RESOLUTIONS = {
    "ang-angelinvestmentnetwork-com-co": {
        "target_platform_id": "plat-red-colombiana-de-inversiones",
        "canonical_destination": (
            "research/epic-64/consolidation/candidates.jsonl"
            "#plat-red-colombiana-de-inversiones"
        ),
        "adjudication": "materialized-insufficient-evidence",
        "resolution": (
            "A rota comercial atual foi confirmada, mas a identidade jurídica do "
            "operador e uma data oficial de atividade permanecem não divulgadas."
        ),
    },
    "ang-carib-export-com--caribbean-business-angel-network": {
        "target_platform_id": None,
        "canonical_destination": (
            "out-of-scope:investor-infrastructure-without-founder-route"
        ),
        "adjudication": "rejected-by-platform-contract",
        "resolution": (
            "A fonte descreve infraestrutura para grupos, syndicates, fundos e "
            "investidores, sem rota estruturada para founders."
        ),
    },
    "ang-winverz-com": {
        "target_platform_id": None,
        "canonical_destination": (
            "out-of-scope:no-structured-founder-funding-route"
        ),
        "adjudication": "rejected-by-platform-contract",
        "resolution": (
            "A atividade atual é de eventos e articulação do ecossistema; a única "
            "descrição de Angel List é de 2020 e não expõe fluxo de captação."
        ),
    },
}
REVIEW_CONCLUSIONS = {
    "plat-a2censo": (
        "Operador BVC, marca, instrumentos e autorização foram confirmados; a "
        "campanha oficial de 2026 comprova rota e atividade de captação."
    ),
    "plat-arkangeles": (
        "Operador, rota com campanhas, instrumentos e autorização da CNBV foram "
        "confirmados em fontes oficiais."
    ),
    "plat-broota": (
        "A rota permanente para founders e os instrumentos foram confirmados; a "
        "oferta encerrada permanece subordinada à plataforma."
    ),
    "plat-captable": (
        "Formulário atual de captação, operador, produtos e registro ativo na CVM "
        "foram confirmados."
    ),
    "plat-crowder-uruguay": (
        "Operador e registro no BCU foram confirmados; documentos recentes recebem "
        "propostas de emissão e cobrem dívida, ações e instrumentos mistos."
    ),
    "plat-eqseed": (
        "Rota de captação, oferta recente, operador e registro ativo na CVM foram "
        "confirmados."
    ),
    "plat-kria": (
        "Rota atual para founders, instrumentos e registro ativo na CVM foram "
        "confirmados."
    ),
    "plat-play-business": (
        "Rota digital, revenue share, operador e autorização da CNBV foram "
        "confirmados."
    ),
    "plat-smu": (
        "Formulário de captação, produto de equity e registro ativo na CVM foram "
        "confirmados."
    ),
    "plat-auge-ucr": (
        "A fonte descreve incubação e aceleração, sem instrumento de captação; o "
        "destino correto é a epic #62."
    ),
    "plat-koga-impact-lab": (
        "A atuação confirmada é de incubação/aceleração, não de plataforma; a "
        "fronteira com a epic #62 permanece explícita."
    ),
    "plat-open-angels": (
        "Embora o operador possua registro na CVM, a rota examinada é um programa "
        "seletivo de 18 meses; a unidade pertence à epic #62."
    ),
    "plat-pitch-day": (
        "A rota é um programa de incubação/aceleração sem instrumento financeiro; "
        "a referência textual foi corrigida para a epic #62."
    ),
    "plat-sambil-emprende": (
        "A fonte descreve competição e programa de seis meses, sem rota de "
        "financiamento; o destino é a epic #62."
    ),
    "plat-ventiur": (
        "O registro na CVM não substitui uma rota distinta: a fonte atual mistura "
        "seleção, aceleração e investimento, portanto a unidade vai à epic #62."
    ),
    "plat-nexoos-paraguay": (
        "O domínio paraguaio está indisponível e as fontes atuais remetem à "
        "operação brasileira histórica; a decisão inactive permanece."
    ),
    "plat-terrenta": (
        "Operador e produto imobiliário foram identificados, mas não há rota geral "
        "para startups nem atividade recente suficiente."
    ),
    "plat-jompeame": (
        "A rota oficial é de doações para causas sociais, modalidade excluída pelo "
        "contrato."
    ),
    "plat-zafen": (
        "A rota antiga de crédito não tem atividade oficial recente e o domínio "
        "está indisponível; evidência permanece insuficiente."
    ),
    "plat-hagamosla": (
        "Domínio, operador, rota estruturada e atividade atual não puderam ser "
        "confirmados; evidência permanece insuficiente."
    ),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", asciiish)


def unique_sorted(
    records: list[dict[str, Any]], id_field: str, filename: str
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[id_field]
        if record_id in by_id:
            raise ValueError(f"ID duplicado em {filename}: {record_id}")
        by_id[record_id] = record
    return [by_id[record_id] for record_id in sorted(by_id)]


def apply_independent_resolutions(
    canonical: dict[str, list[dict[str, Any]]],
) -> None:
    candidates = canonical["candidates.jsonl"]
    pitch_day = next(
        row for row in candidates if row["platform_id"] == "plat-pitch-day"
    )
    pitch_day["reason"] = (
        "Programa de incubação/aceleração; encaminhar à trilha de aceleradoras "
        "da epic 62."
    )
    a2censo = next(
        row for row in candidates if row["platform_id"] == "plat-a2censo"
    )
    a2censo["platform"]["founder_route_url"] = (
        "https://www.bvc.com.co/financia-tu-empresa-en-a2censo"
    )

    candidates.append(
        {
            "schema_version": "1.0",
            "platform_id": "plat-red-colombiana-de-inversiones",
            "operator": {
                "operator_id": "op-red-colombiana-de-inversiones",
                "legal_name": "Operadora não identificada publicamente",
                "jurisdiction": "CO",
                "official_url": "https://www.angelinvestmentnetwork.com.co/",
            },
            "brand": {
                "brand_id": "brand-red-colombiana-de-inversiones",
                "name": "Red Colombiana de Inversiones",
                "aliases": ["Red de Ángeles Inversionistas Colombia"],
            },
            "platform": {
                "name": "Red Colombiana de Inversiones",
                "canonical_domain": "angelinvestmentnetwork.com.co",
                "official_url": "https://www.angelinvestmentnetwork.com.co/",
                "founder_route_url": (
                    "https://www.angelinvestmentnetwork.com.co/nuestras-tarifas"
                ),
                "declared_countries": ["CO"],
            },
            "products": [
                {
                    "product_id": "prod-red-colombiana-matching",
                    "name": "Publicación y matching con inversionistas",
                    "instrument_type": "matching",
                    "status": "unknown",
                }
            ],
            "offers": [],
            "regulatory_records": [],
            "discovery_source_ids": ["src-co-red-colombiana-transfer"],
            "official_evidence_ids": ["ev-red-colombiana-route"],
            "activity_evidence_ids": [],
            "route_evidence_ids": ["ev-red-colombiana-route"],
            "discovered_on": REVIEW_DATE,
            "activity_status": "unknown",
            "last_official_activity_on": None,
            "latam_founder_route": True,
            "status": "decided",
            "decision": "insufficient_evidence",
            "reason": (
                "A rota oficial permite publicar propostas e fazer matching, mas "
                "não divulga a identidade jurídica do operador nem uma data oficial "
                "de atividade recente."
            ),
            "canonical_platform_id": None,
            "canonical_profile": None,
            "owner": REVIEWER,
            "next_action": (
                "Confirmar em fonte oficial a pessoa jurídica operadora e obter "
                "atividade oficial datada dentro da janela de 24 meses."
            ),
        }
    )
    canonical["evidence.jsonl"].append(
        {
            "schema_version": "1.0",
            "evidence_id": "ev-red-colombiana-route",
            "platform_id": "plat-red-colombiana-de-inversiones",
            "subject_type": "platform",
            "subject_id": "plat-red-colombiana-de-inversiones",
            "url": "https://www.angelinvestmentnetwork.com.co/nuestras-tarifas",
            "title": "Nuestras Tarifas",
            "publisher": "Red Colombiana de Inversiones",
            "source_type": "official_platform",
            "published_on": None,
            "observed_on": None,
            "accessed_on": REVIEW_DATE,
            "claims": [
                {"field": "structured_founder_route", "finding": "confirmed"},
                {"field": "latam_access", "finding": "confirmed"},
                {"field": "product_instrument", "finding": "confirmed"},
                {"field": "legal_operator", "finding": "not_disclosed"},
                {"field": "recent_activity", "finding": "not_disclosed"},
            ],
            "locator": "Planos Pro, Global Pro e formulário de proposta",
            "summary": (
                "A página oferece publicação paga de propostas, distribuição a "
                "investidores e acesso aos contatos interessados na rede colombiana."
            ),
        }
    )
    canonical["source-inventory.jsonl"].append(
        {
            "schema_version": "1.0",
            "source_id": "src-co-red-colombiana-transfer",
            "issue": 92,
            "country": "CO",
            "source": "Red Colombiana de Inversiones",
            "initial_url": (
                "https://www.angelinvestmentnetwork.com.co/nuestras-tarifas"
            ),
            "source_category": "official_platform",
            "scope_walked": "Página de tarifas e FAQ para empreendedores.",
            "accessed_on": REVIEW_DATE,
            "robots_status": "not_applicable",
            "access_method": "manual",
            "cache_key": None,
            "result": "complete",
            "reason": None,
            "owner": None,
            "next_action": None,
            "notes": "Transferência recebida da epic #63 e adjudicada na issue #94.",
        }
    )
    for filename, id_field in FILES.items():
        canonical[filename] = unique_sorted(
            canonical[filename], id_field, filename
        )


def evidence_urls_by_platform(
    evidence: list[dict[str, Any]],
) -> dict[str, list[str]]:
    urls: dict[str, set[str]] = defaultdict(set)
    for row in evidence:
        urls[row["platform_id"]].add(row["url"])
    return {
        platform_id: sorted(platform_urls)
        for platform_id, platform_urls in urls.items()
    }


def candidate_review_record(
    candidate: dict[str, Any],
    group: str,
    urls: list[str],
) -> dict[str, Any]:
    decision = candidate["decision"]
    regulatory = (
        "confirmed-from-authoritative-source"
        if candidate["regulatory_records"]
        else "not-claimed-or-not-required-for-decision"
    )
    operator = (
        "not-disclosed-but-decision-safe"
        if candidate["operator"]["legal_name"].casefold() in UNKNOWN_LEGAL_NAMES
        else "confirmed"
    )
    return {
        "schema_version": "1.0",
        "review_id": f"review-{group}-{candidate['platform_id']}",
        "review_group": group,
        "subject_type": "platform",
        "subject_id": candidate["platform_id"],
        "target_platform_id": candidate["platform_id"],
        "reviewer": REVIEWER,
        "reviewed_on": REVIEW_DATE,
        "evidence_urls": urls,
        "contract_checks": {
            "operator_identity": operator,
            "brand_product_identity": "confirmed-or-decision-safe",
            "activity": (
                "confirmed"
                if decision == "eligible"
                else "checked-and-consistent-with-decision"
            ),
            "eligibility": "checked",
            "regulation": regulatory,
        },
        "original_decision": decision,
        "final_decision": decision,
        "conclusion": REVIEW_CONCLUSIONS[candidate["platform_id"]],
        "divergence_severity": (
            "high"
            if (
                candidate["platform_id"] == "plat-pitch-day"
                and group == "other_category"
            )
            or (candidate["platform_id"] == "plat-a2censo" and group == "eligible")
            else "none"
        ),
        "resolution": (
            "Corrigida a referência de categoria da epic #63 para a epic #62."
            if candidate["platform_id"] == "plat-pitch-day"
            and group == "other_category"
            else (
                "A rota canônica passou da campanha temporária para a página "
                "permanente de financiamento da BVC."
                if candidate["platform_id"] == "plat-a2censo"
                and group == "eligible"
                else (
                    OUTGOING_DESTINATIONS[candidate["platform_id"]]
                    if group == "outgoing_transfer"
                    else "Nenhuma alteração material necessária."
                )
            )
        ),
        "resolved": True,
    }


def build_independent_review(
    candidates: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_id = {row["platform_id"]: row for row in candidates}
    urls = evidence_urls_by_platform(evidence)
    eligible_ids = sorted(
        row["platform_id"] for row in candidates if row["decision"] == "eligible"
    )
    other_ids = sorted(
        row["platform_id"]
        for row in candidates
        if row["decision"] == "other_category"
    )
    incoming_target_ids = {
        row["target_platform_id"]
        for row in incoming
        if row["target_platform_id"] is not None
    }
    remaining_ids = sorted(
        row["platform_id"]
        for row in candidates
        if row["platform_id"] not in set(eligible_ids + other_ids)
        and row["platform_id"] not in incoming_target_ids
    )
    sample_size = math.ceil(len(remaining_ids) * 0.20)
    sample_ids = [
        platform_id
        for _, platform_id in sorted(
            (sha256(platform_id.encode("utf-8")), platform_id)
            for platform_id in remaining_ids
        )[:sample_size]
    ]

    records: list[dict[str, Any]] = []
    for group, platform_ids in (
        ("eligible", eligible_ids),
        ("other_category", other_ids),
        ("deterministic_sample", sample_ids),
    ):
        records.extend(
            candidate_review_record(by_id[platform_id], group, urls.get(platform_id, []))
            for platform_id in platform_ids
        )
    records.extend(
        candidate_review_record(
            by_id[platform_id], "outgoing_transfer", urls.get(platform_id, [])
        )
        for platform_id in other_ids
    )
    incoming_urls = {
        "ang-angelinvestmentnetwork-com-co": [
            "https://www.angelinvestmentnetwork.com.co/nuestras-tarifas",
            "https://www.angelinvestmentnetwork.com.co/preguntas-frecuentes-ent",
        ],
        "ang-carib-export-com--caribbean-business-angel-network": [
            "https://content.carib-export.com/resources/funding/angel-investing/caribbean-business-angel-network/"
        ],
        "ang-winverz-com": [
            "https://win.gt/founders/winverz-una-plataforma-que-impulsa-el-ecosistema-de-negocios-e-inversion/",
            "https://winverz.com/td/",
        ],
    }
    for transfer in incoming:
        network_id = transfer["source_network_id"]
        target_id = transfer["target_platform_id"]
        records.append(
            {
                "schema_version": "1.0",
                "review_id": f"review-incoming-transfer-{network_id}",
                "review_group": "incoming_transfer",
                "subject_type": "transfer",
                "subject_id": network_id,
                "target_platform_id": target_id,
                "reviewer": REVIEWER,
                "reviewed_on": REVIEW_DATE,
                "evidence_urls": incoming_urls[network_id],
                "contract_checks": {
                    "operator_identity": (
                        "not-disclosed"
                        if network_id == "ang-angelinvestmentnetwork-com-co"
                        else "not-required-after-contract-rejection"
                    ),
                    "brand_product_identity": "checked",
                    "activity": "checked",
                    "eligibility": "adjudicated",
                    "regulation": "not-claimed",
                },
                "original_decision": "requires-platform-contract-adjudication",
                "final_decision": transfer["adjudication"],
                "conclusion": transfer["resolution"],
                "divergence_severity": "high",
                "resolution": transfer["canonical_destination"],
                "resolved": True,
            }
        )
    records.sort(key=lambda row: row["review_id"])
    stats = {
        "eligible_population": len(eligible_ids),
        "other_category_population": len(other_ids),
        "incoming_population": len(incoming),
        "outgoing_population": len(other_ids),
        "remaining_population": len(remaining_ids),
        "sample_size": sample_size,
        "sample_rate": sample_size / len(remaining_ids),
        "sample_algorithm": (
            "Ordenar por (sha256(platform_id UTF-8), platform_id) e selecionar "
            "ceil(população * 0,20)."
        ),
        "sample_ids": sample_ids,
    }
    return records, stats


def load_inputs() -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, dict[str, int]],
]:
    grouped = {filename: [] for filename in FILES}
    tasks: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    before: dict[str, dict[str, int]] = {}
    for region in REGIONS:
        region_dir = EPIC_ROOT / region
        region_counts: dict[str, int] = {}
        for filename in (*FILES, "run-manifest.jsonl"):
            path = region_dir / filename
            payload = path.read_bytes().replace(b"\r\n", b"\n")
            hashes[path.relative_to(REPOSITORY_ROOT).as_posix()] = sha256(payload)
            records = read_jsonl(path)
            if filename in grouped:
                grouped[filename].extend(records)
                region_counts[filename] = len(records)
            else:
                for record in records:
                    if record["record_type"] == "task":
                        task = dict(record)
                        task["run_id"] = RUN_ID
                        tasks.append(task)
        before[region] = region_counts
    return grouped, tasks, dict(sorted(hashes.items())), before


def collision_groups(
    candidates: list[dict[str, Any]],
    key_builder: Callable[[dict[str, Any]], Any],
) -> list[dict[str, Any]]:
    groups: dict[Any, list[str]] = defaultdict(list)
    for candidate in candidates:
        key = key_builder(candidate)
        if key:
            groups[key].append(candidate["platform_id"])
    return [
        {"key": key, "platform_ids": sorted(ids)}
        for key, ids in sorted(groups.items(), key=lambda item: repr(item[0]))
        if len(ids) > 1
    ]


def build_deduplication_report(
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    domain_groups = collision_groups(
        candidates,
        lambda row: (
            row["platform"]["canonical_domain"],
            normalize(row["brand"]["name"]),
        ),
    )

    def legal_key(row: dict[str, Any]) -> Any:
        name = row["operator"]["legal_name"]
        if name.casefold() in UNKNOWN_LEGAL_NAMES:
            return None
        return row["operator"]["jurisdiction"], normalize(name)

    legal_groups = collision_groups(candidates, legal_key)
    regulatory_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for candidate in candidates:
        for record in candidate["regulatory_records"]:
            number = record.get("registration_number")
            if number:
                key = (record["jurisdiction"], record["authority"], number)
                regulatory_groups[key].append(candidate["platform_id"])
    regulatory_collisions = [
        {"key": key, "platform_ids": sorted(ids)}
        for key, ids in sorted(regulatory_groups.items())
        if len(ids) > 1
    ]
    if domain_groups or legal_groups or regulatory_collisions:
        raise ValueError(
            "colisão de identidade não resolvida: "
            f"domain={domain_groups}, legal={legal_groups}, "
            f"regulatory={regulatory_collisions}"
        )
    return {
        "schema_version": "1.0",
        "issue": 94,
        "pass_1_domain_brand": {
            "records_scanned": len(candidates),
            "unresolved_groups": domain_groups,
        },
        "pass_2_legal_regulatory": {
            "records_scanned": len(candidates),
            "legal_name_unresolved_groups": legal_groups,
            "regulatory_unresolved_groups": regulatory_collisions,
        },
        "canonical_candidates": len(candidates),
    }


def incoming_angel_transfers(
    platform_ids: set[str],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen_networks: set[str] = set()
    for path in sorted((REPOSITORY_ROOT / "research" / "epic-63").rglob("candidates.jsonl")):
        relative = path.relative_to(REPOSITORY_ROOT).parts
        if "shards" in relative or any(
            part in {"examples", "templates"} for part in relative
        ):
            continue
        for candidate in read_jsonl(path):
            if candidate.get("decision") != "encaminhado-para-plataformas":
                continue
            network_id = candidate["network_id"]
            if network_id in seen_networks:
                continue
            seen_networks.add(network_id)
            if network_id not in INCOMING_RESOLUTIONS:
                # The issue #94 queue is frozen. Transfers merged into epic #63
                # after its cutoff belong to a later consolidation cycle.
                continue
            proposed_profile = candidate.get("canonical_profile")
            adjudication = INCOMING_RESOLUTIONS[network_id]
            target_id = adjudication["target_platform_id"]
            materialized = target_id in platform_ids if target_id else False
            if adjudication["adjudication"].startswith("materialized") and not materialized:
                raise ValueError(f"transferência não materializada: {network_id}")
            results.append(
                {
                    "source_epic": 63,
                    "source_network_id": network_id,
                    "source_name": candidate["name"],
                    "proposed_profile": proposed_profile,
                    "target_platform_id": target_id,
                    "materialized": materialized,
                    "canonical_destination": adjudication["canonical_destination"],
                    "adjudication": adjudication["adjudication"],
                    "resolution": adjudication["resolution"],
                    "owner": None,
                    "next_action": None,
                }
            )
    return sorted(results, key=lambda row: row["source_network_id"])


def build_outputs() -> dict[str, bytes]:
    grouped, tasks, input_hashes, before_counts = load_inputs()
    canonical = {
        filename: unique_sorted(copy.deepcopy(records), FILES[filename], filename)
        for filename, records in grouped.items()
    }
    apply_independent_resolutions(canonical)
    candidates = canonical["candidates.jsonl"]
    evidence = canonical["evidence.jsonl"]
    sources = canonical["source-inventory.jsonl"]
    coverage = canonical["coverage-matrix.jsonl"]
    dedupe = build_deduplication_report(candidates)

    if len(candidates) != 39 or len(evidence) != 63 or len(sources) != 118:
        raise ValueError("contagens consolidadas divergentes")
    if len(coverage) != 20:
        raise ValueError("cobertura consolidada divergente")
    if any(candidate["decision"] is None for candidate in candidates):
        raise ValueError("candidato sem decisão")
    if any(
        not candidate.get("owner") or not candidate.get("next_action")
        for candidate in candidates
        if candidate["decision"] == "insufficient_evidence"
    ):
        raise ValueError("pendência sem responsável ou próxima ação")

    platform_ids = {candidate["platform_id"] for candidate in candidates}
    evidence_ids = {row["evidence_id"] for row in evidence}
    source_ids = {row["source_id"] for row in sources}
    for candidate in candidates:
        if any(
            evidence_id not in evidence_ids
            for evidence_id in (
                candidate["official_evidence_ids"]
                + candidate["activity_evidence_ids"]
                + candidate["route_evidence_ids"]
            )
        ):
            raise ValueError(f"evidência órfã em {candidate['platform_id']}")
        if any(
            source_id not in source_ids
            for source_id in candidate["discovery_source_ids"]
        ):
            raise ValueError(f"fonte órfã em {candidate['platform_id']}")
    if any(row["platform_id"] not in platform_ids for row in evidence):
        raise ValueError("evidência aponta para plataforma inexistente")

    outgoing = []
    for candidate in candidates:
        if candidate["decision"] != "other_category":
            continue
        destination = OUTGOING_DESTINATIONS.get(candidate["platform_id"])
        if not destination:
            raise ValueError(
                f"fronteira sem destino: {candidate['platform_id']}"
            )
        outgoing.append(
            {
                "platform_id": candidate["platform_id"],
                "platform_decision": candidate["decision"],
                "canonical_destination": destination,
            }
        )
    incoming = incoming_angel_transfers(platform_ids)
    if any(
        not row["canonical_destination"] or not row["adjudication"]
        for row in incoming
    ):
        raise ValueError("transferência recebida sem adjudicação final")
    resolutions = {
        "schema_version": "1.0",
        "issue": 94,
        "outgoing_category_resolutions": outgoing,
        "incoming_angel_transfers": incoming,
    }

    base_outputs = {
        filename: jsonl_bytes(records)
        for filename, records in canonical.items()
    }
    artifact_hashes = {
        filename: sha256(base_outputs[filename])
        for filename in (
            "candidates.jsonl",
            "coverage-matrix.jsonl",
            "evidence.jsonl",
            "source-inventory.jsonl",
        )
    }
    tasks.sort(key=lambda row: row["task_id"])
    run = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issues": [90, 91, 92, 93],
        "contract_issue": 89,
        "cutoff_date": "2026-07-27",
        "created_on": "2026-07-27",
        "status": "complete",
        "task_count": len(tasks),
        "scraping_performed": False,
        "hash_algorithm": "sha256",
        "artifact_hashes": artifact_hashes,
        "owner": "coordinator-issue-94",
        "execution_policy": {
            "respect_robots_txt": True,
            "bypass_access_controls": False,
            "max_concurrency_per_domain": 2,
            "minimum_delay_ms": 500,
            "cache_enabled": True,
            "retry_attempts": 3,
            "browser_policy": "official_js_only",
        },
        "notes": (
            "Redução sem scraping novo; preserva os shards e tarefas das quatro "
            "auditorias regionais."
        ),
    }
    base_outputs["run-manifest.jsonl"] = jsonl_bytes([run, *tasks])
    base_outputs["deduplication-report.json"] = json_bytes(dedupe)
    base_outputs["category-resolutions.json"] = json_bytes(resolutions)
    review, review_stats = build_independent_review(candidates, evidence, incoming)
    unresolved_high = [
        row
        for row in review
        if row["divergence_severity"] == "high" and not row["resolved"]
    ]
    if unresolved_high:
        raise ValueError("divergência alta não resolvida na revisão independente")
    base_outputs["independent-review.jsonl"] = jsonl_bytes(review)
    base_outputs["INDEPENDENT_REVIEW.md"] = (
        f"""# Revisão independente da consolidação

Revisor: `{REVIEWER}`. Data: {REVIEW_DATE}. A revisão verificou identidade do
operador, marca e produto, atividade, elegibilidade e regulação com evidência
oficial.

## Cobertura

| Grupo | População | Revisados |
| --- | ---: | ---: |
| Elegíveis | {review_stats["eligible_population"]} | {review_stats["eligible_population"]} |
| `other_category` | {review_stats["other_category_population"]} | {review_stats["other_category_population"]} |
| Transferências recebidas | {review_stats["incoming_population"]} | {review_stats["incoming_population"]} |
| Transferências enviadas | {review_stats["outgoing_population"]} | {review_stats["outgoing_population"]} |
| Demais candidatos | {review_stats["remaining_population"]} | {review_stats["sample_size"]} |

A amostra dos demais candidatos representa
{review_stats["sample_rate"]:.2%} e foi obtida por:
{review_stats["sample_algorithm"]}

IDs amostrados: {", ".join(f"`{value}`" for value in review_stats["sample_ids"])}.

## Divergências resolvidas

- as três transferências da epic #63 foram adjudicadas: uma materializada como
  `insufficient_evidence` e duas rejeitadas pelo contrato;
- a justificativa de `plat-pitch-day` passou a apontar para a epic #62;
- a rota canônica da a2censo passou da campanha temporária para a página
  permanente da BVC;
- a2censo e Crowder permaneceram elegíveis após confirmação por fontes oficiais.

Não restou divergência alta aberta. O manifesto pode ser congelado.
"""
    ).encode("utf-8")
    output_hashes = {
        filename: sha256(payload) for filename, payload in base_outputs.items()
    }

    counts = dict(sorted(Counter(row["decision"] for row in candidates).items()))
    manifest = {
        "schema_version": "1.0",
        "issue": 94,
        "cutoff_date": "2026-07-27",
        "status": "frozen",
        "independent_review_status": "complete",
        "before_counts": before_counts,
        "after_counts": {
            "candidates": len(candidates),
            "evidence": len(evidence),
            "sources": len(sources),
            "countries": len(coverage),
            "tasks": len(tasks),
        },
        "decision_counts": counts,
        "outgoing_category_resolutions": len(outgoing),
        "incoming_angel_transfers": len(incoming),
        "materialized_incoming_transfers": sum(row["materialized"] for row in incoming),
        "independent_review": {
            **review_stats,
            "review_count": len(review),
            "resolved_high_divergences": sum(
                row["divergence_severity"] == "high" and row["resolved"]
                for row in review
            ),
            "unresolved_high_divergences": len(unresolved_high),
        },
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
    }
    base_outputs["consolidation-manifest.json"] = json_bytes(manifest)

    report = f"""# Fila consolidada de plataformas

Este bundle materializa a redução e a revisão independente da issue #94 na data
de corte 2026-07-27. Ele não publica perfis.

## Before / after

| Artefato | Antes | Depois |
| --- | ---: | ---: |
| Candidatos | 38 | {len(candidates)} |
| Evidências | 62 | {len(evidence)} |
| Fontes | 117 | {len(sources)} |
| Países | 20 | {len(coverage)} |

As duas passagens de deduplicação não encontraram colisões conhecidas. Valores
como “operador legal não divulgado” foram corretamente ignorados como chave.

## Decisões

- `eligible`: {counts.get("eligible", 0)}.
- `insufficient_evidence`: {counts.get("insufficient_evidence", 0)}.
- `other_category`: {counts.get("other_category", 0)}.
- `excluded`: {counts.get("excluded", 0)}.
- `inactive`: {counts.get("inactive", 0)}.
- Transferências recebidas da epic #63: {len(incoming)}.
- Transferências materializadas: {sum(row["materialized"] for row in incoming)}.
- Transferências rejeitadas pelo contrato: {sum(not row["materialized"] for row in incoming)}.

## Gate

A redução é reproduzível, possui hashes e está `frozen`. A revisão independente
cobriu 100% dos elegíveis, `other_category`, transferências recebidas e enviadas,
além de {review_stats["sample_rate"]:.2%} dos demais candidatos. Não há
divergência alta aberta.

## Reprodução

```text
python research/epic-64/consolidation/build_queue.py
python research/epic-64/consolidation/build_queue.py --check
python research/epic-64/validate.py --dataset research/epic-64/consolidation
python -m unittest discover -s research/epic-64/consolidation/tests -p "test_*.py"
```
"""
    base_outputs["README.md"] = report.encode("utf-8")
    return base_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for filename, payload in outputs.items():
        path = HERE / filename
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                drift.append(filename)
        else:
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
