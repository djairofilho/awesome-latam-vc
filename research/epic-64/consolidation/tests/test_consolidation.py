from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[2]


def read_jsonl(filename: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class ConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = read_jsonl("candidates.jsonl")
        cls.evidence = read_jsonl("evidence.jsonl")
        cls.sources = read_jsonl("source-inventory.jsonl")
        cls.coverage = read_jsonl("coverage-matrix.jsonl")
        cls.review = read_jsonl("independent-review.jsonl")
        cls.manifest_rows = read_jsonl("run-manifest.jsonl")
        cls.manifest = json.loads(
            (ROOT / "consolidation-manifest.json").read_text(encoding="utf-8")
        )
        cls.dedupe = json.loads(
            (ROOT / "deduplication-report.json").read_text(encoding="utf-8")
        )
        cls.resolutions = json.loads(
            (ROOT / "category-resolutions.json").read_text(encoding="utf-8")
        )

    def test_expected_counts_and_unique_ids(self) -> None:
        self.assertEqual(39, len(self.candidates))
        self.assertEqual(63, len(self.evidence))
        self.assertEqual(118, len(self.sources))
        self.assertEqual(20, len(self.coverage))
        for rows, field in (
            (self.candidates, "platform_id"),
            (self.evidence, "evidence_id"),
            (self.sources, "source_id"),
            (self.coverage, "country"),
        ):
            self.assertEqual(len(rows), len({row[field] for row in rows}))

    def test_decisions_are_complete(self) -> None:
        self.assertTrue(all(row["decision"] is not None for row in self.candidates))
        pending = [
            row
            for row in self.candidates
            if row["decision"] == "insufficient_evidence"
        ]
        self.assertEqual(18, len(pending))
        self.assertTrue(all(row["owner"] and row["next_action"] for row in pending))

    def test_nested_identities_are_unique(self) -> None:
        for getter in (
            lambda row: [row["operator"]["operator_id"]],
            lambda row: [row["brand"]["brand_id"]],
            lambda row: [item["product_id"] for item in row["products"]],
            lambda row: [item["offer_id"] for item in row["offers"]],
            lambda row: [
                item["regulatory_id"] for item in row["regulatory_records"]
            ],
        ):
            ids = [item for row in self.candidates for item in getter(row)]
            self.assertEqual(len(ids), len(set(ids)))

    def test_references_are_closed(self) -> None:
        platform_ids = {row["platform_id"] for row in self.candidates}
        evidence_ids = {row["evidence_id"] for row in self.evidence}
        source_ids = {row["source_id"] for row in self.sources}
        self.assertTrue(
            all(row["platform_id"] in platform_ids for row in self.evidence)
        )
        for candidate in self.candidates:
            self.assertLessEqual(
                set(candidate["official_evidence_ids"])
                | set(candidate["activity_evidence_ids"])
                | set(candidate["route_evidence_ids"]),
                evidence_ids,
            )
            self.assertLessEqual(
                set(candidate["discovery_source_ids"]), source_ids
            )

    def test_two_pass_deduplication_is_clean(self) -> None:
        self.assertFalse(
            self.dedupe["pass_1_domain_brand"]["unresolved_groups"]
        )
        self.assertFalse(
            self.dedupe["pass_2_legal_regulatory"][
                "legal_name_unresolved_groups"
            ]
        )
        self.assertFalse(
            self.dedupe["pass_2_legal_regulatory"][
                "regulatory_unresolved_groups"
            ]
        )

    def test_category_transfers_have_destinations(self) -> None:
        outgoing = self.resolutions["outgoing_category_resolutions"]
        incoming = self.resolutions["incoming_angel_transfers"]
        self.assertEqual(6, len(outgoing))
        self.assertTrue(all(row["canonical_destination"] for row in outgoing))
        self.assertEqual(3, len(incoming))
        self.assertTrue(all(row["canonical_destination"] for row in incoming))
        self.assertTrue(all(row["adjudication"] for row in incoming))
        self.assertFalse(any(row["owner"] or row["next_action"] for row in incoming))
        self.assertEqual(1, sum(row["materialized"] for row in incoming))

    def test_single_manifest_run(self) -> None:
        runs = [row for row in self.manifest_rows if row["record_type"] == "run"]
        tasks = [row for row in self.manifest_rows if row["record_type"] == "task"]
        self.assertEqual(1, len(runs))
        self.assertEqual(runs[0]["task_count"], len(tasks))
        self.assertEqual([90, 91, 92, 93], runs[0]["issues"])

    def test_independent_review_covers_required_populations(self) -> None:
        groups = {}
        for row in self.review:
            groups.setdefault(row["review_group"], []).append(row)
        eligible = {
            row["platform_id"]
            for row in self.candidates
            if row["decision"] == "eligible"
        }
        other = {
            row["platform_id"]
            for row in self.candidates
            if row["decision"] == "other_category"
        }
        self.assertEqual(
            eligible,
            {row["subject_id"] for row in groups["eligible"]},
        )
        self.assertEqual(
            other,
            {row["subject_id"] for row in groups["other_category"]},
        )
        self.assertEqual(
            other,
            {row["subject_id"] for row in groups["outgoing_transfer"]},
        )
        self.assertEqual(3, len(groups["incoming_transfer"]))
        self.assertTrue(all(row["resolved"] for row in self.review))

    def test_remaining_sample_is_deterministic_and_at_least_twenty_percent(self) -> None:
        covered = {
            row["subject_id"]
            for row in self.review
            if row["review_group"] in {"eligible", "other_category"}
        }
        incoming_targets = {
            row["target_platform_id"]
            for row in self.resolutions["incoming_angel_transfers"]
            if row["target_platform_id"]
        }
        population = sorted(
            row["platform_id"]
            for row in self.candidates
            if row["platform_id"] not in covered | incoming_targets
        )
        expected_size = math.ceil(len(population) * 0.20)
        expected = [
            platform_id
            for _, platform_id in sorted(
                (
                    hashlib.sha256(platform_id.encode("utf-8")).hexdigest(),
                    platform_id,
                )
                for platform_id in population
            )[:expected_size]
        ]
        actual = [
            row["subject_id"]
            for row in self.review
            if row["review_group"] == "deterministic_sample"
        ]
        self.assertEqual(set(expected), set(actual))
        self.assertEqual(expected, self.manifest["independent_review"]["sample_ids"])
        self.assertGreaterEqual(len(actual) / len(population), 0.20)

    def test_manifest_is_frozen_without_open_high_divergence(self) -> None:
        self.assertEqual("frozen", self.manifest["status"])
        self.assertEqual("complete", self.manifest["independent_review_status"])
        self.assertEqual(
            0,
            self.manifest["independent_review"]["unresolved_high_divergences"],
        )
        self.assertEqual(len(self.review), self.manifest["independent_review"]["review_count"])

    def test_manifest_hashes_match_reviewed_outputs(self) -> None:
        for filename, expected in self.manifest["output_hashes"].items():
            actual = hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
            self.assertEqual(expected, actual, filename)

    def test_generator_has_no_drift(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_queue.py"), "--check"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
