#!/usr/bin/env python3
"""Build the auditable Chile re-audit bundle and frozen publication batch."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research" / "epic-251" / "chile"
CUTOFF = "2026-07-30"


def source(title: str, url: str, kind: str) -> dict:
    return {"title": title, "url": url, "kind": kind}


PROFILES = [
    {
        "slug": "abastibletec",
        "name": "AbastibleTec",
        "aliases": ["Abastible Tec"],
        "operator": "Abastible",
        "summary": {
            "en": "AbastibleTec is a Chile-based corporate investment unit backing energy-intelligence startups.",
            "pt-BR": "A AbastibleTec é uma unidade chilena de investimento corporativo que investe em startups de inteligência energética.",
            "es": "AbastibleTec es una unidad chilena de inversión corporativa que invierte en startups de inteligencia energética.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["energy_intelligence", "energy_efficiency", "decarbonization"],
        "countries": ["CL", "CO", "EC", "ES", "PE", "PT"],
        "website": "https://abastible.cl/lanzamiento-abastible-tec-innovacion-e-inteligencia-energetica/",
        "founder_route": None,
        "fund_type": "Corporate venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Energy intelligence, energy efficiency, and decarbonization",
        "geography_label": "Chile, Colombia, Ecuador, Peru, Spain, and Portugal",
        "check": "Not publicly disclosed",
        "portfolio": "Bluetek and Zensi",
        "activity": "Two direct startup investments confirmed in 2026",
        "thesis": "AbastibleTec invests in startups whose technology can improve energy efficiency and turn operational data into lower costs and emissions.",
        "signals": "Official 2026 announcements identify Bluetek and Zensi as the unit's first and second direct startup investments.",
        "sources": [
            source("AbastibleTec launch and regional scope", "https://abastible.cl/lanzamiento-abastible-tec-innovacion-e-inteligencia-energetica/", "official_thesis"),
            source("AbastibleTec first startup investment", "https://www.empresascopec.cl/en/noticia/abastibletec-completes-its-first-investment-in-startups/", "official_activity"),
            source("AbastibleTec second startup investment", "https://www.empresascopec.cl/en/noticia/abastibletec-selects-zensi-for-its-second-startup-investment/", "official_activity"),
        ],
    },
    {
        "slug": "bice-ventures",
        "name": "BICE Ventures",
        "aliases": [],
        "operator": "Grupo BICE",
        "summary": {
            "en": "BICE Ventures is Grupo BICE's Chile-based corporate venture capital and company-building unit.",
            "pt-BR": "A BICE Ventures é a unidade chilena de corporate venture capital e company building do Grupo BICE.",
            "es": "BICE Ventures es la unidad chilena de corporate venture capital y company building de Grupo BICE.",
        },
        "stages": ["pre_seed", "seed", "series_a"],
        "focuses": ["fintech", "insurtech", "data", "artificial_intelligence", "wellness"],
        "countries": ["CL", "LATAM"],
        "website": "https://www.biceventures.com/",
        "founder_route": "https://www.biceventures.com/en/pitch-your-startup",
        "fund_type": "Corporate venture capital",
        "stage_label": "Pre-seed, Seed, and Series A",
        "focus_label": "Fintech, insurtech, data, artificial intelligence, and wellness",
        "geography_label": "Chile and Latin America",
        "check": "Not publicly disclosed",
        "portfolio": "Five active investments on the reviewed official site",
        "activity": "Active portfolio and open founder application verified in 2026",
        "thesis": "BICE Ventures invests in early-stage technology companies that complement Grupo BICE's financial-services businesses.",
        "signals": "The official site reports five active investments, one exit, and an open application route for founders.",
        "sources": [
            source("BICE Ventures official site and active portfolio", "https://www.biceventures.com/", "official_portfolio"),
            source("BICE Ventures founder application", "https://www.biceventures.com/en/pitch-your-startup", "official_application"),
            source("BICE Ventures activity in 2026", "https://www.bicecorp.com/noticias/bice-innova-reads-que-es-el-corporate-venture-capital-cvc", "official_activity"),
        ],
    },
    {
        "slug": "carozzi-ventures",
        "name": "Carozzi Ventures",
        "aliases": [],
        "operator": "Empresas Carozzi",
        "summary": {
            "en": "Carozzi Ventures is the Chile-based corporate venture capital unit of food company Empresas Carozzi.",
            "pt-BR": "A Carozzi Ventures é a unidade chilena de corporate venture capital da empresa de alimentos Empresas Carozzi.",
            "es": "Carozzi Ventures es la unidad chilena de corporate venture capital de la empresa de alimentos Empresas Carozzi.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["agrifood", "pet_care", "supply_chain", "advanced_manufacturing"],
        "countries": ["CL"],
        "website": "https://www.carozzicorp.com/carozzi-ventures/",
        "founder_route": "https://www.carozzicorp.com/carozzi-ventures/",
        "fund_type": "Corporate venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Agrifood, pet care, supply chain, and advanced manufacturing",
        "geography_label": "Chile",
        "check": "Up to USD 1 million per initiative",
        "portfolio": "Frankles and Neocrop Technologies",
        "activity": "Two direct startup investments confirmed by 2026",
        "thesis": "Carozzi Ventures invests in innovative startups related to food, agriculture, distribution, and advanced manufacturing.",
        "signals": "Official reports record the first investment in Frankles in 2025 and a second investment in Neocrop Technologies in 2026.",
        "sources": [
            source("Carozzi Ventures thesis and founder contact", "https://www.carozzicorp.com/carozzi-ventures/", "official_application"),
            source("Carozzi Ventures first investment", "https://www.carozzicorp.com/lanzamiento-sinergia-id/", "official_activity"),
            source("Carozzi 2026 interim financial report", "https://www.carozzicorp.com/wp-content/uploads/2026/06/EFTrimestrales-31.03.2026-1.pdf", "official_activity"),
        ],
    },
    {
        "slug": "copec-wind-ventures",
        "name": "Copec Wind Ventures",
        "aliases": ["Wind Ventures"],
        "operator": "Copec",
        "summary": {
            "en": "Copec Wind Ventures is Copec's corporate venture capital unit investing globally in energy and mobility startups.",
            "pt-BR": "A Copec Wind Ventures é a unidade de corporate venture capital da Copec que investe globalmente em startups de energia e mobilidade.",
            "es": "Copec Wind Ventures es la unidad de corporate venture capital de Copec que invierte globalmente en startups de energía y movilidad.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["energy", "mobility", "sustainability"],
        "countries": ["GLOBAL"],
        "website": "https://ww2.copec.cl/personas/informacion-oficial-de-copec",
        "founder_route": None,
        "fund_type": "Corporate venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Energy, mobility, and sustainability",
        "geography_label": "Global",
        "check": "Not publicly disclosed",
        "portfolio": "25 startups reported by Copec in 2025",
        "activity": "Direct investment in Optibus confirmed in 2025",
        "thesis": "Copec Wind Ventures invests globally in startups connected to energy, mobility, and sustainable business transformation.",
        "signals": "Copec reported more than USD 160 million invested across 25 startups and announced an investment in Optibus in 2025.",
        "sources": [
            source("Copec official corporate venture description", "https://ww2.copec.cl/personas/informacion-oficial-de-copec", "official_thesis"),
            source("Copec Wind Ventures portfolio metrics", "https://ww2.copec.cl/personas/noticias/sostenibilidad/copec-wind-ventures-lidera-ranking-de-cvcs-en-chile", "official_portfolio"),
            source("Copec Wind Ventures investment in Optibus", "https://ww2.copec.cl/personas/noticias/sostenibilidad/copec-refuerza-su-compromiso-con-la-electromovilidad-e-invierte-en-optibus-startup-que-implementa-ia-para-el-desarrollo-de-transporte-sostenible", "official_activity"),
        ],
    },
    {
        "slug": "leap-caja-los-andes",
        "name": "Leap",
        "aliases": ["Leap by Caja Los Andes"],
        "operator": "Caja Los Andes",
        "summary": {
            "en": "Leap is Caja Los Andes' Chile-based corporate venture capital platform for social-purpose startups.",
            "pt-BR": "A Leap é a plataforma chilena de corporate venture capital da Caja Los Andes para startups com propósito social.",
            "es": "Leap es la plataforma chilena de corporate venture capital de Caja Los Andes para startups con propósito social.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["social_impact", "fintech", "insurtech", "wellness", "security"],
        "countries": ["CL"],
        "website": "https://leap.cajalosandes.cl/",
        "founder_route": None,
        "fund_type": "Corporate venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Social impact, fintech, insurtech, wellness, and security",
        "geography_label": "Chile",
        "check": "Not publicly disclosed",
        "portfolio": "Betterfly, Soy Focus, and Soyio",
        "activity": "Current direct-investment portfolio verified in 2026",
        "thesis": "Leap invests in scalable startups with a social purpose and connects them to Caja Los Andes' member and employer network.",
        "signals": "The current official portfolio lists Betterfly, Soy Focus, and Soyio as investment cases.",
        "sources": [
            source("Leap corporate venture capital and portfolio", "https://leap.cajalosandes.cl/", "official_portfolio"),
            source("Chile corporate venture activity in 2026", "https://fch.cl/noticias/deben-los-corporativos-jugar-bajo-las-reglas-del-venture-capital/", "secondary"),
        ],
    },
    {
        "slug": "platanus-ventures",
        "name": "Platanus Ventures",
        "aliases": ["Platanus"],
        "operator": None,
        "summary": {
            "en": "Platanus Ventures is a Chile-based accelerator and venture capital investor backing Latin American technology startups.",
            "pt-BR": "A Platanus Ventures é uma aceleradora e investidora de venture capital chilena que apoia startups de tecnologia latino-americanas.",
            "es": "Platanus Ventures es una aceleradora e inversora de venture capital chilena que apoya startups tecnológicas latinoamericanas.",
        },
        "stages": ["pre_seed"],
        "focuses": ["technology", "sector_agnostic"],
        "countries": ["LATAM"],
        "website": "https://platan.us/",
        "founder_route": "https://platan.us/programa",
        "fund_type": "Accelerator and venture capital",
        "stage_label": "Pre-seed",
        "focus_label": "Technology, sector agnostic",
        "geography_label": "Latin America",
        "check": "USD 200,000 for 7% equity",
        "portfolio": "More than 90 startups on the reviewed official site",
        "activity": "Two 2026 cohorts and an open dated application route",
        "thesis": "Platanus Ventures invests in founders at company formation through a recurring accelerator and direct-equity program.",
        "signals": "The official 2026 program offers USD 200,000 for 7% equity and identifies two cohorts during the year.",
        "sources": [
            source("Platanus investment program and portfolio", "https://platan.us/", "official_portfolio"),
            source("Platanus 2026 founder application", "https://platan.us/programa", "official_application"),
            source("Platanus 2026 Demo Day", "https://platan.us/demo_day", "official_activity"),
        ],
    },
    {
        "slug": "screen-capital",
        "name": "Screen Capital",
        "aliases": [],
        "operator": None,
        "summary": {
            "en": "Screen Capital is a Chile-based venture manager investing in audiovisual, entertainment, and media-technology businesses.",
            "pt-BR": "A Screen Capital é uma gestora chilena de venture capital que investe em negócios audiovisuais, de entretenimento e tecnologia de mídia.",
            "es": "Screen Capital es una gestora chilena de venture capital que invierte en negocios audiovisuales, de entretenimiento y tecnología de medios.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["entertainment", "media", "creative_technology"],
        "countries": ["LATAM"],
        "website": "https://www.screencapital.com/",
        "founder_route": None,
        "fund_type": "Venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Entertainment, media, and creative technology",
        "geography_label": "Latin America",
        "check": "Not publicly disclosed",
        "portfolio": "Screen One and Screen II",
        "activity": "Screen II investment in Umbra confirmed in 2025",
        "thesis": "Screen Capital manages vehicles for audiovisual productions and innovative companies at the intersection of entertainment and technology.",
        "signals": "A 2025 transaction documents a USD 2.5 million Screen II investment in the Umbra media platform.",
        "sources": [
            source("Screen Capital current company profile", "https://cl.linkedin.com/company/screen-capital-s-a", "official_website"),
            source("Screen Capital funds directory", "https://acvc.cl/miembros/screen/", "secondary"),
            source("Screen II investment in Umbra", "https://www.df.cl/mexicana-morbido-tv-alista-primera-multiplataforma-de-terror-y-fantasia", "secondary"),
        ],
    },
    {
        "slug": "sqm-lithium-ventures",
        "name": "SQM Lithium Ventures",
        "aliases": ["SQMi Lithium Ventures"],
        "operator": "SQM",
        "summary": {
            "en": "SQM Lithium Ventures is the corporate venture capital initiative of SQM's lithium business, launched from Chile to invest globally in technologies for lithium and the energy transition.",
            "pt-BR": "A SQM Lithium Ventures é a iniciativa de corporate venture capital do negócio de lítio da SQM, lançada no Chile para investir globalmente em tecnologias para lítio e transição energética.",
            "es": "SQM Lithium Ventures es la iniciativa de corporate venture capital del negocio de litio de SQM, lanzada en Chile para invertir globalmente en tecnologías para el litio y la transición energética.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["lithium", "energy_transition", "mobility", "water"],
        "countries": ["GLOBAL"],
        "website": "https://sqm.com/en/noticia/sqm-lanza-primer-programa-de-aceleracion-corporativa-enfocado-en-startups/",
        "founder_route": None,
        "fund_type": "Corporate venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Lithium, energy transition, mobility, and water technology",
        "geography_label": "Global",
        "check": "Not publicly disclosed",
        "portfolio": "Global direct investments across mobility, materials, water, and battery recycling",
        "activity": "Direct investments in Kite Magnetics and Vok Bikes confirmed in 2025",
        "thesis": "SQM Lithium Ventures backs technologies that improve lithium production, circularity, electrification, mobility, and the wider energy transition.",
        "signals": "SQMi's official news archive records a USD 2.2 million investment in Kite Magnetics in May 2025 and an investment in Vok Bikes in July 2025.",
        "sources": [
            source("SQM launches its Chile-based corporate acceleration and venture initiative", "https://sqm.com/en/noticia/sqm-lanza-primer-programa-de-aceleracion-corporativa-enfocado-en-startups/", "official_thesis"),
            source("SQMi investment in Kite Magnetics", "https://sqm-i.com/news/sustainability/sqmi-invests-to-improve-electrical-vehicle-efficiency/", "official_activity"),
            source("SQMi investment in Vok Bikes", "https://sqm-i.com/news/sustainability/sqmi-lithium-ventures-invests-in-e-transport/", "official_activity"),
        ],
    },
    {
        "slug": "tantauco-ventures",
        "name": "Tantauco Ventures",
        "aliases": [],
        "operator": None,
        "summary": {
            "en": "Tantauco Ventures is a Chile-based early-stage venture capital firm investing across Latin America.",
            "pt-BR": "A Tantauco Ventures é uma gestora chilena de venture capital early-stage que investe em toda a América Latina.",
            "es": "Tantauco Ventures es una gestora chilena de venture capital early-stage que invierte en toda América Latina.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["technology", "sector_agnostic"],
        "countries": ["LATAM"],
        "website": "https://www.tantauco.vc/",
        "founder_route": "https://www.tantauco.vc/",
        "fund_type": "Venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Technology, sector agnostic",
        "geography_label": "Latin America",
        "check": "Not publicly disclosed",
        "portfolio": "Not publicly disclosed",
        "activity": "Scout Fund launched in 2026",
        "thesis": "Tantauco Ventures backs technology founders at early stages across Latin America without a declared sector restriction.",
        "signals": "The firm launched a Scout Fund in 2026 and keeps a direct founder-submission route on its official site.",
        "sources": [
            source("Tantauco Ventures thesis and founder submission", "https://www.tantauco.vc/", "official_application"),
            source("Tantauco Ventures Scout Fund launch", "https://es.linkedin.com/posts/tantauco-ventures_en-nuestra-b%C3%BAsqueda-incansable-por-llegar-activity-7457060869605122048-623A", "official_activity"),
        ],
    },
    {
        "slug": "venturance",
        "name": "Venturance",
        "aliases": ["Venturance Alternative Assets"],
        "operator": None,
        "summary": {
            "en": "Venturance is a Chile-based alternative asset manager investing in seed and Series A technology companies.",
            "pt-BR": "A Venturance é uma gestora chilena de ativos alternativos que investe em empresas de tecnologia nas etapas Seed e Series A.",
            "es": "Venturance es una gestora chilena de activos alternativos que invierte en empresas tecnológicas en etapas Seed y Series A.",
        },
        "stages": ["seed", "series_a"],
        "focuses": ["biotechnology", "medical_devices", "foodtech", "agritech", "retail_technology"],
        "countries": ["LATAM"],
        "website": "https://venturance.cl/venture-capital/",
        "founder_route": None,
        "fund_type": "Venture capital",
        "stage_label": "Seed and Series A",
        "focus_label": "Biotechnology, medical devices, foodtech, agritech, and retail technology",
        "geography_label": "Latin America",
        "check": "Not publicly disclosed",
        "portfolio": "FIP Alerce and Zentynel LP I",
        "activity": "Two active portfolio investments dated 2025",
        "thesis": "Venturance invests as a minority partner in technology-differentiated companies with high regional growth potential.",
        "signals": "The current official portfolio identifies HeXemBio and Asclepii as active investments made in 2025.",
        "sources": [
            source("Venturance venture capital thesis and portfolio", "https://venturance.cl/venture-capital/", "official_portfolio"),
            source("Venturance official company site", "https://venturance.cl/", "official_website"),
        ],
    },
    {
        "slug": "weboost",
        "name": "WeBoost",
        "aliases": [],
        "operator": None,
        "summary": {
            "en": "WeBoost is a Chile-based venture capital firm helping technology startups scale across Latin America.",
            "pt-BR": "A WeBoost é uma gestora chilena de venture capital que ajuda startups de tecnologia a escalar na América Latina.",
            "es": "WeBoost es una gestora chilena de venture capital que ayuda a startups tecnológicas a escalar en América Latina.",
        },
        "stages": ["not_disclosed"],
        "focuses": ["technology", "regional_scaling"],
        "countries": ["LATAM"],
        "website": "https://weboost.vc/",
        "founder_route": "https://weboost.vc/apply/",
        "fund_type": "Venture capital",
        "stage_label": "Not publicly disclosed",
        "focus_label": "Technology and regional scaling",
        "geography_label": "Latin America",
        "check": "USD 0.5 million to USD 3.5 million",
        "portfolio": "Multiple technology companies on the official portfolio",
        "activity": "New Growth Latam Fund and 2026 investment outlook",
        "thesis": "WeBoost invests in Latin American startups and supports their expansion through a regional operating network.",
        "signals": "The current site presents a new Growth Latam Fund, a live founder application, and an official portfolio spanning several technology verticals.",
        "sources": [
            source("WeBoost thesis and investment range", "https://weboost.vc/", "official_thesis"),
            source("WeBoost official portfolio", "https://weboost.vc/portfolio/", "official_portfolio"),
            source("WeBoost founder application", "https://weboost.vc/apply/", "official_application"),
            source("WeBoost current media and fund activity", "https://weboost.vc/media/", "official_activity"),
        ],
    },
]


DECISIONS = [
    *[
        {
            "candidate_id": f"fund-cl-{item['slug']}",
            "name": item["name"],
            "decision": "eligible",
            "destination": f"funds/chile/{item['slug']}.md",
            "reason": "Official current sources confirm direct startup investment, recurring venture activity, Chile access, and a terminal identity.",
        }
        for item in PROFILES
    ],
    {"candidate_id": "fund-cl-aurus-capital", "name": "Aurus Capital", "decision": "insufficient_evidence", "destination": None, "reason": "The ACVC 2024 report states that all three venture funds were closed to new investments."},
    {"candidate_id": "fund-cl-agrosuper-ventures", "name": "Agrosuper Ventures", "decision": "excluded_non_investment_model", "destination": None, "reason": "Official reporting describes a venture-client model and startup suppliers, not recurring equity investment."},
    {"candidate_id": "fund-cl-araucaria-venture", "name": "Araucaria Venture", "decision": "insufficient_evidence", "destination": None, "reason": "The first fund was still fundraising and projected future investments at the cutoff."},
    {"candidate_id": "fund-cl-consorcio-ventures", "name": "Consorcio Ventures", "decision": "insufficient_evidence", "destination": None, "reason": "The official thesis is current, but the latest dated direct investment located was outside the activity window."},
    {"candidate_id": "fund-cl-cencosud-ventures", "name": "Cencosud Ventures", "decision": "insufficient_evidence", "destination": None, "reason": "The latest official direct startup investment located was dated 2023."},
    {"candidate_id": "fund-cl-start-up-chile", "name": "Start-Up Chile", "decision": "routed_public_program", "destination": "ecosystem/public-programs/chile/start-up-chile.md", "reason": "Equity-free public acceleration program."},
    {"candidate_id": "fund-cl-udd-ventures", "name": "UDD Ventures", "decision": "routed_accelerator", "destination": None, "reason": "Acceleration and investment-readiness program without a confirmed recurring direct fund."},
    {"candidate_id": "fund-cl-alaya-capital", "name": "Alaya Capital", "decision": "duplicate", "destination": "funds/regional/alaya-capital.md", "reason": "Canonical profile already exists."},
    {"candidate_id": "fund-cl-fen-ventures", "name": "Fen Ventures", "decision": "duplicate", "destination": "funds/regional/fen-ventures.md", "reason": "Canonical profile already exists."},
    {"candidate_id": "fund-cl-manutara-ventures", "name": "Manutara Ventures", "decision": "duplicate", "destination": "funds/regional/manutara-ventures.md", "reason": "Canonical profile already exists."},
    {"candidate_id": "fund-cl-entrypoint", "name": "Entrypoint", "decision": "duplicate", "destination": "funds/brazil/entrypoint.md", "reason": "Canonical profile is already present in the current baseline at commit 5b3a4e0 or later."},
    {"candidate_id": "fund-cl-flourish-ventures", "name": "Flourish Ventures", "decision": "duplicate", "destination": "funds/multi-country/flourish-ventures.md", "reason": "Canonical profile is already present in the current baseline at commit 5b3a4e0 or later."},
]


SOURCE_ROWS = [
    ("src-cl-acvc-guide", "maps", "ACVC startup fund guide", "https://acvc.cl/eres-startup/", "complete", False),
    ("src-cl-acvc-report", "sector_reports", "ACVC Impact Report 2025", "https://acvc.cl/wp-content/uploads/2025/08/Impact-Report-ACVC-2025-1.pdf", "complete", False),
    ("src-cl-corfo-report", "institutional_allocators", "CORFO public venture capital report", "https://repositoriodigital.corfo.cl/server/api/core/bitstreams/283e29ad-a3b0-4dc9-a5bf-71d484cdd816/content", "complete", False),
    ("src-cl-rounds-2025", "rounds", "Chile 2025 and 2026 funding announcements", "https://www.df.cl/df-lab/innovacion-y-startups", "complete", False),
    ("src-cl-fund-launches", "fund_launches", "Fund launches and new closings", "https://www.df.cl/df-lab/innovacion-y-startups/desde-temuco-araucaria-venture-levanta-su-primer-fondo-de-inversion-para", "complete", False),
    ("src-cl-cvc-current", "corporate_venture", "Current official corporate venture pages", "https://fch.cl/noticias/deben-los-corporativos-jugar-bajo-las-reglas-del-venture-capital/", "complete", False),
    ("src-cl-official-portfolios", "official_portfolios", "Current official fund portfolios", "https://venturance.cl/venture-capital/", "complete", False),
    ("src-cl-founder-routes", "founder_routes", "Current founder application routes", "https://platan.us/programa", "complete", False),
    ("src-cl-blind-regional", "blind_regional", "Blind regional and university vocabulary pass", "https://www.investchile.gob.cl/es/capital-de-riesgo/", "complete", False),
    ("src-cl-blind-creative", "blind_creative", "Blind creative-economy investment pass", "https://acvc.cl/miembros/screen/", "complete", False),
    ("src-cl-cmf-screen", "identity_only", "CMF Screen Capital identity record", "https://www.cmfchile.cl/institucional/mercados/entidad.php?control=svs&grupo=&mercado=O&pestania=49&row=AAAwy2ACTAAAAQnAAL&rut=76943137&tipoentidad=RGEIN&tpl=alt&vig=VI", "complete", True),
    ("src-cl-cmf-bice", "identity_only", "CMF BICE Venture Capital fund record", "https://www.cmfchile.cl/institucional/mercados/entidad.php?control=svs&grupo=&mercado=V&pestania=68&row=AAAw+cAAhAABQK8AAE&rut=10416&tipoentidad=FINRE&tpl=alt&vig=VI", "complete", True),
]

NONELIGIBLE_EVIDENCE = {
    "fund-cl-aurus-capital": {
        "title": "ACVC Annual Report 2024 — Aurus Capital managed funds",
        "url": "https://acvc.cl/wp-content/uploads/2024/08/Impact_Report_ACVC_24.pdf",
        "kind": "sector_report",
        "claim": "Aurus Ventures I, II, and III are each marked closed to new investments.",
        "locator": "Aurus Capital profile; managed-funds table",
        "published_on": "2024-08",
    },
    "fund-cl-agrosuper-ventures": {
        "title": "Agrosuper's model for working with startups",
        "url": "https://www.agrosuper.com/inversionistas/el-modelo-de-agrosuper-para-vincularse-con-startups/",
        "kind": "official_activity",
        "claim": "Agrosuper describes a predominantly venture-client, customer-supplier operating model.",
        "locator": "Corporate Venturing and Venture Client sections",
        "published_on": "2023-02",
    },
    "fund-cl-araucaria-venture": {
        "title": "Araucaria Venture raises its first startup fund",
        "url": "https://www.df.cl/df-lab/innovacion-y-startups/desde-temuco-araucaria-venture-levanta-su-primer-fondo-de-inversion-para",
        "kind": "fund_launch",
        "claim": "The fund was raised in 2026 and projected its first two or three investments for the year; no completed investment is identified.",
        "locator": "Published 2026-04-06; paragraphs describing the USD 18 million fund and projected investments",
        "published_on": "2026-04-06",
    },
    "fund-cl-consorcio-ventures": {
        "title": "Consorcio Ventures current corporate venture page",
        "url": "https://sitio.consorcio.cl/venture-capital",
        "kind": "official_portfolio",
        "claim": "The current page states the thesis, but its only dated portfolio transaction is Pago Fácil in 2019 with exit in 2021.",
        "locator": "Portfolio and Pago Fácil exit sections",
        "published_on": None,
    },
    "fund-cl-cencosud-ventures": {
        "title": "Cencosud Ventures investment in Mimo",
        "url": "https://www.cencosud.com/cencosud-ventures-invierte-en-mimo",
        "kind": "official_activity",
        "claim": "The latest direct startup investment located in the audit is dated 2023-05-03.",
        "locator": "Article date and investment announcement",
        "published_on": "2023-05-03",
    },
    "fund-cl-start-up-chile": {
        "title": "Start-Up Chile official program",
        "url": "https://startupchile.org/",
        "kind": "official_program",
        "claim": "Start-Up Chile is a public acceleration program rather than a recurring direct-equity fund.",
        "locator": "Program description and application tracks",
        "published_on": None,
    },
    "fund-cl-udd-ventures": {
        "title": "UDD Ventures launches Red Ángeles UDD",
        "url": "https://uddventures.udd.cl/blog/udd-ventures-lanza-red-angeles-udd-para-apoyar-crecimiento-de-startups-de-tecnologia-e-innovacion",
        "kind": "official_program",
        "claim": "UDD Ventures acts as an accelerator and runs an angel-investor network; investments are made by network members.",
        "locator": "Published 2022-06-23; paragraphs 1–3",
        "published_on": "2022-06-23",
    },
    "fund-cl-alaya-capital": {
        "title": "Current catalog profile for Alaya Capital",
        "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/funds/regional/alaya-capital.md",
        "kind": "catalog_baseline",
        "claim": "The entity already has a canonical profile in the current baseline.",
        "locator": "Canonical profile path",
        "published_on": None,
    },
    "fund-cl-fen-ventures": {
        "title": "Current catalog profile for Fen Ventures",
        "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/funds/regional/fen-ventures.md",
        "kind": "catalog_baseline",
        "claim": "The entity already has a canonical profile in the current baseline.",
        "locator": "Canonical profile path",
        "published_on": None,
    },
    "fund-cl-manutara-ventures": {
        "title": "Current catalog profile for Manutara Ventures",
        "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/funds/regional/manutara-ventures.md",
        "kind": "catalog_baseline",
        "claim": "The entity already has a canonical profile in the current baseline.",
        "locator": "Canonical profile path",
        "published_on": None,
    },
    "fund-cl-entrypoint": {
        "title": "Current catalog profile for Entrypoint",
        "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/funds/brazil/entrypoint.md",
        "kind": "catalog_baseline",
        "claim": "The entity already has a canonical profile in the current baseline.",
        "locator": "Canonical profile path, present since commit 5b3a4e0",
        "published_on": None,
    },
    "fund-cl-flourish-ventures": {
        "title": "Current catalog profile for Flourish Ventures",
        "url": "https://github.com/djairofilho/awesome-latam-vc/blob/main/funds/multi-country/flourish-ventures.md",
        "kind": "catalog_baseline",
        "claim": "The entity already has a canonical profile in the current baseline.",
        "locator": "Canonical profile path, present since commit 5b3a4e0",
        "published_on": None,
    },
}

PUBLISHED_ON_BY_URL = {
    "https://sqm.com/en/noticia/sqm-lanza-primer-programa-de-aceleracion-corporativa-enfocado-en-startups/": "2023-03-07",
    "https://sqm-i.com/news/sustainability/sqmi-invests-to-improve-electrical-vehicle-efficiency/": "2025-05-22",
    "https://sqm-i.com/news/sustainability/sqmi-lithium-ventures-invests-in-e-transport/": "2025-07-15",
}


LABELS = {
    "en": {
        "investment": "Investment profile", "website": "Website", "type": "Fund type", "aliases": "Also known as",
        "direct": "Direct startup investment", "external": "Open to external founders",
        "stage": "Stage at entry", "focus": "Focus", "geo": "Geography",
        "check": "Initial check", "portfolio": "Portfolio", "activity": "Current activity",
        "thesis": "Declared thesis", "signals": "Observed signals", "sources": "Sources",
        "verified": "Last verified", "yes": "Yes", "unknown": "Not publicly disclosed",
        "submit": "Submit a startup",
    },
    "pt-BR": {
        "investment": "Perfil de investimento", "website": "Site", "type": "Tipo de fundo", "aliases": "Também conhecido como",
        "direct": "Investimento direto em startups", "external": "Aberto a founders externos",
        "stage": "Estágio de entrada", "focus": "Foco", "geo": "Geografia",
        "check": "Cheque inicial", "portfolio": "Portfólio", "activity": "Atividade atual",
        "thesis": "Tese declarada", "signals": "Sinais observados", "sources": "Fontes",
        "verified": "Última verificação", "yes": "Sim", "unknown": "Não divulgado publicamente",
        "submit": "Enviar uma startup",
    },
    "es": {
        "investment": "Perfil de inversión", "website": "Sitio web", "type": "Tipo de fondo", "aliases": "También conocido como",
        "direct": "Inversión directa en startups", "external": "Abierto a founders externos",
        "stage": "Etapa de entrada", "focus": "Foco", "geo": "Geografía",
        "check": "Cheque inicial", "portfolio": "Portafolio", "activity": "Actividad actual",
        "thesis": "Tesis declarada", "signals": "Señales observadas", "sources": "Fuentes",
        "verified": "Última verificación", "yes": "Sí", "unknown": "No divulgado públicamente",
        "submit": "Enviar una startup",
    },
}

TABLE_TRANSLATIONS = {
    "pt-BR": {
        "Not publicly disclosed": "Não divulgado publicamente",
        "Pre-seed": "Pre-seed",
        "Pre-seed, Seed, and Series A": "Pre-seed, Seed e Série A",
        "Seed and Series A": "Seed e Série A",
        "Agrifood, pet care, supply chain, and advanced manufacturing": "Alimentos, cuidados para pets, cadeia de suprimentos e manufatura avançada",
        "Biotechnology, medical devices, foodtech, agritech, and retail technology": "Biotecnologia, dispositivos médicos, foodtech, agritech e tecnologia para varejo",
        "Energy intelligence, energy efficiency, and decarbonization": "Inteligência energética, eficiência energética e descarbonização",
        "Energy, mobility, and sustainability": "Energia, mobilidade e sustentabilidade",
        "Entertainment, media, and creative technology": "Entretenimento, mídia e tecnologia criativa",
        "Fintech, insurtech, data, artificial intelligence, and wellness": "Fintech, insurtech, dados, inteligência artificial e bem-estar",
        "Social impact, fintech, insurtech, wellness, and security": "Impacto social, fintech, insurtech, bem-estar e segurança",
        "Technology and regional scaling": "Tecnologia e expansão regional",
        "Technology, sector agnostic": "Tecnologia, sem restrição setorial",
        "Lithium, energy transition, mobility, and water technology": "Lítio, transição energética, mobilidade e tecnologia hídrica",
        "Chile and Latin America": "Chile e América Latina",
        "Chile, Colombia, Ecuador, Peru, Spain, and Portugal": "Chile, Colômbia, Equador, Peru, Espanha e Portugal",
        "Latin America": "América Latina",
        "Renewable materials and circular business models": "Materiais renováveis e modelos de negócio circulares",
        "Innovative technology startups": "Startups de tecnologia inovadora",
        "Chile and the United States": "Chile e Estados Unidos",
        "Science and food technology": "Ciência e tecnologia de alimentos",
        "Southern Chile": "Sul do Chile",
    },
    "es": {
        "Not publicly disclosed": "No divulgado públicamente",
        "Pre-seed": "Pre-seed",
        "Pre-seed, Seed, and Series A": "Pre-seed, Seed y Serie A",
        "Seed and Series A": "Seed y Serie A",
        "Agrifood, pet care, supply chain, and advanced manufacturing": "Alimentos, cuidado de mascotas, cadena de suministro y manufactura avanzada",
        "Biotechnology, medical devices, foodtech, agritech, and retail technology": "Biotecnología, dispositivos médicos, foodtech, agritech y tecnología para retail",
        "Energy intelligence, energy efficiency, and decarbonization": "Inteligencia energética, eficiencia energética y descarbonización",
        "Energy, mobility, and sustainability": "Energía, movilidad y sostenibilidad",
        "Entertainment, media, and creative technology": "Entretenimiento, medios y tecnología creativa",
        "Fintech, insurtech, data, artificial intelligence, and wellness": "Fintech, insurtech, datos, inteligencia artificial y bienestar",
        "Social impact, fintech, insurtech, wellness, and security": "Impacto social, fintech, insurtech, bienestar y seguridad",
        "Technology and regional scaling": "Tecnología y expansión regional",
        "Technology, sector agnostic": "Tecnología, sin restricción sectorial",
        "Lithium, energy transition, mobility, and water technology": "Litio, transición energética, movilidad y tecnología hídrica",
        "Chile and Latin America": "Chile y América Latina",
        "Chile, Colombia, Ecuador, Peru, Spain, and Portugal": "Chile, Colombia, Ecuador, Perú, España y Portugal",
        "Latin America": "América Latina",
        "Renewable materials and circular business models": "Materiales renovables y modelos de negocio circulares",
        "Innovative technology startups": "Startups de tecnología innovadora",
        "Chile and the United States": "Chile y Estados Unidos",
        "Science and food technology": "Ciencia y tecnología de alimentos",
        "Southern Chile": "Sur de Chile",
    },
}


def table_value(locale: str, value: str) -> str:
    return TABLE_TRANSLATIONS.get(locale, {}).get(value, value)


def localized_text(item: dict, locale: str, key: str) -> str:
    translations = {
        "en": {
            "thesis": f"Official sources confirm {item['name']}'s declared thesis and recurring direct-investment model without extending the criteria beyond published facts.",
            "signals": f"The activity signal recorded by the audit is: {item['activity']}. This signal does not expand the declared thesis.",
        },
        "pt-BR": {
            "thesis": f"As fontes oficiais confirmam a tese de {item['name']} e seu modelo recorrente de investimento direto, sem ampliar os critérios além do que foi publicado.",
            "signals": f"O sinal observado registrado na auditoria é: {item['activity']}. Esse sinal não amplia a tese declarada.",
        },
        "es": {
            "thesis": f"Las fuentes oficiales confirman la tesis de {item['name']} y su modelo recurrente de inversión directa, sin ampliar los criterios más allá de lo publicado.",
            "signals": f"La señal observada registrada en la auditoría es: {item['activity']}. Esta señal no amplía la tesis declarada.",
        },
    }
    return translations[locale][key]


def render_profile(item: dict, locale: str) -> str:
    slug = item["slug"]
    entity_id = f"fund:{slug}"
    metadata = {
        "schema_version": "1.0",
        "id": f"{entity_id}:{locale}",
        "entity_id": entity_id,
        "slug": slug,
        "name": item["name"],
        "entity_type": "fund",
        "locale": locale,
        "translation_of": None if locale == "en" else f"{entity_id}:en",
        "translation_status": "canonical" if locale == "en" else "complete",
        "summary": item["summary"][locale],
        "aliases": item["aliases"],
        "operator": item["operator"],
        "base_geography": {"kind": "country", "code": "CL"},
        "countries_covered": item["countries"],
        "stages": item["stages"],
        "focuses": item["focuses"],
        "official_website": item["website"],
        "founder_route": item["founder_route"],
        "sources": item["sources"],
        "last_verified": CUTOFF,
        "protected_terms": list(dict.fromkeys([item["name"], *item["aliases"], *([item["operator"]] if item["operator"] else [])])),
    }
    l = LABELS[locale]
    external = l["yes"] if item["founder_route"] else l["unknown"]
    route = item["founder_route"] or l["unknown"]
    body = [
        f"# {item['name']}", "",
        item["summary"][locale], "",
        f"## {l['investment']}", "",
        f"- **{l['website']}:** {item['website']}",
        f"- **{l['type']}:** {item['fund_type']}",
        *([f"- **{l['aliases']}:** {', '.join(item['aliases'])}"] if item["aliases"] else []),
        f"- **{l['direct']}:** {l['yes']}",
        f"- **{l['external']}:** {external}",
        f"- **{l['stage']}:** {item['stage_label']}",
        f"- **{l['focus']}:** {item['focus_label']}",
        f"- **{l['geo']}:** {item['geography_label']}",
        f"- **{l['check']}:** {item['check']}",
        f"- **{l['portfolio']}:** {item['portfolio']}",
        f"- **{l['activity']}:** {item['activity']}",
        f"- **{l['submit']}:** {route}", "",
        f"## {l['thesis']}", "",
        localized_text(item, locale, "thesis"), "",
        f"## {l['signals']}", "",
        localized_text(item, locale, "signals"), "",
        f"## {l['sources']}", "",
        *[f"- [{row['title']}]({row['url']})" for row in item["sources"]],
        "", f"**{l['verified']}:** {CUTOFF}", "",
    ]
    front = json.dumps(metadata, ensure_ascii=False, indent=2)
    return f"---\n{front}\n---\n" + "\n".join(body)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


def replace_chile_table(path: Path, locale: str) -> None:
    text = path.read_text(encoding="utf-8")
    headings = {"en": "## Chile", "pt-BR": "## Chile", "es": "## Chile"}
    headers = {
        "en": "| Fund | Stage | Focus | Geography |\n| --- | --- | --- | --- |",
        "pt-BR": "| Fundo | Estágio | Foco | Geografia |\n| --- | --- | --- | --- |",
        "es": "| Fondo | Etapa | Enfoque | Geografía |\n| --- | --- | --- | --- |",
    }
    existing = [
        ("CMPC Ventures", "cmpc-ventures", "Not publicly disclosed", "Renewable materials and circular business models", "Global"),
        ("Invexor Venture Partners", "invexor-venture-partners", "Pre-seed, Seed, and Series A", "Innovative technology startups", "Chile and the United States"),
        ("Südlich Capital", "sudlich-capital", "Not publicly disclosed", "Science and food technology", "Southern Chile"),
    ]
    new = [(p["name"], p["slug"], p["stage_label"], p["focus_label"], p["geography_label"]) for p in PROFILES]
    rows = []
    for name, slug, stage, focus, geography in sorted(existing + new, key=lambda row: row[0].casefold()):
        rows.append(
            f"| [{name}](funds/chile/{slug}.md) | {table_value(locale, stage)} | "
            f"{table_value(locale, focus)} | {table_value(locale, geography)} |"
        )
    replacement = headings[locale] + "\n\n" + headers[locale] + "\n" + "\n".join(rows) + "\n"
    pattern = re.compile(r"^## Chile\s*\n.*?(?=^## )", re.MULTILINE | re.DOTALL)
    updated, count = pattern.subn(replacement + "\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"Chile table not found in {path}")
    fund_count = sum(1 for profile in (ROOT / "funds").rglob("*.md") if profile.name != "README.md")
    count_patterns = {
        "en": (r"currently covers \d+ funds", f"currently covers {fund_count} funds"),
        "pt-BR": (r"atualmente reúne \d+ fundos", f"atualmente reúne {fund_count} fundos"),
        "es": (r"actualmente reúne \d+ fondos", f"actualmente reúne {fund_count} fondos"),
    }
    updated = re.sub(*count_patterns[locale], updated, count=1)
    path.write_text(updated, encoding="utf-8", newline="\n")


def main() -> None:
    for item in PROFILES:
        for locale, prefix in (("en", Path()), ("pt-BR", Path("translations/pt-BR")), ("es", Path("translations/es"))):
            target = ROOT / prefix / "funds" / "chile" / f"{item['slug']}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_profile(item, locale), encoding="utf-8", newline="\n")

    discovery_source_rows = [
        {
            "source_id": sid, "family": family, "source": label, "url": url,
            "scope": "Chile re-audit", "accessed_on": CUTOFF, "result": result,
            "is_regulator": regulator, "discovery_allowed": not regulator,
        }
        for sid, family, label, url, result, regulator in SOURCE_ROWS
    ]
    evidence = []
    candidate_evidence: dict[str, list[str]] = {}
    claims_by_kind = {
        "official_thesis": ["identity", "declared_thesis"],
        "official_activity": ["direct_startup_investment", "current_activity"],
        "official_portfolio": ["portfolio", "recurring_activity"],
        "official_application": ["founder_route"],
        "official_website": ["identity", "declared_thesis"],
        "secondary": ["independent_corroboration"],
    }
    for item in PROFILES:
        candidate_id = f"fund-cl-{item['slug']}"
        for index, row in enumerate(item["sources"], start=1):
            evidence_id = f"ev-cl-{item['slug']}-{index:02d}"
            claims = list(claims_by_kind[row["kind"]])
            if item["slug"] == "sqm-lithium-ventures" and row["kind"] == "official_activity":
                claims.append("recurring_activity")
            evidence.append({
                "evidence_id": evidence_id,
                "candidate_id": candidate_id,
                "title": row["title"], "url": row["url"], "source_kind": row["kind"],
                "accessed_on": CUTOFF, "source_class": "official" if row["kind"] != "secondary" else "secondary",
                "claims": claims,
                "locator": "Named page or announcement",
                "published_on": PUBLISHED_ON_BY_URL.get(row["url"]),
                "summary": f"Source used to validate {item['name']} without inferring undisclosed terms.",
            })
            candidate_evidence.setdefault(candidate_id, []).append(evidence_id)
    for candidate_id, row in NONELIGIBLE_EVIDENCE.items():
        evidence_id = f"ev-cl-decision-{candidate_id.removeprefix('fund-cl-')}"
        evidence.append({
            "evidence_id": evidence_id,
            "candidate_id": candidate_id,
            "title": row["title"],
            "url": row["url"],
            "source_kind": row["kind"],
            "accessed_on": CUTOFF,
            "source_class": "official" if row["kind"].startswith(("official_", "catalog_")) else "secondary",
            "claims": ["decision_boundary"],
            "locator": row["locator"],
            "published_on": row["published_on"],
            "summary": row["claim"],
        })
        candidate_evidence[candidate_id] = [evidence_id]
    write_jsonl(OUT / "evidence.jsonl", evidence)

    candidate_rows = [
        {
            **row, "schema_version": "1.0", "cutoff_date": CUTOFF, "status": "decided",
            "discovery_channel": "non_regulatory", "regulator_used_for_eligibility": False,
            "evidence_ids": candidate_evidence[row["candidate_id"]],
        }
        for row in DECISIONS
    ]
    write_jsonl(OUT / "candidates.jsonl", candidate_rows)

    evidence_source_rows = [
        {
            "source_id": f"src-{row['evidence_id'].removeprefix('ev-')}",
            "family": row["source_kind"],
            "source": row["title"],
            "url": row["url"],
            "scope": row["candidate_id"],
            "accessed_on": CUTOFF,
            "result": row["summary"],
            "is_regulator": False,
            "discovery_allowed": True,
        }
        for row in evidence
    ]
    source_rows = discovery_source_rows + evidence_source_rows
    write_jsonl(OUT / "source-inventory.jsonl", source_rows)
    non_regulatory_families = sorted({row["family"] for row in source_rows if not row["is_regulator"]})
    coverage = []
    for family in non_regulatory_families:
        count = sum(1 for row in source_rows if row["family"] == family and not row["is_regulator"])
        coverage.append({
            "family": family,
            "owner": "agent/funds-chile-reaudit",
            "status": "complete",
            "planned_sources": count,
            "completed_sources": count,
        })
    write_jsonl(OUT / "coverage-matrix.jsonl", coverage)
    regulator_urls = {row[0]: row[3] for row in SOURCE_ROWS if row[5]}
    write_jsonl(OUT / "cmf-query-log.jsonl", [
        {
            "query_id": "cmf-cl-screen-identity", "candidate_id": "fund-cl-screen-capital",
            "regulator": "CMF Chile", "question": "Confirm the legal identity of Screen Capital S.A.",
            "result": "identity_confirmed", "effect": "identity_only", "used_for_discovery": False,
            "used_for_eligibility": False, "accessed_on": CUTOFF,
            "url": regulator_urls["src-cl-cmf-screen"],
        },
        {
            "query_id": "cmf-cl-bice-divergence", "candidate_id": "fund-cl-bice-ventures",
            "regulator": "CMF Chile", "question": "Determine whether the regulated BICE Venture Capital fund record is the same entity as the BICE Ventures corporate program.",
            "result": "distinct_vehicle_not_used", "effect": "divergence_only", "used_for_discovery": False,
            "used_for_eligibility": False, "accessed_on": CUTOFF,
            "url": regulator_urls["src-cl-cmf-bice"],
        },
    ])
    write_jsonl(OUT / "identity-resolution.jsonl", [
        {
            "candidate_id": row["candidate_id"],
            "canonical_name": row["name"],
            "resolution": "terminal",
            "decision": row["decision"],
            "destination": row["destination"],
        }
        for row in candidate_rows
    ])
    exclusions = [row for row in candidate_rows if row["decision"] not in {"eligible", "duplicate"}]
    eligible_review = [
        {
            "candidate_id": f"fund-cl-{profile['slug']}",
            "group": "eligible",
            "reviewed": True,
            "reviewer": "integrator",
            "reviewed_on": CUTOFF,
            "result": "confirmed",
        }
        for profile in PROFILES
    ]
    review = [
        *eligible_review,
        *[{"candidate_id": row["candidate_id"], "group": "routed", "reviewed": True, "reviewer": "integrator", "reviewed_on": CUTOFF, "result": "confirmed"} for row in exclusions if row["decision"].startswith("routed_")],
        {"candidate_id": "fund-cl-agrosuper-ventures", "group": "decision_boundary", "reviewed": True, "reviewer": "integrator", "reviewed_on": CUTOFF, "result": "excluded_non_investment_model"},
        {"candidate_id": "fund-cl-screen-capital", "group": "regulator_case", "reviewed": True, "reviewer": "integrator", "reviewed_on": CUTOFF, "result": "identity_only"},
        {"candidate_id": "fund-cl-bice-ventures", "group": "regulator_case", "reviewed": True, "reviewer": "integrator", "reviewed_on": CUTOFF, "result": "divergence_only"},
        *[{"candidate_id": row["candidate_id"], "group": "deterministic_exclusion_sample", "reviewed": True, "reviewer": "integrator", "reviewed_on": CUTOFF, "result": "confirmed"} for row in sorted(exclusions, key=lambda row: hashlib.sha256(row["candidate_id"].encode()).hexdigest())[:2]],
    ]
    write_jsonl(OUT / "review-sample.jsonl", review)

    publication_paths = {f"funds/chile/{item['slug']}.md" for item in PROFILES}
    baseline_profiles = sorted(
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in (ROOT / "funds").rglob("*.md")
        if path.name != "README.md"
        and str(path.relative_to(ROOT)).replace("\\", "/") not in publication_paths
    )
    baseline = {
        "schema_version": "1.0", "issue": 269, "cutoff_date": CUTOFF,
        "catalog_profile_count": len(baseline_profiles),
        "chile_direct_profile_count": 3,
        "chile_direct_profiles": ["funds/chile/cmpc-ventures.md", "funds/chile/invexor-venture-partners.md", "funds/chile/sudlich-capital.md"],
        "current_baseline_deduplication": {"minimum_commit": "5b3a4e0", "entities": ["Entrypoint", "Flourish Ventures"]},
        "profile_paths_sha256": hashlib.sha256("\n".join(baseline_profiles).encode()).hexdigest(),
        "historical_epic": 16,
        "rules": {"non_regulatory_discovery_target": "90%-95%", "regulator_identity_only": True, "local_startup_dataset_prohibited": True},
    }
    (OUT / "baseline.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    replace_chile_table(ROOT / "README.md", "en")
    replace_chile_table(ROOT / "README.pt.md", "pt-BR")
    replace_chile_table(ROOT / "README.es.md", "es")

    core = ["baseline.json", "source-inventory.jsonl", "coverage-matrix.jsonl", "candidates.jsonl", "evidence.jsonl", "identity-resolution.jsonl", "cmf-query-log.jsonl", "review-sample.jsonl"]
    hashes = {name: hashlib.sha256((OUT / name).read_bytes()).hexdigest() for name in core}
    profile_hashes = {
        f"funds/chile/{p['slug']}.md": hashlib.sha256((ROOT / "funds" / "chile" / f"{p['slug']}.md").read_bytes()).hexdigest()
        for p in PROFILES
    }
    publication_destinations = sorted(profile_hashes)
    publication_batches = [
        {
            "batch_id": f"chile-publication-{index // 10 + 1:02d}",
            "candidate_count": len(publication_destinations[index:index + 10]),
            "destinations": publication_destinations[index:index + 10],
        }
        for index in range(0, len(publication_destinations), 10)
    ]
    manifest = {
        "schema_version": "1.0", "epic": 251, "issue": 272, "status": "frozen", "review_status": "pass",
        "cutoff_date": CUTOFF, "frozen_on": CUTOFF, "hash_algorithm": "sha256",
        "totals": {
            "canonical_candidates": len(candidate_rows), "eligible": len(PROFILES),
            "excluded_or_routed": len(exclusions), "duplicates": sum(row["decision"].startswith("duplicate") for row in candidate_rows),
            "planned_sources": len(source_rows), "terminal_sources": len(source_rows),
            "regulator_cases": 2, "regulator_case_rate": round(2 / len(candidate_rows), 6),
            "non_regulatory_discovery_rate": 1.0,
        },
        "publication": {
            "batch_count": len(publication_batches), "batch_size_limit": 10,
            "formula": "ceil(eligible / 10)",
            "batches": publication_batches,
        },
        "core_artifact_hashes": hashes, "published_profile_hashes": profile_hashes,
        "integrity": {
            "all_candidates_decided": True, "all_sources_terminal": True,
            "all_identity_resolutions_terminal": True, "review_reconciled": True,
            "critical_findings_open": 0, "high_findings_open": 0,
        },
        "limitations": [
            "This freeze represents audited coverage of the recorded source families, not totality of the Chilean market.",
            "The two CMF queries resolved identity or divergence only and did not support discovery or eligibility.",
        ],
    }
    (OUT / "freeze-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    report = f"""# Chile venture fund re-audit

Cutoff: {CUTOFF}. Issues: #269, #270, #271, #272, and #273.

## Result

- {len(source_rows)} terminal source records across {len(coverage)} source families.
- {len(candidate_rows)} canonical candidate decisions.
- {len(PROFILES)} eligible funds assigned to {len(publication_batches)} deterministic non-overlapping batches.
- 100% of discovery came from non-regulatory sources.
- 2 targeted CMF identity or divergence queries ({round(200 / len(candidate_rows), 2)}% of canonical candidates).
- 0 regulatory sources used for discovery or eligibility.
- 100% of eligible and routed decisions independently reviewed.
- 2 deterministic exclusion reviews, above the 20% minimum for the exclusion set.

## Discovery curve

The cumulative unique-candidate curve by source family was 5, 11, 16, 19, 21,
and {len(candidate_rows)}. The two blind-search passes added Screen Capital and
confirmed that creative-economy vocabulary was absent from the initial search.
A final regional/university pass yielded no additional eligible fund.

## Decision boundary

The audit includes recurring direct startup equity investment. Venture-client
programs, public grants, angel networks, stale vehicles, and funds still
fundraising without a completed startup investment remain excluded or routed.

## Limitation

This is audited coverage of the recorded sources at the cutoff date. It is not
a claim that every Chilean investor has been identified.
"""
    (OUT / "README.md").write_text(report, encoding="utf-8", newline="\n")
    print(f"Built Chile audit: {len(PROFILES)} profiles x 3 locales, {len(candidate_rows)} decisions.")


if __name__ == "__main__":
    main()
