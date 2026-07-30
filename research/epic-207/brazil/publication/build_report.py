"""Build the deterministic aggregate publication report for issue #223."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BRAZIL = Path(__file__).resolve().parents[1]
REPOSITORY = BRAZIL.parents[2]
PUBLICATION = Path(__file__).resolve().parent
FREEZE_PATH = BRAZIL / "freeze-manifest.json"
OUTPUT = PUBLICATION / "publication-report.json"
BATCH_ORDINALS = (1, 2, 3)
EXPECTED_BATCH_HASHES = {
    1: "7e397d3246d7c9fe1c31dc3555dce9c9d65f653f2d985b7497eecf07badd18a4",
    2: "b01d1a3043106144b65c1acb25094f3ecf435a556075d9fbd2b7d210469fecc4",
    3: "9e5609a39f369be5b7ba07ec6dee942f4eefa00e8f574f504ea9327f330458c7",
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report() -> dict[str, Any]:
    freeze = load_json(FREEZE_PATH)
    frozen_batches = freeze["publication"]["batches"]
    if len(frozen_batches) != len(BATCH_ORDINALS):
        raise ValueError("O freeze não contém exatamente três lotes.")

    manifests = []
    frozen_candidates = []
    published_profiles = []
    published_profile_files = []
    for ordinal in BATCH_ORDINALS:
        manifest_path = PUBLICATION / f"batch-{ordinal:02d}.json"
        manifest = load_json(manifest_path)
        frozen_batch = frozen_batches[ordinal - 1]
        frozen = frozen_batch["candidates"]
        frozen_hash = sha256(compact_json(frozen).encode("utf-8"))
        if frozen_hash != EXPECTED_BATCH_HASHES[ordinal]:
            raise ValueError(f"Hash congelado divergente no lote {ordinal}.")
        if manifest["frozen_batch_sha256"] != frozen_hash:
            raise ValueError(f"Manifesto do lote {ordinal} diverge do freeze.")
        if manifest["batch_ordinal"] != ordinal:
            raise ValueError(f"Ordinal divergente no lote {ordinal}.")
        if manifest["batch_id"] != frozen_batch["batch_id"]:
            raise ValueError(f"Identificador divergente no lote {ordinal}.")
        expected_pairs = [
            (item["candidate_id"], item["destination"]) for item in frozen
        ]
        actual_pairs = [
            (item["candidate_id"], item["destination"])
            for item in manifest["profiles"]
        ]
        if actual_pairs != expected_pairs:
            raise ValueError(f"Candidatos divergentes no lote {ordinal}.")
        if manifest["candidate_count"] != len(frozen):
            raise ValueError(f"Contagem divergente no lote {ordinal}.")

        paths = []
        for profile in manifest["profiles"]:
            if set(profile["profiles"]) != {"en", "pt-BR", "es"}:
                raise ValueError(
                    f"Locales incompletos para {profile['candidate_id']}."
                )
            for localized in profile["profiles"].values():
                relative = localized["path"]
                current_hash = sha256((REPOSITORY / relative).read_bytes())
                if localized["sha256"] != current_hash:
                    raise ValueError(f"Hash de perfil divergente: {relative}.")
                paths.append(relative)
                published_profile_files.append(
                    {
                        "path": relative,
                        "sha256": current_hash,
                    }
                )
        if len(paths) != 27 or manifest["profile_file_count"] != 27:
            raise ValueError(f"Lote {ordinal} não contém 27 perfis.")

        frozen_candidates.extend(frozen)
        published_profiles.extend(manifest["profiles"])
        manifests.append(
            {
                "batch_id": manifest["batch_id"],
                "batch_ordinal": ordinal,
                "candidate_count": manifest["candidate_count"],
                "frozen_batch_sha256": frozen_hash,
                "manifest_path": manifest_path.relative_to(
                    REPOSITORY
                ).as_posix(),
                "manifest_sha256": sha256(manifest_path.read_bytes()),
                "profile_file_count": manifest["profile_file_count"],
            }
        )

    candidate_ids = [
        profile["candidate_id"] for profile in published_profiles
    ]
    destinations = [
        profile["destination"] for profile in published_profiles
    ]
    profile_paths = [item["path"] for item in published_profile_files]
    frozen_pairs = [
        (item["candidate_id"], item["destination"])
        for item in frozen_candidates
    ]
    published_pairs = list(zip(candidate_ids, destinations))
    if published_pairs != frozen_pairs:
        raise ValueError("A publicação agregada diverge do freeze.")
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("Há sobreposição de candidatos entre lotes.")
    if len(destinations) != len(set(destinations)):
        raise ValueError("Há sobreposição de destinos entre lotes.")
    if len(profile_paths) != len(set(profile_paths)):
        raise ValueError("Há sobreposição de perfis entre lotes.")
    if (len(candidate_ids), len(profile_paths)) != (27, 81):
        raise ValueError("A publicação agregada está incompleta.")

    return {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 223,
        "freeze_issue": 222,
        "cutoff_date": freeze["cutoff_date"],
        "published_on": freeze["cutoff_date"],
        "hash_algorithm": "sha256",
        "freeze_manifest_sha256": sha256(FREEZE_PATH.read_bytes()),
        "batch_count": len(manifests),
        "candidate_count": len(candidate_ids),
        "destination_count": len(destinations),
        "profile_file_count": len(profile_paths),
        "batches": manifests,
        "candidate_ids": candidate_ids,
        "destinations": destinations,
        "profile_paths": profile_paths,
        "profile_files": published_profile_files,
        "integrity": {
            "exactly_three_batches": len(manifests) == 3,
            "exactly_twenty_seven_candidates": len(candidate_ids) == 27,
            "exactly_eighty_one_profiles": len(profile_paths) == 81,
            "candidate_ids_unique": len(candidate_ids)
            == len(set(candidate_ids)),
            "destinations_unique": len(destinations)
            == len(set(destinations)),
            "profile_paths_unique": len(profile_paths)
            == len(set(profile_paths)),
            "freeze_correspondence_exact": published_pairs == frozen_pairs,
            "batch_hashes_match_freeze": all(
                batch["frozen_batch_sha256"]
                == EXPECTED_BATCH_HASHES[batch["batch_ordinal"]]
                for batch in manifests
            ),
            "profile_hashes_match_current_files": True,
            "zero_omissions": len(candidate_ids)
            == freeze["publication"]["eligible_count"],
            "zero_overlaps": len(candidate_ids) == len(set(candidate_ids))
            and len(destinations) == len(set(destinations))
            and len(profile_paths) == len(set(profile_paths)),
        },
        "limitations": (
            "O relatório comprova a publicação completa do universo elegível "
            "congelado no recorte auditado; não prova totalidade do mercado."
        ),
    }


def write_or_check(check: bool) -> int:
    expected = json_bytes(build_report())
    if check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != expected:
            raise ValueError(f"Relatório agregado divergente: {OUTPUT.name}")
        print(f"Relatório agregado verificado: {OUTPUT.name}.")
        return 0
    OUTPUT.write_bytes(expected)
    print(f"Relatório agregado gerado: {OUTPUT.name}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return write_or_check(args.check)


if __name__ == "__main__":
    raise SystemExit(main())
