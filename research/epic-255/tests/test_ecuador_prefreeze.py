import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/epic-255/ecuador"


def rows(name):
    return [
        json.loads(line)
        for line in (AUDIT / name).read_text(encoding="utf-8").splitlines()
        if line
    ]


class EcuadorPrefreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(
            [sys.executable, str(AUDIT / "build_prefreeze.py")],
            check=True,
        )

    def test_baseline_and_historical_delta_are_hashed(self):
        summary = json.loads(
            (AUDIT / "baseline/summary.json").read_text(encoding="utf-8")
        )
        self.assertGreater(summary["profile_count"], 0)
        self.assertEqual(64, len(summary["profile_manifest_sha256"]))
        prior = rows("baseline/prior-candidates.jsonl")
        self.assertEqual(1, len(prior))
        self.assertEqual(64, len(prior[0]["sha256"]))
        self.assertGreater(prior[0]["record_count"], 0)

    def test_discovery_is_non_regulatory_or_audited_handoff(self):
        allowed = {"non_regulatory", "handoff_audited_non_regulatory"}
        self.assertTrue(
            all(
                candidate["discovery_origin"] in allowed
                for candidate in rows("candidates.jsonl")
            )
        )

    def test_regulator_target_and_limited_effect(self):
        candidates = rows("candidates.jsonl")
        regulators = [
            source
            for source in rows("source-inventory.jsonl")
            if source["family"] == "regulator_identity"
        ]
        ratio = 100 * len(regulators) / len(candidates)
        self.assertGreaterEqual(ratio, 5)
        self.assertLessEqual(ratio, 10)
        query = rows("scvs-query-log.jsonl")[0]
        self.assertFalse(query["used_for_discovery"])
        self.assertFalse(query["used_as_sole_eligibility_evidence"])
        self.assertEqual("identity_resolved_only", query["effect"])

    def test_all_sources_have_provenance_and_owner(self):
        required = {
            "source_id",
            "family",
            "url",
            "scope",
            "owner",
            "accessed_on",
            "result",
        }
        self.assertTrue(
            all(required <= source.keys() for source in rows("source-inventory.jsonl"))
        )

    def test_every_candidate_has_terminal_decision_and_valid_sources(self):
        allowed = {
            "eligible",
            "insufficient_evidence",
            "routed",
            "duplicate",
        }
        source_ids = {
            source["source_id"] for source in rows("source-inventory.jsonl")
        }
        for candidate in rows("candidates.jsonl"):
            self.assertIn(candidate["decision"], allowed)
            self.assertTrue(set(candidate["discovery_source_ids"]) <= source_ids)

    def test_impaqto_is_only_eligible_and_is_an_audited_handoff(self):
        eligible = [
            candidate
            for candidate in rows("candidates.jsonl")
            if candidate["decision"] == "eligible"
        ]
        self.assertEqual(["ec-impaqto-capital"], [row["candidate_id"] for row in eligible])
        self.assertEqual(
            "handoff_audited_non_regulatory",
            eligible[0]["discovery_origin"],
        )

    def test_terminal_counts(self):
        counts = {}
        for candidate in rows("candidates.jsonl"):
            decision = candidate["decision"]
            counts[decision] = counts.get(decision, 0) + 1
        self.assertEqual(
            {
                "eligible": 1,
                "duplicate": 3,
                "routed": 5,
                "insufficient_evidence": 6,
            },
            counts,
        )

    def test_blind_search_and_review_gate(self):
        coverage = json.loads(
            (AUDIT / "coverage-matrix.json").read_text(encoding="utf-8")
        )
        self.assertFalse(
            coverage["blind_search"]["candidate_list_disclosed_to_searcher"]
        )
        self.assertGreaterEqual(
            len(coverage["blind_search"]["new_source_families"]),
            2,
        )
        request = json.loads(
            (AUDIT / "review-request.json").read_text(encoding="utf-8")
        )
        self.assertEqual("pending_independent_review", request["status"])
        self.assertFalse(request["freeze_allowed"])
        self.assertGreaterEqual(len(request["deterministic_exclusion_sample"]), 1)
        self.assertFalse((AUDIT / "freeze-manifest.json").exists())
        self.assertFalse((AUDIT / "publication").exists())

    def test_new_artifacts_have_no_mojibake(self):
        paths = (
            list(AUDIT.rglob("*.json"))
            + list(AUDIT.rglob("*.jsonl"))
            + list(AUDIT.rglob("*.md"))
            + list(AUDIT.rglob("*.py"))
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertFalse(
                any(marker in text for marker in ("Ã", "Â", "�", "â€")),
                path,
            )


if __name__ == "__main__":
    unittest.main()
