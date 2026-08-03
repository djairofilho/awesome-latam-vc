#!/usr/bin/env python3
"""Build the deterministic final audit for epic #327 without network access."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[3]
EPIC = REPO / "research" / "epic-327"
HERE = EPIC / "final-audit"
EXPECTED_CANDIDATES = 1088
EXPECTED_CUTOFF = "2026-08-02"
WAYFINDER_ID = "delta-fund-wayfinder-ventures"
WAYFINDER_ENTITY_ID = "fund:wayfinder-ventures"
WAYFINDER_PROFILE = "funds/multi-country/wayfinder-ventures.md"
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
TERMINAL_DECISIONS = {
    "duplicate",
    "eligible",
    "excluded",
    "identity_conflict",
    "inactive",
    "insufficient_evidence",
    "routed_accelerators",
    "routed_angel_networks",
    "routed_funding_platforms",
    "routed_other",
    "routed_public_programs",
    "unresolved",
}
MANDATORY_REVIEW = {"eligible", "identity_conflict"}
ROUTED_DESTINATIONS = {
    "routed_accelerators": ("ecosystem/accelerators/",),
    "routed_angel_networks": ("ecosystem/angel-networks/",),
    "routed_funding_platforms": ("ecosystem/funding-platforms/",),
    "routed_public_programs": ("ecosystem/public-programs/",),
    "routed_other": (
        "ecosystem/corporate-investors/",
        "ecosystem/fellowships/",
        "ecosystem/impact-investment-platforms/",
        "ecosystem/startup-studios/",
        "ecosystem/university-programs/",
    ),
}
MOJIBAKE_RE = re.compile(
    r"(?:\u00c3(?=[\u0080-\u00bf\u00a1\u00a3\u00a7\u00a9\u00aa\u00b3\u00ba])|"
    r"\u00c2(?=[\u0080-\u00bf\u00a0\u00a9\u00ae\u00b0])|"
    r"\u00e2(?=[\u0080-\u00bf\u20ac])|\ufffd|\x07)"
)
_MODULES: dict[str, Any] = {}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def dump_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(canonical_json(row) + "\n" for row in rows)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def record_sha256(record: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json(record).encode("utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="strict")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(read_text(path).splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        rows.append(value)
    return rows


def load_many_jsonl(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(paths):
        rows.extend(load_jsonl(path))
    return rows


def load_module(name: str, path: Path) -> Any:
    key = f"{name}:{path.resolve()}"
    if key in _MODULES:
        return _MODULES[key]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    _MODULES[key] = module
    return module


def index_unique(
    rows: Iterable[dict[str, Any]], key: str
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    index: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str) or not value:
            duplicates.append("<missing>")
        elif value in index:
            duplicates.append(value)
        else:
            index[value] = row
    return index, sorted(duplicates)


def finding(
    code: str, severity: str, message: str, details: Any | None = None
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if details is not None:
        item["details"] = details
    return item


def routed(decision: str) -> bool:
    return decision.startswith("routed_")


def destination_kind(decision: str) -> str:
    if decision in {"identity_conflict", "unresolved"}:
        return "manual_review"
    if routed(decision):
        return "ecosystem_handoff"
    if decision == "eligible":
        return "fund_publication"
    if decision == "duplicate":
        return "canonical_duplicate"
    if decision == "insufficient_evidence":
        return "evidence_follow_up"
    return "no_publication"


def origin_decision(
    candidate: dict[str, Any], validation: dict[str, Any] | None
) -> tuple[str | None, Any]:
    if validation:
        return validation.get("decision"), validation.get("destination")
    status = candidate.get("status")
    if status == "routed":
        destination = candidate.get("route_destination")
        route_map = {
            "ecosystem/accelerators/": "routed_accelerators",
            "ecosystem/angel-networks/": "routed_angel_networks",
            "ecosystem/funding-platforms/": "routed_funding_platforms",
            "ecosystem/public-programs/": "routed_public_programs",
        }
        for prefix, decision in route_map.items():
            if isinstance(destination, str) and destination.startswith(prefix):
                return decision, destination
        return "routed_other", destination
    if status in {"duplicate", "identity_conflict", "unresolved"}:
        destination = candidate.get("canonical_profile") or candidate.get(
            "route_destination"
        )
        return status, destination
    return None, None


def resolve_final_decisions(
    candidates: dict[str, dict[str, Any]],
    validations: dict[str, dict[str, Any]],
    reviews: dict[str, dict[str, Any]],
    adjudications: dict[str, dict[str, Any]],
    cutoff_date: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Apply adjudication > review > origin precedence to the whole queue."""
    rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    for candidate_id in sorted(candidates):
        source = "origin"
        validation = validations.get(candidate_id)
        source_record = validation or candidates[candidate_id]
        decision, destination = origin_decision(candidates[candidate_id], validation)
        if candidate_id in reviews:
            source = "review"
            source_record = reviews[candidate_id]
            decision = source_record.get("final_decision")
            destination = source_record.get("destination")
        if candidate_id in adjudications:
            source = "adjudication"
            source_record = adjudications[candidate_id]
            decision = source_record.get("final_decision")
            destination = source_record.get("destination")
        if decision not in TERMINAL_DECISIONS or source_record is None:
            unresolved.append(candidate_id)
            continue
        rows.append(
            {
                "candidate_id": candidate_id,
                "cutoff_date": cutoff_date,
                "decision": decision,
                "destination": destination,
                "destination_kind": destination_kind(decision),
                "source": source,
                "source_record_sha256": record_sha256(source_record),
            }
        )
    return rows, unresolved


def coverage_findings(
    origins: dict[str, str], assignments: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    mandatory = {
        candidate_id
        for candidate_id, decision in origins.items()
        if decision in MANDATORY_REVIEW or routed(decision)
    }
    missing = sorted(mandatory - set(assignments))
    if missing:
        findings.append(
            finding(
                "mandatory_review_coverage",
                "high",
                "Eligible, identity-conflict, and routed records require independent review.",
                {"missing_count": len(missing), "candidate_ids": missing},
            )
        )

    sampled_decisions = {"excluded", "inactive", "insufficient_evidence", "unresolved"}
    for decision in sorted(sampled_decisions):
        population = sorted(cid for cid, value in origins.items() if value == decision)
        selected = sorted(
            cid
            for cid, row in assignments.items()
            if cid in population
            and row.get("review_reason") == "deterministic_exclusion_sample"
        )
        minimum = math.ceil(len(population) * 0.2)
        if len(selected) < minimum:
            findings.append(
                finding(
                    "exclusion_sample_coverage",
                    "high",
                    f"The deterministic {decision} sample is below 20 percent.",
                    {
                        "decision": decision,
                        "population": len(population),
                        "minimum": minimum,
                        "selected": len(selected),
                    },
                )
            )
    return findings


def ordered_by(rows: list[dict[str, Any]], key: str) -> bool:
    values = [row.get(key) for row in rows]
    return values == sorted(values)


def gate_status(findings: list[dict[str, Any]], codes: set[str]) -> str:
    return "fail" if any(row["code"] in codes for row in findings) else "pass"


def semantic_destination(decision: str, destination: Any) -> Any:
    if decision in {"identity_conflict", "unresolved"}:
        return "manual_review"
    return destination


def review_pipeline_findings(epic: Path) -> list[dict[str, Any]]:
    """Run the authoritative preparation, reconciliation, freeze, and plan logic."""
    repo = epic.parents[1]
    prepare = load_module(
        "epic327_review_prepare", epic / "review" / "prepare.py"
    )
    reconcile = load_module(
        "epic327_review_reconcile", epic / "review" / "reconcile.py"
    )
    freeze_module = load_module(
        "epic327_review_freeze", epic / "review" / "freeze.py"
    )
    plan_module = load_module(
        "epic327_publication_plan", epic / "publication" / "plan.py"
    )
    findings: list[dict[str, Any]] = []

    prepare_errors, prepare_outputs = prepare.build(epic)
    prepare_drift = sorted(
        relative
        for relative, rendered in prepare_outputs.items()
        if not (epic / "review" / relative).is_file()
        or read_text(epic / "review" / relative) != rendered
    )
    if prepare_errors or prepare_drift:
        findings.append(
            finding(
                "review_assignment_determinism",
                "critical",
                "Assignments, source hashes, reviewer separation, sampling, and summary must exactly match prepare.py.",
                {"errors": prepare_errors, "drift": prepare_drift},
            )
        )

    reconcile_errors, reconcile_outputs = reconcile.build(epic)
    reconcile_drift = sorted(
        relative
        for relative, rendered in reconcile_outputs.items()
        if not (epic / "review" / relative).is_file()
        or read_text(epic / "review" / relative) != rendered
    )
    freeze_errors, expected_freeze = freeze_module.build(epic)
    committed_freeze = load_json(epic / "review" / "freeze-manifest.json")
    freeze_drift = expected_freeze is not None and expected_freeze != committed_freeze
    if reconcile_errors or reconcile_drift or freeze_errors or freeze_drift:
        findings.append(
            finding(
                "review_semantic_integrity",
                "critical",
                "Review results, adjudications, evidence ownership, and freeze semantics must pass the authoritative validators.",
                {
                    "reconcile_errors": reconcile_errors,
                    "reconcile_drift": reconcile_drift,
                    "freeze_errors": freeze_errors,
                    "freeze_drift": freeze_drift,
                },
            )
        )

    assignments = load_many_jsonl((epic / "review" / "assignments").glob("*.jsonl"))
    results = load_many_jsonl((epic / "review" / "results").glob("*.jsonl"))
    validations = load_many_jsonl(epic.glob("shards/validation-*/decisions.jsonl"))
    exceptions = load_jsonl(epic / "consolidation" / "exceptions.jsonl")
    candidates = load_jsonl(epic / "consolidation" / "candidates.jsonl")
    result_index = {row["candidate_id"]: row for row in results}
    source_indexes = {
        "validation_decision": {row["candidate_id"]: row for row in validations},
        "identity_exception": {row["candidate_id"]: row for row in exceptions},
        "consolidation_route": {row["candidate_id"]: row for row in candidates},
    }
    approved_source_mismatches: list[str] = []
    for assignment in assignments:
        result = result_index.get(assignment["candidate_id"])
        if not result or result.get("review_status") != "approved":
            continue
        source = source_indexes[assignment["source_kind"]].get(
            assignment["candidate_id"]
        )
        if source is None:
            approved_source_mismatches.append(assignment["candidate_id"])
            continue
        source_decision = (
            prepare.CONSOLIDATION_ROUTE_DECISIONS.get(
                source.get("category"), "routed_other"
            )
            if assignment["source_kind"] == "consolidation_route"
            else source.get("decision") or source.get("status")
        )
        source_destination = (
            source.get("route_destination")
            if assignment["source_kind"] == "consolidation_route"
            else source.get("destination")
        )
        if result.get("final_decision") != source_decision or semantic_destination(
            result.get("final_decision"), result.get("destination")
        ) != semantic_destination(source_decision, source_destination):
            approved_source_mismatches.append(assignment["candidate_id"])
    if approved_source_mismatches:
        findings.append(
            finding(
                "approved_review_source_mismatch",
                "critical",
                "Approved reviews must preserve the source decision and semantic destination.",
                sorted(approved_source_mismatches),
            )
        )
    assignment_semantic_errors: list[str] = []
    for assignment in assignments:
        source_decision = assignment.get("source_decision", "")
        expected_reason = (
            "all_eligible"
            if source_decision == "eligible"
            else "all_identity_conflicts"
            if source_decision == "identity_conflict"
            else "all_routed"
            if routed(source_decision)
            else "deterministic_exclusion_sample"
        )
        source_worker = assignment.get("source_worker", "")
        reviewer = assignment.get("reviewer", "")
        same_worker = reviewer == source_worker
        if source_worker.startswith("validation-"):
            same_worker = same_worker or reviewer.removeprefix("review-") == source_worker.removeprefix("validation-")
        if same_worker or assignment.get("review_reason") != expected_reason:
            assignment_semantic_errors.append(assignment["candidate_id"])
    if assignment_semantic_errors:
        findings.append(
            finding(
                "review_assignment_semantics",
                "critical",
                "Reviewer separation and review_reason must match the authoritative source decision.",
                sorted(assignment_semantic_errors),
            )
        )

    plan_path = epic / "publication" / "publication-plan.json"
    plan = load_json(plan_path)
    plan_errors = plan_module.validate_plan(
        committed_freeze,
        (epic / "review" / "freeze-manifest.json").read_bytes(),
        plan,
    )
    if plan_errors:
        findings.append(
            finding(
                "publication_plan_integrity",
                "critical",
                "The publication plan must be the exact deterministic projection of the freeze.",
                plan_errors,
            )
        )
    return findings


def validation_pipeline_findings(epic: Path) -> list[dict[str, Any]]:
    reconciler = load_module(
        "epic327_validation_reconcile", epic / "validation" / "reconcile.py"
    )
    errors = reconciler.reconcile(epic)
    return (
        [
            finding(
                "validation_semantic_integrity",
                "critical",
                "Validation shards must preserve frozen input hashes, evidence ownership and claims, and the inclusive 24-month activity window.",
                errors,
            )
        ]
        if errors
        else []
    )


def destination_findings(
    rows: list[dict[str, Any]],
    repo: Path,
    plan_ids: set[str],
    expected_duplicates: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    expected_duplicates = expected_duplicates or {
        "delta-fund-caricaco-vc": "funds/costa-rica/caricaco-ventures.md"
    }
    errors: list[dict[str, Any]] = []
    for row in rows:
        candidate_id = row["candidate_id"]
        decision = row["decision"]
        destination = row.get("destination")
        reason: str | None = None
        if decision == "duplicate":
            if not isinstance(destination, str) or not destination.startswith("funds/"):
                reason = "duplicate destination is not a fund profile"
            elif not (repo / destination).is_file():
                reason = "duplicate destination profile does not exist"
            elif candidate_id in expected_duplicates and destination != expected_duplicates[candidate_id]:
                reason = "duplicate does not resolve to its exact canonical profile"
        elif decision == "eligible":
            if destination != "funds/" or candidate_id not in plan_ids:
                reason = "eligible destination or publication-plan membership differs"
        elif decision in ROUTED_DESTINATIONS:
            prefixes = ROUTED_DESTINATIONS[decision]
            if not isinstance(destination, str) or not destination.startswith(prefixes):
                reason = f"destination must use one of {prefixes}"
        elif decision in {"identity_conflict", "unresolved"}:
            if destination not in {None, "manual_identity_review"}:
                reason = "manual-review destination must be null or manual_identity_review"
        if reason:
            errors.append(
                {
                    "candidate_id": candidate_id,
                    "decision": decision,
                    "destination": destination,
                    "reason": reason,
                }
            )
    return (
        [
            finding(
                "terminal_destination_invalid",
                "critical",
                "Terminal destinations must match their decision vocabulary and real canonical targets.",
                errors,
            )
        ]
        if errors
        else []
    )


def profile_triplet_errors(repo: Path, paths: list[Path]) -> list[str]:
    validator = load_module(
        "epic327_validate_profiles", repo / "tools" / "seo_geo" / "validate_profiles.py"
    )
    schema, enums = validator.read_contract()
    profiles = []
    errors: list[str] = []
    for path in paths:
        try:
            profiles.append(validator.parse_profile(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
    errors.extend(validator.validate_collection(profiles, schema, enums))
    if profiles:
        canonical = next(
            (profile for profile in profiles if profile.metadata.get("locale") == "en"),
            None,
        )
        if canonical is None:
            errors.append("Wayfinder English canonical profile is absent")
        else:
            errors.extend(validator.validate_catalog_correspondence(canonical))
    expected = {
        "en": ("canonical", None),
        "pt-BR": ("complete", "fund:wayfinder-ventures:en"),
        "es": ("complete", "fund:wayfinder-ventures:en"),
    }
    for profile in profiles:
        locale = profile.metadata.get("locale")
        if locale not in expected:
            errors.append(f"{profile.path}: unexpected locale {locale}")
            continue
        status, translation_of = expected[locale]
        if profile.metadata.get("translation_status") != status:
            errors.append(f"{profile.path}: unexpected translation_status")
        if profile.metadata.get("translation_of") != translation_of:
            errors.append(f"{profile.path}: unexpected translation_of")
    return sorted(set(errors))


def normalized_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value).casefold()
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def index_sections(text: str) -> list[list[tuple[str, str]]]:
    sections: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] | None = None
    row_pattern = re.compile(r"^\| \[([^]]+)\]\((funds/[^)]+\.md)\) \|")
    for line in text.splitlines():
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = []
            continue
        match = row_pattern.match(line)
        if match and current is not None:
            current.append((match.group(1), match.group(2)))
    if current:
        sections.append(current)
    return sections


def index_link_errors(repo: Path, current_paths: set[str]) -> list[str]:
    indexes: dict[str, list[list[tuple[str, str]]]] = {}
    for name in ("README.md", "README.pt.md", "README.es.md"):
        indexes[name] = index_sections(read_text(repo / name))
    errors: list[str] = []
    reference = [[path for _, path in section] for section in indexes["README.md"]]
    for name, sections in indexes.items():
        links = [path for section in sections for _, path in section]
        if len(links) != len(set(links)):
            errors.append(f"{name}: duplicate fund links")
        if set(links) != current_paths:
            errors.append(f"{name}: fund-link set differs from canonical profiles")
        section_paths = [[path for _, path in section] for section in sections]
        if section_paths != reference:
            errors.append(f"{name}: fund-link section order differs from README.md")
        for ordinal, section in enumerate(sections, 1):
            expected = sorted(
                section,
                key=lambda row: (normalized_name(row[0]), row[1]),
            )
            if section != expected:
                errors.append(
                    f"{name}: section {ordinal} is not in canonical normalized-name order"
                )
    return errors


def publication_findings(
    repo: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[Path]]:
    profile_paths = [
        repo / WAYFINDER_PROFILE,
        repo / "translations" / "pt-BR" / WAYFINDER_PROFILE,
        repo / "translations" / "es" / WAYFINDER_PROFILE,
    ]
    profile_errors = profile_triplet_errors(repo, profile_paths)
    generator = load_module(
        "epic327_generate_entities", repo / "tools" / "seo_geo" / "generate_entities.py"
    )
    json_path = repo / "data" / "entities.json"
    csv_path = repo / "data" / "entities.csv"
    json_payload = json_path.read_bytes()
    csv_payload = csv_path.read_bytes()
    export_errors = generator.validate_export_consistency(json_payload, csv_payload)
    expected_exports = generator.build_outputs()
    export_drift = [
        path.relative_to(repo).as_posix()
        for path, payload in expected_exports.items()
        if path.read_bytes() != payload
    ]
    entities_json = json.loads(json_payload.decode("utf-8"))
    json_wayfinder = [
        row for row in entities_json["entities"] if row.get("id") == WAYFINDER_ENTITY_ID
    ]
    csv_wayfinder = [
        row
        for row in generator.parse_csv(csv_payload)
        if row.get("id") == WAYFINDER_ENTITY_ID
    ]
    current_paths = {
        path.relative_to(repo).as_posix()
        for path in repo.glob("funds/**/*.md")
        if path.name != "README.md"
    }
    index_errors = index_link_errors(repo, current_paths)
    details = {
        "profile_errors": profile_errors,
        "export_errors": export_errors,
        "export_drift": export_drift,
        "index_errors": index_errors,
        "json_export_count": len(json_wayfinder),
        "csv_export_count": len(csv_wayfinder),
        "audited_profile": WAYFINDER_PROFILE,
    }
    errors = profile_errors + export_errors + export_drift + index_errors
    if len(json_wayfinder) != 1 or len(csv_wayfinder) != 1:
        errors.append("Wayfinder export cardinality differs from one")
    return (
        [
            finding(
                "publication_surface_mismatch",
                "critical",
                "Profiles, exports, and localized indexes must be complete deterministic projections of the canonical Wayfinder profile.",
                details,
            )
        ]
        if errors
        else [],
        details,
        profile_paths,
    )


def utf8_findings(paths: Iterable[Path], repo: Path) -> list[dict[str, Any]]:
    mojibake: list[str] = []
    decode_errors: list[str] = []
    for path in sorted(set(paths)):
        try:
            text = read_text(path)
        except UnicodeDecodeError:
            decode_errors.append(path.relative_to(repo).as_posix())
            continue
        scan_text = "\n".join(
            line
            for line in text.splitlines()
            if not re.match(r"^\s*MOJIBAKE_(?:MARKERS|RE)\s*=", line)
        )
        if MOJIBAKE_RE.search(scan_text):
            mojibake.append(path.relative_to(repo).as_posix())
    return (
        [
            finding(
                "utf8_or_mojibake",
                "high",
                "Audited text must be strict UTF-8 without specific mojibake signatures.",
                {"decode_errors": decode_errors, "mojibake": mojibake},
            )
        ]
        if decode_errors or mojibake
        else []
    )


def dated_record_mismatches(
    validation_rows: list[dict[str, Any]],
    result_rows: list[dict[str, Any]],
    adjudication_rows: list[dict[str, Any]],
    evidence_rows: list[dict[str, Any]],
    cutoff: str,
) -> list[str]:
    def invalid(value: Any) -> bool:
        return not isinstance(value, str) or value > cutoff

    return sorted(
        [
            f"validation:{row.get('candidate_id')}"
            for row in validation_rows
            if row.get("cutoff_date") != cutoff or invalid(row.get("validated_on"))
        ]
        + [
            f"review:{row.get('candidate_id')}"
            for row in result_rows
            if invalid(row.get("reviewed_on"))
        ]
        + [
            f"adjudication:{row.get('candidate_id')}"
            for row in adjudication_rows
            if invalid(row.get("adjudicated_on"))
        ]
        + [
            f"evidence:{row.get('evidence_id')}"
            for row in evidence_rows
            if invalid(row.get("accessed_on"))
        ]
    )


def audit_repository(repo: Path = REPO) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    epic = repo / "research" / "epic-327"
    findings: list[dict[str, Any]] = []

    contract = load_json(epic / "contract.json")
    baseline_summary = load_json(epic / "baseline" / "summary.json")
    intake_summary = load_json(epic / "intake" / "summary.json")
    consolidation_summary = load_json(epic / "consolidation" / "summary.json")
    assignment_summary = load_json(epic / "review" / "assignment-summary.json")
    review_summary = load_json(epic / "review" / "review-summary.json")
    freeze = load_json(epic / "review" / "freeze-manifest.json")
    plan = load_json(epic / "publication" / "publication-plan.json")

    for relative, expected in sorted(baseline_summary["artifact_hashes"].items()):
        path = epic / "baseline" / relative
        actual = sha256_file(path)
        if actual != expected:
            findings.append(
                finding(
                    "baseline_hash_mismatch",
                    "critical",
                    f"Frozen baseline hash differs for {relative}.",
                    {"expected": expected, "actual": actual},
                )
            )
    for item in intake_summary["inputs"]:
        path = repo / item["path"]
        actual = sha256_file(path)
        if actual != item["sha256"]:
            findings.append(
                finding(
                    "intake_hash_mismatch",
                    "critical",
                    f"Frozen intake hash differs for {item['path']}.",
                    {"expected": item["sha256"], "actual": actual},
                )
            )

    baseline_rows = load_jsonl(epic / "baseline" / "catalog-baseline.jsonl")
    candidates_rows = load_jsonl(epic / "consolidation" / "candidates.jsonl")
    candidates, candidate_duplicates = index_unique(candidates_rows, "candidate_id")
    if candidate_duplicates:
        findings.append(
            finding(
                "candidate_identity_duplicates",
                "critical",
                "The consolidated queue contains duplicate or missing candidate IDs.",
                candidate_duplicates,
            )
        )
    declared_counts = {
        "intake.unique_candidates": intake_summary.get("unique_candidates"),
        "consolidation.unique_candidates": consolidation_summary.get("unique_candidates"),
        "consolidation.reconciled_records": consolidation_summary.get(
            "reconciled_records"
        ),
        "actual": len(candidates),
    }
    if set(declared_counts.values()) != {EXPECTED_CANDIDATES}:
        findings.append(
            finding(
                "candidate_universe_mismatch",
                "critical",
                "The frozen queue must reconcile to exactly 1,088 candidates.",
                declared_counts,
            )
        )
    if len(baseline_rows) != baseline_summary["catalog"]["profiles"]:
        findings.append(
            finding(
                "baseline_count_mismatch",
                "critical",
                "Baseline profile count differs from its frozen summary.",
            )
        )

    validation_rows = load_many_jsonl(epic.glob("shards/validation-*/decisions.jsonl"))
    assignment_paths = sorted((epic / "review" / "assignments").glob("*.jsonl"))
    result_paths = sorted((epic / "review" / "results").glob("*.jsonl"))
    assignment_rows = load_many_jsonl(assignment_paths)
    result_rows = load_many_jsonl(result_paths)
    adjudication_rows = load_jsonl(epic / "review" / "adjudications.jsonl")
    validations, validation_duplicates = index_unique(validation_rows, "candidate_id")
    assignments, assignment_duplicates = index_unique(assignment_rows, "candidate_id")
    results, result_duplicates = index_unique(result_rows, "candidate_id")
    adjudications, adjudication_duplicates = index_unique(
        adjudication_rows, "candidate_id"
    )
    duplicate_details = {
        "validation": validation_duplicates,
        "assignments": assignment_duplicates,
        "results": result_duplicates,
        "adjudications": adjudication_duplicates,
    }
    if any(duplicate_details.values()):
        findings.append(
            finding(
                "review_identity_duplicates",
                "critical",
                "Review ledgers contain duplicate or missing candidate IDs.",
                duplicate_details,
            )
        )

    missing_results = sorted(set(assignments) - set(results))
    extra_results = sorted(set(results) - set(assignments))
    bad_bindings = sorted(
        cid
        for cid in set(assignments) & set(results)
        if results[cid].get("assignment_sha256") != record_sha256(assignments[cid])
    )
    changed = {
        cid: row
        for cid, row in results.items()
        if row.get("review_status") == "changes_requested"
    }
    missing_adjudications = sorted(set(changed) - set(adjudications))
    bad_adjudication_bindings = sorted(
        cid
        for cid in set(changed) & set(adjudications)
        if adjudications[cid].get("review_record_sha256") != record_sha256(changed[cid])
    )
    if missing_results or extra_results or bad_bindings:
        findings.append(
            finding(
                "review_result_integrity",
                "critical",
                "Assignments and results must be complete and hash-bound.",
                {
                    "missing_results": missing_results,
                    "extra_results": extra_results,
                    "bad_assignment_hashes": bad_bindings,
                },
            )
        )
    if missing_adjudications or bad_adjudication_bindings:
        findings.append(
            finding(
                "adjudication_integrity",
                "critical",
                "Every requested change must have a hash-bound adjudication.",
                {
                    "missing": missing_adjudications,
                    "bad_review_hashes": bad_adjudication_bindings,
                },
            )
        )
    summary_counts = {
        "assignments_actual": len(assignments),
        "assignments_declared": assignment_summary.get("assignment_records"),
        "assignments_review_declared": review_summary.get("assignment_records"),
        "results_actual": len(results),
        "results_declared": review_summary.get("result_records"),
        "adjudications_actual": len(adjudications),
        "changes_requested": len(changed),
    }
    if len({summary_counts[k] for k in summary_counts if "assignment" in k}) != 1 or (
        summary_counts["results_actual"] != summary_counts["results_declared"]
    ):
        findings.append(
            finding(
                "review_summary_mismatch",
                "critical",
                "Review summaries differ from their ledgers.",
                summary_counts,
            )
        )
    assignment_digest = sha256_bytes(
        dump_jsonl(sorted(assignments.values(), key=lambda row: row["candidate_id"])).encode(
            "utf-8"
        )
    )
    result_digest = sha256_bytes(
        dump_jsonl(sorted(results.values(), key=lambda row: row["candidate_id"])).encode(
            "utf-8"
        )
    )
    review_digest_rows = sorted(
        [{"record_kind": "review", "record": row} for row in result_rows]
        + [
            {"record_kind": "adjudication", "record": row}
            for row in adjudication_rows
        ],
        key=lambda row: (row["record"]["candidate_id"], row["record_kind"]),
    )
    review_digest = sha256_bytes(dump_jsonl(review_digest_rows).encode("utf-8"))
    freeze_path = epic / "review" / "freeze-manifest.json"
    freeze_digest = sha256_file(freeze_path)
    eligible_digest = sha256_bytes(
        dump_jsonl(sorted(freeze.get("eligible_records", []), key=lambda row: row["candidate_id"])).encode(
            "utf-8"
        )
    )
    provenance_hashes = {
        "review_summary.assignments": (
            review_summary.get("assignments_sha256"),
            assignment_digest,
        ),
        "review_summary.results": (review_summary.get("results_sha256"), result_digest),
        "freeze.source_decisions": (
            freeze.get("source_decisions_sha256"),
            assignment_digest,
        ),
        "freeze.review_records": (freeze.get("review_records_sha256"), review_digest),
        "plan.source_manifest": (plan.get("source_manifest_sha256"), freeze_digest),
        "plan.source_decisions": (
            plan.get("source_decisions_sha256"),
            assignment_digest,
        ),
        "plan.review_records": (plan.get("review_records_sha256"), review_digest),
        "plan.eligible_records": (
            plan.get("eligible_records_sha256"),
            eligible_digest,
        ),
    }
    bad_provenance_hashes = {
        label: {"declared": declared, "actual": actual}
        for label, (declared, actual) in provenance_hashes.items()
        if declared != actual
    }
    if bad_provenance_hashes:
        findings.append(
            finding(
                "provenance_hash_mismatch",
                "critical",
                "Review, freeze, and publication provenance hashes must form one chain.",
                bad_provenance_hashes,
            )
        )
    findings.extend(review_pipeline_findings(epic))
    findings.extend(validation_pipeline_findings(epic))

    origins: dict[str, str] = {}
    for cid, candidate in candidates.items():
        decision, _ = origin_decision(candidate, validations.get(cid))
        if isinstance(decision, str):
            origins[cid] = decision
    findings.extend(coverage_findings(origins, assignments))

    final_rows, unresolved = resolve_final_decisions(
        candidates, validations, results, adjudications, contract["cutoff_date"]
    )
    if unresolved or len(final_rows) != EXPECTED_CANDIDATES:
        findings.append(
            finding(
                "terminal_ledger_incomplete",
                "critical",
                "Every candidate must have exactly one terminal decision and destination.",
                {"record_count": len(final_rows), "unresolved": unresolved},
            )
        )
    eligible = [row for row in final_rows if row["decision"] == "eligible"]
    freeze_ids = [row.get("candidate_id") for row in freeze.get("eligible_records", [])]
    plan_candidates = [
        row
        for batch in plan.get("batches", [])
        for row in batch.get("candidates", [])
    ]
    plan_ids = [row.get("candidate_id") for row in plan_candidates]
    expected_duplicates = {
        cid: candidate["canonical_profile"]
        for cid, candidate in candidates.items()
        if candidate.get("status") == "duplicate"
        and isinstance(candidate.get("canonical_profile"), str)
    }
    expected_duplicates["delta-fund-caricaco-vc"] = (
        "funds/costa-rica/caricaco-ventures.md"
    )
    findings.extend(
        destination_findings(
            final_rows, repo, set(plan_ids), expected_duplicates
        )
    )
    if (
        [row["candidate_id"] for row in eligible] != [WAYFINDER_ID]
        or freeze.get("status") != "frozen"
        or freeze.get("eligible_count") != 1
        or freeze_ids != [WAYFINDER_ID]
        or plan.get("eligible_count") != 1
        or plan.get("batch_count") != 1
        or plan_ids != [WAYFINDER_ID]
    ):
        findings.append(
            finding(
                "freeze_plan_mismatch",
                "critical",
                "The unique frozen and planned eligible record must be Wayfinder Ventures.",
                {
                    "final_eligible": [row["candidate_id"] for row in eligible],
                    "freeze": freeze_ids,
                    "plan": plan_ids,
                },
            )
        )

    publication_issues, publication_details, profile_paths = publication_findings(repo)
    findings.extend(publication_issues)

    order_errors: list[str] = []
    for path in assignment_paths + result_paths:
        if not ordered_by(load_jsonl(path), "candidate_id"):
            order_errors.append(path.relative_to(repo).as_posix())
    if not ordered_by(candidates_rows, "candidate_id"):
        order_errors.append("research/epic-327/consolidation/candidates.jsonl")
    if not ordered_by(final_rows, "candidate_id"):
        order_errors.append("research/epic-327/final-audit/final-decisions.jsonl")
    if order_errors:
        findings.append(
            finding(
                "nondeterministic_order",
                "high",
                "Candidate ledgers must be ordered by candidate_id.",
                order_errors,
            )
        )

    text_paths = sorted(epic.rglob("*.json")) + sorted(epic.rglob("*.jsonl"))
    text_paths += sorted(epic.rglob("*.md")) + sorted(epic.rglob("*.py"))
    text_paths += [repo / name for name in ("README.md", "README.pt.md", "README.es.md")]
    text_paths += profile_paths + [
        repo / "data" / "entities.csv",
        repo / "data" / "entities.json",
    ]
    findings.extend(utf8_findings(text_paths, repo))

    cutoff_values = {
        "contract": contract.get("cutoff_date"),
        "baseline": baseline_summary.get("cutoff_date"),
        "freeze": freeze.get("cutoff_date"),
        "plan": plan.get("cutoff_date"),
    }
    evidence_rows = load_many_jsonl(
        list(epic.glob("shards/*/*evidence*.jsonl"))
        + list((epic / "review" / "evidence").glob("*.jsonl"))
    )
    date_mismatches = dated_record_mismatches(
        validation_rows,
        result_rows,
        adjudication_rows,
        evidence_rows,
        EXPECTED_CUTOFF,
    )
    if set(cutoff_values.values()) != {EXPECTED_CUTOFF} or date_mismatches:
        findings.append(
            finding(
                "cutoff_mismatch",
                "high",
                "All final artifacts must use the frozen cutoff date.",
                {
                    "artifacts": cutoff_values,
                    "dated_record_mismatches": date_mismatches,
                },
            )
        )
    if intake_summary.get("unparsed_rows") != 741:
        findings.append(
            finding(
                "limitation_count_mismatch",
                "high",
                "The intake limitation must preserve 741 unparsed rows.",
                {"actual": intake_summary.get("unparsed_rows")},
            )
        )

    findings.sort(key=lambda row: (SEVERITY_ORDER[row["severity"]], row["code"]))
    final_decisions_text = dump_jsonl(final_rows)
    severity_counts = dict(sorted(Counter(row["severity"] for row in findings).items()))
    decision_counts = dict(sorted(Counter(row["decision"] for row in final_rows).items()))
    gates = [
        {
            "gate": gate,
            "status": gate_status(findings, codes),
        }
        for gate, codes in (
            ("baseline_intake_hashes", {"baseline_hash_mismatch", "intake_hash_mismatch", "baseline_count_mismatch"}),
            ("candidate_terminal_ledger", {"candidate_universe_mismatch", "candidate_identity_duplicates", "terminal_ledger_incomplete", "terminal_destination_invalid"}),
            ("mandatory_review_and_sample", {"mandatory_review_coverage", "exclusion_sample_coverage", "review_assignment_determinism"}),
            ("official_validation_integrity", {"validation_semantic_integrity"}),
            ("review_and_adjudication_integrity", {"review_identity_duplicates", "review_result_integrity", "adjudication_integrity", "review_summary_mismatch", "provenance_hash_mismatch", "review_semantic_integrity", "approved_review_source_mismatch", "review_assignment_semantics"}),
            ("freeze_and_publication_plan", {"freeze_plan_mismatch", "publication_plan_integrity"}),
            ("publication_surfaces", {"publication_surface_mismatch"}),
            ("order_and_determinism", {"nondeterministic_order"}),
            ("utf8_and_mojibake", {"utf8_or_mojibake"}),
            ("cutoff_and_limitations", {"cutoff_mismatch", "limitation_count_mismatch"}),
        )
    ]
    blocking = severity_counts.get("critical", 0) + severity_counts.get("high", 0)
    report = {
        "schema_version": "1.0",
        "epic": 327,
        "issue": 338,
        "cutoff_date": EXPECTED_CUTOFF,
        "status": "pass" if blocking == 0 else "blocked",
        "counts": {
            "candidate_universe": len(candidates),
            "review_assignments": len(assignments),
            "review_results": len(results),
            "adjudications": len(adjudications),
            "final_decisions": len(final_rows),
            "decision_counts": decision_counts,
            "findings_by_severity": severity_counts,
            "unparsed_intake_rows": intake_summary.get("unparsed_rows"),
        },
        "gates": gates,
        "findings": findings,
        "publication": publication_details,
        "provenance": {
            "baseline_commit": contract.get("baseline_commit"),
            "final_decisions_sha256": sha256_bytes(final_decisions_text.encode("utf-8")),
            "network_access": False,
            "precedence": ["adjudication", "review", "origin"],
        },
        "limitations": [
            "The audited universe is the frozen 1,088-candidate intake queue, not a claim of market totality.",
            "The source intake preserved 741 unparsed rows outside the candidate ledger.",
            "The audit performs no live HTTP checks; it validates frozen official-source evidence and publication artifacts.",
            "Identity-conflict and unresolved records use destination_kind manual_review; their original destination may be null or manual_identity_review.",
            "routed_other destinations are abstract terminal ecosystem handoffs accepted by the schema; they are not required to be physical paths and do not represent pending fund publication.",
            f"Eligibility and recency are evaluated at the {EXPECTED_CUTOFF} cutoff.",
        ],
    }
    return report, final_rows


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# Epic 327 final audit",
        "",
        f"Status: **{report['status']}**",
        "",
        f"Cutoff: `{report['cutoff_date']}`",
        "",
        "## Summary",
        "",
        f"- Candidate universe: {counts['candidate_universe']}",
        f"- Review assignments/results: {counts['review_assignments']}/{counts['review_results']}",
        f"- Final terminal decisions: {counts['final_decisions']}",
        f"- Critical/high findings: {counts['findings_by_severity'].get('critical', 0)}/{counts['findings_by_severity'].get('high', 0)}",
        "",
        "## Gates",
        "",
        "| Gate | Status |",
        "| --- | --- |",
    ]
    lines.extend(f"| {row['gate']} | {row['status']} |" for row in report["gates"])
    lines += ["", "## Terminal decisions", "", "| Decision | Count |", "| --- | ---: |"]
    lines.extend(
        f"| {decision} | {count} |"
        for decision, count in report["counts"]["decision_counts"].items()
    )
    lines += ["", "## Findings", ""]
    if report["findings"]:
        lines.extend(
            f"- **{row['severity']} / {row['code']}**: {row['message']}"
            for row in report["findings"]
        )
    else:
        lines.append("No findings.")
    lines += ["", "## Limitations", ""]
    lines.extend(f"- {value}" for value in report["limitations"])
    lines += [
        "",
        "The machine-readable report and terminal ledger are `audit-report.json` and `final-decisions.jsonl`.",
        "",
    ]
    return "\n".join(lines)


def build_outputs(repo: Path = REPO) -> dict[str, str]:
    report, final_rows = audit_repository(repo)
    return {
        "final-decisions.jsonl": dump_jsonl(final_rows),
        "audit-report.json": json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "FINAL_AUDIT.md": render_markdown(report),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify generated artifacts")
    parser.add_argument(
        "--allow-findings",
        action="store_true",
        help="return success while a prerequisite integration is still pending",
    )
    args = parser.parse_args()
    outputs = build_outputs()
    stale: list[str] = []
    for relative, rendered in outputs.items():
        path = HERE / relative
        if args.check:
            if not path.exists() or read_text(path) != rendered:
                stale.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
    if stale:
        print("Stale final-audit artifacts: " + ", ".join(stale), file=sys.stderr)
        return 1
    report = json.loads(outputs["audit-report.json"])
    print(
        f"Epic 327 final audit: {report['status']} "
        f"({report['counts']['final_decisions']} terminal decisions)."
    )
    return 0 if report["status"] == "pass" or args.allow_findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
