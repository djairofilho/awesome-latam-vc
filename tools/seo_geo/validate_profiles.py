#!/usr/bin/env python3
"""Validate localized profile front matter and translation equivalence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from jsonschema import Draft202012Validator, FormatChecker


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "contract"
SCHEMA_PATH = CONTRACT_ROOT / "profile.schema.json"
ENUMS_PATH = CONTRACT_ROOT / "enums.json"
FRONT_MATTER_BOUNDARY = "---"
LINK_DESTINATION_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
URL_RE = re.compile(r"https?://[^\s<>)\]]+")
FENCED_CODE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
ISO_DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
NUMBER_RE = re.compile(r"(?<![\w-])\d+(?:[.,]\d+)*(?:%|x)?(?![\w-])")
CURRENCY_CODE_RE = re.compile(
    r"(?<![A-Z])(?:USD|BRL|MXN|ARS|CLP|COP|PEN|UYU|PYG|BOB|CRC|DOP|GTQ|HNL)(?![A-Z])"
)
CURRENCY_SYMBOL_RE = re.compile(r"(?:US\$|R\$|\$|€|£)")


@dataclass(frozen=True)
class Profile:
    path: Path
    metadata: dict
    body: str

    @property
    def display_path(self) -> str:
        try:
            return self.path.relative_to(REPOSITORY_ROOT).as_posix()
        except ValueError:
            return self.path.as_posix()


def read_contract() -> tuple[dict, dict]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    enums = json.loads(ENUMS_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema, enums


def parse_profile(path: Path) -> Profile:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != FRONT_MATTER_BOUNDARY:
        raise ValueError("front matter must start with ---")

    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == FRONT_MATTER_BOUNDARY
        ),
        None,
    )
    if closing_index is None:
        raise ValueError("front matter closing --- is missing")

    raw_metadata = "".join(lines[1:closing_index]).strip()
    if not raw_metadata:
        raise ValueError("front matter is empty")
    try:
        metadata = json.loads(raw_metadata)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "front matter must be a JSON object, which is also valid YAML 1.2: "
            f"{exc}"
        ) from exc
    if not isinstance(metadata, dict):
        raise ValueError("front matter must contain an object")

    body = "".join(lines[closing_index + 1 :]).lstrip("\r\n")
    if not body.strip():
        raise ValueError("localized Markdown body is empty")
    return Profile(path=path, metadata=metadata, body=body)


def format_json_path(parts: Sequence[object]) -> str:
    return ".".join(str(part) for part in parts) or "<root>"


def validate_schema(profile: Profile, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(profile.metadata), key=lambda item: list(item.path)):
        errors.append(
            f"{profile.display_path}: {format_json_path(list(error.path))}: "
            f"{error.message}"
        )
    return errors


def validate_semantics(profile: Profile) -> list[str]:
    metadata = profile.metadata
    errors: list[str] = []
    required = {"id", "entity_id", "entity_type", "slug", "locale"}
    if not required.issubset(metadata):
        return errors

    expected_entity_id = f"{metadata['entity_type']}:{metadata['slug']}"
    expected_profile_id = f"{expected_entity_id}:{metadata['locale']}"
    if metadata["entity_id"] != expected_entity_id:
        errors.append(
            f"{profile.display_path}: entity_id must equal entity_type:slug "
            f"({expected_entity_id})"
        )
    if metadata["id"] != expected_profile_id:
        errors.append(
            f"{profile.display_path}: id must equal entity_id:locale "
            f"({expected_profile_id})"
        )

    base = metadata.get("base_geography", {})
    if (
        base.get("kind") == "country"
        and base.get("code") not in metadata.get("countries_covered", [])
    ):
        errors.append(
            f"{profile.display_path}: base country must be present in countries_covered"
        )

    protected_terms = metadata.get("protected_terms", [])
    for term in protected_terms:
        if term not in profile.body:
            errors.append(
                f"{profile.display_path}: protected term is absent from body: {term!r}"
            )
    return errors


def protected_body_tokens(body: str) -> dict[str, Counter[str]]:
    fenced_blocks = FENCED_CODE_RE.findall(body)
    body_without_fences = FENCED_CODE_RE.sub("", body)
    return {
        "markdown_link_destinations": Counter(LINK_DESTINATION_RE.findall(body)),
        "urls": Counter(URL_RE.findall(body)),
        "inline_code": Counter(INLINE_CODE_RE.findall(body_without_fences)),
        "fenced_code": Counter(block.rstrip("\r\n") for block in fenced_blocks),
        "iso_dates": Counter(ISO_DATE_RE.findall(body)),
        "numbers": Counter(NUMBER_RE.findall(body)),
        "currency_codes": Counter(CURRENCY_CODE_RE.findall(body)),
        "currency_symbols": Counter(CURRENCY_SYMBOL_RE.findall(body)),
    }


def validate_translation(
    canonical: Profile,
    translation: Profile,
    protected_fields: Sequence[str],
) -> list[str]:
    errors: list[str] = []
    for field in protected_fields:
        if translation.metadata.get(field) != canonical.metadata.get(field):
            errors.append(
                f"{translation.display_path}: protected field differs from "
                f"{canonical.display_path}: {field}"
            )

    canonical_tokens = protected_body_tokens(canonical.body)
    translated_tokens = protected_body_tokens(translation.body)
    for token_kind in canonical_tokens:
        if translated_tokens[token_kind] != canonical_tokens[token_kind]:
            errors.append(
                f"{translation.display_path}: protected body tokens differ from "
                f"{canonical.display_path}: {token_kind}"
            )

    for term in canonical.metadata.get("protected_terms", []):
        if translation.body.count(term) != canonical.body.count(term):
            errors.append(
                f"{translation.display_path}: protected term count differs from "
                f"{canonical.display_path}: {term!r}"
            )
    return errors


def validate_collection(profiles: Sequence[Profile], schema: dict, enums: dict) -> list[str]:
    errors: list[str] = []
    for profile in profiles:
        errors.extend(validate_schema(profile, schema))
        errors.extend(validate_semantics(profile))

    ids: dict[str, list[Profile]] = defaultdict(list)
    entity_locales: dict[tuple[str, str], list[Profile]] = defaultdict(list)
    entities: dict[str, list[Profile]] = defaultdict(list)
    for profile in profiles:
        metadata = profile.metadata
        if isinstance(metadata.get("id"), str):
            ids[metadata["id"]].append(profile)
        if isinstance(metadata.get("entity_id"), str):
            entities[metadata["entity_id"]].append(profile)
            if isinstance(metadata.get("locale"), str):
                entity_locales[(metadata["entity_id"], metadata["locale"])].append(profile)

    for profile_id, duplicates in ids.items():
        if len(duplicates) > 1:
            paths = ", ".join(profile.display_path for profile in duplicates)
            errors.append(f"duplicate profile id {profile_id}: {paths}")
    for (entity_id, locale), duplicates in entity_locales.items():
        if len(duplicates) > 1:
            paths = ", ".join(profile.display_path for profile in duplicates)
            errors.append(f"duplicate entity/locale {entity_id}@{locale}: {paths}")

    protected_fields = enums["protected_front_matter_fields"]
    for entity_id, localized_profiles in entities.items():
        canonicals = [
            profile
            for profile in localized_profiles
            if profile.metadata.get("translation_status") == "canonical"
            and profile.metadata.get("locale") == "en"
        ]
        if len(canonicals) != 1:
            errors.append(
                f"{entity_id}: expected exactly one English canonical profile, "
                f"found {len(canonicals)}"
            )
            continue
        canonical = canonicals[0]
        for profile in localized_profiles:
            if profile is canonical:
                continue
            expected_translation_of = canonical.metadata.get("id")
            if profile.metadata.get("translation_of") != expected_translation_of:
                errors.append(
                    f"{profile.display_path}: translation_of must reference exactly "
                    f"{expected_translation_of}"
                )
            errors.extend(validate_translation(canonical, profile, protected_fields))
    return sorted(set(errors))


def discover_markdown(paths: Sequence[Path]) -> list[Path]:
    discovered: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved.is_dir():
            discovered.update(item.resolve() for item in resolved.rglob("*.md"))
        elif resolved.suffix.lower() == ".md" and resolved.is_file():
            discovered.add(resolved)
        else:
            raise ValueError(f"path is not a Markdown file or directory: {path}")
    return sorted(discovered)


def validate_paths(paths: Sequence[Path]) -> list[str]:
    schema, enums = read_contract()
    errors: list[str] = []
    profiles: list[Profile] = []
    try:
        markdown_paths = discover_markdown(paths)
    except ValueError as exc:
        return [str(exc)]
    if not markdown_paths:
        return ["no Markdown profiles found"]

    for path in markdown_paths:
        try:
            profiles.append(parse_profile(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path.as_posix()}: {exc}")
    errors.extend(validate_collection(profiles, schema, enums))
    return sorted(set(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="Markdown profile files or directories",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_paths(args.paths)
    if errors:
        print("SEO/GEO profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("SEO/GEO profile validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
