"""Validation helpers for Epic 62 accelerator research artifacts."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


SCHEMA_BY_FILENAME = {
    "candidates.jsonl": "candidate.schema.json",
    "coverage-matrix.jsonl": "coverage-matrix.schema.json",
    "evidence.jsonl": "evidence.schema.json",
    "run-manifest.jsonl": "run-manifest-record.schema.json",
    "source-inventory.jsonl": "source-inventory.schema.json",
}
REQUIRED_EVIDENCE_FOR_ELIGIBLE = {
    "structured_program",
    "activity",
    "external_access",
    "latam_access",
}
REQUIRED_ACCELERATOR_FIELDS = (
    "Website",
    "Operator",
    "Program type",
    "Open to external founders",
    "Activity status",
    "Application status",
    "Program format",
    "Duration",
    "Stage",
    "Capital offered",
    "Instrument",
    "Equity",
    "Geography",
    "Apply",
)
REQUIRED_ACCELERATOR_SECTIONS = (
    "Program profile",
    "Eligibility and application",
    "Activity signals",
    "Sources",
)


def _display(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"{path.as_posix()}: JSON inválido: {exc}"]
    if not isinstance(value, dict):
        return None, [f"{path.as_posix()}: o schema deve ser um objeto JSON"]
    return value, []


def read_jsonl(root: Path, path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    display_path = _display(root, path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return [], [f"{display_path}: não foi possível ler como UTF-8: {exc}"]
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"{display_path}:{line_number}: linha JSONL vazia")
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{display_path}:{line_number}: JSON inválido: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{display_path}:{line_number}: cada linha deve ser um objeto")
            continue
        records.append(record)
    if not lines:
        errors.append(f"{display_path}: arquivo JSONL vazio")
    return records, errors


def _format_json_path(parts: Iterable[Any]) -> str:
    return "".join(f"[{part}]" if isinstance(part, int) else f".{part}" for part in parts)


def _load_validators(root: Path) -> tuple[dict[str, Draft202012Validator], list[str]]:
    schema_root = root / "research" / "epic-62" / "schemas"
    validators: dict[str, Draft202012Validator] = {}
    errors: list[str] = []
    for schema_name in sorted(set(SCHEMA_BY_FILENAME.values())):
        path = schema_root / schema_name
        schema, schema_errors = _read_json(path)
        errors.extend(
            error.replace(path.as_posix(), _display(root, path))
            for error in schema_errors
        )
        if schema is None:
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            errors.append(f"{_display(root, path)}: schema inválido: {exc.message}")
            continue
        validators[schema_name] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )
    return validators, errors


def _validate_records(
    root: Path,
    path: Path,
    records: list[dict[str, Any]],
    validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []
    display_path = _display(root, path)
    for line_number, record in enumerate(records, start=1):
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.path)):
            location = _format_json_path(error.path)
            errors.append(
                f"{display_path}:{line_number}{location}: {error.message}"
            )
    return errors


def _unique_ids(
    display_dir: str,
    records: list[dict[str, Any]],
    field: str,
) -> list[str]:
    seen: set[str] = set()
    errors: list[str] = []
    for record in records:
        value = record.get(field)
        if not isinstance(value, str):
            continue
        if value in seen:
            errors.append(f"{display_dir}: ID duplicado em {field}: {value}")
        seen.add(value)
    return errors


def _validate_manifest(
    display_dir: str,
    records: list[dict[str, Any]],
) -> list[str]:
    if not records:
        return []
    errors: list[str] = []
    runs = [record for record in records if record.get("record_type") == "run"]
    tasks = [record for record in records if record.get("record_type") == "task"]
    if len(runs) != 1:
        errors.append(f"{display_dir}: manifesto deve conter exatamente um registro run")
        return errors
    run = runs[0]
    if records[0].get("record_type") != "run":
        errors.append(f"{display_dir}: a primeira linha do manifesto deve ser run")
    if run.get("task_count") != len(tasks):
        errors.append(
            f"{display_dir}: task_count={run.get('task_count')} difere de {len(tasks)} tarefas"
        )
    run_id = run.get("run_id")
    for task in tasks:
        if task.get("run_id") != run_id:
            errors.append(
                f"{display_dir}: tarefa {task.get('task_id')} usa run_id divergente"
            )
    return errors


def _validate_artifact_set(
    root: Path,
    directory: Path,
    grouped: dict[str, list[dict[str, Any]]],
) -> list[str]:
    errors: list[str] = []
    display_dir = _display(root, directory)
    candidates = grouped.get("candidates.jsonl", [])
    evidence = grouped.get("evidence.jsonl", [])
    sources = grouped.get("source-inventory.jsonl", [])
    coverage = grouped.get("coverage-matrix.jsonl", [])
    manifests = grouped.get("run-manifest.jsonl", [])

    errors.extend(_unique_ids(display_dir, candidates, "candidate_id"))
    errors.extend(_unique_ids(display_dir, evidence, "evidence_id"))
    errors.extend(_unique_ids(display_dir, sources, "source_id"))
    errors.extend(_unique_ids(display_dir, coverage, "coverage_id"))
    errors.extend(_unique_ids(display_dir, manifests, "task_id"))
    errors.extend(_validate_manifest(display_dir, manifests))

    candidate_ids = {
        record["candidate_id"]
        for record in candidates
        if isinstance(record.get("candidate_id"), str)
    }
    evidence_by_id = {
        record["evidence_id"]: record
        for record in evidence
        if isinstance(record.get("evidence_id"), str)
    }
    source_ids = {
        record["source_id"]
        for record in sources
        if isinstance(record.get("source_id"), str)
    }

    for record in evidence:
        candidate_id = record.get("candidate_id")
        if candidate_id not in candidate_ids:
            errors.append(
                f"{display_dir}: evidência {record.get('evidence_id')} referencia "
                f"candidato inexistente: {candidate_id}"
            )

    for record in candidates:
        candidate_id = record.get("candidate_id")
        for source_id in record.get("discovery_source_ids", []):
            if source_id not in source_ids:
                errors.append(
                    f"{display_dir}: candidato {candidate_id} referencia fonte "
                    f"inexistente: {source_id}"
                )
        for evidence_id in record.get("official_evidence_ids", []):
            if evidence_id not in evidence_by_id:
                errors.append(
                    f"{display_dir}: candidato {candidate_id} referencia evidência "
                    f"inexistente: {evidence_id}"
                )

        if record.get("decision") != "elegível":
            continue
        confirmed_official_claims: set[str] = set()
        for evidence_id in record.get("official_evidence_ids", []):
            item = evidence_by_id.get(evidence_id)
            if not item or item.get("source_type") != "official":
                continue
            confirmed_official_claims.update(
                claim.get("field")
                for claim in item.get("claims", [])
                if claim.get("finding") == "confirmed"
            )
        missing = sorted(REQUIRED_EVIDENCE_FOR_ELIGIBLE - confirmed_official_claims)
        if missing:
            errors.append(
                f"{display_dir}: elegível {candidate_id} não possui evidência oficial "
                f"confirmada para {missing}"
            )

    for record in coverage:
        planned = record.get("planned_sources")
        completed = record.get("completed_sources")
        if isinstance(planned, int) and isinstance(completed, int) and completed > planned:
            errors.append(
                f"{display_dir}: cobertura {record.get('coverage_id')} concluiu mais "
                "fontes do que planejou"
            )
        if record.get("status") == "complete" and completed != planned:
            errors.append(
                f"{display_dir}: cobertura {record.get('coverage_id')} marcada complete "
                "sem concluir todas as fontes"
            )

    for record in evidence:
        published_on = record.get("published_on")
        accessed_on = record.get("accessed_on")
        if published_on and accessed_on:
            try:
                published_date = date.fromisoformat(published_on)
                accessed_date = date.fromisoformat(accessed_on)
            except (TypeError, ValueError):
                continue
            if published_date > accessed_date:
                errors.append(
                    f"{display_dir}: evidência {record.get('evidence_id')} tem publicação "
                    "posterior ao acesso"
                )
    return errors


def validate_epic_62(root: Path) -> list[str]:
    """Validate Epic 62 schemas, JSONL records and cross-file invariants."""
    epic_root = root / "research" / "epic-62"
    if not epic_root.exists():
        return []
    validators, errors = _load_validators(root)
    grouped_by_directory: dict[Path, dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    for path in sorted(epic_root.rglob("*.jsonl")):
        schema_name = SCHEMA_BY_FILENAME.get(path.name)
        if schema_name is None:
            errors.append(f"{_display(root, path)}: tipo de artefato JSONL desconhecido")
            continue
        records, read_errors = read_jsonl(root, path)
        errors.extend(read_errors)
        validator = validators.get(schema_name)
        if validator is not None:
            errors.extend(_validate_records(root, path, records, validator))
        grouped_by_directory[path.parent][path.name] = records
    for directory, grouped in sorted(grouped_by_directory.items()):
        errors.extend(_validate_artifact_set(root, directory, grouped))
    return sorted(set(errors))


def is_accelerator_profile_path(path: str) -> bool:
    return (
        path.startswith("ecosystem/accelerators/")
        and path.endswith(".md")
        and path != "ecosystem/accelerators/README.md"
    )


def accelerator_profile_paths(root: Path) -> set[str]:
    category = root / "ecosystem" / "accelerators"
    if not category.exists():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in category.rglob("*.md")
        if is_accelerator_profile_path(path.relative_to(root).as_posix())
    }


def validate_accelerator_index(root: Path) -> list[str]:
    """Require every accelerator profile to appear exactly once in its category README."""
    readme = root / "ecosystem" / "accelerators" / "README.md"
    if not readme.exists():
        return ["ecosystem/accelerators/README.md: índice da categoria ausente"]
    try:
        text = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"ecosystem/accelerators/README.md: leitura UTF-8 falhou: {exc}"]
    linked_profiles: list[str] = []
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        clean_target = target.strip().split("#", 1)[0]
        if not clean_target or re.match(r"^[a-z][a-z0-9+.-]*:", clean_target, re.I):
            continue
        candidate = (readme.parent / clean_target).resolve()
        try:
            relative = candidate.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
        if is_accelerator_profile_path(relative):
            linked_profiles.append(relative)
    errors: list[str] = []
    for profile in sorted(set(linked_profiles)):
        count = linked_profiles.count(profile)
        if count > 1:
            errors.append(
                f"ecosystem/accelerators/README.md: perfil duplicado no índice: {profile}"
            )
    actual = accelerator_profile_paths(root)
    linked = set(linked_profiles)
    if actual != linked:
        errors.append(
            "ecosystem/accelerators/README.md: conjunto de perfis diverge; "
            f"não indexados={sorted(actual - linked)}, "
            f"links sem perfil={sorted(linked - actual)}"
        )
    return errors


def validate_accelerator_profile(path: Path, display_path: str) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{display_path}: não foi possível ler como UTF-8: {exc}"]
    for section in REQUIRED_ACCELERATOR_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{display_path}: seção obrigatória ausente: {section}")
    fields = {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^- \*\*([^*]+):\*\*\s*(.*)$", text, re.MULTILINE)
    }
    for field in REQUIRED_ACCELERATOR_FIELDS:
        if not fields.get(field):
            errors.append(f"{display_path}: campo obrigatório ausente ou vazio: {field}")
    if not re.search(
        r"^\*\*Last verified:\*\* \d{4}-\d{2}-\d{2}\s*$",
        text,
        re.MULTILINE,
    ):
        errors.append(f"{display_path}: Last verified deve usar YYYY-MM-DD")
    sources_match = re.search(
        r"^## Sources\s*$([\s\S]*?)(?=^\*\*Last verified:|\Z)",
        text,
        re.MULTILINE,
    )
    if not sources_match or not re.search(
        r"^- \[[^\]]+\]\(https?://[^)]+\)",
        sources_match.group(1),
        re.MULTILINE,
    ):
        errors.append(f"{display_path}: inclua ao menos uma fonte HTTP(S)")
    return errors
