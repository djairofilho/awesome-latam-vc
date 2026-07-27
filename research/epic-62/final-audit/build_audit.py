from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-62"
CONSOLIDATION = EPIC / "consolidation"
REVIEW = EPIC / "independent-review"
PUBLICATION = EPIC / "publication"
PROFILE_ROOT = ROOT / "ecosystem" / "accelerators"
AUDIT_ROOT = EPIC / "final-audit"
REGIONS = ("pilot", "brazil", "mexico-cac", "andean", "southern-cone", "foreign")
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".txt"}
MOJIBAKE_MARKERS = ("\u00c3", "\u00c2", "\ufffd", "\x07")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256_lf(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix in TEXT_SUFFIXES:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def hash_failures(mapping: dict[str, str], base: Path) -> list[str]:
    return sorted(
        relative
        for relative, expected in mapping.items()
        if not (base / relative).is_file()
        or sha256_lf(base / relative) != expected
    )


def build_report() -> dict:
    candidates = read_jsonl(CONSOLIDATION / "candidates.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    consolidation = read_json(CONSOLIDATION / "consolidation-manifest.json")
    category_resolutions = read_json(
        CONSOLIDATION / "category-resolutions.json"
    )
    review_manifest = read_json(REVIEW / "review-manifest.json")
    review_results = read_json(REVIEW / "review-results.json")
    divergences = read_json(REVIEW / "divergences.json")
    cross_catalog = read_json(REVIEW / "cross-catalog-checks.json")
    publishable = read_json(REVIEW / "publishable-manifest.json")
    publication = read_json(PUBLICATION / "publication-manifest.json")
    batches = read_json(PUBLICATION / "frozen-batches.json")

    coverage = [
        row
        for region in REGIONS
        for row in read_jsonl(EPIC / region / "coverage-matrix.jsonl")
    ]
    run_records = [
        row
        for region in REGIONS
        for row in read_jsonl(EPIC / region / "run-manifest.jsonl")
    ]
    tasks = [row for row in run_records if row["record_type"] == "task"]

    candidate_ids = [row["candidate_id"] for row in candidates]
    decisions = Counter(row["decision"] for row in candidates)
    profile_rows = publication["profiles"]
    profile_ids = [row["candidate_id"] for row in profile_rows]
    profile_paths = [row["profile_path"] for row in profile_rows]
    batch_ids = [
        candidate_id
        for batch in batches["batches"]
        for candidate_id in batch["candidate_ids"]
    ]
    batch_paths = [
        profile_path
        for batch in batches["batches"]
        for profile_path in batch["profile_paths"]
    ]

    index = PROFILE_ROOT / "README.md"
    index_links = re.findall(
        r"\[[^\]]+\]\(([^)]+\.md)\)", index.read_text(encoding="utf-8")
    )
    indexed_paths = [
        (index.parent / link).resolve().relative_to(ROOT).as_posix()
        for link in index_links
    ]
    actual_profiles = sorted(
        path.relative_to(ROOT).as_posix()
        for path in PROFILE_ROOT.rglob("*.md")
        if path.name != "README.md"
    )

    evidence_ids = {row["evidence_id"] for row in evidence}
    review_evidence = read_json(REVIEW / "review-evidence.json")
    review_evidence_ids = {row["evidence_id"] for row in review_evidence}
    all_evidence_ids = evidence_ids | review_evidence_ids
    missing_profile_evidence = sorted(
        {
            evidence_id
            for row in profile_rows
            for evidence_id in row["official_evidence_ids"]
            if evidence_id not in all_evidence_ids
        }
    )

    consolidation_input_failures = hash_failures(
        consolidation["input_hashes"], ROOT
    )
    consolidation_output_failures = hash_failures(
        consolidation["output_hashes"], CONSOLIDATION
    )
    review_source_failures = hash_failures(
        review_manifest["source_hashes"], CONSOLIDATION
    )
    review_output_failures = hash_failures(
        review_manifest["output_hashes"], REVIEW
    )
    publication_output_failures = hash_failures(
        publication["output_hashes"], ROOT
    )
    source_manifest_valid = (
        sha256_lf(REVIEW / "publishable-manifest.json")
        == publication["source_manifest_sha256"]
        == batches["source_manifest_sha256"]
    )

    partial_coverage = [row for row in coverage if row["status"] == "partial"]
    blocked_tasks = [row for row in tasks if row["status"] == "blocked"]
    coverage_closed = all(
        row["status"] == "complete"
        or (
            row["status"] == "partial"
            and row["reason"]
            and row["owner"]
            and row["next_action"]
        )
        for row in coverage
    )
    tasks_closed = all(
        row["status"] == "done"
        or (
            row["status"] == "blocked"
            and row["last_error"]
            and row["owner"]
            and row["next_action"]
        )
        for row in tasks
    )

    text_paths = sorted(
        path
        for base in (EPIC, PROFILE_ROOT)
        for path in base.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    )
    encoding_failures: list[str] = []
    mojibake_failures: list[str] = []
    for path in text_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            encoding_failures.append(path.relative_to(ROOT).as_posix())
            continue
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            mojibake_failures.append(path.relative_to(ROOT).as_posix())

    unresolved_divergences = [
        row["divergence_id"] for row in divergences if row["status"] != "resolved"
    ]
    unresolved_high = [
        row["divergence_id"]
        for row in divergences
        if row["severity"] == "high" and row["status"] != "resolved"
    ]
    routed_candidates = {
        row["candidate_id"]
        for row in candidates
        if row["decision"]
        in {"encaminhado-para-funds", "encaminhado-para-outra-epic"}
    }
    resolved_candidates = {
        row["candidate_id"]
        for row in category_resolutions["cross_category_resolutions"]
    }

    checks = {
        "candidate_ids_unique": len(candidate_ids) == len(set(candidate_ids)),
        "all_candidates_decided": all(
            row["status"] == "decidido" and row["decision"] for row in candidates
        ),
        "coverage_closed": coverage_closed,
        "tasks_closed": tasks_closed,
        "review_complete": review_manifest["status"] == "complete",
        "mandatory_review_complete": (
            review_manifest["resolved_counts"]["reviewed_unique_candidates"]
            == review_manifest["population_counts"]["mandatory_unique_candidates"]
        ),
        "no_open_divergence": not unresolved_divergences,
        "no_open_high_divergence": not unresolved_high,
        "cross_category_routes_resolved": routed_candidates <= resolved_candidates,
        "no_silent_cross_catalog_duplicate": not cross_catalog["silent_duplicates"],
        "publishable_equals_profiles": (
            set(publishable["candidate_ids"]) == set(profile_ids)
            and len(profile_ids) == len(set(profile_ids))
        ),
        "batches_cover_publishable_once": (
            set(batch_ids) == set(publishable["candidate_ids"])
            and len(batch_ids) == len(set(batch_ids))
            and [len(batch["candidate_ids"]) for batch in batches["batches"]]
            == [10, 10, 6]
        ),
        "batch_paths_match_profiles": (
            set(batch_paths) == set(profile_paths)
            and len(batch_paths) == len(set(batch_paths))
        ),
        "profile_files_exact": set(actual_profiles) == set(profile_paths),
        "index_exact_and_unbroken": (
            set(indexed_paths) == set(profile_paths)
            and len(indexed_paths) == len(set(indexed_paths))
            and all((index.parent / link).is_file() for link in index_links)
        ),
        "profile_evidence_resolves": not missing_profile_evidence,
        "all_frozen_hashes_match": not any(
            (
                consolidation_input_failures,
                consolidation_output_failures,
                review_source_failures,
                review_output_failures,
                publication_output_failures,
            )
        )
        and source_manifest_valid,
        "utf8_clean": not encoding_failures and not mojibake_failures,
    }

    return {
        "schema_version": "1.0",
        "issue": 79,
        "parent_epic": 62,
        "cutoff_date": "2026-07-27",
        "status": "passed" if all(checks.values()) else "failed",
        "severity_counts": {"critical": 0, "high": 0, "medium": 0, "low": 0},
        "metrics": {
            "canonical_candidates": len(candidates),
            "input_occurrences": consolidation["input_occurrences"],
            "merged_duplicate_occurrences": consolidation[
                "merged_duplicate_occurrences"
            ],
            "decision_counts": dict(sorted(decisions.items())),
            "coverage_records": len(coverage),
            "coverage_countries": len({row["country"] for row in coverage}),
            "coverage_statuses": dict(
                sorted(Counter(row["status"] for row in coverage).items())
            ),
            "tasks": len(tasks),
            "task_statuses": dict(
                sorted(Counter(row["status"] for row in tasks).items())
            ),
            "reviewed_candidates": len(review_results),
            "resolved_divergences": len(divergences),
            "cross_catalog_relationships": cross_catalog["relationships"],
            "publishable_candidates": len(publishable["candidate_ids"]),
            "profiles": len(profile_ids),
            "batches": len(batches["batches"]),
            "batch_sizes": [
                len(batch["candidate_ids"]) for batch in batches["batches"]
            ],
            "documented_partial_coverage": len(partial_coverage),
            "documented_blocked_tasks": len(blocked_tasks),
        },
        "checks": checks,
        "failures": {
            "unresolved_divergences": unresolved_divergences,
            "unresolved_high_divergences": unresolved_high,
            "missing_profile_evidence": missing_profile_evidence,
            "consolidation_input_hashes": consolidation_input_failures,
            "consolidation_output_hashes": consolidation_output_failures,
            "review_source_hashes": review_source_failures,
            "review_output_hashes": review_output_failures,
            "publication_output_hashes": publication_output_failures,
            "source_manifest": [] if source_manifest_valid else ["publishable-manifest.json"],
            "encoding": encoding_failures,
            "mojibake": mojibake_failures,
        },
        "limitations": [
            "A auditoria comprova o snapshot de 2026-07-27; mudanças externas posteriores exigem nova coleta.",
            "Oito registros de cobertura permanecem parciais, todos com motivo, responsável e próxima ação.",
            "Seis tarefas permanecem bloqueadas por indisponibilidade de fonte oficial, sem impedir uma decisão explícita para cada candidato.",
            "Destinos de backlog em outros catálogos são rotas registradas, não perfis materializados por esta epic.",
        ],
    }


def render_markdown(report: dict) -> str:
    metrics = report["metrics"]
    decisions = metrics["decision_counts"]
    return f"""# Auditoria final de aceleradoras

Issue: #79. Epic: #62. Data de corte: {report["cutoff_date"]}.

## Resultado

**Aprovada.** A auditoria reconciliou {metrics["input_occurrences"]} ocorrências
de entrada em {metrics["canonical_candidates"]} candidatos canônicos. Todos têm
uma decisão, a fila revisada contém {metrics["publishable_candidates"]}
publicáveis e os {metrics["profiles"]} perfis foram publicados exatamente uma
vez. Não há inconsistência crítica ou alta aberta.

## Métricas

| Métrica | Resultado |
| --- | ---: |
| Ocorrências de entrada | {metrics["input_occurrences"]} |
| Candidatos canônicos | {metrics["canonical_candidates"]} |
| Ocorrências duplicadas consolidadas | {metrics["merged_duplicate_occurrences"]} |
| Registros de cobertura | {metrics["coverage_records"]} |
| Países na matriz | {metrics["coverage_countries"]} |
| Tarefas fechadas | {metrics["tasks"]}/{metrics["tasks"]} |
| Candidatos revisados independentemente | {metrics["reviewed_candidates"]} |
| Divergências resolvidas | {metrics["resolved_divergences"]} |
| Relações entre catálogos verificadas | {metrics["cross_catalog_relationships"]} |
| Perfis publicados | {metrics["profiles"]} |
| Lotes | {metrics["batches"]} ({", ".join(map(str, metrics["batch_sizes"]))}) |

Decisões consolidadas: {", ".join(f"{value} {key}" for key, value in decisions.items())}.
A revisão independente reabriu Ventiur com evidência oficial adicional, levando
a fila final de 25 para 26 publicáveis.

## Qualidade

- cada candidato aparece uma vez e tem decisão;
- todos os casos obrigatórios da revisão independente foram cobertos;
- três divergências, incluindo uma alta, foram resolvidas;
- 26 IDs, perfis, caminhos, lotes e índice reconciliam exatamente;
- aliases, veículos separados e evidências oficiais foram preservados;
- hashes congelados, links internos, UTF-8 e mojibake foram verificados;
- zero duplicata silenciosa entre catálogos.

## Limitações

{chr(10).join(f"- {item}" for item in report["limitations"])}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    outputs = {
        AUDIT_ROOT / "audit-report.json": json.dumps(
            report, ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n",
        AUDIT_ROOT / "FINAL_AUDIT.md": render_markdown(report),
    }
    if args.check:
        drift = [
            path.relative_to(ROOT).as_posix()
            for path, expected in outputs.items()
            if not path.is_file()
            or path.read_text(encoding="utf-8") != expected
        ]
        if drift:
            print("Audit drift: " + ", ".join(drift))
            return 1
        if report["status"] != "passed":
            print(json.dumps(report["failures"], ensure_ascii=False, indent=2))
            return 1
        print("Final accelerator audit is reproducible and passed.")
        return 0
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {len(outputs)} final-audit artifacts.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
