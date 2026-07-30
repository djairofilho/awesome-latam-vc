import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "research/epic-250/colombia"


def jsonl(name):
    return [json.loads(line) for line in (AUDIT / name).read_text(encoding="utf-8").splitlines() if line]


class ColombiaAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(AUDIT / "build.py")], check=True)

    def test_all_discovery_is_non_regulatory(self):
        rows = jsonl("candidates.jsonl")
        self.assertTrue(rows)
        self.assertTrue(all(row["discovery_origin"] == "non_regulatory" for row in rows))

    def test_regulator_is_selective(self):
        rows = jsonl("candidates.jsonl")
        regulatory = [row for row in jsonl("source-inventory.jsonl") if row["family"] == "regulator_identity"]
        self.assertLessEqual(100 * len(regulatory) / len(rows), 10)
        self.assertEqual(["src-sec-h20-identity"], [row["source_id"] for row in regulatory])

    def test_every_candidate_has_terminal_decision(self):
        allowed = {"eligible", "insufficient_evidence", "routed", "duplicate"}
        self.assertTrue(all(row["decision"] in allowed for row in jsonl("candidates.jsonl")))

    def test_publication_is_exact_and_bounded(self):
        manifest = json.loads((AUDIT / "publication/publication-manifest.json").read_text(encoding="utf-8"))
        profiles = [profile for batch in manifest["batches"] for profile in batch["profiles"]]
        self.assertEqual(manifest["eligible_count"], len(profiles))
        self.assertEqual(len(profiles), len(set(profiles)))
        self.assertTrue(all(len(batch["profiles"]) <= 10 for batch in manifest["batches"]))
        for profile in profiles:
            for prefix in ["", "translations/pt-BR/", "translations/es/"]:
                self.assertTrue((ROOT / f"{prefix}{profile}").is_file())

    def test_integrated_baseline_entries_are_deduplicated(self):
        rows = {row["candidate_id"]: row for row in jsonl("candidates.jsonl")}
        self.assertEqual("duplicate", rows["co-entrypoint"]["decision"])
        self.assertEqual("funds/brazil/entrypoint.md", rows["co-entrypoint"]["canonical_destination"])
        self.assertEqual("duplicate", rows["co-flourish-ventures"]["decision"])
        self.assertEqual("funds/multi-country/flourish-ventures.md", rows["co-flourish-ventures"]["canonical_destination"])

    def test_no_mojibake_in_new_artifacts(self):
        bad = ("Ã", "Â", "�")
        paths = list(AUDIT.rglob("*.json")) + list(AUDIT.rglob("*.jsonl"))
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in bad), path)


if __name__ == "__main__":
    unittest.main()
