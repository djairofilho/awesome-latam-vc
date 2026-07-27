"""Valida artefatos JSONL do contrato de redes-anjo da epic 63."""

from __future__ import annotations

import argparse
import json
import sys
from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schemas"
FILES = {
    "candidates.jsonl": "candidate.schema.json",
    "evidence.jsonl": "evidence.schema.json",
    "source-inventory.jsonl": "source-inventory.schema.json",
    "coverage-matrix.jsonl": "coverage-record.schema.json",
    "run-manifest.jsonl": "run-manifest-record.schema.json",
}
MOJIBAKE_MARKERS = ("Ã", "Â", "�")
ROUTED_DECISIONS = {
    "encaminhado-para-funds",
    "encaminhado-para-aceleradoras",
    "encaminhado-para-plataformas",
    "encaminhado-para-programas-públicos",
}


@dataclass(frozen=True)
class Record:
    file: str
    line: int
    data: dict[str, Any]

    @property
    def location(self) -> str:
        return f"{self.file}:{self.line}"


def read_jsonl(path: Path) -> tuple[list[Record], list[str]]:
    records: list[Record] = []
    errors: list[str] = []
    if not path.is_file():
        return records, [f"{path.name}: arquivo obrigatório ausente"]

    text = path.read_text(encoding="utf-8")
    for marker in MOJIBAKE_MARKERS:
        if marker in text:
            errors.append(f"{path.name}: possível mojibake encontrado: {marker!r}")

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"{path.name}:{line_number}: linha vazia não é válida")
            continue
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_number}: JSON inválido: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name}:{line_number}: a linha deve ser um objeto")
            continue
        records.append(Record(path.name, line_number, value))
    return records, errors


def format_schema_error(error: Any) -> str:
    path = ".".join(str(part) for part in error.absolute_path)
    prefix = f"{path}: " if path else ""
    return f"{prefix}{error.message}"


def schema_errors(
    records: Iterable[Record], schema_path: Path
) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for record in records:
        for error in sorted(
            validator.iter_errors(record.data),
            key=lambda item: list(item.absolute_path),
        ):
            errors.append(f"{record.location}: {format_schema_error(error)}")
    return errors


def index_unique(
    records: Iterable[Record], field: str, errors: list[str]
) -> dict[str, Record]:
    index: dict[str, Record] = {}
    for record in records:
        value = record.data.get(field)
        if not isinstance(value, str):
            continue
        if value in index:
            errors.append(
                f"{record.location}: {field} duplicado; primeira ocorrência em "
                f"{index[value].location}"
            )
        else:
            index[value] = record
    return index


def confirmed_official_claims(
    candidate: Record,
    evidence: dict[str, Record],
) -> dict[str, list[Record]]:
    claims: dict[str, list[Record]] = {}
    for evidence_id in candidate.data.get("official_evidence_ids", []):
        record = evidence.get(evidence_id)
        if (
            record is None
            or record.data.get("source_type") != "oficial"
            or record.data.get("network_id") != candidate.data.get("network_id")
        ):
            continue
        for claim in record.data.get("claims", []):
            if claim.get("finding") == "confirmado":
                claims.setdefault(claim.get("field"), []).append(record)
    return claims


def subtract_months(value: date, months: int) -> date:
    total = value.year * 12 + value.month - 1 - months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def validate_candidate_relations(
    candidates: dict[str, Record],
    evidence: dict[str, Record],
    sources: dict[str, Record],
) -> list[str]:
    errors: list[str] = []
    for network_id, record in candidates.items():
        item = record.data

        domain = item.get("canonical_domain")
        if domain:
            expected_base = "ang-" + domain.replace(".", "-")
            if not (
                network_id == expected_base
                or network_id.startswith(expected_base + "--")
            ):
                errors.append(
                    f"{record.location}: network_id não deriva do domínio "
                    f"normalizado {domain!r}"
                )

        for source_id in item.get("discovery_source_ids", []):
            if source_id not in sources:
                errors.append(
                    f"{record.location}: discovery_source_id inexistente: "
                    f"{source_id}"
                )
        for evidence_id in item.get("official_evidence_ids", []):
            linked = evidence.get(evidence_id)
            if linked is None:
                errors.append(
                    f"{record.location}: official_evidence_id inexistente: "
                    f"{evidence_id}"
                )
            elif linked.data.get("network_id") != network_id:
                errors.append(
                    f"{record.location}: evidência {evidence_id} pertence a "
                    f"outro candidato"
                )
            elif linked.data.get("source_type") != "oficial":
                errors.append(
                    f"{record.location}: evidência {evidence_id} não é oficial"
                )

        for link_field in ("parent_network_id", "canonical_network_id"):
            target = item.get(link_field)
            if target is not None and target not in candidates:
                errors.append(
                    f"{record.location}: {link_field} inexistente: {target}"
                )
            if target == network_id:
                errors.append(
                    f"{record.location}: {link_field} não pode apontar para si"
                )

        decision = item.get("decision")
        if decision == "duplicado" and not (
            item.get("canonical_network_id") or item.get("canonical_profile")
        ):
            errors.append(
                f"{record.location}: duplicado sem destino canônico"
            )
        if decision in ROUTED_DECISIONS and not item.get("canonical_profile"):
            errors.append(
                f"{record.location}: encaminhamento sem canonical_profile"
            )
        if item.get("status") == "publicado" and (
            decision != "elegível" or not item.get("canonical_profile")
        ):
            errors.append(
                f"{record.location}: publicado exige decisão elegível e perfil"
            )
        if item.get("chapter_identity") == "alias" and (
            item.get("status") in {"decidido", "publicado"}
            and decision != "duplicado"
        ):
            errors.append(
                f"{record.location}: capítulo alias decidido deve ser duplicado"
            )

        claims = confirmed_official_claims(record, evidence)
        if decision == "elegível":
            for required_claim in ("categoria", "atividade", "acesso externo"):
                if required_claim not in claims:
                    errors.append(
                        f"{record.location}: elegível sem evidência oficial "
                        f"confirmada de {required_claim}"
                    )
            activity_date = item.get("activity_evidence_date")
            if activity_date:
                activity_value = date.fromisoformat(activity_date)
                cutoff = date.fromisoformat(item["cutoff_date"])
                oldest = subtract_months(cutoff, 24)
                if activity_value < oldest or activity_value > cutoff:
                    errors.append(
                        f"{record.location}: atividade fora da janela de 24 "
                        "meses"
                    )
                dated_activity = [
                    linked
                    for linked in claims.get("atividade", [])
                    if linked.data.get("published_on") == activity_date
                ]
                if not dated_activity:
                    errors.append(
                        f"{record.location}: activity_evidence_date não coincide "
                        "com evidência oficial de atividade"
                    )

        if item.get("chapter_identity") == "standalone":
            if "autonomia de capítulo" not in claims:
                errors.append(
                    f"{record.location}: capítulo standalone sem evidência "
                    "oficial de autonomia"
                )

    for record in evidence.values():
        if record.data.get("network_id") not in candidates:
            errors.append(
                f"{record.location}: network_id inexistente: "
                f"{record.data.get('network_id')}"
            )
        published = record.data.get("published_on")
        if published and published > record.data.get("accessed_on", ""):
            errors.append(
                f"{record.location}: published_on posterior a accessed_on"
            )
    return errors


def validate_coverage(
    records: list[Record], sources: dict[str, Record]
) -> list[str]:
    errors: list[str] = []
    cells: dict[tuple[str, str], Record] = {}
    for record in records:
        item = record.data
        key = (item.get("geography"), item.get("source_category"))
        if key in cells:
            errors.append(
                f"{record.location}: célula duplicada de cobertura; primeira "
                f"ocorrência em {cells[key].location}"
            )
        else:
            cells[key] = record
        for source_id in item.get("source_ids", []):
            source = sources.get(source_id)
            if source is None:
                errors.append(
                    f"{record.location}: source_id inexistente: {source_id}"
                )
            elif source.data.get("source_category") != item.get(
                "source_category"
            ):
                errors.append(
                    f"{record.location}: categoria não coincide com "
                    f"{source_id}"
                )
            elif source.data.get("geography") != item.get("geography"):
                errors.append(
                    f"{record.location}: geografia não coincide com {source_id}"
                )
    return errors


def validate_manifest(records: list[Record]) -> list[str]:
    errors: list[str] = []
    runs = [record for record in records if record.data.get("record_type") == "run"]
    tasks = [
        record for record in records if record.data.get("record_type") == "task"
    ]
    if len(runs) != 1:
        errors.append(
            "run-manifest.jsonl: deve conter exatamente um registro run"
        )
        return errors
    run = runs[0]
    if records and records[0].data.get("record_type") != "run":
        errors.append("run-manifest.jsonl: a primeira linha deve ser o run")
    run_id = run.data.get("run_id")
    run_tasks = [task for task in tasks if task.data.get("run_id") == run_id]
    if len(run_tasks) != run.data.get("task_count"):
        errors.append(
            f"{run.location}: task_count não coincide com as tarefas"
        )
    for task in tasks:
        if task.data.get("run_id") != run_id:
            errors.append(
                f"{task.location}: tarefa pertence a outra execução"
            )
        if task.data.get("issue") not in run.data.get("issues", []):
            errors.append(
                f"{task.location}: issue da tarefa não consta no run"
            )
    index_unique(tasks, "task_id", errors)
    return errors


def validate_directory(directory: Path) -> list[str]:
    all_records: dict[str, list[Record]] = {}
    errors: list[str] = []
    for file_name, schema_name in FILES.items():
        records, read_errors = read_jsonl(directory / file_name)
        all_records[file_name] = records
        errors.extend(read_errors)
        errors.extend(schema_errors(records, SCHEMA_DIR / schema_name))

    candidates = index_unique(
        all_records["candidates.jsonl"], "network_id", errors
    )
    evidence = index_unique(
        all_records["evidence.jsonl"], "evidence_id", errors
    )
    sources = index_unique(
        all_records["source-inventory.jsonl"], "source_id", errors
    )
    index_unique(
        all_records["coverage-matrix.jsonl"], "coverage_id", errors
    )

    errors.extend(validate_candidate_relations(candidates, evidence, sources))
    errors.extend(
        validate_coverage(all_records["coverage-matrix.jsonl"], sources)
    )
    errors.extend(validate_manifest(all_records["run-manifest.jsonl"]))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida um diretório de artefatos da epic 63."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Diretório com os cinco arquivos JSONL do contrato.",
    )
    args = parser.parse_args()
    errors = validate_directory(args.directory.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.directory} validado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
