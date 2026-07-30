#!/usr/bin/env python3
"""Record independent approval and freeze the transverse handoff batch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"
ELIGIBLE_IDS = ["ar-beta-impacto", "ar-primary-x", "br-saasholic"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


review = {
    "schema_version": "1.0",
    "status": "approved",
    "reviewer": "integrator",
    "requested_on": CUTOFF,
    "reviewed_on": CUTOFF,
    "review_reconciled": True,
    "publication_authorized": True,
    "critical_open": 0,
    "high_open": 0,
    "eligible_reviewed": ELIGIBLE_IDS,
    "regulatory_cases_reviewed": [],
    "base_geography_reviewed": ELIGIBLE_IDS,
    "findings": [
        {
            "candidate_id": "ar-beta-impacto",
            "severity": "low",
            "status": "accepted_limitation",
            "finding": (
                "Official and institutional sources support a direct early-stage vehicle, "
                "Argentina base, active process and founder application. The absence of "
                "machine-readable portfolio company names remains disclosed but does not "
                "invalidate eligibility."
            ),
        }
    ],
    "regulator_conclusion": (
        "No lookup was justified because official and institutional sources resolved identity "
        "and base geography without a material divergence."
    ),
}
write_json(OUT / "review.json", review)

frozen_paths = [
    OUT / "contract.json",
    OUT / "source-inventory.jsonl",
    OUT / "candidates.jsonl",
    OUT / "evidence.jsonl",
    OUT / "regulator-query-log.jsonl",
    OUT / "coverage-matrix.json",
    OUT / "review-request.json",
    OUT / "prefreeze-manifest.json",
    OUT / "review.json",
]
freeze = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "status": "frozen",
    "reviewer": "integrator",
    "review_reconciled": True,
    "critical_open": 0,
    "high_open": 0,
    "eligible_ids": ELIGIBLE_IDS,
    "publication_batch_count": 1,
    "publication_batch_limit": 10,
    "localized_profile_count": 9,
    "beta_impacto_limitation": (
        "The current official pages describe portfolio operations but do not expose portfolio "
        "company names as machine-readable text."
    ),
    "artifact_hashes": {
        path.relative_to(ROOT).as_posix(): digest(path)
        for path in frozen_paths
    },
}
write_json(OUT / "freeze-manifest.json", freeze)
print(json.dumps({"status": "frozen", "eligible": len(ELIGIBLE_IDS)}, ensure_ascii=False))
