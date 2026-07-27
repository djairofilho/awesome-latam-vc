#!/usr/bin/env python3
"""Build the deterministic provisional accelerator registry for issue #76."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
EPIC_ROOT = HERE.parent
REPOSITORY_ROOT = EPIC_ROOT.parents[1]
RUNS = ("pilot", "brazil", "mexico-cac", "andean", "southern-cone", "foreign")
REGIONAL_RUNS = set(RUNS) - {"pilot"}
EXPECTED_DUPLICATES = {
    "accel-kruger-labs": "andean",
    "accel-oxigenio": "brazil",
}

ELIGIBLE = "elegível"
INSUFFICIENT = "evidência-insuficiente"
ROUTED_FUNDS = "encaminhado-para-funds"
ROUTED_EPIC = "encaminhado-para-outra-epic"

PUBLIC_DESTINATIONS = {
    "accel-acelera-divinopolis": "epic-65:program/program-acelera-divinopolis",
    "accel-acre-for-startups": "epic-65:program/program-acre-for-startups",
    "accel-bndes-garagem": "epic-65:program/program-bndes-garagem",
    "accel-brde-labs-rs": "epic-65:program/program-brde-labs-rs",
    "accel-finep-mulheres-inovadoras": (
        "epic-65:program/program-finep-mulheres-inovadoras"
    ),
    "accel-and-agroinnovatec": "epic-65:program/program-agroinnovatec",
    "accel-and-emprendimiento-digital": (
        "epic-65:program/program-emprendimiento-digital"
    ),
    "accel-and-startup-peru": (
        "research/epic-65/andean/programs.jsonl#program-proinnovate-startup-peru"
    ),
    "accel-mxcac-cenpromype": "epic-65:program/program-cenpromype",
    "accel-sc-anii-sprintuy": "epic-65:program/program-anii-sprintuy",
    "accel-sc-incubate": "epic-65:program/program-incubate",
    "accel-sc-mic-reinventa": "epic-65:program/program-mic-reinventa",
    "accel-sc-startup-chile": (
        "research/epic-65/southern-cone/programs.jsonl#program-start-up-chile"
    ),
}

FUND_DESTINATIONS = {
    "accel-mxcac-carao": "funds/regional/carao-ventures.md",
    "accel-sc-cites": "funds/regional/cites.md",
    "accel-foreign-antler-singapore": (
        "funds/:antler.co#global-venture-capital"
    ),
}

HYBRID_DESTINATIONS = {
    "accel-ace-amazonia-impacto": "funds/brazil/ace-ventures.md",
    "accel-ace-for-doers": "funds/brazil/ace-ventures.md",
    "accel-ace-funses1-digital": "funds/brazil/ace-ventures.md",
    "accel-and-buentrip": "funds/regional/buentrip-ventures.md",
    "accel-and-utec": "funds/regional/utec-ventures.md",
    "accel-capital-empreendedor-rj": (
        "research/epic-65/brazil/programs.jsonl#program-sebrae-capital-empreendedor"
    ),
    "accel-darwin-scale": "funds/brazil/darwin-startups.md",
    "accel-foreign-500-global-flagship": (
        "funds/regional/500-latam-500-global.md"
    ),
    "accel-gb-ventures": "funds/brazil/grupo-boticario-ventures.md",
    "accel-mxcac-500-latam": "funds/regional/500-latam-500-global.md",
    "accel-mxcac-parallel18": "funds/regional/parallel18-ventures.md",
    "accel-sc-grid-transform": "funds/multi-country/gridx.md",
    "accel-sc-platanus": "funds/:platanus.ventures#investment-vehicle",
    "accel-ventiur-acelera-impacto": "funds/brazil/ventiur.md",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _jsonl_bytes(records: list[dict[str, Any]]) -> bytes:
    text = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in records
    )
    return text.encode("utf-8")


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _target_exists(destination: str) -> bool:
    if destination.startswith(("epic-", "funds/:")):
        return False
    path_text, separator, fragment = destination.partition("#")
    path = REPOSITORY_ROOT / path_text
    if not path.is_file():
        return False
    if not separator:
        return True
    try:
        return fragment in path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False


def _load_inputs() -> tuple[
    dict[str, list[tuple[str, dict[str, Any]]]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, str],
]:
    occurrences: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    evidence: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}

    for run in RUNS:
        run_dir = EPIC_ROOT / run
        for filename in (
            "candidates.jsonl",
            "evidence.jsonl",
            "source-inventory.jsonl",
        ):
            path = run_dir / filename
            payload = path.read_bytes().replace(b"\r\n", b"\n")
            input_hashes[path.relative_to(REPOSITORY_ROOT).as_posix()] = _sha256(
                payload
            )
        for candidate in _read_jsonl(run_dir / "candidates.jsonl"):
            occurrences[candidate["candidate_id"]].append((run, candidate))
        evidence.extend(_read_jsonl(run_dir / "evidence.jsonl"))
        sources.extend(_read_jsonl(run_dir / "source-inventory.jsonl"))

    return occurrences, evidence, sources, dict(sorted(input_hashes.items()))


def _merge_candidates(
    candidate_id: str, rows: list[tuple[str, dict[str, Any]]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    regional = [(run, row) for run, row in rows if run in REGIONAL_RUNS]
    if len(rows) == 1:
        selected_run, selected = rows[0]
    else:
        expected_run = EXPECTED_DUPLICATES.get(candidate_id)
        actual_runs = {run for run, _ in rows}
        if (
            expected_run is None
            or actual_runs != {"pilot", expected_run}
            or len(regional) != 1
        ):
            raise ValueError(
                f"duplicata não autorizada para {candidate_id}: {sorted(actual_runs)}"
            )
        selected_run, selected = regional[0]

    merged = dict(selected)
    merged["discovery_source_ids"] = sorted(
        {
            source_id
            for _, row in rows
            for source_id in row["discovery_source_ids"]
        }
    )
    merged["official_evidence_ids"] = sorted(
        {
            evidence_id
            for _, row in rows
            for evidence_id in row["official_evidence_ids"]
        }
    )
    index = {
        "candidate_id": candidate_id,
        "selected_run": selected_run,
        "source_runs": sorted(run for run, _ in rows),
        "input_decisions": [
            {"run": run, "decision": row["decision"], "destination": row["destination"]}
            for run, row in sorted(rows)
        ],
        "merged_occurrences": len(rows),
    }
    return merged, index


def _apply_resolutions(candidate: dict[str, Any]) -> list[str]:
    candidate_id = candidate["candidate_id"]
    notes: list[str] = []

    if candidate_id == "accel-google-for-startups-brazil":
        candidate.update(decision=ELIGIBLE, destination=None, reason=None)
        notes.append(
            "Encaminhamento interno removido: a evidência regional já satisfaz "
            "categoria, atividade, acesso externo e geografia."
        )
    elif candidate_id == "accel-and-rockstart":
        candidate.update(
            decision=INSUFFICIENT,
            destination=None,
            owner="worker-and-08",
            next_action=(
                "Obter evidência oficial atual de programa estruturado, atividade, "
                "acesso externo e candidatura para Rockstart LATAM."
            ),
            reason=(
                "A fonte confirma a operadora, mas não comprova programa estruturado "
                "atual, atividade ou acesso externo; a auditoria estrangeira não "
                "produziu candidato canônico correspondente."
            ),
        )
        notes.append("Encaminhamento interno sem destino convertido em pendência.")
    elif candidate_id == "accel-mxcac-sparklabs":
        candidate.update(
            decision=INSUFFICIENT,
            destination=None,
            owner="worker-mxcac-03",
            next_action=(
                "Obter fonte oficial que confirme identidade, atividade, seleção "
                "externa e candidatura do programa SparkLabs Mexico."
            ),
            reason=(
                "A operadora global não lista um programa mexicano atual e a auditoria "
                "estrangeira não produziu candidato canônico correspondente."
            ),
        )
        notes.append("Encaminhamento interno sem destino convertido em pendência.")

    if candidate_id in PUBLIC_DESTINATIONS:
        destination = PUBLIC_DESTINATIONS[candidate_id]
        candidate["destination"] = destination
        if not _target_exists(destination):
            candidate["owner"] = "epic-65-consolidator"
            candidate["next_action"] = (
                f"Adjudicar {candidate_id} na consolidação pública da issue #102."
            )
        notes.append(f"Destino público normalizado para {destination}.")

    if candidate_id in FUND_DESTINATIONS:
        destination = FUND_DESTINATIONS[candidate_id]
        candidate["destination"] = destination
        if not _target_exists(destination):
            candidate["owner"] = "funds-maintainer"
            candidate["next_action"] = (
                "Avaliar o veículo no backlog de fundos sem publicar nesta issue."
            )
        notes.append(f"Destino de fundo normalizado para {destination}.")

    return notes


def _build() -> dict[str, bytes]:
    occurrences, evidence, sources, input_hashes = _load_inputs()
    candidates: list[dict[str, Any]] = []
    registry_index: list[dict[str, Any]] = []

    for candidate_id in sorted(occurrences):
        candidate, index = _merge_candidates(candidate_id, occurrences[candidate_id])
        index["resolution_notes"] = _apply_resolutions(candidate)
        index["final_decision"] = candidate["decision"]
        index["canonical_destination"] = candidate["destination"]
        candidates.append(candidate)
        registry_index.append(index)

    evidence.sort(key=lambda row: row["evidence_id"])
    sources.sort(key=lambda row: row["source_id"])

    candidate_ids = {row["candidate_id"] for row in candidates}
    if len(candidates) != 78 or sum(len(rows) for rows in occurrences.values()) != 80:
        raise ValueError("contagem de entrada ou registro canônico divergente")
    if any(row["decision"] is None for row in candidates):
        raise ValueError("candidato sem decisão")
    if any(
        "75" in str(row.get("destination"))
        for row in candidates
        if row.get("destination")
    ):
        raise ValueError("encaminhamento interno para #75 permaneceu no registro")
    if any(
        not row.get("owner") or not row.get("next_action")
        for row in candidates
        if row["decision"] == INSUFFICIENT
    ):
        raise ValueError("pendência de evidência sem responsável ou próxima ação")
    if any(
        not row.get("destination")
        for row in candidates
        if row["decision"] in {ROUTED_FUNDS, ROUTED_EPIC}
    ):
        raise ValueError("encaminhamento sem destino canônico")
    if any(row["candidate_id"] not in candidate_ids for row in evidence):
        raise ValueError("evidência órfã")

    cross_category: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        if candidate["decision"] in {ROUTED_FUNDS, ROUTED_EPIC}:
            destination = candidate["destination"]
            cross_category.append(
                {
                    "candidate_id": candidate_id,
                    "relationship": "encaminhado",
                    "canonical_destination": destination,
                    "destination_status": (
                        "materializado" if _target_exists(destination) else "fila-canônica"
                    ),
                    "accelerator_decision": candidate["decision"],
                }
            )
        elif candidate_id in HYBRID_DESTINATIONS:
            destination = HYBRID_DESTINATIONS[candidate_id]
            cross_category.append(
                {
                    "candidate_id": candidate_id,
                    "relationship": "unidades-distintas",
                    "canonical_destination": destination,
                    "destination_status": (
                        "materializado" if _target_exists(destination) else "fila-canônica"
                    ),
                    "accelerator_decision": candidate["decision"],
                }
            )

    vehicle_resolutions = []
    for candidate in candidates:
        vehicle_id = candidate.get("investment_vehicle_id")
        if not vehicle_id:
            continue
        destination = (
            FUND_DESTINATIONS.get(candidate["candidate_id"])
            or HYBRID_DESTINATIONS.get(candidate["candidate_id"])
            or f"funds/:{vehicle_id}"
        )
        vehicle_resolutions.append(
            {
                "candidate_id": candidate["candidate_id"],
                "investment_vehicle_id": vehicle_id,
                "relationship": (
                    "entidade-encaminhada"
                    if candidate["decision"] == ROUTED_FUNDS
                    else "programa-e-veículo-distintos"
                ),
                "canonical_destination": destination,
                "destination_status": (
                    "materializado" if _target_exists(destination) else "não-publicado"
                ),
            }
        )

    decision_counts = dict(
        sorted(Counter(row["decision"] for row in candidates).items())
    )
    queued_routes = sum(
        1
        for row in cross_category
        if row["relationship"] == "encaminhado"
        and row["destination_status"] == "fila-canônica"
    )
    resolution_document = {
        "schema_version": "1.0",
        "issue": 76,
        "cutoff_date": "2026-07-27",
        "cross_category_resolutions": sorted(
            cross_category, key=lambda row: row["candidate_id"]
        ),
        "vehicle_resolutions": sorted(
            vehicle_resolutions, key=lambda row: row["candidate_id"]
        ),
    }

    outputs: dict[str, bytes] = {
        "candidates.jsonl": _jsonl_bytes(candidates),
        "evidence.jsonl": _jsonl_bytes(evidence),
        "source-inventory.jsonl": _jsonl_bytes(sources),
        "registry-index.json": _json_bytes(registry_index),
        "category-resolutions.json": _json_bytes(resolution_document),
    }
    output_hashes = {name: _sha256(payload) for name, payload in outputs.items()}
    manifest = {
        "schema_version": "1.0",
        "issue": 76,
        "cutoff_date": "2026-07-27",
        "status": "provisional",
        "input_occurrences": 80,
        "canonical_candidates": 78,
        "merged_duplicate_occurrences": 2,
        "decision_counts": decision_counts,
        "cross_category_resolutions": len(cross_category),
        "vehicle_resolutions": len(vehicle_resolutions),
        "queued_route_follow_ups": queued_routes,
        "input_hashes": input_hashes,
        "output_hashes": output_hashes,
    }
    outputs["consolidation-manifest.json"] = _json_bytes(manifest)

    report = f"""# Registro provisório consolidado de aceleradoras

Este bundle materializa a issue #76 na data de corte 2026-07-27. Ele não
publica perfis.

## Resultado

- Ocorrências de entrada: 80.
- Candidatos canônicos: 78.
- Ocorrências duplicadas fundidas: 2.
- Decisões: {json.dumps(decision_counts, ensure_ascii=False, sort_keys=True)}.
- Resoluções entre categorias: {len(cross_category)}.
- Veículos separados de seus programas: {len(vehicle_resolutions)}.
- Encaminhamentos em fila canônica com responsável e próxima ação:
  {queued_routes}.

As duas duplicatas eram `accel-oxigenio` e `accel-kruger-labs`, coletadas no
piloto e revalidadas regionalmente. A versão regional prevalece, e as listas de
fontes e evidências das duas ocorrências são preservadas.

## Conflitos resolvidos

- Google for Startups Accelerator: Brazil passou de encaminhamento interno
  para `elegível`, apoiado pela evidência oficial completa da auditoria
  brasileira.
- Rockstart LATAM e SparkLabs Mexico passaram de encaminhamentos internos sem
  destino para `evidência-insuficiente`, cada um com responsável e próxima
  ação.
- Os 13 programas públicos receberam IDs ou caminhos canônicos da epic #65.
- Os três encaminhamentos para fundos receberam caminho publicado ou namespace
  canônico de backlog.
- Programas híbridos e seus veículos permanecem unidades distintas; o mesmo
  capital não é contado como prova de duas categorias.

## Lacunas acionáveis

Os 19 registros com `evidência-insuficiente` têm `owner` e `next_action`. Os
encaminhamentos ainda não materializados fora desta epic também têm responsável
e próxima ação. Uma fila canônica não significa que o perfil de destino já foi
publicado.

## Artefatos

- `candidates.jsonl`: registro canônico completo e compatível com o contrato.
- `evidence.jsonl` e `source-inventory.jsonl`: proveniência combinada.
- `registry-index.json`: execução escolhida, ocorrências e mudança de decisão.
- `category-resolutions.json`: encaminhamentos, híbridos e veículos.
- `consolidation-manifest.json`: contagens e hashes das entradas e saídas.

## Reprodução

```text
python research/epic-62/consolidation/build_registry.py
python research/epic-62/consolidation/build_registry.py --check
python -m unittest discover -s research/epic-62/consolidation/tests -p "test_*.py"
python tools/research/validate.py --base-ref origin/main
```
"""
    outputs["README.md"] = report.encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check", action="store_true", help="fail when generated files differ"
    )
    args = parser.parse_args()
    outputs = _build()
    drift: list[str] = []
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
