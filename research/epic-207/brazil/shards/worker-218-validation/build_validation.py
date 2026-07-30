from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "validation-shards" / "issue-218" / "candidates.jsonl"
OUT = Path(__file__).resolve().parent
ACCESSED_ON = "2026-07-30"
OWNER = "worker-218-validation-1"


def cache_key(url: str) -> str:
    return "sha256:" + hashlib.sha256(url.encode("utf-8")).hexdigest()


def source(
    slug: str,
    title: str,
    url: str,
    family: str,
    scope: str,
    notes: str,
    *,
    prior_source_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "source_id": f"src-fund-br-218-{slug}",
        "issue": 218,
        "source": title,
        "initial_url": url,
        "source_family": family,
        "source_disposition": (
            "prior_source" if prior_source_ids else "new_source"
        ),
        "research_channel": "non_cvm",
        "is_cvm": False,
        "discovery_allowed": True,
        "prior_source_ids": prior_source_ids or [],
        "scope_walked": scope,
        "accessed_on": ACCESSED_ON,
        "robots_status": "allowed",
        "access_method": "http",
        "cache_key": cache_key(url),
        "result": "complete",
        "reason": None,
        "owner": OWNER,
        "next_action": None,
        "notes": notes,
    }


SOURCES = [
    source(
        "canary-about",
        "Canary: About Us",
        "https://www.canary.com.br/about-us/",
        "official_portfolios",
        "Identidade, modelo de operator fund, atuação em venture capital e relação com empreendedores na América Latina.",
        "Revalidação oficial da identidade que já possui perfil canônico.",
    ),
    source(
        "good-karma-anbima-transition",
        "ANBIMA: Good Karma Ventures Gestora de Recursos",
        "https://www.anbima.com.br/pt_br/institucional/perfil-da-instituicao/instituicao/3b8989e0-8365-4371-ad70-c57187ee1e73/perfil/good-karma-ventures-gestora-de-recursos-ltda.htm",
        "official_portfolios",
        "Cadastro institucional atualizado em 9 de julho de 2026, website declarado e aviso de alteração cadastral para Just Climate Limitada.",
        "Fonte institucional não-CVM usada apenas para a transição de identidade.",
    ),
    source(
        "good-karma-restructure",
        "Good Karma Fund: edital de convocação sobre reestruturação",
        "https://funds-tmf-group.com.br/wp-content/uploads/2025/02/Convocacao-de-AGC-Good-Karma-FIP-Multiestrategia-Edital-de-convocacao-28-de-outubro-de-2024.pdf",
        "official_portfolios",
        "Documento do administrador do fundo sobre reestruturação, novo veículo brasileiro e carteira local.",
        "A fonte comprova operação em 2024, mas não resolve a sucessão pública entre Good Karma e Just Climate em 2026.",
    ),
    source(
        "sp-ventures-portfolio",
        "SP Ventures: Portfolio",
        "https://spventures.com.br/portfolio/",
        "official_portfolios",
        "Identidade, portfólio ativo e formulário oficial para envio de pitch.",
        "Revalidação oficial da identidade que já possui perfil canônico.",
    ),
    source(
        "valor-home",
        "Valor Capital Group: site oficial",
        "https://valorcapitalgroup.com/",
        "official_portfolios",
        "Identidade, atuação entre Estados Unidos e América Latina, empresas brasileiras e atividade editorial datada em 2026.",
        "Revalidação oficial da identidade que já possui perfil canônico.",
    ),
    source(
        "30n-finmaq",
        "30N Ventures: Why we invested in Finmaq",
        "https://www.30n.vc/en/stories/why-we-invested-in-finmaq-empowering-entrepreneurs-through-accessible-financing",
        "foreign_access",
        "Anúncio oficial de investimento publicado em 15 de janeiro de 2025 e descrição da atuação em mercados emergentes.",
        "A página não declara mandato, equipe, canal ou presença recorrente no Brasil.",
    ),
    source(
        "fhe-linktree",
        "FHE Ventures: canal oficial agregado",
        "https://linktr.ee/fheventures",
        "regional_sources",
        "Identidade pública e links oficiais disponíveis para a FHE Ventures.",
        "O canal não publica portfólio, veículo, recorrência, atividade datada ou processo de investimento verificável.",
    ),
    source(
        "primus-home",
        "Primus Ventures: site oficial",
        "https://www.primusvc.com.br/",
        "official_portfolios",
        "Identidade, endereço em Florianópolis e atuação como investidor de startups.",
        "Revalidação oficial da identidade que já possui perfil canônico.",
    ),
    source(
        "quartzo-portfolio",
        "Quartzo Capital: portfólio de venture capital",
        "https://quartzocapital.com.br/venture-capital/portfolio",
        "official_portfolios",
        "Histórico de dez veículos de venture capital no Brasil, empresas investidas, exits e operação de investimento direto.",
        "A página confirma os gates estruturais, mas não fornece sozinha uma data de atividade.",
    ),
    source(
        "quartzo-calendar",
        "Quartzo Capital: calendário de eventos",
        "https://www.quartzocapital.com.br/calendario-de-eventos",
        "official_portfolios",
        "Agenda oficial de atividades de venture capital realizadas em 2025, inclusive evento de founders em 26 de novembro.",
        "Mantida como contexto, sem uso no gate de atividade de investimento.",
    ),
    source(
        "quartzo-loopia-investment",
        "Quartzo Capital: investimento do FUNSES1 na Loopia",
        "https://pt.linkedin.com/posts/quartzocapital_a-quartzo-capital-tem-o-prazer-de-divulgar-activity-7303744796290871298-4gna",
        "official_portfolios",
        "Publicação controlada pela Quartzo, datada em 7 de março de 2025, sobre rodada pré-seed liderada pelo FUNSES1, veículo gerido pela organização.",
        "A data vem do campo datePublished do metadata JSON-LD público da própria página; a fonte substitui o calendário como prova de atividade de investimento.",
    ),
    source(
        "sororite-ventures",
        "Sororitê Ventures: fundo e tese",
        "https://www.sororite.com.br/sororite-ventures",
        "official_portfolios",
        "Identidade, Sororitê Fund 1, investimento em startups brasileiras e processo para fundadoras.",
        "Nome, domínio, marca e veículo coincidem com fund-br-sororite-ventures.",
    ),
    source(
        "agroven-home",
        "AgroVen: clube, investimentos e portfólio",
        "https://agroven.com.br/",
        "official_portfolios",
        "Modelo de clube, investimentos realizados pelos membros, processo para startups, portfólio e notícias datadas.",
        "A fonte oficial contradiz investimento direto pela organização e sustenta rota para redes de investidores.",
    ),
    source(
        "ipe-home",
        "IPÊ Investe: programa de aceleração e investimento",
        "https://ipeinvestco.com/",
        "regional_sources",
        "Primeira edição, cronograma iniciado em 24 de junho de 2026, aceleração, seleção e aportes por fases.",
        "A própria organização se apresenta como programa de aceleração; recorrência ainda não foi demonstrada.",
    ),
    source(
        "jatoba-home",
        "Jatobá Gestora: Fundo Impacto Amazônia",
        "https://jatobagestao.com.br/",
        "official_portfolios",
        "Identidade, sede em Manaus e proposta de FIP voltado a startups amazônicas.",
        "A página não data primeiro investimento, carteira ou atividade do veículo.",
    ),
    source(
        "parallax-home",
        "Parallax Ventures: site e portfólio",
        "https://parallax.vc/",
        "official_portfolios",
        "Identidade, sede em São Paulo, operação desde 2018 e portfólio de empresas de tecnologia.",
        "A página institucional não fornece sozinha uma data recente de atividade.",
    ),
    source(
        "parallax-fund-2025",
        "Parallax Ventures FIP: fato relevante de 2025",
        "https://parallax.vc/wp-content/uploads/2025/08/20250801_Parallax-I-Ventures_Fato-Relevante.pdf",
        "official_portfolios",
        "Documento hospedado no domínio oficial sobre atualização da carteira do FIP com data-base de 28 de fevereiro de 2025.",
        "Documento público do fundo, consultado fora da CVM.",
    ),
    source(
        "bs2-launch-revalidation",
        "Banco BS2: lançamento do BS2 Ventures",
        "https://blog.bancobs2.com.br/banco-bs2-fundo-de-cvc-solucoes-pmes/",
        "launches",
        "Anúncio oficial de 12 de novembro de 2024 sobre o veículo, dois investimentos realizados e plano de aportes recorrentes.",
        "Reacesso da fonte oficial já inventariada no shard de lançamento.",
        prior_source_ids=["src-fund-br-bs2-official-launch"],
    ),
    source(
        "canaan-about",
        "Canaan: About",
        "https://c.canaan.com/about",
        "foreign_access",
        "Identidade e modelo recorrente de venture capital da Canaan.",
        "A fonte não declara mandato, presença ou canal recorrente para o Brasil; a Neofin permanece um caso isolado.",
    ),
    source(
        "lightspeed-frubana",
        "Lightspeed: Frubana",
        "https://lsvp.com/company/frubana/",
        "foreign_access",
        "Página oficial de portfólio para investimento de 2021 em empresa com presença no Brasil.",
        "Uma investida com operação brasileira não comprova acesso recorrente da gestora ao país.",
    ),
    source(
        "lux-fund-ix",
        "Lux Capital: Announcing Lux Ventures IX",
        "https://www.luxcapital.com/news/announcing-lux-ventures-ix",
        "foreign_access",
        "Anúncio oficial de 7 de janeiro de 2026 sobre novo fundo e continuidade da operação de venture capital.",
        "A fonte não declara mandato, presença ou acesso recorrente ao Brasil; Magie permanece um caso isolado.",
    ),
    source(
        "mundi-first-close",
        "Mundi Ventures: LatAm Fund I first closing",
        "https://www.mundiventures.com/post/mundi-ventures-announces-its-latam-fund-i-first-closing",
        "launches",
        "Anúncio oficial de 23 de março de 2026 sobre o primeiro fechamento, estratégia regional, operação desde 2015 e mais de 70 empresas apoiadas.",
        "A unidade editorial foi tratada como Mundi Ventures; LatAm Fund I permanece como veículo.",
    ),
    source(
        "mundi-brazil-access",
        "Mundi Ventures: compromisso do IDB Invest no LatAm Fund I",
        "https://www.mundiventures.com/post/idb-invest-commits-us-5-million-to-mundi-ventures-latam-fund-i",
        "foreign_access",
        "Anúncio oficial de 4 de fevereiro de 2025 sobre expansão na América Latina e investidas regionais, incluindo Sami no Brasil.",
        "A combinação de veículo regional, investimento brasileiro e atividade posterior confirma acesso verificável ao Brasil.",
    ),
    source(
        "mundi-linkedin-brazil",
        "Mundi Ventures: estratégia do LatAm Fund I inclui o Brasil",
        "https://www.linkedin.com/posts/mundi-ventures_we-are-excited-to-announce-the-first-closing-activity-7441794544146268160-mi2A",
        "foreign_access",
        "Publicação controlada pela organização que enumera o Brasil entre os países da estratégia do LatAm Fund I.",
        "A enumeração explícita do Brasil elimina a dependência de inferir o país a partir do termo América Latina.",
    ),
    source(
        "sagol-linkedin",
        "Sagol Holdings: perfil institucional",
        "https://www.linkedin.com/company/sagol-holdings",
        "foreign_access",
        "Perfil controlado pela organização com descrição de family office, venture capital e investimentos diretos.",
        "Não há mandato, presença, canal ou atividade recorrente explicitamente ligada ao Brasil.",
    ),
]


def evidence(
    slug: str,
    candidate_id: str,
    url: str,
    title: str,
    publisher: str,
    source_type: str,
    claims: list[tuple[str, str]],
    locator: str,
    summary: str,
    *,
    published_on: str | None = None,
    observed_on: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "evidence_id": f"ev-fund-br-218-{slug}",
        "candidate_id": candidate_id,
        "subject_type": "candidate",
        "subject_id": candidate_id,
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_class": "official",
        "source_type": source_type,
        "cvm_query_id": None,
        "published_on": published_on,
        "observed_on": observed_on,
        "accessed_on": ACCESSED_ON,
        "claims": [
            {"field": field, "finding": finding}
            for field, finding in claims
        ],
        "locator": locator,
        "summary": summary,
    }


EVIDENCE = [
    evidence(
        "canary-about",
        "fund-br-210-canary",
        "https://www.canary.com.br/about-us/",
        "About Us",
        "Canary",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "confirmed"),
        ],
        "Seções “We are Canary”, “We are always on” e depoimentos de fundadores.",
        "A Canary se identifica como operator fund de venture capital early-stage na América Latina e descreve investimentos; o domínio coincide com o perfil canônico.",
    ),
    evidence(
        "good-karma-transition",
        "fund-br-210-good-karma",
        "https://www.anbima.com.br/pt_br/institucional/perfil-da-instituicao/instituicao/3b8989e0-8365-4371-ad70-c57187ee1e73/perfil/good-karma-ventures-gestora-de-recursos-ltda.htm",
        "Good Karma Ventures Gestora de Recursos Ltda.",
        "ANBIMA",
        "official_document",
        [
            ("identity", "confirmed"),
            ("activity", "inconclusive"),
            ("brazil_access", "confirmed"),
        ],
        "Cadastro institucional, website e aviso de alteração cadastral.",
        "O cadastro atualizado em 9 de julho de 2026 identifica a gestora brasileira e informa processo de alteração para Just Climate Limitada, sem resolver a sucessão editorial.",
        published_on="2026-07-09",
        observed_on="2026-07-09",
    ),
    evidence(
        "good-karma-restructure",
        "fund-br-210-good-karma",
        "https://funds-tmf-group.com.br/wp-content/uploads/2025/02/Convocacao-de-AGC-Good-Karma-FIP-Multiestrategia-Edital-de-convocacao-28-de-outubro-de-2024.pdf",
        "Edital de convocação do Good Karma Fund FIP",
        "TMF Brasil",
        "official_document",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Trecho sobre novo fundo brasileiro, GK Ventures LP e carteira local.",
        "O administrador descreve reestruturação do fundo e lista ativos brasileiros, confirmando operação em 2024; o documento não determina a identidade pública após a mudança para Just Climate.",
        published_on="2024-10-28",
        observed_on="2024-10-28",
    ),
    evidence(
        "sp-ventures-portfolio",
        "fund-br-210-sp-ventures",
        "https://spventures.com.br/portfolio/",
        "Portfolio",
        "SP Ventures",
        "official_portfolio",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "confirmed"),
        ],
        "Portfólio, chamada “Submit Your Pitch” e identificação no rodapé.",
        "O domínio e a organização coincidem com o perfil canônico e o site mantém portfólio e canal para founders.",
    ),
    evidence(
        "valor-home",
        "fund-br-210-valor-capital-group",
        "https://valorcapitalgroup.com/",
        "Using Global Insights to Drive Local Innovation",
        "Valor Capital Group",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Cabeçalho institucional, empresas brasileiras, formulário para pitch e publicação de 24 de abril de 2026.",
        "O domínio e a operação cross-border coincidem com o perfil canônico; a publicação oficial de 2026 confirma atividade dentro da janela.",
        published_on="2026-04-24",
        observed_on="2026-04-24",
    ),
    evidence(
        "30n-finmaq",
        "fund-br-213-30n-ventures",
        "https://www.30n.vc/en/stories/why-we-invested-in-finmaq-empowering-entrepreneurs-through-accessible-financing",
        "Why we invested in Finmaq",
        "30N Ventures",
        "official_announcement",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "not_disclosed"),
        ],
        "Título, autoria e anúncio do investimento.",
        "A 30N anuncia investimento em empresa latino-americana e confirma operação de VC em 2025, mas não explicita acesso recorrente ao Brasil.",
        published_on="2025-01-15",
        observed_on="2025-01-15",
    ),
    evidence(
        "fhe-linktree",
        "fund-br-213-fhe-ventures",
        "https://linktr.ee/fheventures",
        "FHE Ventures Official",
        "FHE Ventures",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "not_disclosed"),
            ("recurring_vc", "not_disclosed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "not_disclosed"),
        ],
        "Título do canal e links disponibilizados pela organização.",
        "O canal confirma a marca, mas não publica veículo, portfólio, recorrência, atividade datada ou processo de aporte.",
    ),
    evidence(
        "primus-home",
        "fund-br-213-primus-ventures",
        "https://www.primusvc.com.br/",
        "Primus Ventures",
        "Primus Ventures",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "confirmed"),
        ],
        "Seção “Quem somos”, contato e endereço em Florianópolis.",
        "Nome, domínio e endereço coincidem com o perfil canônico; o site descreve investimento recorrente em startups.",
    ),
    evidence(
        "quartzo-portfolio",
        "fund-br-213-quartzo-capital",
        "https://quartzocapital.com.br/venture-capital/portfolio",
        "Portfólio e Cases: Venture Capital",
        "Quartzo Capital",
        "official_portfolio",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "inconclusive"),
            ("brazil_access", "confirmed"),
        ],
        "Seções “Venture Capital com disciplina” e “Histórico de Fundos”.",
        "A Quartzo declara mais de quinze anos de atuação, dez veículos de VC no Brasil, investidas e exits; a página não data a última atividade.",
    ),
    evidence(
        "quartzo-calendar",
        "fund-br-213-quartzo-capital",
        "https://www.quartzocapital.com.br/calendario-de-eventos",
        "Calendário de Eventos",
        "Quartzo Capital",
        "official_website",
        [("activity", "inconclusive")],
        "Tabela “Eventos passados”, linha “Expansão Global + Future Founders + Formatura Batch 6 | Venture Capital”.",
        "O calendário registra um evento ligado a venture capital, mas não comprova operação da Quartzo como investidora e não sustenta o gate de atividade.",
        observed_on="2025-11-26",
    ),
    evidence(
        "quartzo-loopia-investment",
        "fund-br-213-quartzo-capital",
        "https://pt.linkedin.com/posts/quartzocapital_a-quartzo-capital-tem-o-prazer-de-divulgar-activity-7303744796290871298-4gna",
        "Investimento do FUNSES1 na Loopia",
        "Quartzo Capital",
        "official_announcement",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Texto da publicação e metadata JSON-LD com datePublished 2025-03-07T11:54:16.410Z.",
        "A Quartzo anuncia rodada pré-seed da startup Loopia liderada pelo FUNSES1, veículo de investimento gerido pela organização, comprovando operação de investimento no Brasil dentro da janela.",
        published_on="2025-03-07",
        observed_on="2025-03-07",
    ),
    evidence(
        "sororite-ventures",
        "fund-br-213-sororite-ventures",
        "https://www.sororite.com.br/sororite-ventures",
        "Sororitê Ventures",
        "Sororitê",
        "official_thesis",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "confirmed"),
        ],
        "Seções “Sororitê Fund 1”, tese e chamada “Capte conosco”.",
        "Nome, domínio, gestoras e Sororitê Fund 1 coincidem com fund-br-sororite-ventures, tornando este ID uma redescoberta exata.",
    ),
    evidence(
        "agroven-home",
        "fund-br-214-agroven",
        "https://agroven.com.br/",
        "AgroVen: Innovation Agribusiness Network",
        "AgroVen",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "contradictory"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Seções “Quem somos”, FAQ “Como ser investido”, portfólio e notícias.",
        "A AgroVen se define como clube e informa que os aportes são feitos pelos membros; notícia de 15 de dezembro de 2025 confirma atividade, mas o modelo pertence à rota de redes de investidores.",
        published_on="2025-12-15",
        observed_on="2025-12-15",
    ),
    evidence(
        "ipe-home",
        "fund-br-214-ipe-investe",
        "https://ipeinvestco.com/",
        "IPÊ Investe: Programa de aceleração e investimento",
        "IPÊ Investe",
        "official_application",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "not_disclosed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Título, seção “Sobre o programa”, jornada e cronograma.",
        "A primeira edição abriu em 24 de junho de 2026 e combina aceleração e aportes; não há histórico de recorrência nem veículo autônomo comprovado.",
        published_on="2026-06-24",
        observed_on="2026-06-24",
    ),
    evidence(
        "jatoba-home",
        "fund-br-214-jatoba-impacto-amazonia",
        "https://jatobagestao.com.br/",
        "Jatobá Gestora: Capital que impulsiona negócios sustentáveis",
        "Jatobá Gestora",
        "official_thesis",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "inconclusive"),
            ("activity", "not_disclosed"),
            ("brazil_access", "confirmed"),
        ],
        "Seções institucionais e “Jatobá Impacto Amazônia”.",
        "A gestora brasileira apresenta um FIP voltado a startups amazônicas, mas não publica carteira, primeiro aporte ou atividade datada do veículo.",
    ),
    evidence(
        "parallax-home",
        "fund-br-214-parallax-ventures",
        "https://parallax.vc/",
        "Parallax Ventures",
        "Parallax Ventures",
        "official_portfolio",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "inconclusive"),
            ("brazil_access", "confirmed"),
        ],
        "Cabeçalho, métricas, empresas selecionadas e endereço em São Paulo.",
        "A Parallax declara operação desde 2018, quinze empresas de portfólio e sede brasileira; a página não data a última atividade.",
    ),
    evidence(
        "parallax-fund-2025",
        "fund-br-214-parallax-ventures",
        "https://parallax.vc/wp-content/uploads/2025/08/20250801_Parallax-I-Ventures_Fato-Relevante.pdf",
        "Parallax Ventures FIP: fato relevante",
        "Parallax Ventures FIP",
        "official_filing",
        [("activity", "confirmed"), ("manager_vehicle_relation", "confirmed")],
        "Primeira página, atualização dos ativos da carteira com data-base de 28 de fevereiro de 2025.",
        "O documento hospedado pelo fundo registra reavaliação da carteira e valorização do portfólio, comprovando atividade dentro da janela.",
        published_on="2025-07-31",
        observed_on="2025-02-28",
    ),
    evidence(
        "bs2-launch-revalidation",
        "fund-br-bs2-ventures",
        "https://blog.bancobs2.com.br/banco-bs2-fundo-de-cvc-solucoes-pmes/",
        "BS2 lança fundo de CVC com foco em PMEs",
        "Banco BS2",
        "official_announcement",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Anúncio do veículo, dois investimentos concluídos e plano de alocação.",
        "O banco brasileiro confirma o BS2 Ventures, aportes em Bloxs e Somos Young e plano de investir em uma carteira de empresas.",
        published_on="2024-11-12",
        observed_on="2024-11-12",
    ),
    evidence(
        "canaan-about",
        "fund-br-canaan",
        "https://c.canaan.com/about",
        "About",
        "Canaan",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "not_disclosed"),
        ],
        "Descrição institucional e histórico de mais de trinta anos.",
        "A Canaan confirma modelo recorrente de venture capital, mas não declara mandato, presença ou canal contínuo para o Brasil; Neofin permanece uma ocorrência isolada.",
    ),
    evidence(
        "lightspeed-frubana",
        "fund-br-lightspeed",
        "https://lsvp.com/company/frubana/",
        "Frubana",
        "Lightspeed Venture Partners",
        "official_portfolio",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "inconclusive"),
        ],
        "Campos “LSVP Investment”, estágio e presença da empresa.",
        "A página confirma um investimento de 2021 em empresa com operação no Brasil, mas não prova mandato ou acesso recorrente atual da Lightspeed ao país.",
    ),
    evidence(
        "lux-fund-ix",
        "fund-br-lux-capital",
        "https://www.luxcapital.com/news/announcing-lux-ventures-ix",
        "Announcing Lux Ventures IX",
        "Lux Capital",
        "official_announcement",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "not_disclosed"),
        ],
        "Anúncio do nono fundo e descrição da continuidade da estratégia.",
        "A Lux comprova operação recente e recorrente em 2026, mas não declara mandato, presença ou canal de investimento para startups brasileiras.",
        published_on="2026-01-07",
        observed_on="2026-01-07",
    ),
    evidence(
        "mundi-first-close",
        "fund-br-mundi-ventures-latam",
        "https://www.mundiventures.com/post/mundi-ventures-announces-its-latam-fund-i-first-closing",
        "Mundi Ventures Announces its LatAm Fund I First Closing",
        "Mundi Ventures",
        "official_announcement",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "inconclusive"),
        ],
        "Anúncio do primeiro fechamento e seção “About Mundi Ventures”.",
        "A Mundi anuncia o veículo regional em 2026 e declara operação desde 2015 com mais de setenta empresas apoiadas; o veículo foi preservado sem virar uma segunda organização.",
        published_on="2026-03-23",
        observed_on="2026-03-23",
    ),
    evidence(
        "mundi-brazil-access",
        "fund-br-mundi-ventures-latam",
        "https://www.mundiventures.com/post/idb-invest-commits-us-5-million-to-mundi-ventures-latam-fund-i",
        "IDB Invest Commits US$5 Million to Mundi Ventures LatAm Fund I",
        "Mundi Ventures",
        "official_announcement",
        [
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Escopo regional, histórico na América Latina e lista de investidas, incluindo Sami no Brasil.",
        "A Mundi vincula o novo fundo à expansão latino-americana e registra empresa brasileira no portfólio, confirmando acesso verificável ao país.",
        published_on="2025-02-04",
        observed_on="2025-02-04",
    ),
    evidence(
        "mundi-linkedin-brazil",
        "fund-br-mundi-ventures-latam",
        "https://www.linkedin.com/posts/mundi-ventures_we-are-excited-to-announce-the-first-closing-activity-7441794544146268160-mi2A",
        "Mundi Ventures LatAm Fund I first closing",
        "Mundi Ventures",
        "official_announcement",
        [
            ("recurring_vc", "confirmed"),
            ("activity", "confirmed"),
            ("brazil_access", "confirmed"),
        ],
        "Publicação institucional, parágrafo que enumera os países da estratégia.",
        "A Mundi declara que a estratégia do LatAm Fund I abrange explicitamente Argentina, Brasil, Caribe, América Central, Chile, Colômbia, Equador, México, Peru e Uruguai.",
        published_on="2026-03-23",
        observed_on="2026-03-23",
    ),
    evidence(
        "sagol-linkedin",
        "fund-br-sagol-holdings",
        "https://www.linkedin.com/company/sagol-holdings",
        "Sagol Holdings",
        "Sagol Holdings",
        "official_website",
        [
            ("identity", "confirmed"),
            ("direct_startup_investment", "confirmed"),
            ("recurring_vc", "confirmed"),
            ("activity", "not_disclosed"),
            ("brazil_access", "not_disclosed"),
        ],
        "Seção “About us” do perfil institucional.",
        "A organização se descreve como family office de venture capital e investimentos diretos, mas não publica acesso recorrente ao Brasil; BotCity permanece uma ocorrência isolada.",
    ),
]


UPDATES: dict[str, dict[str, Any]] = {
    "fund-br-210-canary": {
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "duplicate",
        "reason": "Nome, domínio e organização coincidem exatamente com o perfil funds/regional/canary.md.",
        "destination": "funds/regional/canary.md",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-210-good-karma": {
        "canonical_domain": "gkventures.com",
        "official_site": "https://www.gkventures.com/",
        "base_country": "BR",
        "brazil_relation": "based_in_brazil",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "unknown",
        "latest_official_activity_on": "2024-10-28",
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "A operação do fundo em 2024 está documentada, mas o cadastro de 2026 informa mudança para Just Climate e não há fonte oficial que resolva sucessão, marca atual e continuidade do portfólio sob Good Karma.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Obter comunicado oficial da gestora ou do administrador que confirme a data efetiva, a sucessão Good Karma e Just Climate e a atividade atual da carteira.",
    },
    "fund-br-210-sp-ventures": {
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "duplicate",
        "reason": "Nome, domínio e organização coincidem exatamente com o perfil funds/regional/sp-ventures.md.",
        "destination": "funds/regional/sp-ventures.md",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-210-valor-capital-group": {
        "activity_status": "active",
        "latest_official_activity_on": "2026-04-24",
        "status": "decided",
        "decision": "duplicate",
        "reason": "Nome, domínio e organização coincidem exatamente com o perfil funds/multi-country/valor-capital-group.md.",
        "destination": "funds/multi-country/valor-capital-group.md",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-213-30n-ventures": {
        "canonical_domain": "30n.vc",
        "official_site": "https://www.30n.vc/",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2025-01-15",
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "A fonte oficial confirma venture capital e atividade recente na América Latina, mas não explicita mandato, presença, canal ou acesso recorrente para startups brasileiras.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Localizar fonte controlada pela 30N que inclua explicitamente o Brasil na estratégia, equipe, portfólio ou processo de submissão.",
    },
    "fund-br-213-fhe-ventures": {
        "base_country": "BR",
        "direct_startup_investment": None,
        "recurring_vc": None,
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "O canal oficial disponível confirma apenas a marca; não há veículo, portfólio, aporte direto, recorrência ou atividade datada verificáveis.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Obter site ou documento controlado pela FHE com operador, carteira, instrumento de aporte e atividade dentro da janela.",
    },
    "fund-br-213-primus-ventures": {
        "status": "decided",
        "decision": "duplicate",
        "reason": "Nome, domínio, endereço e organização coincidem exatamente com o perfil funds/brazil/primus-ventures.md.",
        "destination": "funds/brazil/primus-ventures.md",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-213-quartzo-capital": {
        "base_country": "BR",
        "brazil_relation": "based_in_brazil",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2025-03-07",
        "status": "decided",
        "decision": "eligible",
        "reason": "Fontes oficiais confirmam identidade, dez veículos de venture capital no Brasil, portfólio e recorrência; anúncio de 7 de março de 2025 comprova investimento do FUNSES1 gerido pela Quartzo na Loopia.",
        "destination": None,
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-213-sororite-ventures": {
        "status": "decided",
        "decision": "duplicate",
        "reason": "Nome, domínio, marca, gestoras e Sororitê Fund 1 coincidem com fund-br-sororite-ventures.",
        "destination": "fund-br-sororite-ventures",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-214-agroven": {
        "direct_startup_investment": False,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2025-12-15",
        "status": "decided",
        "decision": "routed_angel_networks",
        "reason": "A própria AgroVen se define como clube e informa que os investimentos são realizados pelos membros, não por uma organização que aporta capital agrupado diretamente.",
        "destination": "epic-63-angel-networks",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-214-ipe-investe": {
        "base_country": "BR",
        "direct_startup_investment": True,
        "recurring_vc": None,
        "activity_status": "active",
        "latest_official_activity_on": "2026-06-24",
        "status": "decided",
        "decision": "routed_accelerators",
        "reason": "A fonte oficial apresenta a iniciativa como primeira edição de um programa de aceleração com aportes por fases; não há veículo recorrente independente comprovado.",
        "destination": "epic-62-accelerators",
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-214-jatoba-impacto-amazonia": {
        "direct_startup_investment": True,
        "recurring_vc": None,
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "O site confirma a gestora brasileira e a proposta do Fundo Impacto Amazônia, mas não publica carteira, primeiro aporte, recorrência ou atividade datada do veículo.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Obter anúncio oficial datado do primeiro investimento ou relatório do fundo que demonstre carteira e operação dentro da janela.",
    },
    "fund-br-214-parallax-ventures": {
        "base_country": "BR",
        "brazil_relation": "based_in_brazil",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2025-02-28",
        "status": "decided",
        "decision": "eligible",
        "reason": "Site e documento do fundo confirmam identidade, sede brasileira, investimento direto, recorrência, carteira e atividade com data-base em fevereiro de 2025.",
        "destination": None,
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-bs2-ventures": {
        "status": "decided",
        "decision": "eligible",
        "reason": "O anúncio oficial do banco confirma fundo brasileiro de CVC, dois investimentos concluídos, plano recorrente de aportes e atividade em novembro de 2024.",
        "destination": None,
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-canaan": {
        "canonical_domain": "canaan.com",
        "official_site": "https://c.canaan.com/about",
        "base_country": "US",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2025-02-05",
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "A Canaan é uma gestora recorrente e investiu na Neofin, mas uma rodada brasileira isolada não comprova mandato ou acesso contínuo ao país.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Localizar fonte da Canaan que declare explicitamente estratégia, equipe ou canal recorrente para o Brasil.",
    },
    "fund-br-lightspeed": {
        "canonical_domain": "lsvp.com",
        "official_site": "https://lsvp.com/",
        "base_country": "US",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "A Lightspeed possui investidas com operação brasileira, mas as fontes oficiais revisadas não comprovam mandato, presença ou acesso recorrente atual para startups do Brasil.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Obter tese, equipe ou canal oficial da Lightspeed que inclua explicitamente o Brasil e uma atividade datada dentro da janela.",
    },
    "fund-br-lux-capital": {
        "canonical_domain": "luxcapital.com",
        "official_site": "https://www.luxcapital.com/",
        "base_country": "US",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2026-01-07",
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "A Lux confirma operação recente e recorrente, mas não declara mandato, presença ou canal contínuo para o Brasil; a relação com Magie é incidental.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Localizar fonte da Lux que inclua explicitamente o Brasil na estratégia, equipe, portfólio recorrente ou processo de submissão.",
    },
    "fund-br-mundi-ventures-latam": {
        "name": "Mundi Ventures",
        "aliases": ["Mundi Ventures Fundo 6", "Mundi Ventures LatAm Fund I"],
        "entity_type": "investment_organization",
        "base_country": "ES",
        "brazil_relation": "accessible_to_brazil",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "active",
        "latest_official_activity_on": "2026-03-23",
        "status": "decided",
        "decision": "eligible",
        "reason": "A organização opera venture capital desde 2015, mantém portfólio direto, anunciou o LatAm Fund I em 2026 e documenta investida brasileira e expansão regional.",
        "destination": None,
        "owner": OWNER,
        "next_action": None,
    },
    "fund-br-sagol-holdings": {
        "official_site": "https://www.linkedin.com/company/sagol-holdings",
        "base_country": "IL",
        "direct_startup_investment": True,
        "recurring_vc": True,
        "activity_status": "unknown",
        "latest_official_activity_on": None,
        "status": "decided",
        "decision": "insufficient_evidence",
        "reason": "O family office declara venture capital e investimentos diretos, mas não publica mandato, presença, canal ou atividade recorrente ligada ao Brasil; BotCity é uma ocorrência isolada.",
        "destination": None,
        "owner": OWNER,
        "next_action": "Obter fonte controlada pela Sagol com portfólio, atividade datada e acesso recorrente explícito ao Brasil.",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    payload = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def build_candidates() -> list[dict[str, Any]]:
    candidates = read_jsonl(QUEUE)
    source_by_url = {
        item["initial_url"]: item["source_id"]
        for item in SOURCES
    }
    evidence_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for item in EVIDENCE:
        evidence_by_candidate.setdefault(item["candidate_id"], []).append(item)

    if set(UPDATES) != {item["candidate_id"] for item in candidates}:
        raise ValueError("UPDATES não cobre exatamente os IDs do shard #218")

    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        candidate.update(UPDATES[candidate_id])
        new_evidence = evidence_by_candidate[candidate_id]
        candidate["official_evidence_ids"] = sorted(
            set(candidate["official_evidence_ids"])
            | {item["evidence_id"] for item in new_evidence}
        )
        candidate["discovery_source_ids"] = sorted(
            set(candidate["discovery_source_ids"])
            | {source_by_url[item["url"]] for item in new_evidence}
        )
    return sorted(candidates, key=lambda item: item["candidate_id"])


def build_readme(candidates: list[dict[str, Any]]) -> str:
    counts = Counter(item["decision"] for item in candidates)
    rows = "\n".join(
        f"| `{item['candidate_id']}` | {item['name']} | `{item['decision']}` | "
        f"{item['destination'] or 'não se aplica'} |"
        for item in candidates
    )
    return f"""# Validação do shard 1: issue #218

Este shard valida os 19 candidatos atribuídos por `sha256(candidate_id) mod 3 = 1`.
A data de corte é 30 de julho de 2026.

## Resultado

| Decisão | Total |
| --- | ---: |
| `duplicate` | {counts['duplicate']} |
| `eligible` | {counts['eligible']} |
| `routed_accelerators` | {counts['routed_accelerators']} |
| `routed_angel_networks` | {counts['routed_angel_networks']} |
| `insufficient_evidence` | {counts['insufficient_evidence']} |
| **Total** | **{len(candidates)}** |

## Método

Cada ID foi reaberto individualmente em fonte oficial ou institucional atual.
Elegibilidade exigiu as cinco claims oficiais do contrato: identidade, investimento
direto, recorrência, atividade observada entre 2024-07-30 e 2026-07-30 e relação
explícita com o Brasil. Data de acesso em página sem data não foi usada como
atividade.

Não houve consulta à CVM. O arquivo local de startups não foi lido nem usado.
Notícias não sustentam nenhuma decisão deste shard. Cheque, estágio, tese e
recorrência ausentes não foram estimados.

`source-inventory.jsonl` registra {len(SOURCES)} fontes não-CVM e a chave SHA-256 da URL final.
`evidence.jsonl` contém {len(EVIDENCE)} evidências oficiais. `candidates.jsonl` é um overlay
completo dos 19 IDs e preserva as fontes e evidências anteriores.

## Decisões por candidato

| ID | Nome | Decisão | Destino |
| --- | --- | --- | --- |
{rows}

## Pendências explícitas

- Good Karma: resolver a mudança cadastral para Just Climate e a continuidade da
  identidade pública e da carteira.
- 30N, Canaan, Lightspeed, Lux e Sagol: uma investida, presença comercial ou
  menção regional isolada não prova acesso recorrente ao Brasil.
- FHE Ventures: faltam fonte oficial substantiva, veículo, carteira, recorrência
  e atividade datada.
- Jatobá: faltam primeiro investimento, carteira e atividade oficial datada do
  Fundo Impacto Amazônia.

## Fronteiras de categoria

- AgroVen foi encaminhada para `epic-63-angel-networks`: o site informa que os
  aportes são feitos pelos membros do clube.
- IPÊ Investe foi encaminhada para `epic-62-accelerators`: a fonte descreve a
  primeira edição de um programa de aceleração com aportes por fases.
- Mundi Ventures foi tratada como organização investidora. LatAm Fund I continua
  preservado em `vehicle_ids`, sem gerar um segundo perfil para o veículo.
"""


def main() -> None:
    candidates = build_candidates()
    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(
        OUT / "source-inventory.jsonl",
        sorted(SOURCES, key=lambda item: item["source_id"]),
    )
    write_jsonl(
        OUT / "evidence.jsonl",
        sorted(EVIDENCE, key=lambda item: item["evidence_id"]),
    )
    write_jsonl(OUT / "candidates.jsonl", candidates)
    (OUT / "README.md").write_text(
        build_readme(candidates), encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
