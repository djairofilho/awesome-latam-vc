#!/usr/bin/env python3
"""Reconcile the three official-validation shards without writing files."""

from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


EPIC = Path(__file__).resolve().parents[1]
PARTITIONS = range(3)
CUTOFF_DATE = "2026-08-02"
GATE_FIELDS = {
    "direct_investment": {"direct_startup_investment"},
    "recurrence": {"recurrence"},
    "recent_activity": {"activity_date"},
    "latam_access": {"base_geography", "market_access"},
    "identity": {"identity"},
}
ROUTE_DESTINATIONS = {
    "routed_accelerators": "ecosystem/accelerators/",
    "routed_angel_networks": "ecosystem/angel-networks/",
    "routed_funding_platforms": "ecosystem/funding-platforms/",
    "routed_public_programs": "ecosystem/public-programs/",
}
CANONICAL_JSON_KWARGS = {
    "ensure_ascii": False,
    "sort_keys": True,
    "separators": (",", ":"),
}


def canonical_line(record: dict[str, Any]) -> str:
    return json.dumps(record, **CANONICAL_JSON_KWARGS) + "\n"


def canonical_jsonl(records: list[dict[str, Any]], key: str) -> str:
    return "".join(
        canonical_line(record)
        for record in sorted(records, key=lambda row: str(row.get(key, "")))
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def record_sha256(record: dict[str, Any]) -> str:
    return sha256_text(canonical_line(record))


def partition(candidate_id: str) -> int:
    digest = hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % 3


def subtract_months(value: date, months: int) -> date:
    absolute_month = value.year * 12 + value.month - 1 - months
    year, month_index = divmod(absolute_month, 12)
    month = month_index + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: JSON inválido: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: registro deve ser objeto")
        rows.append(value)
    return rows


def unique_index(
    rows: list[dict[str, Any]], key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, str):
            errors.append(f"{label}: {key} ausente ou inválido")
            continue
        if value in result:
            errors.append(f"{label}: {key} duplicado: {value}")
        else:
            result[value] = row
    return result


def claim_finding(claim: dict[str, Any]) -> tuple[str | None, Any]:
    value = claim.get("value")
    if not isinstance(value, dict):
        return None, None
    return value.get("finding"), value.get("value")


def matching_claims(
    evidence: dict[str, Any], gate_name: str, finding: str
) -> list[dict[str, Any]]:
    return [
        claim
        for claim in evidence.get("claims", [])
        if claim.get("field") in GATE_FIELDS[gate_name]
        and claim_finding(claim)[0] == finding
    ]


def validate_gate_evidence(
    record: dict[str, Any],
    evidence: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    candidate_id = record["candidate_id"]
    for gate_name, gate in record["gates"].items():
        finding = gate["finding"]
        if finding == "blocked":
            continue
        for evidence_id in gate["evidence_ids"]:
            item = evidence.get(evidence_id)
            if item is None:
                errors.append(f"{candidate_id}: evidência inexistente em {gate_name}: {evidence_id}")
                continue
            if item.get("candidate_id") != candidate_id:
                errors.append(
                    f"{candidate_id}: evidência {evidence_id} pertence a "
                    f"{item.get('candidate_id')}"
                )
                continue
            if not matching_claims(item, gate_name, finding):
                errors.append(
                    f"{candidate_id}: evidência {evidence_id} não contém claim "
                    f"de {gate_name} com finding {finding}"
                )


def validate_activity(record: dict[str, Any], evidence: dict[str, dict[str, Any]], errors: list[str]) -> None:
    candidate_id = record["candidate_id"]
    gate = record["gates"]["recent_activity"]
    if gate["finding"] not in {"confirmed", "contradictory"}:
        return
    try:
        cutoff = date.fromisoformat(record["cutoff_date"])
        observed = date.fromisoformat(gate["latest_official_activity_on"])
    except (KeyError, TypeError, ValueError):
        return
    lower_bound = subtract_months(cutoff, 24)
    if observed > cutoff:
        errors.append(f"{candidate_id}: atividade oficial está no futuro")
    if gate["finding"] == "confirmed" and not lower_bound <= observed <= cutoff:
        errors.append(f"{candidate_id}: atividade confirmada fora da janela inclusiva de 24 meses")
    if gate["finding"] == "contradictory" and observed >= lower_bound:
        errors.append(f"{candidate_id}: atividade contraditória não é anterior à janela")
    claim_dates = {
        claim_finding(claim)[1]
        for evidence_id in gate["evidence_ids"]
        if (item := evidence.get(evidence_id)) is not None
        for claim in matching_claims(item, "recent_activity", gate["finding"])
    }
    if gate["latest_official_activity_on"] not in claim_dates:
        errors.append(f"{candidate_id}: data de atividade não coincide com evidência referenciada")


def validate_decision(record: dict[str, Any], errors: list[str]) -> None:
    candidate_id = record["candidate_id"]
    findings = {name: gate["finding"] for name, gate in record["gates"].items()}
    decision = record["decision"]
    destination = record["destination"]
    structural = ("direct_investment", "recurrence", "latam_access")
    confirmed_non_activity = all(
        findings[name] == "confirmed"
        for name in ("direct_investment", "recurrence", "latam_access", "identity")
    )
    unresolved = any(value in {"not_disclosed", "blocked"} for value in findings.values())

    if decision == "eligible":
        if set(findings.values()) != {"confirmed"}:
            errors.append(f"{candidate_id}: eligible exige os cinco gates confirmados")
        if destination != "funds/":
            errors.append(f"{candidate_id}: eligible exige destination funds/")
    elif decision == "excluded":
        if not any(findings[name] == "contradictory" for name in structural):
            errors.append(f"{candidate_id}: excluded exige gate estrutural contraditório")
        if destination is not None:
            errors.append(f"{candidate_id}: excluded não aceita destination")
    elif decision == "inactive":
        if not confirmed_non_activity or findings["recent_activity"] != "contradictory":
            errors.append(f"{candidate_id}: inactive exige quatro gates confirmados e atividade antiga")
        if destination is not None:
            errors.append(f"{candidate_id}: inactive não aceita destination")
    elif decision == "insufficient_evidence":
        if not unresolved:
            errors.append(f"{candidate_id}: insufficient_evidence exige not_disclosed ou blocked")
        if any(findings[name] == "contradictory" for name in structural):
            errors.append(f"{candidate_id}: contradição estrutural deve resultar em excluded")
        if confirmed_non_activity and findings["recent_activity"] == "contradictory":
            errors.append(f"{candidate_id}: atividade antiga comprovada deve resultar em inactive")
    elif decision == "duplicate":
        if findings["identity"] != "confirmed":
            errors.append(f"{candidate_id}: duplicate exige identidade confirmada")
        if not isinstance(destination, str) or not destination.startswith("funds/") or not destination.endswith(".md"):
            errors.append(f"{candidate_id}: duplicate exige perfil canônico em funds/")
    elif decision in ROUTE_DESTINATIONS or decision == "routed_other":
        if findings["identity"] != "confirmed":
            errors.append(f"{candidate_id}: encaminhamento exige identidade confirmada")
        expected = ROUTE_DESTINATIONS.get(decision)
        if expected is not None and destination != expected:
            errors.append(f"{candidate_id}: destination incompatível com {decision}")
        if decision == "routed_other" and (
            not isinstance(destination, str) or not destination.startswith("ecosystem/")
        ):
            errors.append(f"{candidate_id}: routed_other exige destination em ecosystem/")


def expected_summary(
    number: int,
    candidates_text: str,
    decisions_text: str,
    evidence_text: str,
    decisions: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "partition": number,
        "worker_id": f"validation-{number}",
        "input_records": len([line for line in candidates_text.splitlines() if line.strip()]),
        "decision_records": len(decisions),
        "evidence_records": len(evidence),
        "decision_counts": dict(
            sorted(Counter(str(row.get("decision", "<invalid>")) for row in decisions).items())
        ),
        "candidates_sha256": sha256_text(candidates_text),
        "decisions_sha256": sha256_text(decisions_text),
        "evidence_sha256": sha256_text(evidence_text),
    }


def reconcile(epic: Path = EPIC) -> list[str]:
    errors: list[str] = []
    consolidation = epic / "consolidation"
    freeze_paths = [
        consolidation / "candidates.jsonl",
        consolidation / "evidence.jsonl",
        consolidation / "exceptions.jsonl",
    ]
    missing_freeze = [path for path in freeze_paths if not path.is_file()]
    if missing_freeze:
        rendered = ", ".join(path.relative_to(epic).as_posix() for path in missing_freeze)
        return [f"freeze da #333 ausente ou incompleto: {rendered}"]

    try:
        consolidated_rows = load_jsonl(freeze_paths[0])
        base_evidence_rows = load_jsonl(freeze_paths[1])
        exception_rows = load_jsonl(freeze_paths[2])
    except (OSError, ValueError) as exc:
        return [str(exc)]

    consolidated = unique_index(consolidated_rows, "candidate_id", "consolidation/candidates.jsonl", errors)
    ready = {
        candidate_id: row
        for candidate_id, row in consolidated.items()
        if row.get("status") == "ready_for_validation"
    }
    exceptions = unique_index(exception_rows, "candidate_id", "consolidation/exceptions.jsonl", errors)
    overlap = sorted(set(ready) & set(exceptions))
    if overlap:
        errors.append(f"candidatos prontos também presentes em exceptions: {overlap}")

    validation_schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "validation-record.schema.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (Path(__file__).resolve().parents[1] / "schemas" / "official-evidence-record.schema.json").read_text(encoding="utf-8")
    )
    decision_validator = Draft202012Validator(validation_schema, format_checker=FormatChecker())
    evidence_validator = Draft202012Validator(evidence_schema, format_checker=FormatChecker())

    all_evidence = unique_index(base_evidence_rows, "evidence_id", "consolidation/evidence.jsonl", errors)
    all_decisions: dict[str, dict[str, Any]] = {}
    new_evidence_ids: set[str] = set()

    for number in PARTITIONS:
        shard = epic / "shards" / f"validation-{number}"
        required = [
            shard / "candidates.jsonl",
            shard / "decisions.jsonl",
            shard / "official-evidence.jsonl",
            shard / "summary.json",
        ]
        missing = [path for path in required if not path.is_file()]
        if missing:
            errors.append(
                f"validation-{number}: artefatos ausentes: "
                + ", ".join(path.name for path in missing)
            )
            continue
        try:
            candidates_text = required[0].read_text(encoding="utf-8")
            decisions_text = required[1].read_text(encoding="utf-8")
            evidence_text = required[2].read_text(encoding="utf-8")
            shard_candidates = load_jsonl(required[0])
            shard_decisions = load_jsonl(required[1])
            shard_evidence = load_jsonl(required[2])
            summary = load_json(required[3])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue

        if candidates_text != canonical_jsonl(shard_candidates, "candidate_id"):
            errors.append(f"validation-{number}/candidates.jsonl: JSONL não canônico")
        if decisions_text != canonical_jsonl(shard_decisions, "candidate_id"):
            errors.append(f"validation-{number}/decisions.jsonl: JSONL não canônico")
        if evidence_text != canonical_jsonl(shard_evidence, "evidence_id"):
            errors.append(f"validation-{number}/official-evidence.jsonl: JSONL não canônico")

        shard_candidate_index = unique_index(shard_candidates, "candidate_id", f"validation-{number}/candidates.jsonl", errors)
        shard_decision_index = unique_index(shard_decisions, "candidate_id", f"validation-{number}/decisions.jsonl", errors)
        if set(shard_candidate_index) != set(shard_decision_index):
            errors.append(f"validation-{number}: decisões não reconciliam exatamente com a entrada")

        expected_ids = {candidate_id for candidate_id in ready if partition(candidate_id) == number}
        if set(shard_candidate_index) != expected_ids:
            errors.append(f"validation-{number}: entrada não coincide com a partição congelada")

        for candidate_id, candidate in shard_candidate_index.items():
            frozen = ready.get(candidate_id)
            if frozen is not None and candidate != frozen:
                errors.append(f"{candidate_id}: registro de entrada diverge do freeze")

        for item in shard_evidence:
            for schema_error in evidence_validator.iter_errors(item):
                errors.append(f"validation-{number}/official-evidence.jsonl: {schema_error.message}")
            evidence_id = item.get("evidence_id")
            if isinstance(evidence_id, str):
                if evidence_id in all_evidence:
                    errors.append(f"evidence_id global duplicado: {evidence_id}")
                else:
                    all_evidence[evidence_id] = item
                    new_evidence_ids.add(evidence_id)

        for candidate_id, record in shard_decision_index.items():
            for schema_error in decision_validator.iter_errors(record):
                errors.append(f"{candidate_id}: {schema_error.message}")
            if candidate_id in all_decisions:
                errors.append(f"decisão global duplicada: {candidate_id}")
            else:
                all_decisions[candidate_id] = record
            frozen = ready.get(candidate_id)
            if frozen is None:
                continue
            if record.get("input_sha256") != record_sha256(frozen):
                errors.append(f"{candidate_id}: input_sha256 divergente")
            if record.get("validation_partition") != number or partition(candidate_id) != number:
                errors.append(f"{candidate_id}: validation_partition divergente")
            if record.get("validator") != f"validation-{number}":
                errors.append(f"{candidate_id}: validator não possui o shard")
            if record.get("cutoff_date") != CUTOFF_DATE:
                errors.append(f"{candidate_id}: cutoff_date diverge do contrato")

        expected = expected_summary(
            number,
            candidates_text,
            decisions_text,
            evidence_text,
            shard_decisions,
            shard_evidence,
        )
        if summary != expected:
            errors.append(f"validation-{number}/summary.json: conteúdo divergente")

    if set(all_decisions) != set(ready):
        missing = sorted(set(ready) - set(all_decisions))
        extra = sorted(set(all_decisions) - set(ready))
        errors.append(f"união dos três shards não é exata; ausentes={missing}, extras={extra}")
    if set(all_decisions) & set(exceptions):
        errors.append("decisões de validação se sobrepõem às exceptions da consolidação")

    referenced: set[str] = set()
    for candidate_id, record in all_decisions.items():
        gates = record.get("gates")
        if not isinstance(gates, dict) or set(gates) != set(GATE_FIELDS):
            continue
        if any(
            not isinstance(gate, dict)
            or "finding" not in gate
            or not isinstance(gate.get("evidence_ids"), list)
            for gate in gates.values()
        ):
            continue
        validate_gate_evidence(record, all_evidence, errors)
        validate_activity(record, all_evidence, errors)
        validate_decision(record, errors)
        for gate in gates.values():
            referenced.update(gate.get("evidence_ids", []))
    orphan_new = sorted(new_evidence_ids - referenced)
    if orphan_new:
        errors.append(f"evidências novas não referenciadas: {orphan_new}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validar sem escrever arquivos")
    parser.parse_args()
    errors = reconcile()
    if errors:
        print("Reconciliação da validação falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Três shards de validação reconciliados sem escrita.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
