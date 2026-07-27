#!/usr/bin/env python3
"""Validate answer-oriented editorial and landing-page content."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from jsonschema import Draft202012Validator, FormatChecker


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CONTENT_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "content"
EDITORIAL_SCHEMA_PATH = CONTENT_ROOT / "editorial-page.schema.json"
LANDING_SCHEMA_PATH = CONTENT_ROOT / "landing-page.schema.json"
EDITORIAL_ROOT = CONTENT_ROOT / "editorial"
LANDING_ROOT = CONTENT_ROOT / "landings"
LOCALES = ("en", "pt-BR", "es")
REQUIRED_EDITORIAL_SLUGS = {
    "methodology",
    "inclusion",
    "sources",
    "updates",
    "license",
    "limitations",
    "citation",
}
REQUIRED_SECTIONS = {
    "methodology": {
        "How the directory is built",
        "What the data means",
        "Quality controls",
        "References",
    },
    "inclusion": {
        "Included entities",
        "Excluded entities",
        "Decision boundaries",
        "References",
    },
    "sources": {
        "Source hierarchy",
        "How evidence is recorded",
        "When evidence is insufficient",
        "References",
    },
    "updates": {
        "Update cycle",
        "Verification dates",
        "Corrections",
        "References",
    },
    "license": {
        "Repository content",
        "Third-party material",
        "Attribution",
        "References",
    },
    "limitations": {
        "Coverage limitations",
        "Data limitations",
        "How to interpret absence",
        "References",
    },
    "citation": {
        "Preferred citation",
        "Dataset citation",
        "Stable references",
        "References",
    },
}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https://[^)\s]+)\)")
FENCED_BLOCK_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class Document:
    path: Path
    metadata: dict
    body: str

    @property
    def display_path(self) -> str:
        try:
            return self.path.relative_to(REPOSITORY_ROOT).as_posix()
        except ValueError:
            return self.path.as_posix()


def read_schema(path: Path) -> dict:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def parse_document(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("front matter must start with ---")
    closing = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        ),
        None,
    )
    if closing is None:
        raise ValueError("front matter closing --- is missing")
    try:
        metadata = json.loads("".join(lines[1:closing]).strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"front matter must be a JSON object: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError("front matter must contain an object")
    body = "".join(lines[closing + 1 :]).lstrip("\r\n")
    if not body.strip():
        raise ValueError("Markdown body is empty")
    return Document(path=path, metadata=metadata, body=body)


def schema_errors(document: Document, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for error in sorted(
        validator.iter_errors(document.metadata), key=lambda item: list(item.path)
    ):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{document.display_path}: {location}: {error.message}")
    return errors


def introduction(body: str) -> str:
    after_h1 = re.split(r"^#\s+.+?$", body, maxsplit=1, flags=re.MULTILINE)
    if len(after_h1) != 2:
        return ""
    return re.split(r"^##\s+", after_h1[1], maxsplit=1, flags=re.MULTILINE)[
        0
    ].strip()


def validate_editorial_document(document: Document, schema: dict) -> list[str]:
    errors = schema_errors(document, schema)
    metadata = document.metadata
    slug = metadata.get("slug")
    locale = metadata.get("locale")
    expected_id = f"editorial:{slug}:{locale}"
    if metadata.get("id") != expected_id:
        errors.append(f"{document.display_path}: id must equal {expected_id}")

    headings = HEADING_RE.findall(document.body)
    h1s = [text for level, text in headings if level == "#"]
    if h1s != [metadata.get("title")]:
        errors.append(
            f"{document.display_path}: body must have one H1 matching title"
        )

    answer = introduction(document.body)
    word_count = len(answer.split())
    if not answer:
        errors.append(f"{document.display_path}: direct answer is missing after H1")
    elif word_count > 80:
        errors.append(
            f"{document.display_path}: direct answer has {word_count} words; maximum is 80"
        )

    second_level = {text for level, text in headings if level == "##"}
    missing_sections = REQUIRED_SECTIONS.get(slug, set()) - second_level
    if missing_sections:
        errors.append(
            f"{document.display_path}: missing sections: "
            f"{', '.join(sorted(missing_sections))}"
        )
    if any(text.casefold() in {"faq", "frequently asked questions"} for text in second_level):
        errors.append(f"{document.display_path}: synthetic FAQ sections are prohibited")

    declared_references = Counter(
        (item["title"], item["url"])
        for item in metadata.get("references", [])
        if isinstance(item, dict) and "title" in item and "url" in item
    )
    visible_references = Counter(MARKDOWN_LINK_RE.findall(document.body))
    for reference, count in declared_references.items():
        if visible_references[reference] < count:
            errors.append(
                f"{document.display_path}: reference is not rendered: "
                f"{reference[0]} ({reference[1]})"
            )
    if not declared_references:
        errors.append(f"{document.display_path}: at least one reference is required")

    if slug == "citation":
        blocks = "\n".join(FENCED_BLOCK_RE.findall(document.body))
        for token in (
            "https://github.com/djairofilho/awesome-latam-vc",
            "YYYY-MM-DD",
            "COMMIT_SHA",
        ):
            if token not in blocks:
                errors.append(
                    f"{document.display_path}: citation template is missing {token}"
                )
    return errors


def load_documents(paths: Iterable[Path]) -> tuple[list[Document], list[str]]:
    documents = []
    errors = []
    for path in sorted(paths):
        try:
            documents.append(parse_document(path))
        except (OSError, ValueError) as exc:
            errors.append(f"{path.as_posix()}: {exc}")
    return documents, errors


def validate_editorial_collection(
    root: Path = EDITORIAL_ROOT,
    *,
    require_complete_locales: bool = False,
) -> list[str]:
    schema = read_schema(EDITORIAL_SCHEMA_PATH)
    documents, errors = load_documents(root.glob("*/*.md"))
    for document in documents:
        errors.extend(validate_editorial_document(document, schema))

    ids = Counter(document.metadata.get("id") for document in documents)
    pairs = Counter(
        (document.metadata.get("slug"), document.metadata.get("locale"))
        for document in documents
    )
    for identifier, count in ids.items():
        if identifier and count > 1:
            errors.append(f"duplicate editorial id: {identifier}")
    for pair, count in pairs.items():
        if all(pair) and count > 1:
            errors.append(f"duplicate editorial slug/locale: {pair[0]}:{pair[1]}")

    by_pair = {
        (document.metadata.get("slug"), document.metadata.get("locale")): document
        for document in documents
    }
    english_slugs = {
        slug for slug, locale in by_pair if locale == "en" and isinstance(slug, str)
    }
    missing_english = REQUIRED_EDITORIAL_SLUGS - english_slugs
    if missing_english:
        errors.append(
            f"missing canonical editorial pages: {', '.join(sorted(missing_english))}"
        )

    for document in documents:
        metadata = document.metadata
        if metadata.get("locale") == "en":
            continue
        canonical = by_pair.get((metadata.get("slug"), "en"))
        if canonical is None:
            errors.append(f"{document.display_path}: canonical English page is missing")
            continue
        if metadata.get("translation_of") != canonical.metadata.get("id"):
            errors.append(
                f"{document.display_path}: translation_of must point to "
                f"{canonical.metadata.get('id')}"
            )
        if metadata.get("references") != canonical.metadata.get("references"):
            errors.append(
                f"{document.display_path}: protected references differ from canonical"
            )

    if require_complete_locales:
        for slug in REQUIRED_EDITORIAL_SLUGS:
            for locale in LOCALES:
                document = by_pair.get((slug, locale))
                if document is None:
                    errors.append(f"missing release page: {slug}:{locale}")
                elif locale != "en" and document.metadata.get("translation_status") != "complete":
                    errors.append(f"incomplete release page: {slug}:{locale}")
    return errors


def validate_landing_collection(root: Path = LANDING_ROOT) -> list[str]:
    schema = read_schema(LANDING_SCHEMA_PATH)
    documents, errors = load_documents(root.glob("*/*.md"))
    introductions: dict[tuple[str, str], Path] = {}
    ids = Counter()
    for document in documents:
        errors.extend(schema_errors(document, schema))
        metadata = document.metadata
        expected_id = (
            f"landing:{metadata.get('subject_type')}:"
            f"{metadata.get('subject_id')}:{metadata.get('locale')}"
        )
        if metadata.get("id") != expected_id:
            errors.append(f"{document.display_path}: id must equal {expected_id}")
        ids[metadata.get("id")] += 1
        answer = introduction(document.body)
        if not answer:
            errors.append(f"{document.display_path}: landing introduction is missing")
            continue
        normalized = re.sub(r"\s+", " ", answer).strip().casefold()
        key = (str(metadata.get("locale")), normalized)
        if key in introductions:
            errors.append(
                f"{document.display_path}: duplicate landing introduction from "
                f"{introductions[key].as_posix()}"
            )
        introductions[key] = document.path
    for identifier, count in ids.items():
        if identifier and count > 1:
            errors.append(f"duplicate landing id: {identifier}")
    return errors


def validate_contract() -> list[str]:
    errors = validate_editorial_collection()
    errors.extend(validate_landing_collection())
    profile_contract = json.loads(
        (CONTENT_ROOT / "profile-answer-contract.json").read_text(encoding="utf-8")
    )
    profile_schema = json.loads(
        (
            REPOSITORY_ROOT
            / "research"
            / "seo-geo"
            / "contract"
            / "profile.schema.json"
        ).read_text(encoding="utf-8")
    )
    properties = set(profile_schema["properties"])
    key_facts = set(profile_contract["sections"]["key_facts"]["fields"])
    unknown = key_facts - properties
    if unknown:
        errors.append(
            "profile answer contract references unknown fields: "
            + ", ".join(sorted(unknown))
        )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-complete-locales",
        action="store_true",
        help="require complete EN, PT-BR and ES editorial coverage",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors = validate_editorial_collection(
        require_complete_locales=args.require_complete_locales
    )
    errors.extend(validate_landing_collection())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Answer-oriented editorial content validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
