from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


EPIC_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("epic_64_validate", EPIC_DIR / "validate.py")
assert SPEC is not None and SPEC.loader is not None
validate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate
SPEC.loader.exec_module(validate)


def load_bundle() -> dict[str, list[dict]]:
    bundle: dict[str, list[dict]] = {}
    for filename in validate.SCHEMAS:
        records, errors = validate.read_jsonl(EPIC_DIR / "examples" / filename)
        if errors:
            raise AssertionError(errors)
        bundle[filename] = records
    return bundle


def write_bundle(root: Path, bundle: dict[str, list[dict]]) -> None:
    for filename, records in bundle.items():
        content = "".join(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            for record in records
        )
        (root / filename).write_text(content, encoding="utf-8")


class ContractValidationTests(unittest.TestCase):
    def validate_mutation(self, mutate) -> list[str]:
        bundle = copy.deepcopy(load_bundle())
        mutate(bundle)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_bundle(root, bundle)
            return validate.validate_dataset(root)

    def test_contract_templates_matrix_and_example_validate(self) -> None:
        self.assertEqual([], validate.validate_contract())

    def test_completed_audit_rejects_tampered_artifact_hash(self) -> None:
        bundle = load_bundle()
        with tempfile.TemporaryDirectory() as directory:
            dataset = Path(directory)
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
                for filename in validate.HASHED_ARTIFACTS
            }
            write_bundle(dataset, bundle)
            candidates = dataset / "candidates.jsonl"
            lines = candidates.read_text(encoding="utf-8").splitlines()
            record = json.loads(lines[0])
            record["brand"]["name"] = f"{record['brand']['name']} alterada"
            lines[0] = json.dumps(
                record,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            candidates.write_text("\n".join(lines) + "\n", encoding="utf-8")

            errors = validate.validate_dataset(dataset)

        self.assertTrue(
            any("hash divergente para candidates.jsonl" in error for error in errors),
            errors,
        )

    def test_eligible_platform_does_not_require_direct_investment(self) -> None:
        candidate = load_bundle()["candidates.jsonl"][0]
        self.assertNotIn("direct_investment", candidate)
        self.assertEqual([], validate.validate_dataset(EPIC_DIR / "examples"))

    def test_rejects_direct_investment_field(self) -> None:
        errors = self.validate_mutation(
            lambda bundle: bundle["candidates.jsonl"][0].update(
                {"direct_investment": True}
            )
        )
        self.assertTrue(any("direct_investment" in error for error in errors))

    def test_eligible_requires_official_structured_latam_route(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            route = bundle["evidence.jsonl"][0]
            route["source_type"] = "third_party"

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("rota estruturada" in error for error in errors))

    def test_regulatory_claim_rejects_third_party_source(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            regulatory = bundle["evidence.jsonl"][2]
            regulatory["source_type"] = "third_party"

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("alegação regulatória" in error for error in errors))

    def test_temporary_offer_can_never_become_profile(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            offer = bundle["candidates.jsonl"][0]["offers"][0]
            offer["profile_eligible"] = True

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("False was expected" in error for error in errors))

    def test_activity_must_be_inside_24_month_window(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            bundle["candidates.jsonl"][0]["last_official_activity_on"] = "2024-07-26"

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("janela de 24 meses" in error for error in errors))

    def test_activity_date_must_match_official_evidence(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            bundle["candidates.jsonl"][0]["last_official_activity_on"] = "2026-02-01"

        errors = self.validate_mutation(mutate)
        self.assertTrue(
            any("não corresponde à evidência oficial" in error for error in errors),
            errors,
        )

    def test_coverage_requires_every_source_category(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            bundle["coverage-matrix.jsonl"][0]["sources"].pop()

        errors = self.validate_mutation(mutate)
        self.assertTrue(errors)
        self.assertTrue(any("coverage-matrix.jsonl" in error for error in errors))

    def test_complete_coverage_source_must_match_country_and_category(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            source = bundle["source-inventory.jsonl"][0]
            source["country"] = "MX"
            source["source_category"] = "discovery"

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("outro país" in error for error in errors), errors)
        self.assertTrue(any("outra categoria" in error for error in errors), errors)

    def test_complete_coverage_requires_complete_inventory(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            source = bundle["source-inventory.jsonl"][0]
            source.update(
                {
                    "result": "partial",
                    "reason": "Coleta incompleta.",
                    "owner": "worker-example",
                    "next_action": "Concluir a coleta.",
                }
            )

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("inventário não concluído" in error for error in errors))

    def test_rejects_duplicate_nested_entity_ids(self) -> None:
        cases = (
            ("products", "product_id"),
            ("offers", "offer_id"),
            ("regulatory_records", "regulatory_id"),
        )
        for collection, key in cases:
            with self.subTest(collection=collection):
                def mutate(
                    bundle: dict[str, list[dict]],
                    collection: str = collection,
                ) -> None:
                    records = bundle["candidates.jsonl"][0][collection]
                    records.append(copy.deepcopy(records[0]))

                errors = self.validate_mutation(mutate)
                self.assertTrue(
                    any(
                        f"{key} duplicado" in error
                        or (
                            collection == "regulatory_records"
                            and "non-unique elements" in error
                        )
                        for error in errors
                    ),
                    errors,
                )

    def test_evidence_subject_type_must_match_subject_id(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            evidence = bundle["evidence.jsonl"][1]
            evidence["subject_type"] = "operator"

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("subject_id" in error for error in errors), errors)

    def test_regulatory_claim_must_reference_declared_record(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            evidence = copy.deepcopy(bundle["evidence.jsonl"][2])
            evidence["evidence_id"] = "ev-regulatoria-solta"
            evidence["subject_type"] = "platform"
            evidence["subject_id"] = "plat-exemplo"
            bundle["evidence.jsonl"].append(evidence)

        errors = self.validate_mutation(mutate)
        self.assertTrue(
            any(
                "deve apontar para um registro regulatório" in error
                for error in errors
            ),
            errors,
        )

    def test_complete_http_source_requires_cache_key(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            bundle["source-inventory.jsonl"][0]["cache_key"] = None

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("cache_key" in error for error in errors), errors)

    def test_insufficient_evidence_requires_owner_and_next_action(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            candidate = bundle["candidates.jsonl"][0]
            candidate.update(
                {
                    "decision": "insufficient_evidence",
                    "reason": "Falta comprovação.",
                    "owner": "reviewer",
                    "next_action": None,
                }
            )

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("next_action" in error for error in errors), errors)

    def test_duplicate_rejects_self_cycle_and_profile_traversal(self) -> None:
        def self_reference(bundle: dict[str, list[dict]]) -> None:
            candidate = bundle["candidates.jsonl"][0]
            candidate.update(
                {
                    "decision": "duplicate",
                    "reason": "Duplicata sintética.",
                    "canonical_platform_id": candidate["platform_id"],
                }
            )

        self_errors = self.validate_mutation(self_reference)
        self.assertTrue(any("si mesma" in error for error in self_errors), self_errors)

        def traversal(bundle: dict[str, list[dict]]) -> None:
            candidate = bundle["candidates.jsonl"][0]
            candidate.update(
                {
                    "decision": "duplicate",
                    "reason": "Duplicata sintética.",
                    "canonical_platform_id": None,
                    "canonical_profile": "ecosystem/funding-platforms/../funds/x.md",
                }
            )

        traversal_errors = self.validate_mutation(traversal)
        self.assertTrue(
            any("canonical_profile" in error for error in traversal_errors),
            traversal_errors,
        )

    def test_duplicate_rejects_canonical_cycle(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            original = bundle["candidates.jsonl"][0]
            clone = copy.deepcopy(original)
            replacements = {
                "plat-exemplo": "plat-exemplo-dois",
                "op-exemplo": "op-exemplo-dois",
                "brand-exemplo": "brand-exemplo-dois",
                "prod-exemplo-equity": "prod-exemplo-dois-equity",
                "offer-exemplo-2025": "offer-exemplo-dois-2025",
                "reg-exemplo": "reg-exemplo-dois",
                "ev-exemplo-rota": "ev-exemplo-dois-rota",
                "ev-exemplo-atividade": "ev-exemplo-dois-atividade",
                "ev-exemplo-regulacao": "ev-exemplo-dois-regulacao",
            }

            def replace(value):
                if isinstance(value, dict):
                    return {key: replace(child) for key, child in value.items()}
                if isinstance(value, list):
                    return [replace(child) for child in value]
                return replacements.get(value, value)

            clone = replace(clone)
            original.update(
                {
                    "decision": "duplicate",
                    "reason": "Duplicata sintética.",
                    "canonical_platform_id": clone["platform_id"],
                }
            )
            clone.update(
                {
                    "decision": "duplicate",
                    "reason": "Duplicata sintética.",
                    "canonical_platform_id": original["platform_id"],
                }
            )
            bundle["candidates.jsonl"].append(clone)
            bundle["evidence.jsonl"].extend(
                replace(copy.deepcopy(bundle["evidence.jsonl"]))
            )

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("ciclo de duplicatas" in error for error in errors), errors)

    def test_active_task_requires_owner_and_next_action(self) -> None:
        for status in ("leased", "extracted", "verified"):
            with self.subTest(status=status):
                def mutate(
                    bundle: dict[str, list[dict]],
                    status: str = status,
                ) -> None:
                    task = bundle["run-manifest.jsonl"][1]
                    task.update(
                        {"status": status, "owner": None, "next_action": None}
                    )

                errors = self.validate_mutation(mutate)
                self.assertTrue(any("owner" in error for error in errors), errors)
                self.assertTrue(any("next_action" in error for error in errors), errors)

    def test_complete_run_rejects_active_task(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            task = bundle["run-manifest.jsonl"][1]
            task.update(
                {
                    "status": "verified",
                    "owner": "worker-example",
                    "next_action": "Consolidar o shard.",
                }
            )

        errors = self.validate_mutation(mutate)
        self.assertTrue(any("run complete contém tarefa ativa" in error for error in errors))

    def test_task_requires_safe_owned_shard(self) -> None:
        def traversal(bundle: dict[str, list[dict]]) -> None:
            bundle["run-manifest.jsonl"][1]["shard_path"] = (
                "research/epic-64/brazil/shards/../shared"
            )

        traversal_errors = self.validate_mutation(traversal)
        self.assertTrue(any("shard_path" in error for error in traversal_errors))

        def ownership(bundle: dict[str, list[dict]]) -> None:
            run = bundle["run-manifest.jsonl"][0]
            first = bundle["run-manifest.jsonl"][1]
            second = copy.deepcopy(first)
            second["task_id"] = "task-exemplo-dois"
            second["worker_id"] = "worker-other"
            run["task_count"] = 2
            bundle["run-manifest.jsonl"].append(second)

        ownership_errors = self.validate_mutation(ownership)
        self.assertTrue(
            any("mais de um worker" in error for error in ownership_errors),
            ownership_errors,
        )

    def test_blocked_task_requires_owner_reason_and_next_action(self) -> None:
        def mutate(bundle: dict[str, list[dict]]) -> None:
            task = bundle["run-manifest.jsonl"][1]
            task.update(
                {
                    "status": "blocked",
                    "owner": None,
                    "block_reason": None,
                    "next_action": None,
                }
            )

        errors = self.validate_mutation(mutate)
        self.assertTrue(errors)
        self.assertTrue(any("run-manifest.jsonl" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
