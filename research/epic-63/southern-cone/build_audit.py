"""Materializa e reduz a auditoria reproduzível da issue #85."""

from __future__ import annotations

from pathlib import Path
import sys


REPOSITORY = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY / "tools" / "research"))

from shards import reduce_shards, write_shard  # noqa: E402


ROOT = Path(__file__).resolve().parent
CUTOFF = "2026-07-27"
RUN_ID = "run-issue-85-southern-cone"
UNKNOWN = [{"name": "não divulgado", "actor_type": "não divulgado"}]


def actor(name: str, actor_type: str) -> list[dict]:
    return [{"name": name, "actor_type": actor_type}]


def source(
    source_id: str,
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
        "source_id": source_id,
        "issue": 85,
        "source": name,
        "initial_url": url,
        "source_category": category,
        "geography": geography,
        "scope_walked": scope,
        "accessed_on": CUTOFF,
        "result": result,
        "reason": reason,
        "owner": source_id.replace("src-", "worker-") if pending else None,
        "next_action": next_action,
        "notes": notes,
    }


def candidate(
    network_id: str,
    name: str,
    domain: str,
    site: str,
    entity_type: str,
    country: str,
    source_ids: list[str],
    decision: str,
    reason: str | None,
    *,
    evidence_ids: list[str],
    geography: list[str] | None = None,
    aliases: list[dict] | None = None,
    chapter_identity: str = "não aplicável",
    parent_network_id: str | None = None,
    canonical_network_id: str | None = None,
    chapter_autonomy: dict | None = None,
    selection: list[dict] | None = None,
    decision_actors: list[dict] | None = None,
    capital: list[dict] | None = None,
    recurring: bool | None = None,
    activity_status: str = "não confirmada",
    activity_date: str | None = None,
    external_access: str = "não confirmado",
    application_route: str | None = None,
    canonical_profile: str | None = None,
    owner: str | None = None,
    next_action: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "network_id": network_id,
        "name": name,
        "canonical_domain": domain,
        "official_site": site,
        "entity_type": entity_type,
        "base_country": country,
        "declared_geography": geography or [country],
        "aliases": aliases or [],
        "chapter_identity": chapter_identity,
        "parent_network_id": parent_network_id,
        "canonical_network_id": canonical_network_id,
        "chapter_autonomy": chapter_autonomy
        or {
            "selection": None,
            "decision": None,
            "geography": None,
            "recent_activity": None,
        },
        "discovery_source_ids": source_ids,
        "official_evidence_ids": evidence_ids,
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
        "already_listed": False,
        "canonical_profile": canonical_profile,
        "status": "decidido",
        "decision": decision,
        "reason": reason,
        "owner": owner,
        "next_action": next_action,
    }


def evidence(
    evidence_id: str,
    network_id: str,
    url: str,
    title: str,
    publisher: str,
    claims: list[str],
    locator: str,
    summary: str,
    *,
    published_on: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "network_id": network_id,
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_type": "oficial",
        "published_on": published_on,
        "accessed_on": CUTOFF,
        "claims": [{"field": field, "finding": "confirmado"} for field in claims],
        "locator": locator,
        "summary": summary,
    }


SOURCES_BY_COUNTRY = {
    "argentina": [
        source("src-argentina-arcap", "ARCAP — diretório de membros", "https://arcap.org/directorio-fondos-inversion-argentina/", "associação", "Argentina", "Diretório nacional percorrido como controle de descoberta e da fronteira com gestores de fundos."),
        source("src-argentina-bac", "Business Angels Club", "https://businessangelsclub.org/para-fundadores.html", "site oficial", "Argentina", "Identidade, seleção, decisão, capital, recorrência e candidatura de startups."),
        source("src-argentina-bac-linkedin", "Business Angels Club — perfil institucional", "https://ar.linkedin.com/company/business-angels-club-emprendeiae", "perfil institucional", "Argentina", "Publicações institucionais e anúncio datado do capítulo Mar del Plata."),
        source("src-argentina-crea", "CREA — reporte institucional", "https://reporte.crea.org.ar/", "site oficial", "Argentina", "Programa do Club de Inversores Ángeles CREA e referências ao ciclo de análise de oportunidades."),
    ],
    "chile": [
        source("src-chile-acvc", "ACVC — membros", "https://acvc.cl/miembros/socios/", "associação", "Chile", "Diretório nacional percorrido como controle de descoberta e fronteira com fundos, CVCs e family offices."),
        source("src-chile-red-uc", "Red Ángeles do Centro de Innovación UC", "https://centrodeinnovacion.uc.cl/red-angeles/", "universidade", "Chile", "Programa, bases, convocatória, atores e acesso externo."),
        source("src-chile-austral", "Austral Angels", "https://www.australangels.com/", "site oficial", "Chile", "Identidade, processo, rotas de cadastro e sinais de atividade."),
        source("src-chile-chileglobal", "ChileGlobal Angels", "https://chileglobalventures.cl/angels/", "site oficial", "Chile", "Identidade, processo, membros, aportes e candidatura."),
        source("src-chile-ain", "Red Chilena de Inversiones", "https://www.angelinvestmentnetwork.cl/nuestras-tarifas", "site oficial", "Chile", "Modelo comercial de publicação de propostas e contato em plataforma."),
    ],
    "paraguai": [
        source("src-paraguai-parcapy", "PARCAPY", "https://parcapy.org/", "associação", "Paraguai", "Associação nacional e referências institucionais a investimento-anjo."),
        source("src-paraguai-riap", "RIAP — perfil institucional", "https://py.linkedin.com/company/redangelpy/", "perfil institucional", "Paraguai", "Identidade, parceria, portfólio e publicações atuais da rede."),
        source("src-paraguai-dinapi", "DINAPI — InfoDINAPI outubro de 2025", "https://www.dinapi.gov.py/portal/v3/assets/biblioteca/documentos/Infodinapi-Octubre-2025.pdf", "notícia", "Paraguai", "Participação institucional da RIAP na mesa nacional de inovação."),
    ],
    "uruguai": [
        source("src-uruguai-urucap", "URUCAP", "https://www.urucap.org/", "associação", "Uruguai", "Associação nacional e controle da fronteira com gestores e iniciativas de formação de anjos."),
        source("src-uruguai-apep", "Uruguay XXI — Red de Inversores APEP", "https://www.uruguayxxi.gub.uy/es/eventos/articulo/suma-tu-startup-a-la-red-de-inversores-apep/", "notícia", "Uruguai", "Convocatória, seleção pública, países participantes e data de atividade."),
        source("src-uruguai-piso40", "WTC Montevideo — Club de Ejecutivos Piso 40", "https://www.wtc.uy/html/servicios", "site oficial", "Uruguai", "Identidade institucional e descrição da rede de investidores-anjo."),
        source("src-uruguai-ain", "Red Uruguaya de Inversiones", "https://www.angelinvestmentnetwork.uy/emprendedores", "site oficial", "Uruguai", "Modelo de plataforma, publicação de propostas e contato com investidores."),
    ],
}


CANDIDATES_BY_COUNTRY = {
    "argentina": [
        candidate(
            "ang-businessangelsclub-org", "Business Angels Club EmprendeIAE", "businessangelsclub.org", "https://businessangelsclub.org/", "clube", "Argentina",
            ["src-argentina-bac", "src-argentina-bac-linkedin"], "elegível", None,
            evidence_ids=["ev-argentina-bac-model", "ev-argentina-bac-activity"],
            geography=["Argentina", "América Latina"], aliases=[{"name": "BAC", "alias_type": "sigla"}, {"name": "Business Angels Club", "alias_type": "nome"}],
            selection=actor("Equipe e comitê do Business Angels Club", "comitê"),
            decision_actors=actor("Sócios participantes do Business Angels Club", "membros individuais"),
            capital=[{"name": "Sócios participantes do Business Angels Club", "actor_type": "membros individuais"}, {"name": "Veículo único da operação", "actor_type": "veículo agrupado"}],
            recurring=True, activity_status="confirmada-recente", activity_date="2026-07-09", external_access="explícito-américa-latina",
            application_route="https://businessangelsclub.org/para-fundadores.html",
        ),
        candidate(
            "ang-businessangelsclub-org--mar-del-plata", "Business Angels Club Mar del Plata", "businessangelsclub.org", "https://businessangelsclub.org/", "capítulo", "Argentina",
            ["src-argentina-bac-linkedin"], "duplicado", "A fonte oficial o apresenta como primeiro capítulo regional do BAC e não demonstra autonomia própria de seleção, decisão, capital ou atividade.",
            evidence_ids=["ev-argentina-bac-mar-del-plata"], geography=["Mar del Plata", "Argentina"], aliases=[{"name": "BAC Mar del Plata", "alias_type": "capítulo"}],
            chapter_identity="alias", parent_network_id="ang-businessangelsclub-org", canonical_network_id="ang-businessangelsclub-org",
            chapter_autonomy={"selection": False, "decision": False, "geography": True, "recent_activity": False},
        ),
        candidate(
            "ang-crea-org-ar--club-inversores-angeles", "Club de Inversores Ángeles CREA", "crea.org.ar", "https://reporte.crea.org.ar/", "clube", "Argentina",
            ["src-argentina-crea"], "evidência-insuficiente", "A fonte confirma um clube e formação para analisar oportunidades, mas não separa com precisão seleção, decisão e capital nem data investimento recente.",
            evidence_ids=["ev-argentina-crea-model"], aliases=[{"name": "Club CREA", "alias_type": "nome"}], recurring=True,
            owner="review-angels-86", next_action="Obter fonte oficial datada de pitch ou aporte e o regulamento decisório do clube.",
        ),
    ],
    "chile": [
        candidate(
            "ang-centrodeinnovacion-uc-cl--red-angeles", "Red Ángeles do Centro de Innovación UC", "centrodeinnovacion.uc.cl", "https://centrodeinnovacion.uc.cl/red-angeles/", "rede", "Chile",
            ["src-chile-red-uc"], "elegível", None,
            evidence_ids=["ev-chile-red-uc-model", "ev-chile-red-uc-activity"], aliases=[{"name": "Red Ángeles UC", "alias_type": "nome"}],
            selection=actor("Equipe da Red Ángeles e Centro de Innovación UC", "equipe da rede"),
            decision_actors=actor("Investidores da Red Ángeles", "membros individuais"),
            capital=actor("Investidores da Red Ángeles", "membros individuais"),
            recurring=True, activity_status="confirmada-recente", activity_date="2026-02-18", external_access="aberto",
            application_route="https://centrodeinnovacion.uc.cl/red-angeles/",
        ),
        candidate(
            "ang-australangels-com", "Austral Angels", "australangels.com", "https://www.australangels.com/", "rede", "Chile",
            ["src-chile-austral"], "evidência-insuficiente", "A fonte confirma rede, análise recorrente e rotas abertas, mas só informa julho-agosto de 2024 sem dia civil verificável para a atividade.",
            evidence_ids=["ev-chile-austral-model"], selection=actor("Equipe da Austral Angels", "equipe da rede"),
            decision_actors=actor("Investidores da Austral Angels", "membros individuais"), capital=actor("Investidores da Austral Angels", "membros individuais"),
            recurring=True, external_access="aberto", application_route="https://www.australangels.com/",
            owner="review-angels-86", next_action="Localizar publicação oficial com data civil exata de pitch, decisão ou aporte dentro da janela.",
        ),
        candidate(
            "ang-chileglobalventures-cl--angels", "ChileGlobal Angels", "chileglobalventures.cl", "https://chileglobalventures.cl/angels/", "rede", "Chile",
            ["src-chile-chileglobal"], "evidência-insuficiente", "A fonte detalha rede, Pitch Day, decisão e coinvestimento dos membros, mas não fornece atividade oficial recente com data exata.",
            evidence_ids=["ev-chile-chileglobal-model"], selection=actor("Equipe da ChileGlobal Ventures", "equipe da rede"),
            decision_actors=actor("Membros da ChileGlobal Angels", "membros individuais"), capital=actor("Membros da ChileGlobal Angels", "membros individuais"),
            recurring=True, external_access="aberto", application_route="https://chileglobalventures.cl/angels/",
            owner="review-angels-86", next_action="Obter notícia oficial datada de Pitch Day ou investimento posterior a 27 de julho de 2024.",
        ),
        candidate(
            "ang-angelinvestmentnetwork-cl", "Red Chilena de Inversiones", "angelinvestmentnetwork.cl", "https://www.angelinvestmentnetwork.cl/", "plataforma", "Chile",
            ["src-chile-ain"], "encaminhado-para-plataformas", "O serviço vende publicação e destaque de propostas em um marketplace global; não opera como rede recorrente que seleciona e decide capital.",
            evidence_ids=["ev-chile-ain-boundary"], external_access="aberto", application_route="https://www.angelinvestmentnetwork.cl/nuestras-tarifas",
            canonical_profile="ecosystem/funding-platforms/red-chilena-de-inversiones.md",
        ),
    ],
    "paraguai": [
        candidate(
            "ang-inversionangel-co", "Red de Inversión Ángel del Paraguay", "inversionangel.co", "https://www.inversionangel.co/", "rede", "Paraguai",
            ["src-paraguai-riap", "src-paraguai-dinapi"], "evidência-insuficiente", "As fontes oficiais confirmam identidade e operação recente da RIAP, mas não publicam data civil exata nem separam integralmente seleção, decisão, capital e acesso externo.",
            evidence_ids=["ev-paraguai-riap-identity", "ev-paraguai-riap-institutional"], aliases=[{"name": "RIAP", "alias_type": "sigla"}],
            owner="review-angels-86", next_action="Obter regulamento oficial, rota aberta e publicação com data exata de pitch ou aporte recente.",
        ),
    ],
    "uruguai": [
        candidate(
            "ang-uruguayxxi-gub-uy--apep", "Red de Inversores APEP", "uruguayxxi.gub.uy", "https://www.uruguayxxi.gub.uy/es/eventos/articulo/suma-tu-startup-a-la-red-de-inversores-apep/", "programa público", "Uruguai",
            ["src-uruguai-apep"], "encaminhado-para-programas-públicos", "A convocatória é uma iniciativa intergovernamental APEP e a seleção é executada por Uruguay XXI, UIH e ANII; a governança é de programa público.",
            evidence_ids=["ev-uruguai-apep-boundary"], geography=["Uruguai", "países APEP"], selection=actor("Uruguay XXI, Uruguay Innovation Hub e ANII", "terceiro"),
            recurring=False, activity_status="confirmada-recente", activity_date="2024-10-21", external_access="aberto",
            application_route="https://www.uruguayxxi.gub.uy/es/eventos/articulo/suma-tu-startup-a-la-red-de-inversores-apep/",
            canonical_profile="ecosystem/public-programs/uruguay/red-inversores-apep.md",
        ),
        candidate(
            "ang-wtc-uy--piso-40", "Red de Inversores Ángeles de Piso 40", "wtc.uy", "https://www.wtc.uy/html/servicios", "rede", "Uruguai",
            ["src-uruguai-piso40"], "evidência-insuficiente", "A fonte institucional confirma a existência da rede, mas não publica processo, atores, acesso externo ou atividade recente com data verificável.",
            evidence_ids=["ev-uruguai-piso40-identity"], aliases=[{"name": "Piso 40", "alias_type": "nome"}],
            owner="review-angels-86", next_action="Obter regulamento oficial e atividade datada posterior a 27 de julho de 2024.",
        ),
        candidate(
            "ang-angelinvestmentnetwork-uy", "Red Uruguaya de Inversiones", "angelinvestmentnetwork.uy", "https://www.angelinvestmentnetwork.uy/", "plataforma", "Uruguai",
            ["src-uruguai-ain"], "encaminhado-para-plataformas", "O serviço permite publicar propostas e contatar investidores em uma plataforma global; não comprova seleção e decisão recorrentes por uma rede.",
            evidence_ids=["ev-uruguai-ain-boundary"], external_access="aberto", application_route="https://www.angelinvestmentnetwork.uy/emprendedores",
            canonical_profile="ecosystem/funding-platforms/red-uruguaya-de-inversiones.md",
        ),
    ],
}


EVIDENCE_BY_COUNTRY = {
    "argentina": [
        evidence("ev-argentina-bac-model", "ang-businessangelsclub-org", "https://businessangelsclub.org/para-fundadores.html", "Para fundadores", "Business Angels Club", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação", "geografia"], "Proceso e preguntas frecuentes", "A equipe filtra, o comitê seleciona para pitch, cada sócio decide individualmente e os participantes investem por veículo único; o BAC declara não administrar fundo e recebe candidaturas latino-americanas."),
        evidence("ev-argentina-bac-activity", "ang-businessangelsclub-org", "https://ar.linkedin.com/company/business-angels-club-emprendeiae", "Publicações do Business Angels Club", "Business Angels Club", ["atividade"], "Publicação sobre o anúncio do capítulo regional", "A conta institucional registra que o BAC anunciou seu primeiro capítulo regional em evento realizado em 9 de julho de 2026.", published_on="2026-07-09"),
        evidence("ev-argentina-bac-mar-del-plata", "ang-businessangelsclub-org--mar-del-plata", "https://ar.linkedin.com/company/business-angels-club-emprendeiae", "Publicações do Business Angels Club", "Business Angels Club", ["categoria", "geografia", "atividade"], "Anúncio do primeiro capítulo regional", "A fonte denomina Mar del Plata como primeiro capítulo regional do BAC e não atribui seleção, decisão ou capital autônomos.", published_on="2026-07-09"),
        evidence("ev-argentina-crea-model", "ang-crea-org-ar--club-inversores-angeles", "https://reporte.crea.org.ar/", "Reporte CREA", "CREA", ["categoria", "seleção", "recorrência"], "Club de Inversores Ángeles CREA", "O reporte descreve edições para membros aprenderem a analisar startups e alternativas de investimento agrifoodtech, sem detalhar decisão, capital ou aporte datado."),
    ],
    "chile": [
        evidence("ev-chile-red-uc-model", "ang-centrodeinnovacion-uc-cl--red-angeles", "https://centrodeinnovacion.uc.cl/red-angeles/", "Red Ángeles", "Centro de Innovación UC", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Programa e convocatórias", "A rede abre candidaturas, executa seleção antes da mesa e conecta startups a investidores que avaliam, decidem e aportam capital."),
        evidence("ev-chile-red-uc-activity", "ang-centrodeinnovacion-uc-cl--red-angeles", "https://centrodeinnovacion.uc.cl/noticias/red-angeles-del-centro-de-innovacion-uc-abre-convocatoria-para-inversionistas-y-startups/", "Red Ángeles abre convocatória para investidores e startups", "Centro de Innovación UC", ["atividade", "recorrência", "acesso externo", "rota de aplicação"], "Notícia e chamadas de postulação", "A notícia de 18 de fevereiro de 2026 abre nova convocatória para startups e investidores.", published_on="2026-02-18"),
        evidence("ev-chile-austral-model", "ang-australangels-com", "https://www.australangels.com/", "Austral Angels", "Austral Angels", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Inversión e formularios", "A rede declara avaliação constante, negociação, investimento e acompanhamento e oferece cadastros para startups e investidores; a atividade de 2024 não tem dia exato."),
        evidence("ev-chile-chileglobal-model", "ang-chileglobalventures-cl--angels", "https://chileglobalventures.cl/angels/", "ChileGlobal Angels", "Fundación Chile", ["categoria", "seleção", "decisão", "capital", "recorrência", "acesso externo", "rota de aplicação"], "Proceso de inversión e Pitch Day", "A rede seleciona startups para Pitch Day, recebe candidaturas e descreve coinvestimentos decididos pelos membros."),
        evidence("ev-chile-ain-boundary", "ang-angelinvestmentnetwork-cl", "https://www.angelinvestmentnetwork.cl/nuestras-tarifas", "Nuestras tarifas", "Angel Investment Network", ["categoria", "acesso externo", "rota de aplicação"], "Publicación de propuestas y tarifas", "O produto cobra planos para publicar e promover propostas perante uma base global de investidores, caracterizando plataforma."),
    ],
    "paraguai": [
        evidence("ev-paraguai-riap-identity", "ang-inversionangel-co", "https://py.linkedin.com/company/redangelpy/", "Red de Inversión Ángel del Paraguay", "RIAP", ["categoria", "geografia", "atividade"], "Descripción e publicaciones institucionales", "A conta oficial identifica a RIAP e relata portfólio com AngelHub e avaliação de startups por investidores, sem data civil exata exposta."),
        evidence("ev-paraguai-riap-institutional", "ang-inversionangel-co", "https://www.dinapi.gov.py/portal/v3/assets/biblioteca/documentos/Infodinapi-Octubre-2025.pdf", "InfoDINAPI — outubro de 2025", "DINAPI", ["categoria", "atividade"], "Mesa de Innovación", "O boletim oficial registra a participação da RIAP na mesa nacional de inovação em outubro de 2025, sem comprovar pitch ou aporte."),
    ],
    "uruguai": [
        evidence("ev-uruguai-apep-boundary", "ang-uruguayxxi-gub-uy--apep", "https://www.uruguayxxi.gub.uy/es/eventos/articulo/suma-tu-startup-a-la-red-de-inversores-apep/", "Suma tu startup a la Red de Inversores APEP", "Uruguay XXI", ["categoria", "atividade", "seleção", "acesso externo", "rota de aplicação", "geografia"], "Convocatoria e instituciones evaluadoras", "A iniciativa intergovernamental abre convocatória e atribui avaliação a Uruguay XXI, Uruguay Innovation Hub e ANII.", published_on="2024-10-21"),
        evidence("ev-uruguai-piso40-identity", "ang-wtc-uy--piso-40", "https://www.wtc.uy/html/servicios", "Servicios — Club de Ejecutivos Piso 40", "WTC Montevideo", ["categoria"], "Red de inversores ángeles", "A página institucional inclui entre os objetivos do clube criar e conectar empreendedores com uma rede de investidores-anjo."),
        evidence("ev-uruguai-ain-boundary", "ang-angelinvestmentnetwork-uy", "https://www.angelinvestmentnetwork.uy/emprendedores", "Emprendedores", "Angel Investment Network", ["categoria", "acesso externo", "rota de aplicação"], "Publicar propuesta y conectar", "O serviço permite publicar proposta e trocar mensagens com investidores de uma base global, caracterizando plataforma."),
    ],
}


COVERAGE = [
    {"schema_version":"1.0","coverage_id":"cov-argentina-associacao","issue":85,"geography":"Argentina","source_category":"associação","source_ids":["src-argentina-arcap"],"status":"concluída","candidate_count":0,"reason":None,"owner":"worker-argentina","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-argentina-oficial","issue":85,"geography":"Argentina","source_category":"site oficial","source_ids":["src-argentina-bac","src-argentina-crea"],"status":"concluída","candidate_count":3,"reason":None,"owner":"worker-argentina","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-chile-associacao","issue":85,"geography":"Chile","source_category":"associação","source_ids":["src-chile-acvc"],"status":"concluída","candidate_count":0,"reason":None,"owner":"worker-chile","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-chile-oficial","issue":85,"geography":"Chile","source_category":"site oficial","source_ids":["src-chile-austral","src-chile-chileglobal","src-chile-ain"],"status":"concluída","candidate_count":3,"reason":None,"owner":"worker-chile","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-chile-universidade","issue":85,"geography":"Chile","source_category":"universidade","source_ids":["src-chile-red-uc"],"status":"concluída","candidate_count":1,"reason":None,"owner":"worker-chile","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-paraguai-associacao","issue":85,"geography":"Paraguai","source_category":"associação","source_ids":["src-paraguai-parcapy"],"status":"concluída","candidate_count":0,"reason":None,"owner":"worker-paraguai","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-paraguai-institucional","issue":85,"geography":"Paraguai","source_category":"perfil institucional","source_ids":["src-paraguai-riap"],"status":"parcial","candidate_count":1,"reason":"A RIAP não expõe regulamento completo nem atividade com data civil exata.","owner":"worker-paraguai","next_action":"Retomar a lacuna na consolidação #86."},
    {"schema_version":"1.0","coverage_id":"cov-uruguai-associacao","issue":85,"geography":"Uruguai","source_category":"associação","source_ids":["src-uruguai-urucap"],"status":"concluída","candidate_count":0,"reason":None,"owner":"worker-uruguai","next_action":None},
    {"schema_version":"1.0","coverage_id":"cov-uruguai-oficial","issue":85,"geography":"Uruguai","source_category":"site oficial","source_ids":["src-uruguai-piso40","src-uruguai-ain"],"status":"parcial","candidate_count":2,"reason":"Piso 40 não publica processo nem atividade recente datada; a plataforma foi encaminhada.","owner":"worker-uruguai","next_action":"Retomar Piso 40 na consolidação #86."},
    {"schema_version":"1.0","coverage_id":"cov-uruguai-publico","issue":85,"geography":"Uruguai","source_category":"notícia","source_ids":["src-uruguai-apep"],"status":"concluída","candidate_count":1,"reason":None,"owner":"worker-uruguai","next_action":None},
]


def manifest() -> list[dict]:
    run = {
        "schema_version": "1.0", "record_type": "run", "run_id": RUN_ID,
        "issues": [85], "contract_issue": 80, "cutoff_date": CUTOFF,
        "created_on": CUTOFF, "status": "concluída", "task_count": 5,
        "scraping_performed": True, "max_global_requests": 8,
        "max_requests_per_domain": 2, "max_browsers": 2,
        "owner": "worker-consolidator",
        "notes": "Dezesseis fontes oficiais em quatro shards exclusivos; nenhum perfil criado.",
    }
    tasks = []
    for country in SOURCES_BY_COUNTRY:
        tasks.append({
            "schema_version": "1.0", "record_type": "task", "run_id": RUN_ID,
            "task_id": f"task-{country}", "issue": 85,
            "url": SOURCES_BY_COUNTRY[country][0]["initial_url"],
            "task_type": "descoberta", "partition": country.title(),
            "shard_path": f"research/epic-63/southern-cone/shards/worker-{country}/",
            "priority": 1, "status": "done", "owner": f"worker-{country}",
            "next_action": None, "last_error": None,
        })
    tasks.append({
        "schema_version": "1.0", "record_type": "task", "run_id": RUN_ID,
        "task_id": "task-consolidacao", "issue": 85,
        "url": "https://github.com/djairofilho/awesome-latam-vc/issues/85",
        "task_type": "revisão", "partition": "Consolidação",
        "shard_path": "research/epic-63/southern-cone/shards/worker-consolidator/",
        "priority": 2, "status": "done", "owner": "worker-consolidator",
        "next_action": None, "last_error": None,
    })
    return [run, *tasks]


def main() -> None:
    research_root = ROOT.parent
    partition = ROOT.name
    for country in SOURCES_BY_COUNTRY:
        worker = f"worker-{country}"
        write_shard(research_root, partition, worker, "sources", SOURCES_BY_COUNTRY[country])
        write_shard(research_root, partition, worker, "candidates", CANDIDATES_BY_COUNTRY[country])
        write_shard(research_root, partition, worker, "evidence", EVIDENCE_BY_COUNTRY[country])
    write_shard(research_root, partition, "worker-consolidator", "coverage", COVERAGE)
    write_shard(research_root, partition, "worker-consolidator", "manifest", manifest())
    for kind, filename in (
        ("candidates", "candidates.jsonl"),
        ("coverage", "coverage-matrix.jsonl"),
        ("evidence", "evidence.jsonl"),
        ("manifest", "run-manifest.jsonl"),
        ("sources", "source-inventory.jsonl"),
    ):
        reduce_shards(research_root, kind, ROOT / filename)


if __name__ == "__main__":
    main()
