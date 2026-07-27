from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "tools" / "seo_geo" / "validate_profiles.py"
SPEC = importlib.util.spec_from_file_location("seo_geo_validate_profiles", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATE
SPEC.loader.exec_module(VALIDATE)

CONTRACT_ROOT = ROOT / "research" / "seo-geo" / "contract"
VALID_EXAMPLES = CONTRACT_ROOT / "examples" / "valid"
INVALID_CASES = CONTRACT_ROOT / "examples" / "invalid-cases.json"


class MetadataContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema, cls.enums = VALIDATE.read_contract()
        cls.valid_profiles = [
            VALIDATE.parse_profile(path)
            for path in sorted(VALID_EXAMPLES.glob("*.md"))
        ]

    def test_valid_examples_cover_every_entity_type(self) -> None:
        self.assertEqual(
            {profile.metadata["entity_type"] for profile in self.valid_profiles},
            set(self.enums["entity_types"]),
        )
        self.assertEqual(
            VALIDATE.validate_collection(
                self.valid_profiles,
                self.schema,
                self.enums,
            ),
            [],
        )

    def test_identity_and_locale_are_independent(self) -> None:
        fund_profiles = [
            profile
            for profile in self.valid_profiles
            if profile.metadata["entity_id"] == "fund:500-latam"
        ]
        self.assertEqual({profile.metadata["locale"] for profile in fund_profiles}, {"en", "pt-BR", "es"})
        self.assertEqual({profile.metadata["entity_id"] for profile in fund_profiles}, {"fund:500-latam"})
        self.assertEqual({profile.metadata["slug"] for profile in fund_profiles}, {"500-latam"})
        self.assertEqual(len({profile.metadata["id"] for profile in fund_profiles}), 3)

    def test_translation_points_to_exactly_one_canonical(self) -> None:
        fund_profiles = [
            profile
            for profile in self.valid_profiles
            if profile.metadata["entity_id"] == "fund:500-latam"
        ]
        canonical = next(
            profile
            for profile in fund_profiles
            if profile.metadata["translation_status"] == "canonical"
        )
        translations = [
            profile
            for profile in fund_profiles
            if profile.metadata["translation_status"] != "canonical"
        ]
        self.assertTrue(
            all(
                profile.metadata["translation_of"] == canonical.metadata["id"]
                for profile in translations
            )
        )

    def test_invalid_examples_fail_for_declared_reason(self) -> None:
        cases = json.loads(INVALID_CASES.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                profiles = [
                    VALIDATE.parse_profile(CONTRACT_ROOT / "examples" / relative)
                    for relative in case["base_examples"]
                ]
                mutation = case["mutation"]
                if mutation:
                    index = mutation["profile_index"]
                    source = profiles[index]
                    metadata = copy.deepcopy(source.metadata)
                    body = source.body
                    if "metadata_field" in mutation:
                        metadata[mutation["metadata_field"]] = mutation["value"]
                    if "body_replace" in mutation:
                        replacement = mutation["body_replace"]
                        body = body.replace(replacement["from"], replacement["to"])
                    profiles[index] = VALIDATE.Profile(
                        path=source.path,
                        metadata=metadata,
                        body=body,
                    )
                errors = VALIDATE.validate_collection(
                    profiles,
                    self.schema,
                    self.enums,
                )
                self.assertTrue(errors)
                self.assertIn(case["expected_error"], "\n".join(errors))

    def test_protected_body_token_extraction(self) -> None:
        tokens = VALIDATE.protected_body_tokens(
            "Value USD 25,000 on 2026-07-27. "
            "[Source](https://example.com/a) and `entity:id`. "
            "See example.org#terms and funds/regional/example.md.\n"
            "```text\nR$ 10\n```\n"
        )
        self.assertEqual(tokens["markdown_link_destinations"]["https://example.com/a"], 1)
        self.assertEqual(tokens["currency_codes"]["USD"], 1)
        self.assertEqual(tokens["currency_symbols"]["R$"], 1)
        self.assertEqual(tokens["iso_dates"]["2026-07-27"], 1)
        self.assertEqual(tokens["inline_code"]["entity:id"], 1)
        self.assertEqual(tokens["fenced_code"]["R$ 10"], 1)
        self.assertEqual(tokens["bare_domains"]["example.org#terms"], 1)
        self.assertEqual(
            tokens["repository_paths"]["funds/regional/example.md"],
            1,
        )

    def test_translation_heading_preserves_the_proper_name(self) -> None:
        canonical = self.valid_profiles[0]
        metadata = {
            **copy.deepcopy(canonical.metadata),
            "id": f"{canonical.metadata['entity_id']}:pt-BR",
            "locale": "pt-BR",
            "translation_of": canonical.metadata["id"],
            "translation_status": "complete",
        }
        changed_heading = canonical.body.replace(
            f"# {canonical.metadata['name']}",
            "# Nome traduzido",
            1,
        )
        translated = VALIDATE.Profile(
            path=canonical.path,
            metadata=metadata,
            body=changed_heading,
        )

        errors = VALIDATE.validate_semantics(translated)
        self.assertIn("H1 must equal metadata name", "\n".join(errors))

    def test_cli_validator_accepts_valid_directory(self) -> None:
        self.assertEqual(VALIDATE.validate_paths([VALID_EXAMPLES]), [])

    def test_catalog_discovery_excludes_directory_indexes(self) -> None:
        paths = VALIDATE.catalog_profile_paths()
        self.assertTrue(paths)
        self.assertTrue(all(not path.name.startswith("README") for path in paths))
        self.assertTrue(
            all(
                "funds" in path.parts or "ecosystem" in path.parts
                for path in paths
            )
        )

    def test_null_website_requires_visible_non_disclosure(self) -> None:
        source = next(
            profile
            for profile in self.valid_profiles
            if profile.metadata["entity_type"] == "funding_platform"
        )
        metadata = copy.deepcopy(source.metadata)
        metadata["official_website"] = None
        profile = VALIDATE.Profile(
            path=source.path,
            metadata=metadata,
            body=source.body,
        )
        errors = VALIDATE.validate_catalog_correspondence(profile)
        self.assertIn("null official_website", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
