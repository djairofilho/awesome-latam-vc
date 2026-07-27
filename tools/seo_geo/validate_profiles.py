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
BARE_DOMAIN_RE = re.compile(
    r"(?<![/@\w-])(?:[a-z0-9-]+\.)+[a-z]{2,}(?:#[a-z0-9-]+)?",
    re.IGNORECASE,
)
REPOSITORY_PATH_RE = re.compile(
    r"\b(?:funds|ecosystem|translations)/"
    r"[a-z0-9_./:#-]*[a-z0-9_:#-](?=[\s,;.)]|$)",
    re.IGNORECASE,
)
FENCED_CODE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
ISO_DATE_RE = re.compile(r"(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)")
NUMBER_RE = re.compile(
    r"(?<![\w-])\d+(?:[.,]\d+)*(?:%|x)?(?:(?=-[A-Za-z])|(?![\w-]))"
)
CURRENCY_CODE_RE = re.compile(
    r"(?<![A-Z])(?:USD|BRL|MXN|ARS|CLP|COP|PEN|UYU|PYG|BOB|CRC|DOP|GTQ|HNL)(?![A-Z])"
)
CURRENCY_SYMBOL_RE = re.compile(r"(?:US\$|R\$|\$|€|£)")
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
VISIBLE_FIELD_RE = re.compile(
    r"^-\s+\*\*(?P<field>[^:*]+):\*\*\s*(?P<value>.*)$",
    re.MULTILINE,
)
SOURCE_SECTION_RE = re.compile(
    r"^## (?:Official sources|Sources)\s*$\n"
    r"(?P<section>.*?)(?=^\*\*Last verified:\*\*|\Z)",
    re.MULTILINE | re.DOTALL,
)
SOURCE_LINK_RE = re.compile(r"^-\s+\[([^\]]+)\]\((https://[^)]+)\)", re.MULTILINE)
LAST_VERIFIED_RE = re.compile(
    r"^\*\*Last verified:\*\*\s+(\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)
LATAM_COUNTRY_CODES = {
    "AR",
    "BO",
    "BR",
    "CL",
    "CO",
    "CR",
    "DO",
    "EC",
    "GT",
    "MX",
    "PA",
    "PE",
    "PR",
    "PY",
    "UY",
}


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

    heading = HEADING_RE.search(profile.body)
    if not heading or heading.group(1) != metadata.get("name"):
        errors.append(f"{profile.display_path}: H1 must equal metadata name")

    base = metadata.get("base_geography", {})
    countries_covered = set(metadata.get("countries_covered", []))
    aggregate_covers_base = (
        "GLOBAL" in countries_covered
        or (
            "LATAM" in countries_covered
            and base.get("code") in LATAM_COUNTRY_CODES
        )
    )
    if (
        metadata.get("entity_type") != "accelerator"
        and base.get("kind") == "country"
        and base.get("code") not in countries_covered
        and "NOT_DISCLOSED" not in countries_covered
        and not aggregate_covers_base
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
        "bare_domains": Counter(BARE_DOMAIN_RE.findall(body_without_fences)),
        "repository_paths": Counter(
            REPOSITORY_PATH_RE.findall(body_without_fences)
        ),
        "inline_code": Counter(INLINE_CODE_RE.findall(body_without_fences)),
        "fenced_code": Counter(block.rstrip("\r\n") for block in fenced_blocks),
        # A translated sentence may avoid repeating a date that remains present
        # elsewhere in the profile. Preserve the exact date inventory without
        # forcing source-language repetition.
        "iso_dates": Counter(set(ISO_DATE_RE.findall(body))),
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


def catalog_profile_paths() -> list[Path]:
    paths = [
        path.resolve()
        for path in (REPOSITORY_ROOT / "funds").rglob("*.md")
        if path.name != "README.md"
    ]
    paths.extend(
        path.resolve()
        for path in (REPOSITORY_ROOT / "ecosystem").rglob("*.md")
        if not path.name.startswith("README")
    )
    return sorted(paths)


def validate_catalog_correspondence(profile: Profile) -> list[str]:
    errors: list[str] = []
    metadata = profile.metadata
    heading = HEADING_RE.search(profile.body)
    if not heading or heading.group(1) != metadata.get("name"):
        errors.append(
            f"{profile.display_path}: H1 must equal metadata name"
        )

    fields = {
        match.group("field"): match.group("value").strip()
        for match in VISIBLE_FIELD_RE.finditer(profile.body)
    }
    website = metadata.get("official_website")
    visible_website = fields.get("Website") or fields.get("Official page", "")
    if website is None:
        if not visible_website.startswith("Not publicly disclosed"):
            errors.append(
                f"{profile.display_path}: null official_website requires an "
                "explicit Not publicly disclosed Website field"
            )
    elif website not in profile.body:
        errors.append(
            f"{profile.display_path}: official_website is absent from body"
        )

    founder_route = metadata.get("founder_route")
    if founder_route is not None and founder_route not in profile.body:
        errors.append(
            f"{profile.display_path}: founder_route is absent from body"
        )

    source_match = SOURCE_SECTION_RE.search(profile.body)
    visible_sources = (
        SOURCE_LINK_RE.findall(source_match.group("section"))
        if source_match
        else []
    )
    metadata_sources = [
        (source["title"], source["url"])
        for source in metadata.get("sources", [])
        if isinstance(source, dict)
        and isinstance(source.get("title"), str)
        and isinstance(source.get("url"), str)
    ]
    if visible_sources != metadata_sources:
        errors.append(
            f"{profile.display_path}: metadata sources must exactly match the "
            "visible Sources section"
        )

    verified_match = LAST_VERIFIED_RE.search(profile.body)
    if not verified_match or verified_match.group(1) != metadata.get("last_verified"):
        errors.append(
            f"{profile.display_path}: metadata last_verified must equal the "
            "visible Last verified date"
        )
    if metadata.get("locale") != "en":
        errors.append(f"{profile.display_path}: canonical catalog locale must be en")
    return errors


def validate_collection(
    profiles: Sequence[Profile],
    schema: dict,
    enums: dict,
    *,
    catalog_correspondence: bool = False,
) -> list[str]:
    errors: list[str] = []
    for profile in profiles:
        errors.extend(validate_schema(profile, schema))
        errors.extend(validate_semantics(profile))
        if catalog_correspondence:
            errors.extend(validate_catalog_correspondence(profile))

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


def validate_paths(
    paths: Sequence[Path], *, catalog_correspondence: bool = False
) -> list[str]:
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
    errors.extend(
        validate_collection(
            profiles,
            schema,
            enums,
            catalog_correspondence=catalog_correspondence,
        )
    )
    return sorted(set(errors))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown profile files or directories",
    )
    parser.add_argument(
        "--catalog",
        action="store_true",
        help="Validate every canonical profile under funds/ and ecosystem/.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.catalog and args.paths:
        print("--catalog cannot be combined with explicit paths", file=sys.stderr)
        return 2
    if not args.catalog and not args.paths:
        print("provide profile paths or use --catalog", file=sys.stderr)
        return 2
    paths = catalog_profile_paths() if args.catalog else args.paths
    errors = validate_paths(paths, catalog_correspondence=args.catalog)
    if errors:
        print("SEO/GEO profile validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("SEO/GEO profile validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
