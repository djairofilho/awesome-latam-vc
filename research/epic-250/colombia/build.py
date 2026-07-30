#!/usr/bin/env python3
"""Build the reproducible Colombia fund re-audit artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8", newline="\n")


def dump_json(path: Path, value: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


sources = [
    ("src-bogota-capital-2025", "round_map", "https://bogota.gov.co/sites/default/files/inline-files/_%20ESP%20LEVANTAMIENTO_CAPITAL_2025.pdf", "Investor ranking and 2025 Bogotá funding rounds", 4),
    ("src-kpmg-tech-report", "sector_map", "https://assets.kpmg.com/content/dam/kpmgsites/co/pdf/2026/01/colombia-tech-report-25-26.pdf", "33 active investors and Colombia market signals", 3),
    ("src-colcapital-report", "industry_association", "https://colcapital.org/estudio-de-la-industria-2026/", "2025-2026 private-capital industry report", 4),
    ("src-colcapital-members", "industry_association", "https://colcapital.org/wp-content/uploads/2025/02/Binder2.pdf", "Capital Emprendedor member roster", 6),
    ("src-bancoldex-simma", "institutional_allocator", "https://www.bancoldex.com/es/noticias/bancoldex-y-ruta-n-invierten-en-simma-fintech", "Allocator commitment to Simma Fintech +", 1),
    ("src-medellin-microvc", "public_allocator", "https://www.medellin.gov.co/es/sala-de-prensa/noticias/por-primera-vez-el-distrito-y-ruta-n-hacen-inversion-por-5-000-millones-en-fondo-para-fortalecer-el-capital-emprendedor/", "MicroVC program and four Colombian manager teams", 2),
    ("src-pacific-launch", "regional_news", "https://forbes.co/emprendedores/pacific-ventures-nuevo-fondo-de-inversion-angel-cali", "Launch of an angel investment vehicle in Cali", 1),
    ("src-pacific-activity", "regional_ecosystem", "https://www.ccc.org.co/pacific-ventures-impulsa-la-inversion-en-startups-desde-el-valle-del-cauca/", "First-year investment activity", 1),
    ("src-startuplinks-colombia", "independent_map", "https://www.startuplinks.world/reportes/inversionistas-de-venture-capital-originarios-de-colombia", "Independent Colombia-origin investor map", 5),
    ("src-marathon-official", "official_portfolio", "https://www.marathonvc.com/", "Current thesis, team, portfolio and founder route", 1),
    ("src-simma-official", "official_portfolio", "https://www.simmacapital.com/", "Current strategies, Colombia angel fund and portfolio", 1),
    ("src-rockstart-official", "official_portfolio", "https://rockstart.com/portfolio/", "Current accelerator-linked funds and dated portfolio", 1),
    ("src-vertical-official", "official_portfolio", "https://vertical-p.com/our-companies/", "Mixed direct companies and fund holdings", 1),
    ("src-sec-h20-identity", "regulator_identity", "https://reports.adviserinfo.sec.gov/reports/ADV/335430/PDF/335430.pdf", "Identity-only check for H20 Capital Innovation II, LP", 0),
    ("src-blind-abseed", "blind_fund_launch", "https://gentyrecruitment.io/news/abseed-launches-197m-evergreen-fund-colombia", "Blind-search report of ABSeed Colombia expansion", 1),
]
source_rows = [
    {
        "schema_version": "1.0",
        "source_id": sid,
        "family": family,
        "url": url,
        "scope": scope,
        "accessed_on": CUTOFF,
        "result": "complete",
        "new_names_observed": found,
        "owner": "colombia-worker",
    }
    for sid, family, url, scope, found in sources
]

candidates = [
    ("simma-capital", "Simma Capital", "simmacapital.com", ["src-colcapital-members", "src-bancoldex-simma"], "eligible", None, "Official site and Bancóldex confirm direct early-stage funds, a current portfolio and Colombian access."),
    ("marathon-ventures", "Marathon Ventures", "marathonvc.com", ["src-startuplinks-colombia", "src-marathon-official"], "eligible", None, "Official site confirms earliest-stage direct investing, a current portfolio, team and founder route."),
    ("amberes-ventures", "Amberes Ventures", "amberesventures.com", ["src-startuplinks-colombia"], "insufficient_evidence", None, "Official site confirms the seed vehicle, but no dated activity within the audit window was found."),
    ("inqlab", "InQlab", "inqlab.co", ["src-colcapital-members"], "insufficient_evidence", None, "Official portfolio remains dated through 2023; current recurring activity was not established."),
    ("h20-capital-innovation", "H20 Capital Innovation", "h20capital.com", ["src-colcapital-members"], "insufficient_evidence", None, "The identity was resolved in a regulatory filing, but current Colombia access and official activity were not established."),
    ("vertical-partners", "Vertical Partners", "vertical-p.com", ["src-colcapital-members", "src-vertical-official"], "insufficient_evidence", None, "Official material mixes fund holdings, ecosystem services and direct companies without a sufficiently clear recurring startup mandate."),
    ("flink-ventures", "Flink Ventures", "flink.co", ["src-colcapital-members"], "insufficient_evidence", None, "Discovery sources describe a manager, but no current official direct-investment thesis and portfolio were found."),
    ("pacific-ventures-cali", "Pacific Ventures", None, ["src-pacific-launch", "src-pacific-activity"], "routed", "angel_network", "The vehicle is explicitly organized as an angel investment fund and belongs in the angel audit."),
    ("rockstart", "Rockstart", "rockstart.com", ["src-colcapital-members", "src-rockstart-official"], "routed", "accelerator", "Investment funds operate together with the accelerator; route to the accelerator audit to avoid split identity."),
    ("medellin-venture-capital", "Medellín Venture Capital", None, ["src-medellin-microvc"], "routed", "public_program", "This is a public allocator/program selecting managers, not a direct startup fund."),
    ("abseed", "ABSeed", "abseed.com.br", ["src-blind-abseed"], "duplicate", "funds/brazil/a.b.seed-ventures.md", "Existing canonical fund; the Colombia launch changes reach but does not create a new identity."),
    ("entrypoint", "Entrypoint", "entrypoint.one", ["src-kpmg-tech-report"], "duplicate", "funds/brazil/entrypoint.md", "Already present in the current baseline through commit 5b3a4e0; excluded from publication."),
    ("flourish-ventures", "Flourish Ventures", "flourishventures.com", ["src-bogota-capital-2025"], "duplicate", "funds/multi-country/flourish-ventures.md", "Already present in the current baseline through commit 5b3a4e0; excluded from publication."),
]
candidate_rows = [
    {
        "schema_version": "1.0",
        "candidate_id": f"co-{cid}",
        "name": name,
        "canonical_domain": domain,
        "discovery_source_ids": discovered,
        "discovery_origin": "non_regulatory",
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "cutoff": CUTOFF,
    }
    for cid, name, domain, discovered, decision, destination, reason in candidates
]

evidence_rows = [
    {
        "schema_version": "1.0",
        "candidate_id": row["candidate_id"],
        "decision": row["decision"],
        "source_ids": row["discovery_source_ids"]
        + (["src-sec-h20-identity"] if row["candidate_id"] == "co-h20-capital-innovation" else []),
        "gates": {
            "identity": "resolved",
            "direct_investment": "confirmed" if row["decision"] == "eligible" else "not_sufficiently_confirmed",
            "recurrence": "confirmed" if row["decision"] == "eligible" else "not_sufficiently_confirmed",
            "recent_activity": "confirmed" if row["decision"] == "eligible" else "not_sufficiently_confirmed",
            "market_access": "confirmed" if row["decision"] == "eligible" else "not_sufficiently_confirmed",
        },
        "reason": row["reason"],
    }
    for row in candidate_rows
]

contract = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "market": "CO",
    "eligible_gates": ["direct_investment", "recurrence", "recent_activity", "market_access", "official_evidence"],
    "discovery_rule": "non_regulatory_only",
    "regulator_rule": "identity_or_divergence_only",
    "regulator_ceiling_percent": 10,
    "excluded_discovery_inputs": ["local_startup_dataset", "regulatory_registry", "existing_catalog"],
    "publication_batch_limit": 10,
    "required_locales": ["en", "pt-BR", "es"],
}

new_profiles = {
    "funds/colombia/marathon-ventures.md",
    "funds/colombia/simma-capital.md",
}
profiles = [
    path
    for path in sorted(ROOT.glob("funds/**/*.md"))
    if path.relative_to(ROOT).as_posix() not in new_profiles
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
        "source": prior_path.relative_to(ROOT).as_posix(),
        "sha256": digest(prior_path),
        "record_count": sum(1 for line in prior_path.read_text(encoding="utf-8").splitlines() if line),
        "classification": "historical_baseline_not_discovery",
    }
]

dump_json(OUT / "contract.json", contract)
dump_jsonl(OUT / "baseline/catalog-baseline.jsonl", baseline_rows)
dump_jsonl(OUT / "baseline/prior-candidates.jsonl", prior_rows)
dump_jsonl(OUT / "source-inventory.jsonl", source_rows)
dump_jsonl(OUT / "candidates.jsonl", candidate_rows)
dump_jsonl(OUT / "evidence.jsonl", evidence_rows)

non_reg_discovery = sum(1 for row in candidate_rows if row["discovery_origin"] == "non_regulatory")
reg_queries = sum(1 for row in source_rows if row["family"] == "regulator_identity")
coverage = {
    "cutoff": CUTOFF,
    "canonical_candidates": len(candidate_rows),
    "non_regulatory_discovery_count": non_reg_discovery,
    "non_regulatory_discovery_percent": round(100 * non_reg_discovery / len(candidate_rows), 1),
    "regulatory_queries": reg_queries,
    "regulatory_query_percent_of_candidates": round(100 * reg_queries / len(candidate_rows), 1),
    "family_yield": [
        {"family": family, "sources_walked": sum(1 for row in source_rows if row["family"] == family), "observed_names": sum(row["new_names_observed"] for row in source_rows if row["family"] == family)}
        for family in sorted({row["family"] for row in source_rows})
    ],
    "marginal_passes": [
        {"pass": 1, "families": ["round_map", "sector_map", "industry_association"], "new_canonical_candidates": 8, "cumulative": 8},
        {"pass": 2, "families": ["institutional_allocator", "regional_news", "official_portfolio"], "new_canonical_candidates": 4, "cumulative": 12},
        {"pass": 3, "families": ["blind_fund_launch", "independent_map"], "new_canonical_candidates": 1, "cumulative": 13},
    ],
    "limitation": "Audited coverage of the walked sources; not a claim of absolute market completeness.",
}
dump_json(OUT / "coverage-matrix.json", coverage)

excluded = sorted(row["candidate_id"] for row in candidate_rows if row["decision"] == "insufficient_evidence")
sample_size = max(1, (len(excluded) + 4) // 5)
review = {
    "reviewer": "integrator",
    "reviewed_on": CUTOFF,
    "method": "SHA-256 lexical order over candidate_id; first ceil(20%) exclusions",
    "blind_families": ["blind_fund_launch", "independent_map"],
    "blind_finding": "ABSeed Colombia expansion",
    "blind_resolution": "duplicate of funds/brazil/a.b.seed-ventures.md",
    "eligible_reviewed": sorted(row["candidate_id"] for row in candidate_rows if row["decision"] == "eligible"),
    "routed_reviewed": sorted(row["candidate_id"] for row in candidate_rows if row["decision"] == "routed"),
    "regulatory_cases_reviewed": ["co-h20-capital-innovation"],
    "exclusion_sample": sorted(excluded, key=lambda value: hashlib.sha256(value.encode()).hexdigest())[:sample_size],
    "critical_or_high_findings_open": 0,
}
dump_json(OUT / "review.json", review)

eligible_profiles = [
    "funds/colombia/marathon-ventures.md",
    "funds/colombia/simma-capital.md",
]
publication = {
    "cutoff": CUTOFF,
    "eligible_count": len(eligible_profiles),
    "batch_limit": 10,
    "batch_count": 1,
    "batches": [{"batch_id": "co-funds-01", "profiles": eligible_profiles}],
    "locales": ["en", "pt-BR", "es"],
}
dump_json(OUT / "publication/publication-manifest.json", publication)

tracked = [
    OUT / "contract.json",
    OUT / "baseline/catalog-baseline.jsonl",
    OUT / "baseline/prior-candidates.jsonl",
    OUT / "source-inventory.jsonl",
    OUT / "candidates.jsonl",
    OUT / "evidence.jsonl",
    OUT / "coverage-matrix.json",
    OUT / "review.json",
    OUT / "publication/publication-manifest.json",
]
freeze = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "counts": {
        "catalog_baseline": len(baseline_rows),
        "candidates": len(candidate_rows),
        "eligible": 2,
        "insufficient_evidence": sum(row["decision"] == "insufficient_evidence" for row in candidate_rows),
        "routed": sum(row["decision"] == "routed" for row in candidate_rows),
        "duplicates": sum(row["decision"] == "duplicate" for row in candidate_rows),
    },
    "artifact_hashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in tracked},
    "limitations": [
        "The audit covers the enumerated public sources, not every possible fund in Colombia.",
        "Inaccessible or undated sources remain explicit evidence gaps.",
        "Regulatory material was used once, only to resolve H20 identity.",
    ],
}
dump_json(OUT / "freeze-manifest.json", freeze)

profile_hashes = {}
for profile in eligible_profiles:
    for localized in [
        profile,
        f"translations/pt-BR/{profile}",
        f"translations/es/{profile}",
    ]:
        path = ROOT / localized
        if path.exists():
            profile_hashes[localized] = digest(path)
audit = {
    "reviewer": "integrator",
    "reviewed_on": CUTOFF,
    "cutoff": CUTOFF,
    "published_eligible_count": len(eligible_profiles),
    "expected_profile_files": len(eligible_profiles) * 3,
    "profile_hashes": profile_hashes,
    "non_regulatory_discovery_percent": coverage["non_regulatory_discovery_percent"],
    "regulatory_query_percent_of_candidates": coverage["regulatory_query_percent_of_candidates"],
    "batch_limit_respected": all(len(batch["profiles"]) <= 10 for batch in publication["batches"]),
    "absolute_completeness_claimed": False,
}
dump_json(OUT / "publication/final-audit.json", audit)
