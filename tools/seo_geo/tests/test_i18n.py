from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "tools" / "seo_geo" / "validate_i18n.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("seo_geo_validate_i18n", MODULE_PATH)
assert SPEC and SPEC.loader
I18N = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = I18N
SPEC.loader.exec_module(I18N)

VALID_EXAMPLES = ROOT / "research" / "seo-geo" / "contract" / "examples" / "valid"
CONFIG_PATH = ROOT / "research" / "seo-geo" / "i18n" / "locales.json"


class RouteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = I18N.load_config()

    def test_localized_routes_and_switching_preserve_suffix(self) -> None:
        self.assertEqual(
            I18N.localized_route(self.config, "pt-BR", "/catalog/500-latam/"),
            "/pt-br/catalog/500-latam/",
        )
        self.assertEqual(
            I18N.switch_locale(
                self.config,
                "/pt-br/catalog/500-latam/",
                "es",
            ),
            "/es/catalog/500-latam/",
        )

    def test_base_and_canonical_url_preserve_github_pages_subdirectory(self) -> None:
        route = I18N.localized_route(self.config, "en", "/catalog/")
        self.assertEqual(
            I18N.with_base(self.config, route),
            "/awesome-latam-vc/en/catalog/",
        )
        self.assertEqual(
            I18N.public_url(self.config, route),
            "https://djairofilho.github.io/awesome-latam-vc/en/catalog/",
        )

    def test_hreflang_omits_unavailable_locale_and_uses_safe_x_default(self) -> None:
        links = I18N.hreflang_urls(
            self.config,
            "/catalog/500-latam/",
            ["en", "pt-BR"],
        )
        self.assertEqual(set(links), {"en", "pt-BR", "x-default"})
        self.assertEqual(
            links["x-default"],
            "https://djairofilho.github.io/awesome-latam-vc/en/catalog/500-latam/",
        )
        self.assertNotIn("es", links)

    def test_home_hreflang_uses_unprefixed_language_chooser(self) -> None:
        links = I18N.hreflang_urls(self.config, "/", ["en", "pt-BR", "es"])
        self.assertEqual(
            links["x-default"],
            "https://djairofilho.github.io/awesome-latam-vc/",
        )

    def test_route_helpers_reject_unknown_locale_and_query_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported locale"):
            I18N.localized_route(self.config, "fr", "/catalog/")
        with self.assertRaisesRegex(ValueError, "query or fragment"):
            I18N.localized_route(self.config, "en", "/catalog/?q=fund")
        with self.assertRaisesRegex(ValueError, "traverse"):
            I18N.localized_route(self.config, "en", "/catalog/../private/")


class CompletenessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "research/seo-geo/i18n").mkdir(parents=True)
        shutil.copy2(CONFIG_PATH, self.root / "research/seo-geo/i18n/locales.json")
        (self.root / "funds/regional").mkdir(parents=True)
        shutil.copy2(
            VALID_EXAMPLES / "fund-500-latam.en.md",
            self.root / "funds/regional/500-latam.md",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def add_translation(self, locale: str, source_name: str) -> Path:
        target = (
            self.root
            / "translations"
            / locale
            / "funds"
            / "regional"
            / "500-latam.md"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(VALID_EXAMPLES / source_name, target)
        return target

    def validate(self, *, release: bool = False):
        return I18N.validate_i18n(root=self.root, release=release)

    def test_migration_warns_but_release_rejects_missing_translations(self) -> None:
        migration = self.validate()
        self.assertEqual(migration.errors, ())
        self.assertEqual(len(migration.warnings), 2)
        release = self.validate(release=True)
        self.assertEqual(release.warnings, ())
        self.assertEqual(len(release.errors), 2)
        self.assertIn("missing translation", "\n".join(release.errors))

    def test_complete_parallel_translations_pass_release_gate(self) -> None:
        self.add_translation("pt-BR", "fund-500-latam.pt-BR.md")
        self.add_translation("es", "fund-500-latam.es.md")
        result = self.validate(release=True)
        self.assertEqual(result.errors, ())
        self.assertEqual(result.warnings, ())
        self.assertEqual(
            result.localized_counts,
            {"en": 1, "pt-BR": 1, "es": 1},
        )

    def test_needs_review_is_warning_then_release_error(self) -> None:
        path = self.add_translation("pt-BR", "fund-500-latam.pt-BR.md")
        text = path.read_text(encoding="utf-8").replace(
            '"translation_status": "complete"',
            '"translation_status": "needs_review"',
        )
        path.write_text(text, encoding="utf-8")
        migration = self.validate()
        self.assertIn("not release-complete", "\n".join(migration.warnings))
        release = self.validate(release=True)
        self.assertIn("not release-complete", "\n".join(release.errors))

    def test_orphan_translation_is_rejected(self) -> None:
        path = self.add_translation("es", "fund-500-latam.es.md")
        text = path.read_text(encoding="utf-8").replace(
            '"entity_id": "fund:500-latam"',
            '"entity_id": "fund:orphan"',
        ).replace(
            '"id": "fund:500-latam:es"',
            '"id": "fund:orphan:es"',
        )
        path.write_text(text, encoding="utf-8")
        result = self.validate()
        self.assertIn("orphan translation", "\n".join(result.errors))

    def test_translation_path_must_mirror_canonical_path(self) -> None:
        path = self.add_translation("es", "fund-500-latam.es.md")
        moved = path.parent.parent / "wrong" / path.name
        moved.parent.mkdir(parents=True)
        path.replace(moved)
        result = self.validate()
        self.assertIn("translation path must mirror", "\n".join(result.errors))

    def test_duplicate_locale_is_rejected(self) -> None:
        first = self.add_translation("es", "fund-500-latam.es.md")
        duplicate = first.parent / "duplicate.md"
        shutil.copy2(first, duplicate)
        result = self.validate()
        self.assertIn("duplicate entity/locale", "\n".join(result.errors))

    def test_config_rejects_duplicate_route_segments(self) -> None:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config["locales"]["es"]["route_segment"] = "en"
        path = self.root / "research/seo-geo/i18n/invalid-locales.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "route segments must be unique"):
            I18N.load_config(path)


if __name__ == "__main__":
    unittest.main()
