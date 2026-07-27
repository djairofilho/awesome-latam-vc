from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
TOOLS_ROOT = REPOSITORY_ROOT / "tools" / "seo_geo"
MIGRATION_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "migration"
sys.path.insert(0, str(TOOLS_ROOT))

import migrate_catalog
import validate_profiles


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CatalogMigrationVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = validate_profiles.catalog_profile_paths()
        cls.relative_paths = {
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path in cls.paths
        }
        cls.inventory = read_jsonl(MIGRATION_ROOT / "inventory.jsonl")
        cls.mapping = read_jsonl(MIGRATION_ROOT / "mapping.jsonl")
        cls.manifest = json.loads(
            (MIGRATION_ROOT / "migration-manifest.json").read_text(
                encoding="utf-8"
            )
        )

    def test_catalog_has_complete_unique_canonical_coverage(self) -> None:
        errors = validate_profiles.validate_paths(
            self.paths,
            catalog_correspondence=True,
        )
        profiles = [validate_profiles.parse_profile(path) for path in self.paths]

        self.assertEqual(errors, [])
        self.assertEqual(
            {row["path"] for row in self.inventory},
            self.relative_paths,
        )
        self.assertEqual(
            {row["path"] for row in self.mapping},
            self.relative_paths,
        )
        self.assertEqual(
            set(self.manifest["profile_hashes"]),
            self.relative_paths,
        )
        self.assertEqual(
            len({profile.metadata["id"] for profile in profiles}),
            len(self.paths),
        )
        self.assertEqual(
            len({profile.metadata["slug"] for profile in profiles}),
            len(self.paths),
        )
        self.assertTrue(
            all(profile.metadata["locale"] == "en" for profile in profiles)
        )
        self.assertTrue(
            all(profile.metadata["translation_of"] is None for profile in profiles)
        )

    def test_body_sources_and_dates_match_frozen_inventory(self) -> None:
        inventory_by_path = {row["path"]: row for row in self.inventory}

        for path in self.paths:
            relative = path.relative_to(REPOSITORY_ROOT).as_posix()
            profile = validate_profiles.parse_profile(path)
            body_hash = hashlib.sha256(
                migrate_catalog.normalize_lf(profile.body).encode("utf-8")
            ).hexdigest()
            row = inventory_by_path[relative]
            self.assertEqual(row["body_sha256_before"], body_hash)
            self.assertEqual(row["body_sha256_after"], body_hash)
            self.assertEqual(row["source_count"], len(profile.metadata["sources"]))
            self.assertEqual(
                row["last_verified"],
                profile.metadata["last_verified"],
            )

    def test_manifest_hashes_match_profiles_contract_and_artifacts(self) -> None:
        self.assertEqual(self.manifest["profile_count"], len(self.paths))
        self.assertEqual(self.manifest["unique_ids"], len(self.paths))
        self.assertEqual(self.manifest["unique_slugs"], len(self.paths))
        self.assertEqual(self.manifest["body_hash_mismatches"], 0)

        for relative, expected in self.manifest["profile_hashes"].items():
            self.assertEqual(digest(REPOSITORY_ROOT / relative), expected)
        for relative, expected in self.manifest["contract_hashes"].items():
            payload = (REPOSITORY_ROOT / relative).read_bytes().replace(
                b"\r\n",
                b"\n",
            )
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)
        for relative, expected in self.manifest["artifact_hashes"].items():
            self.assertEqual(digest(MIGRATION_ROOT / relative), expected)

    def test_generator_is_deterministic(self) -> None:
        expected_outputs = migrate_catalog.build_outputs()
        drift = [
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path, expected in expected_outputs.items()
            if path.read_bytes() != expected
        ]
        self.assertEqual(drift, [])


if __name__ == "__main__":
    unittest.main()
