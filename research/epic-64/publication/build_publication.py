#!/usr/bin/env python3
"""Build deterministic publication artifacts for issue #95."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
CONSOLIDATION = EPIC_ROOT / "consolidation"
PUBLICATION_ROOT = REPOSITORY_ROOT / "ecosystem" / "funding-platforms"
ISSUE = 95
SUB_ISSUE = 151
OWNER = "issue-95-publisher"
BRANCH = "agent/issue-95-platforms-publication"
CUTOFF_DATE = "2026-07-27"
BATCH_SIZE = 10
BATCH_ID = "platforms-001"
PROFILE_PATHS = {
    "plat-a2censo": "ecosystem/funding-platforms/colombia/a2censo.md",
    "plat-arkangeles": "ecosystem/funding-platforms/mexico/arkangeles.md",
    "plat-broota": "ecosystem/funding-platforms/chile/broota.md",
    "plat-captable": "ecosystem/funding-platforms/brazil/captable.md",
    "plat-crowder-uruguay": "ecosystem/funding-platforms/uruguay/crowder.md",
    "plat-eqseed": "ecosystem/funding-platforms/brazil/eqseed.md",
    "plat-kria": "ecosystem/funding-platforms/brazil/kria.md",
    "plat-play-business": "ecosystem/funding-platforms/mexico/play-business.md",
    "plat-smu": "ecosystem/funding-platforms/brazil/smu.md",
}
COUNTRY_NAMES = {
    "BR": {"en": "Brazil", "pt": "Brasil", "es": "Brasil"},
    "CL": {"en": "Chile", "pt": "Chile", "es": "Chile"},
    "CO": {"en": "Colombia", "pt": "Colômbia", "es": "Colombia"},
    "MX": {"en": "Mexico", "pt": "México", "es": "México"},
    "UY": {"en": "Uruguay", "pt": "Uruguai", "es": "Uruguay"},
}
INSTRUMENT_NAMES = {
    "equity crowdfunding": {
        "en": "Equity crowdfunding",
        "pt": "Crowdfunding de participação",
        "es": "Crowdfunding de capital",
    },
    "debt crowdfunding": {
        "en": "Debt crowdfunding",
        "pt": "Crowdfunding de dívida",
        "es": "Crowdfunding de deuda",
    },
    "revenue share": {
        "en": "Revenue share",
        "pt": "Participação na receita",
        "es": "Participación en ingresos",
    },
    "convertible": {
        "en": "Convertible instruments",
        "pt": "Instrumentos conversíveis",
        "es": "Instrumentos convertibles",
    },
    "matching": {
        "en": "Investor matching",
        "pt": "Conexão com investidores",
        "es": "Conexión con inversionistas",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def split_front_matter(payload: bytes) -> tuple[bytes, bytes]:
    normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        return b"", normalized
    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == b"---"
        ),
        None,
    )
    if closing_index is None:
        return b"", normalized
    return (
        b"".join(lines[: closing_index + 1]),
        b"".join(lines[closing_index + 1 :]).lstrip(b"\n"),
    )


def profile_payload(path: Path, body: bytes) -> bytes:
    front_matter = b""
    if path.is_file():
        front_matter, _existing_body = split_front_matter(path.read_bytes())
    return front_matter + body.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def profile_sha256(payload: bytes) -> str:
    _front_matter, body = split_front_matter(payload)
    return sha256(body)


def load_frozen_queue() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]
]:
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    manifest = json.loads(
        (CONSOLIDATION / "consolidation-manifest.json").read_text(encoding="utf-8")
    )
    if manifest["status"] != "frozen":
        raise ValueError("a fila de plataformas não está congelada")
    if manifest["independent_review_status"] != "complete":
        raise ValueError("a revisão independente não está concluída")
    if manifest["independent_review"]["unresolved_high_divergences"] != 0:
        raise ValueError("a fila possui divergência alta não resolvida")
    return candidates, evidence, manifest


def display_countries(candidate: dict[str, Any], language: str = "en") -> str:
    return ", ".join(
        COUNTRY_NAMES[country][language]
        for country in candidate["platform"]["declared_countries"]
    )


def display_instruments(candidate: dict[str, Any], language: str = "en") -> str:
    values = []
    for product in candidate["products"]:
        value = INSTRUMENT_NAMES[product["instrument_type"]][language]
        if value not in values:
            values.append(value)
    return ", ".join(values)


def profile_bytes(
    candidate: dict[str, Any], evidence_by_id: dict[str, dict[str, Any]]
) -> bytes:
    aliases = (
        ", ".join(candidate["brand"]["aliases"])
        if candidate["brand"]["aliases"]
        else "None recorded"
    )
    activity = candidate["activity_status"].replace("_", " ").title()
    product_rows = "\n".join(
        "| {name} | {instrument} | {status} | `{product_id}` |".format(
            name=product["name"],
            instrument=INSTRUMENT_NAMES[product["instrument_type"]]["en"],
            status=product["status"].title(),
            product_id=product["product_id"],
        )
        for product in candidate["products"]
    )
    if candidate["regulatory_records"]:
        regulation = "\n".join(
            "| {authority} | {jurisdiction} | {status} | {number} | `{reg_id}` |".format(
                authority=record["authority"],
                jurisdiction=record["jurisdiction"],
                status=record["claimed_status"].title(),
                number=record["registration_number"] or "Not disclosed",
                reg_id=record["regulatory_id"],
            )
            for record in candidate["regulatory_records"]
        )
        regulation_section = f"""## Regulation

| Authority | Jurisdiction | Status | Registration | Record ID |
| --- | --- | --- | --- | --- |
{regulation}
"""
    else:
        regulation_section = """## Regulation

No regulatory authorization or registration is claimed in the frozen queue.
"""
    if candidate["offers"]:
        offer_rows = "\n".join(
            "| [{name}]({url}) | {status} | `{product_id}` | No |".format(
                name=offer["name"],
                url=offer["official_url"],
                status=offer["status"].title(),
                product_id=offer["product_id"],
            )
            for offer in candidate["offers"]
        )
        offers_section = f"""## Offers observed

Offers are temporary evidence and are not independent profiles.

| Offer | Status | Product ID | Profile eligible |
| --- | --- | --- | --- |
{offer_rows}

"""
    else:
        offers_section = ""
    evidence_rows = []
    seen_evidence: set[str] = set()
    for evidence_id in candidate["official_evidence_ids"]:
        if evidence_id in seen_evidence:
            continue
        seen_evidence.add(evidence_id)
        row = evidence_by_id[evidence_id]
        evidence_rows.append(
            f"- [{row['title']} — {row['publisher']}]({row['url']}) "
            f"({row['source_type'].replace('_', ' ')}, accessed "
            f"{row['accessed_on']})"
        )
    sources = "\n".join(evidence_rows)
    description = textwrap.fill(
        "The platform provides a structured route for founders using these "
        f"instruments: {display_instruments(candidate).lower()}. It is listed as "
        "an intermediary, not as a venture capital fund or as a temporary offer.",
        width=88,
    )
    text = f"""# {candidate["brand"]["name"]}

<!-- platform-id: {candidate["platform_id"]} -->

- **Type:** Funding platform
- **Operator:** {candidate["operator"]["legal_name"]} (`{candidate["operator"]["operator_id"]}`)
- **Operator jurisdiction:** {candidate["operator"]["jurisdiction"]}
- **Operator website:** [{candidate["operator"]["official_url"]}]({candidate["operator"]["official_url"]})
- **Brand:** {candidate["brand"]["name"]} (`{candidate["brand"]["brand_id"]}`)
- **Aliases:** {aliases}
- **Platform:** {candidate["platform"]["name"]} (`{candidate["platform_id"]}`)
- **Website:** [{candidate["platform"]["canonical_domain"]}]({candidate["platform"]["official_url"]})
- **Founder route:** [Start a fundraising process]({candidate["platform"]["founder_route_url"]})
- **Geography:** {display_countries(candidate)}
- **Activity:** {activity}; last official activity on {candidate["last_official_activity_on"]}

{description}

## Products

| Product | Instrument | Status | Product ID |
| --- | --- | --- | --- |
{product_rows}

{regulation_section}
{offers_section}## Official sources

{sources}

**Last verified:** {CUTOFF_DATE}
"""
    return text.encode("utf-8")


def index_bytes(candidates: list[dict[str, Any]], language: str) -> bytes:
    copy = {
        "en": {
            "title": "Funding platforms",
            "intro": (
                "Funding platforms connect companies seeking capital with multiple "
                "investors. They are intermediaries or marketplaces, not venture "
                "capital funds. Each offer can have different instruments, terms, "
                "and risks."
            ),
            "columns": ("Organization", "Instruments", "Geography"),
        },
        "pt": {
            "title": "Plataformas de captação",
            "intro": (
                "Plataformas de captação conectam empresas que buscam recursos a "
                "múltiplos investidores. São intermediárias ou marketplaces, não "
                "fundos de venture capital. Cada oferta pode ter instrumentos, "
                "termos e riscos diferentes."
            ),
            "columns": ("Organização", "Instrumentos", "Geografia"),
        },
        "es": {
            "title": "Plataformas de financiación",
            "intro": (
                "Las plataformas de financiación conectan empresas que buscan "
                "capital con múltiples inversionistas. Son intermediarias o "
                "marketplaces, no fondos de venture capital. Cada oferta puede "
                "tener instrumentos, términos y riesgos diferentes."
            ),
            "columns": ("Organización", "Instrumentos", "Geografía"),
        },
    }[language]
    rows_by_country: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        base_country = candidate["operator"]["jurisdiction"]
        rows_by_country[base_country].append(candidate)
    sections = []
    for country in sorted(rows_by_country, key=lambda code: COUNTRY_NAMES[code][language]):
        rows = "\n".join(
            "| [{name}]({path}) | {instruments} | {geography} |".format(
                name=candidate["brand"]["name"],
                path=Path(PROFILE_PATHS[candidate["platform_id"]])
                .relative_to("ecosystem/funding-platforms")
                .as_posix(),
                instruments=display_instruments(candidate, language),
                geography=display_countries(candidate, language),
            )
            for candidate in sorted(
                rows_by_country[country], key=lambda row: row["platform_id"]
            )
        )
        columns = copy["columns"]
        sections.append(
            f"""## {COUNTRY_NAMES[country][language]}

| {columns[0]} | {columns[1]} | {columns[2]} |
| --- | --- | --- |
{rows}"""
        )
    joined_sections = "\n\n".join(sections)
    text = f"""# {copy["title"]}

{textwrap.fill(copy["intro"], width=88)}

{joined_sections}
"""
    return text.encode("utf-8")


def localized_root_bytes(filename: str, language: str) -> bytes:
    path = REPOSITORY_ROOT / filename
    text = path.read_text(encoding="utf-8")
    localized = f"ecosystem/funding-platforms/README.{language}.md"
    text = text.replace(localized, "ecosystem/funding-platforms/README.md")
    text = text.replace("ecosystem/funding-platforms/README.md", localized)
    return text.encode("utf-8")


def build_outputs() -> dict[Path, bytes]:
    candidates, evidence, frozen_manifest = load_frozen_queue()
    eligible = sorted(
        (row for row in candidates if row["decision"] == "eligible"),
        key=lambda row: row["platform_id"],
    )
    eligible_ids = [row["platform_id"] for row in eligible]
    if eligible_ids != sorted(PROFILE_PATHS):
        raise ValueError("mapa de publicação diverge dos elegíveis congelados")
    expected_batches = math.ceil(len(eligible) / BATCH_SIZE)
    if expected_batches != 1:
        raise ValueError("a issue #151 só representa um lote")
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    outputs: dict[Path, bytes] = {}
    for candidate in eligible:
        relative = Path(PROFILE_PATHS[candidate["platform_id"]])
        path = REPOSITORY_ROOT / relative
        outputs[path] = profile_payload(
            path,
            profile_bytes(candidate, evidence_by_id),
        )
    outputs[PUBLICATION_ROOT / "README.md"] = index_bytes(eligible, "en")
    outputs[PUBLICATION_ROOT / "README.pt.md"] = index_bytes(eligible, "pt")
    outputs[PUBLICATION_ROOT / "README.es.md"] = index_bytes(eligible, "es")
    outputs[REPOSITORY_ROOT / "README.pt.md"] = localized_root_bytes(
        "README.pt.md", "pt"
    )
    outputs[REPOSITORY_ROOT / "README.es.md"] = localized_root_bytes(
        "README.es.md", "es"
    )

    batch_core = {
        "batch_id": BATCH_ID,
        "branch": BRANCH,
        "owner": OWNER,
        "profiles": [
            {
                "platform_id": platform_id,
                "profile_path": PROFILE_PATHS[platform_id],
            }
            for platform_id in eligible_ids
        ],
    }
    batch_hash = sha256(
        json.dumps(
            batch_core,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    if batch_hash != "0ab4c169f89a202a2fe34de56ebaf1850a714d962b45720182fc69250f4aa8c3":
        raise ValueError("hash do lote diverge da sub-issue #151")
    batch = {
        "schema_version": "1.0",
        **batch_core,
        "batch_hash": batch_hash,
        "sub_issue": SUB_ISSUE,
        "sub_issue_url": (
            "https://github.com/djairofilho/awesome-latam-vc/issues/151"
        ),
    }
    batches_payload = jsonl_bytes([batch])
    outputs[HERE / "batches.jsonl"] = batches_payload

    profile_hashes = {
        path.relative_to(REPOSITORY_ROOT).as_posix(): profile_sha256(payload)
        for path, payload in outputs.items()
        if path.suffix == ".md" and "funding-platforms" in path.parts
        and path.name not in {"README.md", "README.pt.md", "README.es.md"}
    }
    index_hashes = {
        path.relative_to(REPOSITORY_ROOT).as_posix(): sha256(outputs[path])
        for path in (
            PUBLICATION_ROOT / "README.md",
            PUBLICATION_ROOT / "README.pt.md",
            PUBLICATION_ROOT / "README.es.md",
            REPOSITORY_ROOT / "README.pt.md",
            REPOSITORY_ROOT / "README.es.md",
        )
    }
    source_hashes = {
        path.name: sha256(path.read_bytes().replace(b"\r\n", b"\n"))
        for path in (
            CONSOLIDATION / "candidates.jsonl",
            CONSOLIDATION / "evidence.jsonl",
            CONSOLIDATION / "consolidation-manifest.json",
            CONSOLIDATION / "independent-review.jsonl",
        )
    }
    decisions = Counter(row["decision"] for row in candidates)
    manifest = {
        "schema_version": "1.0",
        "issue": ISSUE,
        "parent_epic": 64,
        "cutoff_date": CUTOFF_DATE,
        "status": "complete",
        "source_queue_status": frozen_manifest["status"],
        "source_independent_review_status": frozen_manifest[
            "independent_review_status"
        ],
        "eligible_count": len(eligible),
        "published_count": len(profile_hashes),
        "not_published_count": len(candidates) - len(eligible),
        "not_published_decision_counts": {
            decision: count
            for decision, count in sorted(decisions.items())
            if decision != "eligible"
        },
        "batch_size": BATCH_SIZE,
        "batch_count": 1,
        "expected_batch_count": expected_batches,
        "sub_issues": [SUB_ISSUE],
        "branches": [BRANCH],
        "hash_algorithm": "sha256",
        "batch_artifact_hash": sha256(batches_payload),
        "profile_hashes": dict(sorted(profile_hashes.items())),
        "index_hashes": dict(sorted(index_hashes.items())),
        "source_hashes": dict(sorted(source_hashes.items())),
    }
    outputs[HERE / "publication-manifest.json"] = json_bytes(manifest)
    report = f"""# Publicação de plataformas de captação

A issue #95 publicou exatamente os {len(eligible)} candidatos `eligible` da fila
congelada da issue #94. Nenhum candidato `insufficient_evidence`,
`other_category`, `excluded` ou `inactive` foi promovido.

## Lote

- lote: `{BATCH_ID}`;
- sub-issue: [#{SUB_ISSUE}](https://github.com/djairofilho/awesome-latam-vc/issues/{SUB_ISSUE});
- branch: `{BRANCH}`;
- owner: `{OWNER}`;
- perfis: {len(eligible)};
- hash: `{batch_hash}`.

Os perfis e os índices em inglês, português e espanhol são gerados a partir dos
artefatos congelados. O manifesto fixa hashes dos insumos, perfis e índices.

## Reprodução

```text
python research/epic-64/publication/build_publication.py
python research/epic-64/publication/build_publication.py --check
python -m unittest discover -s research/epic-64/publication/tests -p "test_*.py"
```
"""
    outputs[HERE / "README.md"] = report.encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for path, payload in outputs.items():
        if args.check:
            current = (
                path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                if path.is_file()
                else None
            )
            expected = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            if current != expected:
                drift.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
