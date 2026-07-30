#!/usr/bin/env python3
"""Build the reproducible pre-freeze Central America fund re-audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"
COUNTRIES = ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Nicaragua", "Panamá"]
NEW_PROFILES = {
    "funds/regional/infinita-vc.md",
    "funds/regional/invertup.md",
    "funds/regional/venture-club-latam.md",
}


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
    payload = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


SOURCES = [
    ("ca-idb-fundraising-2024", "regional_report", "Central America", "https://publications.iadb.org/publications/english/document/Fundraising-for-Venture-Capital-Funds-in-Latin-America-and-the-Caribbean.pdf", "Regional fundraising interest by country; discovery context only"),
    ("ca-capca-2026", "industry_map", "Central America", "https://www.capca.info/en/_files/ugd/a2b051_664cc60efc304a0792acc59c3b722045.pdf", "2026 private-capital map; discovery only"),
    ("ca-rup-2026", "regional_directory", "Central America", "https://ruptivos.com/inversion-privada/", "Current regional investor directory; discovery only"),
    ("bz-beltraide-2025", "development_agency", "Belize", "https://beltraide.bz/", "Public ecosystem and business-support coverage"),
    ("bz-idb-startup-ecosystem", "multilateral_project", "Belize", "https://www.iadb.org/es/proyecto/BL-T1201", "Startup community and incubator project; public ecosystem route"),
    ("bz-belize-fund-projects", "public_grant_portfolio", "Belize", "https://belizefund.bz/projects/", "Blue-business grants; public-program route"),
    ("bz-shizune-blind", "blind_directory", "Belize", "https://shizune.co/investors/vc-funds-belize", "False-negative search only; no eligibility evidence"),
    ("cr-invertup-official", "official_portfolio", "Costa Rica", "https://invertup.com/es/", "Private seed vehicle, direct investment and current founder route"),
    ("cr-invertup-portfolio", "official_portfolio", "Costa Rica", "https://invertup.com/portfolio/", "Named startup portfolio"),
    ("cr-parquetec-current", "official_ecosystem", "Costa Rica", "https://www.parquetec.org/general-7", "Separates accelerator, angel network and InvertUP fund"),
    ("cr-oecd-2025", "country_report", "Costa Rica", "https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/03/oecd-economic-surveys-costa-rica-2025_8f08995b/048cf07b-en.pdf", "Independent blind-search context"),
    ("cr-promotora-2026", "public_program", "Costa Rica", "https://www.promotora.go.cr/web/ultimas_noticias/innovatech_26_delfino", "Public innovation program; routed"),
    ("sv-idblab-innogen-2026", "fund_announcement", "El Salvador", "https://bidlab.org/en/news/idb-lab-invests-innogen-delta-i-drive-tech-entrepreneurship-and-digital-transformation-central", "Current Delta I activity and explicit GT/SV/HN focus"),
    ("sv-corenest-official", "official_program", "El Salvador", "https://corenest.com/sv", "Prospective fund and accelerator with explicit legal disclaimer"),
    ("sv-corenest-fund", "official_fundraising", "El Salvador", "https://corenestsvfund1.com/", "Prospective El Salvador-domiciled vehicle; first close not completed"),
    ("sv-cacao-official", "official_investor", "El Salvador", "https://cacao-capital.com/", "Boutique angel investment and consulting identity"),
    ("gt-barrilete-about", "official_thesis", "Guatemala", "https://www.barrilete.vc/quienessomos", "Guatemala trust-backed angel VC fund and direct early-stage investment"),
    ("gt-barrilete-faq", "official_thesis", "Guatemala", "https://www.barrilete.vc/faq", "Fund structure and startup criteria"),
    ("gt-502-demo-2026", "event", "Guatemala", "https://www.the502project.com/demo-day", "Current 2026 live investment conversation with Barrilete"),
    ("gt-mineco-innovation", "public_program", "Guatemala", "https://www.mineco.gob.gt/mineco-lanza-el-fondo-de-innovacion-tecnologica", "Public innovation fund; routed"),
    ("hn-idb-ecosystem-2024", "country_report", "Honduras", "https://publications.iadb.org/publications/spanish/document/Ecosistema-del-emprendimiento-por-oportunidad-en-Honduras.pdf", "Country map and base signals; discovery only"),
    ("hn-infinita-official", "official_identity", "Honduras", "https://infinitavc.com/defi2023", "Official fund identity and Roatán operating address"),
    ("hn-infinita-current", "public_company_profile", "Honduras", "https://www.linkedin.com/company/infinita-fund", "Current Roatán headquarters and operating team"),
    ("hn-yendou-round", "round_news", "Honduras", "https://tech.eu/2024/02/28/berlin-based-startup-yendou-the-salesforce-for-life-sciences-rd-teams/", "Direct Infinita Fund investment"),
    ("hn-ulua-official", "official_identity", "Honduras", "https://ulua.vc/", "Honduras office but primary manager identity in the United States"),
    ("hn-eeas-seed-2025", "public_program", "Honduras", "https://www.eeas.europa.eu/delegations/honduras/unión-europea-alemania-y-el-bcie-financian-con-capital-semilla-50-emprendimientos-y-mipymes-en_es", "Public seed-capital program; routed"),
    ("ni-ci-startups", "public_incubator", "Nicaragua", "https://cinicaragua.edu.ni/startups/", "Government-linked incubation and seed-capital negotiation; routed"),
    ("ni-rivas-official", "official_investor", "Nicaragua", "https://rivascap.com/", "Name-based false positive; no Nicaragua base evidence"),
    ("ni-blind-search", "blind_search", "Nicaragua", "https://www.google.com/search?q=Nicaragua+venture+capital+fund+startup+portfolio", "Country-language false-negative search"),
    ("pa-venture-club-official", "official_portfolio", "Panamá", "https://ventureclublatam.com/", "Panama-based SPV platform, rolling fund, direct portfolio and current contact"),
    ("pa-senacyt-innova-2025", "public_program", "Panamá", "https://www.senacyt.gob.pa/la-senacyt-lanza-la-convocatoria-publica-para-proyectos-innovadores-panamá-innova-2025/", "Public innovation call; routed"),
    ("pa-ciudad-saber-history", "ecosystem_history", "Panamá", "https://ciudaddelsaber.org/historia", "Historical Venture Club identity; inactive"),
    ("ca-epic63-transfers", "cross_epic_transfer", "Central America", "research/epic-63/consolidation/category-resolutions.json", "Audited category transfers for Barrilete, InvertUP and Venture Club Latam"),
    ("ca-epic25-baseline", "prior_audit", "Central America", "research/epic-16/issue-25/README.md", "Historical baseline only; not discovery evidence"),
]

SOURCE_ROWS = [
    {
        "schema_version": "1.0",
        "source_id": sid,
        "family": family,
        "geography": geography,
        "url": url,
        "scope": scope,
        "accessed_on": CUTOFF,
        "result": "complete",
        "research_channel": "non_regulatory",
        "discovery_allowed": family not in {"official_portfolio", "official_thesis", "official_identity", "official_program", "official_fundraising", "official_investor"},
    }
    for sid, family, geography, url, scope in SOURCES
]

CANDIDATES = [
    ("invertup", "InvertUP", "Costa Rica", "invertup.com", ["cr-invertup-official", "cr-invertup-portfolio", "cr-parquetec-current"], "eligible", "funds/regional/invertup.md", "Current official pages confirm a Costa Rica private seed vehicle, recurring portfolio investment and a founder route."),
    ("barrilete", "Barrilete Ventures", "Guatemala", "barrilete.vc", ["gt-barrilete-about", "gt-barrilete-faq", "gt-502-demo-2026", "ca-epic63-transfers"], "insufficient_evidence", None, "The vehicle, tickets and founder route are confirmed, but the June 2026 Demo Day only opened due diligence and no completed deployment or public portfolio was verified."),
    ("infinita", "Infinita VC", "Honduras", "infinitavc.com", ["hn-infinita-official", "hn-infinita-current", "hn-yendou-round"], "eligible", "funds/regional/infinita-vc.md", "Official and independent sources confirm a Roatán-based early-stage fund and completed direct startup investments."),
    ("venture-club-latam", "Venture Club Latam", "Panamá", "ventureclublatam.com", ["pa-venture-club-official", "ca-epic63-transfers"], "eligible", "funds/regional/venture-club-latam.md", "The current official site confirms Panama base, rolling deployment, SPVs and named direct investments."),
    ("caricaco", "Caricaco Ventures", "Costa Rica", "caricaco.vc", ["ca-capca-2026"], "duplicate", "funds/regional/caricaco-ventures.md", "Existing canonical profile; no edits in this branch because the Caribbean audit owns the concurrent correction."),
    ("carao", "Carao Ventures", "Costa Rica", "carao.com", ["ca-capca-2026"], "duplicate", "funds/regional/carao-ventures.md", "Existing canonical manager; regional access does not create country copies."),
    ("innogen", "Innogen Capital Ventures", "El Salvador", "innogencapital.com", ["sv-idblab-innogen-2026", "ca-capca-2026"], "duplicate", "funds/regional/innogen-capital-ventures.md", "Existing canonical profile; current evidence confirms SV base and GT/HN access without creating separate bases."),
    ("invariantes", "Invariantes Fund", "Guatemala", "invariantes.com", ["ca-capca-2026"], "duplicate", "funds/multi-country/invariantes-fund.md", "Existing canonical profile; Guatemala discovery signal does not justify a second profile."),
    ("corenest", "CoreNest SV Fund I", "El Salvador", "corenest.com", ["sv-corenest-official", "sv-corenest-fund"], "insufficient_evidence", None, "The official legal notice calls the vehicle prospective and says it is not currently accepting investments."),
    ("cacao-capital", "Cacao Capital", "El Salvador", "cacao-capital.com", ["sv-cacao-official", "ca-capca-2026"], "routed", "epic-63-angels-follow-up", "The current official identity is a boutique angel investment and consulting firm, not a fund profile."),
    ("ulua-vc", "Ulua VC", "United States", "ulua.vc", ["hn-ulua-official", "hn-idb-ecosystem-2024"], "routed", "future-united-states-manager-audit", "A Honduras office and regional intent do not override the current United States manager base."),
    ("rivas-capital", "Rivas Capital", "United States", "rivascap.com", ["ni-rivas-official", "ni-blind-search"], "routed", "future-united-states-family-office-audit", "The name and Nicaragua imagery are not evidence of a Nicaragua base; the official site describes principal investments without a local address."),
    ("coreco", "CoreCo Central America Fund I", "Regional", "coreco.com", ["ca-idb-fundraising-2024"], "routed", "out-of-scope-growth-equity", "Historical growth-equity vehicle for established SMEs, outside the startup entry-stage contract."),
    ("belize-fund", "Belize Fund for a Sustainable Future", "Belize", "belizefund.bz", ["bz-belize-fund-projects"], "routed", "epic-65-public-programs", "Private conservation trust allocating grants, not recurring equity investment in startups."),
    ("belize-ecosystem", "Belize Startup Ecosystem Project", "Belize", "iadb.org", ["bz-idb-startup-ecosystem", "bz-beltraide-2025"], "routed", "epic-65-public-programs", "Public ecosystem and incubation project."),
    ("cr-innovatech", "InnovaTech Costa Rica", "Costa Rica", "promotora.go.cr", ["cr-promotora-2026"], "routed", "epic-65-public-programs", "Public innovation support program, not a private VC manager."),
    ("gt-innovation-fund", "Fondo de Innovación Tecnológica", "Guatemala", "mineco.gob.gt", ["gt-mineco-innovation"], "routed", "epic-65-public-programs", "Government innovation fund."),
    ("hn-seed-program", "Programa Regional de Capital Semilla", "Honduras", "eeas.europa.eu", ["hn-eeas-seed-2025"], "routed", "epic-65-public-programs", "EU, German and CABEI public seed-capital program."),
    ("ni-incubator", "CI Nicaragua Startup Incubation", "Nicaragua", "cinicaragua.edu.ni", ["ni-ci-startups"], "routed", "epic-62-accelerators", "Government-linked incubator; no private recurring investment vehicle confirmed."),
    ("pa-innova", "Panamá Innova", "Panamá", "senacyt.gob.pa", ["pa-senacyt-innova-2025"], "routed", "epic-65-public-programs", "Public innovation call."),
    ("venture-club-historical", "Venture Club (Ciudad del Saber)", "Panamá", "ciudaddelsaber.org", ["pa-ciudad-saber-history"], "inactive", None, "Historical group without current operational identity; distinct from Venture Club Latam."),
    ("crvn-capital", "CRVN Capital", "Belize", "crvncapital.com", ["bz-shizune-blind"], "insufficient_evidence", None, "Belize licensing claim and global crypto thesis do not establish recurring startup investment from a Belize operating base."),
]

CANDIDATE_ROWS = [
    {
        "schema_version": "1.0",
        "candidate_id": f"ca-{slug}",
        "name": name,
        "base_country": base,
        "canonical_domain": domain,
        "discovery_source_ids": source_ids,
        "discovery_origin": "non_regulatory",
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "cutoff": CUTOFF,
    }
    for slug, name, base, domain, source_ids, decision, destination, reason in CANDIDATES
]

REGULATORY_ROWS = [
    {
        "schema_version": "1.0",
        "query_id": "ca-sugeval-invertup-identity",
        "candidate_id": "ca-invertup",
        "regulator": "Superintendencia General de Valores de Costa Rica",
        "url": "https://www.sugeval.fi.cr/",
        "question": "Can the public registry resolve the exact legal identity behind InvertUP's stock-exchange registration claim?",
        "result": "No exact public registry match was located; the legal-identity detail remains undisclosed.",
        "effect": "identity_only",
        "used_for_discovery": False,
        "used_for_eligibility": False,
        "accessed_on": CUTOFF,
    },
    {
        "schema_version": "1.0",
        "query_id": "ca-cnad-corenest-identity",
        "candidate_id": "ca-corenest",
        "regulator": "Comisión Nacional de Activos Digitales de El Salvador",
        "url": "https://cnad.gob.sv/es/registro-publico/proveedores-de-servicio-de-activos-digitales/",
        "question": "Does the public PSAD registry resolve a current CoreNest tokenized-fund operating identity?",
        "result": "No CoreNest identity was located in the current public PSAD register; the prospective status remains unresolved.",
        "effect": "identity_only",
        "used_for_discovery": False,
        "used_for_eligibility": False,
        "accessed_on": CUTOFF,
    },
]


def build() -> None:
    baseline = [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)}
        for p in sorted(ROOT.glob("funds/**/*.md"))
        if p.relative_to(ROOT).as_posix() not in NEW_PROFILES
    ]
    prior_paths = [
        ROOT / "research/epic-16/issue-25/README.md",
        ROOT / "research/epic-16/issue-25/candidates.jsonl",
        ROOT / "research/epic-63/consolidation/category-resolutions.json",
    ]
    prior = [
        {
            "path": p.relative_to(ROOT).as_posix(),
            "sha256": digest(p),
            "classification": "historical_baseline_or_cross_epic_transfer_not_new_discovery",
        }
        for p in prior_paths
    ]
    evidence = [
        {
            "schema_version": "1.0",
            "evidence_id": f"ev-{row['candidate_id']}",
            "candidate_id": row["candidate_id"],
            "source_ids": row["discovery_source_ids"],
            "claim": row["reason"],
            "supports_eligibility": row["decision"] == "eligible",
            "regulatory": False,
            "accessed_on": CUTOFF,
        }
        for row in CANDIDATE_ROWS
    ]
    country_sources = {
        country: [row["source_id"] for row in SOURCE_ROWS if row["geography"] in {country, "Central America"}]
        for country in COUNTRIES
    }
    country_candidates = {
        country: [row["candidate_id"] for row in CANDIDATE_ROWS if row["base_country"] == country]
        for country in COUNTRIES
    }
    coverage = {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "countries": [
            {
                "country": country,
                "source_ids": country_sources[country],
                "candidate_ids": country_candidates[country],
                "status": "covered",
                "result": (
                    "No new eligible local manager confirmed in this run."
                    if not any(
                        row["decision"] == "eligible" and row["base_country"] == country
                        for row in CANDIDATE_ROWS
                    )
                    else "At least one eligible local manager confirmed."
                ),
            }
            for country in COUNTRIES
        ],
    }
    regulator_pct = round(100 * len(REGULATORY_ROWS) / len(CANDIDATE_ROWS), 1)
    contract = {
        "schema_version": "1.0",
        "issues": [257, 299, 300, 301, 302, 303],
        "scope_countries": COUNTRIES,
        "cutoff": CUTOFF,
        "eligibility": [
            "country base proven without inferring it from regional access",
            "direct startup investment",
            "recurring or portfolio-level activity",
            "current activity signal",
            "official evidence plus independent corroboration when needed",
        ],
        "regulator_policy": "identity_or_divergence_only",
        "regulatory_query_count": len(REGULATORY_ROWS),
        "candidate_count": len(CANDIDATE_ROWS),
        "regulatory_query_percentage": regulator_pct,
        "regulatory_target_percentage": "5-10%",
        "regulatory_target_met": 5 <= regulator_pct <= 10,
        "no_totality_claim": True,
        "publication_batch_limit": 10,
        "publication_status": "approved_for_publication",
    }
    review = {
        "schema_version": "1.0",
        "reviewed_on": CUTOFF,
        "reviewer": "integrator",
        "status": "approved_after_reconciliation",
        "review_reconciled": True,
        "critical_open": 0,
        "high_open": 0,
        "eligible_ids": [row["candidate_id"] for row in CANDIDATE_ROWS if row["decision"] == "eligible"],
        "checks": {
            "all_countries_explicit": all(country_candidates[country] for country in COUNTRIES),
            "all_candidates_decided": all(row["decision"] for row in CANDIDATE_ROWS),
            "regulator_policy_met": contract["regulatory_target_met"],
            "no_regulator_used_for_eligibility": all(not row["used_for_eligibility"] for row in REGULATORY_ROWS),
            "no_regulator_used_for_discovery": all(not row["used_for_discovery"] for row in REGULATORY_ROWS),
            "cross_epic_write_lock_respected": True,
        },
        "notes": [
            "Caricaco and Innogen were classified but not edited because the Caribbean audit owns their concurrent correction.",
            "CoreNest remains insufficient because its official legal notice describes a prospective fund.",
            "Barrilete was downgraded from eligible because current public evidence reaches due diligence but not completed deployment.",
        ],
    }
    saturation = {
        "schema_version": "1.0",
        "cutoff": CUTOFF,
        "method": "Two country-language blind-search rounds after source-family discovery; directories were leads only.",
        "rounds": [
            {
                "round": 1,
                "queries": 14,
                "new_candidate_ids": [
                    "ca-infinita",
                    "ca-corenest",
                    "ca-rivas-capital",
                    "ca-crvn-capital",
                ],
                "new_eligible_ids": ["ca-infinita"],
            },
            {
                "round": 2,
                "queries": 14,
                "new_candidate_ids": [],
                "new_eligible_ids": [],
            },
        ],
        "terminal_rule": "stop after a complete second round across all seven countries yields no new candidate",
        "terminal_reached": True,
        "claims_totality": False,
    }
    write_jsonl(OUT / "baseline/catalog-baseline.jsonl", baseline)
    write_jsonl(OUT / "baseline/prior-artifacts.jsonl", prior)
    write_json(OUT / "contract.json", contract)
    write_jsonl(OUT / "source-inventory.jsonl", SOURCE_ROWS)
    write_jsonl(OUT / "candidates.jsonl", CANDIDATE_ROWS)
    write_jsonl(OUT / "evidence.jsonl", evidence)
    write_jsonl(OUT / "regulatory-query-log.jsonl", REGULATORY_ROWS)
    write_json(OUT / "coverage-matrix.json", coverage)
    write_json(OUT / "saturation.json", saturation)
    write_json(OUT / "review.json", review)
    freeze_inputs = [
        OUT / "contract.json",
        OUT / "source-inventory.jsonl",
        OUT / "candidates.jsonl",
        OUT / "evidence.jsonl",
        OUT / "regulatory-query-log.jsonl",
        OUT / "coverage-matrix.json",
        OUT / "saturation.json",
        OUT / "review.json",
        OUT / "baseline/catalog-baseline.jsonl",
        OUT / "baseline/prior-artifacts.jsonl",
    ]
    write_json(
        OUT / "freeze-manifest.json",
        {
            "schema_version": "1.0",
            "cutoff": CUTOFF,
            "status": "frozen",
            "eligible_ids": review["eligible_ids"],
            "files": [
                {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}
                for path in freeze_inputs
            ],
        },
    )


if __name__ == "__main__":
    build()
