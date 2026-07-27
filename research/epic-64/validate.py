#!/usr/bin/env python3
"""Valida o contrato e os conjuntos de pesquisa da epic 64."""

from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parent
SCHEMAS = {
    "candidates.jsonl": "platform-candidate.schema.json",
    "evidence.jsonl": "evidence.schema.json",
    "source-inventory.jsonl": "source-inventory.schema.json",
    "coverage-matrix.jsonl": "coverage-record.schema.json",
    "run-manifest.jsonl": "run-manifest-record.schema.json",
}
SOURCE_CATEGORIES = {
    "regulator",
    "public_ecosystem",
    "official_platform",
    "discovery",
}
LATAM_COUNTRIES = {
    "AR",
    "BO",
    "BR",
    "CL",
    "CO",
    "CR",
    "CU",
    "DO",
    "EC",
    "GT",
    "HN",
    "HT",
    "MX",
    "NI",
    "PA",
    "PE",
    "PY",
    "SV",
    "UY",
    "VE",
}
OFFICIAL_TYPES = {
    "official_platform",
    "official_operator",
    "official_regulator",
    "official_document",
}
REGULATORY_TYPES = {"official_regulator", "official_document"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return [], [f"{path}: não foi possível ler como UTF-8: {exc}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"{path}:{line_number}: linha vazia não é válida em JSONL")
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: JSON inválido: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: cada linha deve conter um objeto")
            continue
        records.append(value)
    return records, errors


def contains_key(value: Any, forbidden: str) -> bool:
    if isinstance(value, dict):
        return forbidden in value or any(
            contains_key(child, forbidden) for child in value.values()
        )
    if isinstance(value, list):
        return any(contains_key(child, forbidden) for child in value)
    return False


def subtract_months(value: date, months: int) -> date:
    total = value.year * 12 + value.month - 1 - months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def record_label(path: Path, index: int) -> str:
    return f"{path}:{index + 1}"


def load_validators() -> tuple[dict[str, Draft202012Validator], list[str]]:
    validators: dict[str, Draft202012Validator] = {}
    errors: list[str] = []
    for filename, schema_name in SCHEMAS.items():
        path = ROOT / "schemas" / schema_name
        try:
            schema = read_json(path)
            Draft202012Validator.check_schema(schema)
            validators[filename] = Draft202012Validator(
                schema,
                format_checker=FormatChecker(),
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, SchemaError) as exc:
            errors.append(f"{path}: schema inválido: {exc}")
    return validators, errors


def validate_schema_records(
    dataset: Path,
    validators: dict[str, Draft202012Validator],
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    loaded: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []
    for filename, validator in validators.items():
        path = dataset / filename
        if not path.exists():
            errors.append(f"{path}: arquivo obrigatório ausente")
            loaded[filename] = []
            continue
        records, read_errors = read_jsonl(path)
        loaded[filename] = records
        errors.extend(read_errors)
        for index, record in enumerate(records):
            for validation_error in sorted(
                validator.iter_errors(record),
                key=lambda item: tuple(str(part) for part in item.absolute_path),
            ):
                location = "/".join(str(part) for part in validation_error.absolute_path)
                suffix = f" ({location})" if location else ""
                errors.append(
                    f"{record_label(path, index)}: {validation_error.message}{suffix}"
                )
    return loaded, errors


def unique_map(
    records: list[dict[str, Any]],
    key: str,
    path: Path,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        identifier = record.get(key)
        if not isinstance(identifier, str):
            continue
        if identifier in result:
            errors.append(
                f"{record_label(path, index)}: {key} duplicado: {identifier}"
            )
        result[identifier] = record
    return result


def confirmed_claim(evidence: dict[str, Any], field: str) -> bool:
    return any(
        claim.get("field") == field and claim.get("finding") == "confirmed"
        for claim in evidence.get("claims", [])
    )


def validate_candidate_invariants(
    dataset: Path,
    loaded: dict[str, list[dict[str, Any]]],
    errors: list[str],
) -> None:
    candidates = loaded["candidates.jsonl"]
    evidences = unique_map(
        loaded["evidence.jsonl"],
        "evidence_id",
        dataset / "evidence.jsonl",
        errors,
    )
    sources = unique_map(
        loaded["source-inventory.jsonl"],
        "source_id",
        dataset / "source-inventory.jsonl",
        errors,
    )
    platforms = unique_map(
        candidates,
        "platform_id",
        dataset / "candidates.jsonl",
        errors,
    )
    entity_ids: set[str] = set()

    for index, evidence in enumerate(loaded["evidence.jsonl"]):
        if confirmed_claim(evidence, "regulatory_status") and (
            evidence.get("source_type") not in REGULATORY_TYPES
        ):
            errors.append(
                f"{record_label(dataset / 'evidence.jsonl', index)}: "
                "alegação regulatória exige regulador ou documento oficial"
            )

    for index, candidate in enumerate(candidates):
        label = record_label(dataset / "candidates.jsonl", index)
        if contains_key(candidate, "direct_investment"):
            errors.append(f"{label}: o contrato não aceita direct_investment")

        platform_id = candidate.get("platform_id")
        operator_id = candidate.get("operator", {}).get("operator_id")
        brand_id = candidate.get("brand", {}).get("brand_id")
        product_ids = {
            product.get("product_id") for product in candidate.get("products", [])
        }
        offer_ids = {offer.get("offer_id") for offer in candidate.get("offers", [])}
        regulatory_ids = {
            record.get("regulatory_id")
            for record in candidate.get("regulatory_records", [])
        }
        current_ids = (
            {platform_id, operator_id, brand_id}
            | product_ids
            | offer_ids
            | regulatory_ids
        )
        current_ids.discard(None)
        collision = entity_ids.intersection(current_ids)
        if collision:
            errors.append(f"{label}: IDs de entidade duplicados: {sorted(collision)}")
        entity_ids.update(current_ids)

        for offer in candidate.get("offers", []):
            if offer.get("product_id") not in product_ids:
                errors.append(
                    f"{label}: oferta {offer.get('offer_id')} referencia produto inexistente"
                )

        for source_id in candidate.get("discovery_source_ids", []):
            if source_id not in sources:
                errors.append(f"{label}: fonte órfã: {source_id}")

        evidence_groups = (
            "official_evidence_ids",
            "activity_evidence_ids",
            "route_evidence_ids",
        )
        for group in evidence_groups:
            for evidence_id in candidate.get(group, []):
                evidence = evidences.get(evidence_id)
                if not evidence:
                    errors.append(f"{label}: evidência órfã em {group}: {evidence_id}")
                elif evidence.get("platform_id") != platform_id:
                    errors.append(
                        f"{label}: {evidence_id} pertence a outra plataforma"
                    )
                elif (
                    group == "official_evidence_ids"
                    and evidence.get("source_type") not in OFFICIAL_TYPES
                ):
                    errors.append(
                        f"{label}: {evidence_id} não é uma evidência oficial"
                    )

        decision = candidate.get("decision")
        if decision == "duplicate":
            target = candidate.get("canonical_platform_id")
            if target and target not in platforms:
                errors.append(f"{label}: plataforma canônica órfã: {target}")

        for regulatory_record in candidate.get("regulatory_records", []):
            evidence_id = regulatory_record.get("evidence_id")
            evidence = evidences.get(evidence_id)
            if not evidence:
                errors.append(f"{label}: evidência regulatória órfã: {evidence_id}")
            elif (
                evidence.get("source_type") not in REGULATORY_TYPES
                or not confirmed_claim(evidence, "regulatory_status")
                or evidence.get("subject_type") != "regulatory_record"
                or evidence.get("subject_id")
                != regulatory_record.get("regulatory_id")
            ):
                errors.append(
                    f"{label}: alegação regulatória {evidence_id} exige "
                    "registro correspondente de regulador ou documento oficial"
                )

        if decision != "eligible":
            continue

        route_evidence = [
            evidences[evidence_id]
            for evidence_id in candidate.get("route_evidence_ids", [])
            if evidence_id in evidences
        ]
        route_is_proven = any(
            evidence.get("source_type") in OFFICIAL_TYPES
            and confirmed_claim(evidence, "structured_founder_route")
            and confirmed_claim(evidence, "latam_access")
            for evidence in route_evidence
        )
        if not route_is_proven:
            errors.append(
                f"{label}: elegível exige evidência oficial da rota estruturada "
                "e do acesso latino-americano"
            )

        activity_evidence = [
            evidences[evidence_id]
            for evidence_id in candidate.get("activity_evidence_ids", [])
            if evidence_id in evidences
        ]
        if not any(
            evidence.get("source_type") in OFFICIAL_TYPES
            and confirmed_claim(evidence, "recent_activity")
            for evidence in activity_evidence
        ):
            errors.append(f"{label}: elegível exige evidência oficial de atividade")

    for index, evidence in enumerate(loaded["evidence.jsonl"]):
        label = record_label(dataset / "evidence.jsonl", index)
        if evidence.get("platform_id") not in platforms:
            errors.append(f"{label}: plataforma órfã: {evidence.get('platform_id')}")
        if evidence.get("subject_id") not in entity_ids:
            errors.append(f"{label}: sujeito órfão: {evidence.get('subject_id')}")


def validate_dates(
    dataset: Path,
    loaded: dict[str, list[dict[str, Any]]],
    errors: list[str],
) -> None:
    run_records = loaded["run-manifest.jsonl"]
    run = next(
        (record for record in run_records if record.get("record_type") == "run"),
        None,
    )
    if not run:
        errors.append(f"{dataset / 'run-manifest.jsonl'}: registro run ausente")
        return
    cutoff = date.fromisoformat(run["cutoff_date"])
    activity_floor = subtract_months(cutoff, 24)
    evidences = {
        record["evidence_id"]: record for record in loaded["evidence.jsonl"]
    }

    for index, candidate in enumerate(loaded["candidates.jsonl"]):
        if candidate.get("decision") != "eligible":
            continue
        activity_value = candidate.get("last_official_activity_on")
        if not activity_value:
            continue
        activity_date = date.fromisoformat(activity_value)
        if not activity_floor <= activity_date <= cutoff:
            errors.append(
                f"{record_label(dataset / 'candidates.jsonl', index)}: "
                "atividade oficial está fora da janela de 24 meses"
            )
        activity_sources = [
            evidences[evidence_id]
            for evidence_id in candidate.get("activity_evidence_ids", [])
            if evidence_id in evidences
            and confirmed_claim(evidences[evidence_id], "recent_activity")
        ]
        if not any(
            evidence.get("published_on")
            and activity_floor
            <= date.fromisoformat(evidence["published_on"])
            <= cutoff
            for evidence in activity_sources
        ):
            errors.append(
                f"{record_label(dataset / 'candidates.jsonl', index)}: "
                "evidência de atividade sem data dentro da janela de 24 meses"
            )

    for index, evidence in enumerate(loaded["evidence.jsonl"]):
        published = evidence.get("published_on")
        if published and date.fromisoformat(published) > date.fromisoformat(
            evidence["accessed_on"]
        ):
            errors.append(
                f"{record_label(dataset / 'evidence.jsonl', index)}: "
                "publicação posterior ao acesso"
            )


def validate_coverage(
    dataset: Path,
    loaded: dict[str, list[dict[str, Any]]],
    errors: list[str],
    expected_countries: set[str] | None = None,
) -> None:
    countries: set[str] = set()
    source_ids = {
        record.get("source_id") for record in loaded["source-inventory.jsonl"]
    }
    for index, record in enumerate(loaded["coverage-matrix.jsonl"]):
        label = record_label(dataset / "coverage-matrix.jsonl", index)
        country = record.get("country")
        if country in countries:
            errors.append(f"{label}: país duplicado na matriz: {country}")
        countries.add(country)
        categories = {
            source.get("source_category") for source in record.get("sources", [])
        }
        if categories != SOURCE_CATEGORIES:
            errors.append(
                f"{label}: categorias incompletas; esperado={sorted(SOURCE_CATEGORIES)}"
            )
        for source in record.get("sources", []):
            source_id = source.get("source_id")
            if source.get("status") == "complete" and source_id not in source_ids:
                errors.append(f"{label}: fonte concluída não inventariada: {source_id}")
    if expected_countries is not None and countries != expected_countries:
        errors.append(
            f"{dataset / 'coverage-matrix.jsonl'}: países divergentes; "
            f"ausentes={sorted(expected_countries - countries)}, "
            f"extras={sorted(countries - expected_countries)}"
        )


def validate_manifest(
    dataset: Path,
    loaded: dict[str, list[dict[str, Any]]],
    errors: list[str],
) -> None:
    records = loaded["run-manifest.jsonl"]
    runs = [record for record in records if record.get("record_type") == "run"]
    tasks = [record for record in records if record.get("record_type") == "task"]
    if len(runs) != 1:
        errors.append(
            f"{dataset / 'run-manifest.jsonl'}: deve existir exatamente um run"
        )
        return
    run = runs[0]
    if run.get("task_count") != len(tasks):
        errors.append(
            f"{dataset / 'run-manifest.jsonl'}: task_count difere das tarefas"
        )
    task_ids: set[str] = set()
    for task in tasks:
        if task.get("run_id") != run.get("run_id"):
            errors.append(
                f"{dataset / 'run-manifest.jsonl'}: tarefa pertence a outro run"
            )
        task_id = task.get("task_id")
        if task_id in task_ids:
            errors.append(
                f"{dataset / 'run-manifest.jsonl'}: task_id duplicado: {task_id}"
            )
        task_ids.add(task_id)


def validate_dataset(
    dataset: Path,
    *,
    expected_countries: set[str] | None = None,
) -> list[str]:
    validators, errors = load_validators()
    if errors:
        return sorted(set(errors))
    loaded, schema_errors = validate_schema_records(dataset, validators)
    errors.extend(schema_errors)
    if schema_errors:
        return sorted(set(errors))
    validate_candidate_invariants(dataset, loaded, errors)
    validate_dates(dataset, loaded, errors)
    validate_coverage(dataset, loaded, errors, expected_countries)
    validate_manifest(dataset, loaded, errors)
    return sorted(set(errors))


def validate_contract() -> list[str]:
    validators, errors = load_validators()
    del validators
    for name in ("templates", "examples"):
        errors.extend(validate_dataset(ROOT / name))

    matrix_path = ROOT / "coverage-matrix.jsonl"
    records, matrix_errors = read_jsonl(matrix_path)
    errors.extend(matrix_errors)
    if not matrix_errors:
        validator = Draft202012Validator(
            read_json(ROOT / "schemas" / "coverage-record.schema.json"),
            format_checker=FormatChecker(),
        )
        loaded = {
            "coverage-matrix.jsonl": records,
            "source-inventory.jsonl": [],
        }
        for index, record in enumerate(records):
            for validation_error in validator.iter_errors(record):
                errors.append(
                    f"{record_label(matrix_path, index)}: {validation_error.message}"
                )
        validate_coverage(ROOT, loaded, errors, LATAM_COUNTRIES)
    return sorted(set(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        action="append",
        help="Diretório adicional com os cinco arquivos JSONL do contrato.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_contract()
    for dataset in args.dataset or []:
        errors.extend(validate_dataset(dataset.resolve()))
    errors = sorted(set(errors))
    if errors:
        print("Validação da epic 64 falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Contrato, templates, matriz e exemplo da epic 64 validados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
