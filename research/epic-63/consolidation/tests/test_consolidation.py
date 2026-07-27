from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[2]
ROUTED = {
    "encaminhado-para-funds",
    "encaminhado-para-aceleradoras",
    "encaminhado-para-plataformas",
    "encaminhado-para-programas-públicos",
}
GENERATED = (
    "INDEPENDENT_REVIEW.md",
    "README.md",
    "candidates.jsonl",
    "category-resolutions.json",
    "consolidation-manifest.json",
    "coverage-matrix.jsonl",
    "evidence.jsonl",
    "identity-resolutions.json",
    "independent-review.jsonl",
    "provenance.jsonl",
    "publication-queue.jsonl",
    "review-divergences.json",
    "run-manifest.jsonl",
    "sha256sums.txt",
    "source-inventory.jsonl",
)


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AngelConsolidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = read_jsonl(ROOT / "candidates.jsonl")
        cls.evidence = read_jsonl(ROOT / "evidence.jsonl")
        cls.sources = read_jsonl(ROOT / "source-inventory.jsonl")
        cls.coverage = read_jsonl(ROOT / "coverage-matrix.jsonl")
        cls.queue = read_jsonl(ROOT / "publication-queue.jsonl")
        cls.provenance = read_jsonl(ROOT / "provenance.jsonl")
        cls.reviews = read_jsonl(ROOT / "independent-review.jsonl")
        cls.category = json.loads(
            (ROOT / "category-resolutions.json").read_text(encoding="utf-8")
        )
        cls.identities = json.loads(
            (ROOT / "identity-resolutions.json").read_text(encoding="utf-8")
        )
        cls.manifest = json.loads(
            (ROOT / "consolidation-manifest.json").read_text(encoding="utf-8")
        )

    def test_input_inventory_is_frozen(self) -> None:
        inventory = json.loads(
            (ROOT / "input-inventory.json").read_text(encoding="utf-8")
        )
        self.assertEqual(25, len(inventory["inputs"]))
        for relative, expected in inventory["inputs"].items():
            self.assertEqual(expected, sha256(REPOSITORY / relative), relative)

    def test_before_after_counts_are_exact(self) -> None:
        self.assertEqual(44, self.manifest["before_occurrences"])
        self.assertEqual(
            {
                "candidates": 44,
                "coverage_rows": 42,
                "evidence": 57,
                "publication_queue": 11,
                "sources": 61,
            },
            self.manifest["after_counts"],
        )
        self.assertEqual(0, self.manifest["merged_duplicate_occurrences"])

    def test_every_candidate_has_one_unique_id_and_decision(self) -> None:
        ids = [item["network_id"] for item in self.candidates]
        self.assertEqual(44, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["decision"] for item in self.candidates))

    def test_candidate_references_are_not_orphaned(self) -> None:
        candidate_ids = {item["network_id"] for item in self.candidates}
        evidence_ids = {item["evidence_id"] for item in self.evidence}
        source_ids = {item["source_id"] for item in self.sources}
        for item in self.candidates:
            self.assertLessEqual(set(item["official_evidence_ids"]), evidence_ids)
            self.assertLessEqual(set(item["discovery_source_ids"]), source_ids)
            for field in ("parent_network_id", "canonical_network_id"):
                if item[field]:
                    self.assertIn(item[field], candidate_ids)

    def test_evidence_and_coverage_references_are_not_orphaned(self) -> None:
        candidate_ids = {item["network_id"] for item in self.candidates}
        source_ids = {item["source_id"] for item in self.sources}
        self.assertTrue(
            all(item["network_id"] in candidate_ids for item in self.evidence)
        )
        for item in self.coverage:
            self.assertLessEqual(set(item["source_ids"]), source_ids)

    def test_provenance_covers_every_candidate_once(self) -> None:
        self.assertEqual(
            {item["network_id"] for item in self.candidates},
            {item["network_id"] for item in self.provenance},
        )
        self.assertEqual(
            {"issue-81", "issue-82", "issue-83", "issue-84", "issue-85"},
            {item["source_audit"] for item in self.provenance},
        )

    def test_known_duplicates_have_direct_destinations(self) -> None:
        duplicates = {
            item["network_id"]: item
            for item in self.candidates
            if item["decision"] == "duplicado"
        }
        self.assertEqual(
            {
                "ang-mulheresinvestidoras-net",
                "ang-businessangelsclub-org--mar-del-plata",
            },
            set(duplicates),
        )
        candidate_ids = {item["network_id"] for item in self.candidates}
        for item in duplicates.values():
            target = item["canonical_network_id"]
            self.assertIn(target, candidate_ids)
            self.assertNotEqual("alias", next(
                row["chapter_identity"]
                for row in self.candidates
                if row["network_id"] == target
            ))

    def test_all_identity_collisions_are_explicit(self) -> None:
        resolutions = self.identities["resolutions"]
        self.assertEqual(7, len(resolutions))
        candidate_ids = {item["network_id"] for item in self.candidates}
        for item in resolutions:
            self.assertLessEqual(set(item["subject_ids"]), candidate_ids)
        self.assertEqual(
            len(resolutions),
            len({item["resolution_id"] for item in resolutions}),
        )

    def test_every_transfer_has_target_id_and_destination(self) -> None:
        transfers = self.category["outgoing_category_resolutions"]
        routed_ids = {
            item["network_id"]
            for item in self.candidates
            if item["decision"] in ROUTED
        }
        self.assertEqual(12, len(transfers))
        self.assertEqual(
            routed_ids,
            {item["source_network_id"] for item in transfers},
        )
        self.assertTrue(
            all(item["target_id"] and item["canonical_destination"] for item in transfers)
        )

    def test_baseline_incoming_profiles_are_materialized(self) -> None:
        incoming = self.category["incoming_baseline_profiles"]
        self.assertEqual(5, len(incoming))
        for item in incoming:
            self.assertTrue(item["materialized"])
            self.assertTrue((REPOSITORY / item["canonical_profile"]).is_file())

    def test_publication_queue_equals_eligible_set(self) -> None:
        eligible = {
            item["network_id"]
            for item in self.candidates
            if item["decision"] == "elegível"
        }
        queued = {item["network_id"] for item in self.queue}
        self.assertEqual(eligible, queued)
        self.assertEqual(
            Counter({"pending-publication": 6, "already-published": 5}),
            Counter(item["publication_status"] for item in self.queue),
        )
        for item in self.queue:
            path = REPOSITORY / item["canonical_profile"]
            if item["publication_status"] == "already-published":
                self.assertTrue(path.is_file())
            else:
                self.assertFalse(path.exists())

    def test_every_eligible_has_official_contract_evidence(self) -> None:
        evidence = {item["evidence_id"]: item for item in self.evidence}
        for item in self.candidates:
            if item["decision"] != "elegível":
                continue
            claims = {
                claim["field"]
                for evidence_id in item["official_evidence_ids"]
                for record in [evidence[evidence_id]]
                if record["source_type"] == "oficial"
                for claim in record["claims"]
                if claim["finding"] == "confirmado"
            }
            self.assertLessEqual(
                {"categoria", "atividade", "acesso externo"},
                claims,
            )
            self.assertTrue(item["selection_actors"])
            self.assertTrue(item["decision_actors"])
            self.assertTrue(item["capital_actors"])

    def test_review_covers_mandatory_scope_and_deterministic_sample(self) -> None:
        reviewed = {item["subject_id"] for item in self.reviews}
        original = {
            item["network_id"]: item["original_decision"] for item in self.provenance
        }
        mandatory = {
            item["network_id"]
            for item in self.candidates
            if original[item["network_id"]] == "elegível"
            or original[item["network_id"]] in ROUTED
            or original[item["network_id"]] in {"evidência-insuficiente", "duplicado"}
            or item["network_id"] in {"ang-brangels-global", "ang-theboardperu-com"}
        }
        self.assertLessEqual(mandatory, reviewed)
        remaining = [
            item["network_id"]
            for item in self.candidates
            if item["network_id"] not in mandatory
        ]
        expected_size = math.ceil(len(remaining) * 0.20)
        expected = sorted(
            remaining,
            key=lambda value: (hashlib.sha256(value.encode()).hexdigest(), value),
        )[:expected_size]
        sampled = sorted(
            item["subject_id"]
            for item in self.reviews
            if item["review_group"] == "deterministic-sample"
        )
        self.assertEqual(expected, sampled)
        self.assertEqual(42, len(self.reviews))

    def test_independent_review_is_separate_and_resolved(self) -> None:
        self.assertTrue(
            all(
                item["reviewer"] == "independent-reviewer-final-issue-86"
                for item in self.reviews
            )
        )
        self.assertTrue(all(item["resolved"] for item in self.reviews))
        self.assertEqual("complete", self.manifest["independent_review_status"])
        self.assertEqual(0, self.manifest["unresolved_high_divergences"])
        self.assertEqual(1, self.manifest["resolved_high_divergences"])
        pad = next(
            item
            for item in self.reviews
            if item["subject_id"] == "ang-hub-udep-pe--pad"
        )
        self.assertEqual("elegível", pad["original_decision"])
        self.assertEqual("evidência-insuficiente", pad["final_decision"])
        divergences = json.loads(
            (ROOT / "review-divergences.json").read_text(encoding="utf-8")
        )
        self.assertEqual(0, divergences["open_high_divergences"])
        self.assertEqual(2, len(divergences["divergences"]))

    def test_manifest_output_hashes_are_frozen(self) -> None:
        for name, expected in self.manifest["output_hashes"].items():
            self.assertEqual(expected, sha256(ROOT / name), name)
        self.assertEqual("frozen", self.manifest["status"])

    def test_sha256sums_match_every_frozen_artifact(self) -> None:
        rows = [
            line.split("  ", 1)
            for line in (ROOT / "sha256sums.txt").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        self.assertEqual(15, len(rows))
        for expected, name in rows:
            self.assertEqual(expected, sha256(ROOT / name), name)

    def test_final_run_manifest_has_only_done_tasks(self) -> None:
        rows = read_jsonl(ROOT / "run-manifest.jsonl")
        self.assertEqual("run", rows[0]["record_type"])
        self.assertEqual("concluída", rows[0]["status"])
        self.assertEqual(rows[0]["task_count"], len(rows) - 1)
        self.assertTrue(all(item["status"] == "done" for item in rows[1:]))

    def test_generator_and_reviewer_are_idempotent(self) -> None:
        before = {name: sha256(ROOT / name) for name in GENERATED}
        for _ in range(2):
            subprocess.run(
                [sys.executable, str(ROOT / "build_registry.py")],
                cwd=REPOSITORY,
                check=True,
            )
            subprocess.run(
                [sys.executable, str(ROOT / "independent_review.py")],
                cwd=REPOSITORY,
                check=True,
            )
            after = {name: sha256(ROOT / name) for name in GENERATED}
            self.assertEqual(before, after)

    def test_utf8_has_no_mojibake(self) -> None:
        bad = ("\u00c3", "\u00c2", "\ufffd", chr(94) + "G")
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {
                ".json",
                ".jsonl",
                ".md",
                ".py",
                ".txt",
            }:
                text = path.read_text(encoding="utf-8")
                self.assertFalse(
                    any(token in text for token in bad),
                    str(path),
                )


if __name__ == "__main__":
    unittest.main()
