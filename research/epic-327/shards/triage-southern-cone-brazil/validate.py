#!/usr/bin/env python3
"""Validate the normalized Southern Cone and Brazil intake shard."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPECTED_COUNTRIES = ["AR", "BR", "CL", "PY", "UY"]
EXPECTED_PAGES = 83
ALLOWED_BASELINE = {"new", "exact_name", "alias", "identity_collision", "unresolved"}
REQUIRED_FIELDS = {
    "schema_version",
    "candidate_id",
    "name",
    "country_occurrences",
    "occurrence_count",
    "baseline_status",
    "baseline_matches",
}
OPTIONAL_FIELDS = {"normalization_notes"}
FORBIDDEN_KEYS = {"discovery_reference", "source", "source_url", "url"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate() -> list[str]:
    errors: list[str] = []
    rows = load_jsonl(HERE / "intake.jsonl")
    gaps = load_json(HERE / "gaps.json")
    summary = load_json(HERE / "summary.json")

    ids: set[str] = set()
    names: set[str] = set()
    materialized = 0
    baseline_matches = 0
    new_candidates = 0
    unresolved_candidates = 0

    for index, row in enumerate(rows, start=1):
        keys = set(row)
        if not REQUIRED_FIELDS <= keys:
            errors.append(f"intake.jsonl:{index}: campos obrigatórios ausentes")
        if keys - REQUIRED_FIELDS - OPTIONAL_FIELDS:
            errors.append(f"intake.jsonl:{index}: campos adicionais")
        if keys & FORBIDDEN_KEYS:
            errors.append(f"intake.jsonl:{index}: referência de descoberta proibida")
        if row.get("schema_version") != "1.0":
            errors.append(f"intake.jsonl:{index}: schema_version inválido")
        candidate_id = row.get("candidate_id", "")
        if not re.fullmatch(r"delta-fund-[a-z0-9]+(?:-[a-z0-9]+)*", candidate_id):
            errors.append(f"intake.jsonl:{index}: candidate_id inválido")
        if candidate_id in ids:
            errors.append(f"intake.jsonl:{index}: candidate_id duplicado")
        ids.add(candidate_id)
        normalized_name = " ".join(str(row.get("name", "")).casefold().split())
        if not normalized_name or normalized_name in names:
            errors.append(f"intake.jsonl:{index}: nome vazio ou duplicado")
        names.add(normalized_name)
        occurrences = row.get("country_occurrences", {})
        if not occurrences or not set(occurrences) <= set(EXPECTED_COUNTRIES):
            errors.append(f"intake.jsonl:{index}: country_occurrences inválido")
        if any(not isinstance(value, int) or value < 1 for value in occurrences.values()):
            errors.append(f"intake.jsonl:{index}: contagem de país inválida")
        count = sum(occurrences.values())
        if row.get("occurrence_count") != count:
            errors.append(f"intake.jsonl:{index}: occurrence_count divergente")
        materialized += count
        status = row.get("baseline_status")
        if status not in ALLOWED_BASELINE:
            errors.append(f"intake.jsonl:{index}: baseline_status inválido")
        matches = row.get("baseline_matches")
        if not isinstance(matches, list) or any(
            not re.fullmatch(r"funds/.+\.md", value) for value in matches
        ):
            errors.append(f"intake.jsonl:{index}: baseline_matches inválido")
        if status in {"exact_name", "alias", "identity_collision"}:
            baseline_matches += 1
            if not matches:
                errors.append(f"intake.jsonl:{index}: match sem perfil canônico")
        elif matches:
            errors.append(f"intake.jsonl:{index}: perfil canônico sem match")
        if status == "new":
            new_candidates += 1
        if status == "unresolved":
            unresolved_candidates += 1

    if summary.get("countries") != EXPECTED_COUNTRIES:
        errors.append("summary.json: countries divergente")
    if summary.get("pages_expected") != EXPECTED_PAGES:
        errors.append("summary.json: pages_expected divergente")
    if summary.get("pages_processed") != EXPECTED_PAGES:
        errors.append("summary.json: pages_processed divergente")
    if summary.get("canonical_candidates") != len(rows):
        errors.append("summary.json: canonical_candidates divergente")
    if summary.get("baseline_matches") != baseline_matches:
        errors.append("summary.json: baseline_matches divergente")
    if summary.get("new_candidates") != new_candidates:
        errors.append("summary.json: new_candidates divergente")
    if summary.get("unresolved_candidates") != unresolved_candidates:
        errors.append("summary.json: unresolved_candidates divergente")

    unmaterialized = gaps.get("unmaterialized_occurrences")
    if materialized + unmaterialized != summary.get("raw_occurrences"):
        errors.append("summary.json: equação de ocorrências divergente")
    if gaps.get("truncated_name_occurrences") != unmaterialized:
        errors.append("gaps.json: truncados devem explicar as ocorrências não materializadas")
    if gaps.get("page_failures") != 0 or gaps.get("pagination_divergences") != 0:
        errors.append("gaps.json: cobertura de páginas divergente")
    if summary.get("gaps", {}).get("unmaterialized_occurrences") != unmaterialized:
        errors.append("summary.json: gaps divergente")

    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação do intake sul e Brasil falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Intake sul e Brasil validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
