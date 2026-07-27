#!/usr/bin/env python3
"""Gera deterministicamente a publicação de redes-anjo da issue #87."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import textwrap
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
CONSOLIDATION = EPIC_ROOT / "consolidation"
PUBLICATION_ROOT = REPOSITORY_ROOT / "ecosystem" / "angel-networks"
ISSUE = 87
SUB_ISSUE = 159
OWNER = "issue-87-publisher"
BRANCH = "agent/issue-87-angels-publication"
CUTOFF_DATE = "2026-07-27"
BATCH_SIZE = 10
BATCH_ID = "angels-001"
EXPECTED_BATCH_HASH = "cdb068e4ba3c2769da4c65b8653dfb73ae2f0d6332ed56867283f28ac119b174"
PAD = "ang-hub-udep-pe--pad"
EXPECTED_PENDING = (
    "ang-businessangelsclub-org",
    "ang-centrodeinnovacion-uc-cl--red-angeles",
    "ang-curitibaangels-com-br",
    "ang-enlaces-org-do",
    "ang-firstangelscaribbean-com",
    "ang-pucangels-org",
)
COUNTRY_NAMES = {
    "Argentina": {"en": "Argentina", "pt": "Argentina", "es": "Argentina"},
    "Brazil": {"en": "Brazil", "pt": "Brasil", "es": "Brasil"},
    "Chile": {"en": "Chile", "pt": "Chile", "es": "Chile"},
    "Jamaica": {"en": "Jamaica", "pt": "Jamaica", "es": "Jamaica"},
    "Mexico": {"en": "Mexico", "pt": "México", "es": "México"},
    "República Dominicana": {
        "en": "Dominican Republic",
        "pt": "República Dominicana",
        "es": "República Dominicana",
    },
}
GEOGRAPHY_NAMES = {
    "América Latina": {
        "en": "Latin America",
        "pt": "América Latina",
        "es": "América Latina",
    },
    "Brazil": {"en": "Brazil", "pt": "Brasil", "es": "Brasil"},
    "Caribe": {"en": "Caribbean", "pt": "Caribe", "es": "Caribe"},
    "Chile": {"en": "Chile", "pt": "Chile", "es": "Chile"},
    "Jamaica": {"en": "Jamaica", "pt": "Jamaica", "es": "Jamaica"},
    "Latin America": {
        "en": "Latin America",
        "pt": "América Latina",
        "es": "América Latina",
    },
    "Mexico": {"en": "Mexico", "pt": "México", "es": "México"},
    "República Dominicana": {
        "en": "Dominican Republic",
        "pt": "República Dominicana",
        "es": "República Dominicana",
    },
    "Argentina": {"en": "Argentina", "pt": "Argentina", "es": "Argentina"},
}
TYPE_NAMES = {
    "clube": {
        "en": "Angel-investment club",
        "pt": "Clube de investimento-anjo",
        "es": "Club de inversión ángel",
    },
    "rede": {
        "en": "Angel-investment network",
        "pt": "Rede de investimento-anjo",
        "es": "Red de inversión ángel",
    },
    "alumni network": {
        "en": "Alumni angel-investment network",
        "pt": "Rede alumni de investimento-anjo",
        "es": "Red alumni de inversión ángel",
    },
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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


def load_frozen_queue() -> tuple[list[dict], list[dict], list[dict], dict]:
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    queue = read_jsonl(CONSOLIDATION / "publication-queue.jsonl")
    manifest = json.loads(
        (CONSOLIDATION / "consolidation-manifest.json").read_text(encoding="utf-8")
    )
    if manifest["status"] != "frozen":
        raise ValueError("a fila de redes-anjo não está congelada")
    if manifest["independent_review_status"] != "complete":
        raise ValueError("a revisão independente não está concluída")
    if manifest["unresolved_high_divergences"] != 0:
        raise ValueError("há divergência alta aberta")
    if manifest["final_eligible_count"] != len(queue):
        raise ValueError("a fila não corresponde aos elegíveis finais")
    return candidates, evidence, queue, manifest


def geography(candidate: dict, language: str) -> str:
    return ", ".join(
        GEOGRAPHY_NAMES.get(value, {}).get(language, value)
        for value in candidate["declared_geography"]
    )


def actor_names(items: list[dict]) -> str:
    return "; ".join(item["name"] for item in items)


def profile_bytes(candidate: dict, evidence_by_id: dict[str, dict]) -> bytes:
    aliases = ", ".join(alias["name"] for alias in candidate["aliases"]) or "None recorded"
    sources = "\n".join(
        "- [{title} — {publisher}]({url}) (official, accessed {date})".format(
            title=evidence_by_id[evidence_id]["title"],
            publisher=evidence_by_id[evidence_id]["publisher"],
            url=evidence_by_id[evidence_id]["url"],
            date=evidence_by_id[evidence_id]["accessed_on"],
        )
        for evidence_id in candidate["official_evidence_ids"]
    )
    summary = textwrap.fill(
        "The network accepts external founder submissions through its official "
        "route. Its selection team screens opportunities, the disclosed decision "
        "actors decide whether to proceed, and the disclosed capital actors supply "
        "the investment. The frozen evidence supports recurring selection and "
        "recent activity; this profile represents the network, not a venture fund.",
        width=88,
    )
    text = f"""# {candidate["name"]}

<!-- angel-network-id: {candidate["network_id"]} -->

- **Type:** {TYPE_NAMES[candidate["entity_type"]]["en"]}
- **Operator:** {candidate["name"]}
- **Website:** [{candidate["canonical_domain"]}]({candidate["official_site"]})
- **Aliases:** {aliases}
- **Geography:** {geography(candidate, "en")}
- **Founder route:** [Submit through the official route]({candidate["application_route"]})
- **Selection:** {actor_names(candidate["selection_actors"])}
- **Decision:** {actor_names(candidate["decision_actors"])}
- **Capital:** {actor_names(candidate["capital_actors"])}
- **Recent activity:** Official activity dated {candidate["activity_evidence_date"]}

{summary}

No standard check, instrument, ownership target, or investment terms are inferred
when they are not stated in the frozen official evidence.

## Official sources

{sources}

**Last verified:** {CUTOFF_DATE}
"""
    return text.encode("utf-8")


def index_bytes(candidates: list[dict], language: str) -> bytes:
    copy = {
        "en": {
            "title": "Angel networks",
            "intro": (
                "Angel networks connect founders with individual investors who "
                "invest their own capital. A network is not the same as a venture "
                "capital fund, even when members invest together."
            ),
            "columns": ("Organization", "Type", "Geography"),
        },
        "pt": {
            "title": "Redes de investidores-anjo",
            "intro": (
                "Redes de investidores-anjo conectam fundadores a investidores "
                "individuais que aplicam capital próprio. Uma rede não é um fundo "
                "de venture capital, mesmo quando seus membros investem em conjunto."
            ),
            "columns": ("Organização", "Tipo", "Geografia"),
        },
        "es": {
            "title": "Redes de inversionistas ángeles",
            "intro": (
                "Las redes de inversionistas ángeles conectan fundadores con "
                "inversionistas individuales que aportan capital propio. Una red "
                "no es un fondo de venture capital, aunque sus miembros inviertan juntos."
            ),
            "columns": ("Organización", "Tipo", "Geografía"),
        },
    }[language]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["base_country"]].append(candidate)
    sections = []
    for country in sorted(grouped, key=lambda value: COUNTRY_NAMES[value][language]):
        rows = "\n".join(
            "| [{name}]({path}) | {type_name} | {geography} |".format(
                name=item["name"],
                path=Path(item["canonical_profile"])
                .relative_to("ecosystem/angel-networks")
                .as_posix(),
                type_name=TYPE_NAMES[item["entity_type"]][language],
                geography=geography(item, language),
            )
            for item in sorted(grouped[country], key=lambda row: row["network_id"])
        )
        columns = copy["columns"]
        sections.append(
            f"""## {COUNTRY_NAMES[country][language]}

| {columns[0]} | {columns[1]} | {columns[2]} |
| --- | --- | --- |
{rows}"""
        )
    return (
        f"# {copy['title']}\n\n{textwrap.fill(copy['intro'], width=88)}\n\n"
        + "\n\n".join(sections)
        + "\n"
    ).encode("utf-8")


def build_outputs() -> dict[Path, bytes]:
    candidates, evidence, queue, frozen_manifest = load_frozen_queue()
    candidate_by_id = {item["network_id"]: item for item in candidates}
    eligible = sorted(
        (candidate_by_id[item["network_id"]] for item in queue),
        key=lambda item: item["network_id"],
    )
    pending_rows = sorted(
        (item for item in queue if item["publication_status"] == "pending-publication"),
        key=lambda item: item["network_id"],
    )
    preserved_rows = sorted(
        (item for item in queue if item["publication_status"] == "already-published"),
        key=lambda item: item["network_id"],
    )
    pending_ids = tuple(item["network_id"] for item in pending_rows)
    if pending_ids != EXPECTED_PENDING:
        raise ValueError("fila pendente diverge do lote fechado da issue #159")
    if PAD in {item["network_id"] for item in queue}:
        raise ValueError("PAD/UDEP não pode integrar a fila final")
    if math.ceil(len(pending_rows) / BATCH_SIZE) != 1:
        raise ValueError("a sub-issue #159 deve representar exatamente um lote")
    if len(preserved_rows) != 5:
        raise ValueError("os cinco perfis existentes devem ser preservados")

    evidence_by_id = {item["evidence_id"]: item for item in evidence}
    outputs: dict[Path, bytes] = {}
    for row in pending_rows:
        candidate = candidate_by_id[row["network_id"]]
        outputs[REPOSITORY_ROOT / row["canonical_profile"]] = profile_bytes(
            candidate, evidence_by_id
        )
    for language, filename in (
        ("en", "README.md"),
        ("pt", "README.pt.md"),
        ("es", "README.es.md"),
    ):
        outputs[PUBLICATION_ROOT / filename] = index_bytes(eligible, language)
    batch_core = {
        "batch_id": BATCH_ID,
        "branch": BRANCH,
        "owner": OWNER,
        "profiles": [
            {
                "network_id": row["network_id"],
                "profile_path": row["canonical_profile"],
            }
            for row in pending_rows
        ],
    }
    batch_hash = sha256(
        json.dumps(
            batch_core, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )
    if batch_hash != EXPECTED_BATCH_HASH:
        raise ValueError("hash do lote diverge da sub-issue #159")
    batch = {
        "schema_version": "1.0",
        **batch_core,
        "batch_hash": batch_hash,
        "sub_issue": SUB_ISSUE,
        "sub_issue_url": (
            f"https://github.com/djairofilho/awesome-latam-vc/issues/{SUB_ISSUE}"
        ),
    }
    batch_payload = jsonl_bytes([batch])
    outputs[HERE / "batches.jsonl"] = batch_payload

    profile_hashes = {
        path.relative_to(REPOSITORY_ROOT).as_posix(): sha256(payload)
        for path, payload in outputs.items()
        if path.suffix == ".md"
        and path.name not in {"README.md", "README.pt.md", "README.es.md"}
        and "angel-networks" in path.parts
    }
    preserved_hashes = {
        row["canonical_profile"]: sha256(
            (REPOSITORY_ROOT / row["canonical_profile"]).read_bytes()
        )
        for row in preserved_rows
    }
    index_paths = (
        PUBLICATION_ROOT / "README.md",
        PUBLICATION_ROOT / "README.pt.md",
        PUBLICATION_ROOT / "README.es.md",
    )
    source_paths = (
        CONSOLIDATION / "candidates.jsonl",
        CONSOLIDATION / "evidence.jsonl",
        CONSOLIDATION / "publication-queue.jsonl",
        CONSOLIDATION / "consolidation-manifest.json",
        CONSOLIDATION / "independent-review.jsonl",
        CONSOLIDATION / "review-divergences.json",
    )
    decisions = Counter(item["decision"] for item in candidates)
    manifest = {
        "schema_version": "1.0",
        "issue": ISSUE,
        "parent_epic": 63,
        "source_issue": 86,
        "cutoff_date": CUTOFF_DATE,
        "status": "complete",
        "source_queue_status": frozen_manifest["status"],
        "source_independent_review_status": frozen_manifest["independent_review_status"],
        "source_unresolved_high_divergences": frozen_manifest[
            "unresolved_high_divergences"
        ],
        "eligible_count": len(eligible),
        "newly_published_count": len(pending_rows),
        "preserved_count": len(preserved_rows),
        "not_published_count": len(candidates) - len(eligible),
        "not_published_decision_counts": {
            key: value
            for key, value in sorted(decisions.items())
            if key != "elegível"
        },
        "excluded_network_ids": [PAD],
        "batch_size": BATCH_SIZE,
        "batch_count": 1,
        "expected_batch_count": math.ceil(len(pending_rows) / BATCH_SIZE),
        "sub_issues": [SUB_ISSUE],
        "branches": [BRANCH],
        "hash_algorithm": "sha256",
        "batch_artifact_hash": sha256(batch_payload),
        "batch_hash": batch_hash,
        "profile_hashes": dict(sorted(profile_hashes.items())),
        "preserved_profile_hashes": dict(sorted(preserved_hashes.items())),
        "index_hashes": {
            path.relative_to(REPOSITORY_ROOT).as_posix(): sha256(outputs[path])
            for path in index_paths
        },
        "source_hashes": {
            path.name: sha256(path.read_bytes().replace(b"\r\n", b"\n"))
            for path in source_paths
        },
    }
    outputs[HERE / "publication-manifest.json"] = json_bytes(manifest)
    outputs[HERE / "README.md"] = f"""# Publicação de redes-anjo

A issue #87 publica exatamente os seis perfis pendentes da fila congelada e
revisada da issue #86. Os cinco perfis já existentes são preservados e aparecem
nos três índices. O PAD/UDEP não integra a publicação.

## Lote

- lote: `{BATCH_ID}`;
- sub-issue: [#{SUB_ISSUE}](https://github.com/djairofilho/awesome-latam-vc/issues/{SUB_ISSUE});
- branch: `{BRANCH}`;
- owner: `{OWNER}`;
- perfis novos: {len(pending_rows)};
- perfis preservados: {len(preserved_rows)};
- hash: `{batch_hash}`.

## Reprodução

```text
python research/epic-63/publication/build_publication.py
python research/epic-63/publication/build_publication.py --check
python -m unittest discover -s research/epic-63/publication/tests -p "test_*.py"
```
""".encode("utf-8")
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
