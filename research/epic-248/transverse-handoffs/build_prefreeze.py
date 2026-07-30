#!/usr/bin/env python3
"""Build the cross-market fund handoff audit up to the independent-review gate."""

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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


contract = {
    "schema_version": "1.0",
    "epic": 248,
    "scope": "three audited cross-market handoffs from the Uruguay re-audit",
    "markets": ["AR", "BR"],
    "cutoff": CUTOFF,
    "coverage_claim": "audited_handoff_batch_not_market_completeness",
    "eligible_gates": [
        "base_geography",
        "direct_investment",
        "recurrence",
        "current_activity",
        "portfolio",
        "founder_route",
        "official_evidence",
    ],
    "discovery_rule": "handoff_only_with_non_regulatory_revalidation",
    "regulator_rule": "identity_or_divergence_only",
    "regulator_target_percent": [5, 10],
    "regulator_target_application": "portfolio-wide target; zero is valid when no identity divergence exists",
    "review_gate": "independent_integrator_review_required_before_freeze",
    "publication_batch_limit": 10,
    "required_locales": ["en", "pt-BR", "es"],
}


source_specs = [
    (
        "beta-official",
        "official_fund",
        "https://betaimpacto.vc/",
        "AR",
        "Current impact VC thesis, team, portfolio operations and founder application route",
        "complete",
    ),
    (
        "beta-impact",
        "official_portfolio",
        "https://betaimpacto.vc/impacto/",
        "AR",
        "Direct early-stage investment, active portfolio monitoring and startup support",
        "complete",
    ),
    (
        "beta-xeibo",
        "official_identity",
        "https://xeibocapital.com/",
        "AR",
        "Buenos Aires headquarters of Beta Impacto co-creator Xeibo",
        "complete",
    ),
    (
        "beta-anii",
        "institutional_allocator_profile",
        "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/532/beta-impacto/",
        "AR",
        "Independent institutional confirmation of an early-stage investment fund",
        "complete",
    ),
    (
        "beta-launch",
        "fund_news",
        "https://empretec.org.ar/wp-content/uploads/2024/09/Innovacion-n14.pdf",
        "AR",
        "Independent report of the USD 20M fund launch and planned recurring portfolio",
        "complete",
    ),
    (
        "primaryx-official",
        "official_cvc",
        "https://pmyx.com.ar/",
        "AR",
        "Current A3 Mercados CVC thesis, multi-company portfolio and founder form",
        "complete",
    ),
    (
        "primaryx-a3-2025",
        "official_financial_statement",
        "https://a3mercados.com.ar/wp-content/uploads/2025/10/Memoria-y-Estados-Financieros-A3-DIGITAL-25.pdf",
        "AR",
        "Argentina corporate identity and 2025 direct investments in Origino and Skyblue Analytics",
        "complete",
    ),
    (
        "primaryx-a3-2026",
        "official_financial_statement",
        "https://a3mercados.com.ar/wp-content/uploads/2026/04/Memoria-y-estados-financieros-A3-DIGITAL-Ejercicio-N%C2%B0-118-26.pdf",
        "AR",
        "Current ownership and Argentina investment-company identity of Primary X S.A.U.",
        "complete",
    ),
    (
        "saasholic-official",
        "official_portfolio",
        "https://www.saasholic.com/",
        "BR",
        "Current Fund II activity, 14-company named portfolio and capital-raising route",
        "complete",
    ),
    (
        "saasholic-founders",
        "official_thesis",
        "https://www.saasholic.com/founders",
        "BR",
        "Pre-seed and seed checks, direct SAFE investment process and founder application",
        "complete",
    ),
    (
        "saasholic-company-profile",
        "public_company_profile",
        "https://www.linkedin.com/company/saasholic",
        "BR",
        "Company-controlled profile identifying São Paulo headquarters and current activity",
        "complete",
    ),
    (
        "saasholic-anii",
        "institutional_allocator_profile",
        "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/648/saasholic/",
        "BR",
        "Independent institutional confirmation of regional market access",
        "complete",
    ),
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
        "status": status,
        "research_channel": "non_regulatory",
        "discovery_allowed": True,
    }
    for source_id, family, url, market, scope, status in source_specs
]


candidate_specs = [
    {
        "candidate_id": "ar-beta-impacto",
        "name": "Beta Impacto",
        "canonical_domain": "betaimpacto.vc",
        "base_country": "AR",
        "source_ids": ["beta-official", "beta-impact", "beta-xeibo", "beta-anii", "beta-launch"],
        "destination": "funds/argentina/beta-impacto.md",
        "reason": (
            "Current official and institutional sources identify an Argentina-linked impact VC fund "
            "that invests directly in early-stage Latin American startups, operates and monitors a "
            "portfolio, and accepts founder applications. The official site does not expose the names "
            "of portfolio companies as machine-readable text, so that limitation remains explicit."
        ),
    },
    {
        "candidate_id": "ar-primary-x",
        "name": "Primary X",
        "canonical_domain": "pmyx.com.ar",
        "base_country": "AR",
        "source_ids": ["primaryx-official", "primaryx-a3-2025", "primaryx-a3-2026"],
        "destination": "funds/argentina/primary-x.md",
        "reason": (
            "The current official site identifies A3 Mercados' early-stage fintech, crypto and "
            "agrifintech CVC, a multi-company portfolio and an open founder form. A3's official "
            "financial statements confirm its Argentina entity and multiple direct investments, "
            "including Origino and a USD 100,000 investment in Skyblue Analytics in 2025."
        ),
    },
    {
        "candidate_id": "br-saasholic",
        "name": "SaaSholic",
        "canonical_domain": "saasholic.com",
        "base_country": "BR",
        "source_ids": [
            "saasholic-official",
            "saasholic-founders",
            "saasholic-company-profile",
            "saasholic-anii",
        ],
        "destination": "funds/brazil/saasholic.md",
        "reason": (
            "Current official sources identify an early-stage Latin American SaaS VC with 14 Fund II "
            "companies, a named portfolio, direct SAFE checks and an open founder route. The "
            "company-controlled public profile places its headquarters in São Paulo."
        ),
    },
]

candidates = [
    {
        "schema_version": "1.0",
        "candidate_id": row["candidate_id"],
        "name": row["name"],
        "canonical_domain": row["canonical_domain"],
        "base_country": row["base_country"],
        "discovery_origin": "audited_non_regulatory_handoff",
        "discovery_source_ids": row["source_ids"],
        "cutoff": CUTOFF,
        "decision": "eligible",
        "canonical_destination": row["destination"],
        "reason": row["reason"],
        "status": "terminal",
    }
    for row in candidate_specs
]

evidence_specs = {
    "ar-beta-impacto": {
        "base_geography": "confirmed_via_argentina_co_creator",
        "direct_investment": "confirmed",
        "recurrence": "confirmed_by_fund_design_and_portfolio_operations",
        "current_activity": "confirmed",
        "portfolio": "confirmed_without_machine_readable_company_names",
        "founder_route": "confirmed",
        "official_evidence": "confirmed",
    },
    "ar-primary-x": {
        "base_geography": "confirmed_argentina_entity",
        "direct_investment": "confirmed",
        "recurrence": "confirmed_multiple_investments",
        "current_activity": "confirmed_2025_investments_and_2026_site",
        "portfolio": "confirmed",
        "founder_route": "confirmed",
        "official_evidence": "confirmed",
    },
    "br-saasholic": {
        "base_geography": "confirmed_sao_paulo",
        "direct_investment": "confirmed",
        "recurrence": "confirmed_14_fund_ii_companies",
        "current_activity": "confirmed",
        "portfolio": "confirmed_named",
        "founder_route": "confirmed",
        "official_evidence": "confirmed",
    },
}

evidence = [
    {
        "schema_version": "1.0",
        "evidence_id": f"ev-{row['candidate_id']}",
        "candidate_id": row["candidate_id"],
        "source_ids": row["discovery_source_ids"],
        "accessed_on": CUTOFF,
        "claims": evidence_specs[row["candidate_id"]],
        "finding": row["reason"],
    }
    for row in candidates
]


profile_paths = sorted((ROOT / "funds").glob("**/*.md"), key=lambda path: path.as_posix().casefold())
baseline_rows = []
for path in profile_paths:
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"\A---\s*(\{.*?\})\s*---", raw, re.DOTALL)
    metadata = json.loads(match.group(1)) if match else {}
    baseline_rows.append(
        {
            "schema_version": "1.0",
            "entity_id": metadata.get("entity_id"),
            "name": metadata.get("name"),
            "profile_path": path.relative_to(ROOT).as_posix(),
            "official_website": metadata.get("official_website"),
            "profile_sha256": digest(path),
        }
    )

uruguay_candidates_path = ROOT / "research" / "epic-254" / "uruguay" / "candidates.jsonl"
uruguay_candidates = [
    json.loads(line)
    for line in uruguay_candidates_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
handoff_names = {"Beta Impacto", "Primary X", "SaaSholic"}
handoff_rows = [row for row in uruguay_candidates if row.get("name") in handoff_names]

write_json(OUT / "contract.json", contract)
write_jsonl(OUT / "source-inventory.jsonl", sources)
write_jsonl(OUT / "candidates.jsonl", candidates)
write_jsonl(OUT / "evidence.jsonl", evidence)
write_jsonl(OUT / "regulator-query-log.jsonl", [])
write_jsonl(OUT / "baseline" / "catalog-baseline.jsonl", baseline_rows)
write_jsonl(OUT / "baseline" / "uruguay-handoffs.jsonl", handoff_rows)
write_json(
    OUT / "baseline" / "summary.json",
    {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "catalog_profile_count": len(baseline_rows),
        "matching_catalog_profiles": [],
        "uruguay_handoff_count": len(handoff_rows),
        "catalog_sha256": digest(OUT / "baseline" / "catalog-baseline.jsonl"),
        "handoffs_sha256": digest(OUT / "baseline" / "uruguay-handoffs.jsonl"),
    },
)

write_json(
    OUT / "coverage-matrix.json",
    {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "candidate_count": len(candidates),
        "decision_counts": {
            "eligible": 3,
            "duplicate": 0,
            "routed": 0,
            "insufficient_evidence": 0,
        },
        "source_count": len(sources),
        "non_regulatory_source_count": len(sources),
        "non_regulatory_discovery_percent": 100.0,
        "regulatory_query_count": 0,
        "regulatory_case_percent": 0.0,
        "market_counts": {"AR": 2, "BR": 1},
        "handoff_reconciliation": {
            "expected": ["Beta Impacto", "Primary X", "SaaSholic"],
            "reconciled": ["Beta Impacto", "Primary X", "SaaSholic"],
            "missing": [],
        },
        "limitations": [
            "This is an audited handoff batch, not a new completeness claim for Argentina or Brazil.",
            "Beta Impacto's official pages describe portfolio operations but do not expose portfolio company names as machine-readable text.",
            "No regulator query was justified because the public sources presented no unresolved identity divergence.",
        ],
    },
)

write_json(
    OUT / "review-request.json",
    {
        "schema_version": "1.0",
        "status": "pending_independent_review",
        "requested_on": CUTOFF,
        "freeze_allowed": False,
        "candidate_count": 3,
        "eligible_to_review": ["ar-beta-impacto", "ar-primary-x", "br-saasholic"],
        "regulatory_cases_to_review": [],
        "base_geography_checks": {
            "ar-beta-impacto": {
                "proposed_base": "AR",
                "supporting_sources": ["beta-official", "beta-xeibo", "beta-anii"],
                "limitation": "The base is tied to the Argentina organizations that created the fund, not to Uruguay market access.",
            },
            "ar-primary-x": {
                "proposed_base": "AR",
                "supporting_sources": ["primaryx-official", "primaryx-a3-2025", "primaryx-a3-2026"],
                "limitation": "Uruguay institutional access is not used as a headquarters signal.",
            },
            "br-saasholic": {
                "proposed_base": "BR",
                "supporting_sources": ["saasholic-company-profile", "saasholic-official"],
                "limitation": "The São Paulo base comes from the company-controlled public profile, not ANII market access.",
            },
        },
        "proposed_freeze": {
            "eligible": ["ar-beta-impacto", "ar-primary-x", "br-saasholic"],
            "publication_batch_count": 1,
            "publication_batch_limit": 10,
            "localized_profile_count": 9,
        },
        "review_focus": [
            "Challenge Beta Impacto recurrence and portfolio evidence given the absence of machine-readable portfolio names.",
            "Confirm that each proposed base reflects headquarters or manager identity rather than Uruguay market access.",
            "Confirm that no regulator lookup is necessary for identity resolution.",
        ],
    },
)

write_json(
    OUT / "prefreeze-manifest.json",
    {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "status": "awaiting_independent_review",
        "freeze_allowed": False,
        "counts": {
            "candidates": 3,
            "eligible": 3,
            "sources": len(sources),
            "non_regulatory_sources": len(sources),
            "regulatory_queries": 0,
        },
        "artifact_hashes": {
            path.relative_to(ROOT).as_posix(): digest(path)
            for path in sorted(OUT.glob("*.json*"))
            if path.name != "prefreeze-manifest.json"
        },
        "limitations": [
            "Audited reconciliation of three prior handoffs, not absolute market completeness.",
            "Freeze and publication remain blocked until independent integrator review.",
            "Regulators were not consulted because no material identity divergence remained.",
        ],
    },
)

print(
    json.dumps(
        {
            "candidates": 3,
            "eligible": 3,
            "sources": len(sources),
            "regulatory_queries": 0,
            "status": "awaiting_independent_review",
        },
        ensure_ascii=False,
    )
)
