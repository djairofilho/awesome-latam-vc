"""Consolida deterministicamente os shards da auditoria do Cone Sul."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
KINDS = {
    "agency_id": ("agencies.jsonl", "agency_id"),
    "program_id": ("programs.jsonl", "program_id"),
    "call_id": ("calls.jsonl", "call_id"),
    "evidence_id": ("evidence.jsonl", "evidence_id"),
}


def main() -> None:
    grouped = {filename: [] for filename, _ in KINDS.values()}
    seen: set[str] = set()
    for shard in sorted((ROOT / "shards").glob("worker-*/records.jsonl")):
        for number, line in enumerate(shard.read_text(encoding="utf-8").splitlines(), 1):
            record = json.loads(line)
            primary_key = next(
                (key for key in ("evidence_id", "call_id", "program_id", "agency_id")
                 if key in record),
                None,
            )
            if primary_key is None:
                raise ValueError(f"{shard}:{number}: tipo de registro ambíguo")
            filename, key = KINDS[primary_key]
            record_id = record[key]
            if record_id in seen:
                raise ValueError(f"{shard}:{number}: ID duplicado: {record_id}")
            seen.add(record_id)
            grouped[filename].append(record)

    for filename, rows in grouped.items():
        key = next(sort_key for output, sort_key in KINDS.values() if output == filename)
        content = "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in sorted(rows, key=lambda item: item[key])
        )
        (ROOT / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
