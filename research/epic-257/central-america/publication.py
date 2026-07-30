#!/usr/bin/env python3
"""Render the approved Central America profiles in deterministic batches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
CUTOFF = "2026-07-30"
LOCALES = ("en", "pt-BR", "es")

PROFILES: dict[str, dict[str, Any]] = {
    "invertup": {
        "name": "InvertUP",
        "destination": "funds/regional/invertup.md",
        "base": {"kind": "country", "code": "CR"},
        "countries": ["CR"],
        "stages": ["seed"],
        "focuses": ["sector_agnostic", "innovative_companies"],
        "website": "https://invertup.com/",
        "route": "https://www.parquetec.org/general-7",
        "summary": {
            "en": "InvertUP is a Costa Rica-based private investment vehicle providing seed capital to a diversified portfolio of early-stage startups.",
            "pt-BR": "A InvertUP é um veículo privado da Costa Rica que oferece capital seed a um portfólio diversificado de startups early-stage.",
            "es": "InvertUP es un vehículo privado de Costa Rica que aporta capital semilla a un portafolio diversificado de startups en etapa temprana.",
        },
        "thesis": {
            "en": "InvertUP invests small seed-capital amounts in innovative early-stage companies. ParqueTec supplies the pipeline, due diligence, mentoring and founder intake.",
            "pt-BR": "A InvertUP investe pequenos cheques de capital seed em empresas inovadoras early-stage. A ParqueTec fornece o pipeline, a diligência, a mentoria e a rota para founders.",
            "es": "InvertUP invierte pequeños cheques de capital semilla en empresas innovadoras en etapa temprana. ParqueTec aporta el pipeline, la diligencia, la mentoría y la ruta para founders.",
        },
        "signal": {
            "en": "The current official portfolio names seven startup investments and states that new companies will be added continuously.",
            "pt-BR": "O portfólio oficial atual cita sete investimentos em startups e informa que novas empresas serão adicionadas continuamente.",
            "es": "El portafolio oficial actual nombra siete inversiones en startups e informa que se incorporarán nuevas empresas de forma continua.",
        },
        "facts": {
            "type": "Private seed investment vehicle",
            "check": "Not publicly disclosed",
            "role": "Seed investor; ParqueTec performs selection and support",
            "portfolio": "7 startups on the reviewed official portfolio",
            "selected": "Grab & Eat, Audazzio, Ainnova Tech, Tecnología Virtual",
        },
        "sources": [
            {"title": "InvertUP", "url": "https://invertup.com/", "kind": "official_website"},
            {"title": "Portfolio & Prospects", "url": "https://invertup.com/portfolio/", "kind": "official_portfolio"},
            {"title": "Costa Rica Angels and InvertUP", "url": "https://www.parquetec.org/general-7", "kind": "official_website"},
        ],
    },
    "infinita-vc": {
        "name": "Infinita VC",
        "destination": "funds/regional/infinita-vc.md",
        "base": {"kind": "country", "code": "HN"},
        "countries": ["HN", "LATAM", "US"],
        "stages": ["seed"],
        "focuses": ["biotechnology", "hardware", "robotics", "fintech", "web3"],
        "website": "https://infinitavc.com/",
        "route": None,
        "summary": {
            "en": "Infinita VC is an early-stage venture capital fund based in Próspera, Roatán, investing in technologies constrained by regulatory bottlenecks.",
            "pt-BR": "A Infinita VC é um fundo de venture capital early-stage sediado em Próspera, Roatán, que investe em tecnologias limitadas por gargalos regulatórios.",
            "es": "Infinita VC es un fondo de capital de riesgo en etapa temprana con sede en Próspera, Roatán, que invierte en tecnologías limitadas por cuellos de botella regulatorios.",
        },
        "thesis": {
            "en": "Infinita uses startup-city placement and legal engineering to support founders in biotechnology, hardware and robotics, fintech and crypto across Latin America and the United States.",
            "pt-BR": "A Infinita usa a presença em startup cities e engenharia jurídica para apoiar founders de biotecnologia, hardware e robótica, fintech e cripto na América Latina e nos Estados Unidos.",
            "es": "Infinita usa su presencia en startup cities e ingeniería jurídica para apoyar founders de biotecnología, hardware y robótica, fintech y cripto en América Latina y Estados Unidos.",
        },
        "signal": {
            "en": "The current public company profile keeps its headquarters and operating team in Roatán. Separately, independent reporting confirms Infinita Fund joined Yendou's USD 1.3 million pre-seed round in 2024; that older round is evidence of deployment, not the current-activity signal.",
            "pt-BR": "O perfil público atual mantém a sede e a equipe operacional em Roatán. Separadamente, a cobertura independente confirma a participação da Infinita Fund na rodada pre-seed de USD 1,3 milhão da Yendou em 2024. Essa rodada anterior prova deployment, não é o sinal de atividade atual.",
            "es": "El perfil público actual mantiene la sede y el equipo operativo en Roatán. Por separado, la cobertura independiente confirma la participación de Infinita Fund en la ronda pre-seed de USD 1,3 millones de Yendou en 2024. Esa ronda anterior prueba deployment, no es la señal de actividad actual.",
        },
        "facts": {
            "type": "Early-stage venture capital fund",
            "check": "Not publicly disclosed",
            "role": "Investor focused on regulatory and market-entry constraints",
            "portfolio": "Not presented as an official current total",
            "selected": "Yendou; other current holdings not disclosed as an official list",
        },
        "sources": [
            {"title": "Infinita VC official site", "url": "https://infinitavc.com/defi2023", "kind": "official_website"},
            {"title": "Infinita VC public company profile", "url": "https://www.linkedin.com/company/infinita-fund", "kind": "secondary"},
            {"title": "Yendou pre-seed round", "url": "https://tech.eu/2024/02/28/berlin-based-startup-yendou-the-salesforce-for-life-sciences-rd-teams/", "kind": "secondary"},
        ],
    },
    "venture-club-latam": {
        "name": "Venture Club Latam",
        "destination": "funds/regional/venture-club-latam.md",
        "base": {"kind": "country", "code": "PA"},
        "countries": ["PA", "LATAM"],
        "stages": ["pre_seed", "seed"],
        "focuses": ["artificial_intelligence", "saas", "iot", "enterprise_software", "climate"],
        "website": "https://ventureclublatam.com/",
        "route": "https://ventureclublatam.com/",
        "summary": {
            "en": "Venture Club Latam is a Panama-based early-stage investment platform using a rolling fund and an SPV for each portfolio investment.",
            "pt-BR": "A Venture Club Latam é uma plataforma de investimento early-stage do Panamá que usa um rolling fund e um SPV para cada investimento.",
            "es": "Venture Club Latam es una plataforma de inversión en etapa temprana de Panamá que utiliza un rolling fund y un SPV para cada inversión.",
        },
        "thesis": {
            "en": "The platform invests in revenue-generating technology companies with demonstrated adoption and execution, focusing on AI, enterprise software, IoT, SaaS and related infrastructure.",
            "pt-BR": "A plataforma investe em empresas de tecnologia com receita, adoção e execução comprovadas, com foco em IA, software empresarial, IoT, SaaS e infraestrutura relacionada.",
            "es": "La plataforma invierte en empresas tecnológicas con ingresos, adopción y ejecución comprobadas, con foco en IA, software empresarial, IoT, SaaS e infraestructura relacionada.",
        },
        "signal": {
            "en": "The current site names two selected investments, documents an investment committee and portfolio monitoring, and provides a public investor contact.",
            "pt-BR": "O site atual cita dois investimentos selecionados, documenta comitê de investimento e monitoramento de portfólio e oferece contato público.",
            "es": "El sitio actual nombra dos inversiones seleccionadas, documenta un comité de inversión y monitoreo de portafolio y ofrece contacto público.",
        },
        "facts": {
            "type": "Rolling fund with SPV-by-investment architecture",
            "check": "Not publicly disclosed",
            "role": "Structured early-stage investor with portfolio monitoring",
            "portfolio": "2 selected investments on the reviewed official site",
            "selected": "Sensify and Layrz",
        },
        "sources": [
            {"title": "Venture Club Latam", "url": "https://ventureclublatam.com/", "kind": "official_portfolio"},
        ],
    },
}

LABELS = {
    "en": {
        "profile": "Investment profile", "website": "Website", "type": "Fund type",
        "direct": "Direct startup investment", "external": "Open to external founders",
        "entry": "Stage at entry", "focus": "Focus", "geo": "Geography",
        "check": "Initial check", "role": "Investment role", "portfolio": "Portfolio size",
        "selected": "Selected companies", "submit": "Submit a startup",
        "thesis": "Declared thesis", "signals": "Portfolio signals", "sources": "Sources",
        "verified": "Last verified", "yes": "Yes", "none": "No public route located",
    },
    "pt-BR": {
        "profile": "Perfil de investimento", "website": "Site", "type": "Tipo de fundo",
        "direct": "Investimento direto em startups", "external": "Aberto a founders externos",
        "entry": "Estágio de entrada", "focus": "Foco", "geo": "Geografia",
        "check": "Cheque inicial", "role": "Papel no investimento", "portfolio": "Tamanho do portfólio",
        "selected": "Empresas selecionadas", "submit": "Enviar uma startup",
        "thesis": "Tese declarada", "signals": "Sinais de portfólio", "sources": "Fontes",
        "verified": "Última verificação", "yes": "Sim", "none": "Nenhuma rota pública localizada",
    },
    "es": {
        "profile": "Perfil de inversión", "website": "Sitio web", "type": "Tipo de fondo",
        "direct": "Inversión directa en startups", "external": "Abierto a founders externos",
        "entry": "Etapa de entrada", "focus": "Enfoque", "geo": "Geografía",
        "check": "Cheque inicial", "role": "Rol de inversión", "portfolio": "Tamaño del portafolio",
        "selected": "Empresas seleccionadas", "submit": "Presentar una startup",
        "thesis": "Tesis declarada", "signals": "Señales del portafolio", "sources": "Fuentes",
        "verified": "Última verificación", "yes": "Sí", "none": "No se encontró una ruta pública",
    },
}


def metadata(slug: str, profile: dict[str, Any], locale: str) -> dict[str, Any]:
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
        "last_verified": CUTOFF,
        "protected_terms": [profile["name"]],
    }


def render(slug: str, profile: dict[str, Any], locale: str) -> str:
    label = LABELS[locale]
    front = json.dumps(metadata(slug, profile, locale), ensure_ascii=False, indent=2)
    sources = "\n".join(f"- [{s['title']}]({s['url']})" for s in profile["sources"])
    stages = ", ".join(profile["stages"]).replace("_", " ")
    focuses = ", ".join(profile["focuses"]).replace("_", " ")
    countries = ", ".join(profile["countries"])
    route = profile["route"] or label["none"]
    facts = profile["facts"]
    return f"""---
{front}
---
# {profile['name']}

{profile['summary'][locale]}

## {label['profile']}

- **{label['website']}:** {profile['website']}
- **{label['type']}:** {facts['type']}
- **{label['direct']}:** {label['yes']}
- **{label['external']}:** {label['yes'] if profile['route'] else label['none']}
- **{label['entry']}:** {stages}
- **{label['focus']}:** {focuses}
- **{label['geo']}:** {countries}
- **{label['check']}:** {facts['check']}
- **{label['role']}:** {facts['role']}
- **{label['portfolio']}:** {facts['portfolio']}
- **{label['selected']}:** {facts['selected']}
- **{label['submit']}:** {route}

## {label['thesis']}

{profile['thesis'][locale]}

## {label['signals']}

{profile['signal'][locale]}

## {label['sources']}

{sources}

**{label['verified']}:** {CUTOFF}
"""


def output_path(profile: dict[str, Any], locale: str) -> Path:
    canonical = ROOT / profile["destination"]
    if locale == "en":
        return canonical
    return ROOT / "translations" / locale / canonical.relative_to(ROOT)


def publish(batch: int) -> None:
    slugs = list(PROFILES)
    batches = {1: slugs, 2: []}
    for slug in batches[batch]:
        profile = PROFILES[slug]
        for locale in LOCALES:
            path = output_path(profile, locale)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(slug, profile, locale), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, choices=(1, 2), required=True)
    args = parser.parse_args()
    publish(args.batch)
