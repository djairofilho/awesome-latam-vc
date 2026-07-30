from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "tools" / "seo_geo" / "scaffold_translations.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location(
    "seo_geo_scaffold_translations",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
SCAFFOLD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCAFFOLD
SPEC.loader.exec_module(SCAFFOLD)


class TranslationScaffoldingTests(unittest.TestCase):
    def test_partition_is_sorted_and_never_exceeds_25_profiles(self) -> None:
        paths = [Path(f"profile-{number:03}.md") for number in range(52, 0, -1)]
        batches = SCAFFOLD.partition(paths)

        self.assertEqual([len(batch) for batch in batches], [25, 25, 2])
        self.assertEqual(
            [path.as_posix() for batch in batches for path in batch],
            sorted(path.as_posix() for path in paths),
        )
        with self.assertRaisesRegex(ValueError, "between 1 and 25"):
            SCAFFOLD.partition(paths, 26)

    def test_localized_profile_preserves_protected_content(self) -> None:
        canonical_path = (
            ROOT / "research/seo-geo/contract/examples/valid/fund-500-latam.en.md"
        )
        canonical = SCAFFOLD.parse_profile(canonical_path)
        localized = SCAFFOLD.localized_profile(canonical, "pt-BR")

        changed = {
            key
            for key in canonical.metadata
            if canonical.metadata[key] != localized.metadata[key]
        }
        self.assertEqual(
            changed,
            {"id", "locale", "translation_of", "translation_status"},
        )
        self.assertEqual(localized.body, canonical.body)
        self.assertEqual(localized.metadata["translation_status"], "needs_review")
        self.assertEqual(
            localized.metadata["translation_of"],
            canonical.metadata["id"],
        )

    def test_manifest_records_the_complete_cut_in_deterministic_batches(self) -> None:
        document = SCAFFOLD.manifest(
            root=ROOT,
            locale="pt-BR",
            source_commit="6c3eff32",
        )

        self.assertEqual(document["profile_count"], 247)
        self.assertEqual(len(document["batches"]), 10)
        self.assertTrue(
            all(batch["profile_count"] <= 25 for batch in document["batches"])
        )
        flattened = [
            path
            for batch in document["batches"]
            for path in batch["canonical_paths"]
        ]
        self.assertEqual(flattened, sorted(flattened))
        self.assertEqual(len(flattened), len(set(flattened)))


if __name__ == "__main__":
    unittest.main()
