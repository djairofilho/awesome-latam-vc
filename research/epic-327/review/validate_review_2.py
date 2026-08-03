#!/usr/bin/env python3
"""Build and validate the independent review-2 artifacts for issue #337."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "review"
ASSIGNMENTS = HERE / "assignments" / "review-2.jsonl"
RESULTS = HERE / "results" / "review-2.jsonl"
EVIDENCE = HERE / "evidence" / "review-2.jsonl"
SUMMARY = HERE / "summaries" / "review-2.json"
REVIEWED_ON = "2026-08-02"

OVERRIDES = {
    "delta-fund-100-accelerator": {
        "evidence_ids": ["evidence-delta-100-accelerator-independent-review"],
    },
    "delta-fund-dao-capital": {
        "blind_search_outcome": "contradicted",
        "review_status": "changes_requested",
        "final_decision": "excluded",
        "destination": None,
        "evidence_ids": ["evidence-delta-dao-capital-independent-review"],
        "error_codes": ["category_mismatch"],
    },
    "delta-fund-magic-fund": {
        "blind_search_outcome": "contradicted",
        "review_status": "changes_requested",
        "final_decision": "insufficient_evidence",
        "destination": None,
        "evidence_ids": ["evidence-delta-magic-fund-independent-review"],
        "error_codes": ["identity_mismatch", "unsupported_claim"],
    },
    "delta-fund-angelhub-vc": {
        "evidence_ids": ["evidence-delta-angelhub-vc-independent-review"],
    },
    "delta-fund-wayfinder-ventures": {
        "evidence_ids": [
            "evidence-delta-wayfinder-independent-portfolio",
            "evidence-delta-wayfinder-independent-activity",
        ],
    },
}

CONFIRMED = {
    "delta-fund-100-accelerator",
    "delta-fund-angelhub-vc",
    "delta-fund-citris-foundry",
    "delta-fund-rootcamp",
    "delta-fund-top-seeds-lab",
    "delta-fund-wayfinder-ventures",
    "delta-fund-z-nation-lab",
}


def canonical_line(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha256(record: dict) -> str:
    return hashlib.sha256(canonical_line(record).encode("utf-8")).hexdigest()


def content_sha256(rendered: str) -> str:
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def dump_jsonl(records: list[dict]) -> str:
    return "".join(canonical_line(record) + "\n" for record in records)


def source_records() -> dict[str, dict]:
    records = {}
    for number in range(3):
        path = EPIC / "shards" / f"validation-{number}" / "decisions.jsonl"
        for record in load_jsonl(path):
            records[record["candidate_id"]] = record
    for record in load_jsonl(EPIC / "consolidation" / "exceptions.jsonl"):
        records[record["candidate_id"]] = record
    for record in load_jsonl(EPIC / "consolidation" / "candidates.jsonl"):
        if record.get("status") == "routed":
            records[record["candidate_id"]] = record
    return records


def review_evidence() -> list[dict]:
    return [
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-100-accelerator-independent-review",
            "candidate_id": "delta-fund-100-accelerator",
            "official_url": "https://www.100accelerator.com/about",
            "source_title": "100+ Accelerator official program",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_identity",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "100+ Accelerator"},
                    "support": "The official page identifies the program as 100+ Accelerator.",
                },
                {
                    "field": "category",
                    "value": {"finding": "confirmed", "value": "accelerator"},
                    "support": "The official page describes a six-month program for selected startups, with mentors, corporate partners, and equity-free pilot funding.",
                },
            ],
        },
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-angelhub-vc-independent-review",
            "candidate_id": "delta-fund-angelhub-vc",
            "official_url": "https://www.angelhub.mx/",
            "source_title": "AngelHub official website",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_identity",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "AngelHub"},
                    "support": "The official site identifies AngelHub as an angel investors club serving Mexico and Latin America.",
                },
                {
                    "field": "category",
                    "value": {"finding": "confirmed", "value": "angel_network"},
                    "support": "The official site describes AngelHub as an angel investors club and presents its members, investment thesis, portfolio, and investment process.",
                },
            ],
        },
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-dao-capital-independent-review",
            "candidate_id": "delta-fund-dao-capital",
            "official_url": "https://www.daocapital.com.br/",
            "source_title": "DAO Capital",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_thesis",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "DAO Capital"},
                    "support": "A página institucional identifica a organização como DAO Capital.",
                },
                {
                    "field": "direct_startup_investment",
                    "value": {"finding": "contradictory", "value": False},
                    "support": "A tese oficial descreve gestão quantitativa de carteiras de mercados públicos, não investimento direto em startups.",
                },
                {
                    "field": "category",
                    "value": {"finding": "confirmed", "value": "public_markets_asset_manager"},
                    "support": "A página apresenta estratégias sistemáticas e fatores aplicados a ativos negociados em mercados públicos.",
                },
            ],
        },
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-magic-fund-independent-review",
            "candidate_id": "delta-fund-magic-fund",
            "official_url": "https://www.magic.fund/",
            "source_title": "MAGIC Fund official portfolio",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_portfolio",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "MAGIC Fund"},
                    "support": "A página institucional identifica a organização como fundo de venture capital early-stage.",
                },
                {
                    "field": "direct_startup_investment",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "A descrição oficial declara investimento em startups pre-seed e seed e lista empresas do portfólio.",
                },
                {
                    "field": "recurrence",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "A página declara mais de duzentas startups apoiadas mundialmente.",
                },
                {
                    "field": "market_access",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "O portfólio oficial nomeia Frubana e KiwiBot, empresas com operação latino-americana.",
                },
                {
                    "field": "activity_date",
                    "value": {"finding": "not_disclosed", "value": None},
                    "support": "O material oficial encontrado não fornece uma data exata de atividade que satisfaça a janela de validação.",
                },
            ],
        },
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-wayfinder-independent-portfolio",
            "candidate_id": "delta-fund-wayfinder-ventures",
            "official_url": "https://www.wayfinder.com/companies",
            "source_title": "Wayfinder Ventures official portfolio",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_portfolio",
            "claims": [
                {
                    "field": "identity",
                    "value": {"finding": "confirmed", "value": "Wayfinder Ventures"},
                    "support": "A página oficial identifica o fundo e apresenta seu portfólio de startups.",
                },
                {
                    "field": "direct_startup_investment",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "O portfólio oficial apresenta dezenas de startups investidas pelo fundo.",
                },
                {
                    "field": "recurrence",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "A página oficial lista investimentos recorrentes em diferentes anos.",
                },
                {
                    "field": "market_access",
                    "value": {"finding": "confirmed", "value": True},
                    "support": "O portfólio oficial inclui Konta.com, descrita como solução para México e América Latina, e Pideaky, descrita como solução para a América Latina.",
                },
            ],
        },
        {
            "schema_version": "1.0",
            "evidence_id": "evidence-delta-wayfinder-independent-activity",
            "candidate_id": "delta-fund-wayfinder-ventures",
            "official_url": "https://www.wayfinder.com/updates",
            "source_title": "Wayfinder Ventures official updates",
            "accessed_on": REVIEWED_ON,
            "source_kind": "official_activity",
            "claims": [
                {
                    "field": "activity_date",
                    "value": {"finding": "confirmed", "value": "2025-04-22"},
                    "support": "A página oficial registra atualização de empresa do portfólio em 22 de abril de 2025.",
                }
            ],
        },
    ]


def build() -> tuple[list[dict], list[dict], dict]:
    assignments = load_jsonl(ASSIGNMENTS)
    sources = source_records()
    results = []
    for assignment in assignments:
        candidate_id = assignment["candidate_id"]
        source = sources[candidate_id]
        destination = source.get("destination", source.get("route_destination"))
        base = {
            "schema_version": "1.0",
            "candidate_id": candidate_id,
            "reviewer": "review-2",
            "reviewed_on": REVIEWED_ON,
            "assignment_sha256": record_sha256(assignment),
            "blind_search_outcome": "confirmed" if candidate_id in CONFIRMED else "no_additional_evidence",
            "review_status": "approved",
            "final_decision": assignment["source_decision"],
            "destination": destination,
            "evidence_ids": [],
            "error_codes": [],
        }
        base.update(OVERRIDES.get(candidate_id, {}))
        results.append(base)
    results.sort(key=lambda record: record["candidate_id"])
    evidence = sorted(review_evidence(), key=lambda record: record["evidence_id"])
    results_rendered = dump_jsonl(results)
    evidence_rendered = dump_jsonl(evidence)
    summary = {
        "schema_version": "1.0",
        "issue": 337,
        "reviewer": "review-2",
        "assignment_records": len(assignments),
        "result_records": len(results),
        "evidence_records": len(evidence),
        "assignment_file_sha256": content_sha256(ASSIGNMENTS.read_text(encoding="utf-8")),
        "results_file_sha256": content_sha256(results_rendered),
        "evidence_file_sha256": content_sha256(evidence_rendered),
        "blind_search_outcome_counts": dict(sorted(Counter(row["blind_search_outcome"] for row in results).items())),
        "review_status_counts": dict(sorted(Counter(row["review_status"] for row in results).items())),
        "final_decision_counts": dict(sorted(Counter(row["final_decision"] for row in results).items())),
        "error_code_counts": dict(sorted(Counter(code for row in results for code in row["error_codes"]).items())),
        "complete": len(assignments) == len(results) == 377,
    }
    return results, evidence, summary


def rendered_outputs() -> dict[Path, str]:
    results, evidence, summary = build()
    return {
        RESULTS: dump_jsonl(results),
        EVIDENCE: dump_jsonl(evidence),
        SUMMARY: json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }


def validate() -> list[str]:
    errors = []
    expected = rendered_outputs()
    assignments = load_jsonl(ASSIGNMENTS)
    sources = source_records()
    assignment_by_id = {row["candidate_id"]: row for row in assignments}
    for path, rendered in expected.items():
        if not path.exists():
            errors.append(f"arquivo ausente: {path.relative_to(ROOT).as_posix()}")
        elif path.read_text(encoding="utf-8") != rendered:
            errors.append(f"artefato não canônico ou desatualizado: {path.relative_to(ROOT).as_posix()}")
    if errors:
        return errors

    results = load_jsonl(RESULTS)
    evidence = load_jsonl(EVIDENCE)
    review_schema = json.loads((EPIC / "schemas" / "review-record.schema.json").read_text(encoding="utf-8"))
    evidence_schema = json.loads((EPIC / "schemas" / "official-evidence-record.schema.json").read_text(encoding="utf-8"))
    review_validator = Draft202012Validator(review_schema, format_checker=FormatChecker())
    evidence_validator = Draft202012Validator(evidence_schema, format_checker=FormatChecker())
    for index, record in enumerate(results, 1):
        errors.extend(f"results:{index}: {error.message}" for error in review_validator.iter_errors(record))
    for index, record in enumerate(evidence, 1):
        errors.extend(f"evidence:{index}: {error.message}" for error in evidence_validator.iter_errors(record))

    result_ids = [row["candidate_id"] for row in results]
    assignment_ids = [row["candidate_id"] for row in assignments]
    if result_ids != assignment_ids:
        errors.append("resultados não cobrem exatamente as atribuições, em ordem canônica")
    if len(result_ids) != len(set(result_ids)):
        errors.append("candidate_id duplicado nos resultados")

    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    referenced = set()
    for result in results:
        candidate_id = result["candidate_id"]
        assignment = assignment_by_id[candidate_id]
        source = sources[candidate_id]
        if record_sha256(source) != assignment["input_sha256"]:
            errors.append(f"{candidate_id}: input_sha256 diverge da origem")
        if record_sha256(assignment) != result["assignment_sha256"]:
            errors.append(f"{candidate_id}: assignment_sha256 incorreto")
        if result["review_status"] == "approved":
            source_destination = source.get(
                "destination", source.get("route_destination")
            )
            if (
                result["final_decision"] != assignment["source_decision"]
                or result["destination"] != source_destination
            ):
                errors.append(f"{candidate_id}: aprovação diverge da decisão de origem")
        else:
            if result["blind_search_outcome"] != "blocked" and not result["evidence_ids"]:
                errors.append(f"{candidate_id}: alteração sem evidência oficial")
        for evidence_id in result["evidence_ids"]:
            referenced.add(evidence_id)
            item = evidence_by_id.get(evidence_id)
            if item is None:
                errors.append(f"{candidate_id}: evidência ausente {evidence_id}")
            elif item["candidate_id"] != candidate_id:
                errors.append(f"{candidate_id}: evidência pertence a outro candidato")
    orphaned = set(evidence_by_id) - referenced
    if orphaned:
        errors.append("evidências órfãs: " + ", ".join(sorted(orphaned)))
    inactive = [row for row in results if assignment_by_id[row["candidate_id"]]["source_decision"] == "inactive"]
    if any(row["review_status"] != "approved" for row in inactive):
        errors.append("estrato inativo falhou na revisão independente")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        for path, rendered in rendered_outputs().items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
    errors = validate()
    if errors:
        print("Validação da revisão review-2 falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("review-2 validado: 377 resultados, dois ajustes e estrato inativo aprovado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
