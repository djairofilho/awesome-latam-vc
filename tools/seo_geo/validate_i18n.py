#!/usr/bin/env python3
"""Validate locale routes and canonical-to-translation associations."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence

try:
    from .validate_profiles import (
        Profile,
        catalog_profile_paths,
        parse_profile,
        read_contract,
        validate_collection,
    )
except ImportError:
    from validate_profiles import (
        Profile,
        catalog_profile_paths,
        parse_profile,
        read_contract,
        validate_collection,
    )


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
I18N_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "i18n"
CONFIG_PATH = I18N_ROOT / "locales.json"
PROFILE_PREFIXES = ("funds/", "ecosystem/")


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    canonical_count: int
    localized_counts: dict[str, int]


def load_config(path: Path = CONFIG_PATH) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "site_origin",
        "site_base",
        "canonical_locale",
        "x_default_path",
        "locales",
        "migration_fallback",
        "release",
    }
    missing = sorted(required - set(config))
    if missing:
        raise ValueError(f"locale config is missing fields: {', '.join(missing)}")
    locales = config["locales"]
    if not isinstance(locales, dict) or not locales:
        raise ValueError("locale config must declare locales")
    if config["canonical_locale"] not in locales:
        raise ValueError("canonical_locale must reference a declared locale")
    route_segments = [row.get("route_segment") for row in locales.values()]
    if len(route_segments) != len(set(route_segments)):
        raise ValueError("locale route segments must be unique")
    for locale, row in locales.items():
        if row.get("html_lang") != locale:
            raise ValueError(f"{locale}: html_lang must equal the metadata locale")
        segment = row.get("route_segment")
        if (
            not isinstance(segment, str)
            or not segment
            or segment != segment.lower()
            or "/" in segment
        ):
            raise ValueError(f"{locale}: invalid route segment")
    site_base = config["site_base"]
    if not isinstance(site_base, str) or not site_base.startswith("/"):
        raise ValueError("site_base must be an absolute path")
    return config


def normalize_suffix(suffix: str = "/") -> str:
    if "?" in suffix or "#" in suffix:
        raise ValueError("localized route suffix cannot contain query or fragment")
    raw_parts = suffix.replace("\\", "/").split("/")
    if ".." in raw_parts:
        raise ValueError("localized route suffix cannot traverse directories")
    parts = PurePosixPath("/" + suffix.lstrip("/")).parts
    cleaned = "/" + "/".join(part for part in parts if part != "/")
    return "/" if cleaned == "/" else cleaned.rstrip("/") + "/"


def localized_route(config: dict, locale: str, suffix: str = "/") -> str:
    try:
        segment = config["locales"][locale]["route_segment"]
    except KeyError as exc:
        raise ValueError(f"unsupported locale: {locale}") from exc
    normalized = normalize_suffix(suffix)
    return f"/{segment}/" if normalized == "/" else f"/{segment}{normalized}"


def switch_locale(config: dict, route: str, target_locale: str) -> str:
    normalized = normalize_suffix(route)
    route_to_locale = {
        f"/{row['route_segment']}/": locale
        for locale, row in config["locales"].items()
    }
    prefix = next(
        (candidate for candidate in route_to_locale if normalized.startswith(candidate)),
        None,
    )
    if prefix is None:
        raise ValueError(f"route has no supported locale prefix: {route}")
    suffix = normalized[len(prefix) :]
    return localized_route(config, target_locale, suffix)


def with_base(config: dict, route: str = "/") -> str:
    normalized = normalize_suffix(route)
    base = config["site_base"].rstrip("/")
    return f"{base}{normalized}" if base else normalized


def public_url(config: dict, route: str = "/") -> str:
    return f"{config['site_origin'].rstrip('/')}{with_base(config, route)}"


def hreflang_urls(
    config: dict,
    suffix: str,
    available_locales: Sequence[str],
) -> dict[str, str]:
    unsupported = sorted(set(available_locales) - set(config["locales"]))
    if unsupported:
        raise ValueError(f"unsupported hreflang locales: {', '.join(unsupported)}")
    normalized = normalize_suffix(suffix)
    links = {
        config["locales"][locale]["html_lang"]: public_url(
            config,
            localized_route(config, locale, normalized),
        )
        for locale in config["locales"]
        if locale in available_locales
    }
    if normalized == "/":
        x_default_route = config["x_default_path"]
    else:
        x_default_route = localized_route(
            config,
            config["canonical_locale"],
            normalized,
        )
    links["x-default"] = public_url(config, x_default_route)
    return links


def canonical_relative_path(path: Path, root: Path = REPOSITORY_ROOT) -> str:
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    if not relative.startswith(PROFILE_PREFIXES):
        raise ValueError(f"not a canonical catalog profile: {relative}")
    return relative


def expected_translation_path(
    config: dict,
    locale: str,
    canonical_relative: str,
    root: Path = REPOSITORY_ROOT,
) -> Path:
    content_root = config["locales"][locale]["content_root"]
    if not content_root:
        return root / canonical_relative
    return root / content_root / canonical_relative


def discover_translation_paths(config: dict, root: Path) -> list[Path]:
    paths: list[Path] = []
    canonical_locale = config["canonical_locale"]
    for locale, row in config["locales"].items():
        if locale == canonical_locale:
            continue
        content_root = row["content_root"]
        if not content_root:
            continue
        directory = root / content_root
        if directory.is_dir():
            paths.extend(
                path.resolve()
                for path in directory.rglob("*.md")
                if not path.name.startswith("README")
            )
    return sorted(paths)


def translation_relative_path(config: dict, profile: Profile, root: Path) -> str:
    locale = profile.metadata.get("locale")
    row = config["locales"].get(locale)
    if not row or not row.get("content_root"):
        raise ValueError(f"{profile.display_path}: translation locale/path mismatch")
    translation_root = (root / row["content_root"]).resolve()
    try:
        return profile.path.resolve().relative_to(translation_root).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"{profile.display_path}: translation is outside {row['content_root']}"
        ) from exc


def validate_i18n(
    *,
    root: Path = REPOSITORY_ROOT,
    release: bool = False,
    config_path: Path | None = None,
) -> ValidationResult:
    config = load_config(config_path or root / CONFIG_PATH.relative_to(REPOSITORY_ROOT))
    schema, enums = read_contract()
    errors: list[str] = []
    warnings: list[str] = []

    canonical_paths = (
        catalog_profile_paths()
        if root.resolve() == REPOSITORY_ROOT.resolve()
        else sorted(
            [
                path.resolve()
                for path in (root / "funds").rglob("*.md")
                if path.name != "README.md"
            ]
            + [
                path.resolve()
                for path in (root / "ecosystem").rglob("*.md")
                if not path.name.startswith("README")
            ]
        )
    )
    canonical_profiles: list[Profile] = []
    translations: list[Profile] = []
    for path in canonical_paths:
        try:
            canonical_profiles.append(parse_profile(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path.as_posix()}: {exc}")
    for path in discover_translation_paths(config, root):
        try:
            translations.append(parse_profile(path))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{path.as_posix()}: {exc}")

    errors.extend(validate_collection(canonical_profiles + translations, schema, enums))
    canonical_by_entity = {
        profile.metadata.get("entity_id"): profile for profile in canonical_profiles
    }
    translations_by_entity_locale = {
        (profile.metadata.get("entity_id"), profile.metadata.get("locale")): profile
        for profile in translations
    }
    localized_counts = {
        locale: (
            len(canonical_profiles)
            if locale == config["canonical_locale"]
            else sum(
                profile.metadata.get("locale") == locale for profile in translations
            )
        )
        for locale in config["locales"]
    }

    canonical_slugs: dict[str, str] = {}
    for entity_id, canonical in canonical_by_entity.items():
        slug = canonical.metadata.get("slug")
        if isinstance(slug, str):
            if slug in canonical_slugs and canonical_slugs[slug] != entity_id:
                errors.append(
                    f"route slug collision {slug}: "
                    f"{canonical_slugs[slug]}, {entity_id}"
                )
            canonical_slugs[slug] = entity_id

    for translation in translations:
        try:
            relative = translation_relative_path(config, translation, root)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        entity_id = translation.metadata.get("entity_id")
        canonical = canonical_by_entity.get(entity_id)
        if canonical is None:
            errors.append(f"{translation.display_path}: orphan translation")
            continue
        expected_relative = canonical_relative_path(canonical.path, root)
        if relative != expected_relative:
            errors.append(
                f"{translation.display_path}: translation path must mirror "
                f"{expected_relative}"
            )

    accepted_statuses = config["release"]["accepted_translation_statuses"]
    required_locales = config["release"]["required_locales"]
    for entity_id, canonical in sorted(canonical_by_entity.items()):
        canonical_relative = canonical_relative_path(canonical.path, root)
        for locale in required_locales:
            if locale == config["canonical_locale"]:
                continue
            translation = translations_by_entity_locale.get((entity_id, locale))
            expected = expected_translation_path(
                config,
                locale,
                canonical_relative,
                root,
            ).relative_to(root).as_posix()
            if translation is None:
                message = f"{entity_id}@{locale}: missing translation at {expected}"
                (errors if release else warnings).append(message)
                continue
            status = translation.metadata.get("translation_status")
            if status not in accepted_statuses[locale]:
                message = (
                    f"{translation.display_path}: translation status {status!r} "
                    f"is not release-complete"
                )
                (errors if release else warnings).append(message)

    return ValidationResult(
        errors=tuple(sorted(set(errors))),
        warnings=tuple(sorted(set(warnings))),
        canonical_count=len(canonical_profiles),
        localized_counts=localized_counts,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--release",
        action="store_true",
        help="Treat missing or needs-review translations as errors.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every migration warning instead of only the total.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = validate_i18n(release=args.release)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"SEO/GEO i18n validation failed: {exc}", file=sys.stderr)
        return 1
    if args.verbose:
        for warning in result.warnings:
            print(f"warning: {warning}", file=sys.stderr)
    if result.errors:
        print("SEO/GEO i18n validation failed:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    counts = ", ".join(
        f"{locale}={count}" for locale, count in result.localized_counts.items()
    )
    print(
        f"SEO/GEO i18n validation passed "
        f"({result.canonical_count} canonical; {counts}; "
        f"warnings={len(result.warnings)})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
