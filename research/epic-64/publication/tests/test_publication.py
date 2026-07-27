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
PLATFORM_ROOT = REPOSITORY_ROOT / "ecosystem" / "funding-platforms"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_platform_publication", ROOT / "build_publication.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
        cls.evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
        cls.batches = read_jsonl(ROOT / "batches.jsonl")
        cls.manifest = json.loads(
            (ROOT / "publication-manifest.json").read_text(encoding="utf-8")
        )
        cls.eligible = {
            row["platform_id"]: row
            for row in cls.candidates
            if row["decision"] == "eligible"
        }

    def test_source_queue_is_frozen_and_reviewed(self) -> None:
        self.assertEqual("frozen", self.manifest["source_queue_status"])
        self.assertEqual(
            "complete", self.manifest["source_independent_review_status"]
        )

    def test_batch_count_size_order_and_exact_coverage(self) -> None:
        self.assertEqual(math.ceil(len(self.eligible) / 10), len(self.batches))
        published_ids = []
        paths = []
        for batch in self.batches:
            self.assertGreater(len(batch["profiles"]), 0)
            self.assertLessEqual(len(batch["profiles"]), 10)
            ids = [row["platform_id"] for row in batch["profiles"]]
            self.assertEqual(sorted(ids), ids)
            published_ids.extend(ids)
            paths.extend(row["profile_path"] for row in batch["profiles"])
        self.assertEqual(set(self.eligible), set(published_ids))
        self.assertEqual(len(published_ids), len(set(published_ids)))
        self.assertEqual(len(paths), len(set(paths)))

    def test_batch_has_sub_issue_branch_owner_and_hash(self) -> None:
        batch = self.batches[0]
        self.assertEqual(151, batch["sub_issue"])
        self.assertEqual(
            "agent/issue-95-platforms-publication", batch["branch"]
        )
        self.assertEqual("issue-95-publisher", batch["owner"])
        core = {
            key: batch[key]
            for key in ("batch_id", "branch", "owner", "profiles")
        }
        payload = json.dumps(
            core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(hashlib.sha256(payload).hexdigest(), batch["batch_hash"])

    def test_only_eligible_candidates_are_published(self) -> None:
        published_ids = {
            row["platform_id"]
            for batch in self.batches
            for row in batch["profiles"]
        }
        noneligible = {
            row["platform_id"]
            for row in self.candidates
            if row["decision"] != "eligible"
        }
        self.assertFalse(published_ids & noneligible)
        self.assertEqual(30, self.manifest["not_published_count"])
        self.assertEqual(
            {
                "excluded": 4,
                "inactive": 2,
                "insufficient_evidence": 18,
                "other_category": 6,
            },
            self.manifest["not_published_decision_counts"],
        )

    def test_profile_set_contains_no_extra_or_missing_files(self) -> None:
        expected = {
            REPOSITORY_ROOT / row["profile_path"]
            for batch in self.batches
            for row in batch["profiles"]
        }
        actual = {
            path
            for path in PLATFORM_ROOT.rglob("*.md")
            if not path.name.startswith("README")
        }
        self.assertEqual(expected, actual)

    def test_profiles_preserve_frozen_identity_and_sources(self) -> None:
        evidence_by_id = {row["evidence_id"]: row for row in self.evidence}
        for batch in self.batches:
            for publication in batch["profiles"]:
                candidate = self.eligible[publication["platform_id"]]
                text = (
                    REPOSITORY_ROOT / publication["profile_path"]
                ).read_text(encoding="utf-8")
                self.assertIn(candidate["operator"]["legal_name"], text)
                self.assertIn(candidate["operator"]["operator_id"], text)
                self.assertIn(candidate["operator"]["official_url"], text)
                self.assertIn(candidate["operator"]["jurisdiction"], text)
                self.assertIn(candidate["brand"]["name"], text)
                self.assertIn(candidate["brand"]["brand_id"], text)
                self.assertIn(candidate["platform"]["name"], text)
                self.assertIn(candidate["platform_id"], text)
                self.assertIn(candidate["platform"]["official_url"], text)
                self.assertIn(candidate["platform"]["founder_route_url"], text)
                for alias in candidate["brand"]["aliases"]:
                    self.assertIn(alias, text)
                for country in candidate["platform"]["declared_countries"]:
                    self.assertIn(self.builder.COUNTRY_NAMES[country]["en"], text)
                for product in candidate["products"]:
                    self.assertIn(product["product_id"], text)
                    self.assertIn(product["name"], text)
                for record in candidate["regulatory_records"]:
                    self.assertIn(record["regulatory_id"], text)
                    self.assertIn(record["authority"], text)
                for evidence_id in candidate["official_evidence_ids"]:
                    self.assertIn(evidence_by_id[evidence_id]["url"], text)

    def test_index_links_are_complete_and_internal_links_exist(self) -> None:
        expected_paths = {
            row["profile_path"]
            for batch in self.batches
            for row in batch["profiles"]
        }
        for filename in ("README.md", "README.pt.md", "README.es.md"):
            path = PLATFORM_ROOT / filename
            text = path.read_text(encoding="utf-8")
            links = re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text)
            resolved = {
                (path.parent / link).resolve().relative_to(REPOSITORY_ROOT).as_posix()
                for link in links
            }
            self.assertEqual(expected_paths, resolved)
            self.assertTrue(all((path.parent / link).is_file() for link in links))
        self.assertIn(
            "ecosystem/funding-platforms/README.pt.md",
            (REPOSITORY_ROOT / "README.pt.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "ecosystem/funding-platforms/README.es.md",
            (REPOSITORY_ROOT / "README.es.md").read_text(encoding="utf-8"),
        )

    def test_manifest_hashes_match_all_publication_outputs(self) -> None:
        for group in ("profile_hashes", "index_hashes"):
            for relative, expected in self.manifest[group].items():
                actual = hashlib.sha256(
                    (REPOSITORY_ROOT / relative).read_bytes()
                ).hexdigest()
                self.assertEqual(expected, actual, relative)
        self.assertEqual(
            self.manifest["batch_artifact_hash"],
            hashlib.sha256((ROOT / "batches.jsonl").read_bytes()).hexdigest(),
        )

    def test_generator_has_no_drift(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "build_publication.py"), "--check"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
