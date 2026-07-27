#!/usr/bin/env python3
"""Validate the reproducible SEO/GEO baseline bundle for issue #108."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
LOCALES = {"en", "pt-BR", "es"}
INTENTS = {
    "broad_discovery",
    "country",
    "stage",
    "sector",
    "organization_type",
    "project_name",
}
REQUIRED_QUERY_FIELDS = {
    "id",
    "query",
    "language",
    "locale",
    "intent",
    "country",
    "stage",
    "sector",
    "organization_type",
    "mechanism",
    "provider",
    "location",
    "measured_on",
    "result_state",
    "project_url_found",
    "observed_url",
    "limitations",
}
REQUIRED_KPI_FIELDS = {
    "id",
    "group",
    "definition",
    "source",
    "frequency",
    "unit",
    "baseline_value",
    "baseline_state",
    "target_kind",
    "result_kind",
}
TECHNICAL_KPIS = {
    "valid_urls",
    "indexable_pages",
    "sitemap_coverage",
    "canonical_coverage",
    "translation_completeness",
    "structured_data_coverage",
}
OBSERVED_KPIS = {
    "indexed_pages",
    "observed_queries",
    "impressions",
    "clicks",
    "generative_presence",
    "generative_citations",
}


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            raise AssertionError(f"{path.name}:{line_number}: blank line")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path.name}:{line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise AssertionError(f"{path.name}:{line_number}: expected object")
        rows.append(value)
    return rows


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_queries(rows: list[dict], cutoff: str) -> None:
    assert len(rows) == 30, f"expected 30 queries, got {len(rows)}"
    assert len({row["id"] for row in rows}) == len(rows), "duplicate query IDs"
    assert len({(row["locale"], row["query"]) for row in rows}) == len(rows), (
        "duplicate query within locale"
    )

    locale_counts = Counter(row["locale"] for row in rows)
    assert locale_counts == Counter({"en": 10, "pt-BR": 10, "es": 10}), locale_counts
    assert {row["intent"] for row in rows} == INTENTS

    for row in rows:
        assert set(row) == REQUIRED_QUERY_FIELDS, row["id"]
        assert row["language"] == row["locale"]
        assert row["locale"] in LOCALES
        assert row["intent"] in INTENTS
        assert row["query"].strip() == row["query"] and row["query"]
        assert row["organization_type"]
        assert row["mechanism"] == "web_search_sample"
        assert row["provider"]
        assert row["measured_on"] == cutoff
        date.fromisoformat(row["measured_on"])
        assert isinstance(row["project_url_found"], bool)
        assert row["limitations"]
        assert "returned_result_sample_not_total_index" in row["limitations"]

        if row["project_url_found"]:
            assert row["result_state"] == "project_result_observed"
            assert row["observed_url"] and is_http_url(row["observed_url"])
        elif row["intent"] == "project_name":
            assert row["result_state"] == "no_matching_project_result_observed"
            assert row["observed_url"] is None
            assert "absence_does_not_prove_not_indexed" in row["limitations"]
        else:
            assert row["result_state"] == "results_returned_project_not_observed"
            assert row["observed_url"] and is_http_url(row["observed_url"])

    for locale in LOCALES:
        localized = [row for row in rows if row["locale"] == locale]
        assert any(row["intent"] == "project_name" for row in localized)
        assert any(row["country"] for row in localized)
        assert any(row["stage"] for row in localized)
        assert any(row["sector"] for row in localized)
        assert any(row["organization_type"] != "project" for row in localized)


def validate_kpis(rows: list[dict]) -> None:
    assert len({row["id"] for row in rows}) == len(rows), "duplicate KPI IDs"
    by_group = {
        group: {row["id"] for row in rows if row["group"] == group}
        for group in {"technical", "observed"}
    }
    assert by_group["technical"] == TECHNICAL_KPIS
    assert by_group["observed"] == OBSERVED_KPIS

    for row in rows:
        assert set(row) == REQUIRED_KPI_FIELDS, row["id"]
        for field in ("definition", "source", "frequency", "unit"):
            assert isinstance(row[field], str) and row[field].strip(), (row["id"], field)
        if row["group"] == "technical":
            assert row["target_kind"] == "internal_readiness"
            assert row["result_kind"] == "observed_technical"
        else:
            assert row["target_kind"] == "observed_outcome"
            assert row["result_kind"] in {
                "real_external_result",
                "non_deterministic_sample",
            }


def validate_repository_state(state: dict, cutoff: str) -> None:
    assert state["captured_on"] == cutoff
    assert state["visibility"] == "public"
    assert state["default_branch"] == "main"
    assert state["repository_url"] == "https://github.com/djairofilho/awesome-latam-vc"
    assert state["github_pages"]["configured"] is False
    assert "HTTP 404" in state["github_pages"]["evidence"]
    implementation = state["site_implementation"]
    assert implementation["package_json_present"] is False
    assert implementation["astro_config_present"] is False
    assert implementation["pages_workflow_present"] is False
    assert len(state["snapshot_commit"]) == 40
    assert len(state["public_surfaces"]) >= 4
    assert all(is_http_url(item["url"]) for item in state["public_surfaces"])


def validate_manifest(manifest: dict, queries: list[dict]) -> None:
    assert manifest["schema_version"] == "1.0"
    assert manifest["issue"] == 108
    assert manifest["query_count"] == len(queries)
    assert manifest["queries_per_locale"] == {"en": 10, "pt-BR": 10, "es": 10}
    assert manifest["project_url_observed_count"] == sum(
        row["project_url_found"] for row in queries
    )
    assert manifest["measurement"]["rank_tracking"] is False
    assert manifest["measurement"]["generative_answers_measured"] is False
    assert len(manifest["repeat"]["instructions"]) >= 6
    limitations = " ".join(manifest["limitations"]).lower()
    assert "not prove" in limitations
    assert "not traffic" in limitations


def main() -> None:
    queries = load_jsonl(ROOT / "queries.jsonl")
    kpis = load_jsonl(ROOT / "kpis.jsonl")
    manifest = json.loads((ROOT / "run-manifest.json").read_text(encoding="utf-8"))
    state = json.loads((ROOT / "repository-state.json").read_text(encoding="utf-8"))
    json.loads((ROOT / "measurement.schema.json").read_text(encoding="utf-8"))

    cutoff = manifest["cutoff_date"]
    validate_queries(queries, cutoff)
    validate_kpis(kpis)
    validate_repository_state(state, cutoff)
    validate_manifest(manifest, queries)
    print(
        "SEO/GEO baseline valid: "
        f"{len(queries)} queries, {len(kpis)} KPIs, cutoff {cutoff}."
    )


if __name__ == "__main__":
    main()
