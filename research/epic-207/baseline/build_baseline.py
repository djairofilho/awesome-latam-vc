"""Build the offline baseline for issue #209 deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
BASELINE = Path(__file__).resolve().parent
BASELINE_COMMIT = "876eb331f84371410ea442dbc1f457685e36a460"
EPIC_16_PREFIX = "research/epic-16/issue-22"
GENERATED = (
    "catalog-baseline.jsonl",
    "identity-index.jsonl",
    "prior-candidates.jsonl",
    "prior-sources.jsonl",
    "queue-manifest.jsonl",
    "pending-changes.jsonl",
    "baseline-summary.json",
)
POSITIVE_DECISIONS = {"elegível", "duplicado"}
NEGATIVE_MEMORY_DECISIONS = {"excluído", "ecossistema", "inativo"}
SECONDARY_IDENTITY_HOSTS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "medium.com",
    "x.com",
    "youtube.com",
}
SOURCE_FAMILIES = {
    18: "directories_associations",
    19: "allocators",
    20: "sector_maps_cvc",
    21: "regional_sources",
}
PRIOR_SOURCE_ID = re.compile(r"^src-22-i(?P<issue>\d+)-")


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def read_jsonl_bytes(data: bytes) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in data.decode("utf-8").splitlines()
        if line.strip()
    ]


def git_output(*args: str) -> bytes:
    result = subprocess.run(
        ("git", *args),
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} falhou: {message}")
    return result.stdout


def baseline_file_bytes(relative_path: str) -> bytes:
    return git_output("show", f"{BASELINE_COMMIT}:{relative_path}")


def baseline_profile_paths() -> list[str]:
    paths = git_output(
        "ls-tree", "-r", "--name-only", BASELINE_COMMIT, "--", "funds"
    ).decode("utf-8").splitlines()
    return sorted(
        path
        for path in paths
        if path.endswith(".md") and not path.endswith("/README.md")
    )


def read_baseline_jsonl(relative_path: str) -> list[dict[str, Any]]:
    return read_jsonl_bytes(baseline_file_bytes(relative_path))


def parse_profile(data: bytes, relative_path: str) -> dict[str, Any]:
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{relative_path}: frontmatter JSON ausente")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise ValueError(f"{relative_path}: frontmatter sem fechamento") from error
    return json.loads("\n".join(lines[1:closing]))


def normalize_host(url: str | None) -> str | None:
    if not url:
        return None
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return host.removeprefix("www.") or None


def normalize_name(value: str) -> str:
    return " ".join(value.casefold().split())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def input_digest(inputs: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for relative_path, data in sorted(inputs):
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest()


def split_balanced(records: list[dict[str, Any]], parts: int) -> list[list[dict[str, Any]]]:
    quotient, remainder = divmod(len(records), parts)
    result: list[list[dict[str, Any]]] = []
    start = 0
    for index in range(parts):
        size = quotient + (1 if index < remainder else 0)
        result.append(records[start : start + size])
        start += size
    return result


def queue_record(
    queue_id: str,
    record_type: str,
    members: list[str],
    *,
    source_issue: int | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "queue_id": queue_id,
        "record_type": record_type,
        "member_count": len(members),
        "members": members,
        "research_performed": False,
    }
    if source_issue is not None:
        record["source_issue"] = source_issue
    return record


def reconcile_canonical_profile(
    candidate: dict[str, Any],
    catalog: list[dict[str, Any]],
) -> None:
    inherited = candidate.get("canonical_profile")
    if not inherited:
        return
    catalog_paths = {record["profile_path"] for record in catalog}
    if inherited in catalog_paths:
        return

    domain = candidate.get("canonical_domain")
    domain_matches = [
        record["profile_path"]
        for record in catalog
        if domain and record["identity_domain"] == domain
    ]
    if len(domain_matches) != 1:
        raise ValueError(
            "canonical_profile herdado sem destino único por domínio: "
            f"{candidate['candidate_id']} -> {inherited}; "
            f"domínio={domain!r}; correspondências={sorted(domain_matches)}"
        )

    candidate["inherited_canonical_profile"] = inherited
    candidate["canonical_profile"] = domain_matches[0]
    candidate["canonical_profile_resolution"] = "reconciled_by_unique_domain"


def build_catalog() -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[tuple[str, bytes]],
    dict[str, list[str]],
]:
    profile_paths = baseline_profile_paths()
    profile_inputs: list[tuple[str, bytes]] = []
    catalog: list[dict[str, Any]] = []
    for relative in profile_paths:
        data = baseline_file_bytes(relative)
        profile_inputs.append((relative, data))
        profile = parse_profile(data, relative)
        host = normalize_host(profile.get("official_website"))
        aliases = sorted(set(profile.get("aliases") or []), key=str.casefold)
        catalog.append(
            {
                "schema_version": "1.0",
                "profile_path": relative,
                "profile_sha256": sha256(data),
                "entity_id": profile["entity_id"],
                "slug": profile["slug"],
                "name": profile["name"],
                "aliases": aliases,
                "official_website": profile.get("official_website"),
                "identity_domain": host,
                "base_geography": profile["base_geography"],
                "countries_covered": profile["countries_covered"],
                "in_brazil_directory": relative.startswith("funds/brazil/"),
            }
        )

    domains: dict[str, list[str]] = defaultdict(list)
    for profile in catalog:
        if profile["identity_domain"]:
            domains[profile["identity_domain"]].append(profile["profile_path"])

    identities: list[dict[str, Any]] = []
    for profile in catalog:
        domain = profile["identity_domain"]
        collision_paths = sorted(domains.get(domain, [])) if domain else []
        if domain is None:
            quality = "missing"
        elif domain in SECONDARY_IDENTITY_HOSTS:
            quality = "secondary_host"
        elif len(collision_paths) > 1:
            quality = "shared"
        else:
            quality = "unique"
        names = sorted(
            {normalize_name(profile["name"]), *(normalize_name(a) for a in profile["aliases"])}
        )
        identities.append(
            {
                "schema_version": "1.0",
                "entity_id": profile["entity_id"],
                "profile_path": profile["profile_path"],
                "canonical_name": profile["name"],
                "aliases": profile["aliases"],
                "normalized_names": names,
                "identity_domain": domain,
                "domain_quality": quality,
                "domain_collision_paths": collision_paths,
            }
        )
    return catalog, identities, profile_inputs, domains


def build_prior_memory(
    candidates: list[dict[str, Any]],
    sources: list[dict[str, Any]],
    evidence_urls: set[str],
    catalog: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    positive = sorted(
        (record for record in candidates if record["decision"] in POSITIVE_DECISIONS),
        key=lambda record: record["candidate_id"],
    )
    negative = sorted(
        (record for record in candidates if record["decision"] in NEGATIVE_MEMORY_DECISIONS),
        key=lambda record: record["candidate_id"],
    )
    insufficient = sorted(
        (record for record in candidates if record["decision"] == "evidência insuficiente"),
        key=lambda record: record["candidate_id"],
    )
    other = [
        record
        for record in candidates
        if record["decision"]
        not in POSITIVE_DECISIONS
        | NEGATIVE_MEMORY_DECISIONS
        | {"evidência insuficiente"}
    ]
    if other:
        raise ValueError(f"decisões da epic 16 sem fila: {sorted({r['decision'] for r in other})}")

    insufficient_with_domain = [
        record for record in insufficient if record.get("canonical_domain")
    ]
    insufficient_without_domain = [
        record for record in insufficient if not record.get("canonical_domain")
    ]
    domain_parts = split_balanced(insufficient_with_domain, 3)
    candidate_queues: dict[str, str] = {}
    for record in positive:
        candidate_queues[record["candidate_id"]] = "prior-positive"
    for record in negative:
        candidate_queues[record["candidate_id"]] = "prior-negative-memory"
    for index, part in enumerate(domain_parts):
        suffix = chr(ord("a") + index)
        for record in part:
            candidate_queues[record["candidate_id"]] = (
                f"prior-insufficient-domain-{suffix}"
            )
    for record in insufficient_without_domain:
        candidate_queues[record["candidate_id"]] = "prior-insufficient-no-domain"

    prior_candidates = []
    for line_number, record in enumerate(candidates, start=1):
        enriched = dict(record)
        reconcile_canonical_profile(enriched, catalog)
        enriched["baseline_source"] = (
            "research/epic-16/issue-22/candidates.jsonl"
        )
        enriched["baseline_source_line"] = line_number
        enriched["baseline_queue"] = candidate_queues[record["candidate_id"]]
        enriched["research_performed_by_issue_209"] = False
        prior_candidates.append(enriched)
    prior_candidates.sort(key=lambda record: record["candidate_id"])
    catalog_paths = {record["profile_path"] for record in catalog}
    orphan_profiles = sorted(
        record["candidate_id"]
        for record in prior_candidates
        if record.get("canonical_profile") not in catalog_paths
        and record.get("canonical_profile") is not None
    )
    if orphan_profiles:
        raise ValueError(
            "candidatos com canonical_profile órfão após reconciliação: "
            + ", ".join(orphan_profiles)
        )

    prior_sources = []
    for line_number, record in enumerate(sources, start=1):
        match = PRIOR_SOURCE_ID.match(record["source_id"])
        if not match:
            raise ValueError(
                f"source_id consolidado sem issue de origem: {record['source_id']}"
            )
        issue = int(match.group("issue"))
        if issue not in SOURCE_FAMILIES:
            raise ValueError(f"fonte anterior com issue inesperada: {issue}")
        enriched = dict(record)
        enriched["baseline_source"] = (
            "research/epic-16/issue-22/source-inventory.jsonl"
        )
        enriched["baseline_source_line"] = line_number
        enriched["prior_issue"] = issue
        enriched["source_family"] = SOURCE_FAMILIES[issue]
        enriched["baseline_role"] = (
            "official_evidence"
            if record["initial_url"] in evidence_urls
            else "discovery_or_coverage"
        )
        enriched["reuse_policy"] = (
            "do_not_retry"
            if record["result"] == "indisponível"
            else "baseline_only"
        )
        enriched["normalized_host"] = normalize_host(record["initial_url"])
        enriched["counts_as_new_discovery"] = False
        enriched["research_performed_by_issue_209"] = False
        prior_sources.append(enriched)
    prior_sources.sort(key=lambda record: record["source_id"])

    queues = [
        queue_record(
            "prior-positive",
            "candidate",
            [record["candidate_id"] for record in positive],
        ),
        queue_record(
            "prior-negative-memory",
            "candidate",
            [record["candidate_id"] for record in negative],
        ),
    ]
    for index, part in enumerate(domain_parts):
        suffix = chr(ord("a") + index)
        queues.append(
            queue_record(
                f"prior-insufficient-domain-{suffix}",
                "candidate",
                [record["candidate_id"] for record in part],
            )
        )
    queues.append(
        queue_record(
            "prior-insufficient-no-domain",
            "candidate",
            [record["candidate_id"] for record in insufficient_without_domain],
        )
    )
    for issue in sorted(SOURCE_FAMILIES):
        members = sorted(
            record["source_id"]
            for record in prior_sources
            if int(record["prior_issue"]) == issue
        )
        queues.append(
            queue_record(
                f"sources-issue-{issue}",
                "source",
                members,
                source_issue=issue,
            )
        )
    return prior_candidates, prior_sources, queues


def build_artifacts() -> dict[str, bytes]:
    catalog, identities, profile_inputs, domains = build_catalog()
    candidate_path = f"{EPIC_16_PREFIX}/candidates.jsonl"
    evidence_path = f"{EPIC_16_PREFIX}/evidence.jsonl"
    source_path = f"{EPIC_16_PREFIX}/source-inventory.jsonl"
    candidate_data = baseline_file_bytes(candidate_path)
    evidence_data = baseline_file_bytes(evidence_path)
    source_data = baseline_file_bytes(source_path)
    candidates = read_jsonl_bytes(candidate_data)
    evidence = read_jsonl_bytes(evidence_data)
    sources = read_jsonl_bytes(source_data)
    evidence_urls = {record["url"] for record in evidence}
    prior_candidates, prior_sources, queues = build_prior_memory(
        candidates, sources, evidence_urls, catalog
    )

    brazil_members = [
        record["entity_id"] for record in catalog if record["in_brazil_directory"]
    ]
    guard_members = [
        record["entity_id"] for record in catalog if not record["in_brazil_directory"]
    ]
    queues.extend(
        [
            queue_record("catalog-br", "profile", sorted(brazil_members)),
            queue_record(
                "catalog-collision-guard", "profile", sorted(guard_members)
            ),
        ]
    )
    queues.sort(key=lambda record: record["queue_id"])

    pending = [
        {
            "schema_version": "1.0",
            "change_id": "github-pr-225",
            "change_type": "pull_request",
            "repository": "djairofilho/awesome-latam-vc",
            "number": 225,
            "status": "pending",
            "imported": False,
            "files_imported": [],
            "treatment": "record_only",
            "notes": (
                "Mudança externa ao snapshot. A issue #209 registra sua existência "
                "sem importar arquivos, nomes ou decisões."
            ),
        }
    ]

    artifacts: dict[str, bytes] = {
        "catalog-baseline.jsonl": jsonl_bytes(catalog),
        "identity-index.jsonl": jsonl_bytes(identities),
        "prior-candidates.jsonl": jsonl_bytes(prior_candidates),
        "prior-sources.jsonl": jsonl_bytes(prior_sources),
        "queue-manifest.jsonl": jsonl_bytes(queues),
        "pending-changes.jsonl": jsonl_bytes(pending),
    }

    catalog_domains = [record["identity_domain"] for record in catalog]
    brazil = [record for record in catalog if record["in_brazil_directory"]]
    brazil_domains = [record["identity_domain"] for record in brazil]
    decision_counts = Counter(record["decision"] for record in prior_candidates)
    source_result_counts = Counter(record["result"] for record in prior_sources)
    source_issue_counts = Counter(str(record["prior_issue"]) for record in prior_sources)
    collision_domains = {
        domain: sorted(paths)
        for domain, paths in sorted(domains.items())
        if len(paths) > 1
    }
    summary = {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 209,
        "baseline_commit": BASELINE_COMMIT,
        "input_digest_sha256": input_digest(
            [
                *profile_inputs,
                (candidate_path, candidate_data),
                (evidence_path, evidence_data),
                (source_path, source_data),
            ]
        ),
        "offline_policy": {
            "network_access": False,
            "cvm_queries": 0,
            "discovery_performed": False,
            "pr_225_imported": False,
        },
        "catalog": {
            "profiles": len(catalog),
            "brazil_directory_profiles": len(brazil),
            "collision_guard_profiles": len(catalog) - len(brazil),
            "profiles_with_identity_domain": sum(
                domain is not None for domain in catalog_domains
            ),
            "profiles_without_identity_domain": sum(
                domain is None for domain in catalog_domains
            ),
            "unique_identity_domains": len(
                {domain for domain in catalog_domains if domain}
            ),
            "profiles_with_aliases": sum(bool(record["aliases"]) for record in catalog),
            "alias_values": sum(len(record["aliases"]) for record in catalog),
            "domain_collisions": collision_domains,
        },
        "brazil_catalog": {
            "profiles": len(brazil),
            "profiles_with_identity_domain": sum(
                domain is not None for domain in brazil_domains
            ),
            "profiles_without_identity_domain": sum(
                domain is None for domain in brazil_domains
            ),
            "unique_identity_domains": len(
                {domain for domain in brazil_domains if domain}
            ),
            "profiles_with_aliases": sum(bool(record["aliases"]) for record in brazil),
            "alias_values": sum(len(record["aliases"]) for record in brazil),
        },
        "epic_16_memory": {
            "candidates": len(prior_candidates),
            "candidate_decisions": dict(sorted(decision_counts.items())),
            "sources": len(prior_sources),
            "source_results": dict(sorted(source_result_counts.items())),
            "sources_by_issue": dict(sorted(source_issue_counts.items())),
        },
        "queues": {
            record["queue_id"]: record["member_count"] for record in queues
        },
        "pending_changes": len(pending),
        "artifact_hashes": {
            name: sha256(content) for name, content in sorted(artifacts.items())
        },
    }
    artifacts["baseline-summary.json"] = json_bytes(summary)
    return artifacts


def write_or_check(artifacts: dict[str, bytes], check: bool) -> int:
    mismatches: list[str] = []
    for name in GENERATED:
        expected = artifacts[name]
        path = BASELINE / name
        if check:
            if not path.exists():
                mismatches.append(f"ausente: {path.relative_to(ROOT).as_posix()}")
            elif path.read_bytes() != expected:
                mismatches.append(f"divergente: {path.relative_to(ROOT).as_posix()}")
        else:
            path.write_bytes(expected)
    if check and mismatches:
        for mismatch in mismatches:
            print(mismatch, file=sys.stderr)
        print(
            "Execute build_baseline.py sem --check para regenerar a baseline.",
            file=sys.stderr,
        )
        return 1
    action = "verificada" if check else "gerada"
    print(f"Baseline offline {action}: {len(GENERATED)} artefatos.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Falha quando os artefatos canônicos diferem da geração.",
    )
    args = parser.parse_args()
    return write_or_check(build_artifacts(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
