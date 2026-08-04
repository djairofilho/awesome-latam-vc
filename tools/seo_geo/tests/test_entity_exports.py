from __future__ import annotations

import copy
import csv
from io import StringIO
import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
SEO_GEO_ROOT = ROOT / "tools" / "seo_geo"
if str(SEO_GEO_ROOT) not in sys.path:
    sys.path.insert(0, str(SEO_GEO_ROOT))

import generate_entities  # noqa: E402
from validate_profiles import catalog_profile_paths, parse_profile  # noqa: E402


DATA = ROOT / "data"


class EntityExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(
            (DATA / "entities.json").read_text(encoding="utf-8")
        )
        cls.csv_text = (DATA / "entities.csv").read_text(encoding="utf-8")
        cls.rows = list(csv.DictReader(StringIO(cls.csv_text, newline="")))
        cls.schema = json.loads(
            (DATA / "entities.schema.json").read_text(encoding="utf-8")
        )
        cls.profiles = [
            parse_profile(path) for path in catalog_profile_paths()
        ]

    def test_json_matches_schema_and_dataset_metadata(self):
        errors = list(
            Draft202012Validator(
                self.schema, format_checker=FormatChecker()
            ).iter_errors(self.document)
        )
        self.assertEqual([], errors)
        self.assertEqual("1.0", self.document["schema_version"])
        self.assertEqual("2026-07-27", self.document["dataset"]["version"])
        self.assertEqual("2026-07-27", self.document["dataset"]["date"])
        self.assertEqual("CC0-1.0", self.document["dataset"]["license"])
        self.assertEqual("UTF-8", self.document["dataset"]["encoding"])

    def test_all_profiles_are_exported_once_in_stable_order(self):
        entities = self.document["entities"]
        ids = [entity["id"] for entity in entities]
        profile_ids = sorted(
            profile.metadata["entity_id"] for profile in self.profiles
        )
        self.assertEqual(324, len(entities))
        self.assertEqual(profile_ids, ids)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(324, self.document["dataset"]["entity_count"])

    def test_json_and_csv_have_identical_ids_order_and_values(self):
        errors = generate_entities.validate_export_consistency(
            (DATA / "entities.json").read_bytes(),
            (DATA / "entities.csv").read_bytes(),
            self.schema,
        )
        self.assertEqual([], errors)
        self.assertEqual(
            [entity["id"] for entity in self.document["entities"]],
            [row["id"] for row in self.rows],
        )

    def test_export_preserves_front_matter_types_dates_sources_and_fields(self):
        by_id = {
            entity["id"]: entity for entity in self.document["entities"]
        }
        for profile in self.profiles:
            metadata = profile.metadata
            entity = by_id[metadata["entity_id"]]
            self.assertEqual(metadata["entity_type"], entity["entity_type"])
            self.assertEqual(metadata["name"], entity["name"])
            self.assertEqual(metadata["summary"], entity["summary"])
            self.assertEqual(metadata["base_geography"], entity["base_geography"])
            self.assertEqual(metadata["countries_covered"], entity["countries_covered"])
            self.assertEqual(metadata["stages"], entity["stages"])
            self.assertEqual(metadata["focuses"], entity["focuses"])
            self.assertEqual(metadata["official_website"], entity["official_website"])
            self.assertEqual(metadata["founder_route"], entity["founder_route"])
            self.assertEqual(metadata["sources"], entity["sources"])
            self.assertEqual(metadata["last_verified"], entity["verified_on"])

    def test_no_schema_org_or_other_entity_type_is_invented(self):
        contract_types = {
            "fund",
            "accelerator",
            "angel_network",
            "funding_platform",
            "public_program",
        }
        exported_types = {
            entity["entity_type"] for entity in self.document["entities"]
        }
        self.assertEqual(contract_types, exported_types)

    def test_null_and_array_csv_encoding_is_unambiguous(self):
        json_by_id = {
            entity["id"]: entity for entity in self.document["entities"]
        }
        for row in self.rows:
            entity = json_by_id[row["id"]]
            for field in generate_entities.NULLABLE_FIELDS:
                expected = "" if entity[field] is None else entity[field]
                self.assertEqual(expected, row[field])
            for field in generate_entities.JSON_LIST_FIELDS:
                self.assertEqual(entity[field], json.loads(row[field]))

    def test_validator_rejects_duplicate_schema_and_format_divergence(self):
        duplicate = copy.deepcopy(self.document)
        duplicate["entities"].append(copy.deepcopy(duplicate["entities"][0]))
        duplicate["dataset"]["entity_count"] += 1
        errors = generate_entities.validate_export_consistency(
            json.dumps(duplicate).encode(),
            (DATA / "entities.csv").read_bytes(),
            self.schema,
        )
        self.assertTrue(any("duplicate entity ID" in error for error in errors))

        invalid = copy.deepcopy(self.document)
        invalid["entities"][0]["entity_type"] = "venture_fund_product"
        errors = generate_entities.validate_export_consistency(
            json.dumps(invalid).encode(),
            (DATA / "entities.csv").read_bytes(),
            self.schema,
        )
        self.assertTrue(any(error.startswith("schema ") for error in errors))

        rows = list(self.rows)
        rows[0]["name"] = "Divergent name"
        output = StringIO(newline="")
        writer = csv.DictWriter(
            output,
            fieldnames=generate_entities.CSV_FIELDS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
        errors = generate_entities.validate_export_consistency(
            (DATA / "entities.json").read_bytes(),
            output.getvalue().encode(),
            self.schema,
        )
        self.assertTrue(any("CSV field differs" in error for error in errors))

    def test_encoding_line_endings_and_mojibake_are_clean(self):
        for name in ("entities.json", "entities.csv"):
            payload = (DATA / name).read_bytes()
            self.assertFalse(payload.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\r\n", payload)
            text = payload.decode("utf-8")
            self.assertFalse(any(marker in text for marker in ("Ã", "Â", "�")))

    def test_generator_is_idempotent_and_committed_exports_have_no_drift(self):
        before = generate_entities.build_outputs()
        self.assertEqual(before, generate_entities.build_outputs())
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "seo_geo" / "generate_entities.py"),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
