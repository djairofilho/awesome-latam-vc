from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

EPIC_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("epic_65_validate", EPIC_DIR / "validate.py")
assert SPEC is not None and SPEC.loader is not None
validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate
SPEC.loader.exec_module(validate)

FILE_CONTRACTS = validate.FILE_CONTRACTS
load_jsonl = validate.load_jsonl
subtract_months = validate.subtract_months
validate_bundle = validate.validate_bundle


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

    def test_signal_must_match_observed_activity_evidence(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(latest_official_signal_on="2026-07-26"),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("observada na mesma data" in error for error in errors))

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
        self.assertTrue(any("capturada na data do sinal" in error for error in errors))
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

    def test_shard_path_rejects_traversal_segments(self) -> None:
        with self.modified_example(
            "run-manifest.jsonl",
            lambda row: row.update(
                shard_path="research/epic-65/../shards/worker-example-chile/"
            ),
            row_index=1,
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("shard_path inseguro" in error for error in errors))

    def test_duplicate_canonical_id_must_exist_and_not_point_to_self(self) -> None:
        for canonical_id, expected in (
            ("program-inexistente", "inexistente"),
            ("program-start-up-chile", "aponta para si"),
        ):
            with self.subTest(canonical_id=canonical_id):
                with self.modified_example(
                    "programs.jsonl",
                    lambda row, target=canonical_id: row.update(
                        decision="duplicado",
                        canonical_program_id=target,
                        reason="Duplicata criada pelo teste.",
                    ),
                ) as bundle:
                    errors = validate_bundle(bundle)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_duplicate_requires_canonical_id_even_with_profile(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(
                decision="duplicado",
                canonical_program_id=None,
                canonical_profile="ecosystem/public-programs/chile/start-up-chile.md",
                reason="Duplicata criada pelo teste.",
            ),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(
            any("duplicado sem canonical_program_id" in error for error in errors)
        )

    def test_duplicate_canonical_ids_cannot_form_cycles(self) -> None:
        def cycle_programs(rows):
            rows[0].update(
                decision="duplicado",
                canonical_program_id="program-cycle-peer",
                reason="Duplicata criada pelo teste.",
            )
            peer = copy.deepcopy(rows[0])
            peer.update(
                program_id="program-cycle-peer",
                canonical_program_id="program-start-up-chile",
                call_ids=[],
                official_evidence_ids=[],
            )
            rows.append(peer)

        def link_peer(rows):
            rows[0]["program_ids"].append("program-cycle-peer")

        with self.modified_bundle(
            {
                "programs.jsonl": cycle_programs,
                "agencies.jsonl": link_peer,
            }
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("ciclo em canonical_program_id" in error for error in errors))

    def test_canonical_profile_rejects_traversal(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(
                canonical_profile=(
                    "ecosystem/public-programs/brazil/../../funds/example.md"
                )
            ),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("canonical_profile inseguro" in error for error in errors))

    def test_pending_record_requires_owner_and_next_action(self) -> None:
        with self.modified_example(
            "programs.jsonl",
            lambda row: row.update(
                research_status="em pesquisa",
                decision=None,
                owner="worker-example",
                next_action=None,
            ),
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("responsável e próxima ação" in error for error in errors))

    def test_completed_run_rejects_unfinished_task(self) -> None:
        with self.modified_example(
            "run-manifest.jsonl",
            lambda row: row.update(status="todo"),
            row_index=1,
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("run concluída contém tarefas" in error for error in errors))

    def test_coverage_must_match_manifest_country_and_source_type(self) -> None:
        with self.modified_example(
            "run-manifest.jsonl",
            lambda row: row.update(source_type="ministério responsável"),
            row_index=1,
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("cobertura e tarefas divergem" in error for error in errors))

    def test_country_and_source_type_pairs_must_be_unique(self) -> None:
        def duplicate_coverage(rows):
            duplicate = copy.deepcopy(rows[0])
            duplicate["coverage_id"] = "coverage-chile-corfo-duplicate"
            rows.append(duplicate)

        def duplicate_task(rows):
            rows[0]["task_count"] = 2
            duplicate = copy.deepcopy(rows[1])
            duplicate.update(
                task_id="task-example-chile-corfo-duplicate",
                worker_id="worker-example-chile-duplicate",
                shard_path=(
                    "research/epic-65/examples/shards/example-chile-duplicate/"
                ),
            )
            rows.append(duplicate)

        with self.modified_bundle(
            {
                "coverage-matrix.jsonl": duplicate_coverage,
                "run-manifest.jsonl": duplicate_task,
            }
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("país × source_type duplicado" in error for error in errors))

    def test_call_status_evidence_must_match_capture_date(self) -> None:
        def open_call(rows):
            rows[0].update(
                call_status="aberta",
                opened_on="2026-07-01",
                closes_on="2026-08-01",
            )

        def stale_status_evidence(rows):
            rows[2]["observed_on"] = "2026-07-26"
            status_claim = next(
                claim
                for claim in rows[2]["claims"]
                if claim["field"] == "status da chamada"
            )
            status_claim["finding"] = "confirmado"

        with self.modified_bundle(
            {
                "calls.jsonl": open_call,
                "evidence.jsonl": stale_status_evidence,
            }
        ) as bundle:
            errors = validate_bundle(bundle)
        self.assertTrue(any("data da captura" in error for error in errors))

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
        def __init__(self, filename, mutate, row_index=0):
            super().__init__({filename: lambda rows: mutate(rows[row_index])})


if __name__ == "__main__":
    unittest.main()
