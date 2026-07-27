from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
PUBLICATION = ROOT / "research/epic-62/publication"
REVIEW = ROOT / "research/epic-62/independent-review"
CONSOLIDATION = ROOT / "research/epic-62/consolidation"
SOURCE_MANIFEST = REVIEW / "publishable-manifest.json"
EXPECTED_SOURCE_HASH = (
    "52da16cfc931aa3c1a1304dbee575a7b805e0db03ca2f96a75e5f4c79604adc2"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def profile_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace(
        "\r",
        "\n",
    )
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        closing_index = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
        text = "".join(lines[closing_index + 1 :]).lstrip("\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frozen_hash(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if (
        relative.startswith("ecosystem/accelerators/")
        and path.name != "README.md"
    ):
        return profile_sha256(path)
    return stable_sha256(path)


def jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        cls.batches = json.loads(
            (PUBLICATION / "frozen-batches.json").read_text(encoding="utf-8")
        )
        cls.manifest = json.loads(
            (PUBLICATION / "publication-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        cls.reviews = {
            row["candidate_id"]: row
            for row in json.loads(
                (REVIEW / "review-results.json").read_text(encoding="utf-8")
            )
        }
        cls.candidates = {
            row["candidate_id"]: row
            for row in jsonl(CONSOLIDATION / "candidates.jsonl")
        }

    def test_source_manifest_is_the_exact_frozen_queue(self) -> None:
        self.assertEqual(EXPECTED_SOURCE_HASH, sha256(SOURCE_MANIFEST))
        self.assertEqual(26, self.source["candidate_count"])
        self.assertEqual(26, len(self.source["candidate_ids"]))
        self.assertEqual(
            sorted(self.source["candidate_ids"]),
            self.source["candidate_ids"],
        )

    def test_batches_are_complete_small_and_deterministic(self) -> None:
        batches = self.batches["batches"]
        self.assertEqual(3, len(batches))
        self.assertEqual([10, 10, 6], [row["profile_count"] for row in batches])
        ids = [item for batch in batches for item in batch["candidate_ids"]]
        self.assertEqual(self.source["candidate_ids"], ids)
        self.assertEqual(len(ids), len(set(ids)))
        for batch in batches:
            self.assertEqual("djairofilho", batch["owner"])
            self.assertEqual(
                "agent/issue-78-accelerators-publication",
                batch["branch"],
            )
            self.assertGreater(batch["sub_issue"], 0)
            self.assertEqual(
                stable_sha256(ROOT / batch["body_path"]),
                batch["body_sha256"],
            )

    def test_exactly_the_frozen_eligible_profiles_are_published(self) -> None:
        profiles = self.manifest["profiles"]
        ids = [row["candidate_id"] for row in profiles]
        self.assertEqual(self.source["candidate_ids"], ids)
        self.assertEqual(26, self.manifest["profiles_created"])
        self.assertEqual(26, len({row["profile_path"] for row in profiles}))
        self.assertTrue(
            all(self.reviews[item]["resolved_decision"] == "elegível" for item in ids)
        )
        rejected = {
            item
            for item, review in self.reviews.items()
            if review["resolved_decision"] != "elegível"
        }
        self.assertTrue(rejected.isdisjoint(ids))

    def test_no_profile_exists_outside_the_queue(self) -> None:
        actual = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "ecosystem/accelerators").glob("*/*.md")
        }
        expected = {row["profile_path"] for row in self.manifest["profiles"]}
        self.assertEqual(expected, actual)

    def test_aliases_and_program_vehicle_relations_are_preserved(self) -> None:
        for profile in self.manifest["profiles"]:
            candidate = self.candidates[profile["candidate_id"]]
            self.assertEqual(candidate["aliases"], profile["aliases"])
            self.assertEqual(
                candidate.get("investment_vehicle_id"),
                profile["investment_vehicle_id"],
            )
            text = (ROOT / profile["profile_path"]).read_text(encoding="utf-8")
            aliases = ", ".join(candidate["aliases"]) or "None published"
            self.assertIn(f"- **Aliases:** {aliases}", text)
            if candidate.get("investment_vehicle_id"):
                self.assertIn(candidate["investment_vehicle_id"], text)
            relationships = self.reviews[profile["candidate_id"]].get(
                "catalog_relationships", []
            )
            for relationship in relationships:
                destination = relationship.get("destination")
                if destination and relationship.get("catalog") == "funds":
                    self.assertIn(destination, text)

    def test_all_evidence_references_resolve_to_official_sources(self) -> None:
        evidence = {
            row["evidence_id"]: row
            for row in jsonl(CONSOLIDATION / "evidence.jsonl")
        }
        evidence.update(
            {
                row["evidence_id"]: row
                for row in json.loads(
                    (REVIEW / "review-evidence.json").read_text(encoding="utf-8")
                )
            }
        )
        for profile in self.manifest["profiles"]:
            ids = profile["official_evidence_ids"]
            self.assertTrue(ids)
            self.assertTrue(all(item in evidence for item in ids))
            self.assertTrue(all(evidence[item]["source_type"] == "official" for item in ids))

    def test_index_has_every_profile_once_and_all_links_resolve(self) -> None:
        index = ROOT / "ecosystem/accelerators/README.md"
        text = index.read_text(encoding="utf-8")
        links = re.findall(r"^- \[[^\]]+\]\(([^)]+\.md)\)$", text, re.MULTILINE)
        expected = {
            str(Path(row["profile_path"]).relative_to("ecosystem/accelerators"))
            .replace("\\", "/")
            for row in self.manifest["profiles"]
        }
        self.assertEqual(26, len(links))
        self.assertEqual(expected, set(links))
        self.assertEqual(len(links), len(set(links)))
        for link in links:
            self.assertTrue((index.parent / link).is_file(), link)

    def test_multilingual_catalog_links_resolve(self) -> None:
        expected_target = "ecosystem/accelerators/README.md"
        for relative in (
            "README.md",
            "README.pt.md",
            "README.es.md",
            "ecosystem/README.md",
        ):
            path = ROOT / relative
            text = path.read_text(encoding="utf-8")
            targets = re.findall(r"!?\[[^\]]*\]\(([^)#]+)", text)
            resolved = {
                (path.parent / target).resolve()
                for target in targets
                if not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I)
            }
            self.assertIn((ROOT / expected_target).resolve(), resolved)

    def test_manifest_and_checksum_hashes_match_files(self) -> None:
        for relative, expected in self.manifest["output_hashes"].items():
            self.assertEqual(expected, frozen_hash(ROOT / relative), relative)
        for line in (PUBLICATION / "sha256sums.txt").read_text(
            encoding="utf-8"
        ).splitlines():
            expected, relative = line.split("  ", 1)
            self.assertEqual(expected, frozen_hash(ROOT / relative), relative)

    def test_generation_is_idempotent(self) -> None:
        tracked = [
            ROOT / relative
            for relative in self.manifest["output_hashes"]
        ] + [
            PUBLICATION / "publication-manifest.json",
            PUBLICATION / "sha256sums.txt",
        ]
        before = {path: frozen_hash(path) for path in tracked}
        subprocess.run(
            [sys.executable, str(PUBLICATION / "build_publication.py")],
            cwd=ROOT,
            check=True,
        )
        after = {path: frozen_hash(path) for path in tracked}
        self.assertEqual(before, after)

    def test_utf8_has_no_mojibake_markers(self) -> None:
        paths = [
            ROOT / row["profile_path"] for row in self.manifest["profiles"]
        ] + list(PUBLICATION.rglob("*.md")) + list(PUBLICATION.rglob("*.json"))
        markers = ("\u00c3", "\u00c2", "\ufffd", "\x07", "\\`")
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertFalse(any(marker in text for marker in markers), path)

    def test_ventiur_reopened_decision_is_published(self) -> None:
        candidate_id = "accel-ventiur-acelera-impacto"
        self.assertEqual(
            "elegível",
            self.reviews[candidate_id]["resolved_decision"],
        )
        profile = next(
            row
            for row in self.manifest["profiles"]
            if row["candidate_id"] == candidate_id
        )
        self.assertIn(
            "ev-accel-review-ventiur-calendar",
            profile["official_evidence_ids"],
        )
        text = (ROOT / profile["profile_path"]).read_text(encoding="utf-8")
        self.assertIn("official 2025 selection", text)


if __name__ == "__main__":
    unittest.main()
