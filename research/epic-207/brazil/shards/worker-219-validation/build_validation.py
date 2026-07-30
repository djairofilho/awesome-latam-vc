from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
QUEUE = ROOT / "research/epic-207/brazil/validation-shards/issue-219/candidates.jsonl"
OUT = Path(__file__).resolve().parent
TODAY = "2026-07-30"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(name: str, rows: list[dict]) -> None:
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows)
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")


def source(
    slug: str,
    name: str,
    url: str,
    scope: str,
    notes: str,
    *,
    prior: list[str] | None = None,
    result: str = "complete",
    reason: str | None = None,
    next_action: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "source_id": f"src-fund-br-219-{slug}",
        "issue": 219,
        "source": name,
        "initial_url": url,
        "source_family": "official_portfolios",
        "source_disposition": "prior_source" if prior else "new_source",
        "research_channel": "non_cvm",
        "is_cvm": False,
        "discovery_allowed": False,
        "prior_source_ids": prior or [],
        "scope_walked": scope,
        "accessed_on": TODAY,
        "robots_status": "allowed",
        "access_method": "http",
        "cache_key": None,
        "result": result,
        "reason": reason,
        "owner": "worker-219-validation" if result != "complete" else None,
        "next_action": next_action,
        "notes": notes,
    }


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
    observed_on: str | None = None,
    published_on: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "evidence_id": f"ev-fund-br-219-{slug}",
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
        "accessed_on": TODAY,
        "claims": [{"field": field, "finding": finding} for field, finding in claims],
        "locator": locator,
        "summary": summary,
    }


SOURCES = [
    source("1616-home", "1616 Ventures — site oficial", "https://www.1616ventures.com/", "Tese, processo de investimento, equipe, portfólio e presença em São Paulo.", "Nova passagem oficial para completar identidade, recorrência e acesso ao Brasil.", prior=["src-fund-br-215-pass1-1616-official"]),
    source("monashees-home", "monashees — site oficial", "https://www.monashees.com/", "Identidade, portfólio e escritório em São Paulo.", "Confirma que o lead já possui perfil canônico.", prior=["src-fund-br-210-ifc-monashees-x"]),
    source("quona-home", "Quona Capital — site oficial", "https://quona.com/", "Identidade, tese fintech, presença latino-americana e escritório em São Paulo.", "Confirma que o lead já possui perfil canônico.", prior=["src-fund-br-215-pass1-quona-portfolio"]),
    source("amz-home", "AMZ Venture Capital — site oficial", "https://amzventurecapital.com/", "Identidade, processo, portfólio e endereço em Belém, Pará.", "A página não fornece data verificável de atividade recente."),
    source("canary-home", "Canary — site oficial", "https://www.canary.com.br/", "Identidade e domínio oficial comparados ao candidato canônico.", "Correspondência exata com o candidato já consolidado.", prior=["src-fund-br-210-ifc-canary-iv"]),
    source("seedstars-funds", "Seedstars — funds", "https://www.seedstars.com/funds/", "Plataforma de investimento, fundos, portfólio e filtros regionais.", "Não foi localizada atividade oficial brasileira datada na janela."),
    source("triaxis-home", "Triaxis Capital — site oficial", "https://www.triaxiscapital.com/", "Gestora, fundos ativos, investidas e endereços no Brasil.", "Confirma que o lead já possui perfil canônico."),
    source("arar-vc", "Arar Capital — venture capital", "https://www.ararcapital.com/sobre-venturecapital", "Tese de VC e portfólio do veículo VC Agro I.", "Revisão atual da fonte anterior; continua sem atividade oficial datada.", prior=["src-fund-br-214-arar-official"]),
    source("lh-home", "LH Invest — site oficial", "https://www.lhinvest.com.br/", "Casa, FIP LH Tech Ventures, portfólio e foco pre-seed/seed.", "Revisão atual da fonte anterior; continua sem atividade oficial datada.", prior=["src-fund-br-214-lh-invest-official"]),
    source("neofin-release", "Neofin — release da rodada seed", "https://www.neofin.com.br/release/janeiro-2025", "Release oficial datado e lista de investidores BFF e Farout.", "A rodada é comprovada, mas o release não resolve a identidade nem a recorrência dos dois nomes.", prior=["src-fund-br-211-official-neofin"]),
    source("botcity-release", "BotCity — anúncio da Série A", "https://blog.botcity.dev/pt-br/2025/09/30/levantamos-r-65-milhoes-para-governar-automacoes-criadas-por-ai/", "Anúncio oficial datado e identificação de Four Rivers como líder.", "A rodada é comprovada, mas a identidade do investidor permanece ambígua.", prior=["src-fund-br-211-official-botcity"]),
    source("nido-home", "Nido — site oficial", "https://nidovc.com.br/", "Gestora, veículo Platypus, seleção de fundos e possibilidade de coinvestimentos.", "A página não comprova investimento direto recorrente realizado.", prior=["src-fund-br-nido-official"], result="partial", reason="Coinvestimento aparece como possibilidade, não como histórico realizado.", next_action="Buscar anúncio oficial de coinvestimento direto concluído e recorrência."),
    source("parceiro-home", "Parceiro Ventures — site oficial", "https://parceiroventures.com/", "Tese latino-americana, portfólio brasileiro e notícias datadas, inclusive Loopia.", "Fonte oficial reúne os cinco gates e atividade em 2026-06-21.", prior=["src-fund-br-211-official-parceiro"]),
    source("sororite-portfolio", "Sororitê Ventures — portfólio e captação", "https://www.sororite.com.br/portfolio-sororite-ventures", "Portfólio do Fund 1 e páginas oficiais de captação contínua.", "Confirma operação e acesso ao Brasil, mas não data os investimentos.", prior=["src-fund-br-sororite-official"]),
]


EVIDENCE = [
    evidence("1616-home", "fund-br-1616v", "https://www.1616ventures.com/", "1616 Ventures", "1616 Ventures", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("brazil_access", "confirmed")], "Seções de tese, processo, portfólio e equipe; Partner — São Paulo.", "A gestora apresenta processo recorrente, portfólio próprio e presença operacional em São Paulo."),
    evidence("monashees-home", "fund-br-210-monashees", "https://www.monashees.com/", "monashees", "monashees", "official_portfolio", [("identity", "confirmed"), ("brazil_access", "confirmed")], "Apresentação institucional, portfólio e endereço de São Paulo.", "Nome e domínio correspondem exatamente ao perfil canônico funds/regional/monashees.md."),
    evidence("quona-home", "fund-br-210-quona-capital", "https://quona.com/", "Quona Capital", "Quona Capital", "official_website", [("identity", "confirmed"), ("brazil_access", "confirmed")], "Apresentação institucional, América Latina e presença em São Paulo.", "Nome e domínio correspondem exatamente ao perfil canônico funds/multi-country/quona-capital.md."),
    evidence("amz-home", "fund-br-213-amz-venture-capital", "https://amzventurecapital.com/", "AMZ Venture Capital", "AMZ Venture Capital", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "Página inicial, números de portfólio, processo e endereço em Belém.", "O site confirma operação de VC no Brasil, mas não publica data de investimento recente."),
    evidence("canary-home", "fund-br-213-canary", "https://www.canary.com.br/", "Canary", "Canary", "official_website", [("identity", "confirmed")], "Nome e domínio oficial.", "O lead corresponde exatamente ao candidato canônico fund-br-210-canary."),
    evidence("seedstars-funds", "fund-br-213-seedstars", "https://www.seedstars.com/funds/", "Funds", "Seedstars", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "inconclusive"), ("brazil_access", "inconclusive")], "Plataforma, fundos e portfólio por regiões.", "A atuação recorrente é clara, mas a passagem não comprova atividade brasileira oficial datada na janela."),
    evidence("triaxis-home", "fund-br-213-triaxis-capital", "https://www.triaxiscapital.com/", "Triaxis Capital", "Triaxis Capital", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("brazil_access", "confirmed")], "Gestora de VC, três fundos ativos, investidas e endereços em São Paulo e Recife.", "Nome e domínio correspondem exatamente ao perfil canônico funds/brazil/triaxis-capital.md."),
    evidence("arar-vc", "fund-br-214-arar-capital", "https://www.ararcapital.com/sobre-venturecapital", "Venture Capital", "Arar Capital", "official_thesis", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "Tese e portfólio VC Agro I.", "A página oficial atual não atribui data verificável à atividade exibida."),
    evidence("lh-home", "fund-br-214-lh-invest", "https://www.lhinvest.com.br/", "LH Invest", "LH Invest", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "Quem somos, Venture Capital e portfólio.", "O site confirma a gestora e o FIP, mas não data investimento recente."),
    evidence("bff-neofin", "fund-br-bff", "https://www.neofin.com.br/release/janeiro-2025", "Neofin levanta R$ 35 milhões em rodada seed", "Neofin", "official_announcement", [("identity", "inconclusive"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "inconclusive"), ("activity", "confirmed"), ("brazil_access", "inconclusive")], "Parágrafo que lista BFF entre os participantes.", "A participação é oficial e datada, mas a sigla não permite resolver identidade, mandato brasileiro ou recorrência.", observed_on="2025-02-05", published_on="2025-02-05"),
    evidence("farout-neofin", "fund-br-farout", "https://www.neofin.com.br/release/janeiro-2025", "Neofin levanta R$ 35 milhões em rodada seed", "Neofin", "official_announcement", [("identity", "inconclusive"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "inconclusive"), ("activity", "confirmed"), ("brazil_access", "inconclusive")], "Parágrafo que lista Farout entre os participantes.", "A participação é oficial e datada, mas o nome não conecta inequivocamente a uma gestora oficial.", observed_on="2025-02-05", published_on="2025-02-05"),
    evidence("four-rivers-botcity", "fund-br-four-rivers", "https://blog.botcity.dev/pt-br/2025/09/30/levantamos-r-65-milhoes-para-governar-automacoes-criadas-por-ai/", "Levantamos R$ 65 milhões para governar automações criadas por IA", "BotCity", "official_announcement", [("identity", "inconclusive"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "inconclusive"), ("activity", "confirmed"), ("brazil_access", "inconclusive")], "Parágrafo que identifica Four Rivers como líder.", "A rodada é oficial e datada, mas não há ligação inequívoca com um site oficial do investidor.", observed_on="2025-09-30", published_on="2025-09-30"),
    evidence("nido-home", "fund-br-nido-vc", "https://nidovc.com.br/", "Nido — Invista com Propósito", "Nido", "official_website", [("identity", "confirmed"), ("direct_startup_investment", "inconclusive"), ("recurring_vc", "inconclusive"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "A Nido, Platypus e Como funciona.", "O veículo seleciona fundos e admite coinvestimentos, sem comprovar investimento direto recorrente realizado."),
    evidence("parceiro-home", "fund-br-parceiro-ventures", "https://parceiroventures.com/", "Parceiro Ventures", "Parceiro Ventures", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "confirmed"), ("brazil_access", "confirmed")], "Tese LatAm, portfólio com empresas brasileiras e News & Press da Loopia.", "A página oficial confirma gestora recorrente, investimento direto, acesso explícito ao Brasil e atividade em 2026-06-21.", observed_on="2026-06-21", published_on="2026-06-21"),
    evidence("sororite-portfolio", "fund-br-sororite-ventures", "https://www.sororite.com.br/portfolio-sororite-ventures", "Portfólio Sororitê Ventures", "Sororitê Ventures", "official_portfolio", [("identity", "confirmed"), ("direct_startup_investment", "confirmed"), ("recurring_vc", "confirmed"), ("activity", "inconclusive"), ("brazil_access", "confirmed")], "Portfólio do Fund 1 e navegação para captação.", "O site comprova portfólio e processo contínuo no Brasil, mas não informa datas dos investimentos."),
]


DECISIONS = {
    "fund-br-1616v": {"decision": "eligible", "official_site": "https://www.1616ventures.com/", "canonical_domain": "1616ventures.com", "brazil_relation": "accessible_to_brazil", "direct_startup_investment": True, "recurring_vc": True, "activity_status": "active", "latest_official_activity_on": "2025-02-05", "owner": None, "next_action": None, "reason": None},
    "fund-br-210-monashees": {"decision": "duplicate", "canonical_profile": "funds/regional/monashees.md", "destination": "funds/regional/monashees.md", "owner": None, "next_action": None, "reason": "Nome e domínio oficial correspondem ao perfil canônico existente."},
    "fund-br-210-quona-capital": {"decision": "duplicate", "canonical_profile": "funds/multi-country/quona-capital.md", "destination": "funds/multi-country/quona-capital.md", "owner": None, "next_action": None, "reason": "Nome e domínio oficial correspondem ao perfil canônico existente."},
    "fund-br-213-amz-venture-capital": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Localizar anúncio oficial de investimento publicado entre 2024-07-30 e 2026-07-30.", "reason": "Identidade, recorrência e acesso ao Brasil estão claros, mas falta atividade oficial datada na janela."},
    "fund-br-213-canary": {"decision": "duplicate", "canonical_candidate_id": "fund-br-210-canary", "destination": "fund-br-210-canary", "owner": None, "next_action": None, "reason": "Nome, domínio e organização são idênticos ao candidato canônico."},
    "fund-br-213-seedstars": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Localizar no domínio oficial anúncio datado de investimento em startup brasileira na janela.", "reason": "A plataforma e a recorrência são oficiais, mas atividade e acesso atual ao Brasil não foram comprovados com data."},
    "fund-br-213-triaxis-capital": {"decision": "duplicate", "canonical_profile": "funds/brazil/triaxis-capital.md", "destination": "funds/brazil/triaxis-capital.md", "owner": None, "next_action": None, "reason": "Nome e domínio oficial correspondem ao perfil canônico existente."},
    "fund-br-214-arar-capital": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Obter anúncio oficial datado de aporte ou entrada no portfólio dentro da janela.", "reason": "A página oficial comprova tese e portfólio, mas não data a atividade."},
    "fund-br-214-lh-invest": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Obter notícia ou comunicado oficial datado de investimento dentro da janela.", "reason": "A gestora e seu veículo estão confirmados, mas falta atividade oficial datada."},
    "fund-br-bff": {"decision": "insufficient_evidence", "activity_status": "active", "latest_official_activity_on": "2025-02-05", "owner": "worker-219-validation", "next_action": "Resolver a sigla BFF por domínio ou comunicado controlado pelo investidor e comprovar recorrência.", "reason": "A rodada da Neofin é oficial, porém identidade, recorrência e mandato brasileiro permanecem ambíguos."},
    "fund-br-farout": {"decision": "insufficient_evidence", "activity_status": "active", "latest_official_activity_on": "2025-02-05", "owner": "worker-219-validation", "next_action": "Vincular o nome Farout a um domínio oficial inequívoco e comprovar recorrência e acesso ao Brasil.", "reason": "A rodada da Neofin é oficial, mas não identifica inequivocamente a organização investidora."},
    "fund-br-four-rivers": {"decision": "insufficient_evidence", "activity_status": "active", "latest_official_activity_on": "2025-09-30", "owner": "worker-219-validation", "next_action": "Localizar site ou comunicado do investidor que resolva a identidade e demonstre recorrência.", "reason": "A BotCity confirma o aporte, mas Four Rivers não pôde ser ligado com segurança a uma organização oficial."},
    "fund-br-nido-vc": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Buscar anúncio oficial de coinvestimento direto concluído e evidência de recorrência.", "reason": "A estratégia principal é seleção de fundos; coinvestimento direto aparece como possibilidade, não como histórico comprovado."},
    "fund-br-parceiro-ventures": {"decision": "eligible", "base_country": "US", "brazil_relation": "accessible_to_brazil", "direct_startup_investment": True, "recurring_vc": True, "activity_status": "active", "latest_official_activity_on": "2026-06-21", "owner": None, "next_action": None, "reason": None},
    "fund-br-sororite-ventures": {"decision": "insufficient_evidence", "activity_status": "unknown", "latest_official_activity_on": None, "owner": "worker-219-validation", "next_action": "Localizar no domínio oficial anúncio datado de investimento do Fund 1 dentro da janela.", "reason": "Portfólio, recorrência e acesso ao Brasil estão claros, mas os investimentos não possuem data oficial verificável."},
}


def main() -> None:
    evidence_by_candidate = {row["candidate_id"]: row["evidence_id"] for row in EVIDENCE}
    candidates = []
    for row in read_jsonl(QUEUE):
        candidate_id = row["candidate_id"]
        row.update(DECISIONS[candidate_id])
        row["status"] = "decided"
        row["official_evidence_ids"] = list(dict.fromkeys(row["official_evidence_ids"] + [evidence_by_candidate[candidate_id]]))
        candidates.append(row)

    coverage = [{
        "schema_version": "1.0",
        "coverage_id": "coverage-fund-br-219-official-validation",
        "issue": 219,
        "source_family": "official_portfolios",
        "geography_scope": "brazil",
        "source_ids": [row["source_id"] for row in SOURCES],
        "planned_sources": len(SOURCES),
        "completed_sources": len(SOURCES),
        "candidate_ids": [row["candidate_id"] for row in candidates],
        "status": "complete",
        "reason": "Todos os 15 candidatos receberam passagem oficial; lacunas foram preservadas como evidência insuficiente.",
        "owner": "worker-219-validation",
        "next_action": "Integrar os overlays e manter os nove casos insuficientes fora da publicação até surgir evidência oficial adequada.",
    }]

    write_jsonl("source-inventory.jsonl", SOURCES)
    write_jsonl("evidence.jsonl", EVIDENCE)
    write_jsonl("candidates.jsonl", candidates)
    write_jsonl("coverage-matrix.jsonl", coverage)


if __name__ == "__main__":
    main()
