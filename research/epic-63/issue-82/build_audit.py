"""Materializa os shards reproduzíveis da auditoria brasileira da issue #82."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CUTOFF = "2026-07-27"
RUN_ID = "run-angels-brazil-2026"
UNKNOWN = [{"name": "não divulgado", "actor_type": "não divulgado"}]


def dump(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for record in sorted(records, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True))
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def actor(name: str, actor_type: str) -> list[dict]:
    return [{"name": name, "actor_type": actor_type}]


def source(
    slug: str,
    name: str,
    url: str,
    category: str,
    geography: str,
    scope: str,
    *,
    result: str = "concluída",
    reason: str | None = None,
    next_action: str | None = None,
    notes: str | None = None,
) -> dict:
    pending = result != "concluída"
    return {
        "schema_version": "1.0",
        "source_id": f"src-br-{slug}",
        "issue": 82,
        "source": name,
        "initial_url": url,
        "source_category": category,
        "geography": geography,
        "scope_walked": scope,
        "accessed_on": CUTOFF,
        "result": result,
        "reason": reason,
        "owner": f"worker-{slug}" if pending else None,
        "next_action": next_action,
        "notes": notes,
    }


def candidate(
    slug: str,
    name: str,
    domain: str | None,
    site: str | None,
    entity_type: str,
    source_slug: str,
    decision: str,
    reason: str | None,
    *,
    geography: list[str] | None = None,
    evidence_slugs: list[str] | None = None,
    selection: list[dict] | None = None,
    decision_actors: list[dict] | None = None,
    capital: list[dict] | None = None,
    recurring: bool | None = None,
    activity_status: str = "não confirmada",
    activity_date: str | None = None,
    external_access: str = "não confirmado",
    application_route: str | None = None,
    canonical_network_id: str | None = None,
    already_listed: bool = False,
    canonical_profile: str | None = None,
    owner: str | None = None,
    next_action: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "network_id": f"ang-{slug}",
        "name": name,
        "canonical_domain": domain,
        "official_site": site,
        "entity_type": entity_type,
        "base_country": "Brazil",
        "declared_geography": geography or ["Brazil"],
        "aliases": [],
        "chapter_identity": "não aplicável",
        "parent_network_id": None,
        "canonical_network_id": canonical_network_id,
        "chapter_autonomy": {
            "selection": None,
            "decision": None,
            "geography": None,
            "recent_activity": None,
        },
        "discovery_source_ids": [f"src-br-{source_slug}"],
        "official_evidence_ids": [f"ev-br-{item}" for item in (evidence_slugs or [])],
        "discovered_on": CUTOFF,
        "cutoff_date": CUTOFF,
        "selection_actors": selection or UNKNOWN,
        "decision_actors": decision_actors or UNKNOWN,
        "capital_actors": capital or UNKNOWN,
        "recurring_selection": recurring,
        "activity_status": activity_status,
        "activity_evidence_date": activity_date,
        "external_access": external_access,
        "application_route": application_route,
        "already_listed": already_listed,
        "canonical_profile": canonical_profile,
        "status": "decidido",
        "decision": decision,
        "reason": reason,
        "owner": owner,
        "next_action": next_action,
    }


def evidence(
    slug: str,
    network_slug: str,
    url: str,
    title: str,
    publisher: str,
    claims: list[str],
    locator: str,
    summary: str,
    *,
    published_on: str | None = None,
    findings: dict[str, str] | None = None,
) -> dict:
    findings = findings or {}
    return {
        "schema_version": "1.0",
        "evidence_id": f"ev-br-{slug}",
        "network_id": f"ang-{network_slug}",
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_type": "oficial",
        "published_on": published_on,
        "accessed_on": CUTOFF,
        "claims": [
            {"field": field, "finding": findings.get(field, "confirmado")}
            for field in claims
        ],
        "locator": locator,
        "summary": summary,
    }


SOURCES = [
    source("gavea", "Gávea Angels", "https://gaveaangels.org/", "site oficial", "Sudeste do Brasil", "Página institucional, tese, processo de seleção e portfólio."),
    source("curitiba", "Curitiba Angels", "https://www.curitibaangels.com.br/", "site oficial", "Sul do Brasil", "Página institucional, processo em quatro etapas, portfólio e conteúdo datado."),
    source(
        "floripa",
        "Floripa Angels",
        "https://floripaangels.com/",
        "site oficial",
        "Sul do Brasil",
        "Tentativa direta ao domínio planejado.",
        result="indisponível",
        reason="O domínio não resolveu no DNS na data de corte.",
        next_action="Revalidar domínio, redirects históricos e registro institucional na revisão da issue #86.",
    ),
    source("poli", "Poli Angels", "https://poliangels.com.br/", "universidade", "Brasil", "Página institucional, processo, FAQ, portfólio e rota de candidatura."),
    source("mit", "MIT Alumni Angels Brazil", "https://brazil.alumcommunity.mit.edu/page/mit-alumni-angels", "universidade", "Brasil", "Página oficial do alumni club, processo e calendário publicado."),
    source("sororite", "Rede Sororitê", "https://www.sororite.com.br/rede-sororite", "perfil institucional", "Brasil", "Página da rede, FAQ, atores de capital e acesso de investidoras."),
    source("wim", "WIM Angels", "https://wimangels.com.br/", "perfil institucional", "Brasil", "Página institucional, números, tese e rotas para founders e investidoras."),
    source("mia", "Mulheres Investidoras Anjo", "https://www.mulheresinvestidoras.net/quem-somos.html", "perfil institucional", "Brasil", "História institucional e vínculo canônico com Anjos do Brasil."),
    source("puc", "PUC angels", "https://pucangels.org/iniciativas/programa-investimento", "universidade", "Brasil", "Programa contínuo, critérios, avaliação, atores e rota para founders."),
    source("bossa", "Bossa Invest", "https://bossainvest.com/", "busca", "Brasil", "Identidade institucional, tese, processo e fronteira com venture capital."),
    source("anjos-brasil", "Anjos do Brasil", "https://anjosdobrasil.net/para-investidores/", "associação", "Brasil", "Fonte de descoberta e controle de cobertura; baseline #81 não reprocessado."),
    source("relatorio", "Relatório nacional Anjos do Brasil 2023", "https://www2.anjosdobrasil.net/wp-content/uploads/2023/06/Evolucao-do-Investimento-Anjo-no-Brasil-2023-2022-Anjos-do-Brasil-1.pdf", "diretório", "Brasil", "Relatório nacional usado somente para descoberta e comparação de cobertura."),
]


CANDIDATES = [
    candidate(
        "gaveaangels-org",
        "Gávea Angels",
        "gaveaangels.org",
        "https://gaveaangels.org/",
        "rede",
        "gavea",
        "evidência-insuficiente",
        "A fonte confirma rede, seleção, decisão e capital, mas não fornece data oficial precisa de atividade de investimento dentro da janela de 24 meses.",
        evidence_slugs=["gavea-model"],
        selection=actor("Equipe da Gávea Angels", "equipe da rede"),
        decision_actors=actor("Associados da Gávea Angels", "membros individuais"),
        capital=actor("Associados da Gávea Angels", "membros individuais"),
        recurring=True,
        external_access="aberto",
        application_route="https://gaveaangels.org/tese-de-investimento/",
        owner="review-angels-86",
        next_action="Localizar resultado, pitch ou investimento oficial com data verificável posterior a 27 de julho de 2024.",
    ),
    candidate(
        "curitibaangels-com-br",
        "Curitiba Angels",
        "curitibaangels.com.br",
        "https://www.curitibaangels.com.br/",
        "rede",
        "curitiba",
        "elegível",
        None,
        evidence_slugs=["curitiba-model", "curitiba-activity"],
        selection=actor("Equipe da Curitiba Angels", "equipe da rede"),
        decision_actors=actor("Investidores da Curitiba Angels", "membros individuais"),
        capital=actor("Investidores da Curitiba Angels", "membros individuais"),
        recurring=True,
        activity_status="confirmada-recente",
        activity_date="2024-12-06",
        external_access="aberto",
        application_route="https://www.curitibaangels.com.br/",
    ),
    candidate(
        "floripaangels-com",
        "Floripa Angels",
        "floripaangels.com",
        "https://floripaangels.com/",
        "rede",
        "floripa",
        "evidência-insuficiente",
        "O domínio planejado não resolveu; não foi possível confirmar identidade atual, atividade recente ou acesso externo em fonte oficial.",
        owner="review-angels-86",
        next_action="Revalidar o domínio e procurar uma migração institucional oficial sem contornar bloqueios.",
    ),
    candidate(
        "poliangels-com-br",
        "Poli Angels",
        "poliangels.com.br",
        "https://poliangels.com.br/",
        "alumni network",
        "poli",
        "evidência-insuficiente",
        "A fonte confirma processo recorrente, acesso e capital individual, mas não publica data recente verificável para um round, pitch ou investimento.",
        evidence_slugs=["poli-model"],
        selection=actor("Comitê de Curadoria da Poli Angels", "comitê"),
        decision_actors=actor("Associados da Poli Angels", "membros individuais"),
        capital=actor("Associados da Poli Angels", "membros individuais"),
        recurring=True,
        external_access="aberto",
        application_route="https://poliangels.com.br/",
        owner="review-angels-86",
        next_action="Obter fonte oficial datada de atividade posterior a 27 de julho de 2024.",
    ),
    candidate(
        "brazil-alumcommunity-mit-edu",
        "MIT Alumni Angels Brazil",
        "brazil.alumcommunity.mit.edu",
        "https://brazil.alumcommunity.mit.edu/page/mit-alumni-angels",
        "alumni network",
        "mit",
        "inativo",
        "A página oficial mantém processo e candidatura, mas o último evento datado exibido é de 26 de abril de 2023, fora da janela de atividade recente.",
        evidence_slugs=["mit-model"],
        selection=actor("MIT Alumni Angels Brazil", "equipe da rede"),
        decision_actors=actor("Membros individuais", "membros individuais"),
        capital=actor("Membros individuais", "membros individuais"),
        recurring=True,
        activity_status="desatualizada",
        activity_date="2023-04-26",
        external_access="aberto",
        application_route="https://brazil.alumcommunity.mit.edu/page/mit-alumni-angels",
    ),
    candidate(
        "sororite-com-br",
        "Rede Sororitê",
        "sororite.com.br",
        "https://www.sororite.com.br/rede-sororite",
        "rede",
        "sororite",
        "evidência-insuficiente",
        "A fonte separa a rede do fundo e confirma capital individual, mas não publica atividade recente com data verificável para a rede-anjo.",
        evidence_slugs=["sororite-model"],
        selection=actor("Experts da Rede Sororitê", "equipe da rede"),
        decision_actors=actor("Investidoras membros", "membros individuais"),
        capital=actor("Investidoras membros", "membros individuais"),
        recurring=True,
        external_access="não confirmado",
        owner="review-angels-86",
        next_action="Confirmar rota pública para startups da rede-anjo e atividade oficial datada dentro da janela.",
    ),
    candidate(
        "wimangels-com-br",
        "WIM Angels",
        "wimangels.com.br",
        "https://wimangels.com.br/",
        "rede",
        "wim",
        "evidência-insuficiente",
        "A página confirma rede, startups avaliadas e rotas de contato, mas não atribui data verificável à atividade exibida.",
        evidence_slugs=["wim-model"],
        recurring=True,
        external_access="aberto",
        application_route="https://wimangels.com.br/",
        owner="review-angels-86",
        next_action="Localizar investimento, seleção ou pitch oficial datado dentro da janela de 24 meses.",
    ),
    candidate(
        "mulheresinvestidoras-net",
        "Mulheres Investidoras Anjo",
        "mulheresinvestidoras.net",
        "https://www.mulheresinvestidoras.net/quem-somos.html",
        "rede",
        "mia",
        "duplicado",
        "A fonte oficial afirma que o MIA está integrado à rede Anjos do Brasil; não há autonomia publicável separada.",
        evidence_slugs=["mia-alias"],
        canonical_network_id=None,
        already_listed=True,
        canonical_profile="ecosystem/angel-networks/brazil/anjos-do-brasil.md",
    ),
    candidate(
        "pucangels-org",
        "PUC angels",
        "pucangels.org",
        "https://pucangels.org/",
        "alumni network",
        "puc",
        "elegível",
        None,
        evidence_slugs=["puc-model", "puc-activity"],
        selection=actor("Equipe de avaliação da PUC angels", "equipe da rede"),
        decision_actors=actor("Investidores anjo e parceiros de capital", "membros individuais"),
        capital=actor("Investidores anjo e parceiros de capital", "membros individuais"),
        recurring=True,
        activity_status="confirmada-recente",
        activity_date="2025-09-22",
        external_access="aberto",
        application_route="https://pucangels.org/iniciativas/programa-investimento",
    ),
    candidate(
        "bossainvest-com",
        "Bossa Invest",
        "bossainvest.com",
        "https://bossainvest.com/",
        "fundo",
        "bossa",
        "encaminhado-para-funds",
        "A organização se apresenta como venture capital, possui tese e equipe própria de análise e investe capital sob gestão.",
        evidence_slugs=["bossa-boundary"],
        recurring=True,
        activity_status="não confirmada",
        activity_date=None,
        external_access="aberto",
        application_route="https://bossainvest.com/receber-investimento/",
        canonical_profile="funds/brazil/bossa-invest-bossanova.md",
    ),
]


EVIDENCE = [
    evidence("gavea-model", "gaveaangels-org", "https://gaveaangels.org/investidas/", "Investidas", "Gávea Angels", ["categoria", "seleção", "decisão", "capital", "acesso externo", "rota de aplicação"], "Apresentação das investidas e tese", "A associação descreve seleção e análise próprias, rodada de investimento, decisão sem obrigatoriedade e capital aportado pelos associados."),
    evidence("curitiba-model", "curitibaangels-com-br", "https://www.curitibaangels.com.br/", "Curitiba Angels", "Curitiba Angels", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Seções Investimento anjo e Etapas", "A página identifica a rede, abre cadastro de startups e separa análise, pitch, interesse dos investidores e aporte dos anjos."),
    evidence("curitiba-activity", "curitibaangels-com-br", "https://www.curitibaangels.com.br/tendencias-e-panorama-do-venture-capital-para-2025-insights-do-nosso-evento-para-investidores-e-startups/", "Tendências e Panorama do Venture Capital para 2025", "Curitiba Angels", ["atividade"], "Evento e retrospectiva de Pitch Nights", "A rede relata três Pitch Nights em 2024 e a última oportunidade do ano em 5 de dezembro.", published_on="2024-12-06"),
    evidence("poli-model", "poliangels-com-br", "https://poliangels.com.br/institucional/perguntas-frequentes", "Perguntas frequentes", "Poli Angels", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Processo de seleção e investimento", "A associação recebe startups via GUST, realiza rounds recorrentes, usa comitê de curadoria e deixa decisão e aporte a cada associado."),
    evidence("mit-model", "brazil-alumcommunity-mit-edu", "https://brazil.alumcommunity.mit.edu/page/mit-alumni-angels", "MIT Alumni Angels", "MIT & MIT Sloan Club of Brazil", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação", "atividade"], "Quick Facts, Entrepreneurs e Upcoming Events", "A página descreve pitches contínuos, candidatura externa e decisões individuais, mas o último evento datado exibido ocorreu em 26 de abril de 2023.", published_on="2023-04-26"),
    evidence("sororite-model", "sororite-com-br", "https://www.sororite.com.br/rede-sororite", "Rede Sororitê", "Sororitê", ["categoria", "seleção", "decisão", "capital", "recorrência"], "Descrição e FAQ da rede", "A página descreve uma rede de investidoras, avaliações de oportunidades e aportes diretos decididos e realizados individualmente pelas membros."),
    evidence("wim-model", "wimangels-com-br", "https://wimangels.com.br/", "WIM Angels", "WIM Angels", ["categoria", "seleção", "capital", "acesso externo", "rota de aplicação"], "Sobre, números e chamadas de ação", "A página se apresenta como rede de mulheres investidoras, informa startups avaliadas e investidas e oferece rota para quem busca investimento, sem data da atividade."),
    evidence("mia-alias", "mulheresinvestidoras-net", "https://www.mulheresinvestidoras.net/quem-somos.html", "Quem somos", "Mulheres Investidoras Anjo", ["categoria"], "Seção Hoje", "A fonte oficial declara que o MIA está integrado à rede de investidores da Anjos do Brasil."),
    evidence("puc-model", "pucangels-org", "https://pucangels.org/iniciativas/programa-investimento", "Programa Investimento", "PUC angels", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Programa e fluxo de avaliação", "A associação recebe inscrições continuamente, avalia internamente e conecta aprovados a investidores anjo que apresentam propostas de investimento."),
    evidence("puc-activity", "pucangels-org", "https://pucangels.org/iniciativas/Destaques", "Destaques PUC angels", "PUC angels", ["atividade"], "Matchmaking de Investimento", "A página registra lançamento em 22 de setembro de 2025 e mantém o programa de matchmaking entre projetos e investidores.", published_on="2025-09-22"),
    evidence("bossa-boundary", "bossainvest-com", "https://bossainvest.com/quem-somos/", "Quem somos", "Bossa Invest", ["categoria", "seleção", "capital", "acesso externo", "rota de aplicação"], "Identidade e especialidade institucional", "A organização se define como empresa de venture capital com tese, portfólio e processo de análise de startups, caracterizando destino em funds/."),
]


COVERAGE = [
    {"schema_version":"1.0","coverage_id":"cov-br-associacao","issue":82,"geography":"Brasil","source_category":"associação","source_ids":["src-br-anjos-brasil"],"status":"concluída","candidate_count":0,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-br-sudeste-oficial","issue":82,"geography":"Sudeste do Brasil","source_category":"site oficial","source_ids":["src-br-gavea"],"status":"concluída","candidate_count":1,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-br-sul-oficial","issue":82,"geography":"Sul do Brasil","source_category":"site oficial","source_ids":["src-br-curitiba","src-br-floripa"],"status":"parcial","candidate_count":2,"reason":"Floripa Angels não resolveu no DNS; Curitiba Angels foi concluída.","owner":"brazil-angels-coordinator","next_action":"Revalidar o domínio de Floripa Angels na consolidação #86."},
    {"schema_version":"1.0","coverage_id":"cov-br-alumni","issue":82,"geography":"Brasil","source_category":"universidade","source_ids":["src-br-mit","src-br-poli","src-br-puc"],"status":"concluída","candidate_count":3,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-br-mulheres","issue":82,"geography":"Brasil","source_category":"perfil institucional","source_ids":["src-br-mia","src-br-sororite","src-br-wim"],"status":"concluída","candidate_count":3,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-br-diretorio","issue":82,"geography":"Brasil","source_category":"diretório","source_ids":["src-br-relatorio"],"status":"concluída","candidate_count":0,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-br-fronteira-fundos","issue":82,"geography":"Brasil","source_category":"busca","source_ids":["src-br-bossa"],"status":"concluída","candidate_count":1,"reason":None,"owner":"brazil-angels-coordinator","next_action":None},
]


def main() -> None:
    shards = ROOT / "shards"
    if shards.exists():
        shutil.rmtree(shards)

    candidates_by_source = {
        record["discovery_source_ids"][0].removeprefix("src-br-"): record
        for record in CANDIDATES
    }
    evidence_by_network: dict[str, list[dict]] = {}
    for record in EVIDENCE:
        evidence_by_network.setdefault(record["network_id"], []).append(record)

    task_rows = []
    for record in SOURCES:
        slug = record["source_id"].removeprefix("src-br-")
        worker = f"worker-{slug}"
        worker_dir = shards / worker
        dump(worker_dir / "source-inventory.jsonl", [record])
        related = candidates_by_source.get(slug)
        if related:
            dump(worker_dir / "candidates.jsonl", [related])
            matching_evidence = evidence_by_network.get(related["network_id"], [])
            if matching_evidence:
                dump(worker_dir / "evidence.jsonl", matching_evidence)
        task_rows.append({
            "schema_version": "1.0",
            "record_type": "task",
            "run_id": RUN_ID,
            "task_id": f"task-angels-br-{slug}",
            "issue": 82,
            "url": record["initial_url"],
            "task_type": "identidade" if slug == "bossa" else ("descoberta" if slug in {"anjos-brasil", "relatorio"} else "evidência"),
            "partition": slug,
            "shard_path": f"research/epic-63/issue-82/shards/{worker}/",
            "priority": 2 if slug in {"anjos-brasil", "relatorio"} else 1,
            "status": "blocked" if record["result"] == "indisponível" else "done",
            "owner": worker,
            "next_action": record["next_action"],
            "last_error": record["reason"] if record["result"] == "indisponível" else None,
        })

    coordinator = shards / "worker-coordinator"
    dump(coordinator / "coverage-matrix.jsonl", COVERAGE)
    run = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issues": [82],
        "contract_issue": 80,
        "cutoff_date": CUTOFF,
        "created_on": CUTOFF,
        "status": "concluída",
        "task_count": len(task_rows) + 1,
        "scraping_performed": True,
        "max_global_requests": 8,
        "max_requests_per_domain": 2,
        "max_browsers": 2,
        "owner": "brazil-angels-coordinator",
        "notes": "Doze fontes em shards exclusivos, uma indisponibilidade preservada e zero perfis publicados.",
    }
    coordinator_task = {
        "schema_version": "1.0",
        "record_type": "task",
        "run_id": RUN_ID,
        "task_id": "task-angels-br-consolidation",
        "issue": 82,
        "url": "https://github.com/djairofilho/awesome-latam-vc/issues/82",
        "task_type": "revisão",
        "partition": "coordinator",
        "shard_path": "research/epic-63/issue-82/shards/worker-coordinator/",
        "priority": 1,
        "status": "done",
        "owner": "brazil-angels-coordinator",
        "next_action": None,
        "last_error": None,
    }
    dump(coordinator / "run-manifest.jsonl", [run, *task_rows, coordinator_task])


if __name__ == "__main__":
    main()
