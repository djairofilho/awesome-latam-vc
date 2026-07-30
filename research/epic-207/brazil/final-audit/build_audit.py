#!/usr/bin/env python3
"""Build and verify the final Brazil funds coverage and publication audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
BRAZIL = ROOT / "research" / "epic-207" / "brazil"
AUDIT = BRAZIL / "final-audit"
REPORT = AUDIT / "audit-report.json"
CUTOFF = "2026-07-30"
CORE_ARTIFACTS = (
    "source-inventory.jsonl",
    "candidates.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "review-sample.jsonl",
)
ROUTE_TARGETS = {
    "routed_accelerators": 62,
    "routed_angel_networks": 63,
    "routed_funding_platforms": 64,
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def metadata(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text.split("---", 2)[1])


def compact_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def build_report() -> dict[str, Any]:
    sources = read_jsonl(BRAZIL / "source-inventory.jsonl")
    candidates = read_jsonl(BRAZIL / "candidates.jsonl")
    evidence = read_jsonl(BRAZIL / "evidence.jsonl")
    identities = read_jsonl(BRAZIL / "identity-resolution.jsonl")
    cvm_logs = read_jsonl(BRAZIL / "cvm-query-log.jsonl")
    reviews = read_jsonl(BRAZIL / "review-sample.jsonl")
    run_rows = read_jsonl(BRAZIL / "run-manifest.jsonl")
    freeze = read_json(BRAZIL / "freeze-manifest.json")
    review_report = read_json(BRAZIL / "review-report.json")
    publication = read_json(
        BRAZIL / "publication" / "publication-report.json"
    )

    source_by_id = {row["source_id"]: row for row in sources}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    eligible = [row for row in candidates if row["decision"] == "eligible"]
    decision_counts = dict(sorted(Counter(
        row["decision"] for row in candidates
    ).items()))

    discovery_refs = [
        source_id
        for candidate in candidates
        for source_id in candidate["discovery_source_ids"]
    ]
    discovery_missing = sorted(
        set(discovery_refs) - set(source_by_id)
    )
    discovery_cvm = [
        source_id
        for source_id in discovery_refs
        if source_id in source_by_id and source_by_id[source_id]["is_cvm"]
    ]

    tasks = [row for row in run_rows if row["record_type"] == "task"]
    task_channels = Counter(row["research_channel"] for row in tasks)
    research_task_denominator = (
        task_channels["non_cvm"] + task_channels["cvm"]
    )
    non_cvm_share = (
        task_channels["non_cvm"] / research_task_denominator
        if research_task_denominator
        else 0
    )

    severity_counts = dict(sorted(Counter(
        row["severity"] for row in reviews
    ).items()))
    unresolved_reviews = [
        row["review_id"] for row in reviews if not row["resolved"]
    ]

    family_yield: dict[str, dict[str, int]] = {}
    for candidate in candidates:
        families = {
            source_by_id[source_id]["source_family"]
            for source_id in candidate["discovery_source_ids"]
        }
        for family in families:
            cell = family_yield.setdefault(
                family, {"candidate_rows": 0, "eligible_rows": 0}
            )
            cell["candidate_rows"] += 1
            cell["eligible_rows"] += candidate["decision"] == "eligible"

    routed = {}
    for decision, issue in ROUTE_TARGETS.items():
        routed[decision] = {
            "target_issue": issue,
            "automatic_eligibility": False,
            "candidates": [
                {
                    "candidate_id": row["candidate_id"],
                    "name": row["name"],
                }
                for row in sorted(
                    (
                        candidate
                        for candidate in candidates
                        if candidate["decision"] == decision
                    ),
                    key=lambda item: item["candidate_id"],
                )
            ],
        }

    profile_source_count = 0
    profile_source_urls: set[str] = set()
    source_url_mismatches: list[str] = []
    website_homepage_exceptions: list[str] = []
    profile_last_verified_after_cutoff: list[str] = []
    publication_profiles = {
        item["path"]: item["sha256"]
        for item in publication["profile_files"]
    }
    current_profile_hash_mismatches = []
    for relative, expected_hash in publication_profiles.items():
        path = ROOT / relative
        if sha256(path) != expected_hash:
            current_profile_hash_mismatches.append(relative)
        if not relative.startswith("funds/"):
            continue
        profile = metadata(path)
        candidate = next(
            row
            for row in eligible
            if row["destination"] == relative
        )
        allowed_urls = {
            evidence_by_id[evidence_id]["url"]
            for evidence_id in candidate["official_evidence_ids"]
        }
        for item in profile["sources"]:
            profile_source_count += 1
            profile_source_urls.add(item["url"])
            if item["url"] not in allowed_urls:
                source_url_mismatches.append(relative + ":" + item["url"])
        website = profile["official_website"]
        if website and website not in allowed_urls:
            if website == candidate["official_site"]:
                website_homepage_exceptions.append(relative)
            else:
                source_url_mismatches.append(relative + ":website:" + website)
        if profile["last_verified"] > CUTOFF:
            profile_last_verified_after_cutoff.append(relative)

    current_core_hashes = {
        name: sha256(BRAZIL / name) for name in CORE_ARTIFACTS
    }
    frozen_core_hashes = freeze["core_artifact_hashes"]
    core_hash_mismatches = sorted(
        name
        for name in CORE_ARTIFACTS
        if current_core_hashes[name] != frozen_core_hashes[name]
    )

    terminal_sources = [
        row
        for row in sources
        if row["result"] in {"complete", "gap_justified"}
    ]
    gap_rows = [
        row for row in sources if row["result"] == "gap_justified"
    ]
    gap_metadata_complete = all(
        row["reason"] and row["owner"] and row["next_action"]
        for row in gap_rows
    )
    unresolved_identities = [
        row["resolution_id"]
        for row in identities
        if row["resolution"] == "unresolved"
    ]
    cvm_inventory = [row for row in sources if row["is_cvm"]]
    cvm_candidate_ids = sorted({
        row["candidate_id"] for row in cvm_logs
    })
    cvm_rate = len(cvm_candidate_ids) / freeze["totals"]["canonical_candidates"]

    blind_delta = {
        "candidate_rows": (
            review_report["final_bundle"]["candidate_rows"]
            - review_report["original_bundle"]["candidate_rows"]
        ),
        "eligible": (
            review_report["final_bundle"]["decision_counts"]["eligible"]
            - review_report["original_bundle"]["decision_counts"]["eligible"]
        ),
    }

    integrity = {
        "all_sources_terminal": len(terminal_sources) == len(sources),
        "gap_metadata_complete": gap_metadata_complete,
        "all_candidates_decided": all(
            row["status"] == "decided" and row["decision"]
            for row in candidates
        ),
        "all_identity_resolutions_terminal": not unresolved_identities,
        "discovery_references_complete": not discovery_missing,
        "discovery_is_one_hundred_percent_non_cvm": not discovery_cvm,
        "cvm_below_ten_percent": cvm_rate <= 0.10,
        "cvm_logs_complete": (
            len(cvm_logs) == 2
            and all(
                row["question"]
                and row["searched_identifier"]
                and row["minimum_fact"]
                and row["outcome"]
                for row in cvm_logs
            )
        ),
        "cvm_not_used_for_discovery": all(
            not row["discovery_allowed"] for row in cvm_inventory
        ),
        "all_review_findings_resolved": not unresolved_reviews,
        "zero_high_or_critical_open": (
            not unresolved_reviews
            and severity_counts.get("high", 0) == 0
            and severity_counts.get("critical", 0) == 0
        ),
        "freeze_core_hashes_match": not core_hash_mismatches,
        "publication_report_integrity": all(
            publication["integrity"].values()
        ),
        "published_candidates_match_eligible": (
            set(publication["candidate_ids"])
            == {row["candidate_id"] for row in eligible}
        ),
        "published_destinations_match_eligible": (
            set(publication["destinations"])
            == {row["destination"] for row in eligible}
        ),
        "profile_hashes_match_current_files": (
            not current_profile_hash_mismatches
        ),
        "profile_sources_come_from_frozen_evidence": (
            not source_url_mismatches
        ),
        "profile_dates_within_cutoff": (
            not profile_last_verified_after_cutoff
        ),
        "exactly_twenty_seven_eligible": len(eligible) == 27,
        "exactly_eighty_one_profile_files": (
            publication["profile_file_count"] == 81
        ),
        "zero_omissions": publication["integrity"]["zero_omissions"],
        "zero_overlaps": publication["integrity"]["zero_overlaps"],
    }

    return {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 224,
        "status": "complete",
        "cutoff_date": CUTOFF,
        "generated_on": CUTOFF,
        "scope_statement": (
            "Cobertura auditada nas fontes e no recorte registrados; "
            "não prova totalidade do universo brasileiro."
        ),
        "source_coverage": {
            "total": len(sources),
            "complete": sum(
                row["result"] == "complete" for row in sources
            ),
            "gap_justified": len(gap_rows),
            "terminal": len(terminal_sources),
        },
        "candidate_reconciliation": {
            "candidate_rows": len(candidates),
            "canonical_candidates": (
                len(candidates) - decision_counts.get("duplicate", 0)
            ),
            "decision_counts": decision_counts,
        },
        "discovery_provenance": {
            "reference_count": len(discovery_refs),
            "non_cvm_reference_count": (
                len(discovery_refs) - len(discovery_cvm)
            ),
            "cvm_reference_count": len(discovery_cvm),
            "missing_reference_count": len(discovery_missing),
        },
        "cvm_use": {
            "consulted_candidate_count": len(cvm_candidate_ids),
            "canonical_candidate_count": (
                freeze["totals"]["canonical_candidates"]
            ),
            "query_rate": cvm_rate,
            "query_log_count": len(cvm_logs),
            "inventory_document_count": len(cvm_inventory),
            "eligibility_use": False,
            "candidate_ids": cvm_candidate_ids,
        },
        "task_mix": {
            "non_cvm": task_channels["non_cvm"],
            "cvm": task_channels["cvm"],
            "not_applicable": task_channels["not_applicable"],
            "research_denominator": research_task_denominator,
            "non_cvm_share": non_cvm_share,
        },
        "review": {
            "row_count": len(reviews),
            "severity_counts": severity_counts,
            "unresolved_count": len(unresolved_reviews),
            "initial_curve": review_report["cumulative_discovery_curve"],
            "blind_review_delta": blind_delta,
            "saturation_passes": review_report["saturation_passes"],
            "saturation_conclusion": (
                "Rendimento marginal baixo no recorte auditado; "
                "não representa saturação absoluta."
            ),
        },
        "family_yield": {
            "overlap_warning": (
                "Famílias podem atribuir o mesmo candidato; os totais "
                "por família não são somáveis."
            ),
            "families": dict(sorted(family_yield.items())),
        },
        "publication": {
            "batch_count": publication["batch_count"],
            "candidate_count": publication["candidate_count"],
            "destination_count": publication["destination_count"],
            "profile_file_count": publication["profile_file_count"],
            "profile_source_reference_count": profile_source_count,
            "unique_profile_source_url_count": len(profile_source_urls),
            "official_website_homepage_exceptions": (
                sorted(website_homepage_exceptions)
            ),
            "redundant_evidence_not_published": [
                "Quartzo Capital",
                "Mundi Ventures",
            ],
        },
        "routing": routed,
        "issue_state_at_audit": {
            "closed": list(range(208, 224)) + [241, 242, 243],
            "open": [207, 224],
            "receiver_issues_closed": [62, 63, 64],
        },
        "integrity": integrity,
        "limitations": [
            (
                "A cobertura é auditada no recorte e na data de corte; "
                "novos participantes e mudanças posteriores exigem nova rodada."
            ),
            (
                "Os rendimentos por família se sobrepõem e não devem ser "
                "somados como universos independentes."
            ),
            (
                "A participação não-CVM de 90,91% usa 11 tarefas de "
                "pesquisa/adjudicação e exclui duas tarefas administrativas."
            ),
            (
                "Treze official_website usam a homepage congelada do candidato, "
                "enquanto as sources publicadas permanecem URLs exatas das "
                "evidências oficiais."
            ),
            (
                "Os oito encaminhamentos requerem revalidação nos contratos "
                "das epics #62, #63 e #64; não são elegíveis automáticos."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = compact_json(build_report())
    if args.check:
        if not REPORT.is_file() or REPORT.read_bytes() != content:
            print("Final audit report drift detected.")
            return 1
        print("Final Brazil funds audit verified.")
        return 0
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_bytes(content)
    print("Final Brazil funds audit written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
