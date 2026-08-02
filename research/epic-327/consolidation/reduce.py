#!/usr/bin/env python3
"""Conservatively reduce regional identity triage into validation shards."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "consolidation"
SHARDS = (
    "triage-mexico-cac",
    "triage-andean",
    "triage-southern-cone-brazil",
)
ROUTED_CATEGORIES = {
    "accelerator",
    "angel_network",
    "funding_platform",
    "private_equity",
    "public_program",
    "startup_studio",
    "venture_and_investment_services",
}
POSITIVE_STATUSES = {
    "identity_confirmed",
    "official_identity_resolved",
    "fund_candidate",
}
ROUTED_STATUSES = {"routed", "official_route_resolved"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: JSON inválido: {exc}") from exc
    return rows


def dump_jsonl(rows: list[dict]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def domain_from(record: dict) -> str | None:
    domain = record.get("official_domain")
    if not domain and record.get("official_url"):
        domain = urlsplit(record["official_url"]).hostname
    if not domain:
        return None
    domain = domain.lower().strip().rstrip(".")
    return domain[4:] if domain.startswith("www.") else domain


def partition(candidate_id: str) -> int:
    return int(hashlib.sha256(candidate_id.encode("utf-8")).hexdigest(), 16) % 3


def collect_inputs() -> tuple[dict[str, dict], dict[str, dict], list[str]]:
    groups: dict[str, dict] = {}
    evidence: dict[str, dict] = {}
    errors: list[str] = []
    for shard_name in SHARDS:
        shard = EPIC / "shards" / shard_name
        intake_path = shard / "intake.jsonl"
        triage_path = shard / "triage.jsonl"
        evidence_path = shard / "official-evidence.jsonl"
        if not intake_path.exists() or not triage_path.exists():
            errors.append(f"{shard_name}: intake.jsonl ou triage.jsonl ausente")
            continue
        try:
            intake_rows = load_jsonl(intake_path)
            triage_rows = load_jsonl(triage_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        triage_by_id = {row.get("candidate_id"): row for row in triage_rows}
        if len(triage_by_id) != len(triage_rows):
            errors.append(f"{shard_name}: candidate_id duplicado na triagem")
        for row in intake_rows:
            candidate_id = row["candidate_id"]
            triage = triage_by_id.get(candidate_id)
            if triage is None:
                errors.append(f"{shard_name}: {candidate_id} sem triagem")
                continue
            group = groups.setdefault(
                candidate_id,
                {
                    "names": set(),
                    "countries": Counter(),
                    "source_shards": set(),
                    "baseline_profiles": set(),
                    "triage": [],
                },
            )
            group["names"].add(row["name"])
            group["countries"].update(row["country_occurrences"])
            group["source_shards"].add(shard_name)
            group["baseline_profiles"].update(row.get("baseline_matches", []))
            group["triage"].append(triage)
        extra_ids = set(triage_by_id) - {row["candidate_id"] for row in intake_rows}
        for candidate_id in sorted(extra_ids):
            errors.append(f"{shard_name}: {candidate_id} sem intake")
        if evidence_path.exists():
            for row in load_jsonl(evidence_path):
                evidence_id = row.get("evidence_id")
                if evidence_id in evidence and evidence[evidence_id] != row:
                    errors.append(f"{evidence_id}: evidência divergente entre shards")
                evidence[evidence_id] = row
    return groups, evidence, errors


def preliminary(candidate_id: str, group: dict) -> dict:
    names = sorted(group["names"], key=lambda value: (len(value), value.casefold()))
    triage = group["triage"]
    profile_targets = set(group["baseline_profiles"])
    profile_targets.update(
        record["canonical_profile"]
        for record in triage
        if record.get("canonical_profile")
    )
    profiles = {target for target in profile_targets if target.startswith("funds/")}
    catalog_routes = {
        target for target in profile_targets if not target.startswith("funds/")
    }
    domains = {domain for record in triage if (domain := domain_from(record))}
    evidence_ids = {
        evidence_id
        for record in triage
        for evidence_id in record.get("evidence_ids", [])
    }
    statuses = {
        record.get("status", record.get("triage_status")) for record in triage
    }
    categories = {
        category
        for record in triage
        if (category := record.get("category", record.get("category_hint")))
        and category != "unresolved"
    }
    destinations = {
        record["route_destination"]
        for record in triage
        if record.get("route_destination")
    }
    destinations.update(catalog_routes)
    notes = []
    status = "unresolved"
    canonical_profile = None
    category = sorted(categories)[0] if len(categories) == 1 else None
    route_destination = sorted(destinations)[0] if len(destinations) == 1 else None

    if len(profiles) > 1 or len(domains) > 1 or len(destinations) > 1:
        status = "identity_conflict"
        notes.append("conflicting_identity_keys")
    elif profiles:
        status = "duplicate"
        canonical_profile = next(iter(profiles))
    elif statuses & ROUTED_STATUSES or categories & ROUTED_CATEGORIES or destinations:
        if route_destination:
            status = "routed"
        else:
            status = "identity_conflict"
            notes.append("route_without_destination")
    elif (
        statuses & POSITIVE_STATUSES
        or category in {"fund", "fund_candidate", "vc_firm", "corporate_vc"}
    ):
        if len(domains) == 1 and evidence_ids:
            status = "ready_for_validation"
        else:
            notes.append("positive_identity_missing_domain_or_evidence")

    record = {
        "schema_version": "1.0",
        "candidate_id": candidate_id,
        "name": names[0],
        "aliases": sorted(set(names[1:]), key=str.casefold),
        "country_occurrences": dict(sorted(group["countries"].items())),
        "occurrence_count": sum(group["countries"].values()),
        "source_shards": sorted(group["source_shards"]),
        "official_domains": sorted(domains),
        "canonical_profile": canonical_profile,
        "canonical_candidate_id": None,
        "category": category,
        "status": status,
        "route_destination": route_destination,
        "evidence_ids": sorted(evidence_ids),
        "validation_partition": None,
        "reducer_notes": sorted(notes),
    }
    return record


def resolve_domains(records: list[dict]) -> None:
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if len(record["official_domains"]) == 1:
            by_domain[record["official_domains"][0]].append(record)
    for domain_records in by_domain.values():
        if len(domain_records) < 2:
            continue
        profile_targets = {
            record["canonical_profile"]
            for record in domain_records
            if record["canonical_profile"]
        }
        if len(profile_targets) > 1:
            for record in domain_records:
                record["status"] = "identity_conflict"
                record["canonical_profile"] = None
                record["canonical_candidate_id"] = None
                record["reducer_notes"] = sorted(
                    set(record["reducer_notes"]) | {"domain_maps_to_multiple_profiles"}
                )
            continue
        if profile_targets:
            profile = next(iter(profile_targets))
            for record in domain_records:
                record["status"] = "duplicate"
                record["canonical_profile"] = profile
                record["canonical_candidate_id"] = None
                record["route_destination"] = None
            continue
        candidates = [
            record
            for record in domain_records
            if record["status"] in {"ready_for_validation", "unresolved"}
        ]
        if len(candidates) < 2:
            continue
        canonical = min(candidates, key=lambda record: record["candidate_id"])
        aliases = set(canonical["aliases"])
        for record in candidates:
            if record is canonical:
                continue
            aliases.add(record["name"])
            aliases.update(record["aliases"])
            record["status"] = "duplicate"
            record["canonical_candidate_id"] = canonical["candidate_id"]
            record["route_destination"] = None
        canonical["aliases"] = sorted(aliases - {canonical["name"]}, key=str.casefold)


def build() -> tuple[list[str], dict[str, str]]:
    groups, evidence, errors = collect_inputs()
    records = [preliminary(candidate_id, groups[candidate_id]) for candidate_id in sorted(groups)]
    resolve_domains(records)
    for record in records:
        if record["status"] == "ready_for_validation":
            record["validation_partition"] = partition(record["candidate_id"])
        else:
            record["validation_partition"] = None

    schema = load_json(EPIC / "schemas" / "consolidated-candidate.schema.json")
    validator = Draft202012Validator(schema)
    for index, record in enumerate(records, 1):
        for error in validator.iter_errors(record):
            errors.append(f"candidates.jsonl:{index}: {error.message}")

    partitions = {
        number: [
            record
            for record in records
            if record["validation_partition"] == number
        ]
        for number in range(3)
    }
    assigned = [record["candidate_id"] for rows in partitions.values() for record in rows]
    if len(assigned) != len(set(assigned)):
        errors.append("candidato atribuído a mais de um shard de validação")
    counts = Counter(record["status"] for record in records)
    summary = {
        "schema_version": "1.0",
        "epic": 327,
        "issue": 333,
        "input_shard_records": sum(len(group["triage"]) for group in groups.values()),
        "unique_candidates": len(records),
        "input_occurrences": sum(record["occurrence_count"] for record in records),
        "status_counts": dict(sorted(counts.items())),
        "validation_partition_counts": {
            str(number): len(rows) for number, rows in partitions.items()
        },
        "evidence_records": len(evidence),
        "eligibility_decisions": 0,
    }
    outputs = {
        "candidates.jsonl": dump_jsonl(records),
        "evidence.jsonl": dump_jsonl([evidence[key] for key in sorted(evidence)]),
        "summary.json": json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    }
    for number, rows in partitions.items():
        outputs[f"validation-{number}.jsonl"] = dump_jsonl(rows)
    return errors, outputs


def output_path(name: str) -> Path:
    if name.startswith("validation-"):
        number = name.removeprefix("validation-").removesuffix(".jsonl")
        return EPIC / "shards" / f"validation-{number}" / "candidates.jsonl"
    return HERE / name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors, outputs = build()
    if errors:
        print("Consolidação falhou:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1
    for name, rendered in outputs.items():
        path = output_path(name)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != rendered:
                print(f"{path}: ausente ou desatualizado", file=sys.stderr)
                return 1
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered, encoding="utf-8", newline="\n")
    print("Candidatos consolidados e particionados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
