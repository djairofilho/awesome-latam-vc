from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

RESEARCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RESEARCH_DIR))

from generate_indexes import synchronization_errors  # noqa: E402


def write_index(root: Path, name: str, paths: list[str]) -> None:
    rows = "\n".join(
        f"| [Fund {index}]({path}) | Seed | SaaS | Latin America |"
        for index, path in enumerate(paths)
    )
    (root / name).write_text(f"# Index\n\n## Funds\n\n{rows}\n", encoding="utf-8")


class SynchronizationTests(unittest.TestCase):
    def test_accepts_matching_path_order_with_translated_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = ["funds/a.md", "funds/b.md"]
            write_index(root, "README.md", paths)
            write_index(root, "README.pt.md", paths)
            write_index(root, "README.es.md", paths)
            self.assertEqual([], synchronization_errors(root))

    def test_reports_different_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_index(root, "README.md", ["funds/a.md", "funds/b.md"])
            write_index(root, "README.pt.md", ["funds/b.md", "funds/a.md"])
            write_index(root, "README.es.md", ["funds/a.md", "funds/b.md"])
            errors = synchronization_errors(root)
            self.assertEqual(["README.pt.md: fund order differs from README.md"], errors)


if __name__ == "__main__":
    unittest.main()
