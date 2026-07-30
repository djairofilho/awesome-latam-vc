from __future__ import annotations

import json
import unittest
from pathlib import Path


EPIC_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SCHEMAS = {
    "audit-report.schema.json",
    "coverage-matrix.schema.json",
    "cvm-query.schema.json",
    "evidence.schema.json",
    "candidate.schema.json",
    "identity-resolution.schema.json",
    "review-sample.schema.json",
    "run-manifest-record.schema.json",
    "source-inventory.schema.json",
}
EXPECTED_TEMPLATES = {
    "audit-report.json",
    "candidates.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "review-sample.jsonl",
    "run-manifest.jsonl",
    "source-inventory.jsonl",
}


class ContractScaffoldTests(unittest.TestCase):
    def test_contract_materializes_every_required_schema(self) -> None:
        schema_dir = EPIC_ROOT / "schemas"
        found = (
            {path.name for path in schema_dir.glob("*.json")}
            if schema_dir.exists()
            else set()
        )
        self.assertEqual(EXPECTED_SCHEMAS, found)

    def test_contract_materializes_templates_and_examples(self) -> None:
        for directory_name in ("templates", "examples"):
            with self.subTest(directory=directory_name):
                directory = EPIC_ROOT / directory_name
                found = (
                    {path.name for path in directory.iterdir() if path.is_file()}
                    if directory.exists()
                    else set()
                )
                self.assertTrue(EXPECTED_TEMPLATES <= found)

    def test_schemas_are_draft_2020_12_and_close_unknown_fields(self) -> None:
        def object_contracts(schema: dict) -> list[dict]:
            contracts: list[dict] = []
            if schema.get("type") == "object":
                contracts.append(schema)
            for value in schema.values():
                if isinstance(value, dict):
                    contracts.extend(object_contracts(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            contracts.extend(object_contracts(item))
            return contracts

        for filename in EXPECTED_SCHEMAS:
            with self.subTest(schema=filename):
                path = EPIC_ROOT / "schemas" / filename
                self.assertTrue(path.exists(), f"schema ausente: {filename}")
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(
                    "https://json-schema.org/draft/2020-12/schema",
                    schema.get("$schema"),
                )
                contracts = object_contracts(schema)
                self.assertTrue(contracts, f"{filename} não define objetos")
                for contract in contracts:
                    self.assertFalse(
                        contract.get("additionalProperties", True),
                        f"{filename} deve rejeitar campos desconhecidos",
                    )

    def test_contract_and_machine_files_have_no_mojibake(self) -> None:
        markers = ("Ã", "Â", "�", "\x07")
        paths = [EPIC_ROOT / "README.md"]
        for directory_name in ("schemas", "templates", "examples"):
            directory = EPIC_ROOT / directory_name
            if directory.exists():
                paths.extend(path for path in directory.rglob("*") if path.is_file())
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertFalse(
                    any(marker in text for marker in markers),
                    f"possível mojibake em {path}",
                )


if __name__ == "__main__":
    unittest.main()
