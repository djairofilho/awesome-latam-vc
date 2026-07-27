#!/usr/bin/env python3
"""Verify issue #103 batches, profiles, relationships, indexes and hashes."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PUBLICATION = ROOT / "research" / "epic-65" / "publication"
CONSOLIDATION = ROOT / "research" / "epic-65" / "consolidation"
CATALOG = ROOT / "ecosystem" / "public-programs"

COUNTRY_SLUGS = {
    "Argentina": "argentina",
    "Bolivia": "bolivia",
    "Brasil": "brazil",
    "Chile": "chile",
    "Colombia": "colombia",
    "Equador": "ecuador",
    "Mexico": "mexico",
    "Paraguai": "paraguay",
    "Peru": "peru",
    "Uruguai": "uruguay",
    "Venezuela": "venezuela",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def asciifold(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalized_hash(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def profile_hash(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if payload.startswith(b"---\n"):
        closing = payload.find(b"\n---\n", 4)
        if closing != -1:
            payload = payload[closing + 5 :].lstrip(b"\n")
    return hashlib.sha256(payload).hexdigest()


def expected_path(
    entity_id: str,
    entity_type: str,
    country: str,
) -> str:
    prefix = f"{entity_type}-"
    slug = entity_id.removeprefix(prefix)
    return (
        f"ecosystem/public-programs/{COUNTRY_SLUGS[asciifold(country)]}/"
        f"{slug}.md"
    )


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    publication = root / "research" / "epic-65" / "publication"
    consolidation = root / "research" / "epic-65" / "consolidation"
    catalog = root / "ecosystem" / "public-programs"
    plan = read_json(publication / "publication-plan.json")
    manifest = read_json(publication / "publication-manifest.json")
    agencies = read_jsonl(consolidation / "agencies.jsonl")
    programs = read_jsonl(consolidation / "programs.jsonl")
    calls = read_jsonl(consolidation / "calls.jsonl")
    evidence = read_jsonl(consolidation / "evidence.jsonl")
    agency_by_id = {row["agency_id"]: row for row in agencies}
    program_by_id = {row["program_id"]: row for row in programs}
    call_by_id = {row["call_id"]: row for row in calls}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}

    eligible_agencies = {
        row["agency_id"] for row in agencies if row["decision"] == "elegível"
    }
    eligible_programs = {
        row["program_id"] for row in programs if row["decision"] == "elegível"
    }
    expected_ids = eligible_agencies | eligible_programs
    batches = plan["batches"]
    expected_batch_count = math.ceil(len(expected_ids) / 10)
    if len(batches) != expected_batch_count:
        errors.append("quantidade de lotes diverge de ceil(elegíveis / 10)")

    profiles = [
        profile for batch in batches for profile in batch["profiles"]
    ]
    profile_ids = [profile["entity_id"] for profile in profiles]
    profile_paths = [profile["path"] for profile in profiles]
    if profile_ids != sorted(profile_ids):
        errors.append("fila de perfis não está ordenada por entity_id")
    if len(profile_ids) != len(set(profile_ids)):
        errors.append("há ID duplicado nos lotes")
    if len(profile_paths) != len(set(profile_paths)):
        errors.append("há caminho duplicado nos lotes")
    if set(profile_ids) != expected_ids:
        missing = sorted(expected_ids - set(profile_ids))
        extra = sorted(set(profile_ids) - expected_ids)
        errors.append(
            f"fila não cobre exatamente os elegíveis; ausentes={missing}, extras={extra}"
        )
    if canonical_hash(profiles) != plan["profile_queue_hash"]:
        errors.append("hash da fila de perfis inválido")

    issue_numbers: list[int] = []
    branches: list[str] = []
    for index, batch in enumerate(batches, start=1):
        batch_profiles = batch["profiles"]
        if not batch_profiles or len(batch_profiles) > 10:
            errors.append(f"lote {index} vazio ou acima de 10 perfis")
        if canonical_hash(batch_profiles) != batch["batch_hash"]:
            errors.append(f"hash inválido no lote {index}")
        if batch["issue_number"] is None:
            errors.append(f"lote {index} sem sub-issue")
        else:
            issue_numbers.append(batch["issue_number"])
        if not batch["branch"]:
            errors.append(f"lote {index} sem branch")
        else:
            branches.append(batch["branch"])
    if len(issue_numbers) != len(set(issue_numbers)):
        errors.append("há sub-issue repetida entre lotes")
    if len(branches) != len(set(branches)):
        errors.append("há branch repetida entre lotes")

    agency_country = {
        row["agency_id"]: row["country"] for row in agencies
    }
    profile_by_id = {profile["entity_id"]: profile for profile in profiles}
    for profile in profiles:
        entity_id = profile["entity_id"]
        if profile["entity_type"] == "agency":
            entity = agency_by_id.get(entity_id)
            country = entity["country"] if entity else ""
        else:
            entity = program_by_id.get(entity_id)
            country = agency_country.get(entity["agency_id"], "") if entity else ""
        if entity is None:
            continue
        if profile["name"] != entity["name"]:
            errors.append(f"{entity_id}: nome divergente da fila")
        if profile["path"] != expected_path(
            entity_id,
            profile["entity_type"],
            country,
        ):
            errors.append(f"{entity_id}: caminho não canônico")

    catalog_profiles = sorted(
        path.relative_to(root).as_posix()
        for path in catalog.rglob("*.md")
        if path.name != "README.md"
    )
    if set(catalog_profiles) != set(profile_paths):
        missing = sorted(set(profile_paths) - set(catalog_profiles))
        extra = sorted(set(catalog_profiles) - set(profile_paths))
        errors.append(
            f"catálogo fora da fila congelada; ausentes={missing}, extras={extra}"
        )

    for profile in profiles:
        entity_id = profile["entity_id"]
        path = root / profile["path"]
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if text.count(f"`{entity_id}`") < 1:
            errors.append(f"{entity_id}: marcador de ID ausente")
        batch = next(
            row
            for row in batches
            if entity_id in {
                item["entity_id"] for item in row["profiles"]
            }
        )
        if f"`{batch['batch_id']}`" not in text:
            errors.append(f"{entity_id}: lote não registrado no perfil")
        if "**Aliases:**" not in text:
            errors.append(f"{entity_id}: aliases não registrados")

        if profile["entity_type"] == "agency":
            entity = agency_by_id[entity_id]
            evidence_ids = entity["official_evidence_ids"]
            for program_id in entity["program_ids"]:
                if program_id in eligible_programs and f"`{program_id}`" not in text:
                    errors.append(
                        f"{entity_id}: programa elegível não relacionado {program_id}"
                    )
        else:
            entity = program_by_id[entity_id]
            evidence_ids = entity["official_evidence_ids"]
            agency_id = entity["agency_id"]
            if agency_id not in profile_by_id or f"`{agency_id}`" not in text:
                errors.append(f"{entity_id}: relação com agência órfã")
            for call_id in entity["call_ids"]:
                if f"`{call_id}`" not in text:
                    errors.append(f"{entity_id}: chamada vinculada ausente {call_id}")
                call = call_by_id[call_id]
                if call["benefit_summary"] not in text:
                    errors.append(f"{entity_id}: benefício da chamada foi alterado")
                if call["eligibility_summary"] not in text:
                    errors.append(f"{entity_id}: elegibilidade da chamada foi alterada")

        for evidence_id in evidence_ids:
            row = evidence_by_id.get(evidence_id)
            if row is None:
                errors.append(f"{entity_id}: evidência órfã {evidence_id}")
                continue
            if row["source_type"] != "oficial":
                errors.append(f"{entity_id}: evidência não oficial {evidence_id}")
            if f"`{evidence_id}`" not in text or row["url"] not in text:
                errors.append(f"{entity_id}: fonte oficial ausente {evidence_id}")

    if any(call["profile_eligible"] for call in calls):
        errors.append("há chamada marcada como publicável")
    call_ids = {call["call_id"] for call in calls}
    if set(profile_ids) & call_ids:
        errors.append("uma chamada foi publicada como perfil")
    if manifest["call_profiles"] != 0:
        errors.append("manifesto registra perfil de chamada")

    index = (catalog / "README.md").read_text(encoding="utf-8")
    for profile in profiles:
        relative = Path(profile["path"]).relative_to(
            Path("ecosystem/public-programs")
        ).as_posix()
        if index.count(f"({relative})") != 1:
            errors.append(f"{profile['entity_id']}: índice não contém link único")
    multilingual = ("README.md", "README.es.md", "README.pt.md")
    category_link = "ecosystem/public-programs/README.md"
    for filename in multilingual:
        path = root / filename
        if not path.is_file() or path.read_text(encoding="utf-8").count(category_link) != 1:
            errors.append(f"{filename}: integração multilíngue ausente ou duplicada")

    source_paths = {
        name: consolidation / name for name in plan["source_hashes"]
    }
    for name, digest in plan["source_hashes"].items():
        if normalized_hash(source_paths[name]) != digest:
            errors.append(f"hash de entrada inválido: {name}")
    for path_text, digest in manifest["profile_hashes"].items():
        path = root / path_text
        if not path.is_file() or profile_hash(path) != digest:
            errors.append(f"hash de perfil inválido: {path_text}")
    if normalized_hash(catalog / "README.md") != manifest["index_hash"]:
        errors.append("hash do índice inválido")

    if manifest["profile_queue_hash"] != plan["profile_queue_hash"]:
        errors.append("manifesto e plano divergem na fila")
    if manifest["profile_count"] != len(profiles):
        errors.append("contagem de perfis inválida no manifesto")
    if manifest["agency_profiles"] != len(eligible_agencies):
        errors.append("contagem de agências inválida no manifesto")
    if manifest["program_profiles"] != len(eligible_programs):
        errors.append("contagem de programas inválida no manifesto")
    if manifest["status"] != "complete":
        errors.append("manifesto de publicação não está completo")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Publicação da issue #103 inválida:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Publicação determinística da issue #103 validada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
