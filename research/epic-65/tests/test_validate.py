from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

import sys

EPIC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EPIC_DIR))

from validate import FILE_CONTRACTS, load_jsonl, subtract_months, validate_bundle  # noqa: E402


class ContractValidationTests(unittest.TestCase):
    def test_templates_and_example_validate(self) -> None:
        self.assertEqual([], validate_bundle(EPIC_DIR / "templates"))
        self.assertEqual([], validate_bundle(EPIC_DIR / "examples"))

    def test_contract_does_not_require_direct_investment(self) -> None:
        programs = load_jsonl(EPIC_DIR / "examples" / "programs.jsonl")
        self.assertNotIn("direct_investment", programs[0])
        self.assertEqual([], validate_bundle(EPIC_DIR / "examples"))

    def test_temporary_call_cannot_become_profile(self) -> None:
        with self.modified_example(
            "calls.jsonl",
            lambda row: row.update(
                profile_eligible=True,
                canonical_profile="ecosystem/public-programs/chile/call.md",
            ),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("profile_eligible" in error for error in errors))
        self.assertTrue(any("canonical_profile" in error for error in errors))

    def test_eligible_program_requires_financial_benefit(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(financial_benefit=False),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("financial_benefit" in error for error in errors))

    def test_orphan_program_is_rejected(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(agency_id="agency-inexistente"),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("agência inexistente" in error for error in errors))

    def test_signal_must_be_within_twenty_four_months(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(latest_official_signal_on="2024-07-26"),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("24 meses" in error for error in errors))

    def test_eligible_agency_requires_eligible_program(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(
                research_status="decidido",
                decision="excluído",
                reason="Exclusão criada pelo teste.",
            ),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("sem programa elegível" in error for error in errors))

    def test_open_call_activity_requires_open_linked_call(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(activity_basis="chamada aberta"),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("sem call_id aberta" in error for error in errors))

    def test_open_call_captured_after_close_cannot_prove_activity(self) -> None:
        def change_programs(rows):
            rows[0]["activity_basis"] = "chamada aberta"

        def change_calls(rows):
            rows[0].update(
                call_status="aberta",
                opened_on="2026-06-01",
                closes_on="2026-07-01",
                captured_on="2026-07-27",
            )

        def change_evidence(rows):
            status_claim = next(
                claim
                for claim in rows[2]["claims"]
                if claim["field"] == "status da chamada"
            )
            status_claim["finding"] = "confirmado"

        with self.modified_bundle(
            {
                "programs.jsonl": change_programs,
                "calls.jsonl": change_calls,
                "evidence.jsonl": change_evidence,
            }
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("temporalmente válida" in error for error in errors))
        self.assertTrue(any("após a data de fechamento" in error for error in errors))

    def test_distinct_workers_cannot_share_shard_path(self) -> None:
        def share_shard(rows):
            rows[0]["task_count"] = 2
            duplicate = copy.deepcopy(rows[1])
            duplicate["task_id"] = "task-example-chile-corfo-2"
            duplicate["worker_id"] = "worker-example-chile-2"
            rows.append(duplicate)

        with self.modified_bundle({"run-manifest.jsonl": share_shard}) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("shard_path duplicado" in error for error in errors))
        self.assertTrue(any("workers distintos" in error for error in errors))

    def test_month_subtraction_handles_leap_day(self) -> None:
        from datetime import date

        self.assertEqual(date(2022, 2, 28), subtract_months(date(2024, 2, 29), 24))

    class modified_bundle:
        def __init__(self, mutators):
            self.mutators = mutators
            self.temporary = tempfile.TemporaryDirectory()

        def __enter__(self):
            target = Path(self.temporary.name)
            for filename in FILE_CONTRACTS:
                rows = load_jsonl(EPIC_DIR / "examples" / filename)
                clean_rows = [
                    {key: value for key, value in row.items() if key != "_line_number"}
                    for row in copy.deepcopy(rows)
                ]
                if filename in self.mutators:
                    self.mutators[filename](clean_rows)
                content = "".join(
                    json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                    for row in clean_rows
                )
                (target / filename).write_text(content, encoding="utf-8")
            return target

        def __exit__(self, *_):
            self.temporary.cleanup()

    class modified_example(modified_bundle):
        def __init__(self, filename, mutate):
            super().__init__({filename: lambda rows: mutate(rows[0])})


if __name__ == "__main__":
    unittest.main()
