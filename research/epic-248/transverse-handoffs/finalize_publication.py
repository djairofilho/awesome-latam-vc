#!/usr/bin/env python3
"""Publish the frozen transverse handoff batch and record its report."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from publication import profile_outputs


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


freeze = json.loads((OUT / "freeze-manifest.json").read_text(encoding="utf-8"))
if not freeze["review_reconciled"] or freeze["critical_open"] or freeze["high_open"]:
    raise SystemExit("Frozen batch is not authorized for publication")

outputs = profile_outputs(ROOT, CUTOFF)
for path, content in outputs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

report = {
    "schema_version": "1.0",
    "cutoff": CUTOFF,
    "status": "published",
    "eligible_ids": freeze["eligible_ids"],
    "canonical_profile_count": 3,
    "localized_profile_count": len(outputs),
    "locales": ["en", "es", "pt-BR"],
    "review_reconciled": True,
    "critical_open": 0,
    "high_open": 0,
    "profile_hashes": {
        path.relative_to(ROOT).as_posix(): digest_bytes(content)
        for path, content in sorted(outputs.items(), key=lambda item: item[0].as_posix())
    },
    "limitations": [
        "This publication reconciles three audited handoffs and does not reopen the Argentina or Brazil completeness claims.",
        "Beta Impacto does not expose portfolio company names as machine-readable text; the profile does not infer any.",
        "No regulator query was used for discovery or eligibility.",
    ],
}
(OUT / "publication-report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({"profiles": len(outputs), "status": "published"}, ensure_ascii=False))
