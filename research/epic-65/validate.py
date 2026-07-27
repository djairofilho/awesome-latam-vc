#!/usr/bin/env python3
"""Validate epic 65 public-program research bundles."""

from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parent
FILE_CONTRACTS = {
    "agencies.jsonl": ("agency.schema.json", "agency_id"),
    "programs.jsonl": ("program.schema.json", "program_id"),
    "calls.jsonl": ("call.schema.json", "call_id"),
    "evidence.jsonl": ("evidence.schema.json", "evidence_id"),
    "coverage-matrix.jsonl": ("coverage.schema.json", "coverage_id"),
    "run-manifest.jsonl": ("run-manifest.schema.json", None),
}
SUBJECT_FILES = {
    "agency": ("agencies.jsonl", "agency_id"),
    "program": ("programs.jsonl", "program_id"),
    "call": ("calls.jsonl", "call_id"),
}


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, raw_line in enumerate(stream, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: JSON inválido: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{line_number}: cada linha deve ser um objeto")
            record["_line_number"] = line_number
            records.append(record)
    return records


def display_error(error) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    return f"{location}: {error.message}" if location else error.message


def subtract_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def confirmed_claims(evidence: dict) -> set[str]:
    return {
        claim["field"]
        for claim in evidence["claims"]
        if claim["finding"] == "confirmado"
    }


def parse_date(value: object) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def call_is_open_on_capture(call: dict) -> bool:
    """Return whether a call is temporally consistent with an open snapshot."""
    if call.get("call_status") != "aberta":
        return False
    captured_date = parse_date(call.get("captured_on"))
    opened_date = parse_date(call.get("opened_on"))
    closes_date = parse_date(call.get("closes_on"))
    if captured_date is None:
        return False
    if opened_date is not None and captured_date < opened_date:
        return False
    if closes_date is not None and captured_date > closes_date:
        return False
    return True


def validate_bundle(bundle: Path) -> list[str]:
    errors: list[str] = []
    schemas: dict[str, dict] = {}
    records: dict[str, list[dict]] = {}

    for filename, (schema_name, _) in FILE_CONTRACTS.items():
        path = bundle / filename
        if not path.is_file():
            errors.append(f"{bundle}: arquivo obrigatório ausente: {filename}")
            continue
        try:
            records[filename] = load_jsonl(path)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(str(exc))
            continue
        schema_path = ROOT / "schemas" / schema_name
        try:
            schemas[filename] = json.loads(schema_path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schemas[filename])
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, SchemaError) as exc:
            errors.append(f"{schema_path}: schema inválido: {exc}")
            continue
        validator = Draft202012Validator(
            schemas[filename],
            format_checker=FormatChecker(),
        )
        for record in records[filename]:
            line_number = record.pop("_line_number")
            for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
                errors.append(
                    f"{path}:{line_number}: {display_error(error)}"
                )
            record["_line_number"] = line_number

    if set(records) != set(FILE_CONTRACTS):
        return sorted(set(errors))

    indexes: dict[str, dict[str, dict]] = {}
    for filename, (_, id_field) in FILE_CONTRACTS.items():
        indexes[filename] = {}
        if id_field is None:
            continue
        for record in records[filename]:
            record_id = record.get(id_field)
            if not isinstance(record_id, str):
                continue
            if record_id in indexes[filename]:
                errors.append(f"{bundle}/{filename}: ID duplicado: {record_id}")
            indexes[filename][record_id] = record

    evidences = indexes["evidence.jsonl"]

    for evidence in records["evidence.jsonl"]:
        subject_type = evidence.get("subject_type")
        subject_id = evidence.get("subject_id")
        if subject_type not in SUBJECT_FILES or not isinstance(subject_id, str):
            continue
        subject_file, _ = SUBJECT_FILES[subject_type]
        if subject_id not in indexes[subject_file]:
            errors.append(
                f"{bundle}/evidence.jsonl: evidência {evidence.get('evidence_id')} "
                f"aponta para entidade inexistente: {subject_id}"
            )
        expected_prefix = f"{subject_type}-"
        if not subject_id.startswith(expected_prefix):
            errors.append(
                f"{bundle}/evidence.jsonl: subject_type {subject_type} "
                f"não corresponde a {subject_id}"
            )
        published_on = evidence.get("published_on")
        accessed_on = evidence.get("accessed_on")
        published_date = parse_date(published_on)
        accessed_date = parse_date(accessed_on)
        if published_date and accessed_date and published_date > accessed_date:
            errors.append(
                f"{bundle}/evidence.jsonl: {evidence.get('evidence_id')} "
                "tem publicação posterior ao acesso"
            )

    def check_evidence_links(filename: str, id_field: str) -> None:
        subject_type = id_field.removesuffix("_id")
        for record in records[filename]:
            record_id = record.get(id_field)
            for evidence_id in record.get("official_evidence_ids", []):
                evidence = evidences.get(evidence_id)
                if evidence is None:
                    errors.append(
                        f"{bundle}/{filename}: {record_id} referencia evidência "
                        f"inexistente: {evidence_id}"
                    )
                elif (
                    evidence.get("subject_type") != subject_type
                    or evidence.get("subject_id") != record_id
                ):
                    errors.append(
                        f"{bundle}/{filename}: {evidence_id} não pertence a {record_id}"
                    )

    check_evidence_links("agencies.jsonl", "agency_id")
    check_evidence_links("programs.jsonl", "program_id")
    check_evidence_links("calls.jsonl", "call_id")

    agencies = indexes["agencies.jsonl"]
    programs = indexes["programs.jsonl"]
    calls = indexes["calls.jsonl"]

    manifest = records["run-manifest.jsonl"]
    run_rows = [record for record in manifest if record.get("record_type") == "run"]
    task_rows = [record for record in manifest if record.get("record_type") == "task"]
    if len(run_rows) != 1:
        errors.append(
            f"{bundle}/run-manifest.jsonl: deve conter exatamente um registro run"
        )
    else:
        run = run_rows[0]
        run_id = run.get("run_id")
        linked_tasks = [task for task in task_rows if task.get("run_id") == run_id]
        if len(linked_tasks) != run.get("task_count"):
            errors.append(
                f"{bundle}/run-manifest.jsonl: task_count não coincide com as tarefas"
            )
        foreign_tasks = [task for task in task_rows if task.get("run_id") != run_id]
        if foreign_tasks:
            errors.append(
                f"{bundle}/run-manifest.jsonl: há tarefas de outro run_id"
            )
        task_ids = [task.get("task_id") for task in task_rows]
        if len(task_ids) != len(set(task_ids)):
            errors.append(
                f"{bundle}/run-manifest.jsonl: task_id duplicado"
            )
        shard_owners: dict[str, str] = {}
        for task in task_rows:
            shard_path = task.get("shard_path")
            worker_id = task.get("worker_id")
            if not isinstance(shard_path, str) or not isinstance(worker_id, str):
                continue
            previous_owner = shard_owners.get(shard_path)
            if previous_owner is not None:
                errors.append(
                    f"{bundle}/run-manifest.jsonl: shard_path duplicado: "
                    f"{shard_path}"
                )
                if previous_owner != worker_id:
                    errors.append(
                        f"{bundle}/run-manifest.jsonl: workers distintos "
                        f"compartilham {shard_path}: {previous_owner} e {worker_id}"
                    )
            else:
                shard_owners[shard_path] = worker_id

    for agency in records["agencies.jsonl"]:
        agency_id = agency.get("agency_id")
        for program_id in agency.get("program_ids", []):
            program = programs.get(program_id)
            if program is None:
                errors.append(
                    f"{bundle}/agencies.jsonl: {agency_id} referencia programa "
                    f"inexistente: {program_id}"
                )
            elif program.get("agency_id") != agency_id:
                errors.append(
                    f"{bundle}: vínculo assimétrico entre {agency_id} e {program_id}"
                )
        if agency.get("decision") == "elegível":
            eligible_programs = [
                program_id
                for program_id in agency.get("program_ids", [])
                if programs.get(program_id, {}).get("decision") == "elegível"
            ]
            if not eligible_programs:
                errors.append(
                    f"{bundle}/agencies.jsonl: {agency_id} elegível sem programa "
                    "elegível vinculado"
                )
            claims = set()
            for evidence_id in agency.get("official_evidence_ids", []):
                if evidence_id in evidences:
                    claims.update(confirmed_claims(evidences[evidence_id]))
            if "rota para startups" not in claims:
                errors.append(
                    f"{bundle}/agencies.jsonl: {agency_id} elegível sem evidência "
                    "oficial confirmada de rota para startups"
                )
        if agency.get("research_status") == "publicada" and not agency.get(
            "canonical_profile"
        ):
            errors.append(
                f"{bundle}/agencies.jsonl: {agency_id} publicada sem perfil canônico"
            )
        if agency.get("research_status") in {"descoberta", "em pesquisa"} or agency.get(
            "decision"
        ) == "evidência insuficiente":
            if not (agency.get("owner") or agency.get("next_action")):
                errors.append(
                    f"{bundle}/agencies.jsonl: {agency_id} pendente sem responsável "
                    "ou próxima ação"
                )

    for program in records["programs.jsonl"]:
        program_id = program.get("program_id")
        agency_id = program.get("agency_id")
        agency = agencies.get(agency_id)
        if agency is None:
            errors.append(
                f"{bundle}/programs.jsonl: {program_id} referencia agência "
                f"inexistente: {agency_id}"
            )
        elif program_id not in agency.get("program_ids", []):
            errors.append(f"{bundle}: vínculo assimétrico entre {agency_id} e {program_id}")
        for call_id in program.get("call_ids", []):
            call = calls.get(call_id)
            if call is None:
                errors.append(
                    f"{bundle}/programs.jsonl: {program_id} referencia chamada "
                    f"inexistente: {call_id}"
                )
            elif call.get("program_id") != program_id:
                errors.append(
                    f"{bundle}: vínculo assimétrico entre {program_id} e {call_id}"
                )
        if program.get("decision") == "elegível":
            claims = set()
            for evidence_id in program.get("official_evidence_ids", []):
                if evidence_id in evidences:
                    claims.update(confirmed_claims(evidences[evidence_id]))
            required_claims = {
                "benefício financeiro",
                "rota para startups",
                "atividade do programa",
            }
            if program.get("activity_basis") == "recorrência oficial em 24 meses":
                required_claims.add("recorrência")
            missing = required_claims - claims
            if missing:
                errors.append(
                    f"{bundle}/programs.jsonl: {program_id} elegível sem "
                    f"evidência oficial confirmada para: {sorted(missing)}"
                )
            signal = program.get("latest_official_signal_on")
            assessed = program.get("assessed_on")
            signal_date = parse_date(signal)
            assessed_date = parse_date(assessed)
            if signal_date and assessed_date:
                if signal_date > assessed_date:
                    errors.append(
                        f"{bundle}/programs.jsonl: {program_id} tem sinal oficial "
                        "posterior à data de avaliação"
                    )
                if signal_date < subtract_months(assessed_date, 24):
                    errors.append(
                        f"{bundle}/programs.jsonl: {program_id} não possui sinal "
                        "oficial nos 24 meses anteriores à avaliação"
                    )
            if program.get("activity_basis") == "chamada aberta":
                has_open_call = any(
                    call_is_open_on_capture(calls.get(call_id, {}))
                    for call_id in program.get("call_ids", [])
                )
                if not has_open_call:
                    errors.append(
                        f"{bundle}/programs.jsonl: {program_id} usa chamada aberta "
                        "sem call_id aberta e temporalmente válida vinculada"
                    )
            if program.get("program_status") == "fechado agora, recorrente" and (
                program.get("activity_basis") != "recorrência oficial em 24 meses"
            ):
                errors.append(
                    f"{bundle}/programs.jsonl: {program_id} fechado agora, recorrente "
                    "sem base de recorrência oficial"
                )
        if program.get("research_status") == "publicado" and not program.get(
            "canonical_profile"
        ):
            errors.append(
                f"{bundle}/programs.jsonl: {program_id} publicado sem perfil canônico"
            )
        if program.get("research_status") in {"descoberto", "em pesquisa"} or program.get(
            "decision"
        ) == "evidência insuficiente":
            if not (program.get("owner") or program.get("next_action")):
                errors.append(
                    f"{bundle}/programs.jsonl: {program_id} pendente sem responsável "
                    "ou próxima ação"
                )

    for call in records["calls.jsonl"]:
        call_id = call.get("call_id")
        program_id = call.get("program_id")
        program = programs.get(program_id)
        if program is None:
            errors.append(
                f"{bundle}/calls.jsonl: {call_id} referencia programa "
                f"inexistente: {program_id}"
            )
        elif call_id not in program.get("call_ids", []):
            errors.append(f"{bundle}: vínculo assimétrico entre {program_id} e {call_id}")
        opened_on = call.get("opened_on")
        closes_on = call.get("closes_on")
        captured_on = call.get("captured_on")
        opened_date = parse_date(opened_on)
        closes_date = parse_date(closes_on)
        captured_date = parse_date(captured_on)
        if opened_date and closes_date and closes_date < opened_date:
            errors.append(
                f"{bundle}/calls.jsonl: {call_id} fecha antes de abrir"
            )
        if call.get("call_status") == "aberta" and captured_date:
            if opened_date and captured_date < opened_date:
                errors.append(
                    f"{bundle}/calls.jsonl: {call_id} foi capturada como aberta "
                    "antes da data de abertura"
                )
            if closes_date and captured_date > closes_date:
                errors.append(
                    f"{bundle}/calls.jsonl: {call_id} foi capturada como aberta "
                    "após a data de fechamento"
                )
        if call.get("call_status") == "fechada" and captured_date:
            if opened_date and captured_date < opened_date:
                errors.append(
                    f"{bundle}/calls.jsonl: {call_id} foi capturada como fechada "
                    "antes da data de abertura"
                )
            if closes_date and captured_date < closes_date:
                errors.append(
                    f"{bundle}/calls.jsonl: {call_id} foi capturada como fechada "
                    "antes da data de fechamento"
                )
        if (
            call.get("call_status") == "prevista"
            and captured_date
            and opened_date
            and captured_date >= opened_date
        ):
            errors.append(
                f"{bundle}/calls.jsonl: {call_id} continua prevista na data "
                "ou após a abertura"
            )
        if call.get("call_status") in {"aberta", "fechada"}:
            claims = set()
            for evidence_id in call.get("official_evidence_ids", []):
                if evidence_id in evidences:
                    claims.update(confirmed_claims(evidences[evidence_id]))
            if "status da chamada" not in claims:
                errors.append(
                    f"{bundle}/calls.jsonl: {call_id} tem status afirmado sem "
                    "evidência oficial confirmada"
                )

    return sorted(set(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "bundles",
        nargs="*",
        type=Path,
        help="diretórios de bundle; por padrão valida templates e examples",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bundles = args.bundles or [ROOT / "templates", ROOT / "examples"]
    errors: list[str] = []
    for bundle in bundles:
        errors.extend(validate_bundle(bundle.resolve()))
    if errors:
        print("Validação da epic 65 falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Validação da epic 65 passou: "
        + ", ".join(str(bundle.resolve()) for bundle in bundles)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
