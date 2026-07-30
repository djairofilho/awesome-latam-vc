from __future__ import annotations

import copy
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

from fixtures import HASHED_ARTIFACTS, build_bundle, write_bundle


EPIC_ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    path = EPIC_ROOT / "validate.py"
    if not path.exists():
        raise AssertionError(
            "research/epic-207/validate.py ausente; "
            "a implementação funcional da #209 ainda não existe"
        )
    spec = importlib.util.spec_from_file_location("epic_207_validate", path)
    if spec is None or spec.loader is None:
        raise AssertionError("não foi possível carregar o validador da epic 207")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ContractInvariantTests(unittest.TestCase):
    def validate_bundle(
        self,
        mutate: Callable[[dict[str, Any]], None] | None = None,
    ) -> list[str]:
        bundle = build_bundle()
        if mutate:
            mutate(bundle)
        with tempfile.TemporaryDirectory() as temporary:
            dataset = Path(temporary)
            write_bundle(dataset, bundle)
            return load_validator().validate_dataset(dataset)

    def test_valid_example_and_zero_cvm_queries_pass(self) -> None:
        self.assertEqual([], self.validate_bundle())

    def test_eligible_requires_official_evidence_for_every_gate(self) -> None:
        field_to_evidence = {
            "investimento direto": "ev-example-direct_investment",
            "recorrência": "ev-example-recurring_investment",
            "atividade": "ev-example-recent_activity",
            "acesso ao Brasil": "ev-example-brazil_relation",
            "identidade": "ev-example-identity",
        }
        for expected, evidence_id in field_to_evidence.items():
            with self.subTest(gate=expected):
                def mutate(
                    bundle: dict[str, Any],
                    target: str = evidence_id,
                ) -> None:
                    evidence = next(
                        item
                        for item in bundle["evidence.jsonl"]
                        if item["evidence_id"] == target
                    )
                    evidence["source_type"] = "third_party"

                errors = self.validate_bundle(mutate)
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_every_candidate_must_originate_outside_cvm(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            source = bundle["source-inventory.jsonl"][0]
            source.update(
                source_family="regulator",
                research_channel="cvm",
                regulatory_source=True,
                discovery_allowed=False,
            )

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("origem não-CVM" in error for error in errors), errors)

    def test_cvm_policy_has_a_ten_percent_ceiling_and_no_floor(self) -> None:
        self.assertEqual([], self.validate_bundle(), "zero consulta CVM deve ser válido")

        def mutate(bundle: dict[str, Any]) -> None:
            bundle["cvm-query-log.jsonl"].append(
                {
                    "schema_version": "1.0",
                    "query_id": "cvm-query-example",
                    "candidate_id": "fund-example-org",
                    "question": "Qual entidade administra o veículo?",
                    "searched_identifier": "Example Fundo I",
                    "reference": "https://cvm.gov.br/example",
                    "accessed_on": "2026-07-30",
                    "minimum_fact": "manager_vehicle_relation",
                    "divergence": None,
                    "outcome": "confirmed",
                    "preexisting_non_cvm_source_ids": ["src-example-rounds"],
                    "owner": "adjudicator",
                    "next_action": None,
                }
            )

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("teto CVM de 10%" in error for error in errors), errors)

    def test_cvm_query_requires_preexisting_non_cvm_provenance(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            bundle["cvm-query-log.jsonl"].append(
                {
                    "schema_version": "1.0",
                    "query_id": "cvm-query-example",
                    "candidate_id": "fund-example-org",
                    "question": "Qual entidade administra o veículo?",
                    "searched_identifier": "Example Fundo I",
                    "reference": "https://cvm.gov.br/example",
                    "accessed_on": "2026-07-30",
                    "minimum_fact": "manager_vehicle_relation",
                    "divergence": None,
                    "outcome": "confirmed",
                    "preexisting_non_cvm_source_ids": [],
                    "owner": "adjudicator",
                    "next_action": None,
                }
            )

        errors = self.validate_bundle(mutate)
        self.assertTrue(
            any("proveniência não-CVM anterior" in error for error in errors),
            errors,
        )

    def test_references_cannot_be_orphaned(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            bundle["candidates.jsonl"][0]["discovery_source_ids"] = [
                "src-does-not-exist"
            ]

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("referência órfã" in error for error in errors), errors)

    def test_candidate_identity_references_cannot_form_cycles(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            first = bundle["candidates.jsonl"][0]
            second = copy.deepcopy(first)
            second.update(
                candidate_id="fund-example-two",
                canonical_candidate_id=first["candidate_id"],
                identity_resolution_ids=[],
                decision="duplicate",
                reason="Duplicate fixture.",
            )
            first.update(
                canonical_candidate_id=second["candidate_id"],
                decision="duplicate",
                reason="Cycle fixture.",
            )
            bundle["candidates.jsonl"].append(second)

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("ciclo de identidade" in error for error in errors), errors)

    def test_recent_activity_must_be_official_and_within_24_months(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            candidate = bundle["candidates.jsonl"][0]
            candidate["last_official_activity_on"] = "2024-07-29"
            evidence = next(
                item
                for item in bundle["evidence.jsonl"]
                if item["evidence_id"] == "ev-example-recent_activity"
            )
            evidence["observed_on"] = "2024-07-29"

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("janela de 24 meses" in error for error in errors), errors)

    def test_workers_cannot_share_or_escape_shards(self) -> None:
        for case in ("shared", "traversal"):
            with self.subTest(case=case):
                def mutate(bundle: dict[str, Any], mutation: str = case) -> None:
                    run, first = bundle["run-manifest.jsonl"]
                    second = copy.deepcopy(first)
                    second.update(
                        task_id="task-example-two",
                        worker_id="worker-two",
                    )
                    if mutation == "traversal":
                        second["shard_path"] = (
                            "research/epic-207/brazil/shards/../shared"
                        )
                    run["task_count"] = 2
                    bundle["run-manifest.jsonl"].append(second)

                errors = self.validate_bundle(mutate)
                expected = "shard_path inseguro" if case == "traversal" else "shard compartilhado"
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_complete_run_rejects_tampered_artifact_hash(self) -> None:
        bundle = build_bundle()
        with tempfile.TemporaryDirectory() as temporary:
            dataset = Path(temporary)
            write_bundle(dataset, bundle)
            run = bundle["run-manifest.jsonl"][0]
            run["hash_algorithm"] = "sha256"
            run["artifact_hashes"] = {
                filename: hashlib.sha256(
                    (dataset / filename)
                    .read_text(encoding="utf-8")
                    .replace("\r\n", "\n")
                    .encode("utf-8")
                ).hexdigest()
                for filename in HASHED_ARTIFACTS
            }
            write_bundle(dataset, bundle)
            candidate = bundle["candidates.jsonl"][0]
            candidate["name"] = "Tampered Ventures"
            write_bundle(dataset, bundle)

            errors = load_validator().validate_dataset(dataset)

        self.assertTrue(
            any("hash divergente para candidates.jsonl" in error for error in errors),
            errors,
        )

    def test_dataset_rejects_mojibake(self) -> None:
        def mutate(bundle: dict[str, Any]) -> None:
            bundle["source-inventory.jsonl"][0]["notes"] = "programaÃ§Ã£o"

        errors = self.validate_bundle(mutate)
        self.assertTrue(any("mojibake" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
