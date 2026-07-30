#!/usr/bin/env python3
"""Build the deterministic Mexico re-audit and its frozen publication batch."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"

SOURCES = [
    ("mx-event-vcday", "events", "https://mexicovcday.com/", "Mexico VC Day 2026", "complete"),
    ("mx-map-femsa", "maps", "https://www.femsaventures.com/portfolio", "FEMSA Ventures portfolio and fund map", "complete"),
    ("mx-femsa-home", "official_portfolios", "https://www.femsaventures.com/", "FEMSA Ventures", "complete"),
    ("mx-femsa-aloi", "rounds", "https://www.femsaventures.com/blogs/why-we-invested-aloi/914", "Why We Invested: Aloi", "complete"),
    ("mx-mita", "regional_sources", "https://mitaventures.com/en/home/", "MITA Ventures", "complete"),
    ("mx-zacua", "official_portfolios", "https://zacuaventures.com/", "Zacua Ventures", "complete"),
    ("mx-zacua-scout", "launches", "https://zacuaventures.com/zacua-ventures-launches-scout-program/", "Zacua Ventures launches scout program", "complete"),
    ("mx-alphaoak", "launches", "https://www.alphaoakcapital.com/", "AlphaOak Capital", "complete"),
    ("mx-soldiers", "regional_sources", "https://www.soldiersfieldangels.com/", "Soldiers Field Angels", "complete"),
    ("mx-factor", "blind_search", "https://factor-capital.com/", "Factor Capital", "gap_justified"),
    ("mx-lightrock", "historical_delta", "https://www.lightrock.com/news/lightrock-expanding-global-presence-to-mexico/", "Lightrock expands to Mexico", "complete"),
]

CANDIDATES = [
    {
        "candidate_id": "fund-mx-femsa-ventures", "name": "FEMSA Ventures",
        "official_site": "https://www.femsaventures.com/", "aliases": [],
        "discovery_source_ids": ["mx-map-femsa", "mx-femsa-home"],
        "decision": "eligible", "destination": "funds/mexico/femsa-ventures.md",
        "reason": "Tese de CVC, portfólio recorrente, rota pública e investimento oficial em 2025.",
        "official_evidence_ids": ["ev-mx-femsa-home", "ev-mx-femsa-aloi"],
    },
    {
        "candidate_id": "fund-mx-zacua-ventures", "name": "Zacua Ventures",
        "official_site": "https://zacuaventures.com/", "aliases": [],
        "discovery_source_ids": ["mx-event-vcday", "mx-zacua"],
        "decision": "eligible", "destination": "funds/multi-country/zacua-ventures.md",
        "reason": "Fundo early-stage, portfólio direto, presença na Cidade do México e atividade oficial em 2026.",
        "official_evidence_ids": ["ev-mx-zacua-home", "ev-mx-zacua-scout"],
    },
    {
        "candidate_id": "fund-mx-alphaoak-capital", "name": "AlphaOak Capital",
        "official_site": "https://www.alphaoakcapital.com/", "aliases": [],
        "discovery_source_ids": ["mx-alphaoak"],
        "decision": "insufficient_evidence", "destination": None,
        "reason": "A página descreve fundo e alocação projetada, mas não comprova investimento concluído.",
        "official_evidence_ids": ["ev-mx-alphaoak"],
    },
    {
        "candidate_id": "fund-mx-mita-ventures", "name": "MITA Ventures",
        "official_site": "https://mitaventures.com/en/home/", "aliases": [],
        "discovery_source_ids": ["mx-mita"],
        "decision": "insufficient_evidence", "destination": None,
        "reason": "Tese e portfólio existem, mas a passagem não encontrou atividade oficial datada no recorte recente.",
        "official_evidence_ids": ["ev-mx-mita"],
    },
    {
        "candidate_id": "fund-mx-soldiers-field-angels", "name": "Soldiers Field Angels",
        "official_site": "https://www.soldiersfieldangels.com/", "aliases": ["SFA"],
        "discovery_source_ids": ["mx-soldiers"],
        "decision": "insufficient_evidence", "destination": None,
        "reason": "O site preserva dois fundos e portfólio, mas o último fechamento datado encontrado é de 2013.",
        "official_evidence_ids": ["ev-mx-soldiers"],
    },
    {
        "candidate_id": "fund-mx-factor-capital", "name": "Factor Capital",
        "official_site": "https://factor-capital.com/", "aliases": [],
        "discovery_source_ids": ["mx-factor"],
        "decision": "insufficient_evidence", "destination": None,
        "reason": "Páginas do mesmo domínio apresentam estágios, AUM e tickets materialmente contraditórios.",
        "official_evidence_ids": ["ev-mx-factor"],
    },
    {
        "candidate_id": "fund-mx-bridge-latam", "name": "Bridge Latam",
        "official_site": "https://bridgelat.com/", "aliases": ["Bridge"],
        "discovery_source_ids": ["mx-map-femsa"],
        "decision": "duplicate", "destination": "funds/regional/nazca.md",
        "reason": "A organização foi integrada à Nazca e não deve gerar perfil canônico separado.",
        "official_evidence_ids": ["ev-mx-bridge"],
    },
    {
        "candidate_id": "fund-mx-lightrock", "name": "Lightrock",
        "official_site": "https://www.lightrock.com/", "aliases": [],
        "discovery_source_ids": ["mx-lightrock"],
        "decision": "duplicate", "destination": "funds/multi-country/lightrock.md",
        "reason": "Perfil canônico publicado durante a reauditoria Brasil.",
        "official_evidence_ids": ["ev-mx-lightrock"],
    },
]

EVIDENCE = [
    ("ev-mx-femsa-home", "fund-mx-femsa-ventures", "https://www.femsaventures.com/", None,
     "Confirma CVC, investimento direto, portfólio, tese e rota pública para startups."),
    ("ev-mx-femsa-aloi", "fund-mx-femsa-ventures", "https://www.femsaventures.com/blogs/why-we-invested-aloi/914", "2025-11-24",
     "Confirma investimento direto e atividade em 2025."),
    ("ev-mx-zacua-home", "fund-mx-zacua-ventures", "https://zacuaventures.com/", None,
     "Confirma fundo early-stage, portfólio, presença na Cidade do México e envio de deck."),
    ("ev-mx-zacua-scout", "fund-mx-zacua-ventures", "https://zacuaventures.com/zacua-ventures-launches-scout-program/", "2026-02-03",
     "Confirma atividade e expansão da originação em 2026."),
    ("ev-mx-alphaoak", "fund-mx-alphaoak-capital", "https://www.alphaoakcapital.com/", "2025-05-12",
     "Confirma tese e construção projetada do portfólio, sem transação concluída identificada."),
    ("ev-mx-mita", "fund-mx-mita-ventures", "https://mitaventures.com/en/home/", None,
     "Confirma tese, cheques e empresas em destaque, sem atividade recente datada."),
    ("ev-mx-soldiers", "fund-mx-soldiers-field-angels", "https://www.soldiersfieldangels.com/", "2013-07-26",
     "Confirma fundo e portfólio, mas não atividade recente."),
    ("ev-mx-factor", "fund-mx-factor-capital", "https://factor-capital.com/", "2025-10-27",
     "Confirma página ativa, porém com afirmações incompatíveis em páginas do mesmo domínio."),
    ("ev-mx-bridge", "fund-mx-bridge-latam", "https://www.femsaventures.com/portfolio", None,
     "Identifica Bridge como fundo da Cidade do México; a consolidação com Nazca impede novo perfil."),
    ("ev-mx-lightrock", "fund-mx-lightrock", "https://www.lightrock.com/news/lightrock-expanding-global-presence-to-mexico/", "2026-02-20",
     "Confirma presença e investimentos no México; já existe perfil canônico."),
]

PROFILES = {
    "femsa-ventures": {
        "destination": "funds/mexico/femsa-ventures.md", "name": "FEMSA Ventures",
        "summary": {
            "en": "FEMSA Ventures is FEMSA's Mexico-based corporate venture capital arm, investing directly in startups that can scale through its Latin American businesses.",
            "es": "FEMSA Ventures es el brazo de capital de riesgo corporativo de FEMSA en México e invierte directamente en startups que pueden escalar mediante sus negocios latinoamericanos.",
            "pt-BR": "A FEMSA Ventures é o braço mexicano de corporate venture capital da FEMSA e investe diretamente em startups que podem escalar por meio de seus negócios latino-americanos.",
        },
        "base": {"kind": "country", "code": "MX"}, "countries": ["MX", "LATAM"],
        "stages": ["not_disclosed"], "focuses": ["retail", "beverages", "logistics"],
        "website": "https://www.femsaventures.com/", "route": "https://www.femsaventures.com/startupjourney",
        "sources": [
            {"title": "FEMSA Ventures", "url": "https://www.femsaventures.com/", "kind": "official_thesis"},
            {"title": "Why We Invested: Aloi", "url": "https://www.femsaventures.com/blogs/why-we-invested-aloi/914", "kind": "official_activity"},
        ],
        "signal": {"en": "On 2025-11-24, FEMSA Ventures published its investment rationale for Aloi. The dated transaction confirms current activity without implying a general stage.",
                   "es": "El 2025-11-24, FEMSA Ventures publicó su tesis de inversión en Aloi. La transacción fechada confirma actividad actual sin inferir una etapa general.",
                   "pt-BR": "Em 2025-11-24, a FEMSA Ventures publicou sua tese de investimento na Aloi. A transação datada confirma atividade atual sem inferir um estágio geral."},
    },
    "zacua-ventures": {
        "destination": "funds/multi-country/zacua-ventures.md", "name": "Zacua Ventures",
        "summary": {
            "en": "Zacua Ventures is a global early-stage construction technology fund with a Mexico City presence, direct portfolio and public deck-submission route.",
            "es": "Zacua Ventures es un fondo global de tecnología para la construcción en etapa temprana, con presencia en Ciudad de México, portafolio directo y canal público para enviar decks.",
            "pt-BR": "A Zacua Ventures é um fundo global early-stage de tecnologia para construção, com presença na Cidade do México, portfólio direto e canal público para envio de decks.",
        },
        "base": {"kind": "global", "code": "GLOBAL"}, "countries": ["GLOBAL", "MX"],
        "stages": ["not_disclosed"], "focuses": ["construction_technology", "built_environment"],
        "website": "https://zacuaventures.com/", "route": "https://zacuaventures.com/",
        "sources": [
            {"title": "Zacua Ventures", "url": "https://zacuaventures.com/", "kind": "official_portfolio"},
            {"title": "Zacua Ventures launches scout program", "url": "https://zacuaventures.com/zacua-ventures-launches-scout-program/", "kind": "official_activity"},
        ],
        "signal": {"en": "On 2026-02-03, Zacua announced a scout program and described an expanding investment scope. This is an activity signal, not a portfolio count.",
                   "es": "El 2026-02-03, Zacua anunció un programa de scouts y describió la expansión de su alcance de inversión. Es una señal de actividad, no un conteo del portafolio.",
                   "pt-BR": "Em 2026-02-03, a Zacua anunciou um programa de scouts e descreveu a expansão do seu escopo de investimento. É um sinal de atividade, não uma contagem do portfólio."},
    },
}


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def jsonl_bytes(values: list[dict[str, Any]]) -> bytes:
    return b"".join((json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n").encode() for v in values)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def profile_metadata(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    return json.loads(text[4:].split("\n---\n", 1)[0])


def metadata(slug: str, profile: dict[str, Any], locale: str) -> dict[str, Any]:
    canonical = f"fund:{slug}:en"
    return {
        "schema_version": "1.0", "id": f"fund:{slug}:{locale}", "entity_id": f"fund:{slug}",
        "slug": slug, "name": profile["name"], "entity_type": "fund", "locale": locale,
        "translation_of": None if locale == "en" else canonical,
        "translation_status": "canonical" if locale == "en" else "complete",
        "summary": profile["summary"][locale], "aliases": [], "operator": None,
        "base_geography": profile["base"], "countries_covered": profile["countries"],
        "stages": profile["stages"], "focuses": profile["focuses"],
        "official_website": profile["website"], "founder_route": profile["route"],
        "sources": profile["sources"], "last_verified": CUTOFF, "protected_terms": [profile["name"]],
    }


def markdown(slug: str, profile: dict[str, Any], locale: str) -> bytes:
    labels = {
        "en": ("Investment profile", "Website", "Fund type", "Stage at entry", "Focus", "Geography",
               "Submit a startup", "Declared thesis", "Portfolio signals", "Sources", "Last verified",
               "Venture capital", "Not publicly disclosed", "Reviewed official sources establish direct recurring investment and separate declared thesis from observed activity."),
        "es": ("Perfil de inversión", "Sitio web", "Tipo de fondo", "Etapa de entrada", "Enfoque", "Geografía",
               "Presentar una startup", "Tesis declarada", "Señales del portafolio", "Fuentes", "Última verificación",
               "Capital de riesgo", "No divulgado públicamente", "Las fuentes oficiales revisadas confirman inversión directa recurrente y separan la tesis declarada de la actividad observada."),
        "pt-BR": ("Perfil de investimento", "Site", "Tipo de fundo", "Estágio de entrada", "Foco", "Geografia",
                  "Enviar uma startup", "Tese declarada", "Sinais de portfólio", "Fontes", "Última verificação",
                  "Venture capital", "Não divulgado publicamente", "As fontes oficiais revisadas confirmam investimento direto recorrente e separam a tese declarada da atividade observada."),
    }[locale]
    extras = {
        "en": [("Direct startup investment", "Yes"), ("Open to external founders", "Yes"), ("Follow-on stages", "Not publicly disclosed"), ("Initial check", "Not publicly disclosed"), ("Investment role", "Not publicly disclosed"), ("Business models", "Not publicly disclosed"), ("Portfolio size", "Not publicly disclosed"), ("Selected companies", "Not publicly disclosed")],
        "es": [("Inversión directa en startups", "Sí"), ("Abierto a fundadores externos", "Sí"), ("Etapas de seguimiento", "No divulgado públicamente"), ("Cheque inicial", "No divulgado públicamente"), ("Rol de inversión", "No divulgado públicamente"), ("Modelos de negocio", "No divulgado públicamente"), ("Tamaño del portafolio", "No divulgado públicamente"), ("Empresas seleccionadas", "No divulgado públicamente")],
        "pt-BR": [("Investimento direto em startups", "Sim"), ("Aberto a founders externos", "Sim"), ("Estágios de follow-on", "Não divulgado publicamente"), ("Cheque inicial", "Não divulgado publicamente"), ("Papel no investimento", "Não divulgado publicamente"), ("Modelos de negócio", "Não divulgado publicamente"), ("Tamanho do portfólio", "Não divulgado publicamente"), ("Empresas selecionadas", "Não divulgado publicamente")],
    }[locale]
    extra_lines = "\n".join(f"- **{key}:** {value}" for key, value in extras)
    focus = ", ".join(profile["focuses"]).replace("_", " ")
    geo = ", ".join(profile["countries"])
    sources = "\n".join(f"- [{s['title']}]({s['url']})" for s in profile["sources"])
    front = json.dumps(metadata(slug, profile, locale), ensure_ascii=False, indent=2)
    text = f"""---
{front}
---
# {profile['name']}

{profile['summary'][locale]}

## {labels[0]}

- **{labels[1]}:** {profile['website']}
- **{labels[2]}:** {labels[11]}
{extra_lines}
- **{labels[3]}:** {labels[12]}
- **{labels[4]}:** {focus}
- **{labels[5]}:** {geo}
- **{labels[6]}:** [{profile['name']}]({profile['route']})

## {labels[7]}

{labels[13]}

## {labels[8]}

{profile['signal'][locale]}

## {labels[9]}

{sources}

**{labels[10]}:** {CUTOFF}
"""
    return text.encode("utf-8")


def outputs() -> dict[Path, bytes]:
    source_rows = [{
        "schema_version": "1.0", "source_id": sid, "source_family": family, "initial_url": url,
        "source": title, "research_channel": "non_regulatory", "is_regulatory": False,
        "discovery_allowed": True, "scope_walked": "México e acesso recorrente ao mercado mexicano",
        "accessed_on": CUTOFF, "result": result,
    } for sid, family, url, title, result in SOURCES]
    candidate_rows = [{
        "schema_version": "1.0", "cutoff_date": CUTOFF, "status": "decided",
        "discovered_on": CUTOFF, **candidate,
    } for candidate in CANDIDATES]
    evidence_rows = [{
        "schema_version": "1.0", "evidence_id": eid, "candidate_id": cid, "url": url,
        "published_on": published, "accessed_on": CUTOFF, "source_class": "official",
        "summary": summary,
    } for eid, cid, url, published, summary in EVIDENCE]
    baseline_paths = []
    publication_destinations = {profile["destination"] for profile in PROFILES.values()}
    for path in (ROOT / "funds").rglob("*.md"):
        record = profile_metadata(path)
        relative = path.relative_to(ROOT).as_posix()
        if (
            record
            and "MX" in record.get("countries_covered", [])
            and relative not in publication_destinations
        ):
            baseline_paths.append(relative)
    baseline_paths.sort()
    integrated = {
        "commit": "5b3a4e0",
        "status": "baseline_integrated",
        "profiles": ["funds/brazil/entrypoint.md", "funds/multi-country/flourish-ventures.md"],
        "treatment": "current_catalog_duplicates_and_deduplication_guards",
    }
    decisions: dict[str, int] = {}
    for candidate in CANDIDATES:
        decisions[candidate["decision"]] = decisions.get(candidate["decision"], 0) + 1
    eligible = [c for c in CANDIDATES if c["decision"] == "eligible"]
    excluded = [c for c in CANDIDATES if c["decision"] != "eligible"]
    exclusion_sample = sorted(
        excluded,
        key=lambda candidate: hashlib.sha256(candidate["candidate_id"].encode()).hexdigest(),
    )[:2]
    freeze = {
        "schema_version": "1.0", "epic": 249, "issue": 262, "market": "Mexico",
        "cutoff_date": CUTOFF, "status": "frozen", "candidate_count": len(CANDIDATES),
        "decision_counts": decisions, "regulatory_queries": 0,
        "publication": {"eligible_count": len(eligible), "batch_count": 1, "batch_size_limit": 10,
                        "candidates": [{"candidate_id": c["candidate_id"], "destination": c["destination"]} for c in eligible]},
        "review": {
            "eligible_reviewed": len(eligible),
            "routed_reviewed": 0,
            "regulatory_cases_reviewed": 0,
            "exclusion_population": len(excluded),
            "exclusion_sample_reviewed": len(exclusion_sample),
            "exclusion_sample_rule": "dois menores SHA-256 de candidate_id entre os seis não elegíveis",
            "exclusion_sample_ids": [candidate["candidate_id"] for candidate in exclusion_sample],
        },
        "limitations": ["Cobertura auditada nas fontes registradas; não representa totalidade do mercado mexicano."],
    }
    audit = {
        "schema_version": "1.0", "epic": 249, "issues": [259, 260, 261, 262, 263],
        "market": "Mexico", "cutoff_date": CUTOFF, "status": "pass",
        "baseline": {"profile_count": len(baseline_paths), "profiles": baseline_paths, "integrated_change": integrated},
        "sources": {"planned": len(SOURCES), "complete": sum(s[4] == "complete" for s in SOURCES),
                    "gap_justified": sum(s[4] == "gap_justified" for s in SOURCES),
                    "discovery_non_regulatory_share": 1.0},
        "candidates": {"rows": len(CANDIDATES), "decision_counts": decisions},
        "review": {"eligible_reviewed": len(eligible), "eligible_coverage": 1.0,
                   "routed_reviewed": 0, "routed_population": 0,
                   "regulatory_cases_reviewed": 0, "regulatory_case_population": 0,
                   "exclusion_population": len(excluded),
                   "exclusion_sample_reviewed": len(exclusion_sample),
                   "exclusion_sample_rate": len(exclusion_sample) / len(excluded),
                   "exclusion_sample_rule": "dois menores SHA-256 de candidate_id entre os seis não elegíveis",
                   "exclusion_sample_ids": [candidate["candidate_id"] for candidate in exclusion_sample],
                   "blind_new_candidates": 3,
                   "blind_new_eligible": 0, "critical_open": 0, "high_open": 0,
                   "saturation": "low_marginal_yield"},
        "regulatory": {"queries": 0, "candidate_rate": 0.0, "eligibility_use": False},
        "publication": {"batch_count": 1, "candidate_count": len(eligible), "profile_file_count": len(eligible) * 3},
        "routes": {}, "language": "cobertura auditada",
        "limitations": freeze["limitations"],
    }
    readme = f"""# Reauditoria de fundos — México

Data de corte: `{CUTOFF}`.

Esta execução registra **cobertura auditada**, sem afirmar totalidade do mercado mexicano.

- {len(SOURCES)} fontes não regulatórias: {audit['sources']['complete']} completas e {audit['sources']['gap_justified']} `gap_justified`;
- {len(CANDIDATES)} candidatos: {decisions.get('eligible', 0)} elegíveis, {decisions.get('duplicate', 0)} duplicatas e {decisions.get('insufficient_evidence', 0)} insuficientes;
- zero consultas regulatórias;
- 100% dos elegíveis revisados; rotas e casos regulatórios têm população zero;
- amostra determinística de {len(exclusion_sample)}/{len(excluded)} não elegíveis, pelos dois menores SHA-256 de `candidate_id`;
- busca cega adicionou três exclusões e nenhuma elegibilidade;
- um lote congelado, com {len(eligible)} fundos e {len(eligible) * 3} perfis localizados.

O commit `5b3a4e0` já integra Entrypoint e Flourish Ventures ao baseline publicado. Ambos foram tratados como duplicatas correntes e guardas de deduplicação; nenhum foi replicado.
"""
    out = {
        HERE / "source-inventory.jsonl": jsonl_bytes(source_rows),
        HERE / "candidates.jsonl": jsonl_bytes(candidate_rows),
        HERE / "evidence.jsonl": jsonl_bytes(evidence_rows),
        HERE / "freeze-manifest.json": json_bytes(freeze),
        HERE / "audit-report.json": json_bytes(audit),
        HERE / "README.md": readme.encode("utf-8"),
    }
    for slug, profile in PROFILES.items():
        for locale in ("en", "es", "pt-BR"):
            path = ROOT / profile["destination"]
            if locale != "en":
                path = ROOT / "translations" / locale / profile["destination"]
            out[path] = markdown(slug, profile, locale)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()
    if args.check:
        mismatches = [p for p, data in expected.items() if not p.is_file() or p.read_bytes() != data]
        if mismatches:
            raise SystemExit("Artefatos divergentes: " + ", ".join(str(p.relative_to(ROOT)) for p in mismatches))
        print(f"Mexico re-audit verified: {len(expected)} artifacts.")
        return 0
    for path, data in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f"Mexico re-audit generated: {len(expected)} artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
