#!/usr/bin/env python3
"""Generate deterministic JSON and CSV exports from canonical profile metadata."""

from __future__ import annotations

import argparse
import csv
from io import StringIO
import json
from pathlib import Path
import sys
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SEO_GEO_ROOT = Path(__file__).resolve().parent
if str(SEO_GEO_ROOT) not in sys.path:
    sys.path.insert(0, str(SEO_GEO_ROOT))

from validate_profiles import (  # noqa: E402
    catalog_profile_paths,
    parse_profile,
    read_contract,
    validate_collection,
)


DATA_ROOT = REPOSITORY_ROOT / "data"
SCHEMA_PATH = DATA_ROOT / "entities.schema.json"
JSON_PATH = DATA_ROOT / "entities.json"
CSV_PATH = DATA_ROOT / "entities.csv"
DATASET_VERSION = "2026-08-04"
DATASET_DATE = "2026-08-04"
LICENSE = "CC0-1.0"
LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
CSV_FIELDS = (
    "id",
    "name",
    "entity_type",
    "summary",
    "aliases",
    "operator",
    "base_geography_kind",
    "base_geography_code",
    "countries_covered",
    "stages",
    "focuses",
    "official_website",
    "founder_route",
    "sources",
    "verified_on",
    "source_profile",
    "dataset_version",
    "dataset_date",
    "license",
)
JSON_LIST_FIELDS = {
    "aliases",
    "countries_covered",
    "stages",
    "focuses",
    "sources",
}
NULLABLE_FIELDS = {"operator", "official_website", "founder_route"}


def compact_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def load_entities() -> list[dict[str, Any]]:
    profile_schema, enums = read_contract()
    profiles = [parse_profile(path) for path in catalog_profile_paths()]
    errors = validate_collection(
        profiles,
        profile_schema,
        enums,
        catalog_correspondence=True,
    )
    if errors:
        raise ValueError("invalid canonical profiles:\n" + "\n".join(errors))

    entities = []
    for profile in profiles:
        metadata = profile.metadata
        entities.append(
            {
                "id": metadata["entity_id"],
                "name": metadata["name"],
                "entity_type": metadata["entity_type"],
                "summary": metadata["summary"],
                "aliases": metadata["aliases"],
                "operator": metadata["operator"],
                "base_geography": metadata["base_geography"],
                "countries_covered": metadata["countries_covered"],
                "stages": metadata["stages"],
                "focuses": metadata["focuses"],
                "official_website": metadata["official_website"],
                "founder_route": metadata["founder_route"],
                "sources": metadata["sources"],
                "verified_on": metadata["last_verified"],
                "source_profile": profile.path.relative_to(
                    REPOSITORY_ROOT
                ).as_posix(),
            }
        )
    entities.sort(key=lambda item: item["id"])
    return entities


def json_document(entities: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "dataset": {
            "id": "awesome-latam-vc-entities",
            "name": "Awesome LatAm VC catalog entities",
            "version": DATASET_VERSION,
            "date": DATASET_DATE,
            "license": LICENSE,
            "license_url": LICENSE_URL,
            "encoding": "UTF-8",
            "entity_count": len(entities),
        },
        "entities": entities,
    }


def json_bytes(entities: list[dict[str, Any]]) -> bytes:
    return (
        json.dumps(
            json_document(entities),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def csv_value(entity: dict[str, Any], field: str) -> str:
    if field in JSON_LIST_FIELDS:
        return compact_json(entity[field])
    if field in NULLABLE_FIELDS:
        return "" if entity[field] is None else str(entity[field])
    if field == "base_geography_kind":
        return entity["base_geography"]["kind"]
    if field == "base_geography_code":
        return entity["base_geography"]["code"]
    if field == "dataset_version":
        return DATASET_VERSION
    if field == "dataset_date":
        return DATASET_DATE
    if field == "license":
        return LICENSE
    return str(entity[field])


def csv_bytes(entities: list[dict[str, Any]]) -> bytes:
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=CSV_FIELDS,
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()
    for entity in entities:
        writer.writerow(
            {field: csv_value(entity, field) for field in CSV_FIELDS}
        )
    return output.getvalue().encode("utf-8")


def parse_csv(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8")
    return list(csv.DictReader(StringIO(text, newline="")))


def validate_export_consistency(
    json_payload: bytes,
    csv_payload: bytes,
    schema: dict[str, Any] | None = None,
) -> list[str]:
    errors = []
    try:
        document = json.loads(json_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"invalid JSON export: {exc}"]
    try:
        rows = parse_csv(csv_payload)
    except (UnicodeDecodeError, csv.Error) as exc:
        return [f"invalid CSV export: {exc}"]

    if schema is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(
        schema, format_checker=FormatChecker()
    )
    for error in sorted(
        validator.iter_errors(document), key=lambda item: list(item.path)
    ):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"schema {location}: {error.message}")

    entities = document.get("entities", [])
    if not isinstance(entities, list):
        return sorted(set(errors))
    json_ids = [
        item.get("id") for item in entities if isinstance(item, dict)
    ]
    csv_ids = [row.get("id") for row in rows]
    if len(json_ids) != len(set(json_ids)):
        errors.append("duplicate entity ID in JSON")
    if len(csv_ids) != len(set(csv_ids)):
        errors.append("duplicate entity ID in CSV")
    if json_ids != sorted(json_ids):
        errors.append("JSON entities are not sorted by ID")
    if csv_ids != json_ids:
        errors.append("JSON and CSV entity IDs or order differ")
    if document.get("dataset", {}).get("entity_count") != len(entities):
        errors.append("dataset entity_count differs from JSON entities")

    rows_by_id = {row.get("id"): row for row in rows}
    for entity in entities:
        if not isinstance(entity, dict) or entity.get("id") not in rows_by_id:
            continue
        row = rows_by_id[entity["id"]]
        expected = {
            field: csv_value(entity, field) for field in CSV_FIELDS
        }
        for field in CSV_FIELDS:
            if row.get(field) != expected[field]:
                errors.append(
                    f"{entity['id']}: CSV field differs from JSON: {field}"
                )
    return sorted(set(errors))


def build_outputs() -> dict[Path, bytes]:
    entities = load_entities()
    return {
        JSON_PATH: json_bytes(entities),
        CSV_PATH: csv_bytes(entities),
    }


def write_or_check(check: bool) -> int:
    outputs = build_outputs()
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    consistency_errors = validate_export_consistency(
        outputs[JSON_PATH], outputs[CSV_PATH], schema
    )
    if consistency_errors:
        print("Structured export validation failed:", file=sys.stderr)
        for error in consistency_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if check:
        drift = [
            path.relative_to(REPOSITORY_ROOT).as_posix()
            for path, expected in outputs.items()
            if not path.is_file() or path.read_bytes() != expected
        ]
        if drift:
            print("Structured export drift: " + ", ".join(drift))
            return 1
        print("Structured exports are deterministic and valid.")
        return 0
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs.items():
        path.write_bytes(payload)
    print(f"Wrote {len(outputs)} structured exports.")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    return write_or_check(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
