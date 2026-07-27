"""Specific closure tests for the issue #93 Southern Cone audit."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


DATASET = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REDUCER = load_module("southern_cone_reduce", DATASET / "reduce.py")
SHARDS = load_module(
    "epic64_shards_test",
    DATASET.parents[2] / "tools" / "research" / "shards.py",
)


class SouthernConeAuditTests(unittest.TestCase):
    def test_reducer_is_idempotent_and_hashes_match(self) -> None:
        REDUCER.main()
        first = {
            path.name: path.read_bytes()
            for path in DATASET.glob("*.jsonl")
            if path.name != "link-audit.jsonl"
        }
        REDUCER.main()
        second = {
            path.name: path.read_bytes()
            for path in DATASET.glob("*.jsonl")
            if path.name != "link-audit.jsonl"
        }
        self.assertEqual(first, second)

        records = [
            json.loads(line)
            for line in (DATASET / "run-manifest.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        run = next(record for record in records if record["record_type"] == "run")
        for filename, expected in run["artifact_hashes"].items():
            normalized = (
                (DATASET / filename)
                .read_text(encoding="utf-8")
                .replace("\r\n", "\n")
                .encode("utf-8")
            )
            self.assertEqual(hashlib.sha256(normalized).hexdigest(), expected)

    def test_candidate_entities_are_unique_and_offers_never_publish(self) -> None:
        candidates = [
            json.loads(line)
            for line in (DATASET / "candidates.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        platform_ids = [candidate["platform_id"] for candidate in candidates]
        self.assertEqual(len(platform_ids), len(set(platform_ids)))
        entity_ids: list[str] = []
        for candidate in candidates:
            entity_ids.extend(
                [
                    candidate["operator"]["operator_id"],
                    candidate["brand"]["brand_id"],
                    candidate["platform_id"],
                ]
            )
            entity_ids.extend(product["product_id"] for product in candidate["products"])
            entity_ids.extend(offer["offer_id"] for offer in candidate["offers"])
            entity_ids.extend(record["regulatory_id"] for record in candidate["regulatory_records"])
            self.assertTrue(all(not offer["profile_eligible"] for offer in candidate["offers"]))
        self.assertEqual(len(entity_ids), len(set(entity_ids)))

    def test_reducer_rejects_conflicting_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for worker, name in (("worker-a", "A"), ("worker-b", "B")):
                shard = root / "partition" / "shards" / worker
                shard.mkdir(parents=True)
                record = {"platform_id": "plat-duplicate", "platform": {"name": name}}
                (shard / "candidates.jsonl").write_text(
                    json.dumps(record) + "\n", encoding="utf-8", newline="\n"
                )
            with self.assertRaisesRegex(ValueError, "conflicting record"):
                SHARDS.reduce_shards(root, "candidates", root / "partition" / "candidates.jsonl")


if __name__ == "__main__":
    unittest.main()
