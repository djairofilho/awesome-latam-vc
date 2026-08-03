from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from collections import Counter
from pathlib import Path


AUDIT_PATH = Path(__file__).resolve().parents[1] / "audit.py"
SPEC = importlib.util.spec_from_file_location("epic_327_final_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def copy_epic() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory()
    destination = Path(temporary.name) / "research" / "epic-327"
    shutil.copytree(audit.EPIC, destination)
    return temporary, destination


class FinalAuditRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report, cls.decisions = audit.audit_repository(audit.REPO)

    def test_current_repository_passes_every_gate(self) -> None:
        self.assertEqual("pass", self.report["status"])
        self.assertEqual([], self.report["findings"])
        self.assertTrue(all(row["status"] == "pass" for row in self.report["gates"]))

    def test_terminal_ledger_has_expected_dynamic_review_counts(self) -> None:
        self.assertEqual(1088, len(self.decisions))
        self.assertEqual(1073, self.report["counts"]["review_assignments"])
        self.assertEqual(1073, self.report["counts"]["review_results"])
        self.assertEqual(
            {
                "duplicate": 15,
                "eligible": 1,
                "excluded": 14,
                "identity_conflict": 592,
                "inactive": 2,
                "insufficient_evidence": 339,
                "routed_accelerators": 10,
                "routed_angel_networks": 4,
                "routed_funding_platforms": 2,
                "routed_other": 10,
                "unresolved": 99,
            },
            dict(Counter(row["decision"] for row in self.decisions)),
        )

    def test_final_ledger_is_sorted_and_unique(self) -> None:
        ids = [row["candidate_id"] for row in self.decisions]
        self.assertEqual(sorted(ids), ids)
        self.assertEqual(len(ids), len(set(ids)))
        manual = [
            row
            for row in self.decisions
            if row["decision"] in {"identity_conflict", "unresolved"}
        ]
        self.assertEqual(691, len(manual))
        self.assertTrue(all(row["destination_kind"] == "manual_review" for row in manual))
        self.assertEqual(358, sum(row["destination"] is None for row in manual))

    def test_generated_artifacts_are_deterministic_and_current(self) -> None:
        first = audit.build_outputs(audit.REPO)
        second = audit.build_outputs(audit.REPO)
        self.assertEqual(first, second)
        for relative, rendered in first.items():
            self.assertEqual(
                rendered,
                (audit.HERE / relative).read_text(encoding="utf-8"),
                relative,
            )
        parsed = json.loads(first["audit-report.json"])
        self.assertFalse(parsed["provenance"]["network_access"])
        self.assertEqual(
            audit.WAYFINDER_PROFILE,
            parsed["publication"]["audited_profile"],
        )
        self.assertNotIn("new_profiles_since_baseline", parsed["publication"])


class FinalDecisionPrecedenceTests(unittest.TestCase):
    def test_adjudication_overrides_review_and_review_overrides_origin(self) -> None:
        candidates = {
            "delta-fund-a": {
                "candidate_id": "delta-fund-a",
                "status": "duplicate",
                "canonical_profile": "funds/a.md",
            },
            "delta-fund-b": {
                "candidate_id": "delta-fund-b",
                "status": "identity_conflict",
            },
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "status": "unresolved",
            },
        }
        reviews = {
            "delta-fund-b": {
                "candidate_id": "delta-fund-b",
                "final_decision": "insufficient_evidence",
                "destination": None,
            },
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "final_decision": "excluded",
                "destination": None,
            },
        }
        adjudications = {
            "delta-fund-c": {
                "candidate_id": "delta-fund-c",
                "final_decision": "eligible",
                "destination": "funds/",
            }
        }
        rows, unresolved = audit.resolve_final_decisions(
            candidates, {}, reviews, adjudications, "2026-08-02"
        )
        self.assertEqual([], unresolved)
        self.assertEqual(
            ["duplicate", "insufficient_evidence", "eligible"],
            [row["decision"] for row in rows],
        )
        self.assertEqual(
            ["origin", "review", "adjudication"],
            [row["source"] for row in rows],
        )
        self.assertEqual(
            ["canonical_duplicate", "evidence_follow_up", "fund_publication"],
            [row["destination_kind"] for row in rows],
        )


class CoverageGateTests(unittest.TestCase):
    def test_positive_coverage_includes_mandatory_records_and_twenty_percent(self) -> None:
        origins = {
            "eligible": "eligible",
            "conflict": "identity_conflict",
            "route": "routed_accelerators",
            **{f"excluded-{number}": "excluded" for number in range(5)},
        }
        assignments = {
            key: {"candidate_id": key, "review_reason": reason}
            for key, reason in (
                ("eligible", "all_eligible"),
                ("conflict", "all_identity_conflicts"),
                ("route", "all_routed"),
                ("excluded-0", "deterministic_exclusion_sample"),
            )
        }
        self.assertEqual([], audit.coverage_findings(origins, assignments))

    def test_negative_coverage_reports_missing_mandatory_record(self) -> None:
        findings = audit.coverage_findings(
            {"route": "routed_angel_networks"}, {}
        )
        self.assertEqual("mandatory_review_coverage", findings[0]["code"])
        self.assertEqual("high", findings[0]["severity"])
        self.assertEqual(["route"], findings[0]["details"]["candidate_ids"])

    def test_negative_coverage_rejects_sample_below_twenty_percent(self) -> None:
        origins = {f"candidate-{number}": "unresolved" for number in range(6)}
        assignments = {
            "candidate-0": {
                "candidate_id": "candidate-0",
                "review_reason": "deterministic_exclusion_sample",
            }
        }
        findings = audit.coverage_findings(origins, assignments)
        sample = next(
            row for row in findings if row["code"] == "exclusion_sample_coverage"
        )
        self.assertEqual(2, sample["details"]["minimum"])
        self.assertEqual(1, sample["details"]["selected"])


class ReviewPipelineNegativeTests(unittest.TestCase):
    def test_approved_review_cannot_change_source_decision(self) -> None:
        temporary, epic = copy_epic()
        self.addCleanup(temporary.cleanup)
        path = epic / "review" / "results" / "review-0.jsonl"
        rows = audit.load_jsonl(path)
        approved = next(row for row in rows if row["review_status"] == "approved")
        approved["final_decision"] = "excluded"
        path.write_text(audit.dump_jsonl(rows), encoding="utf-8", newline="\n")
        codes = {row["code"] for row in audit.review_pipeline_findings(epic)}
        self.assertIn("review_semantic_integrity", codes)
        self.assertIn("approved_review_source_mismatch", codes)

    def test_review_evidence_must_exist_and_belong_to_candidate(self) -> None:
        temporary, epic = copy_epic()
        self.addCleanup(temporary.cleanup)
        path = epic / "review" / "results" / "review-0.jsonl"
        rows = audit.load_jsonl(path)
        changed = next(row for row in rows if row["review_status"] == "changes_requested")
        changed["evidence_ids"] = ["evidence-does-not-exist"]
        path.write_text(audit.dump_jsonl(rows), encoding="utf-8", newline="\n")
        findings = audit.review_pipeline_findings(epic)
        semantic = next(row for row in findings if row["code"] == "review_semantic_integrity")
        self.assertTrue(
            any("missing evidence" in error for error in semantic["details"]["freeze_errors"])
        )

    def test_reviewer_reason_and_sample_must_match_prepare_ranking(self) -> None:
        temporary, epic = copy_epic()
        self.addCleanup(temporary.cleanup)
        path = epic / "review" / "assignments" / "review-0.jsonl"
        rows = audit.load_jsonl(path)
        sampled = next(
            row
            for row in rows
            if row["review_reason"] == "deterministic_exclusion_sample"
        )
        rows.remove(sampled)
        authored = next(
            row for row in rows if row["source_worker"].startswith("validation-")
        )
        authored["reviewer"] = authored["source_worker"].replace(
            "validation-", "review-"
        )
        authored["review_reason"] = "deterministic_exclusion_sample"
        path.write_text(audit.dump_jsonl(rows), encoding="utf-8", newline="\n")
        codes = {row["code"] for row in audit.review_pipeline_findings(epic)}
        self.assertIn("review_assignment_determinism", codes)
        self.assertIn("review_assignment_semantics", codes)


class DestinationNegativeTests(unittest.TestCase):
    def test_rejects_wrong_canonical_and_route_destinations(self) -> None:
        rows = [
            {
                "candidate_id": "delta-fund-caricaco-vc",
                "decision": "duplicate",
                "destination": "funds/regional/wayra.md",
            },
            {
                "candidate_id": audit.WAYFINDER_ID,
                "decision": "eligible",
                "destination": "funds/multi-country/",
            },
            {
                "candidate_id": "accelerator",
                "decision": "routed_accelerators",
                "destination": "ecosystem/angel-networks/",
            },
            {
                "candidate_id": "other",
                "decision": "routed_other",
                "destination": "ecosystem/unknown/",
            },
        ]
        findings = audit.destination_findings(rows, audit.REPO, {audit.WAYFINDER_ID})
        self.assertEqual("terminal_destination_invalid", findings[0]["code"])
        self.assertEqual(4, len(findings[0]["details"]))

    def test_accepts_abstract_routed_other_vocabulary_without_physical_path(self) -> None:
        rows = [
            {
                "candidate_id": "abstract-handoff",
                "decision": "routed_other",
                "destination": "ecosystem/corporate-investors/not-materialized.md",
            }
        ]
        self.assertEqual([], audit.destination_findings(rows, audit.REPO, set()))


class PublicationNegativeTests(unittest.TestCase):
    def test_translation_protected_fields_are_parsed_and_compared(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            paths = []
            for ordinal, source in enumerate((
                audit.REPO / audit.WAYFINDER_PROFILE,
                audit.REPO / "translations" / "pt-BR" / audit.WAYFINDER_PROFILE,
                audit.REPO / "translations" / "es" / audit.WAYFINDER_PROFILE,
            )):
                destination = target / str(ordinal) / source.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                paths.append(destination)
            text = paths[1].read_text(encoding="utf-8").replace(
                '"code": "GLOBAL"',
                '"code": "US"',
                1,
            )
            paths[1].write_text(text, encoding="utf-8", newline="\n")
            errors = audit.profile_triplet_errors(audit.REPO, paths)
            self.assertTrue(any("protected field differs" in error for error in errors))

    def test_export_validator_rejects_csv_field_drift(self) -> None:
        generator = audit.load_module(
            "epic327_generate_entities",
            audit.REPO / "tools" / "seo_geo" / "generate_entities.py",
        )
        json_payload = (audit.REPO / "data" / "entities.json").read_bytes()
        csv_payload = (audit.REPO / "data" / "entities.csv").read_bytes().replace(
            b"Wayfinder Ventures", b"Wayfinder Drift", 1
        )
        errors = generator.validate_export_consistency(json_payload, csv_payload)
        self.assertTrue(any("CSV field differs from JSON" in error for error in errors))

    def test_index_validator_rejects_missing_localized_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            for name in ("README.md", "README.pt.md", "README.es.md"):
                shutil.copy2(audit.REPO / name, repo / name)
            portuguese = repo / "README.pt.md"
            lines = portuguese.read_text(encoding="utf-8").splitlines()
            lines = [line for line in lines if f"]({audit.WAYFINDER_PROFILE})" not in line]
            portuguese.write_text("\n".join(lines) + "\n", encoding="utf-8")
            current = {
                path.relative_to(audit.REPO).as_posix()
                for path in audit.REPO.glob("funds/**/*.md")
                if path.name != "README.md"
            }
            errors = audit.index_link_errors(repo, current)
            self.assertTrue(any("README.pt.md" in error for error in errors))


class EncodingAndCutoffNegativeTests(unittest.TestCase):
    def test_entities_json_mojibake_signature_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            path = repo / "entities.json"
            broken = "programa" + chr(0xC3) + chr(0xA7) + chr(0xC3) + chr(0xA3) + "o"
            path.write_text(
                json.dumps({"name": broken}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            findings = audit.utf8_findings([path], repo)
            self.assertEqual("utf8_or_mojibake", findings[0]["code"])

    def test_evidence_after_cutoff_is_rejected(self) -> None:
        mismatches = audit.dated_record_mismatches(
            [],
            [],
            [],
            [{"evidence_id": "future", "accessed_on": "2026-08-03"}],
            "2026-08-02",
        )
        self.assertEqual(["evidence:future"], mismatches)


if __name__ == "__main__":
    unittest.main()
