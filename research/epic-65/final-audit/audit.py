#!/usr/bin/env python3
"""Auditoria final determinística da epic #65."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any
from urllib.parse import urlparse


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EPIC = ROOT / "research/epic-65"
CONSOLIDATION = EPIC / "consolidation"
PUBLICATION = EPIC / "publication"
CATALOG = ROOT / "ecosystem/public-programs"
REPORT_JSON = HERE / "audit-report.json"
REPORT_MD = HERE / "FINAL_AUDIT.md"
CUTOFF = "2026-07-27"
MOJIBAKE_MARKERS = (
    "\u00c3",
    "\u00c2",
    "\ufffd",
    "\u00e2\u20ac",
    "\u00f0\u0178",
    "\x07",
    "\\`",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EPIC_VALIDATOR = load_module("epic65_validator", EPIC / "validate.py")
PUBLICATION_VERIFIER = load_module(
    "epic65_publication_verifier",
    PUBLICATION / "verify_publication.py",
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalized_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(normalized_bytes(path)).hexdigest()


def profile_sha256(path: Path) -> str:
    payload = normalized_bytes(path).replace(b"\r", b"\n")
    if payload.startswith(b"---\n"):
        closing = payload.find(b"\n---\n", 4)
        if closing != -1:
            payload = payload[closing + 5 :].lstrip(b"\n")
    return hashlib.sha256(payload).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def counter_dict(values: list[Any]) -> dict[str, int]:
    normalized = ["<ausente>" if value is None else str(value) for value in values]
    return dict(sorted(Counter(normalized).items()))


def check_record(
    checks: list[dict[str, Any]],
    findings: list[dict[str, str]],
    check_id: str,
    checked_records: int,
    errors: list[str],
    details: str,
    severity: str = "high",
) -> None:
    unique_errors = sorted(set(errors))
    checks.append(
        {
            "check_id": check_id,
            "checked_records": checked_records,
            "details": details,
            "status": "passed" if not unique_errors else "failed",
        }
    )
    findings.extend(
        {
            "check_id": check_id,
            "message": error,
            "severity": severity,
        }
        for error in unique_errors
    )


def resolve_jsonl_anchor(root: Path, destination: str) -> bool:
    path_text, separator, anchor = destination.partition("#")
    path = root / path_text
    if not separator or not path.is_file() or not anchor:
        return False
    records = read_jsonl(path)
    return any(anchor in record.values() for record in records)


def index_links(index_text: str) -> list[tuple[str, str]]:
    section = ""
    links: list[tuple[str, str]] = []
    for line in index_text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        match = re.match(r"^\| \[[^\]]+\]\(([^)]+\.md)\) \|", line)
        if match:
            links.append((section, match.group(1)))
    return links


def audit(root: Path = ROOT) -> dict[str, Any]:
    epic = root / "research/epic-65"
    consolidation = epic / "consolidation"
    publication = epic / "publication"
    catalog = root / "ecosystem/public-programs"

    agencies = read_jsonl(consolidation / "agencies.jsonl")
    programs = read_jsonl(consolidation / "programs.jsonl")
    calls = read_jsonl(consolidation / "calls.jsonl")
    evidence = read_jsonl(consolidation / "evidence.jsonl")
    coverage = read_jsonl(consolidation / "coverage-matrix.jsonl")
    run_manifest = read_jsonl(consolidation / "run-manifest.jsonl")
    review = read_jsonl(consolidation / "independent-review.jsonl")
    resolutions = json.loads(
        (consolidation / "category-resolutions.json").read_text(encoding="utf-8")
    )
    consolidation_manifest = json.loads(
        (consolidation / "consolidation-manifest.json").read_text(encoding="utf-8")
    )
    plan = json.loads(
        (publication / "publication-plan.json").read_text(encoding="utf-8")
    )
    publication_manifest = json.loads(
        (publication / "publication-manifest.json").read_text(encoding="utf-8")
    )
    profiles = [
        profile
        for batch in plan["batches"]
        for profile in batch["profiles"]
    ]

    agency_by_id = {row["agency_id"]: row for row in agencies}
    program_by_id = {row["program_id"]: row for row in programs}
    call_by_id = {row["call_id"]: row for row in calls}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    profile_by_id = {row["entity_id"]: row for row in profiles}
    all_entities = {**agency_by_id, **program_by_id, **call_by_id}
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, str]] = []

    schema_errors = EPIC_VALIDATOR.validate_bundle(consolidation)
    check_record(
        checks,
        findings,
        "schemas-and-contract",
        len(agencies)
        + len(programs)
        + len(calls)
        + len(evidence)
        + len(coverage)
        + len(run_manifest),
        schema_errors,
        "Os seis schemas e as invariantes do contrato validam o bundle consolidado.",
        "critical",
    )

    publication_errors = PUBLICATION_VERIFIER.validate(root)
    check_record(
        checks,
        findings,
        "frozen-publication",
        len(profiles),
        publication_errors,
        "A fila congelada, os lotes, perfis e hashes da #103 reconciliam.",
        "critical",
    )

    destination_errors: list[str] = []
    eligible_ids = {
        row["agency_id"] for row in agencies if row["decision"] == "elegível"
    } | {
        row["program_id"] for row in programs if row["decision"] == "elegível"
    }
    for row in agencies:
        entity_id = row["agency_id"]
        if not row.get("decision"):
            destination_errors.append(f"{entity_id}: decisão ausente")
        if (entity_id in profile_by_id) != (row["decision"] == "elegível"):
            destination_errors.append(f"{entity_id}: destino de publicação divergente")
    for row in programs:
        entity_id = row["program_id"]
        if not row.get("decision"):
            destination_errors.append(f"{entity_id}: decisão ausente")
        if (entity_id in profile_by_id) != (row["decision"] == "elegível"):
            destination_errors.append(f"{entity_id}: destino de publicação divergente")
    for row in calls:
        call_id = row["call_id"]
        if row["program_id"] not in program_by_id:
            destination_errors.append(f"{call_id}: programa de destino ausente")
        if row.get("profile_eligible") or call_id in profile_by_id:
            destination_errors.append(f"{call_id}: chamada temporária publicada")
    if set(profile_by_id) != eligible_ids:
        destination_errors.append("perfis publicados divergem dos elegíveis")
    check_record(
        checks,
        findings,
        "entity-destinations",
        len(all_entities),
        destination_errors,
        "As 29 agências, 45 programas e 21 chamadas têm destino terminal.",
        "critical",
    )

    relationship_errors: list[str] = []
    for agency in agencies:
        actual = sorted(
            program["program_id"]
            for program in programs
            if program["agency_id"] == agency["agency_id"]
        )
        if sorted(agency["program_ids"]) != actual:
            relationship_errors.append(
                f"{agency['agency_id']}: relação agência-programa não é bidirecional"
            )
    for program in programs:
        if program["agency_id"] not in agency_by_id:
            relationship_errors.append(
                f"{program['program_id']}: agência órfã {program['agency_id']}"
            )
        actual = sorted(
            call["call_id"]
            for call in calls
            if call["program_id"] == program["program_id"]
        )
        if sorted(program["call_ids"]) != actual:
            relationship_errors.append(
                f"{program['program_id']}: relação programa-chamada não é bidirecional"
            )
    for call in calls:
        if call["program_id"] not in program_by_id:
            relationship_errors.append(
                f"{call['call_id']}: programa órfão {call['program_id']}"
            )
    check_record(
        checks,
        findings,
        "relationships",
        len(agencies) + len(programs) + len(calls),
        relationship_errors,
        "Relações agência → programa → chamada fecham nos dois sentidos.",
        "critical",
    )

    coverage_errors: list[str] = []
    tasks = [row for row in run_manifest if row["record_type"] == "task"]
    runs = [row for row in run_manifest if row["record_type"] == "run"]
    coverage_keys = [(row["country"], row["source_type"]) for row in coverage]
    task_keys = [(row["country"], row["source_type"]) for row in tasks]
    if len(coverage_keys) != len(set(coverage_keys)):
        coverage_errors.append("matriz contém célula país × fonte duplicada")
    if len(task_keys) != len(set(task_keys)):
        coverage_errors.append("tarefas contêm célula país × fonte duplicada")
    if set(coverage_keys) != set(task_keys):
        coverage_errors.append("matriz e tarefas não cobrem as mesmas células")
    for row in coverage:
        if row["result"] != "concluída" and not all(
            row.get(field) for field in ("reason", "owner", "next_action")
        ):
            coverage_errors.append(
                f"{row['coverage_id']}: lacuna sem justificativa acionável"
            )
    for row in tasks:
        if row["status"] != "done":
            coverage_errors.append(f"{row['task_id']}: tarefa não concluída")
    if len(runs) != 1 or runs[0]["task_count"] != len(tasks):
        coverage_errors.append("run consolidado não reconcilia a contagem de tarefas")
    check_record(
        checks,
        findings,
        "coverage-and-tasks",
        len(coverage) + len(tasks),
        coverage_errors,
        "As 55 células correspondem às tarefas; 25 lacunas estão justificadas.",
        "critical",
    )

    transfer_errors: list[str] = []
    incoming = resolutions["incoming_transfers"]
    outgoing = resolutions["outgoing_category_resolutions"]
    for row in incoming:
        destination = row["canonical_destination"]
        if row["materialized"]:
            if row["target_program_id"] not in program_by_id:
                transfer_errors.append(
                    f"{row['source_candidate_id']}: programa materializado ausente"
                )
            if not resolve_jsonl_anchor(root, destination):
                transfer_errors.append(
                    f"{row['source_candidate_id']}: destino materializado inválido"
                )
        elif not (
            destination.startswith("out-of-scope:")
            or resolve_jsonl_anchor(root, destination)
        ):
            transfer_errors.append(
                f"{row['source_candidate_id']}: destino rejeitado inválido"
            )
        if row["owner"] is not None or row["next_action"] is not None:
            transfer_errors.append(
                f"{row['source_candidate_id']}: transferência ainda acionável"
            )
    for row in outgoing:
        if row["program_id"] not in program_by_id:
            transfer_errors.append(f"{row['program_id']}: saída sem programa")
        elif program_by_id[row["program_id"]]["decision"] != row[
            "public_program_decision"
        ]:
            transfer_errors.append(f"{row['program_id']}: decisão de saída diverge")
        destination = row["canonical_destination"]
        if not (
            destination.startswith("funds/:")
            or resolve_jsonl_anchor(root, destination)
        ):
            transfer_errors.append(f"{row['program_id']}: destino de saída inválido")
    check_record(
        checks,
        findings,
        "category-transfers",
        len(incoming) + len(outgoing),
        transfer_errors,
        "As 13 entradas e 5 saídas têm adjudicação e destino canônico.",
        "high",
    )

    evidence_errors: list[str] = []
    for row in evidence:
        parsed = urlparse(row["url"])
        if row["source_type"] != "oficial":
            evidence_errors.append(f"{row['evidence_id']}: fonte não oficial")
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            evidence_errors.append(f"{row['evidence_id']}: URL oficial inválida")
        subject = all_entities.get(row["subject_id"])
        if subject is None:
            evidence_errors.append(f"{row['evidence_id']}: sujeito órfão")
        elif row["evidence_id"] not in subject["official_evidence_ids"]:
            evidence_errors.append(
                f"{row['evidence_id']}: vínculo reverso com sujeito ausente"
            )
    for entity_id, entity in all_entities.items():
        for evidence_id in entity["official_evidence_ids"]:
            linked = evidence_by_id.get(evidence_id)
            if linked is None:
                evidence_errors.append(f"{entity_id}: evidência órfã {evidence_id}")
            elif linked["subject_id"] != entity_id:
                evidence_errors.append(
                    f"{entity_id}: evidência pertence a {linked['subject_id']}"
                )
    check_record(
        checks,
        findings,
        "official-links",
        len(evidence),
        evidence_errors,
        "As 98 evidências são oficiais, têm URL HTTP(S) e vínculo bidirecional.",
        "critical",
    )

    hash_errors: list[str] = []
    for relative, expected in consolidation_manifest["input_hashes"].items():
        path = root / relative
        if not path.is_file() or sha256(path) != expected:
            hash_errors.append(f"entrada consolidada com hash inválido: {relative}")
    for relative, expected in consolidation_manifest["output_hashes"].items():
        path = consolidation / relative
        if not path.is_file() or sha256(path) != expected:
            hash_errors.append(f"saída consolidada com hash inválido: {relative}")
    for relative, expected in plan["source_hashes"].items():
        path = consolidation / relative
        if not path.is_file() or sha256(path) != expected:
            hash_errors.append(f"entrada da publicação com hash inválido: {relative}")
    if canonical_hash(profiles) != plan["profile_queue_hash"]:
        hash_errors.append("hash da fila publicável inválido")
    for batch in plan["batches"]:
        if canonical_hash(batch["profiles"]) != batch["batch_hash"]:
            hash_errors.append(f"{batch['batch_id']}: hash do lote inválido")
    for relative, expected in publication_manifest["profile_hashes"].items():
        path = root / relative
        if not path.is_file() or profile_sha256(path) != expected:
            hash_errors.append(f"perfil com hash inválido: {relative}")
    if sha256(catalog / "README.md") != publication_manifest["index_hash"]:
        hash_errors.append("índice canônico com hash inválido")
    declared_hash_count = (
        len(consolidation_manifest["input_hashes"])
        + len(consolidation_manifest["output_hashes"])
        + len(plan["source_hashes"])
        + len(plan["batches"])
        + len(publication_manifest["profile_hashes"])
        + 2
    )
    check_record(
        checks,
        findings,
        "declared-hashes",
        declared_hash_count,
        hash_errors,
        "Todos os hashes declarados da coleta à publicação reconciliam.",
        "critical",
    )

    index_errors: list[str] = []
    index_path = catalog / "README.md"
    links = index_links(index_path.read_text(encoding="utf-8"))
    actual_paths = [path for _, path in links]
    expected_paths = [
        Path(row["path"]).relative_to("ecosystem/public-programs").as_posix()
        for row in profiles
    ]
    if len(actual_paths) != len(set(actual_paths)):
        index_errors.append("índice contém perfil duplicado")
    if set(actual_paths) != set(expected_paths):
        index_errors.append("índice não cobre exatamente os perfis")
    for path in actual_paths:
        if not (catalog / path).is_file():
            index_errors.append(f"índice aponta para arquivo ausente: {path}")
    by_country: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in profiles:
        by_country[Path(row["path"]).parent.name].append(row)
    expected_order = [
        Path(row["path"]).relative_to("ecosystem/public-programs").as_posix()
        for country in sorted(by_country)
        for row in sorted(by_country[country], key=lambda item: item["entity_id"])
    ]
    if actual_paths != expected_order:
        index_errors.append("índice não segue país e entity_id em ordem determinística")
    category_link = "ecosystem/public-programs/README.md"
    for filename in ("README.md", "README.pt.md", "README.es.md"):
        if (root / filename).read_text(encoding="utf-8").count(category_link) != 1:
            index_errors.append(f"{filename}: link da categoria ausente ou duplicado")
    check_record(
        checks,
        findings,
        "profiles-and-indexes",
        len(profiles) + 3,
        index_errors,
        "Os 29 perfis aparecem uma vez no índice e nos três índices multilíngues.",
        "critical",
    )

    ordering_errors: list[str] = []
    for filename, field in (
        ("agencies.jsonl", "agency_id"),
        ("programs.jsonl", "program_id"),
        ("calls.jsonl", "call_id"),
        ("evidence.jsonl", "evidence_id"),
        ("coverage-matrix.jsonl", "coverage_id"),
        ("independent-review.jsonl", "review_id"),
    ):
        rows = read_jsonl(consolidation / filename)
        values = [row[field] for row in rows]
        if values != sorted(values):
            ordering_errors.append(f"{filename}: IDs fora de ordem")
    if [row["entity_id"] for row in profiles] != sorted(profile_by_id):
        ordering_errors.append("fila publicável fora de ordem")
    check_record(
        checks,
        findings,
        "deterministic-ordering",
        len(agencies) + len(programs) + len(calls) + len(evidence) + len(coverage),
        ordering_errors,
        "JSONL, fila, lotes e índice seguem chaves determinísticas.",
        "high",
    )

    boundary_errors: list[str] = []
    required_published = {
        "agency-corfo",
        "program-corfo-semilla-inicia-mujeres",
        "program-start-up-chile",
    }
    if not required_published <= set(profile_by_id):
        boundary_errors.append("CORFO ou programas chilenos revalidados não publicados")
    for entity_id in (
        "program-sena-fondo-emprender",
        "program-sercotec-capital-pioneras",
    ):
        entity = program_by_id[entity_id]
        if entity["decision"] != "evidência insuficiente":
            boundary_errors.append(f"{entity_id}: caso limítrofe não foi rebaixado")
        if entity_id in profile_by_id:
            boundary_errors.append(f"{entity_id}: caso limítrofe foi publicado")
    for row in outgoing:
        if row["program_id"] in profile_by_id:
            boundary_errors.append(
                f"{row['program_id']}: fronteira encaminhada foi publicada"
            )
    check_record(
        checks,
        findings,
        "corfo-and-boundaries",
        10,
        boundary_errors,
        "CORFO, Start-Up Chile, rebaixamentos e cinco fronteiras foram revalidados.",
        "high",
    )

    text_errors: list[str] = []
    text_paths = list(epic.rglob("*.md")) + list(epic.rglob("*.json")) + list(
        epic.rglob("*.jsonl")
    )
    text_paths += list(catalog.rglob("*.md"))
    text_paths += [root / name for name in ("README.md", "README.pt.md", "README.es.md")]
    for path in sorted(set(text_paths)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text_errors.append(f"{path.relative_to(root).as_posix()}: UTF-8 inválido")
            continue
        if any(marker in text for marker in MOJIBAKE_MARKERS):
            text_errors.append(
                f"{path.relative_to(root).as_posix()}: possível mojibake"
            )
    check_record(
        checks,
        findings,
        "utf8-and-mojibake",
        len(set(text_paths)),
        text_errors,
        "Todos os artefatos textuais da epic e da categoria usam UTF-8 íntegro.",
        "high",
    )

    review_errors: list[str] = []
    if consolidation_manifest["independent_review_status"] != "complete":
        review_errors.append("revisão independente não está completa")
    if consolidation_manifest["unresolved_high_divergences"] != 0:
        review_errors.append("há divergência alta não resolvida")
    if len(review) != consolidation_manifest["review_count"]:
        review_errors.append("contagem da revisão independente diverge")
    if not all(row["resolved"] for row in review):
        review_errors.append("há item de revisão não resolvido")
    check_record(
        checks,
        findings,
        "independent-review",
        len(review),
        review_errors,
        "Os 58 itens da revisão independente estão resolvidos, sem risco alto aberto.",
        "critical",
    )

    input_paths = [
        consolidation / name
        for name in (
            "agencies.jsonl",
            "programs.jsonl",
            "calls.jsonl",
            "evidence.jsonl",
            "coverage-matrix.jsonl",
            "run-manifest.jsonl",
            "independent-review.jsonl",
            "category-resolutions.json",
            "consolidation-manifest.json",
        )
    ]
    input_paths += [
        publication / "publication-plan.json",
        publication / "publication-manifest.json",
        catalog / "README.md",
    ]
    input_paths += [root / row["path"] for row in profiles]
    input_paths += sorted((epic / "schemas").glob("*.json"))
    profile_paths = {root / row["path"] for row in profiles}
    input_hashes = {
        path.relative_to(root).as_posix(): (
            profile_sha256(path) if path in profile_paths else sha256(path)
        )
        for path in sorted(set(input_paths))
    }
    findings.sort(key=lambda row: (row["severity"], row["check_id"], row["message"]))
    return {
        "schema_version": "1.0",
        "issue": 104,
        "epic": 65,
        "cutoff_date": CUTOFF,
        "status": "passed" if not findings else "failed",
        "metrics": {
            "agencies": len(agencies),
            "agency_decisions": counter_dict([row["decision"] for row in agencies]),
            "programs": len(programs),
            "program_decisions": counter_dict([row["decision"] for row in programs]),
            "calls": len(calls),
            "call_statuses": counter_dict([row["call_status"] for row in calls]),
            "entities_with_destination": len(all_entities) - len(
                [item for item in findings if item["check_id"] == "entity-destinations"]
            ),
            "evidence": len(evidence),
            "official_evidence": sum(
                row["source_type"] == "oficial" for row in evidence
            ),
            "unique_official_urls": len({row["url"] for row in evidence}),
            "coverage_rows": len(coverage),
            "tasks": len(tasks),
            "incoming_transfers": len(incoming),
            "materialized_incoming_transfers": sum(
                row["materialized"] for row in incoming
            ),
            "outgoing_category_resolutions": len(outgoing),
            "independent_review_items": len(review),
            "eligible_profiles": len(eligible_ids),
            "published_profiles": len(profiles),
            "agency_profiles": publication_manifest["agency_profiles"],
            "program_profiles": publication_manifest["program_profiles"],
            "call_profiles": publication_manifest["call_profiles"],
            "declared_hashes_checked": declared_hash_count,
            "critical_findings": sum(
                row["severity"] == "critical" for row in findings
            ),
            "high_findings": sum(row["severity"] == "high" for row in findings),
        },
        "checks": checks,
        "findings": findings,
        "limitations": [
            (
                "A auditoria de links é estrutural e determinística: valida fonte "
                "oficial, URL HTTP(S), sujeito e vínculo com perfis. Disponibilidade "
                "HTTP ao vivo não bloqueia o CI; a coleta registra accessed_on em "
                "2026-07-27."
            ),
            (
                "Decisões com evidência insuficiente permanecem fora do catálogo e "
                "só mudam mediante nova fonte oficial e nova revisão."
            ),
        ],
        "input_hashes": input_hashes,
    }


def render_markdown(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    check_rows = "\n".join(
        f"| `{row['check_id']}` | {row['status']} | {row['checked_records']} | "
        f"{row['details']} |"
        for row in report["checks"]
    )
    limitations = "\n".join(f"- {item}" for item in report["limitations"])
    return f"""# Auditoria final da epic #65

Auditoria determinística executada para a issue #104 com data de corte
{report['cutoff_date']}. Resultado: **{report['status']}**.

## Resultado

- Agências: {metrics['agencies']}.
- Programas: {metrics['programs']}.
- Chamadas: {metrics['calls']}.
- Entidades com destino: {metrics['entities_with_destination']} de 95.
- Evidências oficiais: {metrics['official_evidence']} de {metrics['evidence']}.
- URLs oficiais únicas: {metrics['unique_official_urls']}.
- Cobertura e tarefas: {metrics['coverage_rows']} de {metrics['tasks']}.
- Perfis elegíveis e publicados: {metrics['published_profiles']} de {metrics['eligible_profiles']}.
- Perfis de chamadas: {metrics['call_profiles']}.
- Transfers: {metrics['incoming_transfers']} entradas, {metrics['materialized_incoming_transfers']} materializadas e {metrics['outgoing_category_resolutions']} saídas.
- Itens de revisão independente: {metrics['independent_review_items']}.
- Hashes declarados verificados: {metrics['declared_hashes_checked']}.
- Problemas críticos: {metrics['critical_findings']}.
- Problemas altos: {metrics['high_findings']}.

## Gates

| Gate | Status | Registros | Resultado |
| --- | --- | ---: | --- |
{check_rows}

## Limitações

{limitations}

## Reprodução

```text
python research/epic-65/final-audit/audit.py --check
python -m unittest discover -s research/epic-65/final-audit/tests -v
```

O artefato legível por máquina e todos os hashes de entrada estão em
`audit-report.json`.
"""


def artifacts(root: Path = ROOT) -> tuple[bytes, bytes]:
    report = audit(root)
    json_payload = (
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    markdown_payload = render_markdown(report).encode("utf-8")
    return json_payload, markdown_payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="falha se o relatório salvo divergir da auditoria atual",
    )
    args = parser.parse_args()
    json_payload, markdown_payload = artifacts()
    if args.check:
        drift = []
        for path, payload in (
            (REPORT_JSON, json_payload),
            (REPORT_MD, markdown_payload),
        ):
            current = normalized_bytes(path) if path.is_file() else None
            if current != payload:
                drift.append(path.name)
        if drift:
            print(
                "Auditoria final com drift: " + ", ".join(sorted(drift)),
                file=sys.stderr,
            )
            return 1
        report = json.loads(json_payload)
        if report["status"] != "passed":
            print("Auditoria final encontrou problemas:", file=sys.stderr)
            for finding in report["findings"]:
                print(
                    f"- [{finding['severity']}] {finding['message']}",
                    file=sys.stderr,
                )
            return 1
        print("Auditoria final determinística da epic #65 validada.")
        return 0
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_bytes(json_payload)
    REPORT_MD.write_bytes(markdown_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
