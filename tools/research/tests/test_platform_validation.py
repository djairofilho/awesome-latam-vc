from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


RESEARCH_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RESEARCH_DIR))

from platform_validation import validate_epic_64  # noqa: E402


class Epic64ArtifactTests(unittest.TestCase):
    def test_repository_contract_validates_in_central_flow(self) -> None:
        self.assertEqual([], validate_epic_64(REPOSITORY_ROOT))

    def test_central_flow_reports_invalid_contract_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = REPOSITORY_ROOT / "research" / "epic-64"
            epic = root / "research" / "epic-64"
            shutil.copytree(source, epic)
            inventory_path = epic / "examples" / "source-inventory.jsonl"
            inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
            inventory["cache_key"] = None
            inventory_path.write_text(
                json.dumps(inventory, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            errors = validate_epic_64(root)

        self.assertTrue(any("cache_key" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
