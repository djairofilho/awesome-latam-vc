from __future__ import annotations

import json
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
        cls.agencies = read_jsonl("agencies.jsonl")
        cls.programs = read_jsonl("programs.jsonl")
        cls.calls = read_jsonl("calls.jsonl")
        cls.evidence = read_jsonl("evidence.jsonl")
        cls.coverage = read_jsonl("coverage-matrix.jsonl")
        cls.manifest_rows = read_jsonl("run-manifest.jsonl")
        cls.manifest = json.loads(
            (ROOT / "consolidation-manifest.json").read_text(encoding="utf-8")
        )
        cls.resolutions = json.loads(
            (ROOT / "category-resolutions.json").read_text(encoding="utf-8")
        )

    def test_expected_counts(self) -> None:
        self.assertEqual(27, len(self.agencies))
        self.assertEqual(39, len(self.programs))
        self.assertEqual(21, len(self.calls))
        self.assertEqual(90, len(self.evidence))
        self.assertEqual(55, len(self.coverage))

    def test_ids_are_unique(self) -> None:
        for records, field in (
            (self.agencies, "agency_id"),
            (self.programs, "program_id"),
            (self.calls, "call_id"),
            (self.evidence, "evidence_id"),
            (self.coverage, "coverage_id"),
        ):
            self.assertEqual(len(records), len({row[field] for row in records}))

    def test_no_decision_is_null(self) -> None:
        self.assertTrue(
            all(row["decision"] is not None for row in (*self.agencies, *self.programs))
        )

    def test_pending_records_are_actionable(self) -> None:
        pending = [
            row
            for row in (*self.agencies, *self.programs)
            if "insuficiente" in row["decision"]
        ]
        self.assertEqual(10, len(pending))
        self.assertTrue(all(row["owner"] and row["next_action"] for row in pending))

    def test_relationships_are_closed(self) -> None:
        agency_ids = {row["agency_id"] for row in self.agencies}
        program_ids = {row["program_id"] for row in self.programs}
        call_ids = {row["call_id"] for row in self.calls}
        evidence_ids = {row["evidence_id"] for row in self.evidence}
        self.assertTrue(all(row["agency_id"] in agency_ids for row in self.programs))
        self.assertTrue(all(row["program_id"] in program_ids for row in self.calls))
        for row in (*self.agencies, *self.programs, *self.calls):
            self.assertLessEqual(set(row["official_evidence_ids"]), evidence_ids)
        for agency in self.agencies:
            self.assertLessEqual(set(agency["program_ids"]), program_ids)
        for program in self.programs:
            self.assertLessEqual(set(program["call_ids"]), call_ids)

    def test_transfers_have_destinations(self) -> None:
        incoming = self.resolutions["incoming_transfers"]
        outgoing = self.resolutions["outgoing_category_resolutions"]
        self.assertEqual(13, len(incoming))
        self.assertEqual(5, len(outgoing))
        self.assertTrue(all(row["target_program_id"] for row in incoming))
        self.assertTrue(all(row["canonical_destination"] for row in outgoing))
        pending = [row for row in incoming if not row["materialized"]]
        self.assertTrue(all(row["owner"] and row["next_action"] for row in pending))

    def test_single_consolidated_run(self) -> None:
        runs = [row for row in self.manifest_rows if row["record_type"] == "run"]
        tasks = [row for row in self.manifest_rows if row["record_type"] == "task"]
        self.assertEqual(1, len(runs))
        self.assertEqual(55, len(tasks))
        self.assertEqual(55, runs[0]["task_count"])

    def test_manifest_is_provisional_until_independent_review(self) -> None:
        self.assertEqual("provisional", self.manifest["status"])
        self.assertEqual("pending", self.manifest["independent_review_status"])

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
