"""Tests for the offline issue #209 baseline."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


BASELINE = Path(__file__).resolve().parents[1]
ROOT = BASELINE.parents[2]
SPEC = importlib.util.spec_from_file_location(
    "build_funds_baseline", BASELINE / "build_baseline.py"
)
assert SPEC and SPEC.loader
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def read_jsonl(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (BASELINE / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = read_jsonl("catalog-baseline.jsonl")
        cls.identities = read_jsonl("identity-index.jsonl")
        cls.candidates = read_jsonl("prior-candidates.jsonl")
        cls.sources = read_jsonl("prior-sources.jsonl")
        cls.queues = read_jsonl("queue-manifest.jsonl")
        cls.pending = read_jsonl("pending-changes.jsonl")
        cls.summary = json.loads(
            (BASELINE / "baseline-summary.json").read_text(encoding="utf-8")
        )

    def test_builder_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BASELINE / "build_baseline.py"), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_catalog_snapshot_matches_published_profiles(self) -> None:
        published = set(BUILD.baseline_profile_paths())
        recorded = {record["profile_path"] for record in self.catalog}
        self.assertEqual(recorded, published)
        self.assertEqual(len(self.identities), len(self.catalog))
        self.assertEqual(
            self.summary["catalog"]["profiles"],
            len(self.catalog),
        )
        self.assertEqual(
            self.summary["catalog"]["brazil_directory_profiles"],
            sum(record["in_brazil_directory"] for record in self.catalog),
        )
        self.assertEqual(
            len({record["entity_id"] for record in self.catalog}),
            len(self.catalog),
        )
        self.assertEqual(
            {record["entity_id"] for record in self.identities},
            {record["entity_id"] for record in self.catalog},
        )

    def test_epic_16_memory_is_complete(self) -> None:
        original_candidates = BUILD.read_baseline_jsonl(
            "research/epic-16/issue-22/candidates.jsonl"
        )
        original_sources = BUILD.read_baseline_jsonl(
            "research/epic-16/issue-22/source-inventory.jsonl"
        )
        self.assertEqual(
            {record["candidate_id"] for record in self.candidates},
            {record["candidate_id"] for record in original_candidates},
        )
        self.assertEqual(
            {record["source_id"] for record in self.sources},
            {record["source_id"] for record in original_sources},
        )
        self.assertEqual(
            self.summary["epic_16_memory"]["candidate_decisions"],
            dict(sorted(Counter(r["decision"] for r in original_candidates).items())),
        )

    def test_queues_partition_each_record_once(self) -> None:
        candidate_members = [
            member
            for queue in self.queues
            if queue["record_type"] == "candidate"
            for member in queue["members"]
        ]
        source_members = [
            member
            for queue in self.queues
            if queue["record_type"] == "source"
            for member in queue["members"]
        ]
        profile_members = [
            member
            for queue in self.queues
            if queue["record_type"] == "profile"
            for member in queue["members"]
        ]
        self.assertEqual(len(candidate_members), len(set(candidate_members)))
        self.assertEqual(
            set(candidate_members),
            {record["candidate_id"] for record in self.candidates},
        )
        self.assertEqual(len(source_members), len(set(source_members)))
        self.assertEqual(
            set(source_members), {record["source_id"] for record in self.sources}
        )
        self.assertEqual(len(profile_members), len(set(profile_members)))
        self.assertEqual(
            set(profile_members), {record["entity_id"] for record in self.catalog}
        )

    def test_domain_collisions_are_not_automatic_merges(self) -> None:
        shared = [
            record
            for record in self.identities
            if record["domain_quality"] in {"shared", "secondary_host"}
        ]
        self.assertTrue(shared)
        for record in shared:
            if record["domain_quality"] == "shared":
                self.assertGreater(len(record["domain_collision_paths"]), 1)

    def test_sources_do_not_count_as_new_discovery(self) -> None:
        self.assertTrue(self.sources)
        self.assertTrue(
            all(record["counts_as_new_discovery"] is False for record in self.sources)
        )
        self.assertTrue(
            all(
                record["research_performed_by_issue_209"] is False
                for record in self.sources
            )
        )

    def test_pr_225_is_pending_and_not_imported(self) -> None:
        self.assertEqual(len(self.pending), 1)
        record = self.pending[0]
        self.assertEqual(record["change_id"], "github-pr-225")
        self.assertEqual(record["status"], "pending")
        self.assertFalse(record["imported"])
        self.assertEqual(record["files_imported"], [])
        self.assertFalse(self.summary["offline_policy"]["pr_225_imported"])

    def test_offline_policy_records_zero_cvm_and_discovery(self) -> None:
        policy = self.summary["offline_policy"]
        self.assertFalse(policy["network_access"])
        self.assertEqual(policy["cvm_queries"], 0)
        self.assertFalse(policy["discovery_performed"])

    def test_summary_hashes_cover_non_circular_artifacts(self) -> None:
        hashes = self.summary["artifact_hashes"]
        self.assertEqual(
            set(hashes),
            {
                "catalog-baseline.jsonl",
                "identity-index.jsonl",
                "pending-changes.jsonl",
                "prior-candidates.jsonl",
                "prior-sources.jsonl",
                "queue-manifest.jsonl",
            },
        )
        for name, expected in hashes.items():
            self.assertEqual(
                hashlib.sha256((BASELINE / name).read_bytes()).hexdigest(),
                expected,
            )


if __name__ == "__main__":
    unittest.main()
