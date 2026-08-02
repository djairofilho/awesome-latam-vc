#!/usr/bin/env python3
"""Reconcile normalized geographic intake shards without reading the private queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
OUTPUT = EPIC / "intake" / "summary.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: JSON inválido: {exc}") from exc
    return records


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile() -> tuple[list[str], dict]:
    errors: list[str] = []
    topology = read_json(EPIC / "workers" / "topology.json")
    schema = read_json(EPIC / "schemas" / "normalized-intake-record.schema.json")
    validator = Draft202012Validator(schema)
    workers = [item for item in topology["workers"] if item["phase"] == "triage"]

    aggregate = Counter()
    candidate_shards: dict[str, list[str]] = defaultdict(list)
    candidate_countries: set[tuple[str, str]] = set()
    inputs = []

    for worker in workers:
        shard = EPIC / "shards" / worker["worker_id"]
        intake_path = shard / "intake.jsonl"
        summary_path = shard / "summary.json"
        if not intake_path.exists() or not summary_path.exists():
            errors.append(f"{worker['worker_id']}: intake.jsonl ou summary.json ausente")
            continue

        try:
            records = read_jsonl(intake_path)
            summary = read_json(summary_path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue

        seen_ids = set()
        observed = 0
        expected_countries = set(worker["countries"])
        status_counts = Counter()
        for index, record in enumerate(records, 1):
            prefix = f"{intake_path}:{index}"
            for error in validator.iter_errors(record):
                errors.append(f"{prefix}: {error.message}")
            candidate_id = record.get("candidate_id")
            if candidate_id in seen_ids:
                errors.append(f"{prefix}: candidate_id duplicado no shard")
            seen_ids.add(candidate_id)
            candidate_shards[candidate_id].append(worker["worker_id"])
            countries = record.get("country_occurrences", {})
            if not set(countries).issubset(expected_countries):
                errors.append(f"{prefix}: país fora da propriedade do worker")
            if record.get("occurrence_count") != sum(countries.values()):
                errors.append(f"{prefix}: occurrence_count não reconcilia")
            for country in countries:
                key = (candidate_id, country)
                if key in candidate_countries:
                    errors.append(f"{prefix}: candidato/país aparece em mais de um shard")
                candidate_countries.add(key)
            observed += record.get("occurrence_count", 0)
            status_counts[record.get("baseline_status")] += 1

        gaps = summary.get("gaps", {})
        page_failures = gaps.get("page_failures", 0)
        unparsed_rows = gaps.get("unparsed_rows", 0)
        checks = {
            "worker_id": worker["worker_id"],
            "countries": sorted(worker["countries"]),
            "canonical_candidates": len(records),
            "baseline_matches": sum(
                status_counts[name]
                for name in ("exact_name", "alias", "identity_collision")
            ),
            "new_candidates": status_counts["new"],
            "unresolved_candidates": status_counts["unresolved"],
            "raw_occurrences": observed + unparsed_rows,
        }
        for key, expected in checks.items():
            actual = sorted(summary.get(key, [])) if key == "countries" else summary.get(key)
            if actual != expected:
                errors.append(
                    f"{summary_path}: {key}={actual!r}; esperado {expected!r}"
                )
        if summary.get("pages_processed", 0) + page_failures != summary.get(
            "pages_expected"
        ):
            errors.append(f"{summary_path}: páginas não reconciliam")

        aggregate.update(
            pages_expected=summary.get("pages_expected", 0),
            pages_processed=summary.get("pages_processed", 0),
            page_failures=page_failures,
            raw_occurrences=summary.get("raw_occurrences", 0),
            unparsed_rows=unparsed_rows,
            shard_candidates=len(records),
            baseline_matches=checks["baseline_matches"],
            new_candidates=checks["new_candidates"],
            unresolved_candidates=checks["unresolved_candidates"],
        )
        inputs.extend(
            [
                {"path": intake_path.relative_to(ROOT).as_posix(), "sha256": sha256(intake_path)},
                {"path": summary_path.relative_to(ROOT).as_posix(), "sha256": sha256(summary_path)},
            ]
        )

    result = {
        "schema_version": "1.0",
        "epic": 327,
        "issue": 329,
        "shards": len(workers),
        **dict(sorted(aggregate.items())),
        "unique_candidates": len(candidate_shards),
        "cross_shard_candidates": sum(
            1 for shards in candidate_shards.values() if len(set(shards)) > 1
        ),
        "inputs": sorted(inputs, key=lambda item: item["path"]),
    }
    return errors, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors, result = reconcile()
    if errors:
        print("Reconciliação do intake falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"{OUTPUT}: resumo ausente ou desatualizado", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print("Intake normalizado reconciliado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
