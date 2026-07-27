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

    def test_month_subtraction_handles_leap_day(self) -> None:
        from datetime import date

        self.assertEqual(date(2022, 2, 28), subtract_months(date(2024, 2, 29), 24))

    class modified_example:
        def __init__(self, filename, mutate):
            self.filename = filename
            self.mutate = mutate
            self.temporary = tempfile.TemporaryDirectory()

        def __enter__(self):
            target = Path(self.temporary.name)
            for filename in FILE_CONTRACTS:
                rows = load_jsonl(EPIC_DIR / "examples" / filename)
                clean_rows = [
                    {key: value for key, value in row.items() if key != "_line_number"}
                    for row in copy.deepcopy(rows)
                ]
                if filename == self.filename:
                    self.mutate(clean_rows[0])
                content = "".join(
                    json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                    for row in clean_rows
                )
                (target / filename).write_text(content, encoding="utf-8")
            return target

        def __exit__(self, *_):
            self.temporary.cleanup()


if __name__ == "__main__":
    unittest.main()
