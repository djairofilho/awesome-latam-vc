from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
AUDIT_PATH = ROOT / "research/epic-65/final-audit/audit.py"
SPEC = importlib.util.spec_from_file_location("epic65_final_audit", AUDIT_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Não foi possível carregar {AUDIT_PATH}")
audit_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_module)


class FinalAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        shutil.copytree(
            ROOT / "research/epic-65",
            self.root / "research/epic-65",
        )
        shutil.copytree(
            ROOT / "research/epic-62/consolidation",
            self.root / "research/epic-62/consolidation",
        )
        shutil.copytree(
            ROOT / "ecosystem/public-programs",
            self.root / "ecosystem/public-programs",
        )
        for filename in ("README.md", "README.pt.md", "README.es.md"):
            shutil.copy2(ROOT / filename, self.root / filename)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def report(self) -> dict:
        return audit_module.audit(self.root)

    def assert_failed_check(self, report: dict, check_id: str) -> None:
        check = next(row for row in report["checks"] if row["check_id"] == check_id)
        self.assertEqual("failed", check["status"])

    def rewrite_jsonl(self, relative: str, mutate) -> None:
        path = self.root / relative
        rows = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        mutate(rows)
        path.write_text(
            "".join(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                for row in rows
            ),
            encoding="utf-8",
        )

    def test_complete_audit_passes_with_exact_metrics(self) -> None:
        report = self.report()
        self.assertEqual("passed", report["status"])
        self.assertEqual([], report["findings"])
        self.assertEqual(29, report["metrics"]["agencies"])
        self.assertEqual(45, report["metrics"]["programs"])
        self.assertEqual(21, report["metrics"]["calls"])
        self.assertEqual(95, report["metrics"]["entities_with_destination"])
        self.assertEqual(29, report["metrics"]["published_profiles"])
        self.assertEqual(0, report["metrics"]["call_profiles"])

    def test_audit_is_deterministic(self) -> None:
        first = self.report()
        second = self.report()
        self.assertEqual(first, second)
        self.assertEqual(
            audit_module.render_markdown(first),
            audit_module.render_markdown(second),
        )

    def test_missing_entity_decision_fails_destination_gate(self) -> None:
        self.rewrite_jsonl(
            "research/epic-65/consolidation/programs.jsonl",
            lambda rows: rows[0].update(decision=None),
        )
        self.assert_failed_check(self.report(), "entity-destinations")

    def test_orphan_relationship_fails(self) -> None:
        self.rewrite_jsonl(
            "research/epic-65/consolidation/calls.jsonl",
            lambda rows: rows[0].update(program_id="program-missing"),
        )
        self.assert_failed_check(self.report(), "relationships")

    def test_incomplete_task_fails_coverage_gate(self) -> None:
        def mutate(rows: list[dict]) -> None:
            task = next(row for row in rows if row["record_type"] == "task")
            task["status"] = "blocked"
            task["reason"] = "teste"
            task["next_action"] = "resolver"

        self.rewrite_jsonl(
            "research/epic-65/consolidation/run-manifest.jsonl",
            mutate,
        )
        self.assert_failed_check(self.report(), "coverage-and-tasks")

    def test_invalid_transfer_destination_fails(self) -> None:
        path = (
            self.root
            / "research/epic-65/consolidation/category-resolutions.json"
        )
        value = json.loads(path.read_text(encoding="utf-8"))
        value["outgoing_category_resolutions"][0][
            "canonical_destination"
        ] = "missing"
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.assert_failed_check(self.report(), "category-transfers")

    def test_nonofficial_evidence_fails_link_gate(self) -> None:
        self.rewrite_jsonl(
            "research/epic-65/consolidation/evidence.jsonl",
            lambda rows: rows[0].update(source_type="terceiro"),
        )
        self.assert_failed_check(self.report(), "official-links")

    def test_index_reordering_fails(self) -> None:
        path = self.root / "ecosystem/public-programs/README.md"
        text = path.read_text(encoding="utf-8")
        left = "| [Banco de Desarrollo Productivo](bolivia/bdp-bolivia.md)"
        right = "| [AgroInnovatec](bolivia/agroinnovatec.md)"
        text = text.replace(left, "__LEFT__", 1).replace(
            right, left, 1
        ).replace("__LEFT__", right, 1)
        path.write_text(text, encoding="utf-8")
        self.assert_failed_check(self.report(), "profiles-and-indexes")

    def test_tampered_profile_fails_hash_gate(self) -> None:
        path = self.root / "ecosystem/public-programs/chile/corfo.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nAlteração.\n",
            encoding="utf-8",
        )
        self.assert_failed_check(self.report(), "declared-hashes")

    def test_mojibake_fails_utf8_gate(self) -> None:
        path = self.root / "research/epic-65/README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nprogramaÃ§Ã£o\n",
            encoding="utf-8",
        )
        self.assert_failed_check(self.report(), "utf8-and-mojibake")

    def test_corfo_and_boundaries_are_explicit(self) -> None:
        report = self.report()
        check = next(
            row for row in report["checks"] if row["check_id"] == "corfo-and-boundaries"
        )
        self.assertEqual("passed", check["status"])
        self.assertEqual(10, check["checked_records"])


if __name__ == "__main__":
    unittest.main()
