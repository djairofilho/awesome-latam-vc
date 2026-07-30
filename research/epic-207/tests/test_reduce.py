from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


EPIC_ROOT = Path(__file__).resolve().parents[1]


def load_reducer():
    path = EPIC_ROOT / "reduce.py"
    if not path.exists():
        raise AssertionError(
            "research/epic-207/reduce.py ausente; "
            "a implementação funcional da #209 ainda não existe"
        )
    spec = importlib.util.spec_from_file_location("epic_207_reduce", path)
    if spec is None or spec.loader is None:
        raise AssertionError("não foi possível carregar o reducer da epic 207")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Epic207ReducerTests(unittest.TestCase):
    def test_reducer_supports_every_epic_207_jsonl_kind(self) -> None:
        reducer = load_reducer()
        expected = {
            "cvm-queries": "cvm-query-log.jsonl",
            "identity": "identity-resolution.jsonl",
            "reviews": "review-sample.jsonl",
        }
        for kind, filename in expected.items():
            with self.subTest(kind=kind):
                self.assertEqual(filename, reducer.KINDS.get(kind)[0])

    def test_candidate_reduction_is_deterministic_across_creation_order(self) -> None:
        reducer = load_reducer()
        records = [
            {"candidate_id": "fund-zeta", "name": "Zeta"},
            {"candidate_id": "fund-alpha", "name": "Alpha"},
        ]
        outputs: list[str] = []
        for workers in (("worker-z", "worker-a"), ("worker-a", "worker-z")):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "research" / "epic-207"
                for worker, record in zip(workers, records, strict=True):
                    path = root / "brazil" / "shards" / worker / "candidates.jsonl"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(
                        json.dumps(record, separators=(",", ":")) + "\n",
                        encoding="utf-8",
                    )
                destination = root / "brazil" / "candidates.jsonl"
                reducer.reduce_shards(root, "candidates", destination)
                outputs.append(destination.read_text(encoding="utf-8"))

        self.assertEqual(outputs[0], outputs[1])
        self.assertLess(outputs[0].index("fund-alpha"), outputs[0].index("fund-zeta"))

    def test_reducer_rejects_conflicting_records_for_the_same_id(self) -> None:
        reducer = load_reducer()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "research" / "epic-207"
            for worker, name in (("worker-a", "Alpha"), ("worker-b", "Changed")):
                path = root / "brazil" / "shards" / worker / "candidates.jsonl"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(
                        {"candidate_id": "fund-alpha", "name": name},
                        separators=(",", ":"),
                    )
                    + "\n",
                    encoding="utf-8",
                )
            destination = root / "brazil" / "candidates.jsonl"
            with self.assertRaisesRegex(ValueError, "duplicate ID"):
                reducer.reduce_shards(root, "candidates", destination)


if __name__ == "__main__":
    unittest.main()
