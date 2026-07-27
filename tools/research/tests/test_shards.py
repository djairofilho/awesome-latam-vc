from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RESEARCH_DIR))

from shards import reduce_shards, shard_path, write_shard  # noqa: E402


class ShardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def candidate(self, candidate_id: str, name: str) -> dict[str, str]:
        return {"candidate_id": candidate_id, "name": name}

    def test_writes_worker_owned_shard_in_stable_order(self) -> None:
        path = write_shard(
            self.root,
            "brazil",
            "worker-1",
            "candidates",
            [
                self.candidate("accel-z", "Zulu"),
                self.candidate("accel-a", "Alpha"),
            ],
        )

        self.assertEqual(
            path,
            self.root
            / "brazil"
            / "shards"
            / "worker-1"
            / "candidates.jsonl",
        )
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [record["candidate_id"] for record in records],
            ["accel-a", "accel-z"],
        )

    def test_reduces_shards_deterministically_and_idempotently(self) -> None:
        shared = self.candidate("accel-shared", "Shared")
        write_shard(
            self.root,
            "andean",
            "worker-2",
            "candidates",
            [shared, self.candidate("accel-z", "Zulu")],
        )
        write_shard(
            self.root,
            "brazil",
            "worker-1",
            "candidates",
            [self.candidate("accel-a", "Alpha"), shared],
        )
        destination = self.root / "candidates.jsonl"

        count = reduce_shards(self.root, "candidates", destination)

        self.assertEqual(count, 3)
        records = [
            json.loads(line)
            for line in destination.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [record["candidate_id"] for record in records],
            ["accel-a", "accel-shared", "accel-z"],
        )

    def test_rejects_conflicting_duplicate_ids(self) -> None:
        write_shard(
            self.root,
            "andean",
            "worker-1",
            "candidates",
            [self.candidate("accel-shared", "One")],
        )
        write_shard(
            self.root,
            "brazil",
            "worker-2",
            "candidates",
            [self.candidate("accel-shared", "Two")],
        )

        with self.assertRaisesRegex(ValueError, "conflicting record"):
            reduce_shards(
                self.root,
                "candidates",
                self.root / "candidates.jsonl",
            )

    def test_rejects_unsafe_path_segments(self) -> None:
        with self.assertRaisesRegex(ValueError, "partition"):
            shard_path(self.root, "../outside", "worker-1", "candidates")
