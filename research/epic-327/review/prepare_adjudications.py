#!/usr/bin/env python3
"""Prepare explicit adjudications for reconciled independent-review changes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[3]
EPIC = ROOT / "research" / "epic-327"
HERE = EPIC / "review"
CHANGES = HERE / "changes-requested.jsonl"
OUTPUT = HERE / "adjudications.jsonl"
ADJUDICATED_ON = "2026-08-02"
ADJUDICATOR = "integration-review"
REASON = (
    "Independent review change accepted after official-evidence schema, ownership, "
    "and decision-transition reconciliation."
)


def canonical_line(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_sha256(record: dict) -> str:
    return hashlib.sha256(canonical_line(record).encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def render(changes_path: Path = CHANGES, epic: Path = EPIC) -> tuple[list[str], str]:
    errors = []
    try:
        changes = load_jsonl(changes_path)
        schema = json.loads(
            (epic / "schemas" / "adjudication-record.schema.json").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)], ""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    rows = []
    seen = set()
    for index, change in enumerate(changes, 1):
        candidate_id = change.get("candidate_id")
        if candidate_id in seen:
            errors.append(f"{candidate_id}: mudança duplicada")
            continue
        seen.add(candidate_id)
        if change.get("review_status") != "changes_requested":
            errors.append(f"{candidate_id}: registro não solicita mudança")
        evidence_ids = change.get("evidence_ids", [])
        if not evidence_ids:
            errors.append(f"{candidate_id}: mudança sem evidência oficial")
        row = {
            "schema_version": "1.0",
            "candidate_id": candidate_id,
            "adjudicator": ADJUDICATOR,
            "adjudicated_on": ADJUDICATED_ON,
            "review_record_sha256": record_sha256(change),
            "resolution": "accept_review_change",
            "final_decision": change.get("final_decision"),
            "destination": change.get("destination"),
            "evidence_ids": evidence_ids,
            "reason": REASON,
        }
        for error in validator.iter_errors(row):
            errors.append(f"adjudications:{index}: {error.message}")
        rows.append(row)
    rows.sort(key=lambda row: row["candidate_id"])
    rendered = "".join(canonical_line(row) + "\n" for row in rows)
    return sorted(set(errors)), rendered


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors, rendered = render()
    if errors:
        print("Preparação de adjudicações falhou:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"{OUTPUT}: ausente ou desatualizado", file=sys.stderr)
            return 1
    else:
        OUTPUT.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"Adjudicações preparadas: {len(rendered.splitlines())} registros.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
