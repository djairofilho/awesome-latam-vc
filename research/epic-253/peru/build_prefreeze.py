#!/usr/bin/env python3
"""Build Peru audit artifacts up to the independent-review gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8", newline="\n")


contract = {
    "schema_version": "1.0",
    "market": "PE",
    "cutoff": CUTOFF,
    "gates": ["direct_investment", "recurrence", "recent_activity", "market_access", "official_evidence"],
    "discovery": "non_regulatory_only",
    "regulator": "identity_or_divergence_only",
    "regulator_target_percent": [5, 10],
    "forbidden_inputs": ["local_startup_dataset", "catalog_as_discovery", "regulator_as_discovery"],
    "review_gate": "independent_integrator_approval_required_before_freeze",
    "publication_batch_limit": 10,
    "locales": ["en", "pt-BR", "es"],
}

source_specs = [
    ("pecap-directory", "industry_directory", "https://www.pecap.pe/directorio", "Current member categories and fund roster", 11),
    ("pecap-2026", "sector_report", "https://www.pecap.pe/reportes-2026", "2026 barriers and opportunities reports", 3),
    ("cofide-2026", "institutional_allocator", "https://documentos.cofide.com.pe/wp-content/uploads/2026/02/NP-COFIDE-financiara-a-unas-85-startups-hasta-fin-de-ano.pdf", "Five selected VC funds and 70 portfolio startups", 4),
    ("caf-fcei", "institutional_allocator", "https://www.caf.com/es/actualidad/noticias/caf-impulsa-ecosistema-emprendedor-peruano-con-inversion-en-fondo-de-cofide/", "Allocator expansion of Peru's fund of funds", 1),
    ("gestion-alaya", "fund_news", "https://gestion.pe/economia/empresas/alaya-capital-prepara-nuevo-fondo-de-venture-capital-para-startups-con-foco-en-peru-noticia/", "2026 fund launch and Peru allocation", 1),
    ("produce-fcei", "public_allocator", "https://www.gob.pe/institucion/produce/noticias/1123782-produce-cofide-y-caf-fortalecen-la-inversion-en-emprendimientos-innovadores-en-el-peru", "FCEI manager-selection capacity", 2),
    ("startup-peru", "public_program", "https://www.gob.pe/institucion/proinnovate/noticias/1290934-mes-del-emprendimiento-startup-peru-impulso-el-talento-emprendedor-con-inversion-superior-a-s-190-millones-para-1160-proyectos-innovadores", "Seed-grant program activity", 1),
    ("impaqto-official", "official_portfolio", "https://www.impaqtocapital.com/es", "Andean impact thesis and current portfolio", 1),
    ("impaqto-close", "official_activity", "https://www.impaqtocapital.com/fund-i-final-close-announcement", "Fund I final close and six investments in 2025", 1),
    ("lucha-faq", "official_identity", "https://www.luchala.org/faq/", "Explicit statement that LUCHA has no direct fund", 1),
    ("capia-official", "official_identity", "https://www.capia.pe/", "Current investment-banking advisory activity", 1),
    ("smv-capia", "regulator_identity", "https://www.smv.gob.pe/ConsultasP8/temp/SAFI%20Comunicacion%20SMV%20CdV.pdf", "Identity/divergence check for CAPIA versus current advisory brand", 0),
    ("blind-axelya", "blind_venture_builder", "https://axelyalabs.com/", "Blind-search venture studio in Lima", 1),
    ("blind-shizune", "blind_investor_map", "https://shizune.co/investors/vc-funds-peru", "Blind-search investor vocabulary and false-negative check", 2),
]
sources = [
    {"schema_version": "1.0", "source_id": sid, "family": family, "url": url, "scope": scope, "accessed_on": CUTOFF, "result": "complete", "observed_names": count}
    for sid, family, url, scope, count in source_specs
]

candidate_specs = [
    ("impaqto-capital", "IMPAQTO Capital", "impaqtocapital.com", ["pecap-2026", "impaqto-official", "impaqto-close"], "eligible", None, "Official sources confirm a direct Andean impact fund, 2025 close, current portfolio and Peru investments."),
    ("lucha", "LUCHA", "luchala.org", ["pecap-directory", "lucha-faq"], "routed", "venture_builder", "Official FAQ states that LUCHA does not have a fund investing directly."),
    ("cofide-fcei", "FCEI", "cofide.com.pe", ["cofide-2026", "caf-fcei"], "routed", "public_program", "Fund of funds and public allocator, not a direct startup fund."),
    ("startup-peru", "StartUp Perú", "gob.pe", ["startup-peru"], "routed", "public_program", "Public seed-grant competition."),
    ("axelya-labs", "Axelya Labs", "axelyalabs.com", ["blind-axelya"], "routed", "venture_builder", "Official site identifies a venture studio building its own companies."),
    ("capia", "CAPIA", "capia.pe", ["pecap-2026", "capia-official"], "insufficient_evidence", None, "Current official site supports advisory activity, not a recurring direct VC mandate; SMV used only to resolve identity divergence."),
    ("confrapar", "Confrapar", "confrapar.com.br", ["pecap-directory"], "insufficient_evidence", None, "No current official Peru mandate or recent activity was established."),
    ("utec-ventures", "UTEC Ventures", "utecventures.com", ["pecap-directory"], "duplicate", "funds/regional/utec-ventures.md", "Existing canonical identity."),
    ("alaya-capital", "Alaya Capital", "alaya-capital.com", ["gestion-alaya"], "duplicate", "funds/argentina/alaya-capital.md", "Existing canonical identity; 2026 Peru allocation is an activity signal."),
    ("ithink-vc", "iThink VC", "ithink.vc", ["pecap-directory", "cofide-2026"], "duplicate", "funds/regional/ithink-vc.md", "Existing canonical identity."),
    ("winnipeg-capital", "Winnipeg Capital", "winnipegcapital.com", ["pecap-directory"], "duplicate", "funds/regional/winnipeg-capital.md", "Existing canonical identity."),
    ("b-venture-capital", "B Venture Capital", "bventure.capital", ["pecap-directory"], "duplicate", "funds/regional/b-venture-capital.md", "Existing canonical identity."),
    ("salkantay-ventures", "Salkantay Ventures", "salkantay.vc", ["pecap-directory", "cofide-2026"], "duplicate", "funds/regional/salkantay-ventures.md", "Existing canonical identity."),
    ("krealo", "Krealo", "krealo.pe", ["pecap-directory"], "duplicate", "funds/regional/krealo.md", "Existing canonical identity."),
    ("adn-vc", "ADN.VC", "adn.vc", ["pecap-directory"], "duplicate", "funds/multi-country/adn.vc.md", "Existing canonical identity."),
]
candidates = [
    {
        "schema_version": "1.0",
        "candidate_id": f"pe-{cid}",
        "name": name,
        "canonical_domain": domain,
        "discovery_source_ids": source_ids,
        "discovery_origin": "non_regulatory",
        "decision": decision,
        "canonical_destination": destination,
        "reason": reason,
        "cutoff": CUTOFF,
    }
    for cid, name, domain, source_ids, decision, destination, reason in candidate_specs
]
evidence = [
    {
        "candidate_id": row["candidate_id"],
        "decision": row["decision"],
        "source_ids": row["discovery_source_ids"] + (["smv-capia"] if row["candidate_id"] == "pe-capia" else []),
        "gates": {
            "identity": "resolved",
            "direct_investment": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_confirmed_or_not_applicable",
            "recurrence": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_confirmed_or_not_applicable",
            "recent_activity": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_confirmed_or_not_applicable",
            "market_access": "confirmed" if row["decision"] in {"eligible", "duplicate"} else "not_confirmed_or_not_applicable",
        },
        "reason": row["reason"],
    }
    for row in candidates
]

new_profile = "funds/regional/impaqto-capital.md"
profiles = [p for p in sorted(ROOT.glob("funds/**/*.md")) if p.relative_to(ROOT).as_posix() != new_profile]
baseline = [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in profiles]
prior = ROOT / "research/epic-16/issue-26/candidates.jsonl"
prior_baseline = [{"path": prior.relative_to(ROOT).as_posix(), "sha256": sha(prior), "record_count": len(prior.read_text(encoding="utf-8").splitlines()), "classification": "historical_not_discovery"}]

write_json(OUT / "contract.json", contract)
write_jsonl(OUT / "baseline/catalog-baseline.jsonl", baseline)
write_jsonl(OUT / "baseline/prior-candidates.jsonl", prior_baseline)
write_jsonl(OUT / "source-inventory.jsonl", sources)
write_jsonl(OUT / "candidates.jsonl", candidates)
write_jsonl(OUT / "evidence.jsonl", evidence)

coverage = {
    "candidate_count": len(candidates),
    "non_regulatory_discovery_percent": 100.0,
    "regulatory_queries": 1,
    "regulatory_percent": round(100 / len(candidates), 1),
    "marginal_passes": [
        {"pass": 1, "families": ["industry_directory", "sector_report", "institutional_allocator"], "new_candidates": 11, "cumulative": 11},
        {"pass": 2, "families": ["fund_news", "official_portfolio", "official_identity"], "new_candidates": 3, "cumulative": 14},
        {"pass": 3, "families": ["blind_venture_builder", "blind_investor_map"], "new_candidates": 1, "cumulative": 15},
    ],
    "limitation": "Audited coverage of the enumerated sources, not absolute market completeness.",
}
write_json(OUT / "coverage-matrix.json", coverage)

excluded = sorted(row["candidate_id"] for row in candidates if row["decision"] == "insufficient_evidence")
review_request = {
    "status": "awaiting_integrator_review",
    "requested_on": CUTOFF,
    "freeze_allowed": False,
    "eligible_to_review": ["pe-impaqto-capital"],
    "routed_to_review": sorted(row["candidate_id"] for row in candidates if row["decision"] == "routed"),
    "regulatory_cases_to_review": ["pe-capia"],
    "blind_findings": ["pe-axelya-labs"],
    "exclusion_sample": sorted(excluded, key=lambda v: hashlib.sha256(v.encode()).hexdigest())[:max(1, (len(excluded) + 4) // 5)],
    "requested_checks": ["identity", "official evidence", "routing", "false negatives", "critical/high findings"],
}
write_json(OUT / "review-request.json", review_request)
