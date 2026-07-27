from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "southern-cone"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class SouthernConeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.candidates = read_jsonl(ROOT / "candidates.jsonl")
        cls.evidence = read_jsonl(ROOT / "evidence.jsonl")
        cls.sources = read_jsonl(ROOT / "source-inventory.jsonl")

    def test_all_candidates_have_a_decision_and_no_profile_was_published(self) -> None:
        self.assertEqual(11, len(self.candidates))
        self.assertTrue(all(item["decision"] for item in self.candidates))
        self.assertFalse(any(item["status"] == "publicado" for item in self.candidates))
        self.assertEqual(
            Counter(
                {
                    "elegível": 2,
                    "evidência-insuficiente": 5,
                    "duplicado": 1,
                    "encaminhado-para-plataformas": 2,
                    "encaminhado-para-programas-públicos": 1,
                }
            ),
            Counter(item["decision"] for item in self.candidates),
        )

    def test_eligible_networks_separate_actors_and_have_dated_official_activity(self) -> None:
        evidence_by_id = {item["evidence_id"]: item for item in self.evidence}
        eligible = [item for item in self.candidates if item["decision"] == "elegível"]
        for item in eligible:
            self.assertTrue(item["recurring_selection"])
            self.assertIn(item["external_access"], {"aberto", "explícito-américa-latina"})
            self.assertIsNotNone(item["application_route"])
            self.assertNotEqual(item["selection_actors"], item["decision_actors"])
            self.assertTrue(item["capital_actors"])
            dated = [
                evidence_by_id[evidence_id]
                for evidence_id in item["official_evidence_ids"]
                if evidence_by_id[evidence_id]["published_on"]
                == item["activity_evidence_date"]
            ]
            self.assertTrue(dated)
            self.assertTrue(all(row["source_type"] == "oficial" for row in dated))

    def test_mar_del_plata_is_a_direct_alias_of_bac(self) -> None:
        by_id = {item["network_id"]: item for item in self.candidates}
        chapter = by_id["ang-businessangelsclub-org--mar-del-plata"]
        self.assertEqual("capítulo", chapter["entity_type"])
        self.assertEqual("alias", chapter["chapter_identity"])
        self.assertEqual("duplicado", chapter["decision"])
        self.assertEqual(
            "ang-businessangelsclub-org",
            chapter["canonical_network_id"],
        )
        self.assertNotEqual(
            "alias",
            by_id[chapter["canonical_network_id"]]["chapter_identity"],
        )

    def test_boundary_routes_do_not_collide_with_angel_profiles(self) -> None:
        routed = [
            item
            for item in self.candidates
            if item["decision"].startswith("encaminhado-")
        ]
        self.assertEqual(3, len(routed))
        self.assertTrue(all(item["canonical_profile"] for item in routed))
        self.assertTrue(
            all(
                item["canonical_profile"].startswith("ecosystem/")
                for item in routed
            )
        )

    def test_country_shards_are_exclusive_and_reduce_to_canonical(self) -> None:
        shard_ids: set[str] = set()
        for country in ("argentina", "chile", "paraguai", "uruguai"):
            rows = read_jsonl(
                ROOT / "shards" / f"worker-{country}" / "candidates.jsonl"
            )
            ids = {item["network_id"] for item in rows}
            self.assertFalse(shard_ids & ids)
            shard_ids |= ids
        self.assertEqual(
            {item["network_id"] for item in self.candidates},
            shard_ids,
        )

    def test_all_inventory_sources_are_official_and_country_owned(self) -> None:
        self.assertEqual(16, len(self.sources))
        self.assertEqual(
            {"Argentina", "Chile", "Paraguai", "Uruguai"},
            {item["geography"] for item in self.sources},
        )
        self.assertFalse(any(item["result"] == "indisponível" for item in self.sources))


if __name__ == "__main__":
    unittest.main()
