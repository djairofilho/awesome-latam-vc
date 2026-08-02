import hashlib
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
SPEC = importlib.util.spec_from_file_location(
    "delta_consolidation", EPIC / "consolidation" / "reduce.py"
)
REDUCER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REDUCER)


def group(*triage, names=("Example Capital",), baseline_profiles=(), countries=None):
    return {
        "names": set(names),
        "countries": Counter(countries or {"BR": 2}),
        "source_shards": {"triage-southern-cone-brazil"},
        "baseline_profiles": set(baseline_profiles),
        "triage": list(triage),
    }


def evidence(evidence_id, candidate_id, claims=()):
    return {
        "schema_version": "1.0",
        "evidence_id": evidence_id,
        "candidate_id": candidate_id,
        "official_url": "https://example.com/official",
        "source_title": "Official page",
        "accessed_on": "2026-08-02",
        "source_kind": "official_identity",
        "claims": list(claims)
        or [{"field": "identity", "value": "Example", "support": "Official identity."}],
    }


class ConsolidationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(
            (EPIC / "schemas" / "consolidated-candidate.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)

    def preliminary(self, candidate_id, candidate_group, evidence_rows=()):
        evidence_by_id = {row["evidence_id"]: row for row in evidence_rows}
        return REDUCER.preliminary(candidate_id, candidate_group, evidence_by_id)

    def test_partition_matches_contract_formula(self):
        candidate_id = "delta-fund-example-capital"
        expected = int(hashlib.sha256(candidate_id.encode()).hexdigest(), 16) % 3
        self.assertEqual(REDUCER.partition(candidate_id), expected)

    def test_baseline_match_is_terminal_duplicate(self):
        record = self.preliminary(
            "delta-fund-example-capital",
            group(
                {
                    "status": "duplicate",
                    "category": "fund",
                    "canonical_profile": "funds/example-capital.md",
                    "evidence_ids": [],
                },
                baseline_profiles={"funds/example-capital.md"},
            ),
        )
        self.assertEqual(record["status"], "duplicate")
        self.assertEqual(record["canonical_profile"], "funds/example-capital.md")
        self.validator.validate(record)

    def test_positive_identity_requires_existing_owned_evidence(self):
        candidate_id = "delta-fund-example-capital"
        evidence_id = "evidence-delta-example-capital-identity"
        triage = {
            "status": "identity_confirmed",
            "category": "fund_candidate",
            "official_domain": "example.com",
            "evidence_ids": [evidence_id],
        }
        missing = self.preliminary(candidate_id, group(triage))
        wrong_owner = self.preliminary(
            candidate_id,
            group(triage),
            [evidence(evidence_id, "delta-fund-another-capital")],
        )
        complete = self.preliminary(
            candidate_id, group(triage), [evidence(evidence_id, candidate_id)]
        )
        self.assertEqual(missing["status"], "unresolved")
        self.assertEqual(wrong_owner["status"], "unresolved")
        self.assertEqual(complete["status"], "ready_for_validation")

    def test_reference_validation_reports_missing_and_wrong_owner(self):
        evidence_id = "evidence-delta-example-capital-identity"
        groups = {
            "delta-fund-example-capital": group(
                {"status": "identity_confirmed", "evidence_ids": [evidence_id]}
            )
        }
        missing = REDUCER.evidence_reference_errors(groups, {})
        wrong_owner = REDUCER.evidence_reference_errors(
            groups,
            {evidence_id: evidence(evidence_id, "delta-fund-another-capital")},
        )
        self.assertIn("evidence_id inexistente", missing[0])
        self.assertIn("pertence a delta-fund-another-capital", wrong_owner[0])

    def test_contradictory_shard_decisions_never_advance(self):
        candidate_id = "delta-fund-example-capital"
        evidence_id = "evidence-delta-example-capital-identity"
        record = self.preliminary(
            candidate_id,
            group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "example.com",
                    "evidence_ids": [evidence_id],
                },
                {
                    "triage_status": "unresolved",
                    "category_hint": None,
                    "official_domain": "example.com",
                    "evidence_ids": [],
                },
            ),
            [evidence(evidence_id, candidate_id)],
        )
        self.assertEqual(record["status"], "identity_conflict")

    def test_category_contradiction_is_identity_conflict(self):
        candidate_id = "delta-fund-example-capital"
        evidence_id = "evidence-delta-example-capital-identity"
        record = self.preliminary(
            candidate_id,
            group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "example.com",
                    "evidence_ids": [evidence_id],
                },
                {
                    "status": "identity_confirmed",
                    "category": "corporate_vc",
                    "official_domain": "example.com",
                    "evidence_ids": [evidence_id],
                },
            ),
            [evidence(evidence_id, candidate_id)],
        )
        self.assertEqual(record["status"], "identity_conflict")

    def test_shared_domain_preserves_route_and_marks_other_record_conflict(self):
        routed = self.preliminary(
            "delta-fund-a-accelerator",
            group(
                {
                    "status": "routed",
                    "category": "accelerator",
                    "official_domain": "umbrella.example",
                    "route_destination": "ecosystem/accelerators/",
                    "evidence_ids": [],
                }
            ),
        )
        duplicate = self.preliminary(
            "delta-fund-z-fund",
            group(
                {
                    "status": "duplicate",
                    "category": "fund",
                    "official_domain": "umbrella.example",
                    "canonical_profile": "funds/z-fund.md",
                    "evidence_ids": [],
                },
                baseline_profiles={"funds/z-fund.md"},
            ),
        )
        REDUCER.resolve_domains([routed, duplicate])
        self.assertEqual(routed["status"], "routed")
        self.assertEqual(routed["route_destination"], "ecosystem/accelerators/")
        self.assertEqual(duplicate["status"], "identity_conflict")
        self.assertIsNone(duplicate["canonical_profile"])

    def test_shared_domain_never_elects_unresolved_or_merges_aliases(self):
        unresolved = self.preliminary(
            "delta-fund-a-unknown",
            group(
                {
                    "status": "identity_unresolved",
                    "category": "unresolved",
                    "official_domain": "shared.example",
                    "evidence_ids": [],
                },
                names=("Unknown",),
            ),
        )
        candidate_id = "delta-fund-z-ready"
        evidence_id = "evidence-delta-z-ready-identity"
        ready = self.preliminary(
            candidate_id,
            group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "shared.example",
                    "evidence_ids": [evidence_id],
                },
                names=("Ready", "Ready Ventures"),
            ),
            [evidence(evidence_id, candidate_id)],
        )
        REDUCER.resolve_domains([unresolved, ready])
        self.assertEqual(unresolved["status"], "identity_conflict")
        self.assertEqual(ready["status"], "identity_conflict")
        self.assertIsNone(ready["canonical_candidate_id"])
        self.assertEqual(ready["aliases"], ["Ready Ventures"])
        self.assertNotIn("Unknown", ready["aliases"])

    def test_geography_comes_only_from_owned_official_evidence(self):
        candidate_id = "delta-fund-example-capital"
        evidence_id = "evidence-delta-example-capital-identity"
        triage = {
            "status": "identity_confirmed",
            "category": "fund_candidate",
            "official_domain": "example.com",
            "evidence_ids": [evidence_id],
        }
        disclosed = self.preliminary(
            candidate_id,
            group(triage, countries={"BR": 7}),
            [
                evidence(
                    evidence_id,
                    candidate_id,
                    [
                        {"field": "base_geography", "value": "MX", "support": "Office."},
                        {
                            "field": "market_access",
                            "value": ["LATAM", "BR"],
                            "support": "Markets.",
                        },
                    ],
                )
            ],
        )
        not_disclosed = self.preliminary(candidate_id, group(triage, countries={"BR": 7}))
        self.assertEqual(disclosed["base_geography"], ["MX"])
        self.assertEqual(disclosed["investment_geography"], ["BR", "LATAM"])
        self.assertEqual(not_disclosed["base_geography"], "not_disclosed")
        self.assertEqual(not_disclosed["investment_geography"], "not_disclosed")

    def test_schema_rejects_invalid_hostname_and_status_fields(self):
        record = self.preliminary(
            "delta-fund-example-capital",
            group(
                {
                    "status": "duplicate",
                    "category": "fund",
                    "official_domain": "example.com",
                    "canonical_profile": "funds/example-capital.md",
                    "evidence_ids": [],
                },
                baseline_profiles={"funds/example-capital.md"},
            ),
        )
        record["official_domains"] = ["foo..bar"]
        record["route_destination"] = "ecosystem/accelerators/"
        messages = [error.message for error in self.validator.iter_errors(record)]
        self.assertTrue(any("does not match" in message for message in messages))
        self.assertTrue(any("is not of type 'null'" in message for message in messages))

    def test_occurrence_count_invariant(self):
        self.assertTrue(
            REDUCER.occurrence_count_is_valid(
                {"occurrence_count": 3, "country_occurrences": {"BR": 2, "MX": 1}}
            )
        )
        self.assertFalse(
            REDUCER.occurrence_count_is_valid(
                {"occurrence_count": 999, "country_occurrences": {"BR": 1}}
            )
        )

    def test_build_reconciles_partitions_terminals_and_manual_exceptions(self):
        ready_id = "delta-fund-ready"
        unresolved_id = "delta-fund-unresolved"
        evidence_id = "evidence-delta-ready-identity"
        groups = {
            ready_id: group(
                {
                    "status": "identity_confirmed",
                    "category": "fund_candidate",
                    "official_domain": "ready.example",
                    "evidence_ids": [evidence_id],
                },
                names=("Ready",),
                countries={"MX": 1},
            ),
            unresolved_id: group(
                {
                    "status": "identity_unresolved",
                    "category": "unresolved",
                    "official_domain": None,
                    "evidence_ids": [],
                },
                names=("Unresolved",),
                countries={"CO": 2},
            ),
        }
        evidence_rows = {evidence_id: evidence(evidence_id, ready_id)}
        with patch.object(REDUCER, "collect_inputs", return_value=(groups, evidence_rows, [])):
            errors, outputs = REDUCER.build()
        self.assertEqual(errors, [])
        exceptions = [json.loads(line) for line in outputs["exceptions.jsonl"].splitlines()]
        summary = json.loads(outputs["summary.json"])
        partitions = [
            json.loads(line)
            for number in range(3)
            for line in outputs[f"validation-{number}.jsonl"].splitlines()
        ]
        self.assertEqual(exceptions[0]["candidate_id"], unresolved_id)
        self.assertEqual(exceptions[0]["destination"], "manual_identity_review")
        self.assertEqual([record["candidate_id"] for record in partitions], [ready_id])
        self.assertEqual(summary["terminal_records"], 1)
        self.assertEqual(summary["exception_records"], 1)
        self.assertEqual(summary["reconciled_records"], summary["unique_candidates"])


if __name__ == "__main__":
    unittest.main()
