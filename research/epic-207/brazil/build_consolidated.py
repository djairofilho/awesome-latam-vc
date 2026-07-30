"""Build the canonical Brazil funds discovery bundle for issue #216."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


EPIC_ROOT = Path(__file__).resolve().parents[1]
BRAZIL = Path(__file__).resolve().parent
REPO_ROOT = EPIC_ROOT.parents[1]
CUTOFF_DATE = "2026-07-30"
DISCOVERY_WORKERS = (
    "worker-210-allocators",
    "worker-211-rounds",
    "worker-212-launches",
    "worker-213-events",
    "worker-214-maps",
    "worker-215-foreign-access",
)
CORE_JSONL = (
    "source-inventory.jsonl",
    "candidates.jsonl",
    "evidence.jsonl",
    "identity-resolution.jsonl",
    "coverage-matrix.jsonl",
    "cvm-query-log.jsonl",
    "review-sample.jsonl",
)
GENERATED = (
    *CORE_JSONL,
    "run-manifest.jsonl",
    "audit-report.json",
    "validation-shards/issue-217/candidates.jsonl",
    "validation-shards/issue-218/candidates.jsonl",
    "validation-shards/issue-219/candidates.jsonl",
    "validation-shards/manifest.json",
    "consolidation-summary.json",
)
ID_FIELDS = {
    "source-inventory.jsonl": "source_id",
    "candidates.jsonl": "candidate_id",
    "evidence.jsonl": "evidence_id",
    "coverage-matrix.jsonl": "coverage_id",
}
EXACT_DUPLICATE_DESTINATIONS = {
    "fund-br-213-canary": "fund-br-210-canary",
    "fund-br-213-sororite-ventures": "fund-br-sororite-ventures",
}
REDISCOVERY_SOURCE_LINKS = {
    "fund-br-17-sigma": ("src-fund-br-215-pass1-17sigma-official",),
    "fund-br-1616v": ("src-fund-br-215-pass1-1616-official",),
    "fund-br-firestreak-ventures": (
        "src-fund-br-215-pass1-firestreak-official",
    ),
    "fund-br-210-quona-capital": (
        "src-fund-br-215-pass1-quona-contact",
        "src-fund-br-215-pass1-quona-portfolio",
    ),
    "fund-br-mundi-ventures-latam": (
        "src-fund-br-215-pass1-mundi-first-close",
    ),
}
POST_BASELINE_GUARDS = {
    "funds/brazil/entrypoint.md": "Entrypoint",
    "funds/multi-country/flourish-ventures.md": "Flourish Ventures",
}
FREEZE_MANIFEST = BRAZIL / "freeze-manifest.json"


def compact_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def jsonl_bytes(records: Iterable[dict[str, Any]]) -> bytes:
    rows = [compact_json(record) for record in records]
    return (("\n".join(rows) + "\n") if rows else "").encode("utf-8")


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            raise ValueError(f"{path}:{line_number}: linha JSONL vazia")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: registro deve ser objeto")
        records.append(value)
    return records


def _shard_records(filename: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: dict[str, Path] = {}
    id_field = ID_FIELDS[filename]
    for worker in DISCOVERY_WORKERS:
        path = BRAZIL / "shards" / worker / filename
        for record in read_jsonl(path):
            record_id = record[id_field]
            if record_id in seen:
                raise ValueError(
                    f"{filename}: ID {record_id} duplicado em "
                    f"{seen[record_id]} e {path}"
                )
            seen[record_id] = path
            records.append(record)
    return sorted(records, key=lambda record: record[id_field])


def _normalized_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_value = decomposed.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.casefold()).strip()


def _id_segment(value: str) -> str:
    return value.replace("_", "-")


def _sorted_union(*values: Iterable[str]) -> list[str]:
    return sorted({item for group in values for item in group}, key=str.casefold)


def _candidate_index(
    candidates: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {record["candidate_id"]: record for record in candidates}


def _assert_known_internal_collisions(
    candidates: list[dict[str, Any]],
) -> None:
    signal_members: dict[tuple[str, str], set[str]] = defaultdict(set)
    for candidate in candidates:
        candidate_id = candidate["candidate_id"]
        for name in (candidate["name"], *candidate["aliases"]):
            signal_members[("name", _normalized_name(name))].add(candidate_id)
        for field in ("canonical_domain", "brand_id", "manager_id"):
            if candidate.get(field):
                signal_members[(field, candidate[field])].add(candidate_id)
        for field in ("vehicle_ids", "program_ids"):
            for value in candidate[field]:
                signal_members[(field, value)].add(candidate_id)
    collision_pairs = {
        tuple(sorted(members))
        for members in signal_members.values()
        if len(members) > 1
    }
    expected_pairs = {
        tuple(sorted((duplicate_id, canonical_id)))
        for duplicate_id, canonical_id in EXACT_DUPLICATE_DESTINATIONS.items()
    }
    if collision_pairs != expected_pairs:
        raise ValueError(
            "colisões internas não adjudicadas: "
            f"esperadas={sorted(expected_pairs)}, atuais={sorted(collision_pairs)}"
        )


def _apply_identity_destinations(
    candidates: list[dict[str, Any]],
    source_ids: set[str],
) -> list[dict[str, Any]]:
    result = [dict(record) for record in candidates]
    index = _candidate_index(result)
    for duplicate_id, canonical_id in EXACT_DUPLICATE_DESTINATIONS.items():
        duplicate = index[duplicate_id]
        canonical = index[canonical_id]
        duplicate["canonical_candidate_id"] = canonical_id
        duplicate["canonical_profile"] = None
        canonical["aliases"] = _sorted_union(
            canonical["aliases"], duplicate["aliases"]
        )
        canonical["vehicle_ids"] = _sorted_union(
            canonical["vehicle_ids"], duplicate["vehicle_ids"]
        )
        canonical["program_ids"] = _sorted_union(
            canonical["program_ids"], duplicate["program_ids"]
        )
        canonical["discovery_source_ids"] = _sorted_union(
            canonical["discovery_source_ids"],
            duplicate["discovery_source_ids"],
        )
        canonical["official_evidence_ids"] = _sorted_union(
            canonical["official_evidence_ids"],
            duplicate["official_evidence_ids"],
        )
    for candidate_id, rediscovery_ids in REDISCOVERY_SOURCE_LINKS.items():
        missing = set(rediscovery_ids) - source_ids
        if missing:
            raise ValueError(
                f"{candidate_id}: fontes de redescoberta ausentes: {sorted(missing)}"
            )
        candidate = index[candidate_id]
        candidate["discovery_source_ids"] = _sorted_union(
            candidate["discovery_source_ids"], rediscovery_ids
        )
    return sorted(result, key=lambda record: record["candidate_id"])


def _candidate_evidence(
    evidence: list[dict[str, Any]],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for record in evidence:
        result[record["candidate_id"]].append(record["evidence_id"])
    return {
        candidate_id: sorted(evidence_ids)
        for candidate_id, evidence_ids in result.items()
    }


def _resolution(
    resolution_id: str,
    subject_ids: list[str],
    canonical_candidate_id: str | None,
    resolution: str,
    reason: str,
    candidates: dict[str, dict[str, Any]],
    evidence_by_candidate: dict[str, list[str]],
    *,
    brand_id: str | None = None,
    manager_id: str | None = None,
    vehicle_ids: list[str] | None = None,
) -> dict[str, Any]:
    anchor = candidates[canonical_candidate_id or subject_ids[0]]
    return {
        "schema_version": "1.0",
        "resolution_id": resolution_id,
        "subject_ids": sorted(subject_ids),
        "canonical_candidate_id": canonical_candidate_id,
        "brand_id": anchor.get("brand_id") if brand_id is None else brand_id,
        "manager_id": (
            anchor.get("manager_id") if manager_id is None else manager_id
        ),
        "vehicle_ids": sorted(
            anchor.get("vehicle_ids", [])
            if vehicle_ids is None
            else vehicle_ids
        ),
        "resolution": resolution,
        "reason": reason,
        "evidence_ids": sorted(
            {
                evidence_id
                for candidate_id in subject_ids
                for evidence_id in evidence_by_candidate.get(candidate_id, [])
            }
        ),
        "resolved_on": CUTOFF_DATE,
        "resolver": "issue-216-identity-reducer",
    }


def build_identity_resolutions(
    candidates: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    index = _candidate_index(candidates)
    evidence_by_candidate = _candidate_evidence(evidence)
    rows = [
        _resolution(
            "identity-fund-br-canary-shards-210-213",
            ["fund-br-210-canary", "fund-br-213-canary"],
            "fund-br-210-canary",
            "same_identity",
            (
                "Nome, domínio, marca e gestora coincidem; o ID do shard #213 "
                "é redescoberta do candidato #210, que já aponta ao perfil "
                "funds/regional/canary.md."
            ),
            index,
            evidence_by_candidate,
        ),
        _resolution(
            "identity-fund-br-sororite-shards-212-213",
            [
                "fund-br-sororite-ventures",
                "fund-br-213-sororite-ventures",
            ],
            "fund-br-sororite-ventures",
            "same_identity",
            (
                "Nome, domínio, marca, gestora e vehicle-sororite-fund-1 "
                "coincidem; o ID do shard #213 é redescoberta do candidato #212."
            ),
            index,
            evidence_by_candidate,
        ),
    ]
    profile_matches = {
        "fund-br-210-valor-capital-group": "funds/multi-country/valor-capital-group.md",
        "fund-br-210-monashees": "funds/regional/monashees.md",
        "fund-br-210-sp-ventures": "funds/regional/sp-ventures.md",
        "fund-br-210-quona-capital": "funds/multi-country/quona-capital.md",
        "fund-br-213-caravela-capital": "funds/regional/caravela-capital.md",
        "fund-br-213-triaxis-capital": "funds/brazil/triaxis-capital.md",
        "fund-br-213-astella": "funds/brazil/astella.md",
    }
    for candidate_id, profile in sorted(profile_matches.items()):
        rows.append(
            _resolution(
                f"identity-{candidate_id}-baseline-profile",
                [candidate_id],
                candidate_id,
                "same_identity",
                (
                    f"Nome e domínio coincidem com o perfil congelado {profile}; "
                    "a linha permanece na fila para decisão posterior e não cria "
                    "novo perfil."
                ),
                index,
                evidence_by_candidate,
            )
        )
    rows.extend(
        [
            _resolution(
                "identity-fund-br-dna-capital-manager-vehicle",
                ["fund-br-210-dna-capital"],
                "fund-br-210-dna-capital",
                "distinct_vehicle",
                (
                    "DNA Capital é a organização candidata e DNA Capital VC II "
                    "permanece vehicle-dna-capital-vc-ii. A memória anterior "
                    "cand-dna-capital-vc-ii já apontava ao gestor "
                    "cand-dna-capital; o veículo não foi unido como organização."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-vinci-prior-managers",
                ["fund-br-213-vinci-partners"],
                None,
                "unresolved",
                (
                    "O domínio vincipartners.com colide com "
                    "cand-vinci-capital-gestora-de-recursos-ltda e "
                    "cand-vinci-gestora. A fonte de evento não resolve plataforma, "
                    "gestora e veículo; o candidato segue para revisão manual."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-primus-sul-ventures",
                ["fund-br-213-primus-ventures"],
                "fund-br-213-primus-ventures",
                "distinct_vehicle",
                (
                    "Primus Ventures permanece a organização do perfil publicado; "
                    "FIP Sul Ventures é memória de veículo distinta e não foi "
                    "fundida automaticamente à gestora."
                ),
                index,
                evidence_by_candidate,
                vehicle_ids=[],
            ),
            _resolution(
                "identity-fund-br-nido-brand",
                ["fund-br-nido-vc"],
                "fund-br-nido-vc",
                "brand_alias",
                (
                    "Nido e NidoVC são nomes da mesma marca; Platypus não é alias "
                    "organizacional e permanece vehicle-nido-platypus."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-nido-platypus",
                ["fund-br-nido-vc"],
                "fund-br-nido-vc",
                "distinct_vehicle",
                (
                    "Platypus permanece veículo separado da organização Nido; "
                    "nenhuma atividade do fundo de fundos é convertida "
                    "automaticamente em investimento direto da organização."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-jatoba-brand",
                ["fund-br-214-jatoba-impacto-amazonia"],
                "fund-br-214-jatoba-impacto-amazonia",
                "brand_alias",
                (
                    "Jatobá Gestora é a organização; Jatobá Impacto Amazônia e "
                    "Fundo Impacto Amazônia são nomes associados ao veículo."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-jatoba-impacto-amazonia-vehicle",
                ["fund-br-214-jatoba-impacto-amazonia"],
                "fund-br-214-jatoba-impacto-amazonia",
                "distinct_vehicle",
                (
                    "vehicle-jatoba-impacto-amazonia permanece separado da "
                    "gestora; estruturação pública não comprova operação do veículo."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-lh-tech-ventures",
                ["fund-br-214-lh-invest"],
                "fund-br-214-lh-invest",
                "distinct_vehicle",
                (
                    "LH Invest permanece a organização e LH Tech Ventures o "
                    "vehicle-lh-tech-ventures; gestor e veículo não foram unidos."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-accion-venture-lab",
                ["fund-br-accion-ventures"],
                "fund-br-accion-ventures",
                "brand_alias",
                (
                    "Accion Venture Lab é preservado como alias histórico de "
                    "Accion Ventures, operada por Accion Impact Management; a "
                    "gestora permanece entidade separada."
                ),
                index,
                evidence_by_candidate,
            ),
            _resolution(
                "identity-fund-br-prosus-naspers",
                ["fund-br-prosus-ventures"],
                "fund-br-prosus-ventures",
                "brand_alias",
                (
                    "Naspers Ventures é alias histórico preservado de Prosus "
                    "Ventures; não foi criado segundo candidato para a marca antiga."
                ),
                index,
                evidence_by_candidate,
            ),
        ]
    )
    return sorted(rows, key=lambda record: record["resolution_id"])


def _canonical_candidate_id(candidate_id: str) -> str:
    return EXACT_DUPLICATE_DESTINATIONS.get(candidate_id, candidate_id)


def build_coverage(
    source_inventory: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    source_index = {record["source_id"]: record for record in source_inventory}
    raw_rows = _shard_records("coverage-matrix.jsonl")
    cells: dict[tuple[str, str], dict[str, Any]] = {}
    for row in raw_rows:
        grouped_sources: dict[str, list[str]] = defaultdict(list)
        for source_id in row["source_ids"]:
            grouped_sources[source_index[source_id]["source_family"]].append(source_id)
        for family, source_ids in grouped_sources.items():
            key = (family, row["geography_scope"])
            cell = cells.setdefault(
                key,
                {
                    "source_ids": set(),
                    "planned_sources": 0,
                    "completed_sources": 0,
                    "candidate_ids": set(),
                    "raw_coverage_ids": [],
                },
            )
            cell["source_ids"].update(source_ids)
            cell["planned_sources"] += len(source_ids)
            cell["completed_sources"] += sum(
                source_index[source_id]["result"] == "complete"
                for source_id in source_ids
            )
            cell["raw_coverage_ids"].append(row["coverage_id"])
            for candidate_id in row["candidate_ids"]:
                candidate_sources = set(
                    _candidate_index(candidates)[candidate_id][
                        "discovery_source_ids"
                    ]
                )
                if candidate_sources.intersection(source_ids):
                    cell["candidate_ids"].add(
                        _canonical_candidate_id(candidate_id)
                    )
    for candidate in candidates:
        for source_id in candidate["discovery_source_ids"]:
            source = source_index[source_id]
            matching_keys = [
                key
                for key, cell in cells.items()
                if source_id in cell["source_ids"]
            ]
            for key in matching_keys:
                cells[key]["candidate_ids"].add(
                    _canonical_candidate_id(candidate["candidate_id"])
                )
    rows: list[dict[str, Any]] = []
    for (family, geography), cell in sorted(cells.items()):
        complete = cell["completed_sources"] == cell["planned_sources"]
        status = "complete" if complete else "gap_justified"
        incomplete = sorted(
            source_id
            for source_id in cell["source_ids"]
            if source_index[source_id]["result"] != "complete"
        )
        reason = (
            None
            if complete
            else (
                "Fontes não concluídas preservadas do inventário: "
                + ", ".join(incomplete)
                + "."
            )
        )
        rows.append(
            {
                "schema_version": "1.0",
                "coverage_id": (
                    "coverage-fund-br-216-"
                    f"{_id_segment(family)}-{_id_segment(geography)}"
                ),
                "issue": 216,
                "source_family": family,
                "geography_scope": geography,
                "source_ids": sorted(cell["source_ids"]),
                "planned_sources": cell["planned_sources"],
                "completed_sources": cell["completed_sources"],
                "candidate_ids": sorted(cell["candidate_ids"]),
                "status": status,
                "reason": reason,
                "owner": None if complete else "issue-216-consolidator",
                "next_action": (
                    None
                    if complete
                    else "Usar as lacunas registradas nas fontes durante a validação."
                ),
            }
        )
    return rows


def _profile_name(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    closing = lines.index("---", 1)
    return json.loads("\n".join(lines[1:closing]))["name"]


def frozen_publication_paths() -> set[str]:
    if not FREEZE_MANIFEST.is_file():
        return set()
    manifest = json.loads(FREEZE_MANIFEST.read_text(encoding="utf-8"))
    return {
        candidate["destination"]
        for batch in manifest["publication"]["batches"]
        for candidate in batch["candidates"]
    }


def guarded_catalog_delta_paths(
    baseline: set[str],
    current: set[str],
    published: set[str],
) -> set[str]:
    delta = current - baseline - published
    if delta != set(POST_BASELINE_GUARDS):
        raise ValueError(
            "delta pós-baseline inesperado: "
            f"esperado={sorted(POST_BASELINE_GUARDS)}, atual={sorted(delta)}"
        )
    return delta


def current_catalog_delta() -> list[dict[str, Any]]:
    baseline = {
        record["profile_path"]
        for record in read_jsonl(
            EPIC_ROOT / "baseline" / "catalog-baseline.jsonl"
        )
    }
    current = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "funds").rglob("*.md")
        if path.name != "README.md"
    }
    delta = guarded_catalog_delta_paths(
        baseline,
        current,
        frozen_publication_paths(),
    )
    rows = []
    for relative in sorted(delta):
        path = REPO_ROOT / relative
        name = _profile_name(path)
        if name != POST_BASELINE_GUARDS[relative]:
            raise ValueError(
                f"{relative}: nome pós-baseline inesperado: {name}"
            )
        rows.append(
            {
                "profile_path": relative,
                "name": name,
                "profile_sha256": sha256(path.read_bytes()),
                "treatment": "already_published_guard_only",
                "candidate_created": False,
                "included_in_validation_shards": False,
            }
        )
    return rows


def assignment_modulo(candidate_id: str) -> int:
    digest = hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()
    return int(digest, 16) % 3


def build_validation_shards(
    candidates: list[dict[str, Any]],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    by_modulo: dict[int, list[dict[str, Any]]] = {0: [], 1: [], 2: []}
    for candidate in candidates:
        by_modulo[assignment_modulo(candidate["candidate_id"])].append(candidate)
    artifacts: dict[str, bytes] = {}
    queues = []
    for modulo in range(3):
        issue = 217 + modulo
        records = sorted(
            by_modulo[modulo], key=lambda record: record["candidate_id"]
        )
        relative = f"validation-shards/issue-{issue}/candidates.jsonl"
        content = jsonl_bytes(records)
        artifacts[relative] = content
        queues.append(
            {
                "issue": issue,
                "modulo": modulo,
                "candidate_count": len(records),
                "candidate_ids": [
                    record["candidate_id"] for record in records
                ],
                "artifact": (
                    "research/epic-207/brazil/" + relative
                ),
                "sha256": sha256(content),
            }
        )
    manifest = {
        "schema_version": "1.0",
        "algorithm": "int(sha256(candidate_id), 16) % 3",
        "candidate_count": len(candidates),
        "queues": queues,
        "generated_on": CUTOFF_DATE,
    }
    artifacts["validation-shards/manifest.json"] = json_bytes(manifest)
    return artifacts, manifest


def _run_manifest(artifact_hashes: dict[str, str]) -> list[dict[str, Any]]:
    tasks = [
        (210, "allocators", "worker-210-allocators"),
        (211, "rounds", "worker-211-rounds"),
        (212, "launches", "worker-212-launches"),
        (213, "events", "worker-213-events"),
        (214, "sector_maps", "worker-214-maps"),
        (214, "regional_sources", "worker-214-maps"),
        (215, "foreign_access", "worker-215-foreign-access"),
    ]
    rows: list[dict[str, Any]] = [
        {
            "schema_version": "1.0",
            "record_type": "run",
            "run_id": "run-fund-br-207",
            "issues": list(range(210, 220)),
            "contract_issue": 208,
            "cutoff_date": CUTOFF_DATE,
            "created_on": CUTOFF_DATE,
            "status": "running",
            "task_count": 10,
            "coordinator": "issue-216-consolidator",
            "scraping_performed": False,
            "hash_algorithm": "sha256",
            "artifact_hashes": artifact_hashes,
            "notes": (
                "Issue #216 consolidated discovery only. Entrypoint and "
                "Flourish Ventures are post-baseline published guards and are "
                "not candidates or validation-shard members."
            ),
        }
    ]
    for issue, family, worker in tasks:
        rows.append(
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": "run-fund-br-207",
                "task_id": (
                    f"task-fund-br-{issue}-{_id_segment(family)}"
                ),
                "issue": issue,
                "phase": "discovery",
                "source_family": family,
                "research_channel": "non_cvm",
                "worker_id": worker,
                "shard_path": f"research/epic-207/brazil/shards/{worker}",
                "status": "done",
                "reason": None,
                "owner": worker,
                "next_action": None,
            }
        )
    for modulo in range(3):
        issue = 217 + modulo
        worker = f"worker-{issue}-validation"
        rows.append(
            {
                "schema_version": "1.0",
                "record_type": "task",
                "run_id": "run-fund-br-207",
                "task_id": f"task-fund-br-{issue}-validation-{modulo}",
                "issue": issue,
                "phase": "validation",
                "source_family": "official_portfolios",
                "research_channel": "non_cvm",
                "worker_id": worker,
                "shard_path": f"research/epic-207/brazil/shards/{worker}",
                "status": "todo",
                "reason": None,
                "owner": worker,
                "next_action": (
                    f"Validar os candidatos com sha256(candidate_id) % 3 = "
                    f"{modulo}."
                ),
            }
        )
    return rows


def build_artifacts() -> dict[str, bytes]:
    sources = _shard_records("source-inventory.jsonl")
    source_ids = {record["source_id"] for record in sources}
    raw_candidates = _shard_records("candidates.jsonl")
    _assert_known_internal_collisions(raw_candidates)
    evidence = _shard_records("evidence.jsonl")
    candidates = _apply_identity_destinations(
        raw_candidates, source_ids
    )
    identities = build_identity_resolutions(candidates, evidence)
    coverage = build_coverage(sources, candidates)
    post_baseline = current_catalog_delta()

    artifacts: dict[str, bytes] = {
        "source-inventory.jsonl": jsonl_bytes(sources),
        "candidates.jsonl": jsonl_bytes(candidates),
        "evidence.jsonl": jsonl_bytes(evidence),
        "identity-resolution.jsonl": jsonl_bytes(identities),
        "coverage-matrix.jsonl": jsonl_bytes(coverage),
        "cvm-query-log.jsonl": b"",
        "review-sample.jsonl": b"",
    }
    validation_artifacts, validation_manifest = build_validation_shards(
        candidates
    )
    artifacts.update(validation_artifacts)
    canonical_count = sum(
        candidate.get("canonical_candidate_id") is None
        and candidate.get("decision") != "duplicate"
        for candidate in candidates
    )
    decision_counts = Counter(
        candidate["decision"]
        for candidate in candidates
        if candidate["decision"] is not None
    )
    audit = {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 216,
        "cutoff_date": CUTOFF_DATE,
        "status": "running",
        "canonical_candidate_count": canonical_count,
        "cvm_consulted_candidate_count": 0,
        "cvm_query_rate": 0,
        "non_cvm_task_share": 1,
        "decision_counts": dict(sorted(decision_counts.items())),
        "limitations": [
            "A issue #216 resolve identidade e não decide elegibilidade.",
            (
                "Entrypoint e Flourish Ventures foram publicados após o baseline; "
                "são guardas de catálogo e não entram como candidatos nem serão "
                "republicados."
            ),
            (
                "O schema de evidence não possui source_id; vínculos entre fonte "
                "e evidência permanecem inferíveis por URL, título e publicador."
            ),
            (
                "Clusters marcados unresolved ou distinct_vehicle exigem revisão "
                "sem fusão automática de gestora, marca e veículo."
            ),
        ],
        "generated_on": CUTOFF_DATE,
    }
    artifacts["audit-report.json"] = json_bytes(audit)
    core_hashes = {
        filename: sha256(artifacts[filename]) for filename in CORE_JSONL
    }
    artifacts["run-manifest.jsonl"] = jsonl_bytes(
        _run_manifest(core_hashes)
    )
    source_results = Counter(record["result"] for record in sources)
    evidence_classes = Counter(
        record["source_class"] for record in evidence
    )
    summary = {
        "schema_version": "1.0",
        "epic": 207,
        "issue": 216,
        "cutoff_date": CUTOFF_DATE,
        "input_workers": list(DISCOVERY_WORKERS),
        "raw_counts": {
            "sources": len(sources),
            "candidates": len(raw_candidates),
            "evidence": len(evidence),
            "coverage_rows": sum(
                len(
                    read_jsonl(
                        BRAZIL / "shards" / worker / "coverage-matrix.jsonl"
                    )
                )
                for worker in DISCOVERY_WORKERS
            ),
        },
        "canonical_counts": {
            "sources": len(sources),
            "candidate_rows": len(candidates),
            "canonical_identities": canonical_count,
            "evidence": len(evidence),
            "identity_resolutions": len(identities),
            "coverage_cells": len(coverage),
        },
        "source_result_counts": dict(sorted(source_results.items())),
        "evidence_class_counts": dict(sorted(evidence_classes.items())),
        "exact_duplicate_destinations": dict(
            sorted(EXACT_DUPLICATE_DESTINATIONS.items())
        ),
        "baseline_profile_matches": {
            "candidate_rows": sum(
                candidate["canonical_profile"] is not None
                for candidate in raw_candidates
            ),
            "unique_profiles": len(
                {
                    candidate["canonical_profile"]
                    for candidate in raw_candidates
                    if candidate["canonical_profile"] is not None
                }
            ),
            "profile_paths": sorted(
                {
                    candidate["canonical_profile"]
                    for candidate in raw_candidates
                    if candidate["canonical_profile"] is not None
                }
            ),
        },
        "post_baseline_catalog_delta": post_baseline,
        "validation_shards": validation_manifest["queues"],
        "core_artifact_hashes": core_hashes,
        "generated_on": CUTOFF_DATE,
    }
    artifacts["consolidation-summary.json"] = json_bytes(summary)
    return artifacts


def write_or_check(artifacts: dict[str, bytes], check: bool) -> int:
    mismatches: list[str] = []
    for relative in GENERATED:
        expected = artifacts[relative]
        path = BRAZIL / relative
        if check:
            if not path.is_file():
                mismatches.append(f"ausente: {relative}")
            elif path.read_bytes() != expected:
                mismatches.append(f"divergente: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if check and mismatches:
        raise ValueError(
            "artefatos canônicos divergentes: " + ", ".join(mismatches)
        )
    return len(artifacts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Falha quando qualquer artefato difere da geração determinística.",
    )
    args = parser.parse_args()
    artifacts = build_artifacts()
    count = write_or_check(artifacts, args.check)
    action = "verificados" if args.check else "gerados"
    print(f"Artefatos canônicos {action}: {count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
