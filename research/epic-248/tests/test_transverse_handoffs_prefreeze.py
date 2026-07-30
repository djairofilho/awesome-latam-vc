import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research" / "epic-248" / "transverse-handoffs"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def read_json_frontmatter(path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw.split("---", 2)[1])


class TransverseHandoffsPrefreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = read_json(AUDIT / "contract.json")
        cls.sources = read_jsonl(AUDIT / "source-inventory.jsonl")
        cls.candidates = read_jsonl(AUDIT / "candidates.jsonl")
        cls.evidence = read_jsonl(AUDIT / "evidence.jsonl")
        cls.regulator = read_jsonl(AUDIT / "regulator-query-log.jsonl")
        cls.coverage = read_json(AUDIT / "coverage-matrix.json")
        cls.request = read_json(AUDIT / "review-request.json")
        cls.manifest = read_json(AUDIT / "prefreeze-manifest.json")

    def test_contract_is_handoff_scoped(self):
        self.assertEqual(self.contract["epic"], 248)
        self.assertEqual(self.contract["markets"], ["AR", "BR"])
        self.assertEqual(self.contract["cutoff"], "2026-07-30")
        self.assertEqual(
            self.contract["coverage_claim"],
            "audited_handoff_batch_not_market_completeness",
        )

    def test_exact_handoff_universe_is_terminal(self):
        self.assertEqual(
            [row["candidate_id"] for row in self.candidates],
            ["ar-beta-impacto", "ar-primary-x", "br-saasholic"],
        )
        self.assertTrue(all(row["decision"] == "eligible" for row in self.candidates))
        self.assertTrue(all(row["status"] == "terminal" for row in self.candidates))
        self.assertTrue(
            all(row["discovery_origin"] == "audited_non_regulatory_handoff" for row in self.candidates)
        )

    def test_sources_cover_every_candidate(self):
        source_ids = {row["source_id"] for row in self.sources}
        self.assertEqual(len(self.sources), 12)
        self.assertTrue(all(row["research_channel"] == "non_regulatory" for row in self.sources))
        self.assertTrue(
            all(set(row["discovery_source_ids"]) <= source_ids for row in self.candidates)
        )
        self.assertEqual(self.coverage["non_regulatory_discovery_percent"], 100.0)

    def test_no_unjustified_regulator_query(self):
        self.assertEqual(self.regulator, [])
        self.assertEqual(self.coverage["regulatory_query_count"], 0)
        self.assertEqual(self.coverage["regulatory_case_percent"], 0.0)
        self.assertIn(
            "zero is valid",
            self.contract["regulator_target_application"],
        )

    def test_eligible_gates_are_documented(self):
        evidence = {row["candidate_id"]: row["claims"] for row in self.evidence}
        for candidate in self.candidates:
            claims = evidence[candidate["candidate_id"]]
            self.assertTrue(claims["base_geography"].startswith("confirmed"))
            self.assertEqual(claims["direct_investment"], "confirmed")
            self.assertTrue(claims["recurrence"].startswith("confirmed"))
            self.assertTrue(claims["current_activity"].startswith("confirmed"))
            self.assertTrue(claims["portfolio"].startswith("confirmed"))
            self.assertEqual(claims["founder_route"], "confirmed")
            self.assertEqual(claims["official_evidence"], "confirmed")

    def test_handoffs_are_reconciled_without_catalog_duplicates(self):
        baseline = read_json(AUDIT / "baseline" / "summary.json")
        self.assertEqual(baseline["matching_catalog_profiles"], [])
        self.assertEqual(baseline["uruguay_handoff_count"], 3)
        self.assertEqual(self.coverage["handoff_reconciliation"]["missing"], [])

    def test_review_gate_blocks_freeze(self):
        self.assertEqual(self.request["status"], "pending_independent_review")
        self.assertFalse(self.request["freeze_allowed"])
        self.assertEqual(
            self.request["proposed_freeze"]["eligible"],
            ["ar-beta-impacto", "ar-primary-x", "br-saasholic"],
        )
        self.assertEqual(self.request["proposed_freeze"]["localized_profile_count"], 9)
        self.assertEqual(self.manifest["status"], "awaiting_independent_review")
        self.assertFalse(self.manifest["freeze_allowed"])

    def test_independent_review_authorizes_exact_batch(self):
        review = read_json(AUDIT / "review.json")
        freeze = read_json(AUDIT / "freeze-manifest.json")
        expected = ["ar-beta-impacto", "ar-primary-x", "br-saasholic"]
        self.assertEqual(review["status"], "approved")
        self.assertTrue(review["review_reconciled"])
        self.assertTrue(review["publication_authorized"])
        self.assertEqual(review["critical_open"], 0)
        self.assertEqual(review["high_open"], 0)
        self.assertEqual(review["eligible_reviewed"], expected)
        self.assertEqual(freeze["status"], "frozen")
        self.assertTrue(freeze["review_reconciled"])
        self.assertEqual(freeze["eligible_ids"], expected)
        self.assertEqual(freeze["localized_profile_count"], 9)
        self.assertIn("machine-readable", freeze["beta_impacto_limitation"])

    def test_freeze_manifest_hashes(self):
        freeze = read_json(AUDIT / "freeze-manifest.json")
        for relative, expected in freeze["artifact_hashes"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)

    def test_publication_matches_frozen_batch(self):
        freeze = read_json(AUDIT / "freeze-manifest.json")
        publication = read_json(AUDIT / "publication-report.json")
        self.assertEqual(publication["status"], "published")
        self.assertEqual(publication["eligible_ids"], freeze["eligible_ids"])
        self.assertEqual(publication["canonical_profile_count"], 3)
        self.assertEqual(publication["localized_profile_count"], 9)
        self.assertTrue(publication["review_reconciled"])
        self.assertEqual(publication["critical_open"], 0)
        self.assertEqual(publication["high_open"], 0)

    def test_publication_hashes_and_locales(self):
        publication = read_json(AUDIT / "publication-report.json")
        self.assertEqual(len(publication["profile_hashes"]), 9)
        for relative, expected in publication["profile_hashes"].items():
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        canonical = [
            read_json_frontmatter(ROOT / "funds" / "argentina" / "beta-impacto.md"),
            read_json_frontmatter(ROOT / "funds" / "argentina" / "primary-x.md"),
            read_json_frontmatter(ROOT / "funds" / "brazil" / "saasholic.md"),
        ]
        self.assertEqual([row["locale"] for row in canonical], ["en", "en", "en"])
        self.assertEqual(
            [row["base_geography"]["code"] for row in canonical],
            ["AR", "AR", "BR"],
        )

    def test_manifest_hashes(self):
        for relative, expected in self.manifest["artifact_hashes"].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)

    def test_no_mojibake(self):
        bad = ["Ãƒ", "Ã‚", "ï¿½", "^G", "�"]
        for path in AUDIT.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".md", ".json", ".jsonl"}:
                text = path.read_text(encoding="utf-8")
                self.assertFalse(any(token in text for token in bad), path)


if __name__ == "__main__":
    unittest.main()
