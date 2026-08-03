import importlib.util
import json
from pathlib import Path


EPIC = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "validate_review_1", EPIC / "review" / "validate_review_1.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_review_1_contract_and_completeness():
    assert VALIDATOR.validate() == []


def test_required_corrections_are_requested():
    results = {
        row["candidate_id"]: row
        for row in load_jsonl(EPIC / "review" / "results" / "review-1.jsonl")
    }
    assert results["delta-fund-creas"]["final_decision"] == "excluded"
    assert results["delta-fund-yellow-hub"]["review_status"] == "changes_requested"
    assert results["delta-fund-struck-capital"]["review_status"] == "changes_requested"
    assert all(
        results[candidate_id]["evidence_ids"]
        for candidate_id in (
            "delta-fund-creas",
            "delta-fund-yellow-hub",
            "delta-fund-struck-capital",
        )
    )
