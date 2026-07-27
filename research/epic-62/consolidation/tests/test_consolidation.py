from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = ROOT.parents[2]


def read_jsonl(name: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class ConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = read_jsonl("candidates.jsonl")
        cls.evidence = read_jsonl("evidence.jsonl")
        cls.sources = read_jsonl("source-inventory.jsonl")
        cls.manifest = json.loads(
            (ROOT / "consolidation-manifest.json").read_text(encoding="utf-8")
        )

    def test_expected_counts_and_unique_ids(self) -> None:
        self.assertEqual(78, len(self.candidates))
        self.assertEqual(
            78, len({candidate["candidate_id"] for candidate in self.candidates})
        )
        self.assertEqual(86, len(self.evidence))
        self.assertEqual(80, len(self.sources))

    def test_every_candidate_has_a_decision(self) -> None:
        self.assertFalse(
            [row["candidate_id"] for row in self.candidates if row["decision"] is None]
        )

    def test_pending_evidence_is_actionable(self) -> None:
        pending = [
            row
            for row in self.candidates
            if "insuficiente" in row["decision"]
        ]
        self.assertEqual(19, len(pending))
        self.assertTrue(all(row["owner"] and row["next_action"] for row in pending))

    def test_routes_have_canonical_destinations(self) -> None:
        routes = [
            row
            for row in self.candidates
            if row["decision"]
            in {"encaminhado-para-funds", "encaminhado-para-outra-epic"}
        ]
        self.assertEqual(16, len(routes))
        self.assertTrue(all(row["destination"] for row in routes))
        self.assertFalse(
            [
                row["candidate_id"]
                for row in routes
                if "75" in row["destination"]
            ]
        )

    def test_duplicate_provenance_is_preserved(self) -> None:
        by_id = {row["candidate_id"]: row for row in self.candidates}
        self.assertGreaterEqual(
            len(by_id["accel-oxigenio"]["official_evidence_ids"]), 2
        )
        self.assertGreaterEqual(
            len(by_id["accel-kruger-labs"]["official_evidence_ids"]), 2
        )

    def test_internal_routes_were_resolved(self) -> None:
        by_id = {row["candidate_id"]: row for row in self.candidates}
        self.assertEqual(
            "elegível",
            by_id["accel-google-for-startups-brazil"]["decision"],
        )
        self.assertEqual(
            "evidência-insuficiente",
            by_id["accel-and-rockstart"]["decision"],
        )
        self.assertEqual(
            "evidência-insuficiente",
            by_id["accel-mxcac-sparklabs"]["decision"],
        )

    def test_all_references_exist(self) -> None:
        source_ids = {row["source_id"] for row in self.sources}
        evidence_ids = {row["evidence_id"] for row in self.evidence}
        for candidate in self.candidates:
            self.assertLessEqual(
                set(candidate["discovery_source_ids"]), source_ids
            )
            self.assertLessEqual(
                set(candidate["official_evidence_ids"]), evidence_ids
            )

    def test_manifest_reconciles(self) -> None:
        self.assertEqual(80, self.manifest["input_occurrences"])
        self.assertEqual(78, self.manifest["canonical_candidates"])
        self.assertEqual(
            78, sum(self.manifest["decision_counts"].values())
        )

    def test_generator_has_no_drift(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_registry.py"), "--check"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
