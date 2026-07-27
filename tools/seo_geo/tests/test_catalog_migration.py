import tempfile
import unittest
from pathlib import Path
import sys

TOOLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_ROOT))

import migrate_catalog
from validate_profiles import (
    Profile,
    catalog_profile_paths,
    read_contract,
    validate_collection,
)


class CatalogMigrationTests(unittest.TestCase):
    def test_every_current_profile_maps_to_valid_canonical_metadata(self):
        schema, enums = read_contract()
        profiles = []
        paths = catalog_profile_paths()

        self.assertGreater(len(paths), 0)
        for path in paths:
            body = migrate_catalog.split_document(path)
            metadata, _notes = migrate_catalog.build_metadata(path, body)
            profiles.append(Profile(path=path, metadata=metadata, body=body))

        errors = validate_collection(
            profiles,
            schema,
            enums,
            catalog_correspondence=True,
        )
        self.assertEqual(errors, [])
        self.assertEqual(len({profile.metadata["id"] for profile in profiles}), len(paths))
        self.assertEqual(
            len({profile.metadata["slug"] for profile in profiles}),
            len(paths),
        )

    def test_profile_serialization_preserves_body_bytes_after_lf_normalization(self):
        path = catalog_profile_paths()[0]
        body = migrate_catalog.split_document(path)
        metadata, _notes = migrate_catalog.build_metadata(path, body)
        payload = migrate_catalog.profile_bytes(metadata, body)

        with tempfile.TemporaryDirectory() as directory:
            temporary_profile = Path(directory) / "profile.md"
            temporary_profile.write_bytes(payload)
            serialized_body = migrate_catalog.split_document(temporary_profile)

        self.assertEqual(
            serialized_body.encode("utf-8"),
            migrate_catalog.normalize_lf(body).encode("utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
