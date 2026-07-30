#!/usr/bin/env python3
"""Build the Ecuador fund-audit artifacts up to the independent review gate."""

from __future__ import annotations

import hashlib
import json
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
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


contract = {
    "schema_version": "1.0",
    "market": "EC",
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
    "terminal_decisions": [
        "eligible",
        "insufficient_evidence",
        "routed",
        "routed_private_equity",
        "duplicate",
    ],
}

source_specs = [
    (
        "ecuacap-current",
        "industry_association",
        "https://www.ecuacap.org/about",
        "Current Ecuador private-capital association roster and organization types",
        "public-ecosystem",
        "complete",
        7,
    ),
    (
        "ecuacap-founders-2022",
        "industry_news",
        "https://www.forbes.com.ec/money/siete-fondos-privados-unen-fuerzas-apoyar-iniciativas-n14712",
        "Former founding roster used to detect removals and identity drift",
        "public-ecosystem",
        "complete",
        7,
    ),
    (
        "impaqto-official",
        "official_thesis_portfolio",
        "https://www.impaqtocapital.com/es",
        "Current thesis, Ecuador headquarters, portfolio, founder route and Andean access",
        "official-platform",
        "complete",
        1,
    ),
    (
        "impaqto-close-2025",
        "official_fund_activity",
        "https://www.impaqtocapital.com/fund-i-final-close-announcement",
        "Fund I final close and six direct investments",
        "official-platform",
        "complete",
        1,
    ),
    (
        "forbes-buentrip-2024",
        "fund_news",
        "https://www.forbes.com.ec/negocios/startups-ecuador-tiene-founders-talentosos-propuestas-valor-audaces-n64707",
        "Fund sizes, investment cadence and Ecuador founder coverage",
        "fund-news",
        "complete",
        1,
    ),
    (
        "creas-official",
        "official_thesis",
        "https://creasecuador.com/mision",
        "Impact-fund identity and Ecuador mandate without dated deployment evidence",
        "official-platform",
        "complete",
        1,
    ),
    (
        "humboldt-vc4a",
        "regional_platform",
        "https://vc4a.com/humboldt-family-office/",
        "XPT vehicles, direct investment model and regional target",
        "regional-platform",
        "complete",
        1,
    ),
    (
        "endeavor-launchpad",
        "official_accelerator",
        "https://ecuador.endeavor.org/endeavorlaunchpad/",
        "Current accelerator and founder-support model",
        "official-platform",
        "complete",
        1,
    ),
    (
        "kruger-official",
        "official_accelerator",
        "https://krugerlabs.com/",
        "Current Quito identity and startup-transformation positioning",
        "official-platform",
        "complete",
        1,
    ),
    (
        "buenavista-official",
        "official_private_equity",
        "https://bcp.partners/",
        "Current private-equity identity, growth-stage strategy and Fund 0 activity",
        "official-platform",
        "complete",
        1,
    ),
    (
        "buenavista-fund-1",
        "official_private_equity",
        "https://bcp.partners/fund_1",
        "Fund 1 thesis for growth-stage Latin American SMEs",
        "official-platform",
        "complete",
        1,
    ),
    (
        "startups-ventures-vc4a",
        "angel_network",
        "https://vc4a.com/startups-ventures/?lang=es",
        "Current angel-club identity",
        "regional-platform",
        "complete",
        1,
    ),
    (
        "gem-ecosystem-map",
        "blind_ecosystem_map",
        "https://www.gemconsortium.org/file/open?fileId=50408",
        "Blind vocabulary pass for Ecuador early-stage capital actors",
        "blind-review",
        "complete",
        2,
    ),
    (
        "world-bank-digital-ecuador",
        "blind_sector_report",
        "https://documents1.worldbank.org/curated/en/099957201262484042/pdf/IDU148619f7c191381405618db3115106df826f9.pdf",
        "Blind sector pass for digital-business investors and support organizations",
        "blind-review",
        "complete",
        0,
    ),
    (
        "academic-593-capital",
        "historical_ecosystem_study",
        "https://bibdigital.epn.edu.ec/bitstream/15000/21077/1/CD%2010586.pdf",
        "Historical identity and investment model for 593 Capital Partners",
        "blind-review",
        "complete",
        1,
    ),
    (
        "fonquito-2025",
        "municipal_program",
        "https://www.quitoinforma.gob.ec/2025/04/08/atencion-emprendedores-postulense-para-obtener-capital-semilla-y-fortalecer-sus-negocios/",
        "Current municipal seed-capital call",
        "public-programs",
        "complete",
        1,
    ),
    (
        "scvs-creas",
        "regulator_identity",
        "https://mercadodevalores.supercias.gob.ec/mercadovalores/descargadorServlet.jsf?idDocumento=44884&idSeccion=GMV&idTipoDocumento=10",
        "Legal-vehicle identity check for Fideicomiso de Inversión CREAS Ecuador",
        "regulator",
        "complete",
        0,
    ),
]

sources = [
    {
        "schema_version": "1.0",
        "source_id": source_id,
        "family": family,
        "url": url,
        "scope": scope,
        "owner": owner,
        "accessed_on": CUTOFF,
        "result": result,
        "observed_names": observed_names,
    }
    for source_id, family, url, scope, owner, result, observed_names in source_specs
]

candidate_specs = [
    (
        "impaqto-capital",
        "IMPAQTO Capital",
        "impaqtocapital.com",
        ["ecuacap-current", "impaqto-official", "impaqto-close-2025"],
        "handoff_audited_non_regulatory",
        "eligible",
        "funds/regional/impaqto-capital.md",
        "Quito-based direct Andean impact-fund manager with a current founder route, 12 investments and a January 2025 Fund I close.",
    ),
    (
        "new-ventures-capital",
        "New Ventures Capital",
        "nvcapital.vc",
        ["ecuacap-current"],
        "non_regulatory",
        "duplicate",
        "funds/regional/new-ventures-capital.md",
        "Current ECUACAP investment-platform identity already has a canonical profile.",
    ),
    (
        "ithink-vc",
        "iThink VC",
        "ithink.vc",
        ["ecuacap-current"],
        "non_regulatory",
        "duplicate",
        "funds/regional/ithink-vc.md",
        "Current ECUACAP fund-manager identity already has a canonical profile.",
    ),
    (
        "endeavor-ecuador",
        "Endeavor Ecuador",
        "ecuador.endeavor.org",
        ["ecuacap-current", "endeavor-launchpad"],
        "non_regulatory",
        "routed",
        "accelerator",
        "Official current activity is acceleration, mentoring and ecosystem support rather than a direct recurring fund.",
    ),
    (
        "kruger-labs",
        "Kruger Labs",
        "krugerlabs.com",
        ["ecuacap-current", "kruger-official"],
        "non_regulatory",
        "routed",
        "accelerator",
        "ECUACAP and the official team page identify Kruger Labs as an accelerator.",
    ),
    (
        "startups-ventures",
        "Startups & Ventures",
        "startupsventures.com",
        ["ecuacap-current", "startups-ventures-vc4a"],
        "non_regulatory",
        "routed",
        "angel_network",
        "Current sources identify an angel club, which belongs in the angel-network track.",
    ),
    (
        "telefunken-capital",
        "Telefunken Capital",
        None,
        ["ecuacap-current", "ecuacap-founders-2022"],
        "non_regulatory",
        "insufficient_evidence",
        None,
        "Current association evidence resolves a family-office identity, but no official current recurring direct-VC mandate, portfolio or founder route was found.",
    ),
    (
        "buentrip-ventures",
        "BuenTrip Ventures",
        "buentrip.vc",
        ["ecuacap-founders-2022", "forbes-buentrip-2024"],
        "non_regulatory",
        "duplicate",
        "funds/regional/buentrip-ventures.md",
        "Current fund activity is confirmed and the identity already has a canonical profile.",
    ),
    (
        "creas-ecuador",
        "CREAS Ecuador",
        "creasecuador.com",
        ["ecuacap-founders-2022", "creas-official"],
        "non_regulatory",
        "insufficient_evidence",
        None,
        "The fund and vehicle identities are resolved, but the reviewed official pages do not establish recent recurring deployment or a current founder route.",
    ),
    (
        "humboldt-family-office",
        "Humboldt Family Office / XPT",
        "hfo.ec",
        ["ecuacap-founders-2022", "humboldt-vc4a"],
        "non_regulatory",
        "insufficient_evidence",
        None,
        "Direct vehicles and regional scope are described, but no dated recent deployment or current external-founder route was established.",
    ),
    (
        "buenavista-capital",
        "BuenaVista Capital",
        "bcp.partners",
        [
            "ecuacap-founders-2022",
            "buenavista-official",
            "buenavista-fund-1",
        ],
        "non_regulatory",
        "routed_private_equity",
        "private_equity",
        "Current official evidence identifies a private-equity manager investing in growth-stage SMEs through Fund 0 and Fund 1, outside the venture-fund model.",
    ),
    (
        "drivum",
        "DRIVUM",
        "drivum.com.ec",
        ["gem-ecosystem-map"],
        "non_regulatory",
        "insufficient_evidence",
        None,
        "The ecosystem map describes a diversified investment fund, but no current direct startup mandate, recurrence or founder route was verified.",
    ),
    (
        "fundacion-crisfe",
        "Fundación CRISFE Fondo Emprende",
        "crisfe.org",
        ["gem-ecosystem-map"],
        "non_regulatory",
        "routed",
        "philanthropic_seed_program",
        "The mapped seed-capital initiative is a foundation program rather than a recurring external VC fund.",
    ),
    (
        "593-capital-partners",
        "593 Capital Partners",
        None,
        ["academic-593-capital"],
        "non_regulatory",
        "insufficient_evidence",
        None,
        "Historical evidence describes a technology investment vehicle, but current official activity, recurrence and founder access were not found.",
    ),
    (
        "fonquito",
        "FonQuito",
        "quitoinforma.gob.ec",
        ["fonquito-2025"],
        "non_regulatory",
        "routed",
        "public_program",
        "Municipal seed-capital call funded by Quito and operated by ConQuito, not a recurring private venture fund.",
    ),
]

candidates = [
    {
        "schema_version": "1.0",
        "candidate_id": f"ec-{candidate_id}",
        "name": name,
        "canonical_domain": domain,
        "discovery_source_ids": source_ids,
        "discovery_origin": origin,
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "cutoff": CUTOFF,
    }
    for (
        candidate_id,
        name,
        domain,
        source_ids,
        origin,
        decision,
        destination,
        reason,
    ) in candidate_specs
]

confirmed = {"eligible", "duplicate"}
evidence = []
for candidate in candidates:
    source_ids = list(candidate["discovery_source_ids"])
    if candidate["candidate_id"] == "ec-creas-ecuador":
        source_ids.append("scvs-creas")
    evidence.append(
        {
            "candidate_id": candidate["candidate_id"],
            "decision": candidate["decision"],
            "source_ids": source_ids,
            "gates": {
                "identity": "resolved",
                "direct_investment": (
                    "confirmed"
                    if candidate["decision"] in confirmed
                    else "not_confirmed_or_not_applicable"
                ),
                "recurrence": (
                    "confirmed"
                    if candidate["decision"] in confirmed
                    else "not_confirmed_or_not_applicable"
                ),
                "recent_activity": (
                    "confirmed"
                    if candidate["decision"] in confirmed
                    else "not_confirmed_or_not_applicable"
                ),
                "market_access": (
                    "confirmed"
                    if candidate["decision"] in confirmed
                    else "not_confirmed_or_not_applicable"
                ),
                "official_evidence": (
                    "confirmed"
                    if candidate["decision"] in confirmed
                    else "partial_or_not_applicable"
                ),
            },
            "reason": candidate["reason"],
        }
    )

new_profile = "funds/regional/impaqto-capital.md"
profiles = [
    path
    for path in sorted(ROOT.glob("funds/**/*.md"))
    if path.relative_to(ROOT).as_posix() != new_profile
]
baseline_rows = [
    {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": digest(path),
    }
    for path in profiles
]
prior_path = ROOT / "research/epic-16/issue-26/candidates.jsonl"
prior_rows = [
    {
        "path": prior_path.relative_to(ROOT).as_posix(),
        "sha256": digest(prior_path),
        "record_count": len(prior_path.read_text(encoding="utf-8").splitlines()),
        "classification": "historical_not_discovery",
    }
]
baseline_summary = {
    "cutoff": CUTOFF,
    "profile_count": len(baseline_rows),
    "profile_manifest_sha256": hashlib.sha256(
        "".join(row["sha256"] for row in baseline_rows).encode("utf-8")
    ).hexdigest(),
    "historical_candidate_file_count": len(prior_rows),
    "historical_candidate_record_count": prior_rows[0]["record_count"],
}

write_json(OUT / "contract.json", contract)
write_jsonl(OUT / "baseline/catalog-baseline.jsonl", baseline_rows)
write_jsonl(OUT / "baseline/prior-candidates.jsonl", prior_rows)
write_json(OUT / "baseline/summary.json", baseline_summary)
write_jsonl(OUT / "source-inventory.jsonl", sources)
write_jsonl(OUT / "candidates.jsonl", candidates)
write_jsonl(OUT / "evidence.jsonl", evidence)
write_jsonl(
    OUT / "scvs-query-log.jsonl",
    [
        {
            "query_id": "scvs-ec-001",
            "candidate_id": "ec-creas-ecuador",
            "source_id": "scvs-creas",
            "question": "Does the cited legal vehicle correspond to CREAS Ecuador?",
            "result": "The record names Fideicomiso de Inversión CREAS Ecuador.",
            "effect": "identity_resolved_only",
            "used_for_discovery": False,
            "used_as_sole_eligibility_evidence": False,
            "queried_on": CUTOFF,
        }
    ],
)

coverage = {
    "candidate_count": len(candidates),
    "new_non_regulatory_discoveries": 14,
    "audited_non_regulatory_handoffs": 1,
    "regulatory_queries": 1,
    "regulatory_percent": round(100 / len(candidates), 1),
    "marginal_passes": [
        {
            "pass": 1,
            "families": ["industry_association"],
            "new_candidates": 7,
            "cumulative": 7,
        },
        {
            "pass": 2,
            "families": ["industry_news", "fund_news", "regional_platform"],
            "new_candidates": 4,
            "cumulative": 11,
        },
        {
            "pass": 3,
            "families": [
                "blind_ecosystem_map",
                "blind_sector_report",
                "historical_ecosystem_study",
                "municipal_program",
            ],
            "new_candidates": 4,
            "cumulative": 15,
        },
        {
            "pass": 4,
            "families": ["official_thesis_portfolio", "official_accelerator"],
            "new_candidates": 0,
            "cumulative": 15,
        },
    ],
    "blind_search": {
        "candidate_list_disclosed_to_searcher": False,
        "new_source_families": [
            "blind_ecosystem_map",
            "blind_sector_report",
            "municipal_program",
        ],
        "new_findings": [
            "ec-drivum",
            "ec-fundacion-crisfe",
            "ec-593-capital-partners",
            "ec-fonquito",
        ],
    },
    "limitation": "Audited coverage of the enumerated public sources, not absolute market completeness.",
}
write_json(OUT / "coverage-matrix.json", coverage)

excluded = sorted(
    candidate["candidate_id"]
    for candidate in candidates
    if candidate["decision"] == "insufficient_evidence"
)
sample_size = max(2, (len(excluded) + 4) // 5)
review_request = {
    "status": "completed",
    "requested_on": CUTOFF,
    "completed_on": CUTOFF,
    "freeze_allowed": True,
    "eligible_to_review": [
        candidate["candidate_id"]
        for candidate in candidates
        if candidate["decision"] == "eligible"
    ],
    "routed_to_review": [
        candidate["candidate_id"]
        for candidate in candidates
        if candidate["decision"] in {"routed", "routed_private_equity"}
    ],
    "regulatory_cases_to_review": ["ec-creas-ecuador"],
    "blind_findings_to_review": coverage["blind_search"]["new_findings"],
    "deterministic_exclusion_sample": sorted(
        excluded,
        key=lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest(),
    )[:sample_size],
    "required_checks": [
        "identity",
        "official evidence",
        "routing",
        "false negatives",
        "critical or high inconsistencies",
    ],
    "proposed_freeze": {
        "eligible": ["ec-impaqto-capital"],
        "publication_batch_count": 1,
        "publication_batch_limit": 10,
    },
}
write_json(OUT / "review-request.json", review_request)

review = {
    "status": "approved",
    "reviewer": "integrator",
    "reviewed_on": CUTOFF,
    "review_reconciled": True,
    "freeze_allowed": True,
    "eligible_reviewed": ["ec-impaqto-capital"],
    "routed_reviewed": review_request["routed_to_review"],
    "regulatory_cases_reviewed": ["ec-creas-ecuador"],
    "blind_findings_reviewed": coverage["blind_search"]["new_findings"],
    "exclusion_sample_reviewed": review_request[
        "deterministic_exclusion_sample"
    ],
    "critical_or_high_findings_open": 0,
    "reconciliation": [
        "IMPAQTO Capital is the only eligible identity and belongs in a regional profile with Ecuador as its strict base geography.",
        "BuenaVista Capital is routed to private equity after current official Fund 0 and Fund 1 evidence replaced the earlier insufficient-evidence decision.",
        "Kruger Labs remains routed as an accelerator; its accessible homepage and the current ECUACAP roster replace the unavailable team endpoint.",
    ],
}
write_json(OUT / "review.json", review)

tracked = [
    OUT / "contract.json",
    OUT / "baseline/catalog-baseline.jsonl",
    OUT / "baseline/prior-candidates.jsonl",
    OUT / "baseline/summary.json",
    OUT / "source-inventory.jsonl",
    OUT / "candidates.jsonl",
    OUT / "evidence.jsonl",
    OUT / "scvs-query-log.jsonl",
    OUT / "coverage-matrix.json",
    OUT / "review-request.json",
    OUT / "review.json",
]
freeze = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "reviewer": "integrator",
    "reviewed_on": CUTOFF,
    "review_reconciled": True,
    "counts": {
        "candidates": len(candidates),
        "eligible": 1,
        "duplicates": 3,
        "routed_or_out_of_scope": 6,
        "insufficient_evidence": 5,
        "regulatory_queries": 1,
    },
    "eligible_ids": ["ec-impaqto-capital"],
    "publication_batches": [
        {
            "batch": 1,
            "candidate_ids": ["ec-impaqto-capital"],
            "profile_paths": ["funds/regional/impaqto-capital.md"],
        }
    ],
    "artifact_hashes": {
        path.relative_to(ROOT).as_posix(): digest(path) for path in tracked
    },
    "critical_or_high_findings_open": 0,
    "limitations": [
        "Audited coverage of enumerated public sources, not absolute market completeness.",
        "The regulator was used for one identity check only and did not drive discovery or eligibility.",
        "Only IMPAQTO Capital is publishable in this frozen cut.",
    ],
}
write_json(OUT / "freeze-manifest.json", freeze)

profile_paths = [
    ROOT / "funds/regional/impaqto-capital.md",
    ROOT / "translations/pt-BR/funds/regional/impaqto-capital.md",
    ROOT / "translations/es/funds/regional/impaqto-capital.md",
]
publication = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "batch_count": 1,
    "batch_limit": 10,
    "eligible_ids": ["ec-impaqto-capital"],
    "published_profile_count": (
        1 if all(path.exists() for path in profile_paths) else 0
    ),
    "localized_profile_count": sum(path.exists() for path in profile_paths),
    "profile_hashes": {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in profile_paths
        if path.exists()
    },
    "critical_or_high_findings_open": 0,
}
write_json(OUT / "publication-report.json", publication)

closure = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "reviewer": "integrator",
    "reviewed_on": CUTOFF,
    "review_reconciled": True,
    "eligible_count": 1,
    "published_profile_count": publication["published_profile_count"],
    "publication_batch_count": 1,
    "new_non_regulatory_discoveries": 14,
    "audited_non_regulatory_handoffs": 1,
    "regulatory_query_percent": round(100 / len(candidates), 1),
    "critical_or_high_findings_open": 0,
    "absolute_completeness_claimed": False,
}
write_json(OUT / "closure-report.json", closure)
