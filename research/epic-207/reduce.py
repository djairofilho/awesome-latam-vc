"""Write worker-owned shards and reduce Brazil funds research deterministically."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


KINDS = {
    "sources": ("source-inventory.jsonl", "source_id"),
    "candidates": ("candidates.jsonl", "candidate_id"),
    "evidence": ("evidence.jsonl", "evidence_id"),
    "identity": ("identity-resolution.jsonl", "resolution_id"),
    "coverage": ("coverage-matrix.jsonl", "coverage_id"),
    "cvm-queries": ("cvm-query-log.jsonl", "query_id"),
    "reviews": ("review-sample.jsonl", "review_id"),
}


def _safe_segment(value: str, label: str) -> str:
    if not value or not all(character in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in value):
        raise ValueError(f"{label} must use lowercase letters, digits and hyphens")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError(f"{path}:{line_number}: empty JSONL line")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    return records


def _key(kind: str, record: dict[str, Any]) -> str:
    field = KINDS[kind][1]
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{kind} record is missing {field}")
    return value


def _serialized(records: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    )


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", text=True
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def shard_path(root: Path, worker: str, kind: str) -> Path:
    worker = _safe_segment(worker, "worker")
    if kind not in KINDS:
        raise ValueError(f"unknown shard kind: {kind}")
    return root / "brazil" / "shards" / worker / KINDS[kind][0]


def write_shard(
    root: Path,
    worker: str,
    kind: str,
    records: list[dict[str, Any]],
) -> Path:
    path = shard_path(root, worker, kind)
    ordered = sorted(records, key=lambda record: _key(kind, record))
    keys = [_key(kind, record) for record in ordered]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate IDs in worker shard: {path}")
    _atomic_write(path, _serialized(ordered))
    return path


def reduce_shards(root: Path, kind: str, destination: Path) -> int:
    if kind not in KINDS:
        raise ValueError(f"unknown shard kind: {kind}")
    expected_destination = root / "brazil" / KINDS[kind][0]
    if destination.resolve() != expected_destination.resolve():
        raise ValueError(f"destination must be {expected_destination}")
    records: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted((root / "brazil" / "shards").glob(f"*/{KINDS[kind][0]}")):
        for record in read_jsonl(path):
            key = _key(kind, record)
            if key in records:
                previous = records[key][0]
                raise ValueError(f"duplicate ID {key} in {previous} and {path}")
            records[key] = (path, record)
    ordered = [records[key][1] for key in sorted(records)]
    _atomic_write(destination, _serialized(ordered))
    return len(ordered)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    write = commands.add_parser("write")
    write.add_argument("root", type=Path)
    write.add_argument("worker")
    write.add_argument("kind", choices=sorted(KINDS))
    write.add_argument("input", type=Path)
    reduce = commands.add_parser("reduce")
    reduce.add_argument("root", type=Path)
    reduce.add_argument("kind", choices=sorted(KINDS))
    reduce.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    if args.command == "write":
        print(write_shard(args.root, args.worker, args.kind, read_jsonl(args.input)))
    else:
        print(reduce_shards(args.root, args.kind, args.destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
