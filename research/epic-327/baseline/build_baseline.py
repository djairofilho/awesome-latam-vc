#!/usr/bin/env python3
"""Build the frozen fund-catalog baseline for issue #328."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[3]
BASELINE = Path(__file__).resolve().parent
BASELINE_COMMIT = "4190d8c59d47e50784383bf6a83efb6249859bdb"
GENERATED = ("catalog-baseline.jsonl", "identity-index.jsonl", "summary.json")
SECONDARY_IDENTITY_HOSTS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "medium.com",
    "x.com",
    "youtube.com",
}


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def git_output(*args: str) -> bytes:
    result = subprocess.run(("git", *args), cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} falhou: {detail}")
    return result.stdout


def profile_paths() -> list[str]:
    paths = git_output(
        "ls-tree", "-r", "--name-only", BASELINE_COMMIT, "--", "funds"
    ).decode("utf-8").splitlines()
    return sorted(
        path
        for path in paths
        if path.endswith(".md") and not path.endswith("/README.md")
    )


def profile_bytes(relative_path: str) -> bytes:
    return git_output("show", f"{BASELINE_COMMIT}:{relative_path}")


def parse_frontmatter(data: bytes, relative_path: str) -> dict[str, Any]:
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{relative_path}: front matter JSON ausente")
    try:
        closing = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{relative_path}: front matter sem fechamento") from exc
    return json.loads("\n".join(lines[1:closing]))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_host(url: str | None) -> str | None:
    if not url:
        return None
    host = (urlsplit(url).hostname or "").casefold().rstrip(".")
    return host.removeprefix("www.") or None


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(without_marks.casefold().split())


def input_digest(inputs: Iterable[tuple[str, bytes]]) -> str:
    digest = hashlib.sha256()
    for path, data in sorted(inputs):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return digest.hexdigest()


def build_artifacts() -> dict[str, bytes]:
    catalog: list[dict[str, Any]] = []
    inputs: list[tuple[str, bytes]] = []
    domains: dict[str, list[str]] = defaultdict(list)

    for path in profile_paths():
        data = profile_bytes(path)
        inputs.append((path, data))
        profile = parse_frontmatter(data, path)
        aliases = sorted(set(profile.get("aliases") or []), key=str.casefold)
        domain = normalize_host(profile.get("official_website"))
        row = {
            "schema_version": "1.0",
            "entity_id": profile["entity_id"],
            "profile_path": path,
            "profile_sha256": sha256(data),
            "slug": profile["slug"],
            "name": profile["name"],
            "aliases": aliases,
            "official_website": profile.get("official_website"),
            "identity_domain": domain,
            "base_geography": profile["base_geography"],
            "countries_covered": profile["countries_covered"],
        }
        catalog.append(row)
        if domain:
            domains[domain].append(path)

    identities: list[dict[str, Any]] = []
    for profile in catalog:
        domain = profile["identity_domain"]
        collisions = sorted(domains.get(domain, [])) if domain else []
        if domain is None:
            quality = "missing"
        elif domain in SECONDARY_IDENTITY_HOSTS:
            quality = "secondary_host"
        elif len(collisions) > 1:
            quality = "shared"
        else:
            quality = "unique"
        identities.append(
            {
                "schema_version": "1.0",
                "entity_id": profile["entity_id"],
                "profile_path": profile["profile_path"],
                "canonical_name": profile["name"],
                "aliases": profile["aliases"],
                "normalized_names": sorted(
                    {
                        normalize_name(profile["name"]),
                        *(normalize_name(alias) for alias in profile["aliases"]),
                    }
                ),
                "identity_domain": domain,
                "domain_quality": quality,
                "domain_collision_paths": collisions,
            }
        )

    catalog.sort(key=lambda row: row["profile_path"])
    identities.sort(key=lambda row: row["profile_path"])
    artifacts = {
        "catalog-baseline.jsonl": jsonl_bytes(catalog),
        "identity-index.jsonl": jsonl_bytes(identities),
    }
    alias_values = sum(len(row["aliases"]) for row in catalog)
    country_counts = Counter(
        row["base_geography"].get("code", "unknown") for row in catalog
    )
    collision_domains = {
        domain: sorted(paths)
        for domain, paths in sorted(domains.items())
        if len(paths) > 1
    }
    summary = {
        "schema_version": "1.0",
        "epic": 327,
        "issue": 328,
        "cutoff_date": "2026-08-02",
        "baseline_ref": "origin/main",
        "baseline_commit": BASELINE_COMMIT,
        "funds_tree_sha": git_output("rev-parse", f"{BASELINE_COMMIT}:funds")
        .decode("ascii")
        .strip(),
        "input_digest_sha256": input_digest(inputs),
        "catalog": {
            "profiles": len(catalog),
            "profiles_with_aliases": sum(bool(row["aliases"]) for row in catalog),
            "alias_values": alias_values,
            "profiles_with_identity_domain": sum(
                row["identity_domain"] is not None for row in catalog
            ),
            "profiles_without_identity_domain": sum(
                row["identity_domain"] is None for row in catalog
            ),
            "unique_identity_domains": len(domains),
            "domain_collisions": collision_domains,
            "base_geography_counts": dict(sorted(country_counts.items())),
        },
        "snapshot_policy": {
            "network_access": False,
            "discovery_performed": False,
            "external_intake_imported": False,
            "source": "Git objects at the frozen commit",
        },
        "artifact_hashes": {
            name: sha256(content) for name, content in sorted(artifacts.items())
        },
    }
    artifacts["summary.json"] = json_bytes(summary)
    return artifacts


def write_or_check(artifacts: dict[str, bytes], check: bool) -> int:
    mismatches: list[str] = []
    for name in GENERATED:
        expected = artifacts[name]
        path = BASELINE / name
        if check:
            if not path.is_file() or path.read_bytes() != expected:
                mismatches.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_bytes(expected)
    if mismatches:
        print("Baseline ausente ou divergente: " + ", ".join(mismatches), file=sys.stderr)
        return 1
    print(f"Baseline delta {'verificada' if check else 'gerada'}: {len(GENERATED)} artefatos.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(build_artifacts(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
