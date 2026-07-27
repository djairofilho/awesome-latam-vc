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

from accelerator_validation import (  # noqa: E402
    accelerator_profile_paths,
    is_accelerator_profile_path,
    validate_accelerator_profile,
    validate_accelerator_index,
    validate_epic_62,
)


class Epic62ArtifactTests(unittest.TestCase):
    def _copy_epic(self, root: Path) -> Path:
        epic = root / "research" / "epic-62"
        source = REPOSITORY_ROOT / "research" / "epic-62"
        shutil.copytree(source, epic)
        return epic

    def test_repository_templates_and_example_validate(self) -> None:
        self.assertEqual([], validate_epic_62(REPOSITORY_ROOT))

    def test_rejects_eligible_candidate_without_required_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epic = root / "research" / "epic-62"
            source = REPOSITORY_ROOT / "research" / "epic-62"
            shutil.copytree(source / "schemas", epic / "schemas")
            shutil.copytree(source / "examples", epic / "examples")
            candidate_path = epic / "examples" / "candidates.jsonl"
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            candidate["official_evidence_ids"] = []
            candidate_path.write_text(
                json.dumps(candidate, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

            errors = validate_epic_62(root)

        self.assertTrue(
            any("official_evidence_ids" in error for error in errors),
            errors,
        )

    def test_rejects_tampered_regional_artifact_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epic = self._copy_epic(root)
            manifest_path = epic / "brazil" / "run-manifest.jsonl"
            records = [
                json.loads(line)
                for line in manifest_path.read_text(encoding="utf-8").splitlines()
            ]
            records[0]["artifact_hashes"]["candidates.jsonl"] = "0" * 64
            manifest_path.write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False) + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )

            errors = validate_epic_62(root)

        self.assertTrue(
            any("hash divergente para candidates.jsonl" in error for error in errors),
            errors,
        )

    def test_rejects_missing_field_level_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epic = self._copy_epic(root)
            evidence_path = epic / "brazil" / "evidence.jsonl"
            records = [
                json.loads(line)
                for line in evidence_path.read_text(encoding="utf-8").splitlines()
            ]
            wow = next(
                record
                for record in records
                if record["candidate_id"] == "accel-wow"
            )
            wow["claims"] = [
                claim for claim in wow["claims"] if claim["field"] != "instrument"
            ]
            evidence_path.write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False) + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )

            errors = validate_epic_62(root)

        self.assertTrue(
            any("accel-wow" in error and "instrument" in error for error in errors),
            errors,
        )

    def test_rejects_incomplete_state_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epic = self._copy_epic(root)
            coverage_path = epic / "brazil" / "state-coverage.jsonl"
            lines = coverage_path.read_text(encoding="utf-8").splitlines()
            coverage_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

            errors = validate_epic_62(root)

        self.assertTrue(
            any("cobertura estadual diverge das 27 UFs" in error for error in errors),
            errors,
        )

    def test_rejects_shared_regional_shard_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epic = self._copy_epic(root)
            manifest_path = epic / "brazil" / "run-manifest.jsonl"
            records = [
                json.loads(line)
                for line in manifest_path.read_text(encoding="utf-8").splitlines()
            ]
            records[2]["shard_path"] = records[1]["shard_path"]
            manifest_path.write_text(
                "".join(
                    json.dumps(record, ensure_ascii=False) + "\n"
                    for record in records
                ),
                encoding="utf-8",
            )

            errors = validate_epic_62(root)

        self.assertTrue(
            any("tarefas compartilham shard_path" in error for error in errors),
            errors,
        )


class AcceleratorProfileTests(unittest.TestCase):
    def test_distinguishes_profiles_from_category_readme(self) -> None:
        self.assertTrue(
            is_accelerator_profile_path(
                "ecosystem/accelerators/brazil/example.md"
            )
        )
        self.assertFalse(
            is_accelerator_profile_path("ecosystem/accelerators/README.md")
        )

    def test_accepts_complete_accelerator_profile(self) -> None:
        fields = "\n".join(
            f"- **{field}:** Value"
            for field in (
                "Website",
                "Operator",
                "Program type",
                "Open to external founders",
                "Activity status",
                "Application status",
                "Program format",
                "Duration",
                "Stage",
                "Capital offered",
                "Instrument",
                "Equity",
                "Geography",
                "Apply",
            )
        )
        text = (
            f"# Example\n\n## Program profile\n\n{fields}\n\n"
            "## Eligibility and application\n\nText.\n\n"
            "## Activity signals\n\nText.\n\n"
            "## Sources\n\n- [Official](https://example.org)\n\n"
            "**Last verified:** 2026-07-27\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.md"
            path.write_text(text, encoding="utf-8")
            errors = validate_accelerator_profile(path, "example.md")
        self.assertEqual([], errors)

    def test_reports_missing_profile_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.md"
            path.write_text("# Example\n\n## Program profile\n", encoding="utf-8")
            errors = validate_accelerator_profile(path, "example.md")
        self.assertTrue(any("Operator" in error for error in errors))
        self.assertTrue(any("Activity signals" in error for error in errors))

    def test_index_requires_every_profile_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            category = root / "ecosystem" / "accelerators"
            profile = category / "brazil" / "example.md"
            profile.parent.mkdir(parents=True)
            profile.write_text("# Example\n", encoding="utf-8")
            readme = category / "README.md"
            readme.write_text("# Accelerators\n", encoding="utf-8")

            missing_errors = validate_accelerator_index(root)
            readme.write_text(
                "# Accelerators\n\n"
                "[Example](brazil/example.md)\n"
                "[Example duplicate](brazil/example.md)\n",
                encoding="utf-8",
            )
            duplicate_errors = validate_accelerator_index(root)
            profile_paths = accelerator_profile_paths(root)

        self.assertEqual(
            {"ecosystem/accelerators/brazil/example.md"},
            profile_paths,
        )
        self.assertTrue(any("não indexados" in error for error in missing_errors))
        self.assertTrue(any("duplicado" in error for error in duplicate_errors))


if __name__ == "__main__":
    unittest.main()
