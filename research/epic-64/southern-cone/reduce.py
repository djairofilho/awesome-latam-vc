"""Reduce Southern Cone shards, then freeze normalized SHA-256 hashes."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[3]
SHARDS_MODULE_PATH = REPOSITORY / "tools" / "research" / "shards.py"
SPEC = importlib.util.spec_from_file_location("epic64_shards", SHARDS_MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Não foi possível carregar {SHARDS_MODULE_PATH}")
SHARDS_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SHARDS_MODULE)
reduce_shards = SHARDS_MODULE.reduce_shards


DATASET = Path(__file__).parent
RESEARCH_ROOT = DATASET.parent
ARTIFACTS = {
    "candidates": "candidates.jsonl",
    "coverage": "coverage-matrix.jsonl",
    "evidence": "evidence.jsonl",
    "sources": "source-inventory.jsonl",
}


def normalized_hash(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def serialized(records: list[dict]) -> str:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    )


def main() -> None:
    for kind, filename in ARTIFACTS.items():
        reduce_shards(RESEARCH_ROOT, kind, DATASET / filename)

    run_shard = DATASET / "shards" / "coordinator" / "run-manifest.jsonl"
    run = json.loads(run_shard.read_text(encoding="utf-8").strip())
    run["hash_algorithm"] = "sha256"
    run["artifact_hashes"] = {
        filename: normalized_hash(DATASET / filename)
        for filename in sorted(ARTIFACTS.values())
    }
    run_shard.write_text(serialized([run]), encoding="utf-8", newline="\n")
    reduce_shards(RESEARCH_ROOT, "manifest", DATASET / "run-manifest.jsonl")


if __name__ == "__main__":
    main()
