#!/usr/bin/env python3
"""Validate the read-only Andean intake artifacts for issues #329 and #331."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC = HERE.parents[1]
INTAKE_KEYS = {
    "schema_version",
    "candidate_id",
    "name",
    "country_occurrences",
    "occurrence_count",
    "baseline_status",
    "baseline_matches",
    "normalization_notes",
}
REQUIRED_INTAKE_KEYS = INTAKE_KEYS - {"normalization_notes"}
SUMMARY_KEYS = {
    "schema_version",
    "worker_id",
    "countries",
    "pages_expected",
    "pages_processed",
    "raw_occurrences",
    "canonical_candidates",
    "baseline_matches",
    "new_candidates",
    "unresolved_candidates",
    "gaps",
}
GAPS_KEYS = {
    "schema_version",
    "worker_id",
    "pages_expected",
    "pages_processed",
    "unparsed_rows",
    "access_failures",
    "pagination_variance",
}
STATUSES = {"new", "exact_name", "alias", "identity_collision", "unresolved"}
COUNTRIES = {"BO", "CO", "EC", "PE", "VE"}
FORBIDDEN_KEYS = {"discovery_reference", "source", "source_url", "url"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    value = value.lower().replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def baseline_index() -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in load_jsonl(EPIC / "baseline" / "identity-index.jsonl"):
        for name in row["normalized_names"]:
            result.setdefault(name, []).append(row)
    return result


def validate() -> list[str]:
    errors: list[str] = []
    intake = load_jsonl(HERE / "intake.jsonl")
    gaps = load_json(HERE / "gaps.json")
    summary = load_json(HERE / "summary.json")
    baseline = baseline_index()

    if set(summary) != SUMMARY_KEYS:
        errors.append("summary.json: chaves divergentes do contrato")
    if set(gaps) != GAPS_KEYS:
        errors.append("gaps.json: chaves divergentes do contrato")

    candidate_ids = [row.get("candidate_id") for row in intake]
    if candidate_ids != sorted(candidate_ids):
        errors.append("intake.jsonl: candidate_id fora de ordem")
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("intake.jsonl: candidate_id duplicado")

    total_occurrences = 0
    status_counts = {status: 0 for status in STATUSES}
    for index, row in enumerate(intake, start=1):
        keys = set(row)
        if not REQUIRED_INTAKE_KEYS <= keys <= INTAKE_KEYS:
            errors.append(f"intake.jsonl:{index}: chaves inválidas")
            continue
        if FORBIDDEN_KEYS & keys:
            errors.append(f"intake.jsonl:{index}: proveniência privada versionada")
        if row["schema_version"] != "1.0":
            errors.append(f"intake.jsonl:{index}: schema_version inválida")
        if not re.fullmatch(r"delta-fund-[a-z0-9]+(?:-[a-z0-9]+)*", row["candidate_id"]):
            errors.append(f"intake.jsonl:{index}: candidate_id inválido")
        if "..." in row["name"] or "http://" in row["name"] or "https://" in row["name"]:
            errors.append(f"intake.jsonl:{index}: nome truncado ou URL materializada")
        countries = row["country_occurrences"]
        if not countries or set(countries) - COUNTRIES:
            errors.append(f"intake.jsonl:{index}: países inválidos")
        if any(not isinstance(value, int) or value < 1 for value in countries.values()):
            errors.append(f"intake.jsonl:{index}: contagem de país inválida")
        occurrence_count = sum(countries.values())
        if occurrence_count != row["occurrence_count"]:
            errors.append(f"intake.jsonl:{index}: occurrence_count divergente")
        total_occurrences += occurrence_count

        status = row["baseline_status"]
        if status not in STATUSES:
            errors.append(f"intake.jsonl:{index}: baseline_status inválido")
            continue
        status_counts[status] += 1
        matches = baseline.get(normalize_name(row["name"]), [])
        expected_paths = sorted(match["profile_path"] for match in matches)
        if row["baseline_matches"] != expected_paths:
            errors.append(f"intake.jsonl:{index}: baseline_matches divergente")
        if len(matches) > 1:
            expected_status = "identity_collision"
        elif len(matches) == 1:
            expected_status = (
                "exact_name"
                if normalize_name(matches[0]["canonical_name"])
                == normalize_name(row["name"])
                else "alias"
            )
        else:
            expected_status = "new"
        if status != expected_status:
            errors.append(f"intake.jsonl:{index}: baseline_status divergente")

    if summary.get("worker_id") != "triage-andean" or gaps.get("worker_id") != "triage-andean":
        errors.append("worker_id divergente")
    if summary.get("countries") != ["BO", "CO", "EC", "PE", "VE"]:
        errors.append("summary.json: países divergentes")
    if summary.get("pages_expected") != 39 or summary.get("pages_processed") != 39:
        errors.append("summary.json: cobertura de páginas incompleta")
    if gaps.get("pages_expected") != 39 or gaps.get("pages_processed") != 39:
        errors.append("gaps.json: cobertura de páginas incompleta")
    if summary.get("canonical_candidates") != len(intake):
        errors.append("summary.json: canonical_candidates divergente")
    baseline_matches = sum(
        status_counts[status] for status in ("exact_name", "alias", "identity_collision")
    )
    if summary.get("baseline_matches") != baseline_matches:
        errors.append("summary.json: baseline_matches divergente")
    if summary.get("new_candidates") != status_counts["new"]:
        errors.append("summary.json: new_candidates divergente")
    if summary.get("unresolved_candidates") != status_counts["unresolved"]:
        errors.append("summary.json: unresolved_candidates divergente")
    if summary.get("raw_occurrences") != total_occurrences + gaps.get("unparsed_rows", -1):
        errors.append("summary.json: raw_occurrences não reconcilia intake e gaps")
    if summary.get("gaps", {}).get("unparsed_rows") != gaps.get("unparsed_rows"):
        errors.append("summary.json: gaps não reconciliado")
    if gaps.get("access_failures") != 0:
        errors.append("gaps.json: falhas de acesso inesperadas")

    for path in (HERE / "intake.jsonl", HERE / "gaps.json", HERE / "summary.json"):
        text = path.read_text(encoding="utf-8").lower()
        if "openvc" in text or "https://www.openvc" in text:
            errors.append(f"{path.name}: fonte privada materializada")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("Validação do intake andino falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Intake andino validado: 39 páginas e contagens reconciliadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
