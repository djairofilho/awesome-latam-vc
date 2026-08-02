#!/usr/bin/env python3
"""Validate the issue #328 delta contract, baseline and worker topology."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASELINE_COMMIT = "4190d8c59d47e50784383bf6a83efb6249859bdb"
MOJIBAKE_MARKERS = ("Ã", "Â", "�", "\x07")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_contract() -> list[str]:
    errors: list[str] = []
    contract = load_json(HERE / "contract.json")
    topology = load_json(HERE / "workers" / "topology.json")
    summary = load_json(HERE / "baseline" / "summary.json")

    if contract.get("baseline_commit") != BASELINE_COMMIT:
        errors.append("contract.json: baseline_commit divergente")
    if summary.get("baseline_commit") != BASELINE_COMMIT:
        errors.append("baseline/summary.json: baseline_commit divergente")
    if topology.get("baseline_commit") != BASELINE_COMMIT:
        errors.append("workers/topology.json: baseline_commit divergente")

    layers = contract.get("layers", {})
    if set(layers) != {"discovery", "official_evidence", "decision"}:
        errors.append("contract.json: camadas de dados incompletas")
    source_policy = contract.get("source_policy", {})
    if not source_policy.get("official_sources_required_for_published_facts"):
        errors.append("contract.json: fonte oficial não é obrigatória")
    if source_policy.get("third_party_descriptions_imported"):
        errors.append("contract.json: descrições externas não podem ser importadas")

    workers = topology.get("workers", [])
    if len(workers) != 6:
        errors.append("workers/topology.json: são necessários seis writers")
    for key in ("worker_id", "branch", "worktree", "write_prefix"):
        values = [worker.get(key) for worker in workers]
        if len(values) != len(set(values)):
            errors.append(f"workers/topology.json: {key} não é exclusivo")
    partitions = sorted(
        worker.get("partition")
        for worker in workers
        if worker.get("phase") == "validation"
    )
    if partitions != [0, 1, 2]:
        errors.append(
            "workers/topology.json: partições de validação devem ser 0, 1 e 2"
        )

    for schema_path in sorted((HERE / "schemas").glob("*.schema.json")):
        try:
            Draft202012Validator.check_schema(load_json(schema_path))
        except Exception as exc:
            relative = schema_path.relative_to(ROOT).as_posix()
            errors.append(f"{relative}: schema inválido: {exc}")

    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".jsonl", ".md", ".py"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            relative = path.relative_to(ROOT).as_posix()
            errors.append(f"{relative}: UTF-8 inválido: {exc}")
            continue
        if path.name == "validate.py":
            continue
        for marker in MOJIBAKE_MARKERS:
            if marker in text:
                relative = path.relative_to(ROOT).as_posix()
                errors.append(f"{relative}: possível mojibake {marker!r}")

    result = subprocess.run(
        [sys.executable, str(HERE / "baseline" / "build_baseline.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        errors.append(f"baseline: geração não é reproduzível: {detail}")

    if not re.fullmatch(r"[0-9a-f]{40}", summary.get("baseline_commit", "")):
        errors.append("baseline/summary.json: SHA deve ter 40 caracteres hexadecimais")
    return sorted(set(errors))


def main() -> int:
    errors = validate_contract()
    if errors:
        print("Validação da epic #327 falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Contrato delta da epic #327 validado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
