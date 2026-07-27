"""Publica deterministicamente os 26 perfis congelados da issue #78."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[2]
MANIFEST_PATH = (
    REPOSITORY
    / "research"
    / "epic-62"
    / "independent-review"
    / "publishable-manifest.json"
)
EXPECTED_MANIFEST_HASH = (
    "52da16cfc931aa3c1a1304dbee575a7b805e0db03ca2f96a75e5f4c79604adc2"
)
CUTOFF = "2026-07-27"
BRANCH = "agent/issue-78-accelerators-publication"

BATCH_ISSUES = {
    "batch-01": {
        "number": 155,
        "url": "https://github.com/djairofilho/awesome-latam-vc/issues/155",
    },
    "batch-02": {
        "number": 156,
        "url": "https://github.com/djairofilho/awesome-latam-vc/issues/156",
    },
    "batch-03": {
        "number": 157,
        "url": "https://github.com/djairofilho/awesome-latam-vc/issues/157",
    },
}

OPERATOR_NAMES = {
    "500.co": "500 Global",
    "aceventures.com.br": "ACE Ventures",
    "alchemistaccelerator.com": "Alchemist Accelerator",
    "aws.amazon.com": "Amazon Web Services",
    "boost.do": "Boost",
    "ccb.org.co": "Cámara de Comercio de Bogotá",
    "centev.ufv.br": "tecnoPARQ / CENTEV-UFV",
    "darwinstartups.com": "Darwin Startups",
    "fi.co": "Founder Institute",
    "google.com": "Google for Startups",
    "gridexponential.com": "GRIDX",
    "grupoboticario.com.br": "Grupo Boticário",
    "inovativa.online": "InovAtiva",
    "magicalstartups.com": "Magical Startups",
    "parallel18.com": "Parallel18",
    "sebrae.com.br": "Sebrae Rio de Janeiro",
    "seedstars.com": "Seedstars",
    "skydeck.berkeley.edu": "Berkeley SkyDeck",
    "startup.google.com": "Google for Startups",
    "theganeshalab.com": "The Ganesha Lab",
    "utecventures.com": "UTEC Ventures",
    "ventiur.net": "Ventiur",
    "wow.ac": "WOW",
    "ycombinator.com": "Y Combinator",
}

COUNTRY_LABELS = {
    "argentina": "Argentina",
    "brazil": "Brazil",
    "chile": "Chile",
    "colombia": "Colombia",
    "dominican-republic": "Dominican Republic",
    "mexico": "Mexico",
    "peru": "Peru",
    "puerto-rico": "Puerto Rico",
    "switzerland": "Switzerland",
    "united-states": "United States",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_batches() -> list[dict]:
    batches = []
    pattern = re.compile(
        r"^\| `(accel-[^`]+)` \| `([^`]+)` \|$",
        re.MULTILINE,
    )
    for path in sorted((ROOT / "batches").glob("batch-*.md")):
        batch_id = path.stem
        rows = pattern.findall(path.read_text(encoding="utf-8"))
        issue = BATCH_ISSUES[batch_id]
        batches.append(
            {
                "batch_id": batch_id,
                "owner": "djairofilho",
                "branch": BRANCH,
                "sub_issue": issue["number"],
                "sub_issue_url": issue["url"],
                "body_path": path.relative_to(REPOSITORY).as_posix(),
                "body_sha256": sha256(path),
                "candidate_ids": [candidate_id for candidate_id, _ in rows],
                "profile_paths": [profile_path for _, profile_path in rows],
                "profile_count": len(rows),
            }
        )
    return batches


def normalized_value(value: object) -> str:
    if value is None:
        return "Not publicly disclosed"
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    mapping = {
        "not_publicly_disclosed": "Not publicly disclosed",
        "not_applicable": "Not applicable",
        "closed_between_cycles": "Closed between cycles",
        "closed": "Closed",
        "open": "Open",
        "active": "Active",
        "unknown": "Not publicly disclosed",
    }
    if isinstance(value, str):
        return mapping.get(value, value)
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "Not publicly disclosed"
    return str(value)


def source_markdown(record: dict) -> str:
    title = record["title"].replace("[", "").replace("]", "")
    return f"- [{title}]({record['url']})"


def unique_sources(records: list[dict]) -> list[dict]:
    """Keep the first occurrence of each official URL in review order."""
    seen_urls: set[str] = set()
    unique = []
    for record in records:
        if record["url"] in seen_urls:
            continue
        seen_urls.add(record["url"])
        unique.append(record)
    return unique


def vehicle_text(candidate: dict, review: dict) -> str:
    vehicle_id = candidate.get("investment_vehicle_id")
    relationships = [
        item
        for item in review.get("catalog_relationships", [])
        if item.get("catalog") == "funds"
        and item.get("relationship") in {
            "programa-e-veículo-distintos",
            "unidades-distintas",
        }
    ]
    if not vehicle_id and not relationships:
        return "No separate qualifying investment vehicle identified"
    parts = []
    if vehicle_id:
        parts.append(vehicle_id)
    destinations = sorted(
        {item["destination"] for item in relationships if item.get("destination")}
    )
    if destinations:
        parts.append("catalog relationship: " + ", ".join(destinations))
    return "Separate from the program: " + "; ".join(parts)


def activity_text(candidate: dict, evidence: list[dict], review: dict) -> str:
    dates = sorted(
        {
            item["published_on"]
            for item in evidence
            if item.get("published_on")
        },
        reverse=True,
    )
    if candidate["candidate_id"] == "accel-ventiur-acelera-impacto":
        return (
            "The independent review confirmed the official 2025 selection and "
            "nine-month program calendar."
        )
    if dates:
        return (
            f"Official evidence dated {dates[0]} confirms activity inside the "
            "24-month review window."
        )
    return (
        "The frozen independent review confirmed current official activity "
        f"with outcome `{review['outcome']}`."
    )


def profile_text(
    candidate: dict,
    review: dict,
    evidence: list[dict],
) -> str:
    operator = OPERATOR_NAMES.get(candidate["operator_id"], candidate["operator_id"])
    aliases = ", ".join(candidate["aliases"]) or "None published"
    apply = (
        candidate["application_url"]
        or f"Closed; monitor {candidate['official_site']}"
    )
    activity_status = (
        "Active"
        if review["resolved_decision"] == "elegível"
        else normalized_value(candidate["activity_status"])
    )
    source_lines = "\n".join(
        source_markdown(item) for item in unique_sources(evidence)
    )
    vehicle = vehicle_text(candidate, review)
    geography = normalized_value(candidate["accepted_geography"])
    return f"""# {candidate['name']}

- **Website:** {candidate['official_site']}
- **Operator:** {operator}
- **Program type:** {normalized_value(candidate['entity_type'])}
- **Open to external founders:** {normalized_value(candidate['open_to_external_founders'])}
- **Activity status:** {activity_status}
- **Application status:** {normalized_value(candidate['application_status'])}
- **Program format:** {normalized_value(candidate['program_format'])}
- **Duration:** {normalized_value(candidate['duration'])}
- **Stage:** {normalized_value(candidate['stage'])}
- **Capital offered:** {normalized_value(candidate['capital_offered'])}
- **Instrument:** {normalized_value(candidate['instrument'])}
- **Equity:** {normalized_value(candidate['equity'])}
- **Geography:** {geography}
- **Apply:** {apply}
- **Aliases:** {aliases}
- **Investment vehicle:** {vehicle}

## Program profile

{candidate['name']} is a structured acceleration program operated by
{operator}. The program record is distinct from its operator and from any
investment vehicle listed above.

## Eligibility and application

The frozen review confirms external founder access and Latin American
eligibility. Published geography: {geography}. Application status is
{normalized_value(candidate['application_status']).lower()}.

## Activity signals

{activity_text(candidate, evidence, review)}

## Sources

{source_lines}

**Last verified:** {CUTOFF}
"""


def build_index(profiles: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in profiles:
        country = Path(item["profile_path"]).parts[2]
        grouped[country].append(item)
    sections = []
    for country in sorted(grouped, key=lambda item: COUNTRY_LABELS[item]):
        links = "\n".join(
            f"- [{item['name']}]({Path(item['profile_path']).relative_to('ecosystem/accelerators').as_posix()})"
            for item in sorted(grouped[country], key=lambda row: row["candidate_id"])
        )
        sections.append(f"## {COUNTRY_LABELS[country]}\n\n{links}")
    return f"""# Accelerators

This category covers active, structured acceleration programs that accept
startups from Latin America but do not replace qualifying recurring investment
vehicles in the main fund catalog.

Programs and their operators or investment vehicles remain separate units.
Capital, instrument, equity, duration and stage are reported only when official
sources publish them.

The 26 profiles below were frozen by the independent review of epic #62 and
verified on {CUTOFF}.

{(chr(10) * 2).join(sections)}
"""


def main() -> None:
    actual_manifest_hash = sha256(MANIFEST_PATH)
    if actual_manifest_hash != EXPECTED_MANIFEST_HASH:
        raise ValueError(
            "publishable-manifest divergiu do freeze: "
            f"{actual_manifest_hash} != {EXPECTED_MANIFEST_HASH}"
        )
    frozen = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    batches = parse_batches()
    batch_ids = [
        candidate_id
        for batch in batches
        for candidate_id in batch["candidate_ids"]
    ]
    if batch_ids != frozen["candidate_ids"]:
        raise ValueError("lotes divergem da ordem e cobertura do manifesto")
    if len(batches) != 3 or any(
        batch["profile_count"] < 1 or batch["profile_count"] > 10
        for batch in batches
    ):
        raise ValueError("particionamento de lotes inválido")

    candidates = {
        item["candidate_id"]: item
        for item in read_jsonl(
            REPOSITORY / "research/epic-62/consolidation/candidates.jsonl"
        )
    }
    reviews = {
        item["candidate_id"]: item
        for item in json.loads(
            (
                REPOSITORY
                / "research/epic-62/independent-review/review-results.json"
            ).read_text(encoding="utf-8")
        )
    }
    evidence = {
        item["evidence_id"]: item
        for item in read_jsonl(
            REPOSITORY / "research/epic-62/consolidation/evidence.jsonl"
        )
    }
    review_evidence = {
        item["evidence_id"]: item
        for item in json.loads(
            (
                REPOSITORY
                / "research/epic-62/independent-review/review-evidence.json"
            ).read_text(encoding="utf-8")
        )
    }
    evidence.update(review_evidence)

    path_by_id = {
        candidate_id: profile_path
        for batch in batches
        for candidate_id, profile_path in zip(
            batch["candidate_ids"],
            batch["profile_paths"],
            strict=True,
        )
    }
    profiles = []
    for candidate_id in frozen["candidate_ids"]:
        candidate = candidates[candidate_id]
        review = reviews[candidate_id]
        if review["resolved_decision"] != "elegível":
            raise ValueError(f"candidato não elegível no freeze: {candidate_id}")
        linked_evidence = [
            evidence[evidence_id]
            for evidence_id in review["official_evidence_ids"]
        ]
        if not linked_evidence or any(
            item["source_type"] != "official" for item in linked_evidence
        ):
            raise ValueError(f"evidência não oficial em {candidate_id}")
        profile_path = path_by_id[candidate_id]
        destination = REPOSITORY / profile_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            profile_text(candidate, review, linked_evidence),
            encoding="utf-8",
            newline="\n",
        )
        profiles.append(
            {
                "candidate_id": candidate_id,
                "name": candidate["name"],
                "profile_path": profile_path,
                "profile_sha256": sha256(destination),
                "official_evidence_ids": review["official_evidence_ids"],
                "investment_vehicle_id": candidate.get("investment_vehicle_id"),
                "aliases": candidate["aliases"],
            }
        )

    index_path = REPOSITORY / "ecosystem/accelerators/README.md"
    index_path.write_text(
        build_index(profiles),
        encoding="utf-8",
        newline="\n",
    )

    batch_manifest = {
        "schema_version": "1.0",
        "issue": 78,
        "source_issue": 77,
        "source_manifest": MANIFEST_PATH.relative_to(REPOSITORY).as_posix(),
        "source_manifest_sha256": actual_manifest_hash,
        "batch_count": len(batches),
        "candidate_count": len(batch_ids),
        "batches": batches,
    }
    dump_json(ROOT / "frozen-batches.json", batch_manifest)

    publication_manifest = {
        "schema_version": "1.0",
        "issue": 78,
        "contract_issue": 68,
        "cutoff_date": CUTOFF,
        "status": "completed",
        "source_manifest_sha256": actual_manifest_hash,
        "candidate_count": len(profiles),
        "batch_count": len(batches),
        "profiles_created": len(profiles),
        "decision_filter": ["elegível"],
        "profiles": profiles,
        "output_hashes": {
            "ecosystem/accelerators/README.md": sha256(index_path),
            "research/epic-62/publication/frozen-batches.json": sha256(
                ROOT / "frozen-batches.json"
            ),
            **{
                item["profile_path"]: item["profile_sha256"]
                for item in profiles
            },
        },
        "indexes": [
            "ecosystem/accelerators/README.md",
            "ecosystem/README.md",
            "README.md",
            "README.pt.md",
            "README.es.md",
        ],
    }
    dump_json(ROOT / "publication-manifest.json", publication_manifest)

    hashed = [
        "ecosystem/accelerators/README.md",
        *(item["profile_path"] for item in profiles),
        "research/epic-62/publication/frozen-batches.json",
        "research/epic-62/publication/publication-manifest.json",
    ]
    (ROOT / "sha256sums.txt").write_text(
        "".join(f"{sha256(REPOSITORY / path)}  {path}\n" for path in hashed),
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
