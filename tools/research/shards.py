"""Write isolated research-worker shards and reduce them deterministically."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


KIND_TO_FILENAME = {
    "candidates": "candidates.jsonl",
    "coverage": "coverage-matrix.jsonl",
    "evidence": "evidence.jsonl",
    "manifest": "run-manifest.jsonl",
    "sources": "source-inventory.jsonl",
}
ID_FIELD_BY_KIND = {
    "candidates": "candidate_id",
    "coverage": "coverage_id",
    "evidence": "evidence_id",
    "sources": "source_id",
}


def _safe_segment(value: str, label: str) -> str:
    if not value or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in value):
        raise ValueError(f"{label} must contain only lowercase letters, digits and hyphens")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            raise ValueError(f"{path}:{line_number}: empty JSONL line")
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(record)
    return records


def _record_key(kind: str, record: dict[str, Any]) -> str:
    if kind == "manifest":
        record_type = record.get("record_type")
        field = "run_id" if record_type == "run" else "task_id"
    else:
        field = ID_FIELD_BY_KIND[kind]
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{kind} record is missing string key {field}")
    return f"{record.get('record_type', kind)}:{value}"


def _serialized(records: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for record in records
    )


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def shard_path(root: Path, partition: str, worker: str, kind: str) -> Path:
    partition = _safe_segment(partition, "partition")
    worker = _safe_segment(worker, "worker")
    if kind not in KIND_TO_FILENAME:
        raise ValueError(f"unknown shard kind: {kind}")
    return root / partition / "shards" / worker / KIND_TO_FILENAME[kind]


def write_shard(
    root: Path,
    partition: str,
    worker: str,
    kind: str,
    records: list[dict[str, Any]],
) -> Path:
    """Atomically replace one worker-owned shard."""
    path = shard_path(root, partition, worker, kind)
    ordered = sorted(records, key=lambda record: _record_key(kind, record))
    keys = [_record_key(kind, record) for record in ordered]
    if len(keys) != len(set(keys)):
        raise ValueError(f"duplicate keys in worker shard: {path}")
    _atomic_write(path, _serialized(ordered))
    return path


def reduce_shards(root: Path, kind: str, destination: Path) -> int:
    """Reduce all worker shards for a kind into a stable canonical JSONL file."""
    if kind not in KIND_TO_FILENAME:
        raise ValueError(f"unknown shard kind: {kind}")
    filename = KIND_TO_FILENAME[kind]
    records_by_key: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob(f"*/shards/*/{filename}")):
        for record in read_jsonl(path):
            key = _record_key(kind, record)
            existing = records_by_key.get(key)
            if existing is not None and existing != record:
                raise ValueError(f"conflicting record {key} in {path}")
            records_by_key[key] = record
    ordered = [records_by_key[key] for key in sorted(records_by_key)]
    _atomic_write(destination, _serialized(ordered))
    return len(ordered)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    write_parser = commands.add_parser("write", help="replace one worker-owned shard")
    write_parser.add_argument("root", type=Path)
    write_parser.add_argument("partition")
    write_parser.add_argument("worker")
    write_parser.add_argument("kind", choices=sorted(KIND_TO_FILENAME))
    write_parser.add_argument("input", type=Path)

    reduce_parser = commands.add_parser(
        "reduce",
        help="reduce all shards of one kind deterministically",
    )
    reduce_parser.add_argument("root", type=Path)
    reduce_parser.add_argument("kind", choices=sorted(KIND_TO_FILENAME))
    reduce_parser.add_argument("destination", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "write":
        records = read_jsonl(args.input)
        print(write_shard(args.root, args.partition, args.worker, args.kind, records))
    else:
        print(reduce_shards(args.root, args.kind, args.destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
