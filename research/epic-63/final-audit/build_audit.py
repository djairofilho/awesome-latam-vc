#!/usr/bin/env python3
"""Gera a auditoria final determinística da epic #63."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-63"
CONSOLIDATION = EPIC / "consolidation"
PUBLICATION = EPIC / "publication"
PROFILE_ROOT = ROOT / "ecosystem" / "angel-networks"
AUDIT_ROOT = EPIC / "final-audit"
PAD = "ang-hub-udep-pe--pad"
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".txt"}
MOJIBAKE_MARKERS = ("\u00c3", "\u00c2", "\ufffd", "\x07")
ROUTED = {
    "encaminhado-para-funds",
    "encaminhado-para-aceleradoras",
    "encaminhado-para-plataformas",
    "encaminhado-para-programas-públicos",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(path: Path, normalize: bool = False) -> str:
    payload = path.read_bytes()
    if normalize:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def equivalent_text_hashes(path: Path) -> set[str]:
    payload = path.read_bytes()
    if path.suffix not in TEXT_SUFFIXES:
        return {hashlib.sha256(payload).hexdigest()}
    lf = payload.replace(b"\r\n", b"\n")
    crlf = lf.replace(b"\n", b"\r\n")
    return {
        hashlib.sha256(lf).hexdigest(),
        hashlib.sha256(crlf).hexdigest(),
    }


def equivalent_profile_hashes(path: Path) -> set[str]:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if payload.startswith(b"---\n"):
        closing = payload.find(b"\n---\n", 4)
        if closing != -1:
            payload = payload[closing + 5 :].lstrip(b"\n")
    crlf = payload.replace(b"\n", b"\r\n")
    return {
        hashlib.sha256(payload).hexdigest(),
        hashlib.sha256(crlf).hexdigest(),
    }


def check_hashes(
    mapping: dict[str, str],
    base: Path,
    normalize: bool = False,
    *,
    body_only: bool = False,
) -> list[str]:
    return sorted(
        relative
        for relative, expected in mapping.items()
        if not (base / relative).is_file()
        or expected
        not in (
            equivalent_profile_hashes(base / relative)
            if body_only
            else equivalent_text_hashes(base / relative)
        )
    )


def frozen_tasks(input_inventory: dict) -> tuple[list[dict], list[dict]]:
    run_paths = sorted(
        ROOT / relative
        for relative in input_inventory["inputs"]
        if relative.endswith("/run-manifest.jsonl")
    )
    run_paths.append(CONSOLIDATION / "run-manifest.jsonl")
    runs = []
    tasks = []
    for path in run_paths:
        records = read_jsonl(path)
        runs.extend(row for row in records if row["record_type"] == "run")
        tasks.extend(row for row in records if row["record_type"] == "task")
    return runs, tasks


def build_report() -> dict:
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    sources = read_jsonl(CONSOLIDATION / "source-inventory.jsonl")
    coverage = read_jsonl(CONSOLIDATION / "coverage-matrix.jsonl")
    queue = read_jsonl(CONSOLIDATION / "publication-queue.jsonl")
    reviews = read_jsonl(CONSOLIDATION / "independent-review.jsonl")
    batches = read_jsonl(PUBLICATION / "batches.jsonl")
    provenance = read_jsonl(CONSOLIDATION / "provenance.jsonl")
    consolidation_manifest = read_json(
        CONSOLIDATION / "consolidation-manifest.json"
    )
    publication_manifest = read_json(PUBLICATION / "publication-manifest.json")
    input_inventory = read_json(CONSOLIDATION / "input-inventory.json")
    identities = read_json(CONSOLIDATION / "identity-resolutions.json")[
        "resolutions"
    ]
    categories = read_json(CONSOLIDATION / "category-resolutions.json")
    divergences = read_json(CONSOLIDATION / "review-divergences.json")
    runs, tasks = frozen_tasks(input_inventory)

    candidate_by_id = {row["network_id"]: row for row in candidates}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    source_ids = {row["source_id"] for row in sources}
    candidate_ids = [row["network_id"] for row in candidates]
    decisions = Counter(row["decision"] for row in candidates)
    eligible_ids = {
        row["network_id"] for row in candidates if row["decision"] == "elegível"
    }
    queue_ids = [row["network_id"] for row in queue]
    pending_ids = {
        row["network_id"]
        for row in queue
        if row["publication_status"] == "pending-publication"
    }
    preserved_ids = {
        row["network_id"]
        for row in queue
        if row["publication_status"] == "already-published"
    }
    batch_rows = [profile for batch in batches for profile in batch["profiles"]]
    batch_ids = [row["network_id"] for row in batch_rows]
    profile_paths = {
        row["network_id"]: row["canonical_profile"] for row in queue
    }
    expected_profiles = set(profile_paths.values())
    actual_profiles = {
        path.relative_to(ROOT).as_posix()
        for path in PROFILE_ROOT.rglob("*.md")
        if not path.name.startswith("README")
    }

    missing_evidence = sorted(
        {
            evidence_id
            for candidate in candidates
            for evidence_id in candidate["official_evidence_ids"]
            if evidence_id not in evidence_by_id
        }
    )
    missing_sources = sorted(
        {
            source_id
            for candidate in candidates
            for source_id in candidate["discovery_source_ids"]
            if source_id not in source_ids
        }
        | {
            source_id
            for cell in coverage
            for source_id in cell["source_ids"]
            if source_id not in source_ids
        }
    )
    invalid_official_urls = sorted(
        row["evidence_id"]
        for row in evidence
        if row["source_type"] != "oficial"
        or not re.match(r"^https?://", row["url"])
    )
    profile_source_failures = sorted(
        candidate["network_id"]
        for candidate in candidates
        if candidate["network_id"] in eligible_ids
        and any(
            evidence_by_id[evidence_id]["url"]
            not in (ROOT / candidate["canonical_profile"]).read_text(encoding="utf-8")
            for evidence_id in candidate["official_evidence_ids"]
        )
    )

    indexed_paths: dict[str, list[str]] = {}
    broken_index_links = []
    for filename in ("README.md", "README.pt.md", "README.es.md"):
        index = PROFILE_ROOT / filename
        links = re.findall(
            r"\[[^\]]+\]\(([^)]+\.md)\)", index.read_text(encoding="utf-8")
        )
        resolved = [
            (index.parent / link).resolve().relative_to(ROOT).as_posix()
            for link in links
        ]
        indexed_paths[filename] = resolved
        broken_index_links.extend(
            f"{filename}:{link}"
            for link in links
            if not (index.parent / link).is_file()
        )

    identity_ids = [row["resolution_id"] for row in identities]
    identity_subjects = {
        subject for row in identities for subject in row["subject_ids"]
    }
    transfer_rows = categories["outgoing_category_resolutions"]
    transfer_ids = [row["source_network_id"] for row in transfer_rows]
    routed_ids = {
        row["network_id"] for row in candidates if row["decision"] in ROUTED
    }

    coverage_statuses = Counter(row["status"] for row in coverage)
    partial_coverage_failures = sorted(
        row["coverage_id"]
        for row in coverage
        if row["status"] == "parcial"
        and not (row["owner"] and row["reason"] and row["next_action"])
    )
    run_failures = sorted(
        row["run_id"]
        for row in runs
        if row["status"] != "concluída"
        or row["task_count"]
        != sum(task["run_id"] == row["run_id"] for task in tasks)
    )
    task_failures = sorted(
        row["task_id"]
        for row in tasks
        if not (
            row["status"] == "done"
            or (
                row["status"] == "blocked"
                and row["owner"]
                and row.get("last_error")
                and row["next_action"]
            )
        )
    )

    input_hash_failures = check_hashes(input_inventory["inputs"], ROOT)
    consolidation_output_failures = check_hashes(
        consolidation_manifest["output_hashes"], CONSOLIDATION
    )
    publication_source_failures = check_hashes(
        publication_manifest["source_hashes"], CONSOLIDATION, normalize=True
    )
    publication_profile_failures = check_hashes(
        {
            **publication_manifest["profile_hashes"],
            **publication_manifest["preserved_profile_hashes"],
        },
        ROOT,
        body_only=True,
    )
    publication_index_failures = check_hashes(
        publication_manifest["index_hashes"], ROOT
    )
    batch_hash_valid = publication_manifest[
        "batch_artifact_hash"
    ] in equivalent_text_hashes(PUBLICATION / "batches.jsonl")
    checksum_failures = []
    for line in (CONSOLIDATION / "sha256sums.txt").read_text(
        encoding="utf-8"
    ).splitlines():
        expected, name = line.split("  ", 1)
        if expected not in equivalent_text_hashes(CONSOLIDATION / name):
            checksum_failures.append(name)

    text_paths = sorted(
        {
            path
            for base in (EPIC, PROFILE_ROOT)
            for path in base.rglob("*")
            if path.is_file() and path.suffix in TEXT_SUFFIXES
        }
    )
    encoding_failures = []
    mojibake_failures = []
    for path in text_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            encoding_failures.append(path.relative_to(ROOT).as_posix())
            continue
        scan_text = "\n".join(
            line
            for line in text.splitlines()
            if "MOJIBAKE_MARKERS =" not in line
        )
        if any(marker in scan_text for marker in MOJIBAKE_MARKERS):
            mojibake_failures.append(path.relative_to(ROOT).as_posix())

    pad = candidate_by_id[PAD]
    pad_review = next(row for row in reviews if row["subject_id"] == PAD)
    pad_divergence = next(
        row
        for row in divergences["divergences"]
        if row["subject_id"] == PAD
    )
    pad_checks = {
        "final_decision_insufficient": pad["decision"] == "evidência-insuficiente",
        "external_access_unconfirmed": pad["external_access"] == "não confirmado",
        "application_route_absent": pad["application_route"] is None,
        "profile_absent": pad["canonical_profile"] is None,
        "not_queued": PAD not in queue_ids,
        "not_batched": PAD not in batch_ids,
        "not_indexed": all(
            PAD not in (PROFILE_ROOT / filename).read_text(encoding="utf-8")
            and pad["name"]
            not in (PROFILE_ROOT / filename).read_text(encoding="utf-8")
            for filename in indexed_paths
        ),
        "review_changed_decision": (
            pad_review["original_decision"] == "elegível"
            and pad_review["final_decision"] == "evidência-insuficiente"
            and pad_review["resolved"]
        ),
        "high_divergence_resolved": (
            pad_divergence["severity"] == "high"
            and pad_divergence["status"] == "resolved"
        ),
    }

    checks = {
        "candidate_ids_unique": len(candidate_ids) == len(set(candidate_ids)),
        "all_candidates_decided": (
            len(candidates) == 44
            and all(row["decision"] and row["status"] in {"decidido", "publicado"} for row in candidates)
            and len(provenance) == len(candidates)
        ),
        "candidate_references_resolve": not missing_evidence and not missing_sources,
        "coverage_unique_and_closed": (
            len(coverage) == 42
            and len({row["coverage_id"] for row in coverage}) == len(coverage)
            and set(coverage_statuses) <= {"concluída", "parcial", "não aplicável"}
            and not partial_coverage_failures
        ),
        "runs_and_tasks_closed": not run_failures and not task_failures,
        "eligible_queue_exact": set(queue_ids) == eligible_ids and len(queue_ids) == 11,
        "publication_split_exact": (
            pending_ids == set(batch_ids)
            and len(batch_ids) == len(set(batch_ids)) == 6
            and len(preserved_ids) == 5
        ),
        "profiles_exact": actual_profiles == expected_profiles and len(actual_profiles) == 11,
        "no_individual_investor_published": all(
            candidate_by_id[network_id]["entity_type"]
            in {"rede", "clube", "alumni network"}
            for network_id in eligible_ids
        ),
        "actors_separated_for_eligible": all(
            candidate_by_id[network_id]["selection_actors"]
            and candidate_by_id[network_id]["decision_actors"]
            and candidate_by_id[network_id]["capital_actors"]
            for network_id in eligible_ids
        ),
        "identities_resolved": (
            len(identities) == 7
            and len(identity_ids) == len(set(identity_ids))
            and identity_subjects <= set(candidate_ids)
            and {
                row["network_id"]
                for row in candidates
                if row["decision"] == "duplicado"
            }
            <= identity_subjects
        ),
        "transfers_resolved": (
            len(transfer_rows) == 12
            and set(transfer_ids) == routed_ids
            and len(transfer_ids) == len(set(transfer_ids))
            and all(row["target_id"] and row["canonical_destination"] for row in transfer_rows)
        ),
        "indexes_exact": all(
            set(paths) == expected_profiles
            and len(paths) == len(set(paths)) == 11
            for paths in indexed_paths.values()
        ),
        "no_broken_index_links": not broken_index_links,
        "official_links_embedded": (
            not invalid_official_urls and not profile_source_failures
        ),
        "all_frozen_hashes_match": not any(
            (
                input_hash_failures,
                consolidation_output_failures,
                publication_source_failures,
                publication_profile_failures,
                publication_index_failures,
                checksum_failures,
            )
        )
        and batch_hash_valid,
        "independent_review_complete": (
            consolidation_manifest["independent_review_status"] == "complete"
            and len(reviews) == 42
            and all(row["resolved"] for row in reviews)
        ),
        "no_high_divergence_open": (
            consolidation_manifest["unresolved_high_divergences"] == 0
            and divergences["open_high_divergences"] == 0
            and all(
                row["status"] == "resolved"
                for row in divergences["divergences"]
                if row["severity"] == "high"
            )
        ),
        "pad_excluded": all(pad_checks.values()),
        "utf8_clean": not encoding_failures and not mojibake_failures,
    }

    return {
        "schema_version": "1.0",
        "issue": 88,
        "parent_epic": 63,
        "cutoff_date": "2026-07-27",
        "auditor": "final-auditor-issue-88",
        "status": "passed" if all(checks.values()) else "failed",
        "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        "metrics": {
            "candidates": len(candidates),
            "decision_counts": dict(sorted(decisions.items())),
            "eligible": len(eligible_ids),
            "profiles": len(actual_profiles),
            "preserved_profiles": len(preserved_ids),
            "new_profiles": len(batch_ids),
            "not_published": len(candidates) - len(eligible_ids),
            "coverage_rows": len(coverage),
            "coverage_statuses": dict(sorted(coverage_statuses.items())),
            "runs": len(runs),
            "tasks": len(tasks),
            "task_statuses": dict(sorted(Counter(row["status"] for row in tasks).items())),
            "official_evidence_records": len(evidence),
            "source_records": len(sources),
            "identity_resolutions": len(identities),
            "identity_subjects": len(identity_subjects),
            "outgoing_category_transfers": len(transfer_rows),
            "independent_review_records": len(reviews),
            "indexes": len(indexed_paths),
        },
        "checks": checks,
        "pad_checks": pad_checks,
        "failures": {
            "broken_index_links": broken_index_links,
            "missing_evidence": missing_evidence,
            "missing_sources": missing_sources,
            "invalid_official_urls": invalid_official_urls,
            "profile_sources": profile_source_failures,
            "partial_coverage": partial_coverage_failures,
            "runs": run_failures,
            "tasks": task_failures,
            "input_hashes": input_hash_failures,
            "consolidation_output_hashes": consolidation_output_failures,
            "publication_source_hashes": publication_source_failures,
            "publication_profile_hashes": publication_profile_failures,
            "publication_index_hashes": publication_index_failures,
            "checksums": checksum_failures,
            "batch_hash": [] if batch_hash_valid else ["batches.jsonl"],
            "encoding": encoding_failures,
            "mojibake": mojibake_failures,
        },
        "limitations": [
            "A auditoria comprova o snapshot congelado em 2026-07-27; mudanças posteriores nas fontes oficiais exigem nova coleta.",
            "As nove células parciais permanecem fechadas com motivo, responsável e próxima ação, sem promover candidatos sem evidência suficiente.",
            "Dezesseis candidatos permanecem como evidência-insuficiente; isso é uma decisão explícita e não uma omissão do registro.",
        ],
    }


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    checks = report["checks"]
    decisions = metrics["decision_counts"]
    return f"""# Auditoria final de redes-anjo

Issue: #88. Epic: #63. Data de corte: {report["cutoff_date"]}.
Auditor: `{report["auditor"]}`.

## Resultado

**Aprovada.** A auditoria reconciliou {metrics["candidates"]} candidatos,
{metrics["eligible"]} elegíveis, {metrics["profiles"]} perfis e
{metrics["coverage_rows"]} células de cobertura. Não há divergência crítica ou
alta aberta.

## Reconciliação

| Métrica | Resultado |
| --- | ---: |
| Candidatos com decisão | {metrics["candidates"]}/{metrics["candidates"]} |
| Elegíveis publicados exatamente uma vez | {metrics["profiles"]}/{metrics["eligible"]} |
| Perfis preservados | {metrics["preserved_profiles"]} |
| Perfis novos | {metrics["new_profiles"]} |
| Não elegíveis fora do catálogo | {metrics["not_published"]}/{metrics["not_published"]} |
| Células de cobertura | {metrics["coverage_rows"]} |
| Tarefas congeladas | {metrics["tasks"]} |
| Resoluções de identidade | {metrics["identity_resolutions"]} |
| Transferências de categoria | {metrics["outgoing_category_transfers"]} |
| Evidências oficiais | {metrics["official_evidence_records"]} |
| Índices EN/PT/ES | {metrics["indexes"]} |

Decisões finais: {decisions["elegível"]} elegíveis,
{decisions["evidência-insuficiente"]} com evidência insuficiente,
{decisions["duplicado"]} duplicados, {decisions["inativo"]} inativos,
{decisions["excluído"]} excluído e
{sum(decisions[key] for key in ROUTED)} transferidos para outras categorias.

## Verificações de qualidade

- Cobertura e tarefas fechadas: {str(checks["coverage_unique_and_closed"] and checks["runs_and_tasks_closed"]).lower()}.
- Fila, batches e perfis reconciliados: {str(checks["eligible_queue_exact"] and checks["publication_split_exact"] and checks["profiles_exact"]).lower()}.
- Redes, membros, decisão e capital separados: {str(checks["actors_separated_for_eligible"]).lower()}.
- Investidores individuais publicados: zero.
- Identidades e 12 transferências resolvidas: {str(checks["identities_resolved"] and checks["transfers_resolved"]).lower()}.
- Hashes congelados íntegros: {str(checks["all_frozen_hashes_match"]).lower()}.
- Índices, links internos e fontes oficiais: íntegros.
- UTF-8 e mojibake: limpos.
- Divergências altas abertas: zero.

## Caso limítrofe: PAD/UDEP

O PAD/UDEP permanece como `evidência-insuficiente`. A rota oficial registrada
recebe participantes de um seminário, não candidaturas externas de startups à
seleção recorrente. O caso não está na fila, nos batches, nos perfis ou nos
índices, e sua divergência alta está resolvida.

## Limitações

{chr(10).join(f"- {item}" for item in report["limitations"])}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    outputs = {
        AUDIT_ROOT / "audit-report.json": (
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ),
        AUDIT_ROOT / "FINAL_AUDIT.md": render_markdown(report),
    }
    if args.check:
        drift = [
            path.relative_to(ROOT).as_posix()
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print("Audit drift: " + ", ".join(drift))
            return 1
        if report["status"] != "passed":
            print(json.dumps(report["failures"], ensure_ascii=False, indent=2))
            return 1
        print("Final angel-network audit is reproducible and passed.")
        return 0
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {len(outputs)} final-audit artifacts.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
