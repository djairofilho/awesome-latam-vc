"""Regression tests for the issue #221 review builder."""

from __future__ import annotations

import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "brazil" / "build_review.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("epic_207_review_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar build_review.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def records(content: bytes) -> list[dict]:
    return [json.loads(line) for line in content.decode("utf-8").splitlines() if line]


class ReviewBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.artifacts = cls.builder.build_artifacts()

    def test_build_is_byte_deterministic(self) -> None:
        self.assertEqual(self.artifacts, self.builder.build_artifacts())

    def test_final_counts_and_review_coverage(self) -> None:
        candidates = records(self.artifacts["candidates.jsonl"])
        reviews = records(self.artifacts["review-sample.jsonl"])
        self.assertEqual(
            Counter(item["decision"] for item in candidates),
            {
                "eligible": 27,
                "duplicate": 13,
                "insufficient_evidence": 28,
                "routed_accelerators": 3,
                "routed_angel_networks": 4,
                "routed_funding_platforms": 1,
            },
        )
        self.assertEqual(
            sum(item["review_group"] == "eligible" for item in reviews),
            27,
        )
        self.assertEqual(
            sum(item["review_group"] == "routed" for item in reviews),
            8,
        )

    def test_review_corrections_are_frozen(self) -> None:
        candidates = {
            item["candidate_id"]: item
            for item in records(self.artifacts["candidates.jsonl"])
        }
        evidence = {
            item["evidence_id"]: item
            for item in records(self.artifacts["evidence.jsonl"])
        }
        identities = {
            item["resolution_id"]: item
            for item in records(self.artifacts["identity-resolution.jsonl"])
        }
        self.assertIsNone(candidates["fund-br-213-vinci-partners"]["manager_id"])
        self.assertEqual(candidates["fund-br-213-vinci-partners"]["aliases"], [])
        for candidate_id in (
            "fund-br-210-dna-capital",
            "fund-br-214-jatoba-impacto-amazonia",
            "fund-br-mundi-ventures-latam",
        ):
            self.assertEqual(candidates[candidate_id]["aliases"], [])
        self.assertIsNone(
            identities["identity-fund-br-vinci-prior-managers"]["manager_id"]
        )
        for evidence_id in self.builder.CORRECTED_ACTIVITY_EVIDENCE:
            activity = next(
                claim
                for claim in evidence[evidence_id]["claims"]
                if claim["field"] == "activity"
            )
            self.assertEqual(activity["finding"], "inconclusive")
            self.assertIsNone(evidence[evidence_id]["observed_on"])

    def test_sha_sample_matches_smallest_final_digests(self) -> None:
        insufficient = [
            item["candidate_id"]
            for item in records(self.artifacts["candidates.jsonl"])
            if item["decision"] == "insufficient_evidence"
        ]
        self.assertEqual(len(insufficient), 28)
        expected = tuple(sorted(
            insufficient,
            key=lambda candidate_id: __import__("hashlib").sha256(
                candidate_id.encode("utf-8")
            ).hexdigest(),
        )[:6])
        self.assertEqual(self.builder.SHA_SAMPLE, expected)
        self.assertGreaterEqual(len(expected) / len(insufficient), 0.20)


if __name__ == "__main__":
    unittest.main()
