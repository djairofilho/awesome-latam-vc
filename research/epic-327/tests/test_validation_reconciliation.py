import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location(
    "validation_reconcile", EPIC / "validation" / "reconcile.py"
)
RECONCILE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RECONCILE)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path, rows, key):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        RECONCILE.canonical_jsonl(rows, key), encoding="utf-8", newline="\n"
    )


def official_evidence(candidate_id, evidence_id, activity_on="2024-08-02"):
    claims = [
        ("identity", "Example Capital"),
        ("direct_startup_investment", True),
        ("recurrence", True),
        ("activity_date", activity_on),
        ("base_geography", "BR"),
    ]
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "candidate_id": candidate_id,
        "official_url": "https://example.com/official",
        "source_title": "Official activity",
        "accessed_on": "2026-08-02",
        "source_kind": "official_activity",
        "claims": [
            {
                "field": field,
                "value": {"finding": "confirmed", "value": value},
                "support": f"Official support for {field}.",
            }
            for field, value in claims
        ],
    }


def eligible_decision(candidate, evidence_id, activity_on="2024-08-02"):
    gate = {"finding": "confirmed", "evidence_ids": [evidence_id]}
    number = RECONCILE.partition(candidate["candidate_id"])
    return {
        "schema_version": "1.0",
        "candidate_id": candidate["candidate_id"],
        "input_sha256": RECONCILE.record_sha256(candidate),
        "validation_partition": number,
        "cutoff_date": "2026-08-02",
        "validated_on": "2026-08-02",
        "validator": f"validation-{number}",
        "gates": {
            "direct_investment": copy.deepcopy(gate),
            "recurrence": copy.deepcopy(gate),
            "recent_activity": {
                **copy.deepcopy(gate),
                "latest_official_activity_on": activity_on,
            },
            "latam_access": copy.deepcopy(gate),
            "identity": copy.deepcopy(gate),
        },
        "decision": "eligible",
        "reason": "Todos os gates foram confirmados.",
        "destination": "funds/",
        "next_action": "independent_review",
        "owner": None,
    }


class SyntheticFreeze:
    def __init__(self, root):
        self.epic = Path(root) / "research" / "epic-327"
        self.candidate = {
            "schema_version": "1.0",
            "candidate_id": "delta-fund-example-capital",
            "status": "ready_for_validation",
            "validation_partition": RECONCILE.partition(
                "delta-fund-example-capital"
            ),
            "name": "Example Capital",
        }
        self.evidence_id = "evidence-delta-example-validation"
        self.evidence = official_evidence(
            self.candidate["candidate_id"], self.evidence_id
        )
        self.decision = eligible_decision(self.candidate, self.evidence_id)

    def write(self, exceptions=()):
        consolidation = self.epic / "consolidation"
        write_jsonl(
            consolidation / "candidates.jsonl", [self.candidate], "candidate_id"
        )
        write_jsonl(consolidation / "evidence.jsonl", [], "evidence_id")
        write_jsonl(
            consolidation / "exceptions.jsonl", list(exceptions), "candidate_id"
        )
        selected = self.candidate["validation_partition"]
        for number in range(3):
            shard = self.epic / "shards" / f"validation-{number}"
            candidates = [self.candidate] if number == selected else []
            decisions = [self.decision] if number == selected else []
            evidence = [self.evidence] if number == selected else []
            candidates_text = RECONCILE.canonical_jsonl(candidates, "candidate_id")
            decisions_text = RECONCILE.canonical_jsonl(decisions, "candidate_id")
            evidence_text = RECONCILE.canonical_jsonl(evidence, "evidence_id")
            shard.mkdir(parents=True, exist_ok=True)
            (shard / "candidates.jsonl").write_text(
                candidates_text, encoding="utf-8", newline="\n"
            )
            (shard / "decisions.jsonl").write_text(
                decisions_text, encoding="utf-8", newline="\n"
            )
            (shard / "official-evidence.jsonl").write_text(
                evidence_text, encoding="utf-8", newline="\n"
            )
            write_json(
                shard / "summary.json",
                RECONCILE.expected_summary(
                    number,
                    candidates_text,
                    decisions_text,
                    evidence_text,
                    decisions,
                    evidence,
                ),
            )


class ValidationReconciliationTests(unittest.TestCase):
    def test_valid_freeze_reconciles_and_check_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.write()
            before = {
                path.relative_to(fixture.epic): path.read_bytes()
                for path in fixture.epic.rglob("*")
                if path.is_file()
            }
            self.assertEqual(RECONCILE.reconcile(fixture.epic), [])
            after = {
                path.relative_to(fixture.epic): path.read_bytes()
                for path in fixture.epic.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_missing_freeze_has_one_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            errors = RECONCILE.reconcile(Path(directory) / "research" / "epic-327")
            self.assertEqual(len(errors), 1)
            self.assertIn("freeze da #333 ausente ou incompleto", errors[0])

    def test_activity_window_is_inclusive_and_rejects_one_day_before(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.write()
            self.assertEqual(RECONCILE.reconcile(fixture.epic), [])

            fixture.evidence = official_evidence(
                fixture.candidate["candidate_id"],
                fixture.evidence_id,
                activity_on="2024-08-01",
            )
            fixture.decision = eligible_decision(
                fixture.candidate, fixture.evidence_id, activity_on="2024-08-01"
            )
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("fora da janela inclusiva" in error for error in errors))

    def test_future_activity_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.evidence = official_evidence(
                fixture.candidate["candidate_id"],
                fixture.evidence_id,
                activity_on="2026-08-03",
            )
            fixture.decision = eligible_decision(
                fixture.candidate, fixture.evidence_id, activity_on="2026-08-03"
            )
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("atividade oficial está no futuro" in error for error in errors))

    def test_partition_worker_and_input_hash_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            number = fixture.candidate["validation_partition"]
            fixture.decision["validation_partition"] = (number + 1) % 3
            fixture.decision["validator"] = f"validation-{(number + 1) % 3}"
            fixture.decision["input_sha256"] = "0" * 64
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("input_sha256 divergente" in error for error in errors))
            self.assertTrue(any("validation_partition divergente" in error for error in errors))
            self.assertTrue(any("validator não possui o shard" in error for error in errors))

    def test_evidence_must_belong_to_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.evidence["candidate_id"] = "delta-fund-another-capital"
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("pertence a delta-fund-another-capital" in error for error in errors))

    def test_claim_field_must_match_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.evidence["claims"] = [
                claim
                for claim in fixture.evidence["claims"]
                if claim["field"] != "recurrence"
            ]
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("claim de recurrence" in error for error in errors))

    def test_not_disclosed_cannot_be_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.decision["gates"]["recurrence"]["finding"] = "not_disclosed"
            for claim in fixture.evidence["claims"]:
                if claim["field"] == "recurrence":
                    claim["value"] = {"finding": "not_disclosed", "value": None}
            fixture.write()
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("eligible exige os cinco gates" in error for error in errors))

    def test_exceptions_are_disjoint_from_ready_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.write(
                exceptions=[
                    {
                        "candidate_id": fixture.candidate["candidate_id"],
                        "status": "identity_conflict",
                    }
                ]
            )
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("também presentes em exceptions" in error for error in errors))
            self.assertTrue(any("se sobrepõem" in error for error in errors))

    def test_union_of_shards_must_be_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.write()
            number = fixture.candidate["validation_partition"]
            shard = fixture.epic / "shards" / f"validation-{number}"
            (shard / "decisions.jsonl").write_text("", encoding="utf-8")
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("união dos três shards não é exata" in error for error in errors))

    def test_noncanonical_jsonl_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = SyntheticFreeze(directory)
            fixture.write()
            number = fixture.candidate["validation_partition"]
            path = fixture.epic / "shards" / f"validation-{number}" / "decisions.jsonl"
            path.write_text(
                json.dumps(fixture.decision, ensure_ascii=False, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            errors = RECONCILE.reconcile(fixture.epic)
            self.assertTrue(any("JSONL não canônico" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
