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
    def profile(self, body: str, operator: str | None = None) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "profile.md"
        metadata = {
            "locale": "es",
            "operator": operator,
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

    def test_rejects_stray_connectors_spacing_and_english_labels(self) -> None:
        path = self.profile(
            "# Perfil\n\n"
            "La fuente presenta la firma as invirtiendo at semilla.\n"
            "La firma  invierte en tecnología.\n"
            "- **Stage at entry:** Seed\n"
        )
        findings = QUALITY.validate(path)
        self.assertIn("contains a stray English connector", findings)
        self.assertIn("contains a repeated internal space", findings)
        self.assertIn(
            "contains an untranslated English heading or label",
            findings,
        )

    def test_rejects_ungrammatical_disclosure_wording(self) -> None:
        path = self.profile(
            "# Perfil\n\n- **Etapa de entrada:** No divulgado públicamente\n"
        )
        self.assertIn(
            "contains ungrammatical disclosure wording",
            QUALITY.validate(path),
        )

    def test_spacing_check_ignores_markdown_indentation_and_urls(self) -> None:
        path = self.profile(
            "# Marca Oficial\n\n"
            "  Lista con sangría válida.\n"
            "- [Official source](https://example.com/source?q=a%20%20b) — Nota.\n"
            "Consulte https://example.com/a%20%20b para más información.\n"
        )
        self.assertEqual([], QUALITY.validate(path))

    def test_accepts_protected_official_program_phrase(self) -> None:
        path = self.profile(
            "# Perfil\n\n"
            "La convocatoria PIPE Invest recibe propuestas todo el año.\n"
        )
        self.assertEqual([], QUALITY.validate(path))

    def test_accepts_protected_references_and_official_product_name(self) -> None:
        path = self.profile(
            "# Perfil\n\n"
            "Vehículo: ejemplo.com#investment-vehicle; "
            "catálogo: funds/regional/ejemplo.md.\n"
            "| Equity | Financiamiento colectivo | `prod-ejemplo-equity` |\n"
        )
        self.assertEqual([], QUALITY.validate(path))

    def test_still_rejects_unprotected_lowercase_equity(self) -> None:
        path = self.profile(
            "# Perfil\n\nLa plataforma ofrece equity crowdfunding.\n"
        )
        self.assertIn(
            "contains an unequivocal English fragment",
            QUALITY.validate(path),
        )

    def test_masks_identity_before_removing_inline_identifier(self) -> None:
        operator = "KRIA INVESTIMENTOS LTDA. (`op-kria`)"
        path = self.profile(
            f"# Perfil\n\n- **Operador:** {operator}\n",
            operator=operator,
        )
        self.assertEqual([], QUALITY.validate(path))


if __name__ == "__main__":
    unittest.main()
