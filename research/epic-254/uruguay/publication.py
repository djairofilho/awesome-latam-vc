"""Render the frozen Uruguay publication batch in English, Spanish and PT-BR."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROFILES: dict[str, dict[str, Any]] = {
    "ic-ventures": {
        "name": "IC Ventures",
        "destination": "funds/uruguay/ic-ventures.md",
        "summary": {
            "en": "IC Ventures is a Montevideo-based private fund investing in Latin American technology startups at seed and pre-Series A.",
            "es": "IC Ventures es un fondo privado con sede en Montevideo que invierte en startups tecnológicas latinoamericanas en capital semilla y pre-Serie A.",
            "pt-BR": "A IC Ventures é um fundo privado com sede em Montevidéu que investe em startups latino-americanas de tecnologia nos estágios seed e pré-Série A.",
        },
        "base": {"kind": "country", "code": "UY"},
        "countries": ["UY", "AR", "LATAM"],
        "stages": ["seed", "series_a"],
        "focuses": ["technology", "artificial_intelligence", "fintech"],
        "website": "https://ic-ventures.vc/",
        "route": "https://ic-ventures.vc/#contacto",
        "fields": {
            "fund_type": "Private venture capital fund",
            "follow_on": "Exceptional strategic participation",
            "initial_check": "Not publicly disclosed",
            "role": "Hands-on investor; may lead financing processes",
            "models": "Preference for B2B and recurring-revenue businesses",
            "portfolio_size": "11 companies named on the reviewed official page",
            "selected": "Paganza, Tryolabs, MonkeyLearn, NocNoc, Nubimetrics",
        },
        "thesis": {
            "en": "The fund seeks technology-centered companies with disruptive projects, rapid scaling potential and execution-focused teams. It reports a non-exclusive preference for B2B, recurring revenue, artificial intelligence and fintech.",
            "es": "El fondo busca empresas centradas en tecnología, con proyectos disruptivos, potencial de rápida escala y equipos orientados a la ejecución. Declara una preferencia no excluyente por B2B, ingresos recurrentes, inteligencia artificial y fintech.",
            "pt-BR": "O fundo busca empresas centradas em tecnologia, com projetos disruptivos, potencial de escala rápida e equipes focadas em execução. Declara preferência não exclusiva por B2B, receita recorrente, inteligência artificial e fintech.",
        },
        "signal": {
            "en": "The official site says the fund is fully active, reports recent seed and Series A investments, and lists investments in Uruguay and Argentina. Follow-on participation is exceptional rather than the standard model.",
            "es": "El sitio oficial afirma que el fondo está plenamente activo, informa inversiones recientes en capital semilla y Serie A y enumera inversiones en Uruguay y Argentina. La participación en rondas posteriores es excepcional.",
            "pt-BR": "O site oficial afirma que o fundo está plenamente ativo, informa investimentos recentes em seed e Série A e lista investimentos no Uruguai e na Argentina. A participação em rodadas posteriores é excepcional.",
        },
        "sources": [
            {"title": "IC Ventures", "url": "https://ic-ventures.vc/", "kind": "official_portfolio"},
            {"title": "ANII: IC Ventures", "url": "https://anii.org.uy/emprendimientos/fondos-de-capital-riesgo/165/ic-ventures/", "kind": "official_program"},
        ],
    },
    "mrpink-vc": {
        "name": "MrPink VC",
        "destination": "funds/uruguay/mrpink-vc.md",
        "summary": {
            "en": "MrPink VC is a Uruguay-based early-stage venture capital manager focused on startups that strengthen human connection.",
            "es": "MrPink VC es un gestor uruguayo de capital de riesgo en etapa temprana enfocado en startups que fortalecen la conexión humana.",
            "pt-BR": "A MrPink VC é uma gestora uruguaia de venture capital early-stage focada em startups que fortalecem a conexão humana.",
        },
        "base": {"kind": "country", "code": "UY"},
        "countries": ["UY", "LATAM", "ES"],
        "stages": ["not_disclosed"],
        "focuses": ["human_connection", "impact", "technology"],
        "website": "https://mrpink.vc/",
        "route": "https://mrpink.vc/contacto",
        "fields": {
            "fund_type": "Venture capital",
            "follow_on": "Not publicly disclosed",
            "initial_check": "Not publicly disclosed",
            "role": "Hands-on early-stage investor",
            "models": "Not publicly disclosed",
            "portfolio_size": "27 Inception Fund investments",
            "selected": "See the official portfolio page",
        },
        "thesis": {
            "en": "MrPink backs early-stage startups in Latin America and Spain whose products strengthen human connection and create tangible impact.",
            "es": "MrPink respalda startups en etapa temprana de América Latina y España cuyos productos fortalecen la conexión humana y generan impacto concreto.",
            "pt-BR": "A MrPink apoia startups early-stage da América Latina e da Espanha cujos produtos fortalecem a conexão humana e geram impacto concreto.",
        },
        "signal": {
            "en": "The Inception Fund invested in 27 startups from 2020 through 2025. The proposed Human Connection Fund has no announced launch date, so this profile does not present it as open or active.",
            "es": "El Inception Fund invirtió en 27 startups entre 2020 y 2025. El futuro Human Connection Fund no tiene fecha de lanzamiento anunciada, por lo que este perfil no lo presenta como abierto o activo.",
            "pt-BR": "O Inception Fund investiu em 27 startups entre 2020 e 2025. O futuro Human Connection Fund não tem data de lançamento anunciada, por isso este perfil não o apresenta como aberto ou ativo.",
        },
        "sources": [
            {"title": "MrPink VC", "url": "https://mrpink.vc/", "kind": "official_portfolio"},
            {"title": "Nuestra tesis", "url": "https://mrpink.vc/tesis", "kind": "official_thesis"},
            {"title": "Contacto", "url": "https://mrpink.vc/contacto", "kind": "official_application"},
        ],
    },
    "eager-ventures": {
        "name": "Eager Ventures",
        "destination": "funds/uruguay/eager-ventures.md",
        "summary": {
            "en": "Eager Ventures is a Uruguay-based early-stage investor combining financial investment with product and engineering support.",
            "es": "Eager Ventures es un inversor uruguayo de etapa temprana que combina inversión financiera con apoyo de producto e ingeniería.",
            "pt-BR": "A Eager Ventures é uma investidora uruguaia early-stage que combina investimento financeiro com apoio de produto e engenharia.",
        },
        "base": {"kind": "country", "code": "UY"},
        "countries": ["UY"],
        "stages": ["pre_seed", "seed"],
        "focuses": ["technology", "software", "artificial_intelligence"],
        "website": "https://www.eagerventures.io/",
        "route": "https://www.eagerventures.io/#contact",
        "fields": {
            "fund_type": "Corporate-backed venture investor",
            "follow_on": "Not publicly disclosed",
            "initial_check": "Up to USD 100,000",
            "role": "Financial investor and technical product partner",
            "models": "Technology startups; further constraints not publicly disclosed",
            "portfolio_size": "Not presented as an official total",
            "selected": "ModernPM, Hipstr, PlanIT, OrderEat",
        },
        "thesis": {
            "en": "Eager Ventures reinvests part of Eagerworks' profits into pre-seed and seed startups, pairing capital with product strategy, development, design, quality assurance and fundraising support.",
            "es": "Eager Ventures reinvierte parte de las ganancias de Eagerworks en startups pre-seed y seed, combinando capital con estrategia de producto, desarrollo, diseño, control de calidad y apoyo para levantar inversión.",
            "pt-BR": "A Eager Ventures reinveste parte dos lucros da Eagerworks em startups pre-seed e seed, combinando capital com estratégia de produto, desenvolvimento, design, qualidade e apoio para captação.",
        },
        "signal": {
            "en": "The current site states a financial investment of up to USD 100,000, names four supported startups and provides a public founder contact form and email.",
            "es": "El sitio actual informa una inversión financiera de hasta USD 100,000, nombra cuatro startups apoyadas y ofrece un formulario y correo público para fundadores.",
            "pt-BR": "O site atual informa investimento financeiro de até USD 100,000, cita quatro startups apoiadas e oferece formulário e e-mail públicos para founders.",
        },
        "sources": [
            {"title": "Eager Ventures", "url": "https://www.eagerventures.io/", "kind": "official_portfolio"},
        ],
    },
    "tokai-ventures": {
        "name": "Tokai Ventures",
        "destination": "funds/uruguay/tokai-ventures.md",
        "summary": {
            "en": "Tokai Ventures is a Montevideo-based seed and venture capital fund investing across Uruguay and international markets.",
            "es": "Tokai Ventures es un fondo de capital semilla y emprendedor con sede en Montevideo que invierte en Uruguay y mercados internacionales.",
            "pt-BR": "A Tokai Ventures é um fundo de capital seed e venture capital com sede em Montevidéu que investe no Uruguai e em mercados internacionais.",
        },
        "base": {"kind": "country", "code": "UY"},
        "countries": ["UY", "AR", "US", "IL", "LATAM"],
        "stages": ["seed"],
        "focuses": ["proptech", "entertainment", "education", "biotechnology", "impact"],
        "website": "https://www.tokaiventures.com/",
        "route": "https://anii.org.uy/emprendimientos/fondos-de-capital-riesgo/169/tokai-ventures/",
        "fields": {
            "fund_type": "Seed and venture capital",
            "follow_on": "Not publicly disclosed",
            "initial_check": "USD 30,000 to USD 1,000,000",
            "role": "Investor, mentor and board participant",
            "models": "Not publicly disclosed",
            "portfolio_size": "23 companies reported by ANII",
            "selected": "Woow, Infocasas, Rural",
        },
        "thesis": {
            "en": "Tokai focuses on e-commerce, proptech and agtech while considering experienced founders in other verticals. The 2025 URUCAP directory also lists entertainment, metaverse, education, biotechnology and impact.",
            "es": "Tokai se enfoca en comercio electrónico, proptech y agtech, y también considera fundadores experimentados de otros sectores. El directorio URUCAP 2025 agrega entretenimiento, metaverso, educación, biotecnología e impacto.",
            "pt-BR": "A Tokai foca e-commerce, proptech e agtech, mas também considera founders experientes de outros setores. O diretório URUCAP 2025 acrescenta entretenimento, metaverso, educação, biotecnologia e impacto.",
        },
        "signal": {
            "en": "ANII currently lists permanent applications and reports 23 investments. The canonical Tokai domain did not return usable content during review, so institutional and industry-directory evidence is disclosed instead.",
            "es": "ANII mantiene actualmente postulaciones permanentes e informa 23 inversiones. El dominio canónico de Tokai no devolvió contenido utilizable durante la revisión, por lo que se declaran fuentes institucionales y del directorio sectorial.",
            "pt-BR": "A ANII mantém atualmente candidaturas permanentes e informa 23 investimentos. O domínio canônico da Tokai não retornou conteúdo utilizável durante a revisão, por isso o perfil explicita as fontes institucionais e do diretório setorial.",
        },
        "sources": [
            {"title": "ANII: Tokai Ventures", "url": "https://anii.org.uy/emprendimientos/fondos-de-capital-riesgo/169/tokai-ventures/", "kind": "official_program"},
            {"title": "URUCAP member directory 2025", "url": "https://drive.google.com/file/d/1tGvZhIUVvhKVyWO4Y2L64LZEvJZinDLK/view", "kind": "secondary"},
        ],
    },
    "labplus-venture-fund": {
        "name": "LAB+ Venture Fund",
        "destination": "funds/uruguay/labplus-venture-fund.md",
        "summary": {
            "en": "LAB+ Venture Fund is a Montevideo life-sciences vehicle created through collaboration between Institut Pasteur de Montevideo and FICUS Advisory.",
            "es": "LAB+ Venture Fund es un vehículo montevideano de ciencias de la vida creado mediante la colaboración entre el Institut Pasteur de Montevideo y FICUS Advisory.",
            "pt-BR": "O LAB+ Venture Fund é um veículo de ciências da vida de Montevidéu criado pela colaboração entre o Institut Pasteur de Montevideo e a FICUS Advisory.",
        },
        "base": {"kind": "country", "code": "UY"},
        "countries": ["UY", "GLOBAL"],
        "stages": ["not_disclosed"],
        "focuses": ["life_sciences", "one_health", "biotechnology"],
        "website": "https://labplus.uy/",
        "route": "https://labplus.uy/start-ups/",
        "fields": {
            "fund_type": "Venture fund with company-building support",
            "follow_on": "Not publicly disclosed",
            "initial_check": "USD 750,000 committed to each of the first four startups",
            "role": "Investor and scientific company-building partner",
            "models": "Patentable science-based projects and startups",
            "portfolio_size": "4 companies on the reviewed official portfolio",
            "selected": "B4-RNA, GUSKA, LoCBio, Scaffold Biotech",
        },
        "thesis": {
            "en": "The fund finances life-sciences projects and startups under a One Health approach, covering human, animal and environmental health. LAB+ periodically runs international calls and also accepts preliminary contact when no call is open.",
            "es": "El fondo financia proyectos y startups de ciencias de la vida bajo el enfoque Una Salud, que abarca salud humana, animal y ambiental. LAB+ realiza llamados internacionales periódicos y acepta contactos preliminares cuando no hay una convocatoria abierta.",
            "pt-BR": "O fundo financia projetos e startups de ciências da vida sob a abordagem Saúde Única, que abrange saúde humana, animal e ambiental. O LAB+ realiza chamadas internacionais periódicas e aceita contatos preliminares quando não há chamada aberta.",
        },
        "signal": {
            "en": "ANII identifies LAB+ Venture Fund as a fund distinct from the LAB+ Company Builder operating role. LAB+ reports that its first capitalization round closed in February 2024 and committed USD 750,000 to each of four portfolio startups.",
            "es": "ANII identifica a LAB+ Venture Fund como un fondo distinto del rol operativo de LAB+ Company Builder. LAB+ informa que su primera ronda de capitalización cerró en febrero de 2024 y comprometió USD 750,000 para cada una de cuatro startups del portafolio.",
            "pt-BR": "A ANII identifica o LAB+ Venture Fund como fundo distinto do papel operacional do LAB+ Company Builder. O LAB+ informa que sua primeira rodada de capitalização fechou em fevereiro de 2024 e comprometeu USD 750,000 para cada uma das quatro startups do portfólio.",
        },
        "sources": [
            {"title": "ANII: LAB+ Venture Fund", "url": "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/540/lab-venture-fund/", "kind": "official_program"},
            {"title": "LAB+ portfolio", "url": "https://labplus.uy/portfolio/", "kind": "official_portfolio"},
            {"title": "LAB+ start-ups", "url": "https://labplus.uy/start-ups/", "kind": "official_application"},
            {"title": "Qué hacemos", "url": "https://labplus.uy/es/que-hacemos/", "kind": "official_thesis"},
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
        "Private venture capital fund": "Fondo privado de capital de riesgo",
        "Exceptional strategic participation": "Participación estratégica excepcional",
        "Not publicly disclosed": "No divulgado públicamente",
        "Hands-on investor; may lead financing processes": "Inversor activo; puede liderar procesos de financiación",
        "Preference for B2B and recurring-revenue businesses": "Preferencia por empresas B2B y con ingresos recurrentes",
        "11 companies named on the reviewed official page": "11 empresas nombradas en la página oficial revisada",
        "Venture capital": "Capital de riesgo",
        "Hands-on early-stage investor": "Inversor activo de etapa temprana",
        "27 Inception Fund investments": "27 inversiones del Inception Fund",
        "See the official portfolio page": "Ver la página oficial del portafolio",
        "Corporate-backed venture investor": "Inversor de venture respaldado por una empresa",
        "Financial investor and technical product partner": "Inversor financiero y socio técnico de producto",
        "Technology startups; further constraints not publicly disclosed": "Startups tecnológicas; no se divulgaron otras restricciones",
        "Not presented as an official total": "No se presenta como un total oficial",
        "Seed and venture capital": "Capital semilla y emprendedor",
        "Investor, mentor and board participant": "Inversor, mentor y participante en directorios",
        "23 companies reported by ANII": "23 empresas informadas por ANII",
        "Venture fund with company-building support": "Fondo de venture con apoyo de creación de empresas",
        "Investor and scientific company-building partner": "Inversor y socio científico para crear empresas",
        "Patentable science-based projects and startups": "Proyectos y startups de base científica con propiedad intelectual protegible",
        "4 companies on the reviewed official portfolio": "4 empresas en el portafolio oficial revisado",
        "USD 750,000 committed to each of the first four startups": "USD 750,000 comprometidos para cada una de las primeras cuatro startups",
        "Up to USD 100,000": "Hasta USD 100,000",
    },
    "pt-BR": {
        "Private venture capital fund": "Fundo privado de venture capital",
        "Exceptional strategic participation": "Participação estratégica excepcional",
        "Not publicly disclosed": "Não divulgado publicamente",
        "Hands-on investor; may lead financing processes": "Investidor ativo; pode liderar processos de captação",
        "Preference for B2B and recurring-revenue businesses": "Preferência por empresas B2B e com receita recorrente",
        "11 companies named on the reviewed official page": "11 empresas citadas na página oficial revisada",
        "Venture capital": "Venture capital",
        "Hands-on early-stage investor": "Investidor early-stage ativo",
        "27 Inception Fund investments": "27 investimentos do Inception Fund",
        "See the official portfolio page": "Consulte a página oficial do portfólio",
        "Corporate-backed venture investor": "Investidor de venture apoiado por empresa",
        "Financial investor and technical product partner": "Investidor financeiro e parceiro técnico de produto",
        "Technology startups; further constraints not publicly disclosed": "Startups de tecnologia; outras restrições não foram divulgadas",
        "Not presented as an official total": "Não apresentado como total oficial",
        "Seed and venture capital": "Capital seed e venture capital",
        "Investor, mentor and board participant": "Investidor, mentor e participante de conselhos",
        "23 companies reported by ANII": "23 empresas informadas pela ANII",
        "Venture fund with company-building support": "Fundo de venture com apoio de construção de empresas",
        "Investor and scientific company-building partner": "Investidor e parceiro científico na construção de empresas",
        "Patentable science-based projects and startups": "Projetos e startups de base científica com propriedade intelectual protegível",
        "4 companies on the reviewed official portfolio": "4 empresas no portfólio oficial revisado",
        "USD 750,000 committed to each of the first four startups": "USD 750,000 comprometidos para cada uma das quatro primeiras startups",
        "Up to USD 100,000": "Até USD 100,000",
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
