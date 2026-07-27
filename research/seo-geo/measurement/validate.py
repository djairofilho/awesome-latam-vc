#!/usr/bin/env python3
"""Validate the public, credential-free measurement contract for issue #119."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
BASELINE = ROOT.parent / "baseline"
PROPERTY_URL = "https://djairofilho.github.io/awesome-latam-vc/"
SITEMAP_URL = f"{PROPERTY_URL}sitemap.xml"
PROVIDERS = {"google_search_console", "bing_webmaster_tools"}
CHECKPOINTS = {"d30": 30, "d60": 60, "d90": 90}
FORBIDDEN_KEYS = {
    "api_key",
    "access_token",
    "refresh_token",
    "client_secret",
    "password",
    "email",
    "cookie",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), f"{path.name}: expected an object"
    return value


def walk(value: object, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            assert key.lower() not in FORBIDDEN_KEYS, f"{path}.{key}: forbidden field"
            walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk(child, f"{path}[{index}]")


def http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate_status(status: dict) -> None:
    assert status["schema_version"] == "1.0"
    assert status["property_url"] == PROPERTY_URL
    assert status["sitemap_url"] == SITEMAP_URL
    assert http_url(status["robots_url"])
    assert set(status["providers"]) == PROVIDERS
    assert all(code == 200 for code in status["public_endpoints"].values())
    assert status["privacy"] == {
        "analytics": False,
        "tracking_pixels": False,
        "visitor_cookies": False,
        "credential_values_committed": False,
    }
    expected_sitemap_status = {
        "google_search_console": "not_submitted_property_not_configured",
        "bing_webmaster_tools": "not_submitted_no_authenticated_session",
    }
    expected_browser_status = {
        "google_search_console": "authenticated_property_not_configured",
        "bing_webmaster_tools": "not_authenticated",
    }
    for provider_id, provider in status["providers"].items():
        assert provider["verification_method"] == "html_meta_tag"
        assert provider["repository_variable"].endswith("_SITE_VERIFICATION")
        assert provider["verification_status"] == "pending_authenticated_owner"
        assert provider["sitemap_status"] == expected_sitemap_status[provider_id]
        assert provider["connector_status"] == "specific_connector_unavailable"
        assert provider["browser_session_status"] == (
            expected_browser_status[provider_id]
        )
        assert provider["required_manual_action"]


def validate_cadence(cadence: dict) -> None:
    assert cadence["launch_date"] is None
    actual = {
        checkpoint["id"]: checkpoint["offset_days"]
        for checkpoint in cadence["checkpoints"]
    }
    assert actual == CHECKPOINTS
    assert cadence["overwrite_previous_runs"] is False
    assert set(cadence["required_outputs"]) == {
        "run.json",
        "query-results.jsonl",
        "generative-samples.jsonl",
    }


def validate_template(template: dict) -> None:
    assert template["property_url"] == PROPERTY_URL
    assert template["sitemap_url"] == SITEMAP_URL
    assert set(template["providers"]) == PROVIDERS
    assert template["period"]["timezone"] == "UTC"
    assert template["baseline_query_rerun"] == {
        "source": "../baseline/queries.jsonl",
        "expected_query_count": 30,
        "results_file": "query-results.jsonl",
        "preserve_query_text_locale_and_intent": True,
    }
    required_metrics = {
        "indexed_pages",
        "observed_queries",
        "impressions",
        "clicks",
        "countries",
        "devices",
    }
    for provider in template["providers"].values():
        assert required_metrics <= set(provider)
    required_generative = {
        "query_id",
        "measured_on",
        "language",
        "mechanism",
        "provider",
        "location",
        "project_present",
        "project_cited",
        "observed_url",
        "limitations",
    }
    assert set(template["generative_measurement"]["required_fields"]) == (
        required_generative
    )
    assert template["privacy"] == {
        "contains_personal_data": False,
        "contains_credentials": False,
        "analytics_or_cookie_data": False,
    }


def validate_baseline_reference() -> None:
    queries = [
        json.loads(line)
        for line in (BASELINE / "queries.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    assert len(queries) == 30
    assert len({row["id"] for row in queries}) == 30
    assert {row["locale"] for row in queries} == {"en", "pt-BR", "es"}
    json.loads((BASELINE / "measurement.schema.json").read_text(encoding="utf-8"))


def main() -> None:
    status = load(ROOT / "provider-status.json")
    cadence = load(ROOT / "cadence.json")
    template = load(ROOT / "run-template.json")
    for document in (status, cadence, template):
        walk(document)
    validate_status(status)
    validate_cadence(cadence)
    validate_template(template)
    validate_baseline_reference()
    print("SEO/GEO measurement contract valid: 2 providers, 30 queries, d30/d60/d90.")


if __name__ == "__main__":
    main()
