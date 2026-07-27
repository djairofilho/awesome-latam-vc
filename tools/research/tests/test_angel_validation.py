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

from angel_validation import validate_epic_63  # noqa: E402


class Epic63GateTests(unittest.TestCase):
    def test_repository_templates_and_examples_validate(self) -> None:
        self.assertEqual([], validate_epic_63(REPOSITORY_ROOT))

    def test_gate_rejects_invalid_epic_63_example(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = REPOSITORY_ROOT / "research" / "epic-63"
            epic = root / "research" / "epic-63"
            shutil.copytree(source, epic)
            path = epic / "examples" / "candidates.jsonl"
            records = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ]
            records[0]["discovered_on"] = "2027-07-27"
            path.write_text(
                "".join(
                    json.dumps(
                        record,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )

            errors = validate_epic_63(root)

        self.assertTrue(
            any("discovered_on posterior" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
