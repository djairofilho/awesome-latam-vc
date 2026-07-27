#!/usr/bin/env python3
"""Build the deterministic platform consolidation queue for issue #94."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
REGIONS = ("brazil", "mexico-cac", "andean", "southern-cone")
FILES = {
    "candidates.jsonl": "platform_id",
    "evidence.jsonl": "evidence_id",
    "source-inventory.jsonl": "source_id",
    "coverage-matrix.jsonl": "country",
}
RUN_ID = "run-platforms-latam-consolidated-2026"
UNKNOWN_LEGAL_NAMES = {
    "operador legal não divulgado na fonte oficial",
    "operadora não identificada publicamente",
}
OUTGOING_DESTINATIONS = {
    "plat-auge-ucr": "epic-62:program/auge-ucr",
    "plat-koga-impact-lab": (
        "research/epic-62/consolidation/candidates.jsonl#accel-sc-koga"
    ),
    "plat-open-angels": "epic-62:program/open-angels",
    "plat-pitch-day": "epic-62:program/pitch-day-pandolab",
    "plat-sambil-emprende": "epic-62:program/sambil-emprende",
    "plat-ventiur": (
        "research/epic-62/consolidation/candidates.jsonl"
        "#accel-ventiur-acelera-impacto"
    ),
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    ).encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    asciiish = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "", asciiish)


def unique_sorted(
    records: list[dict[str, Any]], id_field: str, filename: str
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record[id_field]
        if record_id in by_id:
            raise ValueError(f"ID duplicado em {filename}: {record_id}")
        by_id[record_id] = record
    return [by_id[record_id] for record_id in sorted(by_id)]


def load_inputs() -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, dict[str, int]],
]:
    grouped = {filename: [] for filename in FILES}
    tasks: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    before: dict[str, dict[str, int]] = {}
    for region in REGIONS:
        region_dir = EPIC_ROOT / region
        region_counts: dict[str, int] = {}
        for filename in (*FILES, "run-manifest.jsonl"):
            path = region_dir / filename
            payload = path.read_bytes().replace(b"\r\n", b"\n")
            hashes[path.relative_to(REPOSITORY_ROOT).as_posix()] = sha256(payload)
            records = read_jsonl(path)
            if filename in grouped:
                grouped[filename].extend(records)
                region_counts[filename] = len(records)
            else:
                for record in records:
                    if record["record_type"] == "task":
                        task = dict(record)
                        task["run_id"] = RUN_ID
                        tasks.append(task)
        before[region] = region_counts
    return grouped, tasks, dict(sorted(hashes.items())), before


def collision_groups(
    candidates: list[dict[str, Any]],
    key_builder: Callable[[dict[str, Any]], Any],
) -> list[dict[str, Any]]:
    groups: dict[Any, list[str]] = defaultdict(list)
    for candidate in candidates:
        key = key_builder(candidate)
        if key:
            groups[key].append(candidate["platform_id"])
    return [
        {"key": key, "platform_ids": sorted(ids)}
        for key, ids in sorted(groups.items(), key=lambda item: repr(item[0]))
        if len(ids) > 1
    ]


def build_deduplication_report(
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    domain_groups = collision_groups(
        candidates,
        lambda row: (
            row["platform"]["canonical_domain"],
            normalize(row["brand"]["name"]),
        ),
    )

    def legal_key(row: dict[str, Any]) -> Any:
        name = row["operator"]["legal_name"]
        if name.casefold() in UNKNOWN_LEGAL_NAMES:
            return None
        return row["operator"]["jurisdiction"], normalize(name)

    legal_groups = collision_groups(candidates, legal_key)
    regulatory_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for candidate in candidates:
        for record in candidate["regulatory_records"]:
            number = record.get("registration_number")
            if number:
                key = (record["jurisdiction"], record["authority"], number)
                regulatory_groups[key].append(candidate["platform_id"])
    regulatory_collisions = [
        {"key": key, "platform_ids": sorted(ids)}
        for key, ids in sorted(regulatory_groups.items())
        if len(ids) > 1
    ]
    if domain_groups or legal_groups or regulatory_collisions:
        raise ValueError(
            "colisão de identidade não resolvida: "
            f"domain={domain_groups}, legal={legal_groups}, "
            f"regulatory={regulatory_collisions}"
        )
    return {
        "schema_version": "1.0",
        "issue": 94,
        "pass_1_domain_brand": {
            "records_scanned": len(candidates),
            "unresolved_groups": domain_groups,
        },
        "pass_2_legal_regulatory": {
            "records_scanned": len(candidates),
            "legal_name_unresolved_groups": legal_groups,
            "regulatory_unresolved_groups": regulatory_collisions,
        },
        "canonical_candidates": len(candidates),
    }


def incoming_angel_transfers(
    platform_ids: set[str],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    seen_networks: set[str] = set()
    for path in sorted((REPOSITORY_ROOT / "research" / "epic-63").rglob("candidates.jsonl")):
        relative = path.relative_to(REPOSITORY_ROOT).parts
        if "shards" in relative or any(
            part in {"examples", "templates"} for part in relative
        ):
            continue
        for candidate in read_jsonl(path):
            if candidate.get("decision") != "encaminhado-para-plataformas":
                continue
            network_id = candidate["network_id"]
            if network_id in seen_networks:
                continue
            seen_networks.add(network_id)
            proposed_profile = candidate.get("canonical_profile")
            target_id = (
                "plat-" + normalize(candidate["name"])
                if not proposed_profile
                else "plat-" + Path(proposed_profile).stem
            )
            materialized = target_id in platform_ids
            results.append(
                {
                    "source_epic": 63,
                    "source_network_id": network_id,
                    "source_name": candidate["name"],
                    "proposed_profile": proposed_profile,
                    "target_platform_id": target_id,
                    "materialized": materialized,
                    "resolution": (
                        "matched-existing-platform"
                        if materialized
                        else "requires-platform-contract-adjudication"
                    ),
                    "owner": None if materialized else "independent-reviewer-issue-94",
                    "next_action": (
                        None
                        if materialized
                        else (
                            "Revisar operador, produto, rota para founders e atividade "
                            "contra o contrato da epic #64."
                        )
                    ),
                }
            )
    return sorted(results, key=lambda row: row["source_network_id"])


def build_outputs() -> dict[str, bytes]:
    grouped, tasks, input_hashes, before_counts = load_inputs()
    canonical = {
        filename: unique_sorted(records, FILES[filename], filename)
        for filename, records in grouped.items()
    }
    candidates = canonical["candidates.jsonl"]
    evidence = canonical["evidence.jsonl"]
    sources = canonical["source-inventory.jsonl"]
    coverage = canonical["coverage-matrix.jsonl"]
    dedupe = build_deduplication_report(candidates)

    if len(candidates) != 38 or len(evidence) != 62 or len(sources) != 117:
        raise ValueError("contagens consolidadas divergentes")
    if len(coverage) != 20:
        raise ValueError("cobertura consolidada divergente")
    if any(candidate["decision"] is None for candidate in candidates):
        raise ValueError("candidato sem decisão")
    if any(
        not candidate.get("owner") or not candidate.get("next_action")
        for candidate in candidates
        if candidate["decision"] == "insufficient_evidence"
    ):
        raise ValueError("pendência sem responsável ou próxima ação")

    platform_ids = {candidate["platform_id"] for candidate in candidates}
    evidence_ids = {row["evidence_id"] for row in evidence}
    source_ids = {row["source_id"] for row in sources}
    for candidate in candidates:
        if any(
            evidence_id not in evidence_ids
            for evidence_id in (
                candidate["official_evidence_ids"]
                + candidate["activity_evidence_ids"]
                + candidate["route_evidence_ids"]
            )
        ):
            raise ValueError(f"evidência órfã em {candidate['platform_id']}")
        if any(
            source_id not in source_ids
            for source_id in candidate["discovery_source_ids"]
        ):
            raise ValueError(f"fonte órfã em {candidate['platform_id']}")
    if any(row["platform_id"] not in platform_ids for row in evidence):
        raise ValueError("evidência aponta para plataforma inexistente")

    outgoing = []
    for candidate in candidates:
        if candidate["decision"] != "other_category":
            continue
        destination = OUTGOING_DESTINATIONS.get(candidate["platform_id"])
        if not destination:
            raise ValueError(
                f"fronteira sem destino: {candidate['platform_id']}"
            )
        outgoing.append(
            {
                "platform_id": candidate["platform_id"],
                "platform_decision": candidate["decision"],
                "canonical_destination": destination,
            }
        )
    incoming = incoming_angel_transfers(platform_ids)
    resolutions = {
        "schema_version": "1.0",
        "issue": 94,
        "outgoing_category_resolutions": outgoing,
        "incoming_angel_transfers": incoming,
    }

    base_outputs = {
        filename: jsonl_bytes(records)
        for filename, records in canonical.items()
    }
    artifact_hashes = {
        filename: sha256(base_outputs[filename])
        for filename in (
            "candidates.jsonl",
            "coverage-matrix.jsonl",
            "evidence.jsonl",
            "source-inventory.jsonl",
        )
    }
    tasks.sort(key=lambda row: row["task_id"])
    run = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issues": [90, 91, 92, 93],
        "contract_issue": 89,
        "cutoff_date": "2026-07-27",
        "created_on": "2026-07-27",
        "status": "complete",
        "task_count": len(tasks),
        "scraping_performed": False,
        "hash_algorithm": "sha256",
        "artifact_hashes": artifact_hashes,
        "owner": "coordinator-issue-94",
        "execution_policy": {
            "respect_robots_txt": True,
            "bypass_access_controls": False,
            "max_concurrency_per_domain": 2,
            "minimum_delay_ms": 500,
            "cache_enabled": True,
            "retry_attempts": 3,
            "browser_policy": "official_js_only",
        },
        "notes": (
            "Redução sem scraping novo; preserva os shards e tarefas das quatro "
            "auditorias regionais."
        ),
    }
    base_outputs["run-manifest.jsonl"] = jsonl_bytes([run, *tasks])
    base_outputs["deduplication-report.json"] = json_bytes(dedupe)
    base_outputs["category-resolutions.json"] = json_bytes(resolutions)
    output_hashes = {
        filename: sha256(payload) for filename, payload in base_outputs.items()
    }

    counts = dict(sorted(Counter(row["decision"] for row in candidates).items()))
    manifest = {
        "schema_version": "1.0",
        "issue": 94,
        "cutoff_date": "2026-07-27",
        "status": "provisional",
        "independent_review_status": "pending",
        "before_counts": before_counts,
        "after_counts": {
            "candidates": len(candidates),
            "evidence": len(evidence),
            "sources": len(sources),
            "countries": len(coverage),
            "tasks": len(tasks),
        },
        "decision_counts": counts,
        "outgoing_category_resolutions": len(outgoing),
        "incoming_angel_transfers": len(incoming),
        "materialized_incoming_transfers": sum(row["materialized"] for row in incoming),
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
    }
    base_outputs["consolidation-manifest.json"] = json_bytes(manifest)

    pending_incoming = sum(not row["materialized"] for row in incoming)
    report = f"""# Fila provisória consolidada de plataformas

Este bundle materializa a redução mecânica da issue #94 na data de corte
2026-07-27. Ele não publica perfis.

## Before / after

| Artefato | Antes | Depois |
| --- | ---: | ---: |
| Candidatos | 38 | {len(candidates)} |
| Evidências | 62 | {len(evidence)} |
| Fontes | 117 | {len(sources)} |
| Países | 20 | {len(coverage)} |

As duas passagens de deduplicação não encontraram colisões conhecidas. Valores
como “operador legal não divulgado” foram corretamente ignorados como chave.

## Decisões

- `eligible`: {counts.get("eligible", 0)}.
- `insufficient_evidence`: {counts.get("insufficient_evidence", 0)}.
- `other_category`: {counts.get("other_category", 0)}.
- `excluded`: {counts.get("excluded", 0)}.
- `inactive`: {counts.get("inactive", 0)}.
- Transferências recebidas da epic #63: {len(incoming)}.
- Transferências recebidas ainda não materializadas: {pending_incoming}.

## Gate

A redução é reproduzível e possui hashes, mas a fila permanece `provisional`.
Um agente diferente do consolidador deve revisar 100% dos elegíveis, pendências,
fronteiras e transferências antes de congelar o manifesto.

## Reprodução

```text
python research/epic-64/consolidation/build_queue.py
python research/epic-64/consolidation/build_queue.py --check
python research/epic-64/validate.py --dataset research/epic-64/consolidation
python -m unittest discover -s research/epic-64/consolidation/tests -p "test_*.py"
```
"""
    base_outputs["README.md"] = report.encode("utf-8")
    return base_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    drift = []
    for filename, payload in outputs.items():
        path = HERE / filename
        if args.check:
            if not path.is_file() or path.read_bytes() != payload:
                drift.append(filename)
        else:
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"artefatos divergentes: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
