#!/usr/bin/env python3
"""Verify issue #77 coverage, deterministic sample, evidence and hashes."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


REVIEW = Path(__file__).resolve().parent
ROOT = REVIEW.parents[2]
CONSOLIDATION = ROOT / "research" / "epic-62" / "consolidation"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_sha256(path: Path) -> str:
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def validate(review_dir: Path = REVIEW) -> list[str]:
    errors: list[str] = []
    manifest = read_json(review_dir / "review-manifest.json")
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    evidence += read_json(review_dir / "review-evidence.json")
    results = read_json(review_dir / "review-results.json")
    divergences = read_json(review_dir / "divergences.json")
    publishable = read_json(review_dir / "publishable-manifest.json")
    cross_catalog = read_json(review_dir / "cross-catalog-checks.json")
    category = read_json(CONSOLIDATION / "category-resolutions.json")

    candidate_by_id = {row["candidate_id"]: row for row in candidates}
    result_by_id = {row["candidate_id"]: row for row in results}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}

    current_eligible = sorted(
        row["candidate_id"] for row in candidates if row["decision"] == "elegível"
    )
    current_routed = sorted(
        row["candidate_id"]
        for row in candidates
        if row["decision"].startswith("encaminhado-")
    )
    current_cross = sorted(
        row["candidate_id"] for row in category["cross_category_resolutions"]
    )
    current_vehicles = sorted(
        row["candidate_id"] for row in category["vehicle_resolutions"]
    )
    expected_groups = {
        "eligible": current_eligible,
        "routed": current_routed,
        "cross_category": current_cross,
        "vehicles": current_vehicles,
    }
    for group, expected in expected_groups.items():
        frozen = sorted(manifest["mandatory_groups"][group])
        if frozen != expected:
            errors.append(f"grupo congelado divergente: {group}")
        missing = sorted(set(expected) - set(result_by_id))
        if missing:
            errors.append(f"{group} sem revisão: {', '.join(missing)}")
        missing_tag = sorted(
            candidate_id
            for candidate_id in expected
            if candidate_id in result_by_id
            and group not in result_by_id[candidate_id]["reviewed_groups"]
        )
        if missing_tag:
            errors.append(f"{group} sem marca de cobertura: {', '.join(missing_tag)}")

    excluded = sorted(
        (
            hashlib.sha256(
                f"{row['candidate_id']}|issue-77|2026-07-27".encode()
            ).hexdigest(),
            row["candidate_id"],
        )
        for row in candidates
        if row["decision"] == "excluído"
    )
    sample_size = math.ceil(len(excluded) * 0.2)
    expected_sample = [
        {"candidate_id": candidate_id, "selection_hash": digest}
        for digest, candidate_id in excluded[:sample_size]
    ]
    if manifest["excluded_sample"]["selected"] != expected_sample:
        errors.append("amostra determinística de excluídos divergente")
    missing_sample = sorted(
        set(item["candidate_id"] for item in expected_sample) - set(result_by_id)
    )
    if missing_sample:
        errors.append(f"amostra sem revisão: {', '.join(missing_sample)}")

    required = set(current_eligible + current_routed + current_cross + current_vehicles)
    required.update(item["candidate_id"] for item in expected_sample)
    if set(result_by_id) != required:
        errors.append("review-results.json não corresponde à união congelada")

    for candidate_id, result in result_by_id.items():
        if candidate_id not in candidate_by_id:
            errors.append(f"candidato desconhecido: {candidate_id}")
            continue
        for evidence_id in result["official_evidence_ids"]:
            row = evidence_by_id.get(evidence_id)
            if not row:
                errors.append(f"{candidate_id}: evidência ausente {evidence_id}")
            elif row["source_type"] != "official":
                errors.append(f"{candidate_id}: evidência não oficial {evidence_id}")
        if not result["official_evidence_ids"]:
            errors.append(f"{candidate_id}: nenhuma evidência oficial")

        if result["resolved_decision"] == "elegível":
            claims = {
                claim["field"]
                for evidence_id in result["official_evidence_ids"]
                for claim in evidence_by_id[evidence_id]["claims"]
                if claim["finding"] == "confirmed"
            }
            required_claims = {
                "structured_program",
                "activity",
                "external_access",
                "latam_access",
            }
            if not required_claims.issubset(claims):
                errors.append(f"{candidate_id}: prova elegível incompleta")
            checks = result["checks"]
            if any(
                checks[field] != "confirmed"
                for field in (
                    "official_category",
                    "recent_activity",
                    "external_latam_access",
                )
            ):
                errors.append(f"{candidate_id}: gates elegíveis não confirmados")

        if result["checks"]["funds_epics_63_64_65"] != "checked":
            errors.append(f"{candidate_id}: catálogos não verificados")

    divergence_ids = {row["divergence_id"] for row in divergences}
    referenced_divergences = {
        divergence_id
        for row in results
        for divergence_id in row["divergence_ids"]
    }
    if divergence_ids != referenced_divergences:
        errors.append("divergências e resultados não são bidirecionais")
    if any(row["status"] != "resolved" for row in divergences):
        errors.append("há divergência não resolvida")

    expected_publishable = sorted(
        row["candidate_id"]
        for row in results
        if row["resolved_decision"] == "elegível"
    )
    if publishable["candidate_ids"] != expected_publishable:
        errors.append("manifesto publicável diverge das decisões revisadas")
    if publishable["candidate_count"] != len(expected_publishable):
        errors.append("contagem do manifesto publicável inválida")
    if publishable["profiles_created"] != 0:
        errors.append("a revisão não pode criar perfis")

    expected_catalogs = {"funds", "epic-63", "epic-64", "epic-65"}
    if set(cross_catalog["catalogs_checked"]) != expected_catalogs:
        errors.append("comparação entre catálogos incompleta")
    if cross_catalog["reviewed_candidates"] != len(results):
        errors.append("contagem da comparação entre catálogos inválida")
    if cross_catalog["silent_duplicates"]:
        errors.append("há duplicata silenciosa entre catálogos")

    source_paths = {
        "candidates.jsonl": CONSOLIDATION / "candidates.jsonl",
        "evidence.jsonl": CONSOLIDATION / "evidence.jsonl",
        "source-inventory.jsonl": CONSOLIDATION / "source-inventory.jsonl",
        "category-resolutions.json": CONSOLIDATION / "category-resolutions.json",
        "registry-index.json": CONSOLIDATION / "registry-index.json",
        "consolidation-manifest.json": CONSOLIDATION / "consolidation-manifest.json",
    }
    for name, expected_hash in manifest["source_hashes"].items():
        path = source_paths.get(name)
        if path is None or normalized_sha256(path) != expected_hash:
            errors.append(f"hash de entrada inválido: {name}")

    for name, expected_hash in (manifest.get("output_hashes") or {}).items():
        path = review_dir / name
        if not path.exists() or normalized_sha256(path) != expected_hash:
            errors.append(f"hash inválido: {name}")
    if manifest["status"] != "complete":
        errors.append("manifesto de revisão não está completo")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Revisão independente inválida:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Revisão independente da issue #77 validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
