#!/usr/bin/env python3
"""Validate catalog profiles, research artifacts and translated indexes."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

try:
    from .accelerator_validation import (
        is_accelerator_profile_path,
        validate_accelerator_index,
        validate_accelerator_profile,
        validate_epic_62,
    )
    from .platform_validation import validate_epic_64
except ImportError:  # Allow `python tools/research/validate.py`.
    from accelerator_validation import (
        is_accelerator_profile_path,
        validate_accelerator_index,
        validate_accelerator_profile,
        validate_epic_62,
    )
    from platform_validation import validate_epic_64


README_NAMES = ("README.md", "README.pt.md", "README.es.md")
FUND_LINK_RE = re.compile(
    r"^\| \[([^\]]+)\]\((funds/[^)]+\.md)\) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REQUIRED_PROFILE_FIELDS = (
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
REQUIRED_PROFILE_SECTIONS = (
    "Investment profile",
    "Declared thesis",
    "Portfolio signals",
    "Sources",
)
MOJIBAKE_MARKERS = ("Ã", "Â", "�", "\x07", "\\`")


@dataclass(frozen=True)
class IndexRow:
    name: str
    path: str
    stage: str
    focus: str
    geography: str
    section: str
    line_number: int


def repository_root(start: Path | None = None) -> Path:
    """Return the Git repository root."""
    command = ["git", "rev-parse", "--show-toplevel"]
    result = subprocess.run(
        command,
        cwd=start,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return Path(result.stdout.strip())


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: arquivo não está em UTF-8 ({exc})") from exc


def parse_index(text: str) -> list[IndexRow]:
    """Extract fund rows, preserving their section and order."""
    rows: list[IndexRow] = []
    section = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = FUND_LINK_RE.match(line)
        if match:
            rows.append(
                IndexRow(
                    name=match.group(1).strip(),
                    path=match.group(2),
                    stage=match.group(3).strip(),
                    focus=match.group(4).strip(),
                    geography=match.group(5).strip(),
                    section=section,
                    line_number=line_number,
                )
            )
    return rows


def sort_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).casefold()


def ordering_inversions(rows: Sequence[IndexRow]) -> set[tuple[str, str]]:
    """Return path pairs that appear in reverse alphabetical order per section."""
    inversions: set[tuple[str, str]] = set()
    for left_index, left in enumerate(rows):
        for right in rows[left_index + 1 :]:
            if left.section != right.section:
                continue
            if sort_key(left.name) > sort_key(right.name):
                inversions.add((left.path, right.path))
    return inversions


def git_changed_paths(root: Path, base_ref: str) -> tuple[set[str], set[str]]:
    """Return changed and newly added paths relative to base_ref."""
    result = subprocess.run(
        ["git", "diff", "--name-status", "--find-renames", base_ref, "--"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    changed: set[str] = set()
    added: set[str] = set()
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1].replace("\\", "/")
        changed.add(path)
        if status == "A":
            added.add(path)
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    for line in untracked_result.stdout.splitlines():
        path = line.replace("\\", "/")
        changed.add(path)
        added.add(path)
    return changed, added


def git_file_text(root: Path, base_ref: str, relative_path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{relative_path}"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout if result.returncode == 0 else None


def validate_profile(path: Path, display_path: str) -> list[str]:
    errors: list[str] = []
    try:
        text = read_utf8(path)
    except (OSError, ValueError) as exc:
        return [str(exc)]

    for section in REQUIRED_PROFILE_SECTIONS:
        if f"## {section}" not in text:
            errors.append(f"{display_path}: seção obrigatória ausente: {section}")

    fields = {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^- \*\*([^*]+):\*\*\s*(.*)$", text, re.MULTILINE)
    }
    for field in REQUIRED_PROFILE_FIELDS:
        if not fields.get(field):
            errors.append(f"{display_path}: campo obrigatório ausente ou vazio: {field}")

    if not re.search(r"^\*\*Last verified:\*\* \d{4}-\d{2}-\d{2}\s*$", text, re.MULTILINE):
        errors.append(f"{display_path}: Last verified deve usar YYYY-MM-DD")

    sources_match = re.search(
        r"^## Sources\s*$([\s\S]*?)(?=^\*\*Last verified:|\Z)", text, re.MULTILINE
    )
    if not sources_match or not re.search(
        r"^- \[[^\]]+\]\(https?://[^)]+\)", sources_match.group(1), re.MULTILINE
    ):
        errors.append(f"{display_path}: inclua ao menos uma fonte HTTP(S)")
    return errors


def validate_internal_links(root: Path, readme: Path, text: str) -> list[str]:
    errors: list[str] = []
    display_path = readme.relative_to(root).as_posix()
    for target in MARKDOWN_LINK_RE.findall(text):
        clean_target = target.strip().split("#", 1)[0]
        if not clean_target or re.match(r"^[a-z][a-z0-9+.-]*:", clean_target, re.I):
            continue
        candidate = (readme.parent / clean_target).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{display_path}: link sai do repositório: {target}")
            continue
        if not candidate.exists():
            errors.append(f"{display_path}: link interno inexistente: {target}")
    return errors


def is_fund_profile_path(path: str) -> bool:
    """Return whether a repository path is an individual fund profile."""
    return (
        path.startswith("funds/")
        and path.endswith(".md")
        and path != "funds/README.md"
    )


def fund_profile_paths(root: Path) -> set[str]:
    """Return fund profile paths without directory documentation files."""
    return {
        path.relative_to(root).as_posix()
        for path in (root / "funds").rglob("*.md")
        if is_fund_profile_path(path.relative_to(root).as_posix())
    }


def validate_mojibake(path: Path, display_path: str) -> list[str]:
    try:
        text = read_utf8(path)
    except (OSError, ValueError) as exc:
        return [str(exc)]
    return [
        f"{display_path}: possível mojibake detectado: {marker!r}"
        for marker in MOJIBAKE_MARKERS
        if marker in text
    ]


def validate_repository(root: Path, base_ref: str) -> list[str]:
    errors: list[str] = []
    changed, added = git_changed_paths(root, base_ref)
    index_rows: dict[str, list[IndexRow]] = {}

    for readme_name in README_NAMES:
        path = root / readme_name
        try:
            text = read_utf8(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        rows = parse_index(text)
        index_rows[readme_name] = rows
        errors.extend(validate_internal_links(root, path, text))
        errors.extend(validate_mojibake(path, readme_name))

        duplicates = sorted(
            row_path
            for row_path in {row.path for row in rows}
            if sum(item.path == row_path for item in rows) > 1
        )
        for duplicate in duplicates:
            errors.append(f"{readme_name}: fundo duplicado no índice: {duplicate}")

        current_inversions = ordering_inversions(rows)
        base_text = git_file_text(root, base_ref, readme_name)
        base_inversions = ordering_inversions(parse_index(base_text)) if base_text else set()
        for left, right in sorted(current_inversions - base_inversions):
            errors.append(
                f"{readme_name}: nova inversão alfabética entre {left} e {right}"
            )

    if len(index_rows) == len(README_NAMES):
        reference_name = README_NAMES[0]
        reference_paths = [row.path for row in index_rows[reference_name]]
        reference_set = set(reference_paths)
        for readme_name in README_NAMES[1:]:
            paths = [row.path for row in index_rows[readme_name]]
            if set(paths) != reference_set:
                missing = sorted(reference_set - set(paths))
                extra = sorted(set(paths) - reference_set)
                errors.append(
                    f"{readme_name}: conjunto difere de {reference_name}; "
                    f"ausentes={missing}, extras={extra}"
                )
            if paths != reference_paths:
                errors.append(f"{readme_name}: ordem dos fundos difere de {reference_name}")

        profile_paths = fund_profile_paths(root)
        if reference_set != profile_paths:
            missing = sorted(profile_paths - reference_set)
            extra = sorted(reference_set - profile_paths)
            errors.append(
                "contagem/conjunto entre perfis e índices diverge; "
                f"não indexados={missing}, links sem perfil={extra}"
            )

    added_funds = sorted(path for path in added if is_fund_profile_path(path))
    if len(added_funds) > 10:
        errors.append(
            f"o diff adiciona {len(added_funds)} fundos; o limite por PR é 10"
        )

    changed_profiles = sorted(
        path
        for path in changed
        if is_fund_profile_path(path) and (root / path).exists()
    )
    for relative_path in changed_profiles:
        errors.extend(validate_profile(root / relative_path, relative_path))

    added_accelerators = sorted(
        path for path in added if is_accelerator_profile_path(path)
    )
    if len(added_accelerators) > 10:
        errors.append(
            f"o diff adiciona {len(added_accelerators)} aceleradoras; "
            "o limite por PR é 10"
        )

    changed_accelerators = sorted(
        path
        for path in changed
        if is_accelerator_profile_path(path) and (root / path).exists()
    )
    for relative_path in changed_accelerators:
        errors.extend(
            validate_accelerator_profile(root / relative_path, relative_path)
        )

    errors.extend(validate_accelerator_index(root))
    errors.extend(validate_epic_62(root))
    errors.extend(validate_epic_64(root))

    # Source code intentionally contains the marker literals used by this check.
    # Scan authored/research content, not the validator implementation itself.
    text_extensions = {".md", ".json", ".jsonl", ".yml", ".yaml"}
    for relative_path in sorted(changed):
        path = root / relative_path
        if path.is_file() and path.suffix.lower() in text_extensions:
            errors.extend(validate_mojibake(path, relative_path))
            if path.suffix.lower() == ".md":
                try:
                    text = read_utf8(path)
                except (OSError, ValueError) as exc:
                    errors.append(str(exc))
                else:
                    errors.extend(validate_internal_links(root, path, text))

    return sorted(set(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        default="origin/main",
        help="Git revision used to identify new/changed artifacts (default: origin/main)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="repository root (discovered with git by default)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve() if args.root else repository_root()
    try:
        errors = validate_repository(root, args.base_ref)
    except subprocess.CalledProcessError as exc:
        print(f"validation could not run Git command: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("Research validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Research validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
