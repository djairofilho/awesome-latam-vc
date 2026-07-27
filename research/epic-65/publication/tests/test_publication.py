from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
VERIFIER_PATH = ROOT / "research" / "epic-65" / "publication" / "verify_publication.py"
SPEC = importlib.util.spec_from_file_location("issue103_verify_publication", VERIFIER_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Não foi possível carregar {VERIFIER_PATH}")
verify_publication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_publication)


class PublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for relative in (
            Path("research/epic-65/publication"),
            Path("research/epic-65/consolidation"),
            Path("ecosystem/public-programs"),
        ):
            shutil.copytree(ROOT / relative, self.root / relative)
        for filename in ("README.md", "README.es.md", "README.pt.md"):
            shutil.copy2(ROOT / filename, self.root / filename)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_complete_publication_passes(self) -> None:
        self.assertEqual([], verify_publication.validate(self.root))

    def test_missing_profile_fails_exact_coverage(self) -> None:
        path = self.root / "ecosystem/public-programs/uruguay/ande.md"
        path.unlink()
        errors = verify_publication.validate(self.root)
        self.assertTrue(any("catálogo fora da fila congelada" in error for error in errors))

    def test_extra_profile_fails_frozen_queue(self) -> None:
        path = self.root / "ecosystem/public-programs/brazil/outside-queue.md"
        path.write_text("# Outside queue\n", encoding="utf-8")
        errors = verify_publication.validate(self.root)
        self.assertTrue(any("catálogo fora da fila congelada" in error for error in errors))

    def test_duplicate_batch_path_fails(self) -> None:
        path = self.root / "research/epic-65/publication/publication-plan.json"
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["batches"][0]["profiles"][1]["path"] = plan["batches"][0]["profiles"][0]["path"]
        path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_publication.validate(self.root)
        self.assertIn("há caminho duplicado nos lotes", errors)

    def test_orphan_agency_relation_fails(self) -> None:
        path = (
            self.root
            / "ecosystem/public-programs/ecuador/conquito-fonquito.md"
        )
        text = path.read_text(encoding="utf-8").replace(
            "`agency-conquito`",
            "`agency-missing`",
        )
        path.write_text(text, encoding="utf-8")
        errors = verify_publication.validate(self.root)
        self.assertIn(
            "program-conquito-fonquito: relação com agência órfã",
            errors,
        )

    def test_tampered_source_hash_fails(self) -> None:
        path = self.root / "research/epic-65/publication/publication-plan.json"
        plan = json.loads(path.read_text(encoding="utf-8"))
        plan["source_hashes"]["programs.jsonl"] = "0" * 64
        path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_publication.validate(self.root)
        self.assertIn("hash de entrada inválido: programs.jsonl", errors)


if __name__ == "__main__":
    unittest.main()
