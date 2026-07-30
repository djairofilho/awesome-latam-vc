"""Regression tests for the issue #222 freeze builder."""

from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "brazil" / "build_frozen.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("epic_207_freeze_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar build_frozen.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records(content: bytes) -> list[dict]:
    return [
        json.loads(line)
        for line in content.decode("utf-8").splitlines()
        if line
    ]


class FreezeBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.artifacts = cls.builder.build_artifacts()
        cls.freeze = json.loads(cls.artifacts["freeze-manifest.json"])

    def test_build_is_byte_deterministic(self) -> None:
        self.assertEqual(self.artifacts, self.builder.build_artifacts())

    def test_all_sources_and_identities_are_terminal(self) -> None:
        sources = records(self.artifacts["source-inventory.jsonl"])
        identities = records(self.artifacts["identity-resolution.jsonl"])
        self.assertTrue(
            all(item["result"] in {"complete", "gap_justified"} for item in sources)
        )
        self.assertEqual(
            Counter(item["result"] for item in sources),
            {"complete": 163, "gap_justified": 9},
        )
        self.assertFalse(
            any(item["resolution"] == "unresolved" for item in identities)
        )

    def test_every_candidate_is_decided_and_destinations_are_exact(self) -> None:
        candidates = records(self.artifacts["candidates.jsonl"])
        self.assertEqual(len(candidates), 76)
        self.assertTrue(all(item["decision"] is not None for item in candidates))
        eligible = [item for item in candidates if item["decision"] == "eligible"]
        self.assertEqual(len(eligible), 27)
        destinations = [item["destination"] for item in eligible]
        self.assertEqual(len(destinations), len(set(destinations)))
        self.assertTrue(all(path.endswith(".md") for path in destinations))
        self.assertFalse(self.freeze["publication"]["published_at_freeze"])
        self.assertTrue(all(
            item["decision"] != "duplicate"
            or item["canonical_candidate_id"]
            or item["canonical_profile"]
            for item in candidates
        ))

    def test_review_coverage_satisfies_freeze_contract(self) -> None:
        reviews = records(self.artifacts["review-sample.jsonl"])
        groups = Counter(item["review_group"] for item in reviews)
        self.assertEqual(groups["eligible"], 27)
        self.assertEqual(groups["routed"], 8)
        self.assertEqual(groups["cvm_consulted"], 2)
        self.assertEqual(groups["deterministic_exclusion_sample"], 6)
        self.assertGreaterEqual(6 / 28, 0.20)
        self.assertTrue(all(item["resolved"] for item in reviews))

    def test_freeze_has_three_complete_non_overlapping_batches(self) -> None:
        publication = self.freeze["publication"]
        self.assertEqual(publication["eligible_count"], 27)
        self.assertEqual(publication["batch_count"], 3)
        self.assertEqual(
            [batch["candidate_count"] for batch in publication["batches"]],
            [9, 9, 9],
        )
        members = [
            item["candidate_id"]
            for batch in publication["batches"]
            for item in batch["candidates"]
        ]
        self.assertEqual(len(members), 27)
        self.assertEqual(len(set(members)), 27)
        self.assertFalse(publication["published_at_freeze"])

    def test_core_hashes_and_metrics_are_frozen(self) -> None:
        hashes = self.freeze["core_artifact_hashes"]
        self.assertEqual(set(hashes), set(self.builder.CORE_JSONL))
        for filename in self.builder.CORE_JSONL:
            self.assertEqual(hashes[filename], self.builder.sha256(
                self.artifacts[filename]
            ))
        self.assertEqual(self.freeze["totals"]["canonical_candidates"], 63)
        self.assertEqual(self.freeze["totals"]["critical_findings_open"], 0)
        self.assertEqual(self.freeze["totals"]["high_findings_open"], 0)
        audit = json.loads(self.artifacts["audit-report.json"])
        self.assertEqual(audit["status"], "frozen")
        self.assertEqual(audit["issue"], 222)
        self.assertEqual(audit["cvm_consulted_candidate_count"], 2)
        self.assertEqual(audit["cvm_query_rate"], 2 / 63)
        self.assertEqual(audit["non_cvm_task_share"], 10 / 11)


if __name__ == "__main__":
    unittest.main()
