from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "tools" / "seo_geo" / "validate_editorial.py"
SPEC = importlib.util.spec_from_file_location("seo_geo_validate_editorial", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATE
SPEC.loader.exec_module(VALIDATE)

EDITORIAL_ROOT = VALIDATE.EDITORIAL_ROOT
EDITORIAL_SCHEMA_PATH = VALIDATE.EDITORIAL_SCHEMA_PATH
REQUIRED_EDITORIAL_SLUGS = VALIDATE.REQUIRED_EDITORIAL_SLUGS
parse_document = VALIDATE.parse_document
read_schema = VALIDATE.read_schema
validate_contract = VALIDATE.validate_contract
validate_editorial_collection = VALIDATE.validate_editorial_collection
validate_editorial_document = VALIDATE.validate_editorial_document
validate_landing_collection = VALIDATE.validate_landing_collection


class EditorialContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = read_schema(EDITORIAL_SCHEMA_PATH)
        cls.methodology = parse_document(
            EDITORIAL_ROOT / "en" / "methodology.md"
        )

    def test_repository_editorial_contract_validates(self) -> None:
        self.assertEqual(validate_contract(), [])

    def test_all_canonical_editorial_topics_exist(self) -> None:
        slugs = {
            parse_document(path).metadata["slug"]
            for path in (EDITORIAL_ROOT / "en").glob("*.md")
        }
        self.assertEqual(slugs, REQUIRED_EDITORIAL_SLUGS)

    def test_release_gate_reports_missing_translations(self) -> None:
        errors = validate_editorial_collection(require_complete_locales=True)
        self.assertEqual(
            sum(error.startswith("missing release page:") for error in errors),
            len(REQUIRED_EDITORIAL_SLUGS) * 2,
        )

    def test_rejects_synthetic_faq_and_unrendered_reference(self) -> None:
        metadata = {
            **self.methodology.metadata,
            "references": [
                {
                    "title": "Missing evidence",
                    "url": "https://example.com/evidence",
                }
            ],
        }
        document = replace(
            self.methodology,
            metadata=metadata,
            body=self.methodology.body + "\n## FAQ\n\nArtificial question.\n",
        )
        errors = validate_editorial_document(document, self.schema)
        self.assertTrue(any("synthetic FAQ" in error for error in errors))
        self.assertTrue(any("reference is not rendered" in error for error in errors))

    def test_rejects_duplicate_landing_introductions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            locale_root = root / "en"
            locale_root.mkdir()
            for subject_id in ("brazil", "mexico"):
                metadata = {
                    "schema_version": "1.0",
                    "id": f"landing:country:{subject_id}:en",
                    "subject_type": "country",
                    "subject_id": subject_id,
                    "locale": "en",
                    "title": subject_id.title(),
                    "summary": f"Catalog entries associated with {subject_id.title()}.",
                    "last_reviewed": "2026-07-27",
                }
                content = (
                    "---\n"
                    + json.dumps(metadata, indent=2)
                    + "\n---\n"
                    + f"# {subject_id.title()}\n\n"
                    + "This repeated introduction adds no subject-specific value.\n"
                )
                (locale_root / f"{subject_id}.md").write_text(
                    content, encoding="utf-8", newline="\n"
                )
            errors = validate_landing_collection(root)
            self.assertTrue(
                any("duplicate landing introduction" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
