from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from normalize import import_baseline, name_aliases, normalize_alias, normalize_domain


class NormalizeDomainTests(unittest.TestCase):
    def test_normalizes_urls_hostnames_ports_and_idn(self) -> None:
        self.assertEqual(normalize_domain("HTTPS://WWW.Example.COM:443/path?q=1"), "example.com")
        self.assertEqual(normalize_domain("example.com."), "example.com")
        self.assertEqual(normalize_domain("https://www.açaí.com.br/"), "xn--aa-4iaz.com.br")

    def test_normalizes_aliases_with_accents(self) -> None:
        self.assertEqual(normalize_alias("Itaú Ventures"), "itau ventures")
        self.assertEqual(
            name_aliases("Actions Capital (ex-K50 Ventures)"),
            ["actions capital ex k50 ventures", "k50 ventures", "actions capital"],
        )


class BaselineImportTests(unittest.TestCase):
    def test_imports_readme_profiles_without_merging_shared_domains(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "funds").mkdir()
            (root / "README.md").write_text(
                "[Vehicle A](funds/a.md)\n[Vehicle B](funds/b.md)\n", encoding="utf-8"
            )
            for filename, name in (("a.md", "Vehicle A"), ("b.md", "Vehicle B")):
                (root / "funds" / filename).write_text(
                    f"# {name}\n\n- **Website:** https://manager.example/{filename}\n",
                    encoding="utf-8",
                )

            funds = import_baseline(root)

        self.assertEqual(len(funds), 2)
        self.assertEqual({fund.profile_path for fund in funds}, {"funds/a.md", "funds/b.md"})
        self.assertEqual({fund.domain for fund in funds}, {"manager.example"})


if __name__ == "__main__":
    unittest.main()
