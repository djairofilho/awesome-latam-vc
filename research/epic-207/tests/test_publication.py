"""Regression tests for auditable issue #223 publication batches."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "brazil" / "publication" / "build_batch.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "epic_207_publication_test",
        BUILDER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar build_batch.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.manifest = cls.builder.build_manifest(1)

    def test_batch_one_is_byte_deterministic(self) -> None:
        first = self.builder.json_bytes(self.manifest)
        second = self.builder.json_bytes(self.builder.build_manifest(1))
        self.assertEqual(first, second)

    def test_batch_one_matches_the_frozen_candidate_list(self) -> None:
        freeze = json.loads(
            self.builder.FREEZE_PATH.read_text(encoding="utf-8")
        )
        frozen = freeze["publication"]["batches"][0]["candidates"]
        self.assertEqual(
            [item["candidate_id"] for item in frozen],
            [item["candidate_id"] for item in self.manifest["profiles"]],
        )
        self.assertEqual(
            [item["destination"] for item in frozen],
            [item["destination"] for item in self.manifest["profiles"]],
        )
        self.assertEqual(
            self.manifest["frozen_batch_sha256"],
            "7e397d3246d7c9fe1c31dc3555dce9c9d65f653f2d985b7497eecf07badd18a4",
        )

    def test_batch_one_maps_nine_candidates_to_twenty_seven_files(self) -> None:
        self.assertEqual(self.manifest["issue"], 241)
        self.assertEqual(self.manifest["candidate_count"], 9)
        self.assertEqual(self.manifest["profile_file_count"], 27)
        self.assertTrue(all(self.manifest["integrity"].values()))
        paths = [
            localized["path"]
            for item in self.manifest["profiles"]
            for localized in item["profiles"].values()
        ]
        self.assertEqual(len(paths), len(set(paths)))

    def test_profile_hashes_match_normalized_file_bytes(self) -> None:
        for item in self.manifest["profiles"]:
            for localized in item["profiles"].values():
                path = self.builder.REPOSITORY / localized["path"]
                self.assertEqual(
                    localized["sha256"],
                    self.builder.sha256(path.read_bytes()),
                )

    def test_batch_two_matches_the_frozen_candidate_list_and_hash(self) -> None:
        manifest = self.builder.build_manifest(2)
        freeze = json.loads(
            self.builder.FREEZE_PATH.read_text(encoding="utf-8")
        )
        frozen = freeze["publication"]["batches"][1]["candidates"]

        self.assertEqual(242, manifest["issue"])
        self.assertEqual(9, manifest["candidate_count"])
        self.assertEqual(27, manifest["profile_file_count"])
        self.assertTrue(all(manifest["integrity"].values()))
        self.assertEqual(
            [item["candidate_id"] for item in frozen],
            [item["candidate_id"] for item in manifest["profiles"]],
        )
        self.assertEqual(
            [item["destination"] for item in frozen],
            [item["destination"] for item in manifest["profiles"]],
        )
        self.assertEqual(
            "b01d1a3043106144b65c1acb25094f3ecf435a556075d9fbd2b7d210469fecc4",
            manifest["frozen_batch_sha256"],
        )
        first = self.builder.json_bytes(manifest)
        second = self.builder.json_bytes(self.builder.build_manifest(2))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
