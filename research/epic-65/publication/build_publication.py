#!/usr/bin/env python3
"""Build deterministic public-program profiles from the frozen issue #103 plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONSOLIDATION = HERE.parent / "consolidation"
PLAN = HERE / "publication-plan.json"
INDEX = ROOT / "ecosystem" / "public-programs" / "README.md"

BENEFIT_LABELS = {
    "capital": "capital",
    "cofinanciamento": "co-financing",
    "crédito": "credit",
    "garantia": "guarantee",
    "subvenção": "grant or non-repayable funding",
}
PROGRAM_STATUS_LABELS = {
    "ativo": "Active",
    "fechado agora, recorrente": "Currently closed, officially recurring",
}
ACTIVITY_LABELS = {
    "chamada aberta": "open call at the cutoff snapshot",
    "intake permanente": "permanent intake observed at the cutoff",
    "recorrência oficial em 24 meses": "official recurrence within 24 months",
}
CALL_STATUS_LABELS = {
    "aberta": "Open at the cutoff snapshot",
    "fechada": "Closed",
    "prevista": "Scheduled",
    "não confirmada": "Not confirmed",
}
COUNTRY_ORDER = (
    "Bolivia",
    "Brazil",
    "Chile",
    "Ecuador",
    "Mexico",
    "Peru",
    "Uruguay",
)
COUNTRY_BY_DIRECTORY = {
    "bolivia": "Bolivia",
    "brazil": "Brazil",
    "chile": "Chile",
    "ecuador": "Ecuador",
    "mexico": "Mexico",
    "peru": "Peru",
    "uruguay": "Uruguay",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def normalized_hash(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def split_front_matter(payload: bytes) -> tuple[bytes, bytes]:
    normalized = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = normalized.splitlines(keepends=True)
    if not lines or lines[0].strip() != b"---":
        return b"", normalized
    closing_index = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == b"---"
        ),
        None,
    )
    if closing_index is None:
        return b"", normalized
    return (
        b"".join(lines[: closing_index + 1]),
        b"".join(lines[closing_index + 1 :]).lstrip(b"\n"),
    )


def profile_payload(path: Path, body: bytes) -> bytes:
    front_matter = b""
    if path.is_file():
        front_matter, _existing_body = split_front_matter(path.read_bytes())
    return front_matter + body.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def profile_hash(payload: bytes) -> str:
    _front_matter, body = split_front_matter(payload)
    return hashlib.sha256(body).hexdigest()


def aliases_line(aliases: list[str]) -> str:
    return ", ".join(aliases) if aliases else "None recorded"


def evidence_section(evidence_rows: list[dict[str, Any]]) -> list[str]:
    lines = ["## Official sources", ""]
    for row in evidence_rows:
        lines.append(
            f"- [{row['title']}]({row['url']}) — {row['summary']} "
            f"(`{row['evidence_id']}`)"
        )
    return lines


def render_agency(
    agency: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]],
    eligible_programs: dict[str, dict[str, Any]],
    path_by_id: dict[str, Path],
    batch_id: str,
) -> str:
    program_ids = [
        program_id
        for program_id in agency["program_ids"]
        if program_id in eligible_programs
    ]
    rows = [evidence_by_id[evidence_id] for evidence_id in agency["official_evidence_ids"]]
    summary = " ".join(row["summary"] for row in rows)
    lines = [
        f"# {agency['name']}",
        "",
        f"- **Entity ID:** `{agency['agency_id']}`",
        "- **Entity type:** Public agency",
        f"- **Aliases:** {aliases_line(agency['aliases'])}",
        f"- **Website:** {agency['official_site']}",
        f"- **Geography:** {', '.join(agency['geography'])}",
        f"- **Founder route:** {agency['route_url']}",
        f"- **Publication batch:** `{batch_id}`",
        "",
        summary,
        "",
        "This agency profile represents the stable public route. Program-specific "
        "benefits, eligibility, values, dates, and availability remain attached "
        "to each program or call.",
        "",
        "## Published programs",
        "",
    ]
    for program_id in program_ids:
        target = path_by_id[program_id]
        program = eligible_programs[program_id]
        lines.append(f"- [{program['name']}]({target.name}) (`{program_id}`)")
    lines.extend([""] + evidence_section(rows))
    lines.extend(["", "**Last verified:** 2026-07-27", ""])
    return "\n".join(lines)


def call_lines(
    call_id: str,
    calls_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    call = calls_by_id[call_id]
    lines = [
        f"### {call['name']}",
        "",
        f"- **Call ID:** `{call_id}`",
        f"- **Status:** {CALL_STATUS_LABELS[call['call_status']]}",
        f"- **Snapshot date:** {call['captured_on']}",
    ]
    if call["opened_on"]:
        lines.append(f"- **Opened on:** {call['opened_on']}")
    if call["closes_on"]:
        lines.append(f"- **Closed or closes on:** {call['closes_on']}")
    lines.extend(
        [
            f"- **Call route:** {call['route_url']}",
            f"- **Call-specific benefit:** {call['benefit_summary']}",
            f"- **Call-specific eligibility:** {call['eligibility_summary']}",
            "",
            "This is a historical snapshot, not a permanent availability claim. "
            "Check the official route for the current status.",
            "",
        ]
    )
    return lines


def render_program(
    program: dict[str, Any],
    agency_by_id: dict[str, dict[str, Any]],
    evidence_by_id: dict[str, dict[str, Any]],
    calls_by_id: dict[str, dict[str, Any]],
    path_by_id: dict[str, Path],
    batch_id: str,
) -> str:
    agency = agency_by_id[program["agency_id"]]
    rows = [
        evidence_by_id[evidence_id]
        for evidence_id in program["official_evidence_ids"]
    ]
    benefit = ", ".join(
        BENEFIT_LABELS[item] for item in program["benefit_types"]
    )
    lines = [
        f"# {program['name']}",
        "",
        f"- **Entity ID:** `{program['program_id']}`",
        "- **Entity type:** Public funding program",
        f"- **Operator:** [{agency['name']}]({path_by_id[agency['agency_id']].name}) "
        f"(`{agency['agency_id']}`)",
        f"- **Aliases:** {aliases_line(program['aliases'])}",
        f"- **Official page:** {program['official_url']}",
        f"- **Geography:** {', '.join(program['geography'])}",
        f"- **Financial support:** {benefit}",
        f"- **Program status:** {PROGRAM_STATUS_LABELS[program['program_status']]}",
        f"- **Activity basis:** {ACTIVITY_LABELS[program['activity_basis']]}",
        f"- **Founder route:** {program['route_url']}",
        f"- **Publication batch:** `{batch_id}`",
        "",
        " ".join(row["summary"] for row in rows),
        "",
    ]
    if program["program_status"] == "fechado agora, recorrente":
        lines.extend(
            [
                "The program is not presented as currently open. Official evidence "
                "supports recurrence, while founders must verify the next call and "
                "its specific terms.",
                "",
            ]
        )
    elif program["activity_basis"] == "chamada aberta":
        lines.extend(
            [
                "The open status below is limited to the 2026-07-27 snapshot. "
                "Founders must verify the official route before applying.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Availability is based on the official route observed at the cutoff. "
                "Terms can change, so founders must confirm the current instrument.",
                "",
            ]
        )
    lines.extend(["## Agency relationship", ""])
    lines.append(
        f"- Operated by [{agency['name']}]"
        f"({path_by_id[agency['agency_id']].name})."
    )
    lines.extend(["", "## Calls", ""])
    if program["call_ids"]:
        for call_id in program["call_ids"]:
            lines.extend(call_lines(call_id, calls_by_id))
    else:
        lines.extend(
            [
                "No temporary call is attached to the frozen eligible record. "
                "Use the official founder route for the current intake.",
                "",
            ]
        )
    lines.extend(evidence_section(rows))
    lines.extend(["", "**Last verified:** 2026-07-27", ""])
    return "\n".join(lines)


def render_index(
    profiles: list[dict[str, Any]],
    agency_by_id: dict[str, dict[str, Any]],
    program_by_id: dict[str, dict[str, Any]],
) -> str:
    lines = [
        "# Public programs",
        "",
        "Public agencies and programs in this index provide an official, structured "
        "route to grants, co-financing, credit, guarantees, or capital for startups. "
        "They are not venture capital funds.",
        "",
        "Agency profiles describe stable institutional routes. Program profiles "
        "describe durable instruments. Temporary calls never receive profiles; "
        "their status, dates, values, and eligibility remain call-specific.",
        "",
        "The index contains 12 agencies and 17 programs verified on 2026-07-27. "
        "A program marked as currently closed and recurring is not presented as open.",
        "",
    ]
    by_country: dict[str, list[dict[str, Any]]] = {
        country: [] for country in COUNTRY_ORDER
    }
    for profile in profiles:
        directory = Path(profile["path"]).parent.name
        by_country[COUNTRY_BY_DIRECTORY[directory]].append(profile)
    for country in COUNTRY_ORDER:
        rows = by_country[country]
        if not rows:
            continue
        lines.extend(
            [
                f"## {country}",
                "",
                "| Organization | Entity | Financial route | Status |",
                "| --- | --- | --- | --- |",
            ]
        )
        for profile in sorted(rows, key=lambda row: row["entity_id"]):
            relative = Path(profile["path"]).relative_to(
                Path("ecosystem/public-programs")
            ).as_posix()
            if profile["entity_type"] == "agency":
                entity = agency_by_id[profile["entity_id"]]
                route = "Multiple public instruments"
                status = "Active institutional route"
                entity_type = "Agency"
            else:
                entity = program_by_id[profile["entity_id"]]
                route = ", ".join(
                    BENEFIT_LABELS[item] for item in entity["benefit_types"]
                )
                status = PROGRAM_STATUS_LABELS[entity["program_status"]]
                entity_type = "Program"
            lines.append(
                f"| [{profile['name']}]({relative}) | {entity_type} | "
                f"{route} | {status} |"
            )
        lines.append("")
    return "\n".join(lines)


def build() -> tuple[dict[Path, bytes], dict[str, Any]]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    agencies = read_jsonl(CONSOLIDATION / "agencies.jsonl")
    programs = read_jsonl(CONSOLIDATION / "programs.jsonl")
    calls = read_jsonl(CONSOLIDATION / "calls.jsonl")
    evidence = read_jsonl(CONSOLIDATION / "evidence.jsonl")
    agency_by_id = {row["agency_id"]: row for row in agencies}
    program_by_id = {row["program_id"]: row for row in programs}
    eligible_programs = {
        row["program_id"]: row
        for row in programs
        if row["decision"] == "elegível"
    }
    calls_by_id = {row["call_id"]: row for row in calls}
    evidence_by_id = {row["evidence_id"]: row for row in evidence}
    profiles = [
        profile
        for batch in plan["batches"]
        for profile in batch["profiles"]
    ]
    path_by_id = {
        profile["entity_id"]: ROOT / profile["path"] for profile in profiles
    }
    batch_by_id = {
        profile["entity_id"]: batch["batch_id"]
        for batch in plan["batches"]
        for profile in batch["profiles"]
    }
    outputs: dict[Path, bytes] = {}
    profile_hashes: dict[str, str] = {}
    for profile in profiles:
        entity_id = profile["entity_id"]
        if profile["entity_type"] == "agency":
            text = render_agency(
                agency_by_id[entity_id],
                evidence_by_id,
                eligible_programs,
                path_by_id,
                batch_by_id[entity_id],
            )
        else:
            text = render_program(
                program_by_id[entity_id],
                agency_by_id,
                evidence_by_id,
                calls_by_id,
                path_by_id,
                batch_by_id[entity_id],
            )
        path = path_by_id[entity_id]
        payload = profile_payload(path, text.encode("utf-8"))
        outputs[path] = payload
        profile_hashes[profile["path"]] = profile_hash(payload)
    index_text = render_index(profiles, agency_by_id, program_by_id)
    outputs[INDEX] = index_text.encode("utf-8")
    manifest = {
        "schema_version": "1.0",
        "issue": 103,
        "cutoff_date": "2026-07-27",
        "status": "complete",
        "profile_queue_hash": plan["profile_queue_hash"],
        "batch_count": len(plan["batches"]),
        "profile_count": len(profiles),
        "agency_profiles": sum(
            profile["entity_type"] == "agency" for profile in profiles
        ),
        "program_profiles": sum(
            profile["entity_type"] == "program" for profile in profiles
        ),
        "call_profiles": 0,
        "batches": [
            {
                "batch_id": batch["batch_id"],
                "batch_hash": batch["batch_hash"],
                "issue_number": batch["issue_number"],
                "branch": batch["branch"],
                "profile_count": len(batch["profiles"]),
            }
            for batch in plan["batches"]
        ],
        "profile_hashes": dict(sorted(profile_hashes.items())),
        "index_hash": hashlib.sha256(index_text.encode("utf-8")).hexdigest(),
        "source_hashes": plan["source_hashes"],
        "notes": (
            "A disponibilidade, os valores e as datas de chamadas permanecem "
            "restritos aos snapshots vinculados. Nenhuma chamada recebeu perfil."
        ),
    }
    return outputs, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when profiles, index or manifest differ",
    )
    args = parser.parse_args()
    outputs, manifest = build()
    manifest_path = HERE / "publication-manifest.json"
    manifest_payload = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    outputs[manifest_path] = manifest_payload
    drift: list[str] = []
    for path, payload in outputs.items():
        if args.check:
            current = (
                path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                if path.is_file()
                else None
            )
            expected = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            if current != expected:
                drift.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    if drift:
        raise SystemExit(f"publication drift: {', '.join(sorted(drift))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
