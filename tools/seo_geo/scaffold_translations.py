#!/usr/bin/env python3
"""Create deterministic, review-pending translation scaffolds."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Iterable, Sequence

try:
    from .validate_i18n import (
        CONFIG_PATH,
        REPOSITORY_ROOT,
        canonical_relative_path,
        expected_translation_path,
        load_config,
    )
    from .validate_profiles import Profile, catalog_profile_paths, parse_profile
except ImportError:
    from validate_i18n import (
        CONFIG_PATH,
        REPOSITORY_ROOT,
        canonical_relative_path,
        expected_translation_path,
        load_config,
    )
    from validate_profiles import Profile, catalog_profile_paths, parse_profile


MAX_BATCH_SIZE = 25


def partition(
    paths: Sequence[Path],
    batch_size: int = MAX_BATCH_SIZE,
) -> list[list[Path]]:
    if batch_size < 1 or batch_size > MAX_BATCH_SIZE:
        raise ValueError(f"batch size must be between 1 and {MAX_BATCH_SIZE}")
    ordered = sorted(paths, key=lambda path: path.as_posix())
    return [
        ordered[offset : offset + batch_size]
        for offset in range(0, len(ordered), batch_size)
    ]


def localized_profile(profile: Profile, locale: str) -> Profile:
    metadata = {
        **profile.metadata,
        "id": f"{profile.metadata['entity_id']}:{locale}",
        "locale": locale,
        "translation_of": profile.metadata["id"],
        "translation_status": "needs_review",
    }
    return replace(profile, metadata=metadata)


def render_profile(profile: Profile) -> str:
    front_matter = json.dumps(
        profile.metadata,
        ensure_ascii=False,
        indent=2,
    )
    return f"---\n{front_matter}\n---\n{profile.body.rstrip()}\n"


def scaffold_batch(
    *,
    root: Path,
    locale: str,
    batch_number: int,
    batch_size: int = MAX_BATCH_SIZE,
) -> list[Path]:
    config = load_config(root / CONFIG_PATH.relative_to(REPOSITORY_ROOT))
    content_root = config["locales"].get(locale, {}).get("content_root")
    if not content_root:
        raise ValueError(f"{locale}: locale has no translation content root")

    canonical_paths = [
        root / path.relative_to(REPOSITORY_ROOT)
        for path in catalog_profile_paths()
    ]
    batches = partition(canonical_paths, batch_size)
    if batch_number < 1 or batch_number > len(batches):
        raise ValueError(
            f"batch number must be between 1 and {len(batches)}"
        )

    created: list[Path] = []
    for canonical_path in batches[batch_number - 1]:
        canonical = parse_profile(canonical_path)
        relative = canonical_relative_path(canonical_path, root)
        target = expected_translation_path(config, locale, relative, root)
        if target.exists():
            raise FileExistsError(f"refusing to overwrite {target.as_posix()}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            render_profile(localized_profile(canonical, locale)),
            encoding="utf-8",
            newline="\n",
        )
        created.append(target)
    return created


def manifest(
    *,
    root: Path,
    locale: str,
    source_commit: str,
    batch_size: int = MAX_BATCH_SIZE,
) -> dict:
    paths = [
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for path in catalog_profile_paths()
    ]
    batches = partition([Path(path) for path in paths], batch_size)
    return {
        "schema_version": "1.0",
        "locale": locale,
        "source_commit": source_commit,
        "ordering": "canonical relative path ascending",
        "batch_size": batch_size,
        "profile_count": len(paths),
        "batches": [
            {
                "number": number,
                "profile_count": len(batch),
                "canonical_paths": [path.as_posix() for path in batch],
            }
            for number, batch in enumerate(batches, start=1)
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", required=True)
    parser.add_argument("--batch", type=int)
    parser.add_argument("--batch-size", type=int, default=MAX_BATCH_SIZE)
    parser.add_argument("--write-manifest", type=Path)
    parser.add_argument("--source-commit")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.write_manifest:
        if not args.source_commit:
            raise SystemExit("--source-commit is required with --write-manifest")
        document = manifest(
            root=REPOSITORY_ROOT,
            locale=args.locale,
            source_commit=args.source_commit,
            batch_size=args.batch_size,
        )
        args.write_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.write_manifest.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"Wrote {len(document['batches'])} deterministic batches "
            f"for {document['profile_count']} profiles."
        )
        return 0
    if args.batch is None:
        raise SystemExit("--batch is required unless --write-manifest is used")
    created = scaffold_batch(
        root=REPOSITORY_ROOT,
        locale=args.locale,
        batch_number=args.batch,
        batch_size=args.batch_size,
    )
    print(f"Created {len(created)} review-pending translation scaffolds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
