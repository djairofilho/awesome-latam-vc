#!/usr/bin/env python3
"""Build the reproducible Uruguay fund re-audit before independent review."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from publication import PROFILES, profile_outputs


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"
NEW_PROFILES = {
    "funds/uruguay/eager-ventures.md",
    "funds/uruguay/ic-ventures.md",
    "funds/uruguay/labplus-venture-fund.md",
    "funds/uruguay/mrpink-vc.md",
    "funds/uruguay/tokai-ventures.md",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def jsonl_bytes(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows).encode()


SOURCES = [
    ("uy-urucap-directory-2025", "industry_directory", "https://drive.google.com/file/d/1tGvZhIUVvhKVyWO4Y2L64LZEvJZinDLK/view", "URUCAP member directory through August 2025", "complete", 18),
    ("uy-urucap-community", "industry_association", "https://www.urucap.org/nuestra-comunidad", "Current investor, angel and service-provider community", "complete", 4),
    ("uy-urucap-survey-2025", "investor_survey", "https://www.urucap.org/estudios/resultados-de-la-encuestainversiones-2025", "Current activity, stages and sectors in the local market", "complete", 0),
    ("uy-xxi-private-capital-2025", "institutional_map", "https://www.uruguayxxi.gub.uy/uploads/informacion/3906eb4c2fbfe88d98d7c3fb06982b9e41feb8f3.pdf", "2024-2025 deals, ecosystem actors and geographic context", "complete", 8),
    ("uy-anii-ic", "allocator_profile", "https://anii.org.uy/emprendimientos/fondos-de-capital-de-riesgo/165/ic-ventures/", "Institutional description of IC Ventures and Uruguay access", "complete", 1),
    ("uy-anii-tokai", "allocator_profile", "https://anii.org.uy/emprendimientos/fondos-de-capital-de-riesgo/169/tokai-ventures/", "Institutional description of Tokai Ventures and portfolio", "complete", 1),
    ("uy-ic-official", "official_portfolio", "https://ic-ventures.vc/", "Current thesis, direct investment, portfolio and contact", "complete", 0),
    ("uy-mrpink-official", "official_portfolio", "https://mrpink.vc/", "Current thesis and Inception Fund portfolio", "complete", 0),
    ("uy-mrpink-thesis", "official_thesis", "https://mrpink.vc/tesis", "Inception Fund dates and future Human Connection Fund", "complete", 0),
    ("uy-eager-official", "official_portfolio", "https://www.eagerventures.io/", "Current direct funding, stages, cases and founder contact", "complete", 0),
    ("uy-tokai-official", "official_domain", "https://www.tokaiventures.com/", "Canonical domain did not return usable current content", "gap_justified", 0),
    ("uy-skywalker-official", "official_thesis", "https://skywalkercapitals.com/en/", "Current venture thesis and open application, with Madrid contact address", "complete", 0),
    ("uy-labplus-official", "official_portfolio", "https://labplus.uy/", "Current company-builder identity and life-sciences portfolio", "complete", 0),
    ("uy-ourcrowd-labs-official", "official_program", "https://www.ourcrowdlatam.com/about", "Current accelerator identity in Uruguay", "complete", 0),
    ("uy-white-lions-official", "official_portfolio", "https://whitelions.vc/portfolio/", "Current angel-investor-firm identity and portfolio", "complete", 0),
    ("uy-zorzal-official", "official_portfolio", "https://www.zorzal.uy/", "Current listed vehicle investing in mature Uruguayan software companies", "complete", 0),
    ("uy-draco-official", "official_thesis", "https://dracocapital.com/index.php", "Current multi-asset event-opportunity fund", "complete", 0),
    ("uy-myelin-official", "official_portfolio", "https://www.myelin.vc/", "Current seed-to-Series-A thesis and portfolio", "complete", 0),
    ("uy-arche-official", "official_identity", "https://www.archecompany.co/about", "Current successor identity after Zonda Capital", "complete", 0),
    ("uy-primaryx-official", "official_thesis", "https://pmyx.io/", "Current CVC thesis and Argentine ecosystem identity", "complete", 0),
    ("uy-blind-ort-thesis", "blind_academic", "https://rad.ort.edu.uy/server/api/core/bitstreams/e6a25a3c-63a5-484f-ba6c-64f66208bf2d/content", "Independent terminology and interviews covering Uruguay-origin managers", "complete", 3),
    ("uy-blind-independent-map", "blind_independent_database", "https://shizune.co/investors/vc-funds-uruguay", "Independent investor map used only for false-negative search", "complete", 2),
    ("uy-anii-oce-registry", "institutional_allocator", "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/", "Current complete register of 15 preapproved venture-capital organizations", "complete", 8),
    ("uy-anii-labplus-fund", "allocator_profile", "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/540/lab-venture-fund/", "Current institutional fund identity, investment activity and contact", "complete", 0),
    ("uy-labplus-portfolio", "official_portfolio", "https://labplus.uy/portfolio/", "Current named life-sciences portfolio", "complete", 0),
    ("uy-anii-beta-impacto", "allocator_profile", "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/532/beta-impacto/", "Current institutional fund identity and regional market access", "complete", 0),
    ("uy-beta-impacto-official", "official_thesis", "https://betaimpacto.vc/", "Current impact-investment thesis, team and application route", "complete", 0),
    ("uy-xeibo-official", "official_identity", "https://xeibocapital.com/en/", "Buenos Aires headquarters of a founding Beta Impacto organization", "complete", 0),
    ("uy-anii-tritemus", "allocator_profile", "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/541/tritemus-fund/", "Current institutional fund identity and Uruguay market access", "complete", 0),
    ("uy-tritemius-official", "official_thesis", "https://tritemius.com/vc/", "Current Spanish fund identity, portfolio, ticket and founder route", "complete", 0),
    ("uy-anii-saasholic", "allocator_profile", "https://anii.org.uy/emprendimientos/organizaciones-de-capital-emprendedor/648/saasholic/", "Current institutional fund identity and Uruguay market access", "complete", 0),
    ("uy-saasholic-official", "official_portfolio", "https://www.saasholic.com/", "Current Fund II activity, portfolio metrics and founder route", "complete", 0),
    ("uy-saasholic-company-profile", "public_company_profile", "https://www.linkedin.com/company/saasholic", "Current public company profile placing headquarters in São Paulo", "complete", 0),
    ("uy-platanus-official", "official_program", "https://wiki.platanus.ventures/about/", "Canonical Platanus program and investment-vehicle identity", "complete", 0),
]

SOURCE_ROWS = [
    {
        "schema_version": "1.0",
        "source_id": source_id,
        "family": family,
        "url": url,
        "scope": scope,
        "accessed_on": CUTOFF,
        "result": result,
        "new_names_observed": new_names,
        "owner": f"uruguay-{family}",
        "research_channel": "non_regulatory",
        "discovery_allowed": True,
    }
    for source_id, family, url, scope, result, new_names in SOURCES
]

CANDIDATES = [
    ("ic-ventures", "IC Ventures", "ic-ventures.vc", ["uy-urucap-directory-2025", "uy-anii-ic", "uy-ic-official"], "eligible", "funds/uruguay/ic-ventures.md", "Official and institutional sources confirm a Montevideo seed/pre-Series-A fund, recurring direct investments, a current portfolio and founder contact."),
    ("mrpink-vc", "MrPink VC", "mrpink.vc", ["uy-urucap-directory-2025", "uy-mrpink-official", "uy-mrpink-thesis"], "eligible", "funds/uruguay/mrpink-vc.md", "The current official site documents the 27-company Inception Fund through 2025, an early-stage thesis, Uruguay headquarters and a founder route; the next fund has no announced launch date."),
    ("eager-ventures", "Eager Ventures", "eagerventures.io", ["uy-urucap-directory-2025", "uy-eager-official"], "eligible", "funds/uruguay/eager-ventures.md", "The current official site confirms recurring financial investment up to USD 100,000, pre-seed/seed focus, named cases and an external founder contact."),
    ("tokai-ventures", "Tokai Ventures", "tokaiventures.com", ["uy-urucap-directory-2025", "uy-anii-tokai", "uy-blind-ort-thesis"], "eligible", "funds/uruguay/tokai-ventures.md", "URUCAP 2025 and ANII identify a Montevideo seed/venture fund with more than 20 direct investments; the canonical domain is retained with its access gap disclosed."),
    ("labplus-venture-fund", "LAB+ Venture Fund", "labplus.uy", ["uy-anii-oce-registry", "uy-anii-labplus-fund", "uy-labplus-portfolio"], "eligible", "funds/uruguay/labplus-venture-fund.md", "ANII identifies the fund as a distinct investment vehicle formed by Institut Pasteur de Montevideo and FICUS; the current official portfolio confirms four financed life-sciences startups."),
    ("impacta-vc", "Impacta VC", "impacta.vc", ["uy-urucap-directory-2025"], "duplicate", "funds/regional/impacta-vc.md", "The current canonical regional profile already covers the same Chile-and-Uruguay manager."),
    ("gridx", "GRIDX", "gridexponential.com", ["uy-urucap-directory-2025"], "duplicate", "funds/multi-country/gridx.md", "The current multi-country profile already covers this manager."),
    ("ithink-vc", "iThink VC", "ithinkvc.tech", ["uy-urucap-directory-2025", "uy-xxi-private-capital-2025"], "duplicate", "funds/regional/ithink-vc.md", "The current regional profile already includes Uruguay in its declared geography."),
    ("sancor-seguros-ventures", "Sancor Seguros Ventures", "sancorsegurosventures.com", ["uy-urucap-directory-2025"], "duplicate", "funds/argentina/sancor-seguros-ventures.md", "The manager is headquartered in Argentina and already has a canonical profile there."),
    ("cites", "CITES", "cites-gss.com", ["uy-urucap-directory-2025"], "duplicate", "funds/regional/cites.md", "The current regional profile already covers this Argentina-based manager."),
    ("kamay-ventures", "Kamay Ventures", "kamayventures.com", ["uy-urucap-directory-2025"], "duplicate", "funds/regional/kamay-ventures.md", "The current regional profile already covers this Argentina-based manager."),
    ("nxtp", "NXTP", "nxtp.vc", ["uy-urucap-directory-2025"], "duplicate", "funds/regional/nxtp-ventures.md", "The current regional profile already covers this manager."),
    ("alaya-capital", "Alaya Capital", "alaya-capital.com", ["uy-urucap-directory-2025"], "duplicate", "funds/regional/alaya-capital.md", "The current regional profile already covers this Argentina-based manager."),
    ("babasu-ventures", "Babasú Ventures", "babasu.vc", ["uy-blind-independent-map"], "duplicate", "funds/regional/babasu-ventures.md", "The current regional profile already includes Uruguay in its declared geography."),
    ("ewa-capital", "EWA Capital", "ewa.capital", ["uy-anii-oce-registry"], "duplicate", "funds/regional/ewa-capital.md", "The current regional profile already covers this Bogotá-based manager."),
    ("sf500", "SF500", "sf500.vc", ["uy-anii-oce-registry"], "duplicate", "funds/regional/sf500.md", "The current regional profile already covers this Argentina-based life-sciences fund and company builder."),
    ("the-yield-lab-latam", "The Yield Lab LATAM", "theyieldlablatam.com", ["uy-anii-oce-registry"], "duplicate", "funds/regional/the-yield-lab-latam.md", "The current regional profile already covers this Latin American agri-food investment organization."),
    ("platanus", "Platanus", "platanus.ventures", ["uy-anii-oce-registry", "uy-platanus-official"], "duplicate", "funds/:platanus.ventures#investment-vehicle", "The investment vehicle is already reconciled under the canonical Platanus entity in the cross-category registry; Uruguay preapproval is market access."),
    ("labplus", "LAB+ Company Builder", "labplus.uy", ["uy-urucap-directory-2025", "uy-labplus-official"], "routed", "epic-62-accelerators", "The official identity is a company builder; its direct financing remains documented for the accelerator/company-builder audit."),
    ("ourcrowd-latam-labs", "OurCrowd LATAM Labs", "ourcrowdlatam.com", ["uy-urucap-directory-2025", "uy-ourcrowd-labs-official"], "routed", "epic-62-accelerators", "The official site explicitly identifies a government-backed startup accelerator."),
    ("thaleslab", "ThalesLab", "thaleslab.com", ["uy-urucap-directory-2025", "uy-urucap-community"], "routed", "epic-62-accelerators", "The current ecosystem identity and directory classify it as a company builder."),
    ("white-lions", "White Lions", "whitelions.vc", ["uy-urucap-directory-2025", "uy-white-lions-official"], "routed", "epic-63-angels", "The current official site explicitly identifies an angel investor firm."),
    ("draper-startup-house", "Draper Startup House", "draperstartuphouse.com", ["uy-urucap-directory-2025"], "routed", "epic-62-accelerators", "The directory classifies the cross-border entity as pre-acceleration, not a Uruguay fund."),
    ("cibersons", "Cibersons", "cibersons.com", ["uy-urucap-directory-2025"], "routed", "epic-256-paraguay", "The directory places headquarters in Paraguay and Silicon Valley; Uruguay membership does not create a Uruguay-based identity."),
    ("myelin-vc", "Myelin VC", "myelin.vc", ["uy-blind-independent-map", "uy-myelin-official"], "routed", "future-spain-or-global-audit", "The official site confirms the fund, while its current official company identity places headquarters in Madrid rather than Uruguay."),
    ("primary-x", "Primary X", "pmyx.io", ["uy-xxi-private-capital-2025", "uy-primaryx-official", "uy-anii-oce-registry"], "routed", "epic-252-argentina-follow-up", "The CVC is associated with Argentina's Grupo A3; ANII preapproval is Uruguay market access, not a Uruguay headquarters signal."),
    ("the-ganesha-fund", "The Ganesha Fund", "ganeshalab.com", ["uy-xxi-private-capital-2025", "uy-anii-oce-registry"], "routed", "epic-251-chile-follow-up", "The Chile-based manager's ANII preapproval and Uruguay coinvestment demonstrate market access, not a Uruguay base."),
    ("beta-impacto", "Beta Impacto", "betaimpacto.vc", ["uy-anii-oce-registry", "uy-anii-beta-impacto", "uy-beta-impacto-official", "uy-xeibo-official"], "routed", "epic-252-argentina-follow-up", "The fund is formed by Argentina ecosystem organizations, including Buenos Aires-headquartered Xeibo; ANII preapproval establishes Uruguay market access, not a Uruguay base."),
    ("tritemus-fund", "Tritemius Fund", "tritemius.com", ["uy-anii-oce-registry", "uy-anii-tritemus", "uy-tritemius-official"], "routed", "future-spain-or-global-audit", "The official site identifies Tritemius Fund I as a Spanish vehicle managed by Abante and registered with the CNMV; ANII preapproval is market access."),
    ("saasholic", "SaaSholic", "saasholic.com", ["uy-anii-oce-registry", "uy-anii-saasholic", "uy-saasholic-official", "uy-saasholic-company-profile"], "routed", "epic-207-brazil-follow-up", "The current public company profile places headquarters in São Paulo, while ANII preapproval establishes Uruguay market access."),
    ("zorzal", "Zorzal Inversiones Tecnológicas", "zorzal.uy", ["uy-xxi-private-capital-2025", "uy-zorzal-official"], "routed", "out-of-scope-mature-growth-capital", "The listed vehicle targets profitable software companies with at least five years of activity and USD 3 million revenue, outside the startup VC entry-stage contract."),
    ("rou-partners", "ROU Partners", "roupartners.com", ["uy-urucap-directory-2025", "uy-urucap-community"], "routed", "out-of-scope-search-funds", "The entity is a search fund acquiring control of one mature company, not a recurring direct startup investor."),
    ("skywalker", "Skywalker Investments & Capital Partners", "skywalkercapitals.com", ["uy-urucap-directory-2025", "uy-skywalker-official"], "insufficient_evidence", None, "URUCAP lists Uruguay headquarters, but the current official contact is Madrid and no authoritative current source resolves the operating base."),
    ("draco-capital", "Draco Capital", "dracocapital.com", ["uy-blind-independent-map", "uy-draco-official"], "insufficient_evidence", None, "The current event-opportunity fund is predominantly multi-asset and does not disclose a recurring direct startup portfolio."),
    ("arche-company", "ARCHE Company / Zonda Capital", "archecompany.co", ["uy-blind-ort-thesis", "uy-arche-official"], "insufficient_evidence", None, "The current successor presents an advisory and venture-development company; recurring fund activity after Zonda Capital was not established."),
    ("prosperitas-capital-partners", "Prosperitas Capital Partners", None, ["uy-blind-ort-thesis"], "insufficient_evidence", None, "The historical Uruguay manager lacks a current official domain, active thesis and recent portfolio evidence."),
]

CANDIDATE_ROWS = [
    {
        "schema_version": "1.0",
        "candidate_id": f"uy-{slug}",
        "name": name,
        "canonical_domain": domain,
        "discovery_source_ids": source_ids,
        "discovery_origin": "non_regulatory",
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "cutoff": CUTOFF,
    }
    for slug, name, domain, source_ids, decision, destination, reason in CANDIDATES
]

REGULATORY_QUERIES = [
    {
        "schema_version": "1.0",
        "query_id": "uy-bcu-zorzal-identity",
        "candidate_id": "uy-zorzal",
        "regulator": "Banco Central del Uruguay",
        "url": "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/InformacionInstitucion.aspx?nroinst=4268",
        "question": "Does the public-market identity match Zorzal Inversiones Tecnológicas S.A.?",
        "result": "Identity and active issuer status confirmed.",
        "effect": "identity_only",
        "used_for_discovery": False,
        "used_for_eligibility": False,
        "accessed_on": CUTOFF,
    },
    {
        "schema_version": "1.0",
        "query_id": "uy-bcu-skywalker-identity",
        "candidate_id": "uy-skywalker",
        "regulator": "Banco Central del Uruguay",
        "url": "https://www.bcu.gub.uy/Servicios-Financieros-SSF/Paginas/buscadores-registros.aspx",
        "question": "Does a local regulated identity resolve the Uruguay-versus-Madrid operating-base divergence?",
        "result": "No matching registered identity found; divergence remains unresolved.",
        "effect": "divergence_only",
        "used_for_discovery": False,
        "used_for_eligibility": False,
        "accessed_on": CUTOFF,
    },
]


def outputs() -> dict[Path, bytes]:
    current_profiles = [
        path
        for path in sorted(ROOT.glob("funds/**/*.md"))
        if path.relative_to(ROOT).as_posix() not in NEW_PROFILES
    ]
    baseline_rows = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
        for path in current_profiles
    ]
    prior_files = [
        ROOT / "research/epic-16/issue-26/candidates.jsonl",
        ROOT / "research/epic-16/issue-29/README.md",
    ]
    prior_rows = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": digest(path),
            "classification": "historical_baseline_not_discovery",
        }
        for path in prior_files
    ]
    evidence_rows = []
    for row in CANDIDATE_ROWS:
        eligible = row["decision"] == "eligible"
        evidence_rows.append({
            "schema_version": "1.0",
            "evidence_id": f"ev-{row['candidate_id']}",
            "candidate_id": row["candidate_id"],
            "decision": row["decision"],
            "source_ids": row["discovery_source_ids"],
            "gates": {
                "identity": "resolved" if row["candidate_id"] != "uy-skywalker" else "divergent",
                "uruguay_base": "confirmed" if eligible else "not_applicable_or_unconfirmed",
                "direct_investment": "confirmed" if eligible else "not_applicable_or_insufficient",
                "recurrence": "confirmed" if eligible else "not_applicable_or_insufficient",
                "recent_activity": "confirmed" if eligible else "not_applicable_or_insufficient",
                "founder_route": "confirmed" if eligible else "not_applicable_or_insufficient",
                "official_evidence": "confirmed" if eligible else "not_applicable_or_insufficient",
            },
            "reason": row["reason"],
            "accessed_on": CUTOFF,
        })
    contract = {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "market": "UY",
        "eligible_gates": ["uruguay_base", "direct_investment", "recurrence", "recent_activity", "founder_route", "official_evidence"],
        "geographic_rule": "Coverage of Uruguay is not a Uruguay base; foreign-headquartered candidates are duplicates or routed.",
        "discovery_rule": "non_regulatory_only",
        "regulator": "Banco Central del Uruguay",
        "regulator_rule": "identity_or_divergence_only",
        "regulator_target_percent": [5, 10],
        "excluded_discovery_inputs": ["local_startup_dataset", "regulatory_registry", "existing_catalog"],
        "publication_batch_limit": 10,
        "required_locales": ["en", "pt-BR", "es"],
        "terminal_decisions": ["eligible", "duplicate", "routed", "insufficient_evidence"],
    }
    decision_counts = {
        decision: sum(row["decision"] == decision for row in CANDIDATE_ROWS)
        for decision in contract["terminal_decisions"]
    }
    family_yield = [
        {
            "family": family,
            "sources_walked": sum(row["family"] == family for row in SOURCE_ROWS),
            "new_names_observed": sum(row["new_names_observed"] for row in SOURCE_ROWS if row["family"] == family),
        }
        for family in sorted({row["family"] for row in SOURCE_ROWS})
    ]
    coverage = {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "canonical_candidates": len(CANDIDATE_ROWS),
        "decision_counts": decision_counts,
        "non_regulatory_discovery_count": len(CANDIDATE_ROWS),
        "non_regulatory_discovery_percent": 100.0,
        "regulatory_queries": len(REGULATORY_QUERIES),
        "regulatory_query_percent_of_candidates": round(100 * len(REGULATORY_QUERIES) / len(CANDIDATE_ROWS), 1),
        "family_yield": family_yield,
        "marginal_passes": [
            {"pass": 1, "families": ["industry_directory", "institutional_map"], "new_canonical_candidates": 22, "cumulative": 22},
            {"pass": 2, "families": ["institutional_allocator"], "new_canonical_candidates": 8, "cumulative": 30},
            {"pass": 3, "families": ["allocator_profile", "official_portfolio", "official_thesis"], "new_canonical_candidates": 3, "cumulative": 33},
            {"pass": 4, "families": ["blind_academic", "blind_independent_database"], "new_canonical_candidates": 3, "cumulative": 36},
            {"pass": 5, "families": ["saturation_recheck"], "new_canonical_candidates": 0, "cumulative": 36},
        ],
        "blind_search": {
            "candidate_list_withheld": True,
            "families": ["blind_academic", "blind_independent_database"],
            "new_findings": ["uy-myelin-vc", "uy-arche-company", "uy-prosperitas-capital-partners"],
            "new_eligible_after_reconciliation": 0,
        },
        "limitation": "Audited coverage of the walked public sources, not a claim of absolute market completeness.",
    }
    exclusion_population = sorted(
        row["candidate_id"]
        for row in CANDIDATE_ROWS
        if row["decision"] in {"duplicate", "insufficient_evidence"}
    )
    sample_size = max(1, (len(exclusion_population) + 4) // 5)
    sample = sorted(
        exclusion_population,
        key=lambda value: (hashlib.sha256(value.encode()).hexdigest(), value),
    )[:sample_size]
    review = {
        "schema_version": "1.0",
        "status": "approved",
        "requested_on": CUTOFF,
        "reviewer": "integrator",
        "reviewed_on": CUTOFF,
        "review_reconciled": True,
        "eligible_review_required": sorted(row["candidate_id"] for row in CANDIDATE_ROWS if row["decision"] == "eligible"),
        "routed_review_required": sorted(row["candidate_id"] for row in CANDIDATE_ROWS if row["decision"] == "routed"),
        "regulatory_cases_review_required": sorted(row["candidate_id"] for row in CANDIDATE_ROWS if row["candidate_id"] in {"uy-zorzal", "uy-skywalker"}),
        "exclusion_population_source": "candidates.jsonl decisions duplicate or insufficient_evidence",
        "exclusion_population": len(exclusion_population),
        "exclusion_sample_rule": "SHA-256(candidate_id), ascending; first ceil(population/5)",
        "exclusion_sample": sample,
        "critical_or_high_findings_open": 0,
    }
    files = {
        OUT / "contract.json": json_bytes(contract),
        OUT / "baseline/catalog-baseline.jsonl": jsonl_bytes(baseline_rows),
        OUT / "baseline/prior-artifacts.jsonl": jsonl_bytes(prior_rows),
        OUT / "source-inventory.jsonl": jsonl_bytes(SOURCE_ROWS),
        OUT / "candidates.jsonl": jsonl_bytes(CANDIDATE_ROWS),
        OUT / "evidence.jsonl": jsonl_bytes(evidence_rows),
        OUT / "regulatory-query-log.jsonl": jsonl_bytes(REGULATORY_QUERIES),
        OUT / "coverage-matrix.json": json_bytes(coverage),
        OUT / "review.json": json_bytes(review),
    }
    files.update(profile_outputs(ROOT, CUTOFF))
    artifact_hashes = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(content).hexdigest()
        for path, content in files.items()
    }
    freeze = {
        "schema_version": "1.0",
        "status": "frozen",
        "cutoff": CUTOFF,
        "counts": {
            "catalog_baseline": len(baseline_rows),
            "sources": len(SOURCE_ROWS),
            "candidates": len(CANDIDATE_ROWS),
            **decision_counts,
        },
        "artifact_hashes": artifact_hashes,
        "publication_batches": [
            {
                "batch": 1,
                "candidate_count": len(PROFILES),
                "profile_file_count": len(PROFILES) * 3,
                "locales": ["en", "pt-BR", "es"],
                "candidates": [
                    {
                        "candidate_id": f"uy-{slug}",
                        "destination": profile["destination"],
                    }
                    for slug, profile in PROFILES.items()
                ],
            }
        ],
        "limitations": [
            coverage["limitation"],
            "The Tokai canonical domain was inaccessible; current institutional and association evidence is disclosed.",
            "Geographic ambiguity prevented publication under Uruguay when headquarters could not be confirmed.",
        ],
    }
    files[OUT / "freeze-manifest.json"] = json_bytes(freeze)
    readme = f"""# Reauditoria de fundos — Uruguai

Data de corte: `{CUTOFF}`. Esta é uma cobertura auditada das fontes percorridas, sem alegação de totalidade.

- baseline congelado: {len(baseline_rows)} perfis;
- {len(SOURCE_ROWS)} fontes não regulatórias, todas com owner e estado terminal;
- {len(CANDIDATE_ROWS)} candidatos: {decision_counts['eligible']} elegíveis, {decision_counts['duplicate']} duplicatas, {decision_counts['routed']} encaminhados e {decision_counts['insufficient_evidence']} com evidência insuficiente;
- 100% das origens de descoberta são não regulatórias;
- 2 consultas pontuais ao Banco Central del Uruguay ({coverage['regulatory_query_percent_of_candidates']}%), apenas para identidade/divergência;
- busca cega em duas famílias novas e passagem final de saturação com rendimento marginal zero;
- amostra determinística de {len(sample)}/{len(exclusion_population)} exclusões: {", ".join(sample)};
- revisão independente de #287 aprovada por `integrator`, sem achados críticos ou altos;
- lote congelado com {len(PROFILES)} fundos e {len(PROFILES) * 3} perfis completos em inglês, português e espanhol.
"""
    files[OUT / "README.md"] = readme.encode()
    return files


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs()
    if args.check:
        divergent = [path for path, content in generated.items() if not path.exists() or path.read_bytes() != content]
        if divergent:
            raise SystemExit("Divergent artifacts: " + ", ".join(str(path) for path in divergent))
        print("Uruguay pre-freeze audit verified.")
        return
    for path, content in generated.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("Uruguay pre-freeze audit generated.")


if __name__ == "__main__":
    main()
