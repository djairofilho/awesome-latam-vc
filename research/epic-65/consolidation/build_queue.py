#!/usr/bin/env python3
"""Build the deterministic public-program consolidation queue for issue #102."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
REGIONS = ("brazil", "mexico", "andean", "southern-cone")
IDENTIFIERS = {
    "agencies.jsonl": "agency_id",
    "programs.jsonl": "program_id",
    "calls.jsonl": "call_id",
    "evidence.jsonl": "evidence_id",
    "coverage-matrix.jsonl": "coverage_id",
}
RUN_ID = "run-issue-102-public-program-consolidation"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_inputs() -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, dict[str, int]],
]:
    grouped = {filename: [] for filename in IDENTIFIERS}
    tasks: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}
    before_counts: dict[str, dict[str, int]] = {}

    for region in REGIONS:
        region_counts: dict[str, int] = {}
        region_dir = EPIC_ROOT / region
        for filename in (*IDENTIFIERS, "run-manifest.jsonl"):
            path = region_dir / filename
            payload = path.read_bytes().replace(b"\r\n", b"\n")
            input_hashes[path.relative_to(REPOSITORY_ROOT).as_posix()] = sha256(
                payload
            )
            records = read_jsonl(path)
            if filename in grouped:
                grouped[filename].extend(records)
                region_counts[filename] = len(records)
            else:
                for record in records:
                    if record["record_type"] == "task":
                        task = dict(record)
                        task["run_id"] = RUN_ID
                        tasks.append(task)
        before_counts[region] = region_counts

    return grouped, tasks, dict(sorted(input_hashes.items())), before_counts


def unique_and_sorted(
    records: list[dict[str, Any]], id_field: str, filename: str
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[id_field]
        previous = by_id.get(record_id)
        if previous is not None:
            if previous != record:
                raise ValueError(f"ID divergente em {filename}: {record_id}")
            raise ValueError(f"ID duplicado em {filename}: {record_id}")
        by_id[record_id] = record
    return [by_id[record_id] for record_id in sorted(by_id)]


def build_transfer_resolutions(program_ids: set[str]) -> list[dict[str, Any]]:
    accelerator_candidates = read_jsonl(
        REPOSITORY_ROOT
        / "research"
        / "epic-62"
        / "consolidation"
        / "candidates.jsonl"
    )
    results: list[dict[str, Any]] = []
    for candidate in accelerator_candidates:
        destination = candidate.get("destination")
        if (
            candidate.get("decision") != "encaminhado-para-outra-epic"
            or not isinstance(destination, str)
            or "65" not in destination
        ):
            continue
        if "#" in destination:
            target_program_id = destination.rsplit("#", 1)[1]
        elif destination.startswith("epic-65:program/"):
            target_program_id = destination.rsplit("/", 1)[1]
        else:
            raise ValueError(
                f"destino público não canônico para {candidate['candidate_id']}"
            )
        materialized = target_program_id in program_ids
        results.append(
            {
                "source_epic": 62,
                "source_candidate_id": candidate["candidate_id"],
                "incoming_destination": destination,
                "target_program_id": target_program_id,
                "resolution": (
                    "matched-existing-program"
                    if materialized
                    else "requires-public-contract-adjudication"
                ),
                "materialized": materialized,
                "owner": None if materialized else "independent-reviewer-issue-102",
                "next_action": (
                    None
                    if materialized
                    else (
                        "Revisar a evidência oficial de origem contra o contrato da "
                        "epic #65 sem inferir benefício financeiro ou recorrência."
                    )
                ),
            }
        )
    return sorted(results, key=lambda row: row["source_candidate_id"])


def build_category_resolutions(
    programs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    explicit = {
        "program-bndes-selecao-fundos": "funds/:bndes-selecao-de-fundos",
        "program-finep-inovar": "funds/:finep-programa-inovar",
        "program-nafin-capital-emprendedor": "funds/:nafin-capital-emprendedor",
        "program-sebrae-capital-empreendedor": (
            "research/epic-62/consolidation/candidates.jsonl"
            "#accel-capital-empreendedor-rj"
        ),
        "program-sebrae-fic-fip": "funds/:sebrae-fic-fip",
    }
    known_ids = {program["program_id"] for program in programs}
    missing = sorted(set(explicit) - known_ids)
    if missing:
        raise ValueError(f"fronteiras ausentes do registro: {missing}")
    return [
        {
            "program_id": program_id,
            "public_program_decision": next(
                row["decision"]
                for row in programs
                if row["program_id"] == program_id
            ),
            "relationship": "transferred-to-other-category",
            "canonical_destination": destination,
        }
        for program_id, destination in sorted(explicit.items())
    ]


def build_outputs() -> dict[str, bytes]:
    grouped, tasks, input_hashes, before_counts = load_inputs()
    canonical = {
        filename: unique_and_sorted(records, IDENTIFIERS[filename], filename)
        for filename, records in grouped.items()
    }

    tasks.sort(key=lambda row: row["task_id"])
    run_record = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issue": 102,
        "region": "América Latina",
        "cutoff_date": "2026-07-27",
        "status": "concluída",
        "task_count": len(tasks),
        "coordinator": "coordinator-issue-102",
        "scraping_performed": False,
    }
    manifests = [run_record, *tasks]

    agencies = canonical["agencies.jsonl"]
    programs = canonical["programs.jsonl"]
    calls = canonical["calls.jsonl"]
    evidence = canonical["evidence.jsonl"]
    agency_ids = {row["agency_id"] for row in agencies}
    program_ids = {row["program_id"] for row in programs}
    call_ids = {row["call_id"] for row in calls}
    evidence_ids = {row["evidence_id"] for row in evidence}

    if any(row["decision"] is None for row in (*agencies, *programs)):
        raise ValueError("agência ou programa sem decisão")
    if any(row["agency_id"] not in agency_ids for row in programs):
        raise ValueError("programa com agência órfã")
    if any(row["program_id"] not in program_ids for row in calls):
        raise ValueError("chamada com programa órfão")
    for row in (*agencies, *programs, *calls):
        if any(evidence_id not in evidence_ids for evidence_id in row["official_evidence_ids"]):
            raise ValueError("referência de evidência órfã")
    for row in (*agencies, *programs):
        if "insuficiente" in row["decision"] and not (
            row.get("owner") and row.get("next_action")
        ):
            raise ValueError(f"pendência sem ação: {row}")

    transfer_resolutions = build_transfer_resolutions(program_ids)
    if len(transfer_resolutions) != 13:
        raise ValueError("transferências recebidas da epic #62 divergiram")
    category_resolutions = build_category_resolutions(programs)
    resolutions = {
        "schema_version": "1.0",
        "issue": 102,
        "incoming_transfers": transfer_resolutions,
        "outgoing_category_resolutions": category_resolutions,
    }

    outputs = {
        filename: jsonl_bytes(records)
        for filename, records in canonical.items()
    }
    outputs["run-manifest.jsonl"] = jsonl_bytes(manifests)
    outputs["category-resolutions.json"] = json_bytes(resolutions)
    output_hashes = {name: sha256(payload) for name, payload in outputs.items()}

    counts = {
        "agencies": len(agencies),
        "programs": len(programs),
        "calls": len(calls),
        "evidence": len(evidence),
        "coverage_rows": len(canonical["coverage-matrix.jsonl"]),
        "tasks": len(tasks),
    }
    manifest = {
        "schema_version": "1.0",
        "issue": 102,
        "cutoff_date": "2026-07-27",
        "status": "provisional",
        "independent_review_status": "pending",
        "before_counts": before_counts,
        "after_counts": counts,
        "decision_counts": {
            "agencies": dict(
                sorted(Counter(row["decision"] for row in agencies).items())
            ),
            "programs": dict(
                sorted(Counter(row["decision"] for row in programs).items())
            ),
        },
        "incoming_transfers": len(transfer_resolutions),
        "materialized_incoming_transfers": sum(
            row["materialized"] for row in transfer_resolutions
        ),
        "outgoing_category_resolutions": len(category_resolutions),
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
    }
    outputs["consolidation-manifest.json"] = json_bytes(manifest)

    eligible_agencies = sum(row["decision"] == "elegível" for row in agencies)
    eligible_programs = sum(row["decision"] == "elegível" for row in programs)
    pending_agencies = sum("insuficiente" in row["decision"] for row in agencies)
    pending_programs = sum("insuficiente" in row["decision"] for row in programs)
    unmaterialized = sum(not row["materialized"] for row in transfer_resolutions)
    report = f"""# Fila provisória consolidada de programas públicos

Este bundle consolida as quatro auditorias regionais da epic #65 na data de
corte 2026-07-27. Nenhum perfil é publicado nesta etapa.

## Before / after

| Entidade | Antes | Depois |
| --- | ---: | ---: |
| Agências | 27 | {len(agencies)} |
| Programas | 39 | {len(programs)} |
| Chamadas | 21 | {len(calls)} |
| Evidências | 90 | {len(evidence)} |
| Linhas de cobertura | 55 | {len(canonical["coverage-matrix.jsonl"])} |

Não havia IDs duplicados entre regiões. A redução preservou todos os registros,
ordenou-os por ID e reconciliou suas relações.

## Decisões

- Agências elegíveis: {eligible_agencies}.
- Programas elegíveis: {eligible_programs}.
- Agências com evidência insuficiente: {pending_agencies}.
- Programas com evidência insuficiente: {pending_programs}.
- Transferências recebidas da epic #62: {len(transfer_resolutions)}.
- Transferências já ligadas a programas existentes: {
        len(transfer_resolutions) - unmaterialized
    }.
- Transferências que exigem revisão pelo contrato público: {unmaterialized}.
- Fronteiras encaminhadas para fundos ou aceleradoras: {
        len(category_resolutions)
    }.

## Estado do gate

A redução mecânica está concluída, mas a fila ainda é `provisional`. Um agente
diferente do consolidador deve revisar 100% dos elegíveis, pendências e casos de
fronteira antes de congelar os hashes.

## Reprodução

```text
python research/epic-65/consolidation/build_queue.py
python research/epic-65/consolidation/build_queue.py --check
python research/epic-65/validate.py research/epic-65/consolidation
python -m unittest discover -s research/epic-65/consolidation/tests -p "test_*.py"
```
"""
    outputs["README.md"] = report.encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for filename, payload in outputs.items():
        path = HERE / filename
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                drift.append(filename)
        else:
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
