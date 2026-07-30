"""Regression tests for the aggregate issue #223 publication report."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "brazil" / "publication" / "build_report.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "epic_207_publication_report_test",
        BUILDER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar build_report.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.report = cls.builder.build_report()

    def test_report_is_byte_deterministic_and_complete(self) -> None:
        self.assertEqual(
            self.builder.json_bytes(self.report),
            self.builder.json_bytes(self.builder.build_report()),
        )
        self.assertEqual(3, self.report["batch_count"])
        self.assertEqual(27, self.report["candidate_count"])
        self.assertEqual(27, self.report["destination_count"])
        self.assertEqual(81, self.report["profile_file_count"])
        self.assertTrue(all(self.report["integrity"].values()))

    def test_report_matches_the_frozen_candidates_exactly(self) -> None:
        freeze = json.loads(
            self.builder.FREEZE_PATH.read_text(encoding="utf-8")
        )
        frozen = [
            item
            for batch in freeze["publication"]["batches"]
            for item in batch["candidates"]
        ]
        self.assertEqual(
            [item["candidate_id"] for item in frozen],
            self.report["candidate_ids"],
        )
        self.assertEqual(
            [item["destination"] for item in frozen],
            self.report["destinations"],
        )

    def test_batch_and_profile_hashes_match_current_bytes(self) -> None:
        for batch in self.report["batches"]:
            manifest = self.builder.REPOSITORY / batch["manifest_path"]
            self.assertEqual(
                batch["manifest_sha256"],
                self.builder.sha256(manifest.read_bytes()),
            )
        for profile in self.report["profile_files"]:
            path = self.builder.REPOSITORY / profile["path"]
            self.assertEqual(
                profile["sha256"],
                self.builder.sha256(path.read_bytes()),
            )


if __name__ == "__main__":
    unittest.main()
