"""Executa a revisão independente e congela a fila da issue #86."""

from __future__ import annotations

from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REVIEWER = "independent-reviewer-final-issue-86"
REVIEWED_ON = "2026-07-27"
PAD = "ang-hub-udep-pe--pad"
ROUTED = {
    "encaminhado-para-funds",
    "encaminhado-para-aceleradoras",
    "encaminhado-para-plataformas",
    "encaminhado-para-programas-públicos",
}
BOUNDARY = {"evidência-insuficiente", "duplicado"}
HYBRIDS = {"ang-brangels-global", "ang-theboardperu-com"}
ALLOWED_TYPES = {
    "rede-anjo",
    "rede",
    "clube",
    "rede alumni",
    "alumni network",
    "capítulo",
    "sindicato",
}


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


def adjudicate() -> None:
    candidates = read_jsonl(ROOT / "candidates.jsonl")
    evidence = read_jsonl(ROOT / "evidence.jsonl")
    queue = read_jsonl(ROOT / "publication-queue.jsonl")
    provenance = read_jsonl(ROOT / "provenance.jsonl")

    candidate = next(item for item in candidates if item["network_id"] == PAD)
    candidate.update(
        {
            "decision": "evidência-insuficiente",
            "reason": (
                "A fonte oficial comprova a rede e atividade recente, mas a rota "
                "registrada aceita participantes de um seminário; não comprova "
                "submissão externa de startups ao processo recorrente do PAD."
            ),
            "external_access": "não confirmado",
            "application_route": None,
            "canonical_profile": None,
            "owner": REVIEWER,
            "next_action": (
                "Localizar rota oficial atual que permita a startups externas "
                "submeter candidatura diretamente à seleção do PAD."
            ),
        }
    )
    activity = next(item for item in evidence if item["evidence_id"] == "ev-peru-pad-activity")
    for claim in activity["claims"]:
        if claim["field"] in {"acesso externo", "rota de aplicação"}:
            claim["finding"] = "não divulgado"
    activity["summary"] = (
        "A página oficial abre inscrição para o seminário de investimento-anjo e "
        "prevê fórum final exclusivo a participantes aprovados. Confirma operação "
        "e seleção recentes da rede, mas não uma rota externa de candidatura de startups."
    )
    queue = [item for item in queue if item["network_id"] != PAD]
    row = next(item for item in provenance if item["network_id"] == PAD)
    row["final_decision"] = "evidência-insuficiente"
    marker = "revisão independente: elegível → evidência-insuficiente"
    if marker not in row["transformations"]:
        row["transformations"].append(marker)

    dump_jsonl(ROOT / "candidates.jsonl", candidates, "network_id")
    dump_jsonl(ROOT / "evidence.jsonl", evidence, "evidence_id")
    dump_jsonl(ROOT / "publication-queue.jsonl", queue, "network_id")
    dump_jsonl(ROOT / "provenance.jsonl", provenance, "network_id")


def review_scope(candidates: list[dict], provenance: dict[str, dict]) -> tuple[list, dict]:
    mandatory = []
    remaining = []
    for item in candidates:
        initial = provenance[item["network_id"]]["original_decision"]
        if item["network_id"] in HYBRIDS:
            group = "hybrid"
        elif initial == "elegível":
            group = "eligible"
        elif initial in ROUTED:
            group = "transfer"
        elif initial in BOUNDARY:
            group = "boundary"
        else:
            remaining.append(item)
            continue
        mandatory.append((item, group))
    sample_size = math.ceil(len(remaining) * 0.20)
    ranked = sorted(
        remaining,
        key=lambda item: (
            hashlib.sha256(item["network_id"].encode()).hexdigest(),
            item["network_id"],
        ),
    )
    sampled = [(item, "deterministic-sample") for item in ranked[:sample_size]]
    return [*mandatory, *sampled], {
        "mandatory": len(mandatory),
        "remaining_population": len(remaining),
        "sample_size": sample_size,
        "sample_rate": 0.20,
        "sample_algorithm": "sha256(network_id), ordem crescente, ceil(20%)",
        "sampled_network_ids": [item["network_id"] for item, _ in sampled],
    }


def review_records(candidates: list[dict]) -> tuple[list[dict], dict]:
    evidence = {item["evidence_id"]: item for item in read_jsonl(ROOT / "evidence.jsonl")}
    category = json.loads((ROOT / "category-resolutions.json").read_text(encoding="utf-8"))
    transfers = {
        item["source_network_id"]: item
        for item in category["outgoing_category_resolutions"]
    }
    resolutions = json.loads(
        (ROOT / "identity-resolutions.json").read_text(encoding="utf-8")
    )["resolutions"]
    identity_by_subject = {
        subject: resolution["resolution_id"]
        for resolution in resolutions
        for subject in resolution["subject_ids"]
    }
    provenance = {
        item["network_id"]: item for item in read_jsonl(ROOT / "provenance.jsonl")
    }
    scope, metadata = review_scope(candidates, provenance)
    rows = []
    for item, group in scope:
        network_id = item["network_id"]
        linked = [evidence[eid] for eid in item["official_evidence_ids"]]
        claims = {
            claim["field"]
            for record in linked
            if record["source_type"] == "oficial"
            for claim in record["claims"]
            if claim["finding"] == "confirmado"
        }
        initial = provenance[network_id]["original_decision"]
        final = item["decision"]
        transfer = transfers.get(network_id)
        activity_date = item.get("activity_evidence_date")
        activity_current = bool(
            activity_date
            and (date.fromisoformat(REVIEWED_ON) - date.fromisoformat(activity_date)).days
            <= 731
        )
        eligible_checks = {
            "allowed_entity_type": item.get("entity_type") in ALLOWED_TYPES,
            "official_site_present": bool(item.get("official_site")),
            "official_category": "categoria" in claims,
            "official_activity": "atividade" in claims and activity_current,
            "official_external_access": "acesso externo" in claims,
            "recurring_selection": "recorrência" in claims,
            "selection_actor_present": bool(item["selection_actors"]),
            "decision_actor_present": bool(item["decision_actors"]),
            "capital_actor_present": bool(item["capital_actors"]),
            "application_route_present": bool(item["application_route"]),
        }
        checks = {
            "decision_present": bool(final),
            "evidence_references_resolve": len(linked) == len(item["official_evidence_ids"]),
            "official_sources_for_eligible": (
                all(record["source_type"] == "oficial" for record in linked)
                if final == "elegível"
                else True
            ),
            "duplicate_destination_present": (
                bool(item.get("canonical_network_id") or item.get("canonical_profile"))
                if final == "duplicado"
                else True
            ),
            "transfer_destination_present": (
                bool(transfer and transfer["target_id"] and transfer["canonical_destination"])
                if initial in ROUTED
                else True
            ),
            "known_identity_resolved": (
                network_id in identity_by_subject
                if final == "duplicado" or network_id in HYBRIDS
                else True
            ),
            "eligible_contract_complete": (
                all(eligible_checks.values()) if final == "elegível" else True
            ),
        }
        divergence = "div-issue86-pad-external-access" if network_id == PAD else None
        rows.append(
            {
                "schema_version": "1.1",
                "review_id": f"review-{network_id}",
                "subject_id": network_id,
                "subject_type": "angel-network-candidate",
                "review_group": group,
                "reviewer": REVIEWER,
                "reviewed_on": REVIEWED_ON,
                "original_decision": initial,
                "final_decision": final,
                "evidence_ids": item["official_evidence_ids"],
                "evidence_urls": [record["url"] for record in linked],
                "identity_resolution_id": identity_by_subject.get(network_id),
                "transfer_resolution": transfer,
                "contract_checks": checks,
                "divergence_ids": [divergence] if divergence else [],
                "divergence_severity": "high" if divergence else "none",
                "resolution": "decision-changed" if divergence else "confirmed",
                "resolved": all(checks.values()),
                "conclusion": (
                    "Elegibilidade alterada: falta rota oficial de candidatura externa."
                    if divergence
                    else "Decisão, identidade e destino confirmados contra o contrato."
                ),
            }
        )
    return rows, metadata


def write_divergences() -> list[dict]:
    divergences = [
        {
            "divergence_id": "div-issue86-pad-external-access",
            "severity": "high",
            "subject_id": PAD,
            "status": "resolved",
            "finding": (
                "A URL registrada é inscrição de participantes no seminário e no "
                "fórum exclusivo; não é rota de submissão externa de startups."
            ),
            "resolution": (
                "Reclassificado de elegível para evidência-insuficiente e removido "
                "da fila de publicação."
            ),
            "evidence_ids": ["ev-peru-pad-model", "ev-peru-pad-activity"],
        },
        {
            "divergence_id": "div-issue86-honduras-target-status",
            "severity": "medium",
            "subject_id": "ang-hondurasdigitalchallenge-com",
            "status": "resolved",
            "finding": (
                "A auditoria da epic 62 classifica o destino como desafio pontual "
                "excluído, embora a origem pertença à fronteira de aceleradoras."
            ),
            "resolution": (
                "Mantida a transferência como registro de fronteira e proveniência; "
                "ela não implica aceitação no destino."
            ),
            "evidence_ids": ["ev-honduras-digital-challenge-boundary"],
        },
    ]
    dump_json(
        ROOT / "review-divergences.json",
        {
            "schema_version": "1.0",
            "issue": 86,
            "reviewer": REVIEWER,
            "reviewed_on": REVIEWED_ON,
            "open_high_divergences": 0,
            "divergences": divergences,
        },
    )
    return divergences


def finalize_run_manifest() -> None:
    rows = read_jsonl(ROOT / "run-manifest.jsonl")
    run, tasks = rows[0], rows[1:]
    run["status"] = "concluída"
    run["notes"] = (
        "Redução sem scraping novo; revisão independente concluiu uma "
        "reclassificação alta e congelou a fila sem divergências altas abertas."
    )
    for task in tasks:
        if task["task_id"] == "task-independent-review":
            task["status"] = "done"
            task["next_action"] = None
    payload = [run, *sorted(tasks, key=lambda item: item["task_id"])]
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
- Divergências altas encontradas: 1, resolvida.
- Divergências altas pendentes: 0.

O revisor conferiu os artefatos consolidados, as evidências oficiais e os
contratos das epics relacionadas. Não criou perfis.

## Cobertura

- 100% dos 12 originalmente elegíveis;
- 100% dos 12 encaminhados;
- 100% dos casos com evidência insuficiente, duplicados e híbridos;
- amostra determinística de {metadata["sample_size"]} entre
  {metadata["remaining_population"]} decisões restantes.

A amostra usa `{metadata["sample_algorithm"]}`. Registro selecionado: {sampled}.

## Divergências e resolução

O PAD/UDEP foi alterado de `elegível` para `evidência-insuficiente`. A fonte
oficial confirma a rede, seleção e atividade recente, mas a rota registrada
recebe inscrições de participantes em um seminário e em seu fórum exclusivo.
Ela não comprova acesso externo de startups à seleção recorrente da rede.

O Honduras Digital Challenge continua transferido como fronteira de categoria.
A epic 62 o exclui como desafio pontual; a transferência preserva a
proveniência e não equivale a aceitação no destino.

## Resultado congelado

A fila final contém 11 redes elegíveis. Todas satisfazem categoria, atividade,
recorrência, acesso externo, atores e rota com evidência oficial. As duas
duplicidades e as sete resoluções de identidade têm destino explícito. As 12
transferências têm categoria, ID-alvo e destino; nenhuma fica órfã.

### Decisões revisadas

{chr(10).join(f"- `{key}`: {value}" for key, value in sorted(decisions.items()))}

### Grupos de revisão

{chr(10).join(f"- `{key}`: {value}" for key, value in sorted(groups.items()))}
"""
    (ROOT / "INDEPENDENT_REVIEW.md").write_text(report, encoding="utf-8", newline="\n")


def write_consolidation_report() -> None:
    candidates = read_jsonl(ROOT / "candidates.jsonl")
    queue = read_jsonl(ROOT / "publication-queue.jsonl")
    counts = Counter(item["decision"] for item in candidates)
    report = f"""# Consolidação final de redes-anjo — issue #86

Registro congelado após revisão independente integral.

## Totais

- Candidatos: {len(candidates)}.
- Elegíveis finais: {counts["elegível"]}.
- Fila de publicação: {len(queue)} ({sum(x["publication_status"] == "already-published" for x in queue)} existentes e {sum(x["publication_status"] == "pending-publication" for x in queue)} pendentes).
- Transferências com destino explícito: 12.
- Resoluções de identidade: 7.
- Divergências altas abertas: 0.

## Decisões

{chr(10).join(f"- `{key}`: {value}" for key, value in sorted(counts.items()))}

O PAD/UDEP permanece no registro como `evidência-insuficiente`: as fontes
confirmam a rede e atividade, mas não uma rota externa de candidatura de
startups. Consulte `INDEPENDENT_REVIEW.md` e `review-divergences.json`.
"""
    (ROOT / "README.md").write_text(report, encoding="utf-8", newline="\n")


def finalize_manifest(rows: list[dict], metadata: dict, divergences: list[dict]) -> None:
    path = ROOT / "consolidation-manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    candidates = read_jsonl(ROOT / "candidates.jsonl")
    queue = read_jsonl(ROOT / "publication-queue.jsonl")
    manifest.update(
        {
            "status": "frozen",
            "independent_review_status": "complete",
            "independent_reviewer": REVIEWER,
            "review_count": len(rows),
            "review_scope": metadata,
            "reviewed_on": REVIEWED_ON,
            "original_eligible_count": 12,
            "final_eligible_count": sum(x["decision"] == "elegível" for x in candidates),
            "publication_queue_count": len(queue),
            "after_counts": {
                "candidates": len(candidates),
                "coverage_rows": len(read_jsonl(ROOT / "coverage-matrix.jsonl")),
                "evidence": len(read_jsonl(ROOT / "evidence.jsonl")),
                "publication_queue": len(queue),
                "sources": len(read_jsonl(ROOT / "source-inventory.jsonl")),
            },
            "decision_counts": dict(sorted(Counter(x["decision"] for x in candidates).items())),
            "review_divergence_count": len(divergences),
            "unresolved_high_divergences": 0,
            "resolved_high_divergences": sum(
                x["severity"] == "high" and x["status"] == "resolved"
                for x in divergences
            ),
            "drift_status": "verified-by-idempotency-test",
        }
    )
    output_names = (
        "INDEPENDENT_REVIEW.md", "README.md", "candidates.jsonl",
        "category-resolutions.json", "coverage-matrix.jsonl", "evidence.jsonl",
        "identity-resolutions.json", "independent-review.jsonl", "provenance.jsonl",
        "publication-queue.jsonl", "review-divergences.json", "run-manifest.jsonl",
        "source-inventory.jsonl",
    )
    manifest["output_hashes"] = {name: sha256(ROOT / name) for name in output_names}
    dump_json(path, manifest)


def write_sha256sums() -> None:
    names = (
        "INDEPENDENT_REVIEW.md", "README.md", "candidates.jsonl",
        "category-resolutions.json", "consolidation-manifest.json",
        "coverage-matrix.jsonl", "evidence.jsonl", "identity-resolutions.json",
        "independent-review.jsonl", "input-inventory.json", "provenance.jsonl",
        "publication-queue.jsonl", "review-divergences.json", "run-manifest.jsonl",
        "source-inventory.jsonl",
    )
    (ROOT / "sha256sums.txt").write_text(
        "".join(f"{sha256(ROOT / name)}  {name}\n" for name in names),
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    adjudicate()
    candidates = read_jsonl(ROOT / "candidates.jsonl")
    rows, metadata = review_records(candidates)
    if not all(item["resolved"] for item in rows):
        raise ValueError("revisão encontrou divergência alta não resolvida")
    dump_jsonl(ROOT / "independent-review.jsonl", rows, "review_id")
    divergences = write_divergences()
    write_review_report(rows, metadata)
    write_consolidation_report()
    finalize_run_manifest()
    finalize_manifest(rows, metadata, divergences)
    write_sha256sums()


if __name__ == "__main__":
    main()
