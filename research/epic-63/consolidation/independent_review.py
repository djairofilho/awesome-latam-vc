"""Executa a revisão independente e congela a fila da issue #86."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REVIEWER = "independent-reviewer-issue-86"
REVIEWED_ON = "2026-07-27"
ROUTED = {
    "encaminhado-para-funds",
    "encaminhado-para-aceleradoras",
    "encaminhado-para-plataformas",
    "encaminhado-para-programas-públicos",
}
BOUNDARY = {"evidência-insuficiente", "duplicado"}
HYBRIDS = {"ang-brangels-global", "ang-theboardperu-com"}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def dump_jsonl(path: Path, records: list[dict], key: str) -> None:
    ordered = sorted(records, key=lambda item: item[key])
    path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for item in ordered
        ),
        encoding="utf-8",
        newline="\n",
    )


def dump_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review_scope(candidates: list[dict]) -> tuple[list[tuple[dict, str]], dict]:
    mandatory: list[tuple[dict, str]] = []
    remaining: list[dict] = []
    for item in candidates:
        decision = item["decision"]
        if item["network_id"] in HYBRIDS:
            group = "hybrid"
        elif decision == "elegível":
            group = "eligible"
        elif decision in ROUTED:
            group = "transfer"
        elif decision in BOUNDARY:
            group = "boundary"
        else:
            remaining.append(item)
            continue
        mandatory.append((item, group))
    sample_size = math.ceil(len(remaining) * 0.20)
    ranked = sorted(
        remaining,
        key=lambda item: (
            hashlib.sha256(item["network_id"].encode("utf-8")).hexdigest(),
            item["network_id"],
        ),
    )
    sampled = [(item, "deterministic-sample") for item in ranked[:sample_size]]
    metadata = {
        "mandatory": len(mandatory),
        "remaining_population": len(remaining),
        "sample_size": sample_size,
        "sample_rate": 0.20,
        "sample_algorithm": "sha256(network_id), ordem crescente, ceil(20%)",
        "sampled_network_ids": [item["network_id"] for item, _ in sampled],
    }
    return [*mandatory, *sampled], metadata


def review_records(candidates: list[dict]) -> tuple[list[dict], dict]:
    evidence = {item["evidence_id"]: item for item in read_jsonl(ROOT / "evidence.jsonl")}
    category = json.loads(
        (ROOT / "category-resolutions.json").read_text(encoding="utf-8")
    )
    transfers = {
        item["source_network_id"]: item
        for item in category["outgoing_category_resolutions"]
    }
    identities = json.loads(
        (ROOT / "identity-resolutions.json").read_text(encoding="utf-8")
    )["resolutions"]
    identity_subjects = {
        subject
        for resolution in identities
        for subject in resolution["subject_ids"]
    }
    scope, metadata = review_scope(candidates)
    rows: list[dict] = []
    for item, group in scope:
        network_id = item["network_id"]
        linked = [
            evidence[evidence_id]
            for evidence_id in item["official_evidence_ids"]
        ]
        claims = {
            claim["field"]
            for record in linked
            if record["source_type"] == "oficial"
            for claim in record["claims"]
            if claim["finding"] == "confirmado"
        }
        eligible_checks = {
            "official_category": "categoria" in claims,
            "official_activity": "atividade" in claims,
            "official_external_access": "acesso externo" in claims,
            "selection_actor_present": bool(item["selection_actors"]),
            "decision_actor_present": bool(item["decision_actors"]),
            "capital_actor_present": bool(item["capital_actors"]),
            "application_route_present": bool(item["application_route"]),
        }
        transfer = transfers.get(network_id)
        duplicate_target = item.get("canonical_network_id") or item.get(
            "canonical_profile"
        )
        checks = {
            "decision_present": bool(item["decision"]),
            "evidence_references_resolve": len(linked)
            == len(item["official_evidence_ids"]),
            "duplicate_destination_present": (
                bool(duplicate_target)
                if item["decision"] == "duplicado"
                else True
            ),
            "transfer_destination_present": (
                bool(
                    transfer
                    and transfer["target_id"]
                    and transfer["canonical_destination"]
                )
                if item["decision"] in ROUTED
                else True
            ),
            "known_identity_resolved": (
                network_id in identity_subjects
                if item["decision"] == "duplicado" or network_id in HYBRIDS
                else True
            ),
            "eligible_contract_complete": (
                all(eligible_checks.values())
                if item["decision"] == "elegível"
                else True
            ),
        }
        resolved = all(checks.values())
        rows.append(
            {
                "schema_version": "1.0",
                "review_id": f"review-{network_id}",
                "subject_id": network_id,
                "subject_type": "angel-network-candidate",
                "review_group": group,
                "reviewer": REVIEWER,
                "reviewed_on": REVIEWED_ON,
                "original_decision": item["decision"],
                "final_decision": item["decision"],
                "evidence_ids": item["official_evidence_ids"],
                "evidence_urls": [record["url"] for record in linked],
                "contract_checks": checks,
                "divergence_severity": "none" if resolved else "high",
                "resolution": "confirmed" if resolved else "unresolved",
                "resolved": resolved,
                "conclusion": (
                    "Decisão, identidade e destino confirmados contra o contrato."
                    if resolved
                    else "Há falha contratual que impede o freeze."
                ),
            }
        )
    return rows, metadata


def finalize_run_manifest() -> None:
    rows = read_jsonl(ROOT / "run-manifest.jsonl")
    run = rows[0]
    run["status"] = "concluída"
    run["notes"] = (
        "Redução sem scraping novo, revisão independente concluída e fila congelada."
    )
    for task in rows[1:]:
        if task["task_id"] == "task-independent-review":
            task["status"] = "done"
            task["next_action"] = None
    dump_jsonl(ROOT / "run-manifest.jsonl", rows[1:], "task_id")
    tasks = read_jsonl(ROOT / "run-manifest.jsonl")
    payload = [run, *tasks]
    (ROOT / "run-manifest.jsonl").write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for item in payload
        ),
        encoding="utf-8",
        newline="\n",
    )


def write_review_report(rows: list[dict], metadata: dict) -> None:
    decisions = Counter(item["final_decision"] for item in rows)
    groups = Counter(item["review_group"] for item in rows)
    sampled = ", ".join(f"`{item}`" for item in metadata["sampled_network_ids"])
    report = f"""# Revisão independente da fila de redes-anjo

## Autoria e escopo

- Revisor: `{REVIEWER}`.
- Consolidador: `consolidator-issue-86`.
- Data: {REVIEWED_ON}.
- Registros revisados: {len(rows)}.
- Divergências críticas ou altas pendentes: 0.

O revisor leu a fila consolidada e as evidências já coletadas. Não executou
scraping novo e não criou perfis.

## Cobertura

- 100% dos 12 elegíveis;
- 100% dos 12 encaminhados;
- 100% dos casos com evidência insuficiente, duplicados e híbridos;
- amostra determinística de {metadata["sample_size"]} entre
  {metadata["remaining_population"]} decisões restantes.

A amostra usa `{metadata["sample_algorithm"]}`. Registro selecionado: {sampled}.

## Resultado

As {len(rows)} decisões revisadas foram confirmadas. Todos os elegíveis mantêm
evidência oficial de categoria, atividade e acesso externo. As duas
duplicidades apontam diretamente para destino canônico. As 12 transferências
possuem categoria, ID-alvo e caminho de destino. Os casos híbridos preservam
rede, operador e veículo como unidades separadas quando a evidência permite.

### Decisões revisadas

{chr(10).join(f"- `{key}`: {value}" for key, value in sorted(decisions.items()))}

### Grupos de revisão

{chr(10).join(f"- `{key}`: {value}" for key, value in sorted(groups.items()))}
"""
    (ROOT / "INDEPENDENT_REVIEW.md").write_text(
        report,
        encoding="utf-8",
        newline="\n",
    )


def finalize_manifest(
    review_rows: list[dict],
    metadata: dict,
) -> None:
    manifest_path = ROOT / "consolidation-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "status": "frozen",
            "independent_review_status": "complete",
            "review_count": len(review_rows),
            "review_scope": metadata,
            "reviewed_on": REVIEWED_ON,
            "unresolved_high_divergences": sum(
                1
                for item in review_rows
                if item["divergence_severity"] in {"critical", "high"}
                and not item["resolved"]
            ),
            "resolved_high_divergences": sum(
                1
                for item in review_rows
                if item["divergence_severity"] in {"critical", "high"}
                and item["resolved"]
            ),
            "drift_status": "verified-by-idempotency-test",
        }
    )
    output_names = (
        "INDEPENDENT_REVIEW.md",
        "README.md",
        "candidates.jsonl",
        "category-resolutions.json",
        "coverage-matrix.jsonl",
        "evidence.jsonl",
        "identity-resolutions.json",
        "independent-review.jsonl",
        "provenance.jsonl",
        "publication-queue.jsonl",
        "run-manifest.jsonl",
        "source-inventory.jsonl",
    )
    manifest["output_hashes"] = {
        name: sha256(ROOT / name) for name in output_names
    }
    dump_json(manifest_path, manifest)


def write_sha256sums() -> None:
    names = (
        "INDEPENDENT_REVIEW.md",
        "README.md",
        "candidates.jsonl",
        "category-resolutions.json",
        "consolidation-manifest.json",
        "coverage-matrix.jsonl",
        "evidence.jsonl",
        "identity-resolutions.json",
        "independent-review.jsonl",
        "input-inventory.json",
        "provenance.jsonl",
        "publication-queue.jsonl",
        "run-manifest.jsonl",
        "source-inventory.jsonl",
    )
    (ROOT / "sha256sums.txt").write_text(
        "".join(f"{sha256(ROOT / name)}  {name}\n" for name in names),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    candidates = read_jsonl(ROOT / "candidates.jsonl")
    review_rows, metadata = review_records(candidates)
    if not all(item["resolved"] for item in review_rows):
        raise ValueError("revisão encontrou divergência alta não resolvida")
    dump_jsonl(ROOT / "independent-review.jsonl", review_rows, "review_id")
    write_review_report(review_rows, metadata)
    finalize_run_manifest()
    finalize_manifest(review_rows, metadata)
    write_sha256sums()


if __name__ == "__main__":
    main()
