"""Registros determinísticos da revisão final da issue #221."""

from __future__ import annotations

from typing import Any


CUTOFF = "2026-07-30"
WORKER = "worker-221-review"


SOURCE_SPECS = [
    ("hiker-datlo", "Datlo", "https://blog.datlo.com/datlo-recebe-aporte-hiker-ventures", "rounds", "Anúncio de rodada liderada pela Hiker Ventures."),
    ("grao-stay", "Grão VC", "https://grao.vc/en/por-que-investimos-na-stay/", "rounds", "Anúncio oficial de investimento na Stay."),
    ("valutia-wehandle", "Inova Unicamp", "https://parque.inova.unicamp.br/wehandle-empresa-instalada-do-parque-cientifico-e-tecnologico-da-unicamp-capta-r-36-milhoes-em-investimento/", "rounds", "Rodada da Wehandle com participação da Valutia."),
    ("blustone-wehandle", "Inova Unicamp", "https://parque.inova.unicamp.br/wehandle-empresa-instalada-do-parque-cientifico-e-tecnologico-da-unicamp-capta-r-36-milhoes-em-investimento/", "rounds", "Rodada da Wehandle com participação da BluStone."),
    ("honey-4um", "4UM Investimentos", "https://www.4um.com.br/informacoes-regulatorias/", "official_portfolios", "Relação institucional do veículo Honey Island by 4UM."),
    ("broom-brick", "Economia PR", "https://economiapr.com.br/2025/02/24/startup-recebe-aporte-para-impulsionar-ia-na-prevencao-de-fraudes-e-subscricao/", "rounds", "Aporte da Broom Ventures na startup brasileira Brick."),
    ("venture-hub-unicamp", "Inova Unicamp", "https://parque.inova.unicamp.br/portfolio/venture-hub/", "official_portfolios", "Perfil institucional da Venture Hub no parque da Unicamp."),
    ("fundepar-ufmg", "UFMG", "https://www.ufmg.br/comunicacao/noticias/noticias-externas/fundepar-investe-em-startup-que-reduz-uso-de-plastico-no-setor-automotivo/", "rounds", "Notícia institucional de investimento da Fundepar."),
    ("positive-report-2025", "Positive Ventures", "https://www.positiveimpactreport25.com/", "official_portfolios", "Relatório de impacto 2025 publicado pela gestora."),
    ("lightrock-sao-paulo", "Lightrock", "https://www.lightrock.com/news/state-of-sao-paulo-s-development-agency-commits-r-50-million-to-lightrock/", "foreign_access", "Compromisso da Desenvolve SP com a estratégia brasileira da Lightrock."),
    ("marcha-tecnopuc", "Tecnopuc", "https://tecnopuc.pucrs.br/conheca-a-marcha-a-primeira-university-venture-capital-do-brasil-que-impulsiona-startups-no-tecnopuc/", "rounds", "Apresentação institucional da Marcha como University Venture Capital."),
    ("cv-idexo-totvs", "TOTVS", "https://api.mziq.com/mzfilemanager/v2/d/d3be5d49-62e7-4def-a3e1-ab25ff09f153/6f68bd5d-b48f-f806-7e1d-8261e809845b?origin=2", "launches", "Documento institucional que identifica o veículo CV iDEXO."),
    ("link-ventures-site", "Link Ventures", "https://www.linkventures.com.br/", "official_portfolios", "Site institucional da Link Ventures."),
    ("startvc-site", "StartVC", "https://startvc.com.br/", "official_portfolios", "Site oficial do programa StartVC."),
    ("3c-site", "3C Invest", "https://3cinvest.com.br/", "official_portfolios", "Site oficial da plataforma 3C Invest."),
    ("uniangels-unicamp", "Inova Unicamp", "https://www.inova.unicamp.br/2025/06/investimento-anjo-e-tema-de-webinar-promovido-pela-inova-unicamp-em-parceria-com-a-uniangels/", "regional_sources", "Parceria institucional confirma a natureza de rede anjo da UniAngels."),
    ("insper-angels-kolek", "Insper", "https://www.insper.edu.br/pt/conteudos/gestao-e-negocios/investimento-na-startup-kolek-marca-nova-fase-do-insper-angels", "regional_sources", "Notícia institucional sobre investimento da rede Insper Angels."),
    ("csn-inova-sosa", "CSN", "https://esg.csn.com.br/news/csn-inova-e-sosa-firmam-parceria-para-impulsionar-inovacao-no-brasil/", "launches", "Anúncio oficial da estratégia CSN Inova Ventures e de sua carteira."),
    ("vibra-ventures-report", "Vibra Energia", "https://vibraenergia.com.br/sites/default/files/2025-05/Relat%C3%B3rio%20Integrado_Vibra_2024_PTBR.pdf", "launches", "Relatório integrado identifica o fundo Vibra Ventures e seus investimentos."),
    ("copel-ventures-fu2re", "Copel", "https://www.copel.com/site/noticias/copel-investe-em-startup-de-inteligencia-artificial-para-a-gestao-de-ativos/", "launches", "Anúncio oficial de investimento do Copel Ventures I."),
    ("bb-ventures-startups", "Banco do Brasil", "https://www.bb.com.br/site/startups/", "launches", "Portal oficial identifica BB Ventures, MSW Capital e o portfólio."),
    ("basf-vc-brazil", "BASF", "https://www.basf.com/basf/www/br/pt/who-we-are/digitalization/startups", "foreign_access", "Página oficial brasileira apresenta a atuação da BASF com startups."),
    ("carbyne-fucape", "Fucape", "https://fucape.br/hub-fucape-abre-portas-para-startups-selecionadas-em-fevereiro/", "regional_sources", "Fonte institucional identifica a Carbyne Investimentos."),
    ("ita-angels-insper", "Insper", "https://www.insper.edu.br/pt/conteudos/tecnologia/startup-de-bolsistas-do-insper-capta-r-12-milhao-na-primeira-rodada-de-investimentos", "regional_sources", "Anúncio institucional identifica a rede ITA Angels."),
    ("foks-insper-demoday", "Insper", "https://www.insper.edu.br/pt/eventos/2025/11/demoday-do-hub", "regional_sources", "Página institucional identifica o programa de aceleração FOKS."),
    ("saturation-ctit-spin-offs", "CTIT UFMG", "https://www.ctit.ufmg.br/spin-offs/", "regional_sources", "Passagem de saturação por spin-offs e licenciamento; nenhum investidor novo identificado."),
    ("saturation-unicamp-kasco", "Inova Unicamp", "https://www.inova.unicamp.br/2025/07/ti-inside-tecnologia-que-automatiza-inspecao-de-redes-eletricas-e-licenciada-para-spin-off-da-unicamp/", "regional_sources", "Passagem de saturação por licenciamento tecnológico; nenhum investidor novo identificado."),
    ("saturation-petrobras-supplier-award", "Petrobras", "https://canalfornecedor.petrobras.com.br/documents/d/canal-do-fornecedor/regulamento-pmf-8-edicao-publicado-2?download=true", "sector_maps", "Passagem de saturação por prêmio de inovação de fornecedores; nenhum fundo investidor identificado."),
    ("saturation-fieb-veracel-suppliers", "FIEB", "https://www.fieb.org.br/noticias/12-empresas-concluem-4o-ciclo-do-programa-de-desenvolvimento-de-fornecedores-da-veracel-celulose-em-parceria-com-o-iel-bahia/", "sector_maps", "Passagem de saturação por programa corporativo de fornecedores; nenhum fundo investidor identificado."),
]


def source_records() -> list[dict[str, Any]]:
    rows = []
    for slug, source, url, family, notes in SOURCE_SPECS:
        rows.append({
            "schema_version": "1.0",
            "source_id": f"src-fund-br-221-{slug}",
            "issue": 221,
            "source": source,
            "initial_url": url,
            "source_family": family,
            "source_disposition": "new_source",
            "research_channel": "non_cvm",
            "is_cvm": False,
            "discovery_allowed": True,
            "prior_source_ids": [],
            "scope_walked": notes,
            "accessed_on": CUTOFF,
            "robots_status": "allowed",
            "access_method": "browser",
            "cache_key": None,
            "result": "complete",
            "reason": None,
            "owner": WORKER,
            "next_action": None,
            "notes": notes,
        })
    return rows


def candidate(
    slug: str,
    name: str,
    source_slug: str,
    site: str | None,
    domain: str | None,
    base_country: str | None,
    relation: str,
    decision: str,
    *,
    entity_type: str = "investment_organization",
    direct: bool | None = None,
    recurring: bool | None = None,
    activity_status: str = "unknown",
    activity_on: str | None = None,
    destination: str | None = None,
    profile: str | None = None,
    reason: str | None = None,
    owner: str | None = None,
    next_action: str | None = None,
    manager_id: str | None = None,
    vehicle_ids: list[str] | None = None,
    program_ids: list[str] | None = None,
) -> dict[str, Any]:
    candidate_id = f"fund-br-221-{slug}"
    return {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "name": name,
        "brand_id": f"brand-{slug}",
        "manager_id": manager_id,
        "vehicle_ids": vehicle_ids or [],
        "program_ids": program_ids or [],
        "successor_id": None,
        "canonical_candidate_id": None,
        "canonical_profile": profile,
        "aliases": [],
        "entity_type": entity_type,
        "canonical_domain": domain,
        "official_site": site,
        "base_country": base_country,
        "brazil_relation": relation,
        "direct_startup_investment": direct,
        "recurring_vc": recurring,
        "activity_status": activity_status,
        "latest_official_activity_on": activity_on,
        "cutoff_date": CUTOFF,
        "discovery_source_ids": [f"src-fund-br-221-{source_slug}"],
        "official_evidence_ids": [],
        "discovered_on": CUTOFF,
        "status": "decided",
        "decision": decision,
        "reason": reason,
        "destination": destination,
        "owner": owner,
        "next_action": next_action,
    }


def candidate_records() -> list[dict[str, Any]]:
    rows = [
        candidate("hiker-ventures", "Hiker Ventures", "hiker-datlo", "https://www.hiker.ventures/", "hiker.ventures", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2025-05-13", destination="funds/brazil/hiker-ventures.md", manager_id="manager-af-invest-administracao-recursos"),
        candidate("grao-vc", "Grão VC", "grao-stay", "https://grao.vc/", "grao.vc", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2024-10-29", destination="funds/brazil/grao-vc.md"),
        candidate("valutia", "Valutia", "valutia-wehandle", "https://www.valutia.com/", "valutia.com", "PT", "accessible_to_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2025-09-09", destination="funds/regional/valutia.md"),
        candidate("blustone-capital", "BluStone Capital", "blustone-wehandle", "https://blustone.capital/", "blustone.capital", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2025-09-09", destination="funds/brazil/blustone-capital.md"),
        candidate("honey-island-by-4um", "Honey Island by 4UM", "honey-4um", "https://www.4um.com.br/informacoes-regulatorias/", "4um.com.br", "BR", "based_in_brazil", "duplicate", entity_type="vehicle", profile="funds/brazil/honey-island-capital.md", reason="O nome identifica um veículo distinto da organização Honey Island Capital, que já possui perfil canônico.", vehicle_ids=["vehicle-honey-island-by-4um-fip"]),
        candidate("broom-ventures", "Broom Ventures", "broom-brick", "https://www.broom.ventures/", "broom.ventures", None, "brazil_incidental", "insufficient_evidence", direct=True, recurring=True, reason="O portfólio confirma investimento na brasileira Brick, mas não comprova acesso recorrente e explícito a startups do Brasil.", owner=WORKER, next_action="Obter tese, formulário ou declaração oficial que confirme acesso recorrente ao Brasil."),
        candidate("venture-hub", "Venture Hub", "venture-hub-unicamp", "https://venturehub.se/investimentos/", "venturehub.se", "BR", "based_in_brazil", "insufficient_evidence", reason="A atuação híbrida de hub, boutique, pools e parceria com a Valetec não permite atribuir os aportes a uma única organização ou veículo.", owner=WORKER, next_action="Identificar veículo, gestora e carteira em fontes oficiais separadas."),
        candidate("fundepar", "Fundepar", "fundepar-ufmg", "https://fundepar.com.br/", "fundepar.com.br", "BR", "based_in_brazil", "duplicate", profile="funds/brazil/fundepar.md", reason="A organização já possui perfil canônico no catálogo."),
        candidate("positive-ventures", "Positive Ventures", "positive-report-2025", "https://positive.ventures/", "positive.ventures", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2026-06-30", destination="funds/brazil/positive-ventures.md"),
        candidate("lightrock", "Lightrock", "lightrock-sao-paulo", "https://www.lightrock.com/", "lightrock.com", None, "accessible_to_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2026-02-05", destination="funds/regional/lightrock.md"),
        candidate("marcha", "Marcha", "marcha-tecnopuc", "https://www.linkedin.com/company/marcha-s-a", "linkedin.com", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2025-04-04", destination="funds/brazil/marcha.md"),
        candidate("cv-idexo", "CV iDEXO", "cv-idexo-totvs", "https://api.mziq.com/mzfilemanager/v2/d/d3be5d49-62e7-4def-a3e1-ab25ff09f153/6f68bd5d-b48f-f806-7e1d-8261e809845b?origin=2", None, "BR", "based_in_brazil", "eligible", entity_type="vehicle", direct=True, recurring=True, activity_status="active", activity_on="2025-02-25", destination="funds/brazil/cv-idexo.md", vehicle_ids=["vehicle-cv-idexo"]),
        candidate("link-ventures", "Link Ventures", "link-ventures-site", "https://www.linkventures.com.br/", "linkventures.com.br", "BR", "based_in_brazil", "insufficient_evidence", direct=True, recurring=True, reason="A tese e a relação institucional são verificáveis, mas não há atividade oficial datada dentro da janela.", owner=WORKER, next_action="Localizar anúncio oficial datado de aporte, desinvestimento ou nova captação."),
        candidate("startvc", "StartVC", "startvc-site", "https://startvc.com.br/", "startvc.com.br", "BR", "based_in_brazil", "routed_accelerators", entity_type="unknown", destination="epic-62-accelerators", reason="A oferta oficial é um programa de aceleração e preparação de startups.", program_ids=["program-startvc"]),
        candidate("3c-invest", "3C Invest", "3c-site", "https://3cinvest.com.br/", "3cinvest.com.br", "BR", "based_in_brazil", "routed_funding_platforms", destination="funding-platforms", reason="A organização opera uma plataforma de conexão e captação, não um fundo de venture capital.", program_ids=["program-3c-invest"]),
        candidate("uniangels", "UniAngels", "uniangels-unicamp", "https://uniangels.com.br/", "uniangels.com.br", "BR", "based_in_brazil", "routed_angel_networks", destination="epic-63-angel-networks", reason="A fonte institucional e o site oficial identificam uma rede de investidores-anjo."),
        candidate("insper-angels", "Insper Angels", "insper-angels-kolek", "https://www.insperangels.com.br/startups", "insperangels.com.br", "BR", "based_in_brazil", "routed_angel_networks", destination="epic-63-angel-networks", reason="A organização é uma rede de investidores-anjo ligada à comunidade Insper."),
        candidate("csn-inova-ventures", "CSN Inova Ventures", "csn-inova-sosa", "https://esg.csn.com.br/inovacao/", "esg.csn.com.br", "BR", "based_in_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2024-09-15", destination="funds/brazil/csn-inova-ventures.md"),
        candidate("vibra-ventures", "Vibra Ventures", "vibra-ventures-report", "https://vibraenergia.com.br/", "vibraenergia.com.br", "BR", "based_in_brazil", "eligible", entity_type="fund", direct=True, recurring=True, activity_status="active", activity_on="2026-06-08", destination="funds/brazil/vibra-ventures.md"),
        candidate("copel-ventures-i", "Copel Ventures I", "copel-ventures-fu2re", "https://www.copel.com/", "copel.com", "BR", "based_in_brazil", "eligible", entity_type="vehicle", direct=True, recurring=True, activity_status="active", activity_on="2025-07-24", destination="funds/brazil/copel-ventures-i.md", manager_id="manager-vox-capital", vehicle_ids=["vehicle-copel-ventures-i"]),
        candidate("bb-ventures", "BB Ventures", "bb-ventures-startups", "https://www.bb.com.br/site/startups/", "bb.com.br", "BR", "based_in_brazil", "eligible", entity_type="vehicle", direct=True, recurring=True, activity_status="active", activity_on="2025-08-14", destination="funds/brazil/bb-ventures.md", manager_id="manager-msw-capital", vehicle_ids=["vehicle-bb-ventures-fip"]),
        candidate("basf-venture-capital", "BASF Venture Capital GmbH", "basf-vc-brazil", "https://www.basf.com/global/en/who-we-are/organization/group-companies/BASF_Venture-Capital", "basf.com", "DE", "accessible_to_brazil", "eligible", direct=True, recurring=True, activity_status="active", activity_on="2025-12-04", destination="funds/regional/basf-venture-capital.md"),
        candidate("carbyne-investimentos", "Carbyne Investimentos", "carbyne-fucape", "https://carbyneinvestimentos.com/", "carbyneinvestimentos.com", "BR", "based_in_brazil", "insufficient_evidence", reason="As fontes confirmam a organização brasileira, mas não comprovam aporte direto nem atividade startup atual datada.", owner=WORKER, next_action="Obter anúncio oficial datado de aporte direto em startup e esclarecer o veículo investidor."),
        candidate("ita-angels", "ITA Angels", "ita-angels-insper", None, None, "BR", "based_in_brazil", "routed_angel_networks", destination="epic-63-angel-networks", reason="A organização é uma rede de membros investidores-anjo."),
        candidate("foks", "FOKS", "foks-insper-demoday", None, None, "BR", "based_in_brazil", "routed_accelerators", destination="epic-62-accelerators", reason="A fonte institucional descreve programa de aceleração e Demo Day.", program_ids=["program-foks"]),
    ]
    evidence_by_candidate: dict[str, list[str]] = {}
    for item in evidence_records():
        evidence_by_candidate.setdefault(item["candidate_id"], []).append(item["evidence_id"])
    for row in rows:
        row["official_evidence_ids"] = sorted(
            evidence_id
            for evidence_id in evidence_by_candidate.get(row["candidate_id"], [])
            if EVIDENCE_CLASS[evidence_id] == "official"
        )
    return rows


def evidence(
    slug: str,
    candidate_slug: str,
    url: str,
    title: str,
    publisher: str,
    source_type: str,
    claims: list[tuple[str, str]],
    summary: str,
    *,
    observed_on: str | None = None,
    published_on: str | None = None,
    source_class: str = "official",
    subject_type: str = "candidate",
    subject_id: str | None = None,
) -> dict[str, Any]:
    candidate_id = f"fund-br-221-{candidate_slug}"
    return {
        "schema_version": "1.0",
        "evidence_id": f"ev-fund-br-221-{slug}",
        "candidate_id": candidate_id,
        "subject_type": subject_type,
        "subject_id": subject_id or candidate_id,
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_class": source_class,
        "source_type": source_type,
        "cvm_query_id": None,
        "published_on": published_on,
        "observed_on": observed_on,
        "accessed_on": CUTOFF,
        "claims": [{"field": field, "finding": finding} for field, finding in claims],
        "locator": title,
        "summary": summary,
    }


def evidence_records() -> list[dict[str, Any]]:
    four = [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("brazil_access", "confirmed")]
    all_five = [*four, ("activity", "confirmed")]
    rows = [
        evidence("hiker-site", "hiker-ventures", "https://www.hiker.ventures/", "Hiker Ventures", "Hiker Ventures", "official_website", four, "A marca da AF Invest se apresenta como venture capital early stage, com capital próprio, portfólio e presença em São Paulo e Belo Horizonte.", subject_type="manager", subject_id="manager-af-invest-administracao-recursos"),
        evidence("hiker-datlo", "hiker-ventures", "https://blog.datlo.com/datlo-recebe-aporte-hiker-ventures", "Datlo recebe aporte liderado pela Hiker Ventures", "Datlo", "official_announcement", [("activity", "confirmed")], "A investida anunciou rodada de R$ 4 milhões liderada pela Hiker e descreveu sua carteira.", observed_on="2025-05-13", published_on="2025-05-13"),
        evidence("grao-about", "grao-vc", "https://grao.vc/a-grao/", "A Grão", "Grão VC", "official_website", four, "A gestora se define como braço de venture capital de um family office, focado em startups brasileiras em estágio inicial."),
        evidence("grao-stay", "grao-vc", "https://grao.vc/en/por-que-investimos-na-stay/", "Why did we invest in Stay?", "Grão VC", "official_announcement", [("activity", "confirmed")], "A Grão documenta seu investimento direto na Stay.", observed_on="2024-10-29", published_on="2024-10-29"),
        evidence("valutia-about", "valutia", "https://www.valutia.com/about", "About Valutia", "Valutia", "official_website", four, "A firma informa 28 investimentos e tese para empreendedores do Brasil e de Portugal."),
        evidence("valutia-wehandle", "valutia", "https://br.linkedin.com/company/valutia", "Valutia — Wehandle funding round", "Valutia", "official_announcement", [("activity", "confirmed")], "A Valutia anunciou participação na rodada da Wehandle e sua expansão no Brasil e Chile.", observed_on="2025-09-09", published_on="2025-09-09"),
        evidence("blustone-site", "blustone-capital", "https://blustone.capital/", "BluStone Capital", "BluStone Capital", "official_portfolio", four, "O site confirma venture capital early stage, endereço em São Paulo, dois fundos e quatorze empresas no portfólio."),
        evidence("blustone-wehandle", "blustone-capital", "https://www.linkedin.com/posts/canary-venture-capital_we-are-very-excited-to-partner-with-rodrigo-activity-7371543021445742592-Uhea", "Canary anuncia rodada da Wehandle", "Canary", "official_announcement", [("activity", "confirmed")], "A co-investidora oficial confirmou a participação da BluStone na rodada de R$ 36 milhões.", observed_on="2025-09-09", published_on="2025-09-09"),
        evidence("honey-4um", "honey-island-by-4um", "https://www.4um.com.br/informacoes-regulatorias/", "Informações regulatórias", "4UM Investimentos", "official_filing", [("identity", "confirmed"), ("manager_vehicle_relation", "confirmed")], "A página lista o Honey Island by 4UM FIP como veículo regulado.", subject_type="vehicle", subject_id="vehicle-honey-island-by-4um-fip"),
        evidence("honey-vehicles", "honey-island-by-4um", "https://www.linkedin.com/posts/hi.capital_fintech-transfeera-honeyisland-activity-7200861846650675202-CS8B", "Honey Island — Transfeera", "Honey Island Capital", "official_announcement", [("identity", "confirmed"), ("manager_vehicle_relation", "confirmed")], "A organização distingue investimentos feitos pelos veículos Honey Island I e Honey Island by 4UM.", observed_on="2024-05-23"),
        evidence("broom-site", "broom-ventures", "https://www.broom.ventures/companies", "Broom Ventures — Companies", "Broom Ventures", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("brazil_access", "inconclusive"), ("activity", "inconclusive")], "O portfólio confirma a Brick, mas não declara tese ou acesso recorrente ao Brasil."),
        evidence("venture-hub-site", "venture-hub", "https://venturehub.se/investimentos/", "Venture Hub — Investimentos", "Venture Hub", "official_website", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("recurring_vc", "inconclusive"), ("brazil_access", "confirmed"), ("manager_vehicle_relation", "inconclusive")], "A página mistura boutique, pools, FIP, CVC e parceria com a Valetec."),
        evidence("fundepar-site", "fundepar", "https://fundepar.com.br/", "Fundepar", "Fundepar", "official_website", [("identity", "confirmed")], "O site confirma a mesma organização já publicada no catálogo."),
        evidence("positive-report", "positive-ventures", "https://www.positiveimpactreport25.com/", "Positive Impact Report 2025", "Positive Ventures", "official_document", all_five, "O relatório confirma gestora de venture capital de impacto, capital direto, carteira recorrente, operação em São Paulo e atividade em 2025.", observed_on="2026-06-30", published_on="2026-06-30"),
        evidence("lightrock-about", "lightrock", "https://www.lightrock.com/about/private-equity/", "Private Equity", "Lightrock", "official_thesis", four, "A estratégia global de growth e venture mantém portfólio direto, incluindo Agrolend e Buser no Brasil."),
        evidence("lightrock-sao-paulo", "lightrock", "https://www.lightrock.com/news/state-of-sao-paulo-s-development-agency-commits-r-50-million-to-lightrock/", "Desenvolve SP commits R$ 50 million to Lightrock", "Lightrock", "official_announcement", [("activity", "confirmed"), ("brazil_access", "confirmed")], "A Lightrock anunciou compromisso de R$ 50 milhões para sua estratégia no Brasil.", observed_on="2026-02-05", published_on="2026-02-05"),
        evidence("marcha-tecnopuc", "marcha", "https://tecnopuc.pucrs.br/conheca-a-marcha-a-primeira-university-venture-capital-do-brasil-que-impulsiona-startups-no-tecnopuc/", "Conheça a Marcha", "Tecnopuc", "official_announcement", four, "O parque da PUCRS apresenta a Marcha como University Venture Capital brasileira que investe em startups.", observed_on="2025-03-06", published_on="2025-03-06"),
        evidence("marcha-pureai", "marcha", "https://tecnopuc.pucrs.br/pureai-abre-rodada-de-captacao-de-investimento-para-impulsionar-infraestrutura-de-ia/", "PureAI abre rodada de captação", "Tecnopuc", "official_announcement", [("activity", "confirmed")], "O parque registra atividade da Marcha com a startup PureAI.", observed_on="2025-04-04", published_on="2025-04-04"),
        evidence("cv-idexo-totvs", "cv-idexo", "https://api.mziq.com/mzfilemanager/v2/d/d3be5d49-62e7-4def-a3e1-ab25ff09f153/6f68bd5d-b48f-f806-7e1d-8261e809845b?origin=2", "Documento institucional TOTVS — CV iDEXO", "TOTVS", "official_document", four, "O documento identifica o CV iDEXO como veículo de corporate venture capital com carteira direta e operação brasileira.", subject_type="vehicle", subject_id="vehicle-cv-idexo"),
        evidence("cv-idexo-malga", "cv-idexo", "https://pt.linkedin.com/posts/felipefornaziere_malga-marketplace-de-pagamentos-do-ecommerce-activity-7300210272747634688-Ov8O", "Rodada da Malga", "CV iDEXO", "official_announcement", [("activity", "confirmed")], "Anúncio da rodada da Malga confirma atividade do veículo.", observed_on="2025-02-25", published_on="2025-02-25", subject_type="vehicle", subject_id="vehicle-cv-idexo"),
        evidence("link-site", "link-ventures", "https://www.linkventures.com.br/", "Link Ventures", "Link Ventures", "official_website", [*four, ("activity", "inconclusive")], "O site confirma tese e investimentos, mas não oferece marco oficial datado na janela."),
        evidence("startvc-site", "startvc", "https://startvc.com.br/", "StartVC", "StartVC", "official_application", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "O programa oferece aceleração, mentoria e preparação para investimento.", subject_type="program", subject_id="program-startvc"),
        evidence("3c-site", "3c-invest", "https://3cinvest.com.br/", "3C Invest", "3C Invest", "official_application", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "A plataforma conecta empresas e investidores para captação.", subject_type="program", subject_id="program-3c-invest"),
        evidence("uniangels-site", "uniangels", "https://uniangels.com.br/", "UniAngels", "UniAngels", "official_website", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "O site identifica uma rede de investimento-anjo."),
        evidence("insper-angels-site", "insper-angels", "https://www.insperangels.com.br/startups", "Insper Angels — Startups", "Insper Angels", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "A organização reúne investidores-anjo e apresenta startups apoiadas."),
        evidence("csn-inova-sosa", "csn-inova-ventures", "https://esg.csn.com.br/news/csn-inova-e-sosa-firmam-parceria-para-impulsionar-inovacao-no-brasil/", "CSN Inova e SOSA firmam parceria", "CSN", "official_announcement", all_five, "A CSN identifica a frente Ventures, investimentos sucessivos, dez empresas no portfólio e acesso estruturado ao Brasil.", observed_on="2024-09-15", published_on="2024-09-15"),
        evidence("vibra-ventures-report", "vibra-ventures", "https://vibraenergia.com.br/sites/default/files/2025-05/Relat%C3%B3rio%20Integrado_Vibra_2024_PTBR.pdf", "Relatório Integrado Vibra 2024", "Vibra Energia", "official_document", four, "O relatório confirma fundo criado em 2022, compromisso de R$ 150 milhões e três investimentos diretos."),
        evidence("vibra-ventures-websummit", "vibra-ventures", "https://www.vibraenergia.com.br/sites/default/files/2026-06/08.06.2026_Release%20Vibra%20no%20WebSummitRio2026_V4.docx_.pdf", "Vibra no Web Summit Rio 2026", "Vibra Energia", "official_announcement", [("activity", "confirmed")], "O release oficial confirma a operação ativa da estratégia de corporate venture.", observed_on="2026-06-08", published_on="2026-06-08"),
        evidence("copel-ventures-fu2re", "copel-ventures-i", "https://www.copel.com/site/noticias/copel-investe-em-startup-de-inteligencia-artificial-para-a-gestao-de-ativos/", "Copel investe na Fu2re", "Copel", "official_announcement", all_five, "A Copel identifica o veículo, a parceria com a Vox, a tese CVC, investimentos em startups e o aporte de R$ 7,5 milhões na Fu2re.", observed_on="2025-07-24", published_on="2025-07-24", subject_type="vehicle", subject_id="vehicle-copel-ventures-i"),
        evidence("bb-ventures-portal", "bb-ventures", "https://www.bb.com.br/site/startups/", "Investimentos em Startups", "Banco do Brasil", "official_portfolio", four, "O portal distingue BB Ventures de BB Impacto, identifica gestão pela MSW Capital, FIP, formulário e quatro empresas no portfólio.", subject_type="vehicle", subject_id="vehicle-bb-ventures-fip"),
        evidence("bb-ventures-expenses", "bb-ventures", "https://blog.bb.com.br/bb-expenses/", "BB Expenses", "Banco do Brasil", "official_announcement", [("activity", "confirmed")], "O Banco do Brasil documenta solução criada no BB Ventures em parceria com a investida Payfy.", observed_on="2025-08-14", published_on="2025-08-14", subject_type="vehicle", subject_id="vehicle-bb-ventures-fip"),
        evidence("basf-vc-group", "basf-venture-capital", "https://www.basf.com/global/en/who-we-are/organization/group-companies/BASF_Venture-Capital", "BASF Venture Capital", "BASF", "official_website", four, "A unidade corporativa evergreen investe diretamente e de forma recorrente em startups globais; a página brasileira e a responsável regional em São Paulo confirmam acesso ao Brasil."),
        evidence("basf-vc-ph7", "basf-venture-capital", "https://www.basf.com/global/en/who-we-are/organization/group-companies/BASF_Venture-Capital/publications/2025/251204-ph7", "BASF Venture Capital invests in pH7", "BASF", "official_announcement", [("activity", "confirmed")], "A BASF Venture Capital anunciou investimento na pH7.", observed_on="2025-12-04", published_on="2025-12-04"),
        evidence("carbyne-site", "carbyne-investimentos", "https://carbyneinvestimentos.com/", "Carbyne Investimentos", "Carbyne Investimentos", "official_website", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("recurring_vc", "inconclusive"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "O site não oferece prova suficiente de aporte direto e atividade startup atual."),
        evidence("ita-angels-insper", "ita-angels", "https://www.insper.edu.br/pt/conteudos/tecnologia/startup-de-bolsistas-do-insper-capta-r-12-milhao-na-primeira-rodada-de-investimentos", "Startup capta R$ 1,2 milhão", "Insper", "official_announcement", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "O Insper identifica a ITA Angels como rede de membros investidores.", observed_on="2026-01-14", published_on="2026-01-14"),
        evidence("foks-insper", "foks", "https://www.insper.edu.br/pt/eventos/2025/11/demoday-do-hub", "DemoDay do Hub", "Insper", "official_announcement", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("brazil_access", "confirmed")], "A página descreve aceleração e apresentação de startups, sem data diária exata.", subject_type="program", subject_id="program-foks"),
    ]
    return rows


EVIDENCE_CLASS = {
    item["evidence_id"]: item["source_class"] for item in evidence_records()
}


def identity_records() -> list[dict[str, Any]]:
    candidates = candidate_records()
    rows = []
    for item in candidates:
        candidate_id = item["candidate_id"]
        slug = candidate_id.removeprefix("fund-br-221-")
        resolution = "same_identity"
        canonical = candidate_id
        reason = "A fonte oficial confirma a organização candidata como identidade canônica."
        if slug in {"honey-island-by-4um", "cv-idexo", "copel-ventures-i", "bb-ventures"}:
            resolution = "distinct_vehicle"
            reason = "O nome identifica um veículo distinto de sua marca ou organização gestora."
        elif item["decision"] == "duplicate":
            canonical = None
            reason = "A identidade corresponde a uma organização já publicada no perfil canônico indicado."
        elif slug in {"venture-hub", "link-ventures"}:
            resolution = "unresolved"
            canonical = None
            reason = "A relação entre marca, organização, gestora e veículos não está completamente resolvida."
        rows.append({
            "schema_version": "1.0",
            "resolution_id": f"identity-fund-br-221-{slug}",
            "subject_ids": [candidate_id],
            "canonical_candidate_id": canonical,
            "brand_id": item["brand_id"],
            "manager_id": item["manager_id"],
            "vehicle_ids": item["vehicle_ids"],
            "resolution": resolution,
            "reason": reason,
            "evidence_ids": item["official_evidence_ids"],
            "resolved_on": CUTOFF,
            "resolver": WORKER,
        })
    return rows
