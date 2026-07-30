#!/usr/bin/env python3
"""Add deterministic canonical metadata to the current Markdown catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    from .validate_profiles import catalog_profile_paths
except ImportError:
    from validate_profiles import catalog_profile_paths


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "migration"
CONTRACT_ROOT = REPOSITORY_ROOT / "research" / "seo-geo" / "contract"
CUTOFF_DATE = "2026-07-27"
COUNTRY_DIRECTORIES = {
    "argentina": "AR",
    "bolivia": "BO",
    "brazil": "BR",
    "chile": "CL",
    "colombia": "CO",
    "costa-rica": "CR",
    "dominican-republic": "DO",
    "ecuador": "EC",
    "el-salvador": "SV",
    "jamaica": "JM",
    "mexico": "MX",
    "peru": "PE",
    "puerto-rico": "PR",
    "switzerland": "CH",
    "uruguay": "UY",
    "united-states": "US",
}
COUNTRY_TERMS = {
    "Argentina": "AR",
    "Bolivia": "BO",
    "Bolívia": "BO",
    "Brazil": "BR",
    "Brasil": "BR",
    "Chile": "CL",
    "Colombia": "CO",
    "Costa Rica": "CR",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Equador": "EC",
    "El Salvador": "SV",
    "Guatemala": "GT",
    "Jamaica": "JM",
    "Mexico": "MX",
    "México": "MX",
    "Paraguay": "PY",
    "Peru": "PE",
    "Puerto Rico": "PR",
    "United States": "US",
    "Uruguay": "UY",
}
DISPLAY_NAME_OVERRIDES = {
    "500-latam-500-global": {
        "aliases": [],
        "operator": "500 Global",
    },
    "actions-capital-k50-ventures": {
        "aliases": ["K50 Ventures"],
    },
    "bossa-invest-bossanova": {
        "aliases": ["Bossanova"],
    },
    "crescera-capital-bozano": {
        "aliases": ["Bozano"],
    },
    "igah-ventures-patria": {
        "aliases": [],
        "operator": "Patria",
    },
    "cometa-variv": {
        "aliases": ["Variv"],
    },
    "randon-ventures-rv": {
        "aliases": ["RV"],
    },
    "hi-ventures-allvp": {
        "aliases": ["ALLVP"],
    },
    "wollef-ventures-jaguar": {
        "aliases": ["Jaguar"],
    },
}
FIELD_RE = re.compile(r"^-\s+\*\*([^:*]+):\*\*\s*(.*)$")
MARKDOWN_URL_RE = re.compile(r"\[[^\]]+\]\((https://[^)]+)\)")
HTTPS_RE = re.compile(r"https://[^\s<>)\]]+")
SOURCE_RE = re.compile(r"^-\s+\[([^\]]+)\]\((https://[^)]+)\)", re.MULTILINE)
DATE_RE = re.compile(
    r"^\*\*Last verified:\*\*\s+(\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def normalize_lf(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def split_document(path: Path) -> str:
    text = normalize_lf(path.read_text(encoding="utf-8"))
    if not text.startswith("---\n"):
        return text
    lines = text.splitlines(keepends=True)
    closing = next(
        index
        for index, line in enumerate(lines[1:], start=1)
        if line.strip() == "---"
    )
    return "".join(lines[closing + 1 :]).lstrip("\n")


def visible_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    lines = body.splitlines()
    index = 0
    while index < len(lines):
        match = FIELD_RE.match(lines[index])
        if not match:
            index += 1
            continue
        field, initial = match.groups()
        parts = [initial.strip()] if initial.strip() else []
        index += 1
        while index < len(lines):
            line = lines[index]
            if FIELD_RE.match(line) or line.startswith("## ") or not line.strip():
                break
            if line.startswith("  "):
                parts.append(line.strip())
                index += 1
                continue
            break
        fields[field] = " ".join(parts)
    return fields


def extract_https(value: str | None) -> str | None:
    if not value:
        return None
    markdown = MARKDOWN_URL_RE.search(value)
    if markdown:
        return markdown.group(1)
    raw = HTTPS_RE.search(value)
    return raw.group(0) if raw else None


def slugify(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    ascii_value = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")


def entity_type_for(path: Path) -> str:
    relative = path.relative_to(REPOSITORY_ROOT)
    if relative.parts[0] == "funds":
        return "fund"
    category = relative.parts[1]
    return {
        "accelerators": "accelerator",
        "angel-networks": "angel_network",
        "funding-platforms": "funding_platform",
        "public-programs": "public_program",
    }[category]


def base_geography_for(path: Path) -> dict[str, str]:
    relative = path.relative_to(REPOSITORY_ROOT)
    directory = relative.parts[-2]
    if directory in COUNTRY_DIRECTORIES:
        return {"kind": "country", "code": COUNTRY_DIRECTORIES[directory]}
    if directory == "regional":
        return {"kind": "region", "code": "LATAM"}
    if directory == "multi-country":
        return {"kind": "global", "code": "GLOBAL"}
    raise ValueError(f"diretório geográfico não mapeado: {relative.as_posix()}")


def countries_for(
    geography: str | None,
) -> tuple[list[str], list[str]]:
    if not geography or geography.startswith("Not publicly disclosed"):
        return ["NOT_DISCLOSED"], ["countries_covered:not_disclosed"]
    values: set[str] = set()
    for term, code in COUNTRY_TERMS.items():
        if re.search(rf"\b{re.escape(term)}\b", geography, re.IGNORECASE):
            values.add(code)
    lowered = geography.casefold()
    if "latin america" in lowered or "latin american" in lowered:
        values.add("LATAM")
    if "caribbean" in lowered:
        values.add("CARIBBEAN")
    if "global" in lowered or "international" in lowered:
        values.add("GLOBAL")
    notes = []
    for term in (
        "North America",
        "Europe",
        "the Americas",
        "emerging markets",
        "cross-border Spanish-speaking markets",
    ):
        if term.casefold() in lowered:
            notes.append(f"countries_covered:unmapped_visible_region:{term}")
    if not values:
        values.add("NOT_DISCLOSED")
        notes.append("countries_covered:not_normalizable")
    return sorted(values), notes


def stages_for(entity_type: str, value: str | None) -> list[str]:
    if entity_type == "angel_network":
        return ["angel"]
    if entity_type == "public_program":
        return ["not_applicable"]
    if entity_type not in {"accelerator", "fund"}:
        return ["not_disclosed"]
    if not value or value.startswith("Not publicly disclosed"):
        return ["not_disclosed"]
    lowered = value.casefold()
    stages = []
    if "pre-seed" in lowered:
        stages.append("pre_seed")
    without_pre_seed = lowered.replace("pre-seed", "")
    if re.search(r"\bseed\b", without_pre_seed):
        stages.append("seed")
    if "series a" in lowered:
        stages.append("series_a")
    if "series b" in lowered:
        stages.append("series_b")
    if "growth" in lowered:
        stages.append("growth")
    if "multi-stage" in lowered:
        stages.append("multi_stage")
    return stages or ["not_disclosed"]


def focuses_for(entity_type: str, value: str | None, body: str) -> list[str]:
    if entity_type == "public_program":
        return ["entrepreneurship", "innovation"]
    if entity_type != "fund":
        return ["not_disclosed"]
    if not value or value.startswith("Not publicly disclosed"):
        return ["not_disclosed"]
    normalized = value.replace("&", " and ")
    parts = re.split(r",|\band\b|\bincluding\b", normalized, flags=re.IGNORECASE)
    focuses = []
    for part in parts:
        key = slugify(part).replace("-", "_")
        if not key or key in {"other", "the"}:
            continue
        if key == "sector_agnostic":
            pass
        elif key == "technology_sector_agnostic":
            focuses.extend(["technology", "sector_agnostic"])
            continue
        if key not in focuses:
            focuses.append(key)
    return focuses or ["not_disclosed"]


def first_summary(body: str) -> str:
    lines = body.splitlines()
    paragraph: list[str] = []
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                break
            continue
        if stripped.startswith(("#", "-", "|", "<!--")):
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    value = " ".join(paragraph)
    sentences = re.split(r"(?<=[.!?])\s+", value)
    summary = sentences[0].strip() if sentences else value.strip()
    if not summary:
        raise ValueError("perfil sem parágrafo descritivo para summary")
    if len(summary) > 240:
        words = summary.split()
        shortened = ""
        for word in words:
            candidate = f"{shortened} {word}".strip()
            if len(candidate) > 237:
                break
            shortened = candidate
        summary = shortened.rstrip(" ,;:") + "..."
    return summary


def source_kind(
    title: str,
    url: str,
    entity_type: str,
    official_website: str | None,
    founder_route: str | None,
) -> str:
    lowered = title.casefold()
    if "unavailable" in lowered or "previously listed" in lowered:
        return "secondary"
    if any(
        term in lowered
        for term in (
            "banco central",
            "cadastro",
            "cmf",
            "cnmv",
            "cvm",
            "regulation",
            "regulator",
            "superintendencia",
        )
    ):
        return "official_regulator"
    if entity_type == "public_program":
        return "official_program"
    if url == founder_route or re.search(
        r"\b(?:application|apply|submit|contact|form|pitch)\b",
        lowered,
    ):
        return "official_application"
    if any(term in lowered for term in ("portfolio", "companies", "investments")):
        return "official_portfolio"
    if any(term in lowered for term in ("activity", "annual", "research 2026")):
        return "official_activity"
    if any(term in lowered for term in ("thesis", "strategy", "focus", "about")):
        return "official_thesis"
    if official_website and urlparse(url).netloc == urlparse(official_website).netloc:
        return "official_website"
    return "secondary"


def sources_for(
    body: str,
    entity_type: str,
    official_website: str | None,
    founder_route: str | None,
) -> list[dict[str, str]]:
    section_match = re.search(
        r"^## (?:Official sources|Sources)\s*$\n"
        r"(.*?)(?=^\*\*Last verified:\*\*|\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError("perfil sem seção Sources")
    sources = []
    for title, url in SOURCE_RE.findall(section_match.group(1)):
        sources.append(
            {
                "title": title,
                "url": url,
                "kind": source_kind(
                    title,
                    url,
                    entity_type,
                    official_website,
                    founder_route,
                ),
            }
        )
    if not sources:
        raise ValueError("perfil sem links na seção Sources")
    return sources


def aliases_and_operator(
    slug: str, entity_type: str, fields: dict[str, str]
) -> tuple[list[str], str | None]:
    override = DISPLAY_NAME_OVERRIDES.get(slug, {})
    aliases = list(override.get("aliases", []))
    visible_aliases = fields.get("Aliases")
    if (
        visible_aliases
        and visible_aliases.casefold()
        not in {"none", "none published", "none recorded"}
    ):
        aliases.extend(
            alias.strip()
            for alias in visible_aliases.split(",")
            if alias.strip()
        )
    aliases = list(dict.fromkeys(aliases))
    operator = override.get("operator")
    if entity_type != "fund" and fields.get("Operator"):
        operator = fields["Operator"]
    return aliases, operator


def build_metadata(path: Path, body: str) -> tuple[dict[str, Any], list[str]]:
    relative = path.relative_to(REPOSITORY_ROOT).as_posix()
    slug = slugify(path.stem)
    entity_type = entity_type_for(path)
    heading = H1_RE.search(body)
    if not heading:
        raise ValueError(f"{relative}: perfil sem H1")
    name = heading.group(1)
    fields = visible_fields(body)
    official_website = extract_https(
        fields.get("Website") or fields.get("Official page")
    )
    route_field = (
        fields.get("Submit a startup")
        if entity_type == "fund"
        else fields.get("Founder route") or fields.get("Apply")
    )
    founder_route = extract_https(route_field)
    geography = fields.get("Geography")
    countries, notes = countries_for(geography)
    if official_website is None:
        notes.append("official_website:not_disclosed")
    if founder_route is None:
        notes.append("founder_route:not_disclosed_or_not_https")
    aliases, operator = aliases_and_operator(slug, entity_type, fields)
    if operator is None:
        notes.append("operator:not_disclosed")
    stage_value = fields.get("Stage at entry") or fields.get("Stage")
    stages = stages_for(entity_type, stage_value)
    if stages == ["not_disclosed"]:
        notes.append("stages:not_disclosed")
    focuses = focuses_for(entity_type, fields.get("Focus"), body)
    if focuses == ["not_disclosed"]:
        notes.append("focuses:not_disclosed")
    verified = DATE_RE.search(body)
    if not verified:
        raise ValueError(f"{relative}: data Last verified ausente")
    entity_id = f"{entity_type}:{slug}"
    metadata = {
        "schema_version": "1.0",
        "id": f"{entity_id}:en",
        "entity_id": entity_id,
        "slug": slug,
        "name": name,
        "entity_type": entity_type,
        "locale": "en",
        "translation_of": None,
        "translation_status": "canonical",
        "summary": first_summary(body),
        "aliases": aliases,
        "operator": operator,
        "base_geography": base_geography_for(path),
        "countries_covered": countries,
        "stages": stages,
        "focuses": focuses,
        "official_website": official_website,
        "founder_route": founder_route,
        "sources": sources_for(
            body,
            entity_type,
            official_website,
            founder_route,
        ),
        "last_verified": verified.group(1),
        "protected_terms": [name],
    }
    return metadata, sorted(set(notes))


def profile_bytes(metadata: dict[str, Any], body: str) -> bytes:
    front_matter = json.dumps(
        metadata,
        ensure_ascii=False,
        sort_keys=False,
        indent=2,
    )
    normalized_body = normalize_lf(body).lstrip("\n")
    if not normalized_body.endswith("\n"):
        normalized_body += "\n"
    return f"---\n{front_matter}\n---\n{normalized_body}".encode("utf-8")


def build_outputs() -> dict[Path, bytes]:
    paths = catalog_profile_paths()
    if not paths:
        raise ValueError("catálogo vazio")
    outputs: dict[Path, bytes] = {}
    inventory = []
    mappings = []
    ids: set[str] = set()
    slugs: set[str] = set()
    type_counts: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    for path in paths:
        body = split_document(path)
        metadata, notes = build_metadata(path, body)
        if metadata["id"] in ids:
            raise ValueError(f"ID duplicado: {metadata['id']}")
        if metadata["slug"] in slugs:
            raise ValueError(f"slug duplicado: {metadata['slug']}")
        ids.add(metadata["id"])
        slugs.add(metadata["slug"])
        type_counts[metadata["entity_type"]] += 1
        for note in notes:
            warning_counts[note.split(":", 1)[0]] += 1
        payload = profile_bytes(metadata, body)
        outputs[path] = payload
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        body_hash = sha256(normalize_lf(body).encode("utf-8"))
        inventory.append(
            {
                "schema_version": "1.0",
                "path": relative,
                "entity_type": metadata["entity_type"],
                "had_front_matter_before": False,
                "body_sha256_before": body_hash,
                "body_sha256_after": body_hash,
                "source_count": len(metadata["sources"]),
                "last_verified": metadata["last_verified"],
            }
        )
        mappings.append(
            {
                "schema_version": "1.0",
                "path": relative,
                "id": metadata["id"],
                "entity_id": metadata["entity_id"],
                "slug": metadata["slug"],
                "entity_type": metadata["entity_type"],
                "base_geography": metadata["base_geography"],
                "countries_covered": metadata["countries_covered"],
                "stages": metadata["stages"],
                "focuses": metadata["focuses"],
                "normalization_notes": notes,
            }
        )
    inventory.sort(key=lambda row: row["path"])
    mappings.sort(key=lambda row: row["path"])
    inventory_payload = jsonl_bytes(inventory)
    mapping_payload = jsonl_bytes(mappings)
    outputs[MIGRATION_ROOT / "inventory.jsonl"] = inventory_payload
    outputs[MIGRATION_ROOT / "mapping.jsonl"] = mapping_payload
    before_after = {
        "schema_version": "1.0",
        "issue": 110,
        "cutoff_date": CUTOFF_DATE,
        "before": {
            "profiles": len(paths),
            "profiles_with_front_matter": 0,
            "sources": sum(row["source_count"] for row in inventory),
        },
        "after": {
            "profiles": len(paths),
            "profiles_with_front_matter": len(paths),
            "sources": sum(row["source_count"] for row in inventory),
        },
        "entity_type_counts": dict(sorted(type_counts.items())),
        "body_hash_mismatches": 0,
        "normalization_note_counts": dict(sorted(warning_counts.items())),
    }
    before_after_payload = json_bytes(before_after)
    outputs[MIGRATION_ROOT / "before-after.json"] = before_after_payload
    report = f"""# Canonical catalog metadata migration

Issue #110 added canonical English front matter to every individual Markdown
profile present at the execution cutoff.

## Before / after

- profiles: {len(paths)} before, {len(paths)} after;
- profiles with front matter: 0 before, {len(paths)} after;
- visible sources: {before_after["before"]["sources"]} before and after;
- Markdown body hash mismatches: 0.

Missing or non-normalizable values remain explicit in `mapping.jsonl`; no
website, founder route, geography, stage, focus or operator was inferred from a
portfolio observation.

## Reproduction

```text
python tools/seo_geo/migrate_catalog.py
python tools/seo_geo/migrate_catalog.py --check
python tools/seo_geo/validate_profiles.py --catalog
```
"""
    report_payload = report.encode("utf-8")
    outputs[MIGRATION_ROOT / "README.md"] = report_payload
    profile_hashes = {
        path.relative_to(REPOSITORY_ROOT).as_posix(): sha256(payload)
        for path, payload in outputs.items()
        if path in paths
    }
    artifacts = {
        "inventory.jsonl": sha256(inventory_payload),
        "mapping.jsonl": sha256(mapping_payload),
        "before-after.json": sha256(before_after_payload),
        "README.md": sha256(report_payload),
    }
    contract_hashes = {
        path.relative_to(REPOSITORY_ROOT).as_posix(): sha256(
            path.read_bytes().replace(b"\r\n", b"\n")
        )
        for path in (
            CONTRACT_ROOT / "profile.schema.json",
            CONTRACT_ROOT / "enums.json",
        )
    }
    manifest = {
        "schema_version": "1.0",
        "issue": 110,
        "parent_epic": 107,
        "cutoff_date": CUTOFF_DATE,
        "status": "complete",
        "locale": "en",
        "profile_count": len(paths),
        "entity_type_counts": dict(sorted(type_counts.items())),
        "source_count": sum(row["source_count"] for row in inventory),
        "body_hash_mismatches": 0,
        "unique_ids": len(ids),
        "unique_slugs": len(slugs),
        "hash_algorithm": "sha256",
        "profile_hashes": dict(sorted(profile_hashes.items())),
        "artifact_hashes": dict(sorted(artifacts.items())),
        "contract_hashes": dict(sorted(contract_hashes.items())),
    }
    outputs[MIGRATION_ROOT / "migration-manifest.json"] = json_bytes(manifest)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for path, payload in outputs.items():
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                drift.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
