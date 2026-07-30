"""Render the frozen transverse handoff batch in English, Spanish and PT-BR."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "beta-impacto": {
        "name": "Beta Impacto",
        "destination": "funds/argentina/beta-impacto.md",
        "summary": {
            "en": "Beta Impacto is an Argentina-based impact venture capital fund investing in scalable early-stage companies across Latin America.",
            "es": "Beta Impacto es un fondo argentino de capital de riesgo de impacto que invierte en empresas escalables de etapa temprana en América Latina.",
            "pt-BR": "A Beta Impacto é um fundo argentino de venture capital de impacto que investe em empresas escaláveis em estágio inicial na América Latina.",
        },
        "base": {"kind": "country", "code": "AR"},
        "countries": ["AR", "LATAM"],
        "stages": ["pre_seed"],
        "focuses": ["impact", "climate_technology", "agriculture", "energy_transition"],
        "website": "https://betaimpacto.vc/",
        "route": "https://betaimpacto.vc/",
        "fields": {
            "fund_type": "Impact venture capital fund",
            "follow_on": "Not publicly disclosed",
            "initial_check": "Not publicly disclosed",
            "role": "Active investor with tailored acceleration support",
            "models": "Scalable technology-based businesses with measurable social or environmental impact",
            "portfolio_size": "Not publicly disclosed",
            "selected": "Not disclosed in machine-readable text on the reviewed official pages",
        },
        "thesis": {
            "en": "Beta Impacto backs purpose-driven companies addressing social inclusion and environmental challenges through disruptive technology. Its stated priorities include agroecology, food security, climate change and the energy transition.",
            "es": "Beta Impacto respalda empresas con propósito que abordan la inclusión social y los desafíos ambientales mediante tecnología disruptiva. Sus prioridades declaradas incluyen agroecología, seguridad alimentaria, cambio climático y transición energética.",
            "pt-BR": "A Beta Impacto apoia empresas orientadas por propósito que enfrentam a inclusão social e os desafios ambientais com tecnologia disruptiva. Suas prioridades declaradas incluem agroecologia, segurança alimentar, mudanças climáticas e transição energética.",
        },
        "signal": {
            "en": "The current official site describes active early-stage investment, portfolio monitoring and an open application route. Beta was created through Sumatoria and Buenos Aires-based Xeibo. The reviewed pages do not expose portfolio company names as machine-readable text, so no names or portfolio total are inferred.",
            "es": "El sitio oficial actual describe inversión activa en etapa temprana, seguimiento del portafolio y una vía abierta de postulación. Beta fue creada por Sumatoria y Xeibo, con sede en Buenos Aires. Las páginas revisadas no exponen nombres de empresas del portafolio en texto legible por máquina, por lo que no se infieren nombres ni un total.",
            "pt-BR": "O site oficial atual descreve investimento ativo em estágio inicial, acompanhamento do portfólio e uma rota aberta de candidatura. A Beta foi criada pela Sumatoria e pela Xeibo, sediada em Buenos Aires. As páginas revisadas não expõem nomes das empresas do portfólio em texto legível por máquina, por isso nenhum nome ou total é inferido.",
        },
        "sources": [
            {"title": "Beta Impacto", "url": "https://betaimpacto.vc/", "kind": "official_thesis"},
            {"title": "Beta Impacto: impact", "url": "https://betaimpacto.vc/impacto/", "kind": "official_portfolio"},
            {"title": "Xeibo", "url": "https://xeibocapital.com/", "kind": "official_thesis"},
            {
                "title": "ANII: Beta Impacto",
                "url": "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/532/beta-impacto/",
                "kind": "secondary",
            },
        ],
    },
    "primary-x": {
        "name": "Primary X",
        "destination": "funds/argentina/primary-x.md",
        "summary": {
            "en": "Primary X is A3 Mercados' Argentina-based corporate venture capital unit for early-stage fintech, crypto and agrifintech startups.",
            "es": "Primary X es la unidad argentina de capital de riesgo corporativo de A3 Mercados para startups tempranas de fintech, cripto y agrifintech.",
            "pt-BR": "A Primary X é a unidade argentina de corporate venture capital da A3 Mercados para startups early-stage de fintech, cripto e agrifintech.",
        },
        "base": {"kind": "country", "code": "AR"},
        "countries": ["AR", "UY"],
        "stages": ["pre_seed", "seed", "series_a"],
        "focuses": ["fintech", "cryptocurrency", "agritech"],
        "website": "https://pmyx.com.ar/",
        "route": "https://pmyx.com.ar/#aplicar",
        "fields": {
            "fund_type": "Corporate venture capital",
            "follow_on": "Not publicly disclosed",
            "initial_check": "Not publicly disclosed",
            "role": "Strategic corporate investor and operating partner",
            "models": "Fintech, crypto and agrifintech for capital markets",
            "portfolio_size": "Multiple startups; no official total disclosed",
            "selected": "Origino, Skyblue Analytics",
        },
        "thesis": {
            "en": "Primary X invests in early-stage startups developing novel businesses and technologies for capital markets. It combines capital with planning, networking, partnerships, legal and financial support.",
            "es": "Primary X invierte en startups de etapa temprana que desarrollan negocios y tecnologías novedosas para el mercado de capitales. Combina capital con planificación, redes, alianzas y apoyo legal y financiero.",
            "pt-BR": "A Primary X investe em startups early-stage que desenvolvem negócios e tecnologias novas para o mercado de capitais. Combina capital com planejamento, networking, parcerias e apoio jurídico e financeiro.",
        },
        "signal": {
            "en": "The current official site states that Primary X has invested in multiple startups and accepts founder applications. A3 Mercados' official financial statements identify Primary X S.A.U. as an Argentina investment company and record investments in Origino and Skyblue Analytics during 2025.",
            "es": "El sitio oficial actual afirma que Primary X invirtió en varias startups y acepta postulaciones de fundadores. Los estados financieros oficiales de A3 Mercados identifican a Primary X S.A.U. como una sociedad de inversión argentina y registran inversiones en Origino y Skyblue Analytics durante 2025.",
            "pt-BR": "O site oficial atual afirma que a Primary X investiu em várias startups e aceita candidaturas de founders. As demonstrações financeiras oficiais da A3 Mercados identificam a Primary X S.A.U. como uma empresa argentina de investimentos e registram aportes na Origino e na Skyblue Analytics durante 2025.",
        },
        "sources": [
            {"title": "Primary X", "url": "https://pmyx.com.ar/", "kind": "official_portfolio"},
            {
                "title": "A3 Mercados 2025 financial statements",
                "url": "https://a3mercados.com.ar/wp-content/uploads/2025/10/Memoria-y-Estados-Financieros-A3-DIGITAL-25.pdf",
                "kind": "official_activity",
            },
            {
                "title": "A3 Mercados 2026 financial statements",
                "url": "https://a3mercados.com.ar/wp-content/uploads/2026/04/Memoria-y-estados-financieros-A3-DIGITAL-Ejercicio-N%C2%B0-118-26.pdf",
                "kind": "official_activity",
            },
        ],
    },
    "saasholic": {
        "name": "SaaSholic",
        "destination": "funds/brazil/saasholic.md",
        "summary": {
            "en": "SaaSholic is a São Paulo-based early-stage venture capital firm investing in SaaS and B2B software companies across Latin America.",
            "es": "SaaSholic es una firma de capital de riesgo de etapa temprana con sede en São Paulo que invierte en empresas SaaS y software B2B de América Latina.",
            "pt-BR": "A SaaSholic é uma gestora de venture capital early-stage sediada em São Paulo que investe em empresas SaaS e software B2B da América Latina.",
        },
        "base": {"kind": "country", "code": "BR"},
        "countries": ["BR", "LATAM"],
        "stages": ["pre_seed", "seed"],
        "focuses": ["b2b_saas", "software", "artificial_intelligence"],
        "website": "https://www.saasholic.com/",
        "route": "https://memo.saasholic.com/",
        "fields": {
            "fund_type": "Early-stage venture capital",
            "follow_on": "Not publicly disclosed",
            "initial_check": "Typically USD 250,000 at pre-seed and USD 500,000 at seed",
            "role": "High-conviction investor seeking to lead and support go-to-market execution",
            "models": "Latin American SaaS, AI-SaaS and B2B software",
            "portfolio_size": "14 Fund II companies",
            "selected": "Sinky, HiSofi, Didit, Atlas Governance, Jusfy, Clicksign, Conta Simples, Salvy, Liquid",
        },
        "thesis": {
            "en": "SaaSholic backs Latin American SaaS, AI-SaaS and B2B software founders from pre-seed through seed. It looks for initial traction and supports sales, marketing, pricing, hiring and subsequent fundraising.",
            "es": "SaaSholic respalda fundadores latinoamericanos de SaaS, AI-SaaS y software B2B desde pre-seed hasta seed. Busca tracción inicial y apoya ventas, marketing, precios, contratación y rondas posteriores.",
            "pt-BR": "A SaaSholic apoia founders latino-americanos de SaaS, AI-SaaS e software B2B do pre-seed ao seed. Busca tração inicial e apoia vendas, marketing, precificação, contratação e rodadas posteriores.",
        },
        "signal": {
            "en": "The current official site reports 14 Fund II companies and names portfolio companies. Its founder page documents direct SAFE investment, typical checks, an application route and an active investment process.",
            "es": "El sitio oficial actual informa 14 empresas en el Fund II y nombra compañías del portafolio. La página para fundadores documenta inversión directa mediante SAFE, cheques típicos, una vía de postulación y un proceso de inversión activo.",
            "pt-BR": "O site oficial atual informa 14 empresas no Fund II e nomeia companhias do portfólio. A página para founders documenta investimento direto via SAFE, cheques típicos, uma rota de candidatura e um processo de investimento ativo.",
        },
        "sources": [
            {"title": "SaaSholic", "url": "https://www.saasholic.com/", "kind": "official_portfolio"},
            {"title": "SaaSholic for founders", "url": "https://www.saasholic.com/founders", "kind": "official_application"},
            {"title": "SaaSholic company profile", "url": "https://www.linkedin.com/company/saasholic", "kind": "secondary"},
        ],
    },
}


LABELS = {
    "en": {
        "profile": "Investment profile", "website": "Website", "type": "Fund type",
        "direct": "Direct startup investment", "external": "Open to external founders",
        "entry": "Stage at entry", "follow": "Follow-on stages", "focus": "Focus",
        "geo": "Geography", "check": "Initial check", "role": "Investment role",
        "models": "Business models", "size": "Portfolio size", "selected": "Selected companies",
        "submit": "Submit a startup", "thesis": "Declared thesis", "signals": "Portfolio signals",
        "sources": "Sources", "verified": "Last verified", "yes": "Yes",
    },
    "es": {
        "profile": "Perfil de inversión", "website": "Sitio web", "type": "Tipo de fondo",
        "direct": "Inversión directa en startups", "external": "Abierto a fundadores externos",
        "entry": "Etapa de entrada", "follow": "Etapas posteriores", "focus": "Enfoque",
        "geo": "Geografía", "check": "Cheque inicial", "role": "Rol de inversión",
        "models": "Modelos de negocio", "size": "Tamaño del portafolio", "selected": "Empresas seleccionadas",
        "submit": "Presentar una startup", "thesis": "Tesis declarada", "signals": "Señales del portafolio",
        "sources": "Fuentes", "verified": "Última verificación", "yes": "Sí",
    },
    "pt-BR": {
        "profile": "Perfil de investimento", "website": "Site", "type": "Tipo de fundo",
        "direct": "Investimento direto em startups", "external": "Aberto a founders externos",
        "entry": "Estágio de entrada", "follow": "Estágios de follow-on", "focus": "Foco",
        "geo": "Geografia", "check": "Cheque inicial", "role": "Papel no investimento",
        "models": "Modelos de negócio", "size": "Tamanho do portfólio", "selected": "Empresas selecionadas",
        "submit": "Enviar uma startup", "thesis": "Tese declarada", "signals": "Sinais de portfólio",
        "sources": "Fontes", "verified": "Última verificação", "yes": "Sim",
    },
}


VALUE_TRANSLATIONS = {
    "es": {
        "Impact venture capital fund": "Fondo de capital de riesgo de impacto",
        "Not publicly disclosed": "No divulgado públicamente",
        "Active investor with tailored acceleration support": "Inversor activo con apoyo de aceleración a medida",
        "Scalable technology-based businesses with measurable social or environmental impact": "Negocios tecnológicos escalables con impacto social o ambiental medible",
        "Not disclosed in machine-readable text on the reviewed official pages": "No divulgado en texto legible por máquina en las páginas oficiales revisadas",
        "Corporate venture capital": "Capital de riesgo corporativo",
        "Strategic corporate investor and operating partner": "Inversor corporativo estratégico y socio operativo",
        "Fintech, crypto and agrifintech for capital markets": "Fintech, cripto y agrifintech para el mercado de capitales",
        "Multiple startups; no official total disclosed": "Varias startups; no se divulgó un total oficial",
        "Early-stage venture capital": "Capital de riesgo de etapa temprana",
        "Typically USD 250,000 at pre-seed and USD 500,000 at seed": "Normalmente USD 250,000 en pre-seed y USD 500,000 en seed",
        "High-conviction investor seeking to lead and support go-to-market execution": "Inversor de alta convicción que busca liderar y apoyar la ejecución de go-to-market",
        "Latin American SaaS, AI-SaaS and B2B software": "SaaS, AI-SaaS y software B2B de América Latina",
        "14 Fund II companies": "14 empresas del Fund II",
    },
    "pt-BR": {
        "Impact venture capital fund": "Fundo de venture capital de impacto",
        "Not publicly disclosed": "Não divulgado publicamente",
        "Active investor with tailored acceleration support": "Investidor ativo com apoio de aceleração sob medida",
        "Scalable technology-based businesses with measurable social or environmental impact": "Negócios de base tecnológica escaláveis com impacto social ou ambiental mensurável",
        "Not disclosed in machine-readable text on the reviewed official pages": "Não divulgado em texto legível por máquina nas páginas oficiais revisadas",
        "Corporate venture capital": "Corporate venture capital",
        "Strategic corporate investor and operating partner": "Investidor corporativo estratégico e parceiro operacional",
        "Fintech, crypto and agrifintech for capital markets": "Fintech, cripto e agrifintech para o mercado de capitais",
        "Multiple startups; no official total disclosed": "Várias startups; nenhum total oficial foi divulgado",
        "Early-stage venture capital": "Venture capital early-stage",
        "Typically USD 250,000 at pre-seed and USD 500,000 at seed": "Normalmente USD 250,000 no pre-seed e USD 500,000 no seed",
        "High-conviction investor seeking to lead and support go-to-market execution": "Investidor de alta convicção que busca liderar e apoiar a execução de go-to-market",
        "Latin American SaaS, AI-SaaS and B2B software": "SaaS, AI-SaaS e software B2B da América Latina",
        "14 Fund II companies": "14 empresas do Fund II",
    },
}


def metadata(slug: str, profile: dict[str, Any], locale: str, cutoff: str) -> dict[str, Any]:
    canonical = f"fund:{slug}:en"
    return {
        "schema_version": "1.0",
        "id": f"fund:{slug}:{locale}",
        "entity_id": f"fund:{slug}",
        "slug": slug,
        "name": profile["name"],
        "entity_type": "fund",
        "locale": locale,
        "translation_of": None if locale == "en" else canonical,
        "translation_status": "canonical" if locale == "en" else "complete",
        "summary": profile["summary"][locale],
        "aliases": [],
        "operator": None,
        "base_geography": profile["base"],
        "countries_covered": profile["countries"],
        "stages": profile["stages"],
        "focuses": profile["focuses"],
        "official_website": profile["website"],
        "founder_route": profile["route"],
        "sources": profile["sources"],
        "last_verified": cutoff,
        "protected_terms": [profile["name"]],
    }


def render(slug: str, profile: dict[str, Any], locale: str, cutoff: str) -> bytes:
    label = LABELS[locale]
    fields = profile["fields"]
    front = json.dumps(metadata(slug, profile, locale, cutoff), ensure_ascii=False, indent=2)
    sources = "\n".join(f"- [{source['title']}]({source['url']})" for source in profile["sources"])
    stage = ", ".join(profile["stages"]).replace("_", " ")
    focuses = ", ".join(profile["focuses"]).replace("_", " ")
    geography = ", ".join(profile["countries"])

    def value(key: str) -> str:
        raw = fields[key]
        return VALUE_TRANSLATIONS.get(locale, {}).get(raw, raw)

    text = f"""---
{front}
---
# {profile['name']}

{profile['summary'][locale]}

## {label['profile']}

- **{label['website']}:** {profile['website']}
- **{label['type']}:** {value('fund_type')}
- **{label['direct']}:** {label['yes']}
- **{label['external']}:** {label['yes']}
- **{label['entry']}:** {stage}
- **{label['follow']}:** {value('follow_on')}
- **{label['focus']}:** {focuses}
- **{label['geo']}:** {geography}
- **{label['check']}:** {value('initial_check')}
- **{label['role']}:** {value('role')}
- **{label['models']}:** {value('models')}
- **{label['size']}:** {value('portfolio_size')}
- **{label['selected']}:** {value('selected')}
- **{label['submit']}:** [{profile['name']}]({profile['route']})

## {label['thesis']}

{profile['thesis'][locale]}

## {label['signals']}

{profile['signal'][locale]}

## {label['sources']}

{sources}

**{label['verified']}:** {cutoff}
"""
    return text.encode("utf-8")


def profile_outputs(root: Path, cutoff: str) -> dict[Path, bytes]:
    outputs: dict[Path, bytes] = {}
    for slug, profile in PROFILES.items():
        for locale in ("en", "es", "pt-BR"):
            destination = Path(profile["destination"])
            path = root / destination if locale == "en" else root / "translations" / locale / destination
            outputs[path] = render(slug, profile, locale, cutoff)
    return outputs
