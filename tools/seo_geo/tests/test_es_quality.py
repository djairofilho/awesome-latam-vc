from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "translations" / "es" / "validate_quality.py"
SPEC = importlib.util.spec_from_file_location("validate_es_quality", MODULE_PATH)
QUALITY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(QUALITY)


class SpanishQualityGateTests(unittest.TestCase):
    def profile(self, body: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "profile.md"
        metadata = {
            "locale": "es",
            "sources": [
                {
                    "title": "Official source",
                    "url": "https://example.com/source",
                }
            ],
            "protected_terms": ["Marca Oficial"],
        }
        path.write_text(
            "---\n"
            + json.dumps(metadata, ensure_ascii=False)
            + "\n---\n"
            + body,
            encoding="utf-8",
        )
        return path

    def test_accepts_natural_spanish_and_protected_source_title(self) -> None:
        path = self.profile(
            "# Marca Oficial\n\n"
            "La entidad invierte en startups tecnológicas.\n\n"
            "- [Official source](https://example.com/source)\n"
        )
        self.assertEqual([], QUALITY.validate(path))

    def test_rejects_placeholders_portuguese_and_known_calques(self) -> None:
        path = self.profile(
            "# Perfil\n\n"
            "ZXQMASK00001QXZ também aparece en una revisión congelada.\n"
        )
        findings = QUALITY.validate(path)
        self.assertIn("contains a translation placeholder", findings)
        self.assertIn("contains an unequivocal Portuguese fragment", findings)
        self.assertIn(
            "contains known calque: revisión congelada",
            findings,
        )

    def test_rejects_untranslated_english_prose(self) -> None:
        path = self.profile("# Perfil\n\nLa duración es de 8 weeks.\n")
        self.assertIn(
            "contains an unequivocal English fragment",
            QUALITY.validate(path),
        )

    def test_rejects_question_mark_encoding_damage(self) -> None:
        path = self.profile("# Perfil\n\nNo divulgado p?blicamente.\n")
        self.assertIn("contains mojibake", QUALITY.validate(path))


if __name__ == "__main__":
    unittest.main()
