#!/usr/bin/env python3
"""Validate the normalized Mexico, Central America and Caribbean intake."""

from __future__ import annotations

import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC = HERE.parents[1]
EXPECTED_FIELDS = {
    "schema_version",
    "candidate_id",
    "name",
    "country_occurrences",
    "occurrence_count",
    "baseline_status",
    "baseline_matches",
}
OPTIONAL_FIELDS = {"normalization_notes"}
STATUSES = {"new", "exact_name", "alias", "identity_collision", "unresolved"}
COUNTRIES = {"MX", "CR", "CU", "DO", "SV", "GT", "HT", "HN", "NI", "PA"}
MOJIBAKE = (
    "\u00c3\u0192",
    "\u00c3\u201a",
    "\u00ef\u00bf\u00bd",
    "\u00c3\u00a2\u00e2\u201a\u00ac",
    "\ufffd",
    "\x07",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join("".join(char if char.isalnum() else " " for char in value.casefold()).split())


def validate() -> list[str]:
    errors: list[str] = []
    intake = read_jsonl(HERE / "intake.jsonl")
    gaps = read_json(HERE / "gaps.json")
    summary = read_json(HERE / "summary.json")
    baseline = read_jsonl(EPIC / "baseline" / "identity-index.jsonl")

    ids = [row.get("candidate_id") for row in intake]
    if len(ids) != len(set(ids)):
        errors.append("intake.jsonl: candidate_id duplicado")
    normalized_names = [normalize_name(row.get("name", "")) for row in intake]
    if len(normalized_names) != len(set(normalized_names)):
        errors.append("intake.jsonl: nome normalizado duplicado")

    baseline_names: dict[str, list[str]] = {}
    baseline_aliases: dict[str, list[str]] = {}
    for row in baseline:
        baseline_names.setdefault(normalize_name(row["canonical_name"]), []).append(row["profile_path"])
        for alias in row["aliases"]:
            baseline_aliases.setdefault(normalize_name(alias), []).append(row["profile_path"])

    for line_number, row in enumerate(intake, start=1):
        fields = set(row)
        if not EXPECTED_FIELDS <= fields or fields - EXPECTED_FIELDS - OPTIONAL_FIELDS:
            errors.append(f"intake.jsonl:{line_number}: campos inválidos")
        if row.get("schema_version") != "1.0":
            errors.append(f"intake.jsonl:{line_number}: schema_version inválida")
        if row.get("baseline_status") not in STATUSES:
            errors.append(f"intake.jsonl:{line_number}: baseline_status inválido")
        countries = row.get("country_occurrences", {})
        if not countries or not set(countries) <= COUNTRIES:
            errors.append(f"intake.jsonl:{line_number}: países inválidos")
        if row.get("occurrence_count") != sum(countries.values()):
            errors.append(f"intake.jsonl:{line_number}: occurrence_count divergente")
        if any(not isinstance(count, int) or count < 1 for count in countries.values()):
            errors.append(f"intake.jsonl:{line_number}: contagem de país inválida")
        if not all(path.startswith("funds/") and path.endswith(".md") for path in row.get("baseline_matches", [])):
            errors.append(f"intake.jsonl:{line_number}: baseline_matches inválido")

        key = normalize_name(row["name"])
        exact = sorted(set(baseline_names.get(key, [])))
        alias = sorted(set(baseline_aliases.get(key, [])))
        expected_matches = sorted(set(exact + alias))
        expected_status = (
            "identity_collision" if len(expected_matches) > 1
            else "exact_name" if exact
            else "alias" if alias
            else "new"
        )
        if row["baseline_matches"] != expected_matches or row["baseline_status"] != expected_status:
            errors.append(f"intake.jsonl:{line_number}: reconciliação do baseline divergente")

    materialized = sum(row["occurrence_count"] for row in intake)
    if summary.get("raw_occurrences") != materialized + gaps.get("unparsed_rows", -1):
        errors.append("summary.json: equação de ocorrências não fecha")
    expected_summary = {
        "pages_expected": 62,
        "pages_processed": 62,
        "canonical_candidates": len(intake),
        "baseline_matches": sum(bool(row["baseline_matches"]) for row in intake),
        "new_candidates": sum(row["baseline_status"] == "new" for row in intake),
        "unresolved_candidates": sum(row["baseline_status"] == "unresolved" for row in intake),
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(f"summary.json: {key} divergente")
    if gaps.get("unparsed_rows") != sum(gaps.get("unparsed_rows_by_country", {}).values()):
        errors.append("gaps.json: soma por país divergente")
    if gaps.get("page_errors") != 0:
        errors.append("gaps.json: página congelada não processada")

    forbidden = {"description", "thesis", "stage", "check", "source", "url", "discovery_reference"}
    for row in intake:
        if forbidden & set(row):
            errors.append(f"intake.jsonl: campo factual ou de fonte proibido em {row['candidate_id']}")

    for path in (HERE / "intake.jsonl", HERE / "gaps.json", HERE / "summary.json"):
        text = path.read_text(encoding="utf-8")
        for marker in MOJIBAKE:
            if marker in text:
                errors.append(f"{path.name}: possível mojibake {marker!r}")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação do intake falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Intake normalizado validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
