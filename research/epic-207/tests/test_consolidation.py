from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


EPIC_ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = EPIC_ROOT / "brazil" / "build_consolidated.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "epic_207_consolidation", BUILD_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ConsolidationBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.artifacts = cls.builder.build_artifacts()
        cls.candidates = [
            json.loads(line)
            for line in cls.artifacts["candidates.jsonl"]
            .decode("utf-8")
            .splitlines()
        ]
        cls.sources = [
            json.loads(line)
            for line in cls.artifacts["source-inventory.jsonl"]
            .decode("utf-8")
            .splitlines()
        ]
        cls.evidence = [
            json.loads(line)
            for line in cls.artifacts["evidence.jsonl"]
            .decode("utf-8")
            .splitlines()
        ]
        cls.identities = [
            json.loads(line)
            for line in cls.artifacts["identity-resolution.jsonl"]
            .decode("utf-8")
            .splitlines()
        ]
        cls.coverage = [
            json.loads(line)
            for line in cls.artifacts["coverage-matrix.jsonl"]
            .decode("utf-8")
            .splitlines()
        ]

    def test_raw_records_and_third_party_evidence_are_preserved(self) -> None:
        self.assertEqual(82, len(self.sources))
        self.assertEqual(51, len(self.candidates))
        self.assertEqual(69, len(self.evidence))
        self.assertEqual(
            {"complete": 75, "partial": 6, "unavailable": 1},
            dict(Counter(record["result"] for record in self.sources)),
        )
        self.assertEqual(
            {"official": 42, "third_party": 27},
            dict(Counter(record["source_class"] for record in self.evidence)),
        )
        self.assertTrue(
            all(record["decision"] is None for record in self.candidates)
        )
        candidate_ids = {
            record["candidate_id"] for record in self.candidates
        }
        self.assertEqual(51, len(candidate_ids))
        self.assertTrue(
            all(
                record["candidate_id"] in candidate_ids
                for record in self.evidence
            )
        )
        official_ids = {
            record["evidence_id"]
            for record in self.evidence
            if record["source_class"] == "official"
        }
        self.assertTrue(
            all(
                set(candidate["official_evidence_ids"]) <= official_ids
                for candidate in self.candidates
            )
        )

    def test_frozen_profiles_are_ignored_but_unknown_additions_fail(self) -> None:
        guards = set(self.builder.POST_BASELINE_GUARDS)
        frozen = self.builder.frozen_publication_paths()
        baseline = {"funds/brazil/existing.md"}
        current = baseline | guards | frozen

        self.assertEqual(27, len(frozen))
        self.assertEqual(
            guards,
            self.builder.guarded_catalog_delta_paths(
                baseline,
                current,
                frozen,
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "delta pós-baseline inesperado",
        ):
            self.builder.guarded_catalog_delta_paths(
                baseline,
                current | {"funds/brazil/not-frozen.md"},
                frozen,
            )

    def test_exact_duplicates_have_canonical_destinations(self) -> None:
        candidates = {
            record["candidate_id"]: record for record in self.candidates
        }
        self.assertEqual(
            "fund-br-210-canary",
            candidates["fund-br-213-canary"]["canonical_candidate_id"],
        )
        self.assertEqual(
            "fund-br-sororite-ventures",
            candidates["fund-br-213-sororite-ventures"][
                "canonical_candidate_id"
            ],
        )
        resolution_subjects = {
            tuple(record["subject_ids"]): record
            for record in self.identities
        }
        self.assertIn(
            ("fund-br-210-canary", "fund-br-213-canary"),
            resolution_subjects,
        )
        self.builder._assert_known_internal_collisions(self.candidates)
        self.assertIn(
            (
                "fund-br-213-sororite-ventures",
                "fund-br-sororite-ventures",
            ),
            resolution_subjects,
        )

    def test_known_ambiguous_identity_clusters_are_explicit(self) -> None:
        resolution_ids = {
            record["resolution_id"] for record in self.identities
        }
        expected = {
            "identity-fund-br-dna-capital-manager-vehicle",
            "identity-fund-br-vinci-prior-managers",
            "identity-fund-br-primus-sul-ventures",
            "identity-fund-br-nido-brand",
            "identity-fund-br-nido-platypus",
            "identity-fund-br-jatoba-brand",
            "identity-fund-br-jatoba-impacto-amazonia-vehicle",
            "identity-fund-br-lh-tech-ventures",
            "identity-fund-br-accion-venture-lab",
            "identity-fund-br-prosus-naspers",
        }
        self.assertTrue(expected <= resolution_ids)

    def test_coverage_has_unique_family_geography_cells(self) -> None:
        keys = [
            (record["source_family"], record["geography_scope"])
            for record in self.coverage
        ]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn(
            ("official_portfolios", "foreign_access_brazil"), keys
        )
        official = next(
            record
            for record in self.coverage
            if (
                record["source_family"],
                record["geography_scope"],
            )
            == ("official_portfolios", "foreign_access_brazil")
        )
        self.assertEqual(
            [
                "src-fund-br-215-pass1-quona-portfolio",
                "src-fund-br-215-pass2-prosus-ventures",
            ],
            official["source_ids"],
        )
        covered_sources = {
            source_id
            for record in self.coverage
            for source_id in record["source_ids"]
        }
        self.assertEqual(
            {record["source_id"] for record in self.sources},
            covered_sources,
        )

    def test_validation_shards_partition_all_candidates_stably(self) -> None:
        manifest = json.loads(
            self.artifacts["validation-shards/manifest.json"].decode("utf-8")
        )
        self.assertEqual(
            {0: 17, 1: 19, 2: 15},
            {
                queue["modulo"]: queue["candidate_count"]
                for queue in manifest["queues"]
            },
        )
        assigned = [
            candidate_id
            for queue in manifest["queues"]
            for candidate_id in queue["candidate_ids"]
        ]
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(
            {record["candidate_id"] for record in self.candidates},
            set(assigned),
        )
        for queue in manifest["queues"]:
            self.assertTrue(
                all(
                    self.builder.assignment_modulo(candidate_id)
                    == queue["modulo"]
                    for candidate_id in queue["candidate_ids"]
                )
            )

    def test_post_baseline_profiles_are_guarded_not_republished(self) -> None:
        summary = json.loads(
            self.artifacts["consolidation-summary.json"].decode("utf-8")
        )
        delta = summary["post_baseline_catalog_delta"]
        self.assertEqual(
            {"Entrypoint", "Flourish Ventures"},
            {record["name"] for record in delta},
        )
        self.assertTrue(
            all(
                not record["candidate_created"]
                and not record["included_in_validation_shards"]
                for record in delta
            )
        )
        candidate_names = {record["name"] for record in self.candidates}
        self.assertFalse(
            {"Entrypoint", "Flourish Ventures"} & candidate_names
        )
        self.assertEqual(
            {"candidate_rows": 10, "unique_profiles": 9},
            {
                key: summary["baseline_profile_matches"][key]
                for key in ("candidate_rows", "unique_profiles")
            },
        )

    def test_foreign_access_rediscoveries_are_linked_to_existing_ids(self) -> None:
        candidates = {
            record["candidate_id"]: record for record in self.candidates
        }
        for candidate_id, source_ids in (
            self.builder.REDISCOVERY_SOURCE_LINKS.items()
        ):
            self.assertTrue(
                set(source_ids)
                <= set(candidates[candidate_id]["discovery_source_ids"])
            )

    def test_build_is_byte_deterministic(self) -> None:
        rebuilt = self.builder.build_artifacts()
        self.assertEqual(self.artifacts, rebuilt)

    def test_declared_hashes_match_every_generated_queue_and_core_file(
        self,
    ) -> None:
        manifest = json.loads(
            self.artifacts["validation-shards/manifest.json"].decode("utf-8")
        )
        for queue in manifest["queues"]:
            relative = queue["artifact"].removeprefix(
                "research/epic-207/brazil/"
            )
            self.assertEqual(
                queue["sha256"],
                self.builder.sha256(self.artifacts[relative]),
            )
        run = json.loads(
            self.artifacts["run-manifest.jsonl"]
            .decode("utf-8")
            .splitlines()[0]
        )
        self.assertEqual(
            {
                filename: self.builder.sha256(self.artifacts[filename])
                for filename in self.builder.CORE_JSONL
            },
            run["artifact_hashes"],
        )


if __name__ == "__main__":
    unittest.main()
