from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

RESEARCH_DIR = Path(__file__).resolve().parents[1]

from tools.research.validate import (
    IndexRow,
    fund_profile_paths,
    git_changed_paths,
    is_fund_profile_path,
    profile_body_changed,
    ordering_inversions,
    parse_index,
    validate_internal_links,
    validate_mojibake,
    validate_profile,
)


class IndexParsingTests(unittest.TestCase):
    def test_parses_fund_rows_and_sections(self) -> None:
        rows = parse_index(
            "## Brazil\n\n"
            "| Fund | Stage | Focus | Geography |\n"
            "| --- | --- | --- | --- |\n"
            "| [Áurea](funds/brazil/aurea.md) | Seed | SaaS | Brazil |\n"
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("Brazil", rows[0].section)
        self.assertEqual("funds/brazil/aurea.md", rows[0].path)

    def test_detects_accent_insensitive_ordering_inversion(self) -> None:
        rows = [
            IndexRow("Zulu", "funds/z.md", "", "", "", "Brazil", 1),
            IndexRow("Áurea", "funds/a.md", "", "", "", "Brazil", 2),
        ]
        self.assertEqual(
            {("funds/z.md", "funds/a.md")},
            ordering_inversions(rows),
        )


class GitChangedPathTests(unittest.TestCase):
    def test_includes_untracked_files_as_added(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(
                ["git", "init"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "--allow-empty",
                    "-m",
                    "base",
                ],
                cwd=root,
                check=True,
                capture_output=True,
            )
            (root / "new.md").write_text("# New\n", encoding="utf-8")
            changed, added = git_changed_paths(root, "HEAD")
            self.assertIn("new.md", changed)
            self.assertIn("new.md", added)


class ProfileValidationTests(unittest.TestCase):
    def test_front_matter_only_migration_does_not_count_as_body_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profile = root / "funds" / "brazil" / "fund.md"
            profile.parent.mkdir(parents=True)
            profile.write_text("# Fund\n\nLegacy body.\n", encoding="utf-8")
            subprocess.run(
                ["git", "init"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "add", "funds/brazil/fund.md"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.com",
                    "commit",
                    "-m",
                    "base",
                ],
                cwd=root,
                check=True,
                capture_output=True,
            )
            profile.write_text(
                '---\n{"schema_version": "1.0"}\n---\n'
                "# Fund\n\nLegacy body.\n",
                encoding="utf-8",
            )
            self.assertFalse(
                profile_body_changed(
                    root,
                    "HEAD",
                    "funds/brazil/fund.md",
                )
            )

            profile.write_text(
                '---\n{"schema_version": "1.0"}\n---\n'
                "# Fund\n\nChanged body.\n",
                encoding="utf-8",
            )
            self.assertTrue(
                profile_body_changed(
                    root,
                    "HEAD",
                    "funds/brazil/fund.md",
                )
            )

    def test_distinguishes_fund_profiles_from_directory_readme(self) -> None:
        self.assertTrue(is_fund_profile_path("funds/brazil/fund.md"))
        self.assertFalse(is_fund_profile_path("funds/README.md"))

    def test_excludes_funds_readme_from_profile_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "funds" / "brazil").mkdir(parents=True)
            (root / "funds" / "README.md").write_text("# Funds\n", encoding="utf-8")
            profile = root / "funds" / "brazil" / "fund.md"
            profile.write_text("# Fund\n", encoding="utf-8")
            self.assertEqual(
                {"funds/brazil/fund.md"},
                fund_profile_paths(root),
            )

    def test_validates_links_relative_to_nested_document(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            category = root / "ecosystem" / "angel-networks"
            profile = category / "brazil" / "network.md"
            profile.parent.mkdir(parents=True)
            profile.write_text("# Network\n", encoding="utf-8")
            readme = category / "README.md"
            readme.write_text(
                "[Network](brazil/network.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_internal_links(
                    root,
                    readme,
                    readme.read_text(encoding="utf-8"),
                ),
            )

    def test_translation_link_can_fall_back_to_canonical_during_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / "ecosystem" / "public-programs" / "bolivia"
            canonical.mkdir(parents=True)
            (canonical / "operator.md").write_text("# Operator\n", encoding="utf-8")
            translated = (
                root
                / "translations"
                / "pt-BR"
                / "ecosystem"
                / "public-programs"
                / "bolivia"
                / "program.md"
            )
            translated.parent.mkdir(parents=True)
            text = "[Operator](operator.md)\n"
            translated.write_text(text, encoding="utf-8")
            self.assertEqual(
                [],
                validate_internal_links(root, translated, text),
            )

    def test_ignores_example_links_inside_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "contributing.md"
            text = (
                "```markdown\n"
                "[Example](funds/region/example.md)\n"
                "```\n\n"
                "Use `[Inline](missing.md)` as a literal.\n"
            )
            readme.write_text(text, encoding="utf-8")
            self.assertEqual([], validate_internal_links(root, readme, text))

    def test_still_reports_missing_links_in_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            text = "[Missing](missing.md)\n"
            readme.write_text(text, encoding="utf-8")
            errors = validate_internal_links(root, readme, text)
            self.assertEqual(1, len(errors))
            self.assertIn("missing.md", errors[0])

    def test_reports_missing_enriched_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fund.md"
            path.write_text("# Fund\n\n## Investment profile\n", encoding="utf-8")
            errors = validate_profile(path, "funds/test/fund.md")
        self.assertTrue(any("Direct startup investment" in error for error in errors))
        self.assertTrue(any("Declared thesis" in error for error in errors))

    def test_accepts_complete_profile(self) -> None:
        fields = "\n".join(
            f"- **{name}:** Value"
            for name in (
                "Website",
                "Fund type",
                "Direct startup investment",
                "Open to external founders",
                "Stage at entry",
                "Follow-on stages",
                "Focus",
                "Geography",
                "Initial check",
                "Investment role",
                "Business models",
                "Portfolio size",
                "Selected companies",
                "Submit a startup",
            )
        )
        text = (
            f"# Fund\n\n## Investment profile\n\n{fields}\n\n"
            "## Declared thesis\n\nText.\n\n"
            "## Portfolio signals\n\nText.\n\n"
            "## Sources\n\n- [Official](https://example.com)\n\n"
            "**Last verified:** 2026-07-27\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fund.md"
            path.write_text(text, encoding="utf-8")
            errors = validate_profile(path, "funds/test/fund.md")
        self.assertEqual([], errors)

    def test_detects_mojibake(self) -> None:
        for broken_text in ("programaÃ§Ã£o", "Texto â€œquebradoâ€"):
            with self.subTest(text=broken_text):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "bad.md"
                    path.write_text(broken_text, encoding="utf-8")
                    errors = validate_mojibake(path, "bad.md")
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
