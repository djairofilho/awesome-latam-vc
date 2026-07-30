"""Build auditable publication manifests without changing the frozen research core."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BRAZIL = Path(__file__).resolve().parents[1]
REPOSITORY = BRAZIL.parents[2]
FREEZE_PATH = BRAZIL / "freeze-manifest.json"
PUBLICATION = Path(__file__).resolve().parent
CUTOFF = "2026-07-30"
ISSUES = {1: 241, 2: 242, 3: 243}
EXPECTED_BATCH_HASHES = {
    1: "7e397d3246d7c9fe1c31dc3555dce9c9d65f653f2d985b7497eecf07badd18a4",
}


def compact_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest()


def profile_record(candidate: dict[str, Any]) -> dict[str, Any]:
    canonical = Path(candidate["destination"])
    paths = {
        "en": canonical,
        "pt-BR": Path("translations") / "pt-BR" / canonical,
        "es": Path("translations") / "es" / canonical,
    }
    missing = [
        relative.as_posix()
        for relative in paths.values()
        if not (REPOSITORY / relative).is_file()
    ]
    if missing:
        raise ValueError(f"Perfis ausentes para {candidate['candidate_id']}: {missing}")
    return {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["name"],
        "destination": canonical.as_posix(),
        "profiles": {
            locale: {
                "path": relative.as_posix(),
                "sha256": sha256((REPOSITORY / relative).read_bytes()),
            }
            for locale, relative in paths.items()
        },
    }


def build_manifest(batch_ordinal: int) -> dict[str, Any]:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    batch = freeze["publication"]["batches"][batch_ordinal - 1]
    candidates = batch["candidates"]
    frozen_payload = compact_json(candidates).encode("utf-8")
    frozen_hash = sha256(frozen_payload)
    expected_hash = EXPECTED_BATCH_HASHES.get(batch_ordinal)
    if expected_hash is not None and frozen_hash != expected_hash:
        raise ValueError(
            f"Hash congelado divergente no lote {batch_ordinal}: {frozen_hash}"
        )
    profiles = [profile_record(candidate) for candidate in candidates]
    candidate_ids = [item["candidate_id"] for item in profiles]
    destinations = [item["destination"] for item in profiles]
    localized_paths = [
        localized["path"]
        for item in profiles
        for localized in item["profiles"].values()
    ]
    return {
        "schema_version": "1.0",
        "epic": 207,
        "parent_issue": 223,
        "freeze_issue": 222,
        "issue": ISSUES[batch_ordinal],
        "batch_id": batch["batch_id"],
        "batch_ordinal": batch_ordinal,
        "cutoff_date": CUTOFF,
        "published_on": CUTOFF,
        "hash_algorithm": "sha256",
        "freeze_manifest_sha256": sha256(FREEZE_PATH.read_bytes()),
        "frozen_batch_sha256": frozen_hash,
        "candidate_count": len(profiles),
        "profile_file_count": len(localized_paths),
        "profiles": profiles,
        "integrity": {
            "candidate_ids_unique": len(candidate_ids) == len(set(candidate_ids)),
            "destinations_unique": len(destinations) == len(set(destinations)),
            "localized_paths_unique": len(localized_paths)
            == len(set(localized_paths)),
            "one_candidate_to_three_locales": all(
                set(item["profiles"]) == {"en", "pt-BR", "es"}
                for item in profiles
            ),
            "all_profile_hashes_present": all(
                localized["sha256"]
                for item in profiles
                for localized in item["profiles"].values()
            ),
        },
        "limitations": (
            "Este manifesto prova correspondência com o lote congelado e os "
            "arquivos publicados; não altera os artefatos centrais da pesquisa."
        ),
    }


def write_or_check(batch_ordinal: int, check: bool) -> int:
    output = PUBLICATION / f"batch-{batch_ordinal:02d}.json"
    expected = json_bytes(build_manifest(batch_ordinal))
    if check:
        if not output.is_file() or output.read_bytes() != expected:
            raise ValueError(f"Manifesto de publicação divergente: {output.name}")
        print(f"Manifesto de publicação verificado: {output.name}.")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    print(f"Manifesto de publicação gerado: {output.name}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=int, choices=ISSUES, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(args.batch, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
