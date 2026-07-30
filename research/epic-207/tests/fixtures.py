from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


JSONL_FILES = (
    "candidates.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "review-sample.jsonl",
    "run-manifest.jsonl",
    "source-inventory.jsonl",
)

HASHED_ARTIFACTS = tuple(
    filename for filename in JSONL_FILES if filename != "run-manifest.jsonl"
)


def build_bundle() -> dict[str, Any]:
    candidate_id = "fund-example-org"
    evidence = [
        {
            "schema_version": "1.0",
            "evidence_id": f"ev-example-{field}",
            "candidate_id": candidate_id,
            "subject_type": "candidate",
            "subject_id": candidate_id,
            "url": f"https://example.org/{field}",
            "title": f"Official {field}",
            "publisher": "Example Ventures",
            "source_type": source_type,
            "published_on": "2026-06-15",
            "observed_on": "2026-06-15",
            "accessed_on": "2026-07-30",
            "claims": [{"field": field, "finding": "confirmed"}],
            "locator": f"Section {field}",
            "summary": f"The official source confirms {field}.",
        }
        for field, source_type in (
            ("direct_investment", "official_thesis"),
            ("recurring_investment", "official_thesis"),
            ("recent_activity", "official_announcement"),
            ("brazil_relation", "official_thesis"),
            ("identity", "official_website"),
        )
    ]
    evidence_ids = [record["evidence_id"] for record in evidence]
    candidate = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "name": "Example Ventures",
        "canonical_domain": "example.org",
        "official_site": "https://example.org",
        "brand_id": "brand-example-org",
        "manager_id": "manager-example-org",
        "vehicle_ids": ["vehicle-example-i"],
        "program_ids": [],
        "successor_id": None,
        "entity_type": "investment_firm",
        "aliases": [],
        "canonical_candidate_id": None,
        "canonical_profile": None,
        "identity_resolution_ids": ["identity-example-org"],
        "base_country": "BR",
        "declared_geography": ["BR"],
        "brazil_relation": "based_in_brazil",
        "direct_investment_status": "confirmed",
        "recurring_investment_status": "confirmed",
        "activity_status": "active_recent",
        "last_official_activity_on": "2026-06-15",
        "cutoff_date": "2026-07-30",
        "discovery_source_ids": ["src-example-rounds"],
        "official_evidence_ids": evidence_ids,
        "direct_investment_evidence_ids": ["ev-example-direct_investment"],
        "recurrence_evidence_ids": ["ev-example-recurring_investment"],
        "activity_evidence_ids": ["ev-example-recent_activity"],
        "brazil_access_evidence_ids": ["ev-example-brazil_relation"],
        "identity_evidence_ids": ["ev-example-identity"],
        "discovered_on": "2026-07-30",
        "already_listed": False,
        "status": "decided",
        "decision": "eligible",
        "reason": None,
        "destination": None,
        "owner": None,
        "next_action": None,
    }
    source = {
        "schema_version": "1.0",
        "source_id": "src-example-rounds",
        "issue": 211,
        "source": "Example startup announcement",
        "initial_url": "https://startup.example/round",
        "source_family": "rounds",
        "source_classification": "new_source",
        "research_channel": "non_cvm",
        "regulatory_source": False,
        "discovery_allowed": True,
        "countries": ["BR"],
        "regions": [],
        "sectors": [],
        "scope_walked": "One official funding announcement.",
        "accessed_on": "2026-07-30",
        "robots_status": "allowed",
        "access_method": "http",
        "cache_key": "https://startup.example/round",
        "result": "complete",
        "reason": None,
        "owner": None,
        "next_action": None,
        "notes": None,
    }
    coverage = {
        "schema_version": "1.0",
        "coverage_id": "coverage-rounds-br",
        "issue": 211,
        "source_family": "rounds",
        "geography": "BR",
        "sector": None,
        "planned_sources": 1,
        "completed_sources": 1,
        "source_ids": ["src-example-rounds"],
        "status": "complete",
        "gap_reason": None,
        "owner": None,
        "next_action": None,
    }
    identity = {
        "schema_version": "1.0",
        "resolution_id": "identity-example-org",
        "candidate_ids": [candidate_id],
        "canonical_candidate_id": candidate_id,
        "relation_type": "same_entity",
        "brand_id": "brand-example-org",
        "manager_id": "manager-example-org",
        "vehicle_ids": ["vehicle-example-i"],
        "successor_id": None,
        "evidence_ids": ["ev-example-identity"],
        "resolution": "confirmed",
        "reason": "The official domain identifies one investment organization.",
        "resolved_by": "coordinator",
        "resolved_on": "2026-07-30",
        "review_status": "reviewed",
        "reviewed_by": "independent-reviewer",
        "reviewed_on": "2026-07-30",
    }
    review = {
        "schema_version": "1.0",
        "review_id": "review-example-org",
        "candidate_id": candidate_id,
        "review_type": "eligible",
        "selection_basis": "all_eligible",
        "original_decision": "eligible",
        "review_decision": "confirmed",
        "reviewer": "independent-reviewer",
        "reviewed_on": "2026-07-30",
        "findings": [],
        "next_action": None,
    }
    run = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": "run-epic-207-example",
        "issues": [211],
        "contract_issue": 208,
        "cutoff_date": "2026-07-30",
        "created_on": "2026-07-30",
        "status": "complete",
        "task_count": 1,
        "owner": "coordinator",
        "hash_algorithm": None,
        "artifact_hashes": None,
        "execution_policy": {
            "respect_robots_txt": True,
            "bypass_access_controls": False,
            "max_concurrency_per_domain": 2,
            "minimum_delay_ms": 500,
            "cache_enabled": True,
            "retry_attempts": 4,
            "browser_policy": "official_js_only",
        },
        "source_policy": {
            "cvm_discovery_allowed": False,
            "non_cvm_origin_required": True,
            "max_cvm_candidate_ratio": 0.10,
            "minimum_cvm_candidate_ratio": None,
            "max_cvm_task_ratio": 0.10,
            "candidate_denominator_stage": "post_consolidation",
            "local_startup_file_allowed": False,
        },
        "notes": None,
    }
    task = {
        "schema_version": "1.0",
        "record_type": "task",
        "run_id": "run-epic-207-example",
        "task_id": "task-example-rounds",
        "issue": 211,
        "task_type": "source_research",
        "source_id": "src-example-rounds",
        "candidate_id": None,
        "source_family": "rounds",
        "research_channel": "non_cvm",
        "regulatory_task": False,
        "partition": "brazil",
        "worker_id": "worker-rounds",
        "shard_path": "research/epic-207/brazil/shards/worker-rounds",
        "priority": 1,
        "status": "done",
        "owner": "worker-rounds",
        "block_reason": None,
        "next_action": None,
        "last_error": None,
    }
    audit_report = {
        "schema_version": "1.0",
        "cutoff_date": "2026-07-30",
        "canonical_candidate_count": 1,
        "candidates_with_cvm_query": 0,
        "cvm_query_rate": 0.0,
        "completed_research_tasks": 1,
        "completed_non_cvm_tasks": 1,
        "completed_cvm_tasks": 0,
        "non_cvm_task_share": 1.0,
        "cvm_task_share": 0.0,
        "policy_compliant": True,
    }
    return {
        "candidates.jsonl": [candidate],
        "coverage-matrix.jsonl": [coverage],
        "cvm-query-log.jsonl": [],
        "evidence.jsonl": evidence,
        "identity-resolution.jsonl": [identity],
        "review-sample.jsonl": [review],
        "run-manifest.jsonl": [run, task],
        "source-inventory.jsonl": [source],
        "audit-report.json": audit_report,
    }


def clone_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(bundle)


def write_bundle(root: Path, bundle: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for filename, records in bundle.items():
        path = root / filename
        if filename.endswith(".jsonl"):
            path.write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )
        else:
            path.write_text(
                json.dumps(records, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def artifact_hash(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
