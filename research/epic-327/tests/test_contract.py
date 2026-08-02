import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"


class LatamDeltaContractTests(unittest.TestCase):
    def test_contract_matches_frozen_baseline(self):
        contract = json.loads((EPIC / "contract.json").read_text(encoding="utf-8"))
        summary = json.loads(
            (EPIC / "baseline" / "summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(contract["epic"], 327)
        self.assertEqual(contract["baseline_commit"], summary["baseline_commit"])
        self.assertEqual(contract["cutoff_date"], summary["cutoff_date"])
        self.assertFalse(summary["snapshot_policy"]["external_intake_imported"])

    def test_worker_ownership_is_exclusive(self):
        topology = json.loads(
            (EPIC / "workers" / "topology.json").read_text(encoding="utf-8")
        )
        triage = [worker for worker in topology["workers"] if worker["phase"] == "triage"]
        validation = [
            worker for worker in topology["workers"] if worker["phase"] == "validation"
        ]
        triage_paths = [worker["write_prefix"] for worker in triage]
        validation_paths = [worker["write_prefix"] for worker in validation]
        self.assertEqual(len(triage_paths), len(set(triage_paths)))
        self.assertEqual(len(validation_paths), len(set(validation_paths)))
        self.assertEqual(
            sorted(worker["partition"] for worker in validation),
            [0, 1, 2],
        )
        self.assertEqual(topology["shared_write_policy"], "integrator_only")

    def test_schemas_are_valid_json_schema(self):
        try:
            from jsonschema.validators import Draft202012Validator
        except ImportError as exc:  # pragma: no cover - dependency is part of research tooling
            self.fail(f"jsonschema is required by the research validators: {exc}")
        for path in sorted((EPIC / "schemas").glob("*.schema.json")):
            with self.subTest(path=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)

    def test_baseline_is_deterministic(self):
        result = subprocess.run(
            [
                sys.executable,
                str(EPIC / "baseline" / "build_baseline.py"),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
