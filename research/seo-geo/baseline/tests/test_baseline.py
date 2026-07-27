from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("seo_geo_baseline_validate", ROOT / "validate.py")
assert SPEC and SPEC.loader
VALIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATE)


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.queries = VALIDATE.load_jsonl(ROOT / "queries.jsonl")
        cls.kpis = VALIDATE.load_jsonl(ROOT / "kpis.jsonl")
        cls.manifest = json.loads(
            (ROOT / "run-manifest.json").read_text(encoding="utf-8")
        )
        cls.state = json.loads(
            (ROOT / "repository-state.json").read_text(encoding="utf-8")
        )

    def test_complete_bundle(self) -> None:
        VALIDATE.main()

    def test_locale_distribution_is_exact(self) -> None:
        counts = {
            locale: sum(row["locale"] == locale for row in self.queries)
            for locale in VALIDATE.LOCALES
        }
        self.assertEqual(counts, {"en": 10, "pt-BR": 10, "es": 10})

    def test_required_intents_are_covered(self) -> None:
        self.assertEqual(
            {row["intent"] for row in self.queries},
            VALIDATE.INTENTS,
        )

    def test_project_absence_is_scoped_as_sample(self) -> None:
        named = [row for row in self.queries if row["intent"] == "project_name"]
        self.assertEqual(len(named), 3)
        for row in named:
            self.assertFalse(row["project_url_found"])
            self.assertIn(
                "absence_does_not_prove_not_indexed",
                row["limitations"],
            )

    def test_kpis_separate_readiness_from_outcomes(self) -> None:
        technical = [row for row in self.kpis if row["group"] == "technical"]
        observed = [row for row in self.kpis if row["group"] == "observed"]
        self.assertTrue(all(row["target_kind"] == "internal_readiness" for row in technical))
        self.assertTrue(all(row["target_kind"] == "observed_outcome" for row in observed))

    def test_no_site_is_recorded_as_observation(self) -> None:
        self.assertFalse(self.state["github_pages"]["configured"])
        self.assertFalse(self.state["site_implementation"]["package_json_present"])
        self.assertFalse(self.state["site_implementation"]["astro_config_present"])
        self.assertFalse(self.state["site_implementation"]["pages_workflow_present"])

    def test_repeat_contract_requires_versioned_append(self) -> None:
        instructions = " ".join(self.manifest["repeat"]["instructions"]).lower()
        self.assertIn("append", instructions)
        self.assertIn("do not overwrite", instructions)


if __name__ == "__main__":
    unittest.main()
