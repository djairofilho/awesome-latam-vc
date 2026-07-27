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

from public_program_validation import validate_epic_65  # noqa: E402


class Epic65ArtifactTests(unittest.TestCase):
    def test_repository_templates_and_example_validate(self) -> None:
        self.assertEqual([], validate_epic_65(REPOSITORY_ROOT))

    def test_central_validation_rejects_stale_open_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = REPOSITORY_ROOT / "research" / "epic-65"
            epic = root / "research" / "epic-65"
            shutil.copytree(source, epic)

            program_path = epic / "examples" / "programs.jsonl"
            program = json.loads(program_path.read_text(encoding="utf-8"))
            program["activity_basis"] = "chamada aberta"
            program_path.write_text(
                json.dumps(program, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            call_path = epic / "examples" / "calls.jsonl"
            call = json.loads(call_path.read_text(encoding="utf-8"))
            call.update(
                call_status="aberta",
                opened_on="2026-06-01",
                closes_on="2026-07-01",
                captured_on="2026-07-27",
            )
            call_path.write_text(
                json.dumps(call, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            evidence_path = epic / "examples" / "evidence.jsonl"
            evidence = [
                json.loads(line)
                for line in evidence_path.read_text(encoding="utf-8").splitlines()
            ]
            status_claim = next(
                claim
                for claim in evidence[2]["claims"]
                if claim["field"] == "status da chamada"
            )
            status_claim["finding"] = "confirmado"
            evidence_path.write_text(
                "".join(
                    json.dumps(row, ensure_ascii=False) + "\n"
                    for row in evidence
                ),
                encoding="utf-8",
            )

            errors = validate_epic_65(root)

        self.assertTrue(any("após a data de fechamento" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
