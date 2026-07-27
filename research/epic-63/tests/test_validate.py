from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable


EPIC_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "epic_63_validate", EPIC_ROOT / "validate.py"
)
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATE
SPEC.loader.exec_module(VALIDATE)


def rewrite_record(
    path: Path,
    index: int,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    records = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    mutate(records[index])
    path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


class ContractValidationTests(unittest.TestCase):
    def validate_copy(
        self,
        source: str = "examples",
        mutate: Callable[[Path], None] | None = None,
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / source
            shutil.copytree(EPIC_ROOT / source, target)
            if mutate:
                mutate(target)
            return VALIDATE.validate_directory(target)

    def test_complete_example_is_valid(self) -> None:
        self.assertEqual([], self.validate_copy())

    def test_templates_are_valid(self) -> None:
        self.assertEqual([], self.validate_copy("templates"))

    def test_pending_candidate_requires_owner_and_next_action(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                0,
                lambda item: item.update(owner=None, next_action=None),
            )

        errors = self.validate_copy("templates", mutate)
        self.assertTrue(any("owner" in error for error in errors))
        self.assertTrue(any("next_action" in error for error in errors))

    def test_eligible_requires_official_activity_claim(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "evidence.jsonl",
                1,
                lambda item: item.update(source_type="terceiro"),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(
            any("evidência oficial confirmada de atividade" in error for error in errors)
        )

    def test_activity_must_be_within_24_months(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                0,
                lambda item: item.update(activity_evidence_date="2024-07-26"),
            )
            rewrite_record(
                directory / "evidence.jsonl",
                1,
                lambda item: item.update(published_on="2024-07-26"),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("janela de 24 meses" in error for error in errors))

    def test_decided_chapter_alias_must_be_duplicate(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                1,
                lambda item: item.update(
                    decision="excluído",
                    reason="Classificação propositalmente inválida.",
                ),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(
            any("capítulo alias decidido deve ser duplicado" in error for error in errors)
        )

    def test_standalone_chapter_requires_all_autonomies(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                1,
                lambda item: item.update(
                    chapter_identity="standalone",
                    canonical_network_id=None,
                    chapter_autonomy={
                        "selection": True,
                        "decision": True,
                        "geography": True,
                        "recent_activity": False,
                    },
                ),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("recent_activity" in error for error in errors))

    def test_selection_decision_and_capital_are_required_separately(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                0,
                lambda item: item.pop("capital_actors"),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("capital_actors" in error for error in errors))

    def test_references_cannot_be_orphaned(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "candidates.jsonl",
                0,
                lambda item: item.update(
                    discovery_source_ids=["src-inexistente"]
                ),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("discovery_source_id inexistente" in error for error in errors))

    def test_manifest_task_count_must_match(self) -> None:
        def mutate(directory: Path) -> None:
            rewrite_record(
                directory / "run-manifest.jsonl",
                0,
                lambda item: item.update(task_count=2),
            )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("task_count não coincide" in error for error in errors))

    def test_coverage_cell_is_unique(self) -> None:
        def mutate(directory: Path) -> None:
            path = directory / "coverage-matrix.jsonl"
            first = json.loads(path.read_text(encoding="utf-8"))
            first["coverage_id"] = "cov-example-duplicate"
            with path.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(first, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )

        errors = self.validate_copy(mutate=mutate)
        self.assertTrue(any("célula duplicada" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
