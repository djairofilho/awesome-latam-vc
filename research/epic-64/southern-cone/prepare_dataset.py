"""Materialize the reviewed Southern Cone platform audit into frozen shards."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
SHARDS = ROOT / "shards"
TODAY = "2026-07-27"
RUN_ID = "run-platforms-southern-cone-2026"


def write_jsonl(path: Path, records: list[dict]) -> None:
    text = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in sorted(
            records,
            key=lambda item: (
                item.get("platform_id")
                or item.get("evidence_id")
                or item.get("source_id")
                or item.get("country")
                or item.get("task_id")
                or item.get("run_id")
            ),
        )
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def evidence(
    evidence_id: str,
    platform_id: str,
    subject_type: str,
    subject_id: str,
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
) -> dict:
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "platform_id": platform_id,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "url": url,
        "title": title,
        "publisher": publisher,
        "source_type": source_type,
        "published_on": published_on,
        "observed_on": observed_on,
        "accessed_on": TODAY,
        "claims": [{"field": field, "finding": finding} for field, finding in claims],
        "locator": locator,
        "summary": summary,
    }


def candidate(
    slug: str,
    country: str,
    legal_name: str,
    brand_name: str,
    domain: str,
    official_url: str,
    founder_route_url: str | None,
    source_ids: list[str],
    decision: str,
    reason: str | None,
    *,
    products: list[dict] | None = None,
    offers: list[dict] | None = None,
    regulatory_records: list[dict] | None = None,
    evidence_ids: list[str] | None = None,
    activity_ids: list[str] | None = None,
    route_ids: list[str] | None = None,
    activity_status: str = "unknown",
    activity_on: str | None = None,
    latam_route: bool | None = None,
    owner: str | None = None,
    next_action: str | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "platform_id": f"plat-{slug}",
        "operator": {
            "operator_id": f"op-{slug}",
            "legal_name": legal_name,
            "jurisdiction": country,
            "official_url": official_url,
        },
        "brand": {"brand_id": f"brand-{slug}", "name": brand_name, "aliases": []},
        "platform": {
            "name": brand_name,
            "canonical_domain": domain,
            "official_url": official_url,
            "founder_route_url": founder_route_url,
            "declared_countries": [country],
        },
        "products": products or [],
        "offers": offers or [],
        "regulatory_records": regulatory_records or [],
        "discovery_source_ids": source_ids,
        "official_evidence_ids": evidence_ids or [],
        "activity_evidence_ids": activity_ids or [],
        "route_evidence_ids": route_ids or [],
        "discovered_on": TODAY,
        "activity_status": activity_status,
        "last_official_activity_on": activity_on,
        "latam_founder_route": latam_route,
        "status": "decided",
        "decision": decision,
        "reason": reason,
        "canonical_platform_id": None,
        "canonical_profile": None,
        "owner": owner,
        "next_action": next_action,
    }


def product(slug: str, name: str, instrument: str, status: str) -> dict:
    return {
        "product_id": f"prod-{slug}",
        "name": name,
        "instrument_type": instrument,
        "status": status,
    }


def build_candidates() -> dict[str, list[dict]]:
    return {
        "worker-ar-official-platform": [
            candidate(
                "crowdium",
                "AR",
                "Crowdium S.R.L.",
                "Crowdium",
                "crowdium.com.ar",
                "https://www.crowdium.com.ar/",
                None,
                ["src-ar-official-platform"],
                "excluded",
                "A rota oficial é um produto imobiliário voltado a investidores; não há fluxo estruturado para startups captarem recursos.",
                products=[
                    product("crowdium-real-estate", "Investimento imobiliário fracionado", "other", "active")
                ],
                evidence_ids=["ev-crowdium-product", "ev-crowdium-operator"],
                activity_ids=["ev-crowdium-product"],
                activity_status="open",
                activity_on=TODAY,
                latam_route=False,
            ),
            candidate(
                "afluenta-argentina",
                "AR",
                "Afluenta S.A.",
                "Afluenta",
                "afluenta.com",
                "https://www.afluenta.com/",
                "https://www.afluenta.com/solicitar",
                ["src-ar-afluenta"],
                "excluded",
                "A rota é crédito P2P genérico para pessoas e empresas, sem fluxo oficial específico para startups.",
                products=[
                    product("afluenta-credit", "Crédito colaborativo", "debt crowdfunding", "active")
                ],
                evidence_ids=["ev-afluenta-route", "ev-afluenta-operator"],
                activity_ids=["ev-afluenta-route"],
                activity_status="open",
                activity_on=TODAY,
                latam_route=True,
            ),
        ],
        "worker-cl-official-platform": [
            candidate(
                "broota",
                "CL",
                "BROOTA PFC SpA",
                "Broota",
                "broota.com",
                "https://inversion.broota.com/",
                "https://inversion.broota.com/levantar-capital/",
                ["src-cl-official-platform"],
                "eligible",
                None,
                products=[
                    product("broota-equity", "Rondas de inversión", "equity crowdfunding", "recurring"),
                    product("broota-convertible", "Instrumentos convertibles", "convertible", "recurring"),
                ],
                offers=[
                    {
                        "offer_id": "offer-broota-blanco",
                        "product_id": "prod-broota-convertible",
                        "name": "Blanco",
                        "status": "closed",
                        "official_url": "https://inversion.broota.com/campaign/blanco/",
                        "profile_eligible": False,
                    }
                ],
                evidence_ids=["ev-broota-route", "ev-broota-activity", "ev-broota-offer"],
                activity_ids=["ev-broota-activity"],
                route_ids=["ev-broota-route"],
                activity_status="open",
                activity_on=TODAY,
                latam_route=True,
            ),
            candidate(
                "redcapital-chile",
                "CL",
                "RedCapital SpA",
                "RedCapital",
                "redcapital.cl",
                "https://redcapital.cl/",
                "https://redcapital.cl/solicitar",
                ["src-cl-redcapital"],
                "insufficient_evidence",
                "Há rota estruturada para PMEs, mas as fontes oficiais auditadas não confirmam uma rota específica para startups.",
                products=[
                    product("redcapital-credit", "Financiamiento para pymes", "debt crowdfunding", "active")
                ],
                evidence_ids=["ev-redcapital-route"],
                activity_ids=["ev-redcapital-route"],
                activity_status="open",
                activity_on=TODAY,
                latam_route=True,
                owner="issue-93-maintainer",
                next_action="Obter confirmação oficial de que startups podem usar a rota de solicitação sem presumir equivalência entre PME e startup.",
            ),
            candidate(
                "cumplo-chile",
                "CL",
                "Cumplo Chile S.A.",
                "Cumplo",
                "cumplo.cl",
                "https://secure.cumplo.cl/",
                "https://secure.cumplo.cl/publica-tu-credito/empresas",
                ["src-cl-cumplo"],
                "insufficient_evidence",
                "Há crédito empresarial com investidores da plataforma, mas não foi encontrada confirmação oficial de uma rota específica para startups.",
                products=[
                    product("cumplo-credit", "Crédito para empresas", "debt crowdfunding", "active")
                ],
                evidence_ids=["ev-cumplo-route", "ev-cumplo-operator"],
                activity_ids=["ev-cumplo-route"],
                activity_status="open",
                activity_on=TODAY,
                latam_route=True,
                owner="issue-93-maintainer",
                next_action="Solicitar à Cumplo confirmação oficial sobre elegibilidade de startups e registrar critérios de estágio ou receita.",
            ),
        ],
        "worker-py-official-platform": [
            candidate(
                "nexoos-paraguay",
                "PY",
                "Nexoos Group S.A.",
                "Nexoos Paraguay",
                "nexoos.com.py",
                "https://www.nexoos.com.py/",
                None,
                ["src-py-official-platform"],
                "inactive",
                "O domínio paraguaio estava indisponível e a história oficial atual da Nexoos descreve a operação posterior no Brasil, sem atividade recente comprovada no Paraguai.",
                evidence_ids=["ev-nexoos-history"],
                activity_status="inactive",
                latam_route=True,
            )
        ],
        "worker-py-public-ecosystem": [
            candidate(
                "koga-impact-lab",
                "PY",
                "KOGA – Impact Lab",
                "KOGA",
                "koga.com.py",
                "https://www.koga.com.py/",
                None,
                ["src-py-public-ecosystem"],
                "other_category",
                "A fonte pública classifica a organização como incubadora e aceleradora; a entidade pertence ao escopo da epic #62, não ao de plataformas da epic #64.",
                evidence_ids=["ev-koga-category"],
                activity_status="unknown",
                latam_route=False,
            )
        ],
        "worker-uy-official-platform": [
            candidate(
                "crowder-uruguay",
                "UY",
                "CROWDER PLATAFORMA DE FINANCIAMIENTO COLECTIVO S.A.",
                "Crowder",
                "crowder.fund",
                "https://crowder.fund/",
                "https://docs.crowder.fund/d08efa00-6be6-431e-ace6-6377e1cd1cd0_Informaci__n_a_presentar_por_Emisores.pdf",
                ["src-uy-official-platform", "src-uy-regulator"],
                "eligible",
                None,
                products=[
                    product("crowder-equity", "Emisiones de capital", "equity crowdfunding", "active"),
                    product("crowder-debt", "Emisiones de deuda", "debt crowdfunding", "active"),
                    product("crowder-mixed", "Emisiones mixtas", "convertible", "active"),
                ],
                regulatory_records=[
                    {
                        "regulatory_id": "reg-crowder-bcu-4261",
                        "authority": "Banco Central del Uruguay",
                        "jurisdiction": "UY",
                        "registration_number": "4261",
                        "claimed_status": "authorized",
                        "evidence_id": "ev-crowder-regulatory",
                    }
                ],
                evidence_ids=["ev-crowder-route", "ev-crowder-activity", "ev-crowder-regulatory"],
                activity_ids=["ev-crowder-activity"],
                route_ids=["ev-crowder-route"],
                activity_status="open",
                activity_on="2026-02-06",
                latam_route=True,
            )
        ],
    }


def build_evidence() -> dict[str, list[dict]]:
    confirmed = "confirmed"
    refuted = "refuted"
    return {
        "worker-ar-official-platform": [
            evidence(
                "ev-crowdium-product", "plat-crowdium", "product", "prod-crowdium-real-estate",
                "https://www.crowdium.com.ar/", "Crowdium", "Crowdium", "official_platform",
                [("product_instrument", confirmed), ("structured_founder_route", refuted), ("recent_activity", confirmed)],
                "Página inicial e projetos", "A plataforma oferece participações em fideicomissos imobiliários a investidores, não captação para startups.", observed_on=TODAY,
            ),
            evidence(
                "ev-crowdium-operator", "plat-crowdium", "operator", "op-crowdium",
                "https://www.crowdium.com.ar/terminos-y-condiciones", "Términos y condiciones", "Crowdium", "official_operator",
                [("legal_operator", confirmed)], "Identificação do operador", "Os termos identificam Crowdium S.R.L. como operador do serviço.",
            ),
            evidence(
                "ev-afluenta-route", "plat-afluenta-argentina", "platform", "plat-afluenta-argentina",
                "https://www.afluenta.com/solicitar", "Solicitar crédito", "Afluenta", "official_platform",
                [("structured_founder_route", refuted), ("latam_access", confirmed), ("recent_activity", confirmed)],
                "Formulário de solicitação", "A rota aberta solicita crédito na Argentina, mas não apresenta fluxo específico para startups.", observed_on=TODAY,
            ),
            evidence(
                "ev-afluenta-operator", "plat-afluenta-argentina", "operator", "op-afluenta-argentina",
                "https://www.afluenta.com/legal", "Información legal", "Afluenta", "official_operator",
                [("legal_operator", confirmed)], "Aviso legal", "A página identifica Afluenta S.A. como responsável pela plataforma.",
            ),
        ],
        "worker-cl-official-platform": [
            evidence(
                "ev-broota-route", "plat-broota", "platform", "plat-broota",
                "https://inversion.broota.com/preguntas-frecuentes/", "Preguntas frecuentes", "Broota", "official_platform",
                [("structured_founder_route", confirmed), ("latam_access", confirmed), ("product_instrument", confirmed)],
                "Seção para startups", "A Broota descreve uma plataforma chilena em que startups solicitam financiamento por instrumentos de investimento.",
            ),
            evidence(
                "ev-broota-activity", "plat-broota", "platform", "plat-broota",
                "https://inversion.broota.com/levantar-capital/", "Levantar capital", "Broota", "official_platform",
                [("structured_founder_route", confirmed), ("latam_access", confirmed), ("recent_activity", confirmed)],
                "Convocação 2026", "A rota oficial aceitava candidaturas de startups em 2026 na data de corte.", observed_on=TODAY,
            ),
            evidence(
                "ev-broota-offer", "plat-broota", "offer", "offer-broota-blanco",
                "https://inversion.broota.com/campaign/blanco/", "Blanco", "Broota", "official_platform",
                [("offer_status", confirmed), ("product_instrument", confirmed)],
                "Estado da campanha", "A campanha Blanco aparece encerrada e usa instrumento SAFE; a oferta não é um perfil.",
            ),
            evidence(
                "ev-redcapital-route", "plat-redcapital-chile", "platform", "plat-redcapital-chile",
                "https://redcapital.cl/solicitar", "Solicitar financiamiento", "RedCapital", "official_platform",
                [("structured_founder_route", "not_disclosed"), ("latam_access", confirmed), ("recent_activity", confirmed)],
                "Solicitação para pymes", "A rota aberta atende PMEs chilenas, mas não declara startups como público específico.", observed_on=TODAY,
            ),
            evidence(
                "ev-cumplo-route", "plat-cumplo-chile", "platform", "plat-cumplo-chile",
                "https://secure.cumplo.cl/publica-tu-credito/empresas", "Financiamiento para empresas", "Cumplo", "official_platform",
                [("structured_founder_route", "not_disclosed"), ("latam_access", confirmed), ("recent_activity", confirmed)],
                "Crédito para empresas", "A rota aberta oferece capital de giro e antecipação de faturas, sem declarar uma rota específica para startups.", observed_on=TODAY,
            ),
            evidence(
                "ev-cumplo-operator", "plat-cumplo-chile", "operator", "op-cumplo-chile",
                "https://secure.cumplo.cl/politicas-de-privacidad", "Políticas de privacidad", "Cumplo", "official_operator",
                [("legal_operator", confirmed)], "Responsável pelo tratamento", "A política identifica Cumplo Chile S.A. como operador.",
            ),
        ],
        "worker-py-official-platform": [
            evidence(
                "ev-nexoos-history", "plat-nexoos-paraguay", "platform", "plat-nexoos-paraguay",
                "https://www.nexoos.com.br/quem-somos", "Quem somos", "Nexoos", "official_operator",
                [("geography", confirmed), ("recent_activity", refuted)],
                "História da empresa", "A história oficial menciona o piloto no Paraguai e a operação posterior no Brasil, sem comprovar atividade paraguaia recente.",
            )
        ],
        "worker-py-public-ecosystem": [
            evidence(
                "ev-koga-category", "plat-koga-impact-lab", "platform", "plat-koga-impact-lab",
                "https://portalemprendedor.mic.gov.py/institucion.php?id=25", "KOGA – Impact Lab", "Ministerio de Industria y Comercio", "official_document",
                [("structured_founder_route", refuted), ("geography", confirmed)],
                "Descrição institucional", "O portal público descreve KOGA como incubadora e aceleradora com programas de inovação.",
            )
        ],
        "worker-uy-official-platform": [
            evidence(
                "ev-crowder-route", "plat-crowder-uruguay", "platform", "plat-crowder-uruguay",
                "https://docs.crowder.fund/d08efa00-6be6-431e-ace6-6377e1cd1cd0_Informaci__n_a_presentar_por_Emisores.pdf",
                "Información a presentar por emisores", "Crowder", "official_document",
                [("structured_founder_route", confirmed), ("latam_access", confirmed), ("product_instrument", confirmed)],
                "Requisitos de emisores", "O documento oficial define a rota para empresas uruguaias emitirem capital, dívida ou instrumentos mistos.",
            ),
            evidence(
                "ev-crowder-activity", "plat-crowder-uruguay", "platform", "plat-crowder-uruguay",
                "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/InformacionInstitucion.aspx?nroinst=4261",
                "Información de institución 4261", "Banco Central del Uruguay", "official_regulator",
                [("recent_activity", confirmed), ("geography", confirmed)],
                "Últimos eventos informados", "O registro oficial ativo da Crowder apresenta evento em 6 de fevereiro de 2026.", published_on="2026-02-06", observed_on="2026-02-06",
            ),
            evidence(
                "ev-crowder-regulatory", "plat-crowder-uruguay", "regulatory_record", "reg-crowder-bcu-4261",
                "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/InformacionInstitucion.aspx?nroinst=4261",
                "Información de institución 4261", "Banco Central del Uruguay", "official_regulator",
                [("regulatory_status", confirmed), ("legal_operator", confirmed), ("geography", confirmed)],
                "Identificação e atividades habilitadas", "O BCU registra CROWDER PLATAFORMA DE FINANCIAMIENTO COLECTIVO S.A. sob o código 4261, com atividades ativas.",
            ),
        ],
    }


SOURCE_RESULTS = {
    ("AR", "regulator"): ("Comisión Nacional de Valores", "https://www.argentina.gob.ar/cnv/registros-publicos", "Registros públicos e marco vigente de plataformas de financiamiento colectivo."),
    ("AR", "public_ecosystem"): ("Ministerio de Economía", "https://www.argentina.gob.ar/economia/inclusion-financiera/sistema-de-financiamiento-colectivo", "Descrição pública do sistema de financiamento coletivo para empreendedores."),
    ("AR", "official_platform"): ("Crowdium", "https://www.crowdium.com.ar/", "Página institucional, projetos e termos do operador."),
    ("AR", "discovery"): ("ARCAP", "https://arcap.org/", "Mapa associativo revisado para colisões com fundos e investidores."),
    ("CL", "regulator"): ("Comisión para el Mercado Financiero", "https://www.cmfchile.cl/portal/principal/613/w3-propertyvalue-43581.html", "Registro de Prestadores de Servicios Financieros e requisitos da Lei Fintec."),
    ("CL", "public_ecosystem"): ("CORFO", "https://www.corfo.cl/sites/cpp/homecorfo", "Programas públicos revisados para separar apoio estatal da rota de plataforma."),
    ("CL", "official_platform"): ("Broota", "https://inversion.broota.com/", "FAQ, rota de captação, produtos e campanhas."),
    ("CL", "discovery"): ("ACVC", "https://acvc.cl/", "Mapa associativo revisado para colisões com fundos."),
    ("PY", "regulator"): ("Banco Central del Paraguay", "https://www.bcp.gov.py/web/institucional/w/ley-del-mercado-de-valores-y-productos-fortalece-proteccion-al-inversionista-y-consolida-supervision-basada-en-riesgos-resalta-superintendente", "Lei 7572/2025 e previsão regulatória para financiamento coletivo."),
    ("PY", "public_ecosystem"): ("Ministerio de Industria y Comercio", "https://portalemprendedor.mic.gov.py/", "Portal público de instituições e programas para empreendedores."),
    ("PY", "official_platform"): ("Nexoos Paraguay", "https://www.nexoos.com.py/", "Domínio oficial indisponível; nenhuma rota atual verificável."),
    ("PY", "discovery"): ("ASEPY", "https://www.asepy.org/", "Ecossistema empreendedor revisado para descoberta e colisões."),
    ("UY", "regulator"): ("Banco Central del Uruguay", "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/Empresas-Administradoras-de-Plataformas-de-Financiamiento-Colectivo.aspx", "Lista oficial e ficha da única plataforma registrada."),
    ("UY", "public_ecosystem"): ("ANDE", "https://www.ande.org.uy/", "Programas públicos revisados para separar apoio estatal da rota privada."),
    ("UY", "official_platform"): ("Crowder", "https://crowder.fund/", "Documentação de emissores, produtos e termos da plataforma."),
    ("UY", "discovery"): ("URUCAP", "https://www.urucap.org/", "Mapa associativo revisado para colisões com gestores e investidores."),
}


EXTRA_SOURCES = {
    "worker-ar-official-platform": [
        ("src-ar-afluenta", "AR", "Afluenta", "https://www.afluenta.com/", "official_platform", "Página inicial, solicitação e aviso legal.")
    ],
    "worker-cl-official-platform": [
        ("src-cl-redcapital", "CL", "RedCapital", "https://redcapital.cl/", "official_platform", "Página institucional e rota de solicitação para PMEs."),
        ("src-cl-cumplo", "CL", "Cumplo", "https://secure.cumplo.cl/", "official_platform", "Rota de crédito empresarial e política de privacidade."),
    ],
}


def source_record(source_id: str, country: str, source: str, url: str, category: str, scope: str, *, unavailable: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "source_id": source_id,
        "issue": 93,
        "country": country,
        "source": source,
        "initial_url": url,
        "source_category": category,
        "scope_walked": scope,
        "accessed_on": TODAY,
        "robots_status": "unavailable" if unavailable else "not_applicable",
        "access_method": "not_accessed" if unavailable else "manual",
        "cache_key": None,
        "result": "unavailable" if unavailable else "complete",
        "reason": "O domínio oficial não respondeu e não houve tentativa de contornar o bloqueio." if unavailable else None,
        "owner": "issue-93-maintainer" if unavailable else None,
        "next_action": "Confirmar com o operador ou regulador se existe sucessor oficial da plataforma." if unavailable else None,
        "notes": "Revisão manual; a auditoria automatizada de links e robots.txt está registrada separadamente.",
    }


def update_sources_and_tasks() -> None:
    for country, category in SOURCE_RESULTS:
        worker = f"worker-{country.lower()}-{category.replace('_', '-')}"
        source_name, url, scope = SOURCE_RESULTS[(country, category)]
        unavailable = country == "PY" and category == "official_platform"
        source_id = f"src-{country.lower()}-{category.replace('_', '-')}"
        records = [source_record(source_id, country, source_name, url, category, scope, unavailable=unavailable)]
        for extra in EXTRA_SOURCES.get(worker, []):
            records.append(source_record(*extra))
        write_jsonl(SHARDS / worker / "source-inventory.jsonl", records)

        task_path = SHARDS / worker / "run-manifest.jsonl"
        task = json.loads(task_path.read_text(encoding="utf-8").strip())
        task["url"] = url
        task["status"] = "blocked" if unavailable else "done"
        task["owner"] = "issue-93-maintainer" if unavailable else None
        task["block_reason"] = records[0]["reason"] if unavailable else None
        task["next_action"] = records[0]["next_action"] if unavailable else None
        task["last_error"] = "Domínio oficial indisponível na data de corte." if unavailable else None
        write_jsonl(task_path, [task])


def update_coverage_and_run() -> None:
    coverage = []
    for country in ("AR", "CL", "PY", "UY"):
        sources = []
        for category in ("regulator", "public_ecosystem", "official_platform", "discovery"):
            unavailable = country == "PY" and category == "official_platform"
            sources.append(
                {
                    "source_category": category,
                    "status": "gap_justified" if unavailable else "complete",
                    "source_id": f"src-{country.lower()}-{category.replace('_', '-')}",
                    "gap_reason": "Nenhuma plataforma oficial ativa pôde ser verificada; o domínio histórico da Nexoos estava indisponível." if unavailable else None,
                    "owner": "issue-93-maintainer" if unavailable else None,
                    "next_action": "Revisitar após a regulamentação paraguaia de financiamento coletivo ou confirmação de novo operador." if unavailable else None,
                }
            )
        coverage.append({"schema_version": "1.0", "country": country, "regional_issue": 93, "sources": sources})
    write_jsonl(SHARDS / "coordinator" / "coverage-matrix.jsonl", coverage)

    run_path = SHARDS / "coordinator" / "run-manifest.jsonl"
    run = json.loads(run_path.read_text(encoding="utf-8").strip())
    run["status"] = "complete"
    run["notes"] = "Auditoria manual concluída; uma lacuna oficial no Paraguai foi justificada sem contornar controles de acesso."
    write_jsonl(run_path, [run])


def main() -> None:
    for worker_dir in SHARDS.iterdir():
        if worker_dir.name != "coordinator":
            write_jsonl(worker_dir / "candidates.jsonl", [])
            write_jsonl(worker_dir / "evidence.jsonl", [])
    for worker, records in build_candidates().items():
        write_jsonl(SHARDS / worker / "candidates.jsonl", records)
    for worker, records in build_evidence().items():
        write_jsonl(SHARDS / worker / "evidence.jsonl", records)
    update_sources_and_tasks()
    update_coverage_and_run()


if __name__ == "__main__":
    main()
