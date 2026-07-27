from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


EPIC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EPIC_DIR))

import validate  # noqa: E402


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
