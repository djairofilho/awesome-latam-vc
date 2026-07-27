from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from research.epic_62_independent_review import verify_review


class IndependentReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.review = Path(self.temp_dir.name) / "review"
        shutil.copytree(verify_review.REVIEW, self.review)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_complete_review_passes(self) -> None:
        self.assertEqual([], verify_review.validate(self.review))

    def test_missing_required_candidate_fails(self) -> None:
        path = self.review / "review-results.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(
            json.dumps(rows[1:], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_review.validate(self.review)
        self.assertTrue(any("sem revisão" in error for error in errors))

    def test_tampered_excluded_sample_fails(self) -> None:
        path = self.review / "review-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["excluded_sample"]["selected"][0]["candidate_id"] = "accel-invalid"
        path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_review.validate(self.review)
        self.assertIn("amostra determinística de excluídos divergente", errors)

    def test_tampered_source_hash_fails(self) -> None:
        path = self.review / "review-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["source_hashes"]["candidates.jsonl"] = "0" * 64
        path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_review.validate(self.review)
        self.assertIn("hash de entrada inválido: candidates.jsonl", errors)

    def test_eligible_requires_all_official_claims(self) -> None:
        path = self.review / "review-results.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        eligible = next(row for row in rows if row["resolved_decision"] == "elegível")
        eligible["official_evidence_ids"] = []
        path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        errors = verify_review.validate(self.review)
        self.assertTrue(any("nenhuma evidência oficial" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
