#!/usr/bin/env python3
"""Build the Bolivia, Paraguay and Venezuela audit up to the review gate."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


contract = {
    "schema_version": "1.0",
    "markets": ["BO", "PY", "VE"],
    "cutoff": CUTOFF,
    "gates": [
        "direct_investment",
        "recurrence",
        "recent_activity",
        "market_access",
        "official_evidence",
    ],
    "discovery": "non_regulatory_only",
    "regulator": "identity_or_divergence_only",
    "regulator_target_percent": [5, 10],
    "forbidden_inputs": [
        "local_startup_dataset",
        "catalog_as_discovery",
        "regulator_as_discovery",
    ],
    "review_gate": "independent_integrator_review_required_before_freeze",
    "publication_batch_limit": 10,
    "locales": ["en", "pt-BR", "es"],
    "coverage_claim": "audited_coverage",
}

source_specs = [
    ("bocap-current", "industry_association", "https://www.bocap.vc/", "BO", "Current founding roster and ecosystem classification", 4),
    ("idb-bolivia-2026", "sector_diagnostic", "https://publications.iadb.org/publications/spanish/document/Diagnostico-del-ecosistema-de-emprendimiento-innovador-e-inversion-en-etapas-tempranas-en-Bolivia-.pdf", "BO", "Independent current diagnostic and local-fund count", 2),
    ("vcilat-2025", "sector_event", "https://www.vcilat.com/wp-content/uploads/2025/07/AGENDA-VCILAT-OK-U.pdf", "BO", "Event pass for active managers and foreign access", 2),
    ("yango-bolivia-2025", "fund_news", "https://www.economy.com.bo/articulo/business/yango-ventures-aterriza-bolivia-fondo-us-20-millones-impulsar-startups/20250408150455017851.html", "BO", "Bolivia launch and explicit local access", 1),
    ("yango-official", "official_fund", "https://ventures.yango.com/", "BO", "Current thesis, stages, sectors and founder route", 1),
    ("yango-launch", "official_fund_launch", "https://yango.com/en_int/news/yango-group-launches-corporate-venture-fund-to-support-young-entrepreneurs", "BO", "Fund size, recurrence design and LATAM scope", 1),
    ("bdp-startup", "public_program", "https://www.bdp.com.bo/fondo-startup/", "BO", "Current public startup-risk-capital program", 1),
    ("aceleratec", "accelerator", "https://aceleratec.org/", "BO", "Current acceleration model and linked Escalatec capital", 1),
    ("parcapy-current", "industry_association", "https://parcapy.org/", "PY", "Current founders, members and affiliates", 10),
    ("parcapy-report-2026", "sector_report", "https://parcapy.org/wp-content/uploads/2026/04/Informe-parcapy_diseno_actualizado_Final.pdf", "PY", "2023–2025 investment flows and fund-origin distribution", 4),
    ("urucap-cibersons", "regional_directory", "https://urucap.org/wp-content/uploads/2024/09/Directorio-de-Socios-Agosto23-Agosto24.pdf", "PY", "Cibersons headquarters, thesis, check and portfolio", 1),
    ("lavca-cibersons", "regional_investor_profile", "https://www.lavca.org/people/vivianne-bernardes-cibils/", "PY", "Current Asunción base and investor classification", 1),
    ("mic-cibersons", "government_ecosystem_directory", "https://portalemprendedor.mic.gov.py/institucion.php?id=10", "PY", "Paraguayan operating identity and direct fund activity", 1),
    ("cibersons-official", "official_portfolio", "https://ccibils7.wixsite.com/cibersons/ventures", "PY", "Official fund and startup portfolio", 1),
    ("idb-lan-2025", "institutional_program", "https://www.iadb.org/es/proyecto/PR-T1375", "PY", "LAN accelerator and financing-program identity", 1),
    ("mitic-innovandopy-2025", "public_program", "https://mitic.gov.py/innovandopy-adjudica-un-total-usd-140-000-en-capital-semilla-para-siete-startups-paraguayas/", "PY", "Current public seed-capital awards", 1),
    ("tecnomyl-h2o", "corporate_innovation", "https://www.tecnomyl.com.py/lanzamiento-h20-innovation/", "PY", "H2O corporate innovation-hub model", 1),
    ("venecapital-map", "ecosystem_map", "https://venecapital.org/", "VE", "Current Venezuelan ecosystem and market-map pass", 5),
    ("venezuela-tech-week", "sector_event", "https://venezuelatechweek.org/", "VE", "Blind event pass using a different vocabulary", 2),
    ("impulsa-official", "official_investment_firm", "https://www.impulsa.vc/", "VE", "Current direct startup investment and founder route", 1),
    ("impulsa-duwu-2026", "investment_announcement", "https://es.linkedin.com/posts/impulsa-vc_venturecapital-inversion-impulsavc-activity-7408157066474987521-Fpqq", "VE", "Recent direct portfolio addition", 1),
    ("epakon-official", "official_fund", "https://epakon.com/", "VE", "Current checks, stages, LATAM scope, portfolio and pitch route", 1),
    ("plus58-official", "official_launch", "https://plus58ventures.com/", "VE", "Venezuela thesis and early-access launch state", 1),
    ("avila-official", "official_fund", "https://www.avila.vc/", "VE", "Current thesis and portfolio without explicit Venezuela access", 1),
    ("sunaval-impulsa", "regulator_identity", "http://www.sunaval.gob.ve/", "VE", "Minimal legal-identity divergence check for Impulsa only", 0),
]

sources = [
    {
        "schema_version": "1.0",
        "source_id": source_id,
        "family": family,
        "url": url,
        "market": market,
        "scope": scope,
        "accessed_on": CUTOFF,
        "status": "complete" if source_id != "sunaval-impulsa" else "gap_justified",
        "result": "reviewed",
        "candidate_yield": candidate_yield,
        "owner": f"worker-{market.lower()}",
    }
    for source_id, family, url, market, scope, candidate_yield in source_specs
]

candidate_specs = [
    ("bo-babasu", "Babasú Ventures", "babasuventures.com", ["BO", "PY"], ["bocap-current", "idb-bolivia-2026"], "duplicate", "funds/regional/babasu-ventures.md", "Current Bolivia-based manager already has one canonical profile."),
    ("bo-escalatec", "Escalatec", "escalatec.vc", ["BO"], ["bocap-current", "idb-bolivia-2026", "vcilat-2025"], "duplicate", "funds/bolivia/escalatec.md", "Current Bolivia-based fund already has one canonical profile."),
    ("py-ithink", "iThink VC", "ithink.vc", ["BO", "PY"], ["bocap-current", "parcapy-current"], "duplicate", "funds/regional/ithink-vc.md", "Current Paraguay-based manager already has one canonical profile."),
    ("py-cibersons", "Cibersons", "cibersons.com", ["BO", "PY"], ["bocap-current", "parcapy-current", "urucap-cibersons", "lavca-cibersons", "mic-cibersons", "cibersons-official"], "eligible", "funds/regional/cibersons.md", "Direct recurring early-stage investor with an official portfolio; LAVCA, MIC and URUCAP explicitly locate the manager in Asunción, Paraguay."),
    ("bo-yango-ventures", "Yango Ventures", "ventures.yango.com", ["BO"], ["yango-bolivia-2025", "yango-official", "yango-launch"], "eligible", "funds/multi-country/yango-ventures.md", "Dubai-based corporate venture fund with a current USD 20M vehicle, active thesis, founder route and explicit Bolivia launch."),
    ("bo-bdp-startup", "BDP Fondo Startup", "bdp.com.bo", ["BO"], ["bdp-startup"], "routed", "public_program", "Government-created and BDP-administered public risk-capital program, not a private VC manager."),
    ("bo-aceleratec", "Aceleratec", "aceleratec.org", ["BO"], ["aceleratec"], "routed", "accelerator", "Three-month accelerator; its USD 20K capital is supplied by the separately cataloged Escalatec."),
    ("bo-bocap", "BOCAP", "bocap.vc", ["BO"], ["bocap-current"], "routed", "industry_association", "Association and ecosystem map that expressly does not administer capital."),
    ("py-parcapy", "PARCAPY", "parcapy.org", ["PY"], ["parcapy-current", "parcapy-report-2026"], "routed", "industry_association", "Industry association and research publisher rather than an investing vehicle."),
    ("py-fiip", "Fondo de Inversión en Innovación de Paraguay (FIIP)", None, ["PY"], ["parcapy-current"], "insufficient_evidence", None, "Current roster confirms the name, but no current official thesis, deployment, portfolio or founder route was found."),
    ("py-riiap", "RIIAP", None, ["PY"], ["parcapy-current"], "routed", "angel_network", "PARCAPY identifies the Paraguayan angel-investor network, which belongs in the angel track."),
    ("py-lan", "LAN Accelerator", "lan.ventures", ["PY"], ["parcapy-current", "idb-lan-2025"], "routed", "accelerator", "Current accelerator and grant-backed financing program; no separate recurring VC fund was established."),
    ("py-h2o", "H2O Innovation", "tecnomyl.com.py", ["PY"], ["parcapy-current", "tecnomyl-h2o"], "routed", "corporate_innovation_hub", "Corporate innovation hub and open-innovation program, not a recurring external fund."),
    ("py-zeal", "Zeal Fund", None, ["PY"], ["parcapy-current"], "insufficient_evidence", None, "Current member label is ambiguous and no authoritative identity, Paraguay mandate or portfolio was resolved."),
    ("py-innovandopy", "InnovandoPY", "mitic.gov.py", ["PY"], ["mitic-innovandopy-2025"], "routed", "public_program", "Government incubation and non-recurring public seed-capital awards."),
    ("ve-venecapital", "Venecápital", "venecapital.org", ["VE"], ["venecapital-map"], "routed", "industry_association", "Private-capital association and ecosystem-map publisher, not a direct investment vehicle."),
    ("ve-impulsa", "Impulsa VC", "impulsa.vc", ["VE"], ["venecapital-map", "impulsa-official", "impulsa-duwu-2026"], "eligible", "funds/venezuela/impulsa-vc.md", "Caracas investment company with direct startup deployment, a current portfolio addition and an external contact route."),
    ("ve-plus58", "+58 Ventures", "plus58ventures.com", ["VE"], ["venecapital-map", "plus58-official"], "insufficient_evidence", None, "Official launch page states a direct Venezuela thesis but not yet a verifiable portfolio, recurring deployment or completed fund activity."),
    ("ve-epakon", "Epakon Capital", "epakon.com", ["VE"], ["venecapital-map", "epakon-official"], "eligible", "funds/multi-country/epakon-capital.md", "US-based early-stage fund with explicit LatAm access, a pitch route, 40+ companies and current Venezuelan portfolio activity."),
    ("ve-avila", "Avila VC", "avila.vc", ["VE"], ["venezuela-tech-week", "avila-official"], "insufficient_evidence", None, "Official fund and portfolio are current, but the Caracas name reference does not establish an explicit Venezuela investment mandate or founder access."),
]

candidates = [
    {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "name": name,
        "canonical_domain": domain,
        "markets": markets,
        "discovery_origin": "handoff_audited_non_regulatory" if candidate_id == "py-cibersons" else "non_regulatory",
        "discovery_source_ids": source_ids,
        "cutoff": CUTOFF,
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "status": "terminal",
    }
    for candidate_id, name, domain, markets, source_ids, decision, destination, reason in candidate_specs
]

evidence = [
    {
        "schema_version": "1.0",
        "evidence_id": f"ev-{row['candidate_id']}",
        "candidate_id": row["candidate_id"],
        "source_ids": row["discovery_source_ids"],
        "accessed_on": CUTOFF,
        "claims": {
            "identity": "resolved" if row["canonical_domain"] else "partial",
            "direct_investment": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_sufficient_for_funds",
            "recent_activity": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_required_or_unconfirmed",
            "market_access": "explicit" if row["decision"] in {"eligible", "duplicate"} else "not_eligible",
            "official_evidence": "confirmed" if row["decision"] == "eligible" else "reviewed",
        },
        "finding": row["reason"],
    }
    for row in candidates
]

regulator_log = [{
    "schema_version": "1.0",
    "query_id": "reg-ve-impulsa-identity",
    "candidate_id": "ve-impulsa",
    "regulator": "SUNAVAL",
    "url": "http://www.sunaval.gob.ve/",
    "question": "Is the current legal issuer identity Impulsa Venture Capital, C.A.?",
    "accessed_on": CUTOFF,
    "result": "No stable public issuer lookup was accessible; the query was not used for discovery or eligibility. Current official company disclosures retain the legal name and RIF.",
    "effect": "identity_note_only",
}]

profile_paths = sorted(
    list((ROOT / "funds").glob("**/*.md")),
    key=lambda path: path.as_posix().casefold(),
)
baseline_rows = []
for path in profile_paths:
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"\A---\s*(\{.*?\})\s*---", raw, re.DOTALL)
    metadata = json.loads(match.group(1)) if match else {}
    baseline_rows.append({
        "schema_version": "1.0",
        "entity_id": metadata.get("entity_id"),
        "name": metadata.get("name"),
        "profile_path": path.relative_to(ROOT).as_posix(),
        "official_website": metadata.get("official_website"),
        "profile_sha256": digest(path),
    })

historical_path = ROOT / "research" / "epic-16" / "issue-26" / "candidates.jsonl"
historical_rows = [
    json.loads(line)
    for line in historical_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
historical_subset = [
    row for row in historical_rows
    if row.get("base_country") in {"Bolívia", "Paraguai", "Venezuela", "Estados Unidos"}
    or any(country in {"Bolívia", "Paraguai", "Venezuela"} for country in row.get("declared_geography", []))
]

write_json(OUT / "contract.json", contract)
write_jsonl(OUT / "source-inventory.jsonl", sources)
write_jsonl(OUT / "candidates.jsonl", candidates)
write_jsonl(OUT / "evidence.jsonl", evidence)
write_jsonl(OUT / "regulator-query-log.jsonl", regulator_log)
write_jsonl(OUT / "baseline" / "catalog-baseline.jsonl", baseline_rows)
write_jsonl(OUT / "baseline" / "prior-candidates.jsonl", historical_subset)
write_json(OUT / "baseline" / "summary.json", {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "catalog_profile_count": len(baseline_rows),
    "historical_candidate_count": len(historical_subset),
    "catalog_sha256": digest(OUT / "baseline" / "catalog-baseline.jsonl"),
    "historical_sha256": digest(OUT / "baseline" / "prior-candidates.jsonl"),
})

family_order = [
    "industry_association",
    "sector_diagnostic",
    "sector_event",
    "fund_news",
    "official_fund",
    "public_program",
    "regional_directory",
    "ecosystem_map",
    "investment_announcement",
]
yield_curve = []
seen = set()
for family in family_order:
    new_ids = {
        candidate["candidate_id"]
        for candidate in candidates
        if any(
            source_id in candidate["discovery_source_ids"]
            for source_id in [source["source_id"] for source in sources if source["family"] == family]
        )
    } - seen
    seen.update(new_ids)
    yield_curve.append({"family": family, "marginal_candidates": len(new_ids), "cumulative_candidates": len(seen)})

counts = {
    decision: sum(candidate["decision"] == decision for candidate in candidates)
    for decision in ["eligible", "duplicate", "routed", "insufficient_evidence"]
}
write_json(OUT / "coverage-matrix.json", {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "markets": {
        market: {
            "candidate_count": sum(market in row["markets"] for row in candidates),
            "eligible_count": sum(market in row["markets"] and row["decision"] == "eligible" for row in candidates),
            "source_count": sum(source["market"] == market for source in sources),
        }
        for market in ["BO", "PY", "VE"]
    },
    "yield_curve": yield_curve,
    "saturation_passes": [
        {"pass": "sector_events_and_reports", "new_candidates": 2},
        {"pass": "alternate_vocabulary_blind_search", "new_candidates": 1},
        {"pass": "official_portfolio_reconciliation", "new_candidates": 0},
    ],
    "candidate_counts": counts,
    "regulatory_query_count": len(regulator_log),
    "regulatory_case_percent": round(100 * len(regulator_log) / len(candidates), 2),
    "non_regulatory_discovery_percent": 100.0,
})

write_json(OUT / "review-request.json", {
    "schema_version": "1.0",
    "status": "pending_independent_review",
    "requested_on": CUTOFF,
    "freeze_allowed": False,
    "candidate_count": len(candidates),
    "eligible_to_review": [row["candidate_id"] for row in candidates if row["decision"] == "eligible"],
    "routed_to_review": [row["candidate_id"] for row in candidates if row["decision"] == "routed"],
    "regulatory_cases_to_review": ["ve-impulsa"],
    "deterministic_exclusion_sample": ["py-fiip", "ve-plus58"],
    "blind_findings_to_review": ["bo-yango-ventures", "ve-plus58", "ve-avila"],
    "base_geography_checks": {
        "py-cibersons": {
            "proposed_base": "PY",
            "not_inferred_from": ["founder nationality", "BOCAP membership", "Uruguay handoff"],
            "supporting_sources": ["lavca-cibersons", "mic-cibersons", "urucap-cibersons"],
        }
    },
    "proposed_freeze": {
        "eligible": [row["candidate_id"] for row in candidates if row["decision"] == "eligible"],
        "publication_batch_count": 1,
        "publication_batch_limit": 10,
    },
})

write_json(OUT / "prefreeze-manifest.json", {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "status": "awaiting_independent_review",
    "freeze_allowed": False,
    "counts": {"candidates": len(candidates), **counts, "regulatory_queries": len(regulator_log)},
    "artifact_hashes": {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in sorted(OUT.glob("*.json*"))
        if path.name != "prefreeze-manifest.json"
    },
    "limitations": [
        "Audited coverage of enumerated public sources, not absolute market completeness.",
        "Sparse public evidence remains a material limitation in all three markets.",
        "The single regulator query concerns identity only and does not support discovery or eligibility.",
    ],
})

print(json.dumps({
    "candidates": len(candidates),
    "eligible": counts["eligible"],
    "regulatory_queries": len(regulator_log),
    "regulatory_percent": round(100 * len(regulator_log) / len(candidates), 2),
    "status": "awaiting_independent_review",
}, ensure_ascii=False))
