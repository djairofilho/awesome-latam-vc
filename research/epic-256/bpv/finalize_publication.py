#!/usr/bin/env python3
"""Freeze the approved BPV audit and record the exact publication batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


review = read_json(OUT / "review.json")
assert review["status"] == "approved"
assert review["review_reconciled"] is True
assert review["publication_authorized"] is True
assert review["critical_open"] == review["high_open"] == 0

candidates = read_jsonl(OUT / "candidates.jsonl")
eligible = [row for row in candidates if row["decision"] == "eligible"]
expected = {
    row["candidate_id"]: row["canonical_destination"]
    for row in eligible
}
localized_paths = []
for destination in expected.values():
    relative = Path(destination)
    localized_paths.extend([
        relative,
        Path("translations") / "pt-BR" / relative,
        Path("translations") / "es" / relative,
    ])
for relative in localized_paths:
    assert (ROOT / relative).is_file(), relative

artifact_paths = [
    OUT / "contract.json",
    OUT / "source-inventory.jsonl",
    OUT / "candidates.jsonl",
    OUT / "evidence.jsonl",
    OUT / "regulator-query-log.jsonl",
    OUT / "coverage-matrix.json",
    OUT / "review-request.json",
    OUT / "review.json",
    OUT / "baseline" / "catalog-baseline.jsonl",
    OUT / "baseline" / "prior-candidates.jsonl",
    OUT / "baseline" / "summary.json",
]
freeze = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "reviewed_on": review["reviewed_on"],
    "reviewer": review["reviewer"],
    "review_reconciled": True,
    "critical_or_high_findings_open": 0,
    "eligible_ids": list(expected),
    "counts": {
        "candidates": len(candidates),
        "eligible": len(eligible),
        "duplicates": sum(row["decision"] == "duplicate" for row in candidates),
        "routed_or_out_of_scope": sum(row["decision"] == "routed" for row in candidates),
        "insufficient_evidence": sum(row["decision"] == "insufficient_evidence" for row in candidates),
        "regulatory_queries": len(read_jsonl(OUT / "regulator-query-log.jsonl")),
    },
    "publication_batches": [{
        "batch": 1,
        "candidate_ids": list(expected),
        "profile_paths": list(expected.values()),
    }],
    "artifact_hashes": {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in artifact_paths
    },
    "limitations": [
        "Audited coverage of enumerated public sources, not absolute market completeness.",
        "The regulator was used for one identity check only and did not drive discovery or eligibility.",
        "Sparse public evidence leaves FIIP, Zeal Fund, +58 Ventures and Avila VC outside this publication cut.",
    ],
}
write_json(OUT / "freeze-manifest.json", freeze)

profile_hashes = {
    path.as_posix(): digest(ROOT / path)
    for path in localized_paths
}
publication = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "batch_count": 1,
    "batch_limit": 10,
    "eligible_ids": list(expected),
    "published_profile_count": len(expected),
    "localized_profile_count": len(localized_paths),
    "profile_hashes": profile_hashes,
    "critical_or_high_findings_open": 0,
}
write_json(OUT / "publication-report.json", publication)
write_json(OUT / "closure-report.json", {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "status": "complete",
    "issues": [294, 295, 296, 297, 298],
    "issues_closed": False,
    "audited_coverage": True,
    "candidate_count": len(candidates),
    "eligible_published": len(expected),
    "publication_batches": 1,
    "non_regulatory_discovery_percent": 100.0,
    "regulatory_case_percent": 5.0,
    "critical_or_high_findings_open": 0,
})
print(json.dumps({"eligible": len(expected), "localized_profiles": len(localized_paths)}, ensure_ascii=False))
