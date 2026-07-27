#!/usr/bin/env python3
"""Safely verify that translated fund indexes are structurally synchronized."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from validate import README_NAMES, parse_index, read_utf8, repository_root


def synchronization_errors(root: Path) -> list[str]:
    """Compare fund paths and order without rewriting translated prose."""
    rows_by_readme = {
        name: parse_index(read_utf8(root / name))
        for name in README_NAMES
    }
    reference_name = README_NAMES[0]
    reference = [row.path for row in rows_by_readme[reference_name]]
    errors: list[str] = []
    for name in README_NAMES[1:]:
        current = [row.path for row in rows_by_readme[name]]
        if set(current) != set(reference):
            errors.append(f"{name}: fund set differs from {reference_name}")
        elif current != reference:
            errors.append(f"{name}: fund order differs from {reference_name}")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify synchronization (the only safe supported mode)",
    )
    parser.add_argument("--root", type=Path, help="repository root")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.check:
        print(
            "Refusing to rewrite translated indexes; use --check.",
            file=sys.stderr,
        )
        return 2
    root = args.root.resolve() if args.root else repository_root()
    errors = synchronization_errors(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("All translated indexes are structurally synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
