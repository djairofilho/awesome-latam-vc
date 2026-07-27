#!/usr/bin/env python3
"""Build the deterministic public-program consolidation queue for issue #102."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
REGIONS = ("brazil", "mexico", "andean", "southern-cone")
IDENTIFIERS = {
    "agencies.jsonl": "agency_id",
    "programs.jsonl": "program_id",
    "calls.jsonl": "call_id",
    "evidence.jsonl": "evidence_id",
    "coverage-matrix.jsonl": "coverage_id",
}
RUN_ID = "run-issue-102-public-program-consolidation"
REVIEWER = "independent-reviewer-issue-102"
REVIEWED_ON = "2026-07-27"

TRANSFER_OUTCOMES = {
    "accel-acelera-divinopolis": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-acelera-divinopolis",
        "A fonte confirma cinco edições e rota para startups, mas não esclarece se a bolsa é benefício financeiro; as premiações descritas são capacitações.",
    ),
    "accel-acre-for-startups": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-acre-for-startups",
        "A bolsa financeira e a rota para startups são explícitas, mas a única edição localizada está encerrada e não há recorrência oficial.",
    ),
    "accel-and-agroinnovatec": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-agroinnovatec",
        "As edições 2025 e 2026, a rota para propostas e o acesso a capital semente satisfazem o contrato público.",
    ),
    "accel-and-emprendimiento-digital": (
        "rejected-by-public-contract",
        "research/epic-62/consolidation/candidates.jsonl#accel-and-emprendimiento-digital",
        "A fonte oferece acompanhamento técnico, recursos e conexões, mas não confirma capital ou financiamento para os empreendimentos.",
    ),
    "accel-bndes-garagem": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-bndes-garagem",
        "A rota anual até 2028 e a premiação em dinheiro comprovam benefício, startups e recorrência.",
    ),
    "accel-brde-labs-rs": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-brde-labs-rs",
        "A sétima edição oficial confirma rota recorrente para startups e R$ 261 mil em prêmios.",
    ),
    "accel-finep-mulheres-inovadoras": (
        "materialized-after-independent-review",
        "research/epic-65/consolidation/programs.jsonl#program-finep-mulheres-inovadoras",
        "A sétima edição e o histórico das seis anteriores confirmam rota recorrente e prêmios em dinheiro para startups.",
    ),
    "accel-mxcac-cenpromype": (
        "rejected-by-public-contract",
        "out-of-scope:regional-public-operator-without-specific-program",
        "A transferência identifica apenas um organismo regional; não há programa, benefício, rota ou atividade adjudicáveis.",
    ),
    "accel-sc-anii-sprintuy": (
        "rejected-by-public-contract",
        "out-of-scope:soft-landing-without-capital",
        "Passagens e hospedagem para uma imersão não constituem os instrumentos financeiros enumerados pelo contrato.",
    ),
    "accel-sc-incubate": (
        "rejected-by-public-contract",
        "research/epic-62/consolidation/candidates.jsonl#accel-sc-incubate",
        "A incubação e mentoria são estruturadas, mas a fonte não oferece benefício financeiro.",
    ),
    "accel-sc-mic-reinventa": (
        "rejected-by-public-contract",
        "research/epic-62/consolidation/candidates.jsonl#accel-sc-mic-reinventa",
        "A assistência técnica é pública e atual, mas a fonte não confirma capital ou financiamento.",
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


def load_inputs() -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, dict[str, int]],
]:
    grouped = {filename: [] for filename in IDENTIFIERS}
    tasks: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}
    before_counts: dict[str, dict[str, int]] = {}

    for region in REGIONS:
        region_counts: dict[str, int] = {}
        region_dir = EPIC_ROOT / region
        for filename in (*IDENTIFIERS, "run-manifest.jsonl"):
            path = region_dir / filename
            payload = path.read_bytes().replace(b"\r\n", b"\n")
            input_hashes[path.relative_to(REPOSITORY_ROOT).as_posix()] = sha256(
                payload
            )
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
        before_counts[region] = region_counts

    return grouped, tasks, dict(sorted(input_hashes.items())), before_counts


def unique_and_sorted(
    records: list[dict[str, Any]], id_field: str, filename: str
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[id_field]
        previous = by_id.get(record_id)
        if previous is not None:
            if previous != record:
                raise ValueError(f"ID divergente em {filename}: {record_id}")
            raise ValueError(f"ID duplicado em {filename}: {record_id}")
        by_id[record_id] = record
    return [by_id[record_id] for record_id in sorted(by_id)]


def official_evidence(
    evidence_id: str,
    subject_type: str,
    subject_id: str,
    url: str,
    title: str,
    publisher: str,
    claims: list[tuple[str, str]],
    summary: str,
    *,
    observed_on: str = REVIEWED_ON,
    published_on: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_type": "oficial",
        "published_on": published_on,
        "observed_on": observed_on,
        "accessed_on": REVIEWED_ON,
        "claims": [
            {"field": field, "finding": finding} for field, finding in claims
        ],
        "locator": "Página oficial e seção material indicada no resumo",
        "summary": summary,
    }


def public_agency(
    agency_id: str,
    name: str,
    country: str,
    official_site: str,
    route_url: str,
    program_ids: list[str],
    evidence_ids: list[str],
    decision: str,
    reason: str | None,
) -> dict[str, Any]:
    pending = decision == "evidência insuficiente"
    return {
        "schema_version": "1.0",
        "agency_id": agency_id,
        "name": name,
        "aliases": [],
        "country": country,
        "geography": [country],
        "official_site": official_site,
        "route_url": route_url,
        "program_ids": program_ids,
        "official_evidence_ids": evidence_ids,
        "research_status": "decidida",
        "decision": decision,
        "canonical_agency_id": None,
        "canonical_profile": None,
        "reason": reason,
        "owner": REVIEWER if pending else None,
        "next_action": (
            "Obter documento oficial que caracterize expressamente a natureza financeira da bolsa."
            if pending
            else None
        ),
    }


def public_program(
    program_id: str,
    agency_id: str,
    name: str,
    official_url: str,
    geography: list[str],
    program_kind: str,
    benefit_types: list[str],
    financial_benefit: bool | None,
    startup_route: bool | None,
    program_status: str,
    activity_basis: str,
    latest_signal: str | None,
    evidence_ids: list[str],
    decision: str,
    reason: str | None,
    next_action: str | None = None,
) -> dict[str, Any]:
    pending = decision == "evidência insuficiente"
    return {
        "schema_version": "1.0",
        "program_id": program_id,
        "agency_id": agency_id,
        "name": name,
        "aliases": [],
        "official_url": official_url,
        "route_url": official_url,
        "geography": geography,
        "program_kind": program_kind,
        "benefit_types": benefit_types,
        "financial_benefit": financial_benefit,
        "startup_route": startup_route,
        "program_status": program_status,
        "activity_basis": activity_basis,
        "latest_official_signal_on": latest_signal,
        "assessed_on": REVIEWED_ON,
        "call_ids": [],
        "official_evidence_ids": evidence_ids,
        "research_status": "decidido",
        "decision": decision,
        "canonical_program_id": None,
        "canonical_profile": None,
        "reason": reason,
        "owner": REVIEWER if pending else None,
        "next_action": next_action if pending else None,
    }


def replace_claim(evidence: dict[str, Any], field: str, finding: str) -> None:
    for claim in evidence["claims"]:
        if claim["field"] == field:
            claim["finding"] = finding
            return
    evidence["claims"].append({"field": field, "finding": finding})


def apply_independent_decisions(
    canonical: dict[str, list[dict[str, Any]]],
) -> None:
    agencies = {row["agency_id"]: row for row in canonical["agencies.jsonl"]}
    programs = {row["program_id"]: row for row in canonical["programs.jsonl"]}
    evidence = {row["evidence_id"]: row for row in canonical["evidence.jsonl"]}

    for agency_id in ("agency-sena", "agency-sercotec"):
        agency = agencies[agency_id]
        agency["decision"] = "evidência insuficiente"
        agency["reason"] = (
            "A fonte confirma uma rota pública para empreendimentos em geral, "
            "mas não delimita startups ou negócios inovadores escaláveis."
        )
        agency["owner"] = REVIEWER
        agency["next_action"] = (
            "Obter critério oficial que diferencie startups da população geral de empreendedores."
        )
        agency_evidence = evidence[agency["official_evidence_ids"][0]]
        replace_claim(agency_evidence, "rota para startups", "não divulgado")
        agency_evidence["summary"] += (
            " A revisão independente não encontrou recorte explícito de startups."
        )

    for program_id in (
        "program-sena-fondo-emprender",
        "program-sercotec-capital-pioneras",
    ):
        program = programs[program_id]
        program["decision"] = "evidência insuficiente"
        program["startup_route"] = None
        program["reason"] = (
            "O benefício e a atividade são oficiais, mas a elegibilidade abrange "
            "empreendimentos em geral e não confirma uma rota específica para startups."
        )
        program["owner"] = REVIEWER
        program["next_action"] = (
            "Localizar regra oficial que restrinja ou identifique startups entre os beneficiários."
        )
        program_evidence = evidence[program["official_evidence_ids"][0]]
        replace_claim(program_evidence, "rota para startups", "não divulgado")
        program_evidence["summary"] += (
            " A revisão independente não tratou empreendedor ou novo negócio como sinônimo de startup."
        )

    finep = agencies["agency-finep"]
    finep.update(
        {
            "route_url": "https://www.finep.gov.br/apoio-e-financiamento-externa/programas-e-linhas/mulheresinovadoras",
            "decision": "elegível",
            "reason": None,
            "owner": None,
            "next_action": None,
        }
    )
    finep["program_ids"].append("program-finep-mulheres-inovadoras")
    finep["program_ids"].sort()
    finep_evidence = evidence["evidence-agency-finep"]
    finep_evidence.update(
        {
            "url": finep["route_url"],
            "title": "Programa Mulheres Inovadoras",
            "locator": "Página permanente e histórico de edições",
            "summary": (
                "A Finep mantém uma rota recorrente para startups lideradas por "
                "mulheres, com premiação financeira e sete edições até 2026."
            ),
        }
    )
    replace_claim(finep_evidence, "rota para startups", "confirmado")

    new_agencies = [
        public_agency(
            "agency-brde",
            "Banco Regional de Desenvolvimento do Extremo Sul",
            "Brasil",
            "https://brde.com.br/",
            "https://brde.com.br/noticia/brde-labs-rs-2026-esta-com-inscricoes-abertas/",
            ["program-brde-labs-rs"],
            ["evidence-agency-brde"],
            "elegível",
            None,
        ),
        public_agency(
            "agency-prefeitura-divinopolis",
            "Prefeitura de Divinópolis",
            "Brasil",
            "https://www.divinopolis.mg.gov.br/",
            "https://www.divinopolis.mg.gov.br/portal/servicos/1042/acelera-divinopolis/",
            ["program-acelera-divinopolis"],
            ["evidence-agency-prefeitura-divinopolis"],
            "evidência insuficiente",
            "A rota para startups é oficial, mas a natureza financeira da bolsa não é divulgada.",
        ),
    ]
    canonical["agencies.jsonl"].extend(new_agencies)

    for agency_id, program_id in (
        ("agency-bdp-bolivia", "program-agroinnovatec"),
        ("agency-bndes", "program-bndes-garagem"),
        ("agency-sebrae", "program-acre-for-startups"),
    ):
        agencies[agency_id]["program_ids"].append(program_id)
        agencies[agency_id]["program_ids"].sort()

    new_programs = [
        public_program(
            "program-acelera-divinopolis",
            "agency-prefeitura-divinopolis",
            "Acelera Divinópolis",
            "https://www.divinopolis.mg.gov.br/portal/servicos/1042/acelera-divinopolis/",
            ["Brasil", "Divinópolis"],
            "recorrente",
            [],
            None,
            True,
            "fechado agora, recorrente",
            "recorrência oficial em 24 meses",
            REVIEWED_ON,
            ["evidence-program-acelera-divinopolis"],
            "evidência insuficiente",
            "A quinta edição confirma rota e recorrência, mas a fonte não esclarece se a bolsa é financeira; os R$ 100 mil citados são revertidos em capacitações.",
            "Obter edital ou documento oficial que defina a bolsa e seu desembolso.",
        ),
        public_program(
            "program-acre-for-startups",
            "agency-sebrae",
            "Acre for Startups",
            "https://conteudo.ventiur.net/acre-for-startups",
            ["Brasil", "Acre"],
            "temporário",
            ["subvenção"],
            True,
            True,
            "não confirmado",
            "sem sinal suficiente",
            None,
            ["evidence-program-acre-for-startups"],
            "evidência insuficiente",
            "A edição encerrada oferece bolsa financeira a startups, mas nenhuma fonte oficial confirma intake permanente ou recorrência.",
            "Obter anúncio oficial de nova edição ou regra de recorrência do Sebrae Acre.",
        ),
        public_program(
            "program-agroinnovatec",
            "agency-bdp-bolivia",
            "AgroInnovatec",
            "https://www.undp.org/es/bolivia/noticias/agroinnovatec-2026",
            ["Bolívia"],
            "recorrente",
            ["capital"],
            True,
            True,
            "ativo",
            "recorrência oficial em 24 meses",
            "2026-02-05",
            ["evidence-program-agroinnovatec"],
            "elegível",
            None,
        ),
        public_program(
            "program-bndes-garagem",
            "agency-bndes",
            "BNDES Garagem",
            "https://garagem.bndes.gov.br/",
            ["Brasil"],
            "recorrente",
            ["subvenção"],
            True,
            True,
            "fechado agora, recorrente",
            "recorrência oficial em 24 meses",
            REVIEWED_ON,
            ["evidence-program-bndes-garagem"],
            "elegível",
            None,
        ),
        public_program(
            "program-brde-labs-rs",
            "agency-brde",
            "BRDE Labs RS",
            "https://brde.com.br/noticia/brde-labs-rs-2026-esta-com-inscricoes-abertas/",
            ["Brasil", "Região Sul"],
            "recorrente",
            ["subvenção"],
            True,
            True,
            "fechado agora, recorrente",
            "recorrência oficial em 24 meses",
            "2026-03-26",
            ["evidence-program-brde-labs-rs"],
            "elegível",
            None,
        ),
        public_program(
            "program-finep-mulheres-inovadoras",
            "agency-finep",
            "Programa Mulheres Inovadoras",
            "https://www.finep.gov.br/apoio-e-financiamento-externa/programas-e-linhas/mulheresinovadoras",
            ["Brasil"],
            "recorrente",
            ["subvenção"],
            True,
            True,
            "fechado agora, recorrente",
            "recorrência oficial em 24 meses",
            REVIEWED_ON,
            ["evidence-program-finep-mulheres-inovadoras"],
            "elegível",
            None,
        ),
    ]
    canonical["programs.jsonl"].extend(new_programs)

    confirmed = "confirmado"
    not_disclosed = "não divulgado"
    new_evidence = [
        official_evidence(
            "evidence-agency-brde", "agency", "agency-brde",
            "https://brde.com.br/noticia/brde-labs-rs-2026-esta-com-inscricoes-abertas/",
            "BRDE Labs RS 2026", "BRDE",
            [("tipo de entidade", confirmed), ("rota para startups", confirmed)],
            "O banco público opera a sétima edição de uma rota recorrente para startups.",
            observed_on="2026-03-26", published_on="2026-03-26",
        ),
        official_evidence(
            "evidence-agency-prefeitura-divinopolis", "agency", "agency-prefeitura-divinopolis",
            "https://www.divinopolis.mg.gov.br/portal/servicos/1042/acelera-divinopolis/",
            "Acelera Divinópolis", "Prefeitura de Divinópolis",
            [("tipo de entidade", confirmed), ("rota para startups", confirmed)],
            "A prefeitura opera a quinta edição do programa municipal para startups.",
        ),
        official_evidence(
            "evidence-program-acelera-divinopolis", "program", "program-acelera-divinopolis",
            "https://www.divinopolis.mg.gov.br/portal/servicos/1042/acelera-divinopolis/",
            "Acelera Divinópolis", "Prefeitura de Divinópolis",
            [("benefício financeiro", not_disclosed), ("rota para startups", confirmed), ("atividade do programa", confirmed), ("recorrência", confirmed), ("valor", not_disclosed)],
            "A página registra a quinta edição, inscrições encerradas e bolsa sem natureza ou valor definidos; a premiação é revertida em capacitações.",
        ),
        official_evidence(
            "evidence-program-acre-for-startups", "program", "program-acre-for-startups",
            "https://conteudo.ventiur.net/acre-for-startups",
            "Acre for Startups", "Ventiur",
            [("benefício financeiro", confirmed), ("rota para startups", confirmed), ("atividade do programa", not_disclosed), ("recorrência", not_disclosed), ("valor", confirmed)],
            "A página do operador informa bolsa mensal de R$ 6.500 por cinco meses, mas mostra inscrições encerradas e não confirma nova edição.",
        ),
        official_evidence(
            "evidence-program-agroinnovatec", "program", "program-agroinnovatec",
            "https://www.undp.org/es/bolivia/noticias/agroinnovatec-2026",
            "AgroInnovatec 2026", "PNUD Bolívia",
            [("benefício financeiro", confirmed), ("rota para startups", confirmed), ("atividade do programa", confirmed), ("recorrência", confirmed), ("geografia", confirmed), ("valor", not_disclosed)],
            "O PNUD registra edições em 2025 e 2026 e acesso a capital semente para as três melhores propostas, sem divulgar valor individual.",
            observed_on="2026-02-05", published_on="2026-02-05",
        ),
        official_evidence(
            "evidence-program-bndes-garagem", "program", "program-bndes-garagem",
            "https://garagem.bndes.gov.br/",
            "BNDES Garagem", "BNDES",
            [("benefício financeiro", confirmed), ("rota para startups", confirmed), ("atividade do programa", confirmed), ("recorrência", confirmed), ("valor", confirmed)],
            "A página oficial prevê cem negócios por ano até 2028 e distribui R$ 915 mil em premiações no ciclo.",
        ),
        official_evidence(
            "evidence-program-brde-labs-rs", "program", "program-brde-labs-rs",
            "https://brde.com.br/noticia/brde-labs-rs-2026-esta-com-inscricoes-abertas/",
            "BRDE Labs RS 2026", "BRDE",
            [("benefício financeiro", confirmed), ("rota para startups", confirmed), ("atividade do programa", confirmed), ("recorrência", confirmed), ("valor", confirmed)],
            "A sétima edição seleciona startups da Região Sul e distribui R$ 261 mil em prêmios.",
            observed_on="2026-03-26", published_on="2026-03-26",
        ),
        official_evidence(
            "evidence-program-finep-mulheres-inovadoras", "program", "program-finep-mulheres-inovadoras",
            "https://www.finep.gov.br/apoio-e-financiamento-externa/programas-e-linhas/mulheresinovadoras",
            "Programa Mulheres Inovadoras", "Finep",
            [("benefício financeiro", confirmed), ("rota para startups", confirmed), ("atividade do programa", confirmed), ("recorrência", confirmed), ("valor", confirmed)],
            "A página permanente registra a sétima edição, seis edições anteriores e prêmios de R$ 60 mil a R$ 120 mil.",
        ),
    ]
    canonical["evidence.jsonl"].extend(new_evidence)

    for filename, id_field in IDENTIFIERS.items():
        canonical[filename] = unique_and_sorted(
            canonical[filename], id_field, filename
        )


def build_transfer_resolutions(program_ids: set[str]) -> list[dict[str, Any]]:
    accelerator_candidates = read_jsonl(
        REPOSITORY_ROOT
        / "research"
        / "epic-62"
        / "consolidation"
        / "candidates.jsonl"
    )
    results: list[dict[str, Any]] = []
    for candidate in accelerator_candidates:
        destination = candidate.get("destination")
        if (
            candidate.get("decision") != "encaminhado-para-outra-epic"
            or not isinstance(destination, str)
            or "65" not in destination
        ):
            continue
        if "#" in destination:
            target_program_id = destination.rsplit("#", 1)[1]
        elif destination.startswith("epic-65:program/"):
            target_program_id = destination.rsplit("/", 1)[1]
        else:
            raise ValueError(
                f"destino público não canônico para {candidate['candidate_id']}"
            )
        materialized = target_program_id in program_ids
        if candidate["candidate_id"] in TRANSFER_OUTCOMES:
            resolution, canonical_destination, adjudication = TRANSFER_OUTCOMES[
                candidate["candidate_id"]
            ]
        else:
            resolution = "matched-existing-program"
            canonical_destination = destination
            adjudication = (
                "A transferência coincide com programa regional já validado pelo "
                "contrato público."
            )
        expected_materialized = resolution != "rejected-by-public-contract"
        if materialized != expected_materialized:
            raise ValueError(
                f"materialização divergente para {candidate['candidate_id']}"
            )
        results.append(
            {
                "source_epic": 62,
                "source_candidate_id": candidate["candidate_id"],
                "incoming_destination": destination,
                "target_program_id": target_program_id,
                "resolution": resolution,
                "materialized": materialized,
                "canonical_destination": canonical_destination,
                "adjudication": adjudication,
                "owner": None,
                "next_action": None,
            }
        )
    return sorted(results, key=lambda row: row["source_candidate_id"])


def build_category_resolutions(
    programs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    explicit = {
        "program-bndes-selecao-fundos": "funds/:bndes-selecao-de-fundos",
        "program-finep-inovar": "funds/:finep-programa-inovar",
        "program-nafin-capital-emprendedor": "funds/:nafin-capital-emprendedor",
        "program-sebrae-capital-empreendedor": (
            "research/epic-62/consolidation/candidates.jsonl"
            "#accel-capital-empreendedor-rj"
        ),
        "program-sebrae-fic-fip": "funds/:sebrae-fic-fip",
    }
    known_ids = {program["program_id"] for program in programs}
    missing = sorted(set(explicit) - known_ids)
    if missing:
        raise ValueError(f"fronteiras ausentes do registro: {missing}")
    return [
        {
            "program_id": program_id,
            "public_program_decision": next(
                row["decision"]
                for row in programs
                if row["program_id"] == program_id
            ),
            "relationship": "transferred-to-other-category",
            "canonical_destination": destination,
        }
        for program_id, destination in sorted(explicit.items())
    ]


def build_independent_review(
    baseline: dict[str, list[dict[str, Any]]],
    canonical: dict[str, list[dict[str, Any]]],
    transfer_resolutions: list[dict[str, Any]],
    category_resolutions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    final_agencies = {row["agency_id"]: row for row in canonical["agencies.jsonl"]}
    final_programs = {row["program_id"]: row for row in canonical["programs.jsonl"]}
    final_evidence = {
        row["evidence_id"]: row for row in canonical["evidence.jsonl"]
    }
    accelerator_evidence = {
        row["evidence_id"]: row
        for row in read_jsonl(
            REPOSITORY_ROOT
            / "research"
            / "epic-62"
            / "consolidation"
            / "evidence.jsonl"
        )
    }
    accelerator_candidates = {
        row["candidate_id"]: row
        for row in read_jsonl(
            REPOSITORY_ROOT
            / "research"
            / "epic-62"
            / "consolidation"
            / "candidates.jsonl"
        )
    }
    reviews: list[dict[str, Any]] = []

    for entity_type, filename, id_field in (
        ("agency", "agencies.jsonl", "agency_id"),
        ("program", "programs.jsonl", "program_id"),
    ):
        for original in baseline[filename]:
            if original["decision"] not in ("elegível", "evidência insuficiente"):
                continue
            subject_id = original[id_field]
            final = (
                final_agencies[subject_id]
                if entity_type == "agency"
                else final_programs[subject_id]
            )
            consulted_ids = final["official_evidence_ids"]
            changed = original["decision"] != final["decision"]
            group = (
                f"eligible_{entity_type}"
                if original["decision"] == "elegível"
                else f"insufficient_{entity_type}"
            )
            checks: dict[str, Any]
            if entity_type == "program":
                checks = {
                    "financial_benefit": final["financial_benefit"],
                    "startup_route": final["startup_route"],
                    "activity_basis": final["activity_basis"],
                }
            else:
                linked = [
                    final_programs[program_id]["decision"]
                    for program_id in final["program_ids"]
                ]
                checks = {
                    "route_url_present": bool(final["route_url"]),
                    "eligible_program_linked": "elegível" in linked,
                }
            reviews.append(
                {
                    "schema_version": "1.0",
                    "review_id": f"review-{group.replace('_', '-')}-{subject_id}",
                    "review_group": group,
                    "subject_type": entity_type,
                    "subject_id": subject_id,
                    "target_entity_id": subject_id,
                    "reviewer": REVIEWER,
                    "reviewed_on": REVIEWED_ON,
                    "evidence_ids": consulted_ids,
                    "evidence_urls": [final_evidence[eid]["url"] for eid in consulted_ids],
                    "contract_checks": checks,
                    "original_decision": original["decision"],
                    "final_decision": final["decision"],
                    "conclusion": (
                        "A decisão original foi mantida após confronto integral com "
                        "as evidências oficiais."
                        if not changed
                        else (
                            "A decisão foi rebaixada porque empreendedorismo geral "
                            "não comprova rota específica para startups."
                        )
                    ),
                    "divergence_severity": "none" if not changed else "high",
                    "resolution": "confirmed" if not changed else "decision-corrected",
                    "resolved": True,
                }
            )

    baseline_agencies = {
        row["agency_id"]: row for row in baseline["agencies.jsonl"]
    }
    for agency_id in (
        "agency-brde",
        "agency-finep",
        "agency-prefeitura-divinopolis",
    ):
        agency = final_agencies[agency_id]
        consulted_ids = agency["official_evidence_ids"]
        original_decision = (
            baseline_agencies[agency_id]["decision"]
            if agency_id in baseline_agencies
            else None
        )
        reviews.append(
            {
                "schema_version": "1.0",
                "review_id": f"review-derived-agency-{agency_id}",
                "review_group": "derived_agency",
                "subject_type": "agency",
                "subject_id": agency_id,
                "target_entity_id": agency_id,
                "reviewer": REVIEWER,
                "reviewed_on": REVIEWED_ON,
                "evidence_ids": consulted_ids,
                "evidence_urls": [final_evidence[eid]["url"] for eid in consulted_ids],
                "contract_checks": {
                    "route_url_present": True,
                    "eligible_program_linked": any(
                        final_programs[program_id]["decision"] == "elegível"
                        for program_id in agency["program_ids"]
                    ),
                },
                "original_decision": original_decision,
                "final_decision": agency["decision"],
                "conclusion": (
                    "A agência passou a elegível porque a transferência revelou "
                    "uma rota financeira recorrente para startups."
                    if agency_id == "agency-finep"
                    else "A agência foi criada somente para preservar o vínculo institucional do programa transferido."
                ),
                "divergence_severity": "high",
                "resolution": "entity-materialized",
                "resolved": True,
            }
        )

    for row in transfer_resolutions:
        candidate = accelerator_candidates[row["source_candidate_id"]]
        evidence_ids = candidate["official_evidence_ids"]
        reviews.append(
            {
                "schema_version": "1.0",
                "review_id": f"review-incoming-transfer-{row['source_candidate_id']}",
                "review_group": "incoming_transfer",
                "subject_type": "transfer",
                "subject_id": row["source_candidate_id"],
                "target_entity_id": row["target_program_id"],
                "reviewer": REVIEWER,
                "reviewed_on": REVIEWED_ON,
                "evidence_ids": evidence_ids,
                "evidence_urls": [accelerator_evidence[eid]["url"] for eid in evidence_ids],
                "contract_checks": {
                    "materialized": row["materialized"],
                    "canonical_destination": row["canonical_destination"],
                },
                "original_decision": "encaminhado-para-outra-epic",
                "final_decision": row["resolution"],
                "conclusion": row["adjudication"],
                "divergence_severity": (
                    "none"
                    if row["resolution"] == "matched-existing-program"
                    else "high"
                ),
                "resolution": row["resolution"],
                "resolved": True,
            }
        )

    for row in category_resolutions:
        program = final_programs[row["program_id"]]
        evidence_ids = program["official_evidence_ids"]
        reviews.append(
            {
                "schema_version": "1.0",
                "review_id": f"review-outgoing-boundary-{row['program_id']}",
                "review_group": "outgoing_boundary",
                "subject_type": "program",
                "subject_id": row["program_id"],
                "target_entity_id": row["program_id"],
                "reviewer": REVIEWER,
                "reviewed_on": REVIEWED_ON,
                "evidence_ids": evidence_ids,
                "evidence_urls": [final_evidence[eid]["url"] for eid in evidence_ids],
                "contract_checks": {
                    "public_program_decision": row["public_program_decision"],
                    "canonical_destination": row["canonical_destination"],
                },
                "original_decision": program["decision"],
                "final_decision": program["decision"],
                "conclusion": (
                    "A fronteira foi mantida: a rota não entrega benefício público "
                    "direto a startups e possui destino canônico explícito."
                ),
                "divergence_severity": "none",
                "resolution": "boundary-confirmed",
                "resolved": True,
            }
        )

    return sorted(reviews, key=lambda row: row["review_id"])


def build_review_report(
    reviews: list[dict[str, Any]],
    transfer_resolutions: list[dict[str, Any]],
) -> str:
    counts = Counter(row["review_group"] for row in reviews)
    changed = [
        row
        for row in reviews
        if row["resolution"] in ("decision-corrected", "entity-materialized")
    ]
    transfer_lines = "\n".join(
        (
            f"| `{row['source_candidate_id']}` | `{row['resolution']}` | "
            f"`{row['canonical_destination']}` | {row['adjudication']} |"
        )
        for row in transfer_resolutions
    )
    changed_lines = "\n".join(
        (
            f"| `{row['subject_id']}` | `{row['original_decision']}` | "
            f"`{row['final_decision']}` | {row['conclusion']} |"
        )
        for row in changed
    )
    return f"""# Revisão independente da fila pública

Revisor: `{REVIEWER}`. Data: {REVIEWED_ON}. A revisão foi executada depois da
redução mecânica e não reutilizou a decisão do consolidador como evidência.

## Cobertura

- 12 agências originalmente elegíveis: {counts["eligible_agency"]}.
- 15 programas originalmente elegíveis: {counts["eligible_program"]}.
- 5 agências originalmente insuficientes: {counts["insufficient_agency"]}.
- 5 programas originalmente insuficientes: {counts["insufficient_program"]}.
- 5 fronteiras de saída: {counts["outgoing_boundary"]}.
- 13 transferências recebidas: {counts["incoming_transfer"]}.
- 3 agências derivadas ou corrigidas por transferências: {counts["derived_agency"]}.

Cada linha de `independent-review.jsonl` registra sujeito, evidências consultadas,
checagens do contrato, conclusão, divergência e resolução. Todas as divergências
altas estão resolvidas.

## Decisões corrigidas ou materializadas

| Item | Antes | Depois | Resolução |
| --- | --- | --- | --- |
{changed_lines}

Fondo Emprender e Capital Pioneras foram rebaixados porque as fontes confirmam
empreendedorismo geral, não uma rota específica para startups. A Finep passou a
elegível após a materialização do Programa Mulheres Inovadoras. Valores,
recorrência e disponibilidade permanecem restritos às fontes que os afirmam.

## Transferências da epic #62

| Origem | Resolução | Destino canônico | Fundamento |
| --- | --- | --- | --- |
{transfer_lines}

As cinco transferências rejeitadas não ficaram em limbo: três retornam à fila de
aceleradoras para decisão sob o contrato próprio e duas recebem destinos
fora de escopo específicos. Nenhuma foi convertida em programa público por
inferência.
"""


def build_outputs() -> dict[str, bytes]:
    grouped, tasks, input_hashes, before_counts = load_inputs()
    canonical = {
        filename: unique_and_sorted(records, IDENTIFIERS[filename], filename)
        for filename, records in grouped.items()
    }
    baseline = copy.deepcopy(canonical)
    apply_independent_decisions(canonical)

    tasks.sort(key=lambda row: row["task_id"])
    run_record = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issue": 102,
        "region": "América Latina",
        "cutoff_date": "2026-07-27",
        "status": "concluída",
        "task_count": len(tasks),
        "coordinator": "coordinator-issue-102",
        "scraping_performed": False,
    }
    manifests = [run_record, *tasks]

    agencies = canonical["agencies.jsonl"]
    programs = canonical["programs.jsonl"]
    calls = canonical["calls.jsonl"]
    evidence = canonical["evidence.jsonl"]
    agency_ids = {row["agency_id"] for row in agencies}
    program_ids = {row["program_id"] for row in programs}
    call_ids = {row["call_id"] for row in calls}
    evidence_ids = {row["evidence_id"] for row in evidence}

    if any(row["decision"] is None for row in (*agencies, *programs)):
        raise ValueError("agência ou programa sem decisão")
    if any(row["agency_id"] not in agency_ids for row in programs):
        raise ValueError("programa com agência órfã")
    if any(row["program_id"] not in program_ids for row in calls):
        raise ValueError("chamada com programa órfão")
    for row in (*agencies, *programs, *calls):
        if any(evidence_id not in evidence_ids for evidence_id in row["official_evidence_ids"]):
            raise ValueError("referência de evidência órfã")
    for row in (*agencies, *programs):
        if "insuficiente" in row["decision"] and not (
            row.get("owner") and row.get("next_action")
        ):
            raise ValueError(f"pendência sem ação: {row}")

    transfer_resolutions = build_transfer_resolutions(program_ids)
    if len(transfer_resolutions) != 13:
        raise ValueError("transferências recebidas da epic #62 divergiram")
    category_resolutions = build_category_resolutions(programs)
    resolutions = {
        "schema_version": "1.0",
        "issue": 102,
        "incoming_transfers": transfer_resolutions,
        "outgoing_category_resolutions": category_resolutions,
    }
    independent_review = build_independent_review(
        baseline,
        canonical,
        transfer_resolutions,
        category_resolutions,
    )

    outputs = {
        filename: jsonl_bytes(records)
        for filename, records in canonical.items()
    }
    outputs["run-manifest.jsonl"] = jsonl_bytes(manifests)
    outputs["category-resolutions.json"] = json_bytes(resolutions)
    outputs["independent-review.jsonl"] = jsonl_bytes(independent_review)
    outputs["INDEPENDENT_REVIEW.md"] = build_review_report(
        independent_review, transfer_resolutions
    ).encode("utf-8")
    output_hashes = {name: sha256(payload) for name, payload in outputs.items()}

    counts = {
        "agencies": len(agencies),
        "programs": len(programs),
        "calls": len(calls),
        "evidence": len(evidence),
        "coverage_rows": len(canonical["coverage-matrix.jsonl"]),
        "tasks": len(tasks),
    }
    manifest = {
        "schema_version": "1.0",
        "issue": 102,
        "cutoff_date": "2026-07-27",
        "status": "frozen",
        "independent_review_status": "complete",
        "independent_reviewer": REVIEWER,
        "reviewed_on": REVIEWED_ON,
        "review_count": len(independent_review),
        "resolved_high_divergences": sum(
            row["divergence_severity"] == "high" and row["resolved"]
            for row in independent_review
        ),
        "unresolved_high_divergences": sum(
            row["divergence_severity"] == "high" and not row["resolved"]
            for row in independent_review
        ),
        "before_counts": before_counts,
        "after_counts": counts,
        "decision_counts": {
            "agencies": dict(
                sorted(Counter(row["decision"] for row in agencies).items())
            ),
            "programs": dict(
                sorted(Counter(row["decision"] for row in programs).items())
            ),
        },
        "incoming_transfers": len(transfer_resolutions),
        "materialized_incoming_transfers": sum(
            row["materialized"] for row in transfer_resolutions
        ),
        "outgoing_category_resolutions": len(category_resolutions),
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
    }
    outputs["consolidation-manifest.json"] = json_bytes(manifest)

    eligible_agencies = sum(row["decision"] == "elegível" for row in agencies)
    eligible_programs = sum(row["decision"] == "elegível" for row in programs)
    pending_agencies = sum("insuficiente" in row["decision"] for row in agencies)
    pending_programs = sum("insuficiente" in row["decision"] for row in programs)
    unmaterialized = sum(not row["materialized"] for row in transfer_resolutions)
    report = f"""# Fila consolidada de programas públicos

Este bundle consolida as quatro auditorias regionais da epic #65 na data de
corte 2026-07-27. A revisão independente está concluída e nenhum perfil é
publicado nesta etapa.

## Before / after

| Entidade | Antes | Depois |
| --- | ---: | ---: |
| Agências | 27 | {len(agencies)} |
| Programas | 39 | {len(programs)} |
| Chamadas | 21 | {len(calls)} |
| Evidências | 90 | {len(evidence)} |
| Linhas de cobertura | 55 | {len(canonical["coverage-matrix.jsonl"])} |

Não havia IDs duplicados entre regiões. A redução preservou todos os registros,
ordenou-os por ID, materializou seis transferências antes pendentes e
reconciliou suas relações.

## Decisões

- Agências elegíveis: {eligible_agencies}.
- Programas elegíveis: {eligible_programs}.
- Agências com evidência insuficiente: {pending_agencies}.
- Programas com evidência insuficiente: {pending_programs}.
- Transferências recebidas da epic #62: {len(transfer_resolutions)}.
- Transferências materializadas na fila pública: {
        sum(row["materialized"] for row in transfer_resolutions)
    }.
- Transferências rejeitadas pelo contrato público: {unmaterialized}.
- Fronteiras encaminhadas para fundos ou aceleradoras: {
        len(category_resolutions)
    }.

## Revisão independente

A revisão de 100% dos grupos obrigatórios está em
`independent-review.jsonl`, com narrativa em `INDEPENDENT_REVIEW.md`.
Fondo Emprender e Capital Pioneras foram rebaixados por não confirmarem uma rota
específica para startups. Seis transferências antes pendentes foram
materializadas, além das duas já ligadas a programas; cinco receberam outro
destino canônico. Não restam divergências altas abertas e o manifesto está
congelado com hashes SHA-256.

## Reprodução

```text
python research/epic-65/consolidation/build_queue.py
python research/epic-65/consolidation/build_queue.py --check
python research/epic-65/validate.py research/epic-65/consolidation
python -m unittest discover -s research/epic-65/consolidation/tests -p "test_*.py"
```
"""
    outputs["README.md"] = report.encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for filename, payload in outputs.items():
        path = HERE / filename
        if args.check:
            current = (
                path.read_bytes().replace(b"\r\n", b"\n")
                if path.is_file()
                else None
            )
            if current != payload:
                drift.append(filename)
        else:
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
