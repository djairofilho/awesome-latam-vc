"""Consolida deterministicamente as auditorias da epic #63."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[2]
CUTOFF = "2026-07-27"
RUN_ID = "run-issue-86-angels-consolidation"

AUDITS = {
    "issue-81": ROOT.parent / "issue-81",
    "issue-82": ROOT.parent / "issue-82",
    "issue-83": ROOT.parent / "mexico-cac",
    "issue-84": ROOT.parent / "issue-84",
    "issue-85": ROOT.parent / "southern-cone",
}
FILES = (
    "candidates.jsonl",
    "coverage-matrix.jsonl",
    "evidence.jsonl",
    "run-manifest.jsonl",
    "source-inventory.jsonl",
)
KEYS = {
    "candidates.jsonl": "network_id",
    "coverage-matrix.jsonl": "coverage_id",
    "evidence.jsonl": "evidence_id",
    "source-inventory.jsonl": "source_id",
}

PROPOSED_PROFILES = {
    "ang-curitibaangels-com-br": "ecosystem/angel-networks/brazil/curitiba-angels.md",
    "ang-pucangels-org": "ecosystem/angel-networks/brazil/puc-angels.md",
    "ang-enlaces-org-do": "ecosystem/angel-networks/dominican-republic/enlaces.md",
    "ang-firstangelscaribbean-com": "ecosystem/angel-networks/jamaica/firstangels-caribbean.md",
    "ang-hub-udep-pe--pad": "ecosystem/angel-networks/peru/pad-red-inversionistas-angeles.md",
    "ang-businessangelsclub-org": "ecosystem/angel-networks/argentina/business-angels-club.md",
    "ang-centrodeinnovacion-uc-cl--red-angeles": "ecosystem/angel-networks/chile/red-angeles-uc.md",
}

TRANSFER_TARGETS = {
    "ang-bossainvest-com": ("funds", "funds/brazil/bossa-invest-bossanova.md", "fund-profile:bossa-invest"),
    "ang-barrilete-vc": ("funds", "funds/regional/barrilete-ventures.md", "fund-profile:barrilete-ventures"),
    "ang-parquetec-org--invertup": ("funds", "funds/regional/invertup.md", "fund-profile:invertup"),
    "ang-ventureclublatam-com": ("funds", "funds/regional/venture-club-latam.md", "fund-profile:venture-club-latam"),
    "ang-hondurasdigitalchallenge-com": ("epic-62", "ecosystem/accelerators/honduras/honduras-digital-challenge.md", "accel-mxcac-honduras-digital"),
    "ang-parquetec-org": ("epic-62", "ecosystem/accelerators/costa-rica/parquetec.md", "accel-mxcac-parquetec"),
    "ang-carib-export-com--caribbean-business-angel-network": ("epic-64", "ecosystem/funding-platforms/regional/caribbean-business-angel-network.md", "plat-caribbean-business-angel-network"),
    "ang-winverz-com": ("epic-64", "ecosystem/funding-platforms/guatemala/winverz.md", "plat-winverz"),
    "ang-angelinvestmentnetwork-com-co": ("epic-64", "ecosystem/funding-platforms/red-colombiana-de-inversiones.md", "plat-red-colombiana-de-inversiones"),
    "ang-angelinvestmentnetwork-cl": ("epic-64", "ecosystem/funding-platforms/red-chilena-de-inversiones.md", "plat-red-chilena-de-inversiones"),
    "ang-angelinvestmentnetwork-uy": ("epic-64", "ecosystem/funding-platforms/red-uruguaya-de-inversiones.md", "plat-red-uruguaya-de-inversiones"),
    "ang-uruguayxxi-gub-uy--apep": ("epic-65", "ecosystem/public-programs/uruguay/red-inversores-apep.md", "program-red-inversores-apep"),
}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def serialized(records: list[dict], key: str) -> str:
    ordered = sorted(records, key=lambda item: item[key])
    return "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for item in ordered
    )


def dump_jsonl(path: Path, records: list[dict], key: str) -> None:
    path.write_text(serialized(records, key), encoding="utf-8", newline="\n")


def dump_ordered_jsonl(path: Path, records: list[dict]) -> None:
    payload = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for item in records
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def dump_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_input_inventory() -> dict:
    inventory = json.loads((ROOT / "input-inventory.json").read_text(encoding="utf-8"))
    for relative, expected in inventory["inputs"].items():
        actual = sha256(REPOSITORY / relative)
        if actual != expected:
            raise ValueError(
                f"entrada divergiu do freeze: {relative}: {actual} != {expected}"
            )
    return inventory


def merge_records(filename: str) -> tuple[list[dict], dict[str, str]]:
    key = KEYS[filename]
    by_id: dict[str, dict] = {}
    provenance: dict[str, str] = {}
    for audit, directory in AUDITS.items():
        for record in read_jsonl(directory / filename):
            record_id = record[key]
            existing = by_id.get(record_id)
            if existing is not None and existing != record:
                raise ValueError(f"registro conflitante: {filename}:{record_id}")
            by_id[record_id] = record
            provenance[record_id] = audit
    return [by_id[item] for item in sorted(by_id)], provenance


def consolidate_candidates(
    candidates: list[dict],
    candidate_provenance: dict[str, str],
) -> tuple[list[dict], list[dict], list[dict]]:
    output: list[dict] = []
    queue: list[dict] = []
    provenance_rows: list[dict] = []
    for original in candidates:
        item = deepcopy(original)
        transformations: list[str] = []
        network_id = item["network_id"]
        if network_id == "ang-mulheresinvestidoras-net":
            item["canonical_network_id"] = "ang-anjosdobrasil-net"
            transformations.append("destino de alias ligado ao ID canônico")
        if item["decision"] == "elegível" and not item["canonical_profile"]:
            item["canonical_profile"] = PROPOSED_PROFILES[network_id]
            transformations.append("rota publicável proposta")
        output.append(item)
        audit = candidate_provenance[network_id]
        provenance_rows.append(
            {
                "schema_version": "1.0",
                "network_id": network_id,
                "source_audit": audit,
                "source_path": str(
                    (AUDITS[audit] / "candidates.jsonl")
                    .relative_to(REPOSITORY)
                ).replace("\\", "/"),
                "original_decision": original["decision"],
                "final_decision": item["decision"],
                "transformations": transformations,
            }
        )
        if item["decision"] == "elegível":
            queue.append(
                {
                    "schema_version": "1.0",
                    "queue_id": f"publish-{network_id}",
                    "network_id": network_id,
                    "name": item["name"],
                    "entity_type": item["entity_type"],
                    "base_country": item["base_country"],
                    "source_audit": audit,
                    "canonical_profile": item["canonical_profile"],
                    "publication_status": (
                        "already-published"
                        if item["already_listed"]
                        else "pending-publication"
                    ),
                    "activity_evidence_date": item["activity_evidence_date"],
                    "application_route": item["application_route"],
                }
            )
    return output, queue, provenance_rows


def identity_resolutions() -> dict:
    return {
        "schema_version": "1.0",
        "issue": 86,
        "resolutions": [
            {
                "resolution_id": "identity-mia-anjos-do-brasil",
                "subject_ids": ["ang-mulheresinvestidoras-net", "ang-anjosdobrasil-net"],
                "resolution": "alias",
                "canonical_network_id": "ang-anjosdobrasil-net",
                "reason": "O MIA declara integração à Anjos do Brasil e não comprova autonomia publicável.",
            },
            {
                "resolution_id": "identity-bac-mar-del-plata",
                "subject_ids": ["ang-businessangelsclub-org--mar-del-plata", "ang-businessangelsclub-org"],
                "resolution": "chapter-alias",
                "canonical_network_id": "ang-businessangelsclub-org",
                "reason": "O capítulo não comprova as quatro autonomias exigidas.",
            },
            {
                "resolution_id": "identity-firstangels-jamaica",
                "subject_ids": ["ang-firstangelscaribbean-com"],
                "resolution": "brand-alias",
                "canonical_network_id": "ang-firstangelscaribbean-com",
                "reason": "FirstAngels Jamaica é marca anterior da rede caribenha, não candidato separado.",
            },
            {
                "resolution_id": "identity-angel-investment-network-products",
                "subject_ids": ["ang-angelinvestmentnetwork-cl", "ang-angelinvestmentnetwork-com-co", "ang-angelinvestmentnetwork-uy"],
                "resolution": "distinct-country-products",
                "canonical_network_id": None,
                "reason": "Os domínios nacionais são produtos regionais distintos do mesmo modelo de plataforma e preservam destinos próprios na epic #64.",
            },
            {
                "resolution_id": "identity-parquetec-costa-rica-angels",
                "subject_ids": ["ang-parquetec-org", "ang-parquetec-org--costa-rica-angels"],
                "resolution": "operator-and-hosted-unit-distinct",
                "canonical_network_id": None,
                "reason": "ParqueTec é aceleradora; Costa Rica Angels é uma rede hospedada com decisão própria ainda insuficiente.",
            },
            {
                "resolution_id": "identity-br-angels-vehicle",
                "subject_ids": ["ang-brangels-global"],
                "resolution": "network-and-vehicle-distinct",
                "canonical_network_id": "ang-brangels-global",
                "reason": "O veículo agrupado é ator de capital e não substitui a identidade da rede.",
            },
            {
                "resolution_id": "identity-the-board-hybrid",
                "subject_ids": ["ang-theboardperu-com"],
                "resolution": "hybrid-retained-insufficient",
                "canonical_network_id": "ang-theboardperu-com",
                "reason": "Rede e fundo aparecem na mesma operação, sem prova para separar unidades canônicas.",
            },
        ],
    }


def category_resolutions(candidates: list[dict]) -> dict:
    by_id = {item["network_id"]: item for item in candidates}
    outgoing = []
    for network_id, (target_category, destination, target_id) in sorted(
        TRANSFER_TARGETS.items()
    ):
        item = by_id[network_id]
        outgoing.append(
            {
                "source_network_id": network_id,
                "source_name": item["name"],
                "source_decision": item["decision"],
                "target_category": target_category,
                "target_id": target_id,
                "canonical_destination": destination,
                "destination_status": (
                    "materialized"
                    if (REPOSITORY / destination).exists()
                    else "queued-with-explicit-target"
                ),
            }
        )
    incoming_baseline = [
        {
            "network_id": item["network_id"],
            "canonical_profile": item["canonical_profile"],
            "source": "catalog-baseline",
            "materialized": True,
        }
        for item in sorted(candidates, key=lambda row: row["network_id"])
        if item["already_listed"] and item["decision"] == "elegível"
    ]
    return {
        "schema_version": "1.0",
        "issue": 86,
        "incoming_baseline_profiles": incoming_baseline,
        "incoming_cross_epic_transfers": [],
        "outgoing_category_resolutions": outgoing,
    }


def provisional_manifest(
    inventory: dict,
    candidates: list[dict],
    evidence: list[dict],
    sources: list[dict],
    coverage: list[dict],
    queue: list[dict],
) -> dict:
    before_counts = {}
    for audit, directory in AUDITS.items():
        before_counts[audit] = {
            filename: len(read_jsonl(directory / filename))
            for filename in FILES
        }
    decision_counts = Counter(item["decision"] for item in candidates)
    core_files = (
        "candidates.jsonl",
        "category-resolutions.json",
        "coverage-matrix.jsonl",
        "evidence.jsonl",
        "identity-resolutions.json",
        "provenance.jsonl",
        "publication-queue.jsonl",
        "source-inventory.jsonl",
    )
    return {
        "schema_version": "1.0",
        "issue": 86,
        "cutoff_date": CUTOFF,
        "status": "provisional",
        "before_counts": before_counts,
        "before_occurrences": sum(
            values["candidates.jsonl"] for values in before_counts.values()
        ),
        "after_counts": {
            "candidates": len(candidates),
            "evidence": len(evidence),
            "sources": len(sources),
            "coverage_rows": len(coverage),
            "publication_queue": len(queue),
        },
        "decision_counts": dict(sorted(decision_counts.items())),
        "merged_duplicate_occurrences": 0,
        "known_duplicate_resolutions": 2,
        "incoming_baseline_profiles": sum(
            1
            for item in candidates
            if item["already_listed"] and item["decision"] == "elegível"
        ),
        "incoming_cross_epic_transfers": 0,
        "outgoing_category_resolutions": len(TRANSFER_TARGETS),
        "input_hashes": inventory["inputs"],
        "output_hashes": {name: sha256(ROOT / name) for name in core_files},
        "independent_review_status": "pending",
        "independent_reviewer": "independent-reviewer-issue-86",
        "review_count": 0,
        "unresolved_high_divergences": None,
        "drift_status": "not-yet-checked",
    }


def provisional_run_manifest() -> list[dict]:
    tasks = []
    for audit, directory in AUDITS.items():
        tasks.append(
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": RUN_ID,
                "task_id": f"task-reduce-{audit}",
                "issue": 86,
                "url": f"https://github.com/djairofilho/awesome-latam-vc/issues/{audit.removeprefix('issue-')}",
                "task_type": "revisão",
                "partition": audit,
                "shard_path": f"research/epic-63/consolidation/shards/reduce-{audit}/",
                "priority": 1,
                "status": "done",
                "owner": "consolidator-issue-86",
                "next_action": None,
                "last_error": None,
            }
        )
    tasks.extend(
        [
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": RUN_ID,
                "task_id": "task-global-identity-resolution",
                "issue": 86,
                "url": "https://github.com/djairofilho/awesome-latam-vc/issues/86",
                "task_type": "identidade",
                "partition": "global",
                "shard_path": "research/epic-63/consolidation/shards/consolidator/",
                "priority": 2,
                "status": "done",
                "owner": "consolidator-issue-86",
                "next_action": None,
                "last_error": None,
            },
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": RUN_ID,
                "task_id": "task-independent-review",
                "issue": 86,
                "url": "https://github.com/djairofilho/awesome-latam-vc/issues/86",
                "task_type": "revisão",
                "partition": "independent-review",
                "shard_path": "research/epic-63/consolidation/shards/independent-reviewer/",
                "priority": 3,
                "status": "todo",
                "owner": "independent-reviewer-issue-86",
                "next_action": "Revisar o escopo obrigatório e congelar a fila.",
                "last_error": None,
            },
        ]
    )
    run = {
        "schema_version": "1.0",
        "record_type": "run",
        "run_id": RUN_ID,
        "issues": [81, 82, 83, 84, 85, 86],
        "contract_issue": 80,
        "cutoff_date": CUTOFF,
        "created_on": CUTOFF,
        "status": "planejada",
        "task_count": len(tasks),
        "scraping_performed": False,
        "max_global_requests": 8,
        "max_requests_per_domain": 2,
        "max_browsers": 2,
        "owner": "consolidator-issue-86",
        "notes": "Redução sem scraping novo; freeze depende de revisão independente.",
    }
    return [run, *tasks]


def main() -> None:
    inventory = verify_input_inventory()
    raw_candidates, candidate_provenance = merge_records("candidates.jsonl")
    evidence, _ = merge_records("evidence.jsonl")
    sources, _ = merge_records("source-inventory.jsonl")
    coverage, _ = merge_records("coverage-matrix.jsonl")
    candidates, queue, provenance = consolidate_candidates(
        raw_candidates,
        candidate_provenance,
    )
    dump_jsonl(ROOT / "candidates.jsonl", candidates, "network_id")
    dump_jsonl(ROOT / "evidence.jsonl", evidence, "evidence_id")
    dump_jsonl(ROOT / "source-inventory.jsonl", sources, "source_id")
    dump_jsonl(ROOT / "coverage-matrix.jsonl", coverage, "coverage_id")
    dump_jsonl(ROOT / "publication-queue.jsonl", queue, "queue_id")
    dump_jsonl(ROOT / "provenance.jsonl", provenance, "network_id")
    dump_json(ROOT / "identity-resolutions.json", identity_resolutions())
    dump_json(ROOT / "category-resolutions.json", category_resolutions(candidates))
    dump_json(
        ROOT / "consolidation-manifest.json",
        provisional_manifest(
            inventory,
            candidates,
            evidence,
            sources,
            coverage,
            queue,
        ),
    )
    dump_ordered_jsonl(
        ROOT / "run-manifest.jsonl",
        provisional_run_manifest(),
    )


if __name__ == "__main__":
    main()
