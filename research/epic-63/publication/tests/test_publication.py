from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPIC_ROOT = ROOT.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
CONSOLIDATION = EPIC_ROOT / "consolidation"
NETWORK_ROOT = REPOSITORY_ROOT / "ecosystem" / "angel-networks"
PAD = "ang-hub-udep-pe--pad"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_angel_publication", ROOT / "build_publication.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AngelPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
        cls.evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
        cls.queue = read_jsonl(CONSOLIDATION / "publication-queue.jsonl")
        cls.batches = read_jsonl(ROOT / "batches.jsonl")
        cls.manifest = json.loads(
            (ROOT / "publication-manifest.json").read_text(encoding="utf-8")
        )
        cls.candidate_by_id = {
            item["network_id"]: item for item in cls.candidates
        }

    def test_source_queue_is_frozen_reviewed_and_without_open_high_divergence(self):
        self.assertEqual("frozen", self.manifest["source_queue_status"])
        self.assertEqual("complete", self.manifest["source_independent_review_status"])
        self.assertEqual(0, self.manifest["source_unresolved_high_divergences"])

    def test_exact_pending_and_preserved_counts(self):
        self.assertEqual(11, self.manifest["eligible_count"])
        self.assertEqual(6, self.manifest["newly_published_count"])
        self.assertEqual(5, self.manifest["preserved_count"])
        self.assertEqual(
            {"already-published": 5, "pending-publication": 6},
            {
                status: sum(item["publication_status"] == status for item in self.queue)
                for status in {"already-published", "pending-publication"}
            },
        )

    def test_batch_count_size_order_and_exact_pending_coverage(self):
        pending = {
            item["network_id"]
            for item in self.queue
            if item["publication_status"] == "pending-publication"
        }
        self.assertEqual(math.ceil(len(pending) / 10), len(self.batches))
        published = []
        for batch in self.batches:
            self.assertGreater(len(batch["profiles"]), 0)
            self.assertLessEqual(len(batch["profiles"]), 10)
            ids = [item["network_id"] for item in batch["profiles"]]
            self.assertEqual(sorted(ids), ids)
            published.extend(ids)
        self.assertEqual(pending, set(published))
        self.assertEqual(len(published), len(set(published)))

    def test_batch_has_linked_sub_issue_owner_branch_and_valid_hash(self):
        batch = self.batches[0]
        self.assertEqual(159, batch["sub_issue"])
        self.assertEqual("agent/issue-87-angels-publication", batch["branch"])
        self.assertEqual("issue-87-publisher", batch["owner"])
        core = {
            key: batch[key]
            for key in ("batch_id", "branch", "owner", "profiles")
        }
        payload = json.dumps(
            core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), batch["batch_hash"])
        self.assertEqual(
            "cdb068e4ba3c2769da4c65b8653dfb73ae2f0d6332ed56867283f28ac119b174",
            batch["batch_hash"],
        )

    def test_pad_is_not_published_or_indexed(self):
        self.assertEqual([PAD], self.manifest["excluded_network_ids"])
        published = {
            item["network_id"]
            for batch in self.batches
            for item in batch["profiles"]
        }
        self.assertNotIn(PAD, published)
        for path in NETWORK_ROOT.glob("README*.md"):
            self.assertNotIn(PAD, path.read_text(encoding="utf-8"))
            self.assertNotIn("PAD — Red de Inversionistas Ángeles", path.read_text(encoding="utf-8"))

    def test_only_six_new_profiles_are_materialized(self):
        expected_new = {
            REPOSITORY_ROOT / item["profile_path"]
            for batch in self.batches
            for item in batch["profiles"]
        }
        actual = {
            path
            for path in NETWORK_ROOT.rglob("*.md")
            if not path.name.startswith("README")
        }
        preserved = {
            REPOSITORY_ROOT / item["canonical_profile"]
            for item in self.queue
            if item["publication_status"] == "already-published"
        }
        self.assertEqual(expected_new | preserved, actual)
        self.assertEqual(6, len(expected_new))
        self.assertEqual(5, len(preserved))

    def test_profiles_preserve_frozen_identity_actors_routes_and_sources(self):
        evidence = {item["evidence_id"]: item for item in self.evidence}
        for publication in self.batches[0]["profiles"]:
            candidate = self.candidate_by_id[publication["network_id"]]
            text = (
                REPOSITORY_ROOT / publication["profile_path"]
            ).read_text(encoding="utf-8")
            for value in (
                candidate["network_id"],
                candidate["name"],
                candidate["official_site"],
                candidate["application_route"],
                candidate["activity_evidence_date"],
            ):
                self.assertIn(value, text)
            for actor_field in (
                "selection_actors",
                "decision_actors",
                "capital_actors",
            ):
                for actor in candidate[actor_field]:
                    self.assertIn(actor["name"], text)
            for evidence_id in candidate["official_evidence_ids"]:
                self.assertIn(evidence[evidence_id]["url"], text)

    def test_indexes_cover_all_eleven_once_and_links_exist(self):
        expected = {item["canonical_profile"] for item in self.queue}
        for filename in ("README.md", "README.pt.md", "README.es.md"):
            path = NETWORK_ROOT / filename
            links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", path.read_text(encoding="utf-8"))
            resolved = {
                (path.parent / link).resolve().relative_to(REPOSITORY_ROOT).as_posix()
                for link in links
            }
            self.assertEqual(expected, resolved)
            self.assertEqual(len(expected), len(links))
            self.assertTrue(all((path.parent / link).is_file() for link in links))

    def test_localized_root_indexes_point_to_localized_network_indexes(self):
        self.assertIn(
            "ecosystem/angel-networks/README.pt.md",
            (REPOSITORY_ROOT / "README.pt.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "ecosystem/angel-networks/README.es.md",
            (REPOSITORY_ROOT / "README.es.md").read_text(encoding="utf-8"),
        )

    def test_manifest_hashes_match_profiles_indexes_sources_and_batch(self):
        for group in (
            "profile_hashes",
            "preserved_profile_hashes",
            "index_hashes",
        ):
            for relative, expected in self.manifest[group].items():
                self.assertEqual(
                    expected,
                    hashlib.sha256((REPOSITORY_ROOT / relative).read_bytes()).hexdigest(),
                    relative,
                )
        self.assertEqual(
            self.manifest["batch_artifact_hash"],
            hashlib.sha256((ROOT / "batches.jsonl").read_bytes()).hexdigest(),
        )
        for name, expected in self.manifest["source_hashes"].items():
            payload = (CONSOLIDATION / name).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(expected, hashlib.sha256(payload).hexdigest(), name)

    def test_generator_is_idempotent_and_has_no_drift(self):
        before = self.builder.build_outputs()
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_publication.py"), "--check"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, self.builder.build_outputs())

    def test_utf8_has_no_mojibake(self):
        bad = ("\u00c3", "\u00c2", "\ufffd", chr(94) + "G")
        paths = [
            *ROOT.rglob("*"),
            *NETWORK_ROOT.rglob("*.md"),
            REPOSITORY_ROOT / "README.pt.md",
            REPOSITORY_ROOT / "README.es.md",
        ]
        for path in paths:
            if path.is_file() and path.suffix in {".json", ".jsonl", ".md", ".py"}:
                text = path.read_text(encoding="utf-8")
                self.assertFalse(any(token in text for token in bad), str(path))


if __name__ == "__main__":
    unittest.main()
