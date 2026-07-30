from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


EPIC_ROOT = Path(__file__).resolve().parents[1]
JSONL_FILES = (
    "candidates.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "review-sample.jsonl",
    "run-manifest.jsonl",
    "source-inventory.jsonl",
)
HASHED_ARTIFACTS = tuple(
    filename for filename in JSONL_FILES if filename != "run-manifest.jsonl"
)


def build_bundle() -> dict[str, Any]:
    """Load the contract example as the canonical mutable test fixture."""
    root = EPIC_ROOT / "examples"
    bundle: dict[str, Any] = {}
    for filename in JSONL_FILES:
        text = (root / filename).read_text(encoding="utf-8")
        bundle[filename] = [
            json.loads(line) for line in text.splitlines() if line.strip()
        ]
    bundle["audit-report.json"] = json.loads(
        (root / "audit-report.json").read_text(encoding="utf-8")
    )
    return bundle


def clone_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(bundle)


def write_bundle(root: Path, bundle: dict[str, Any]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for filename, records in bundle.items():
        path = root / filename
        if filename.endswith(".jsonl"):
            path.write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )
        else:
            path.write_text(
                json.dumps(records, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def artifact_hash(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
