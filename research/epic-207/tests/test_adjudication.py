from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


EPIC_ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = EPIC_ROOT / "brazil" / "build_adjudicated.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "epic_207_adjudication", BUILD_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AdjudicationBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.artifacts = cls.builder.build_artifacts()
        cls.records = {
            filename: [
                json.loads(line)
                for line in cls.artifacts[filename]
                .decode("utf-8")
                .splitlines()
            ]
            for filename in cls.builder.CORE_JSONL
        }

    def test_all_validation_overlays_are_applied(self) -> None:
        candidates = self.records["candidates.jsonl"]
        self.assertEqual(51, len(candidates))
        self.assertEqual(
            {
                "eligible": 14,
                "duplicate": 11,
                "insufficient_evidence": 24,
                "routed_accelerators": 1,
                "routed_angel_networks": 1,
            },
            dict(Counter(record["decision"] for record in candidates)),
        )
        canonical_count = sum(
            record["decision"] != "duplicate"
            and record["canonical_candidate_id"] is None
            for record in candidates
        )
        self.assertEqual(40, canonical_count)

    def test_cvm_is_limited_to_two_identity_queries(self) -> None:
        queries = self.records["cvm-query-log.jsonl"]
        self.assertEqual(2, len(queries))
        self.assertEqual(
            self.builder.EXPECTED_QUERY_CANDIDATES,
            {record["candidate_id"] for record in queries},
        )
        allowed = {
            "legal_identity",
            "manager_vehicle_relation",
            "regulatory_divergence",
        }
        self.assertTrue(
            all(set(record["confirmed_claims"]) <= allowed for record in queries)
        )
        candidates = {
            record["candidate_id"]: record
            for record in self.records["candidates.jsonl"]
        }
        self.assertTrue(
            all(
                candidates[candidate_id]["decision"]
                == "insufficient_evidence"
                for candidate_id in self.builder.EXPECTED_QUERY_CANDIDATES
            )
        )

    def test_task_and_query_ratios_respect_contract(self) -> None:
        audit = json.loads(
            self.artifacts["audit-report.json"].decode("utf-8")
        )
        self.assertEqual(0.05, audit["cvm_query_rate"])
        self.assertEqual(10 / 11, audit["non_cvm_task_share"])
        tasks = [
            record
            for record in (
                json.loads(line)
                for line in self.artifacts["run-manifest.jsonl"]
                .decode("utf-8")
                .splitlines()
            )
            if record["record_type"] == "task"
        ]
        self.assertEqual(11, len(tasks))
        self.assertEqual(
            {"non_cvm": 10, "cvm": 1},
            dict(Counter(record["research_channel"] for record in tasks)),
        )

    def test_validation_coverage_is_reduced_to_one_cell(self) -> None:
        keys = [
            (row["source_family"], row["geography_scope"])
            for row in self.records["coverage-matrix.jsonl"]
        ]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn(("cvm", "brazil"), keys)
        validation = next(
            row
            for row in self.records["coverage-matrix.jsonl"]
            if (
                row["source_family"],
                row["geography_scope"],
            )
            == ("official_portfolios", "brazil")
        )
        self.assertEqual(32, len(validation["source_ids"]))
        self.assertEqual(32, len(validation["candidate_ids"]))
        self.assertEqual(32, validation["planned_sources"])
        self.assertEqual(32, validation["completed_sources"])

    def test_stale_access_dates_do_not_prove_activity(self) -> None:
        evidence = {
            record["evidence_id"]: record
            for record in self.records["evidence.jsonl"]
        }
        for evidence_id in self.builder.STALE_ACCESS_DATE_ACTIVITY_EVIDENCE:
            record = evidence[evidence_id]
            self.assertIsNone(record["published_on"])
            self.assertIsNone(record["observed_on"])
            activity = next(
                claim
                for claim in record["claims"]
                if claim["field"] == "activity"
            )
            self.assertEqual("inconclusive", activity["finding"])

    def test_build_is_byte_deterministic(self) -> None:
        self.assertEqual(self.artifacts, self.builder.build_artifacts())


if __name__ == "__main__":
    unittest.main()
