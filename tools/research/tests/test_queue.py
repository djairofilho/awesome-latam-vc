from __future__ import annotations

import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from queue import (
    complete,
    enqueue,
    export_jsonl,
    fail,
    import_baseline_into_database,
    init_database,
    lease,
    main,
    requeue_expired,
)


class QueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.database = self.root / "queue.sqlite"
        init_database(self.database)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def test_initializes_wal_and_enqueues_idempotently(self) -> None:
        self.assertTrue(enqueue(self.database, "one", "https://example.com", payload={"á": 1}))
        self.assertFalse(enqueue(self.database, "one", "https://changed.example"))
        with closing(self.connect()) as connection:
            mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
            row = connection.execute("SELECT * FROM tasks").fetchone()
        self.assertEqual(mode, "wal")
        self.assertEqual(row["source_url"], "https://example.com")
        self.assertEqual(json.loads(row["payload"]), {"á": 1})

    def test_leases_by_priority_and_requires_owner_to_complete(self) -> None:
        enqueue(self.database, "low", "https://low.example", priority=1)
        enqueue(self.database, "high", "https://high.example", priority=10)

        task = lease(self.database, "worker-1", seconds=60)

        self.assertEqual(task["task_id"], "high")
        self.assertEqual(task["attempts"], 1)
        with self.assertRaises(ValueError):
            complete(self.database, "high", "worker-2")
        complete(self.database, "high", "worker-1", {"result": "ok"})
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT status, output FROM tasks WHERE task_id = 'high'"
            ).fetchone()
        self.assertEqual(row["status"], "done")
        self.assertEqual(json.loads(row["output"]), {"result": "ok"})

    def test_two_connections_cannot_lease_the_same_task(self) -> None:
        enqueue(self.database, "only", "https://example.com")
        barrier = threading.Barrier(2)
        results = []

        def claim(worker: str) -> None:
            barrier.wait()
            results.append(lease(self.database, worker))

        threads = [
            threading.Thread(target=claim, args=(worker,))
            for worker in ("worker-1", "worker-2")
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        leased = [task for task in results if task is not None]
        self.assertEqual([task["task_id"] for task in leased], ["only"])
        self.assertEqual(results.count(None), 1)

    def test_leases_only_requested_partition(self) -> None:
        enqueue(
            self.database,
            "andean",
            "https://andean.example",
            partition="andean",
            priority=10,
        )
        enqueue(
            self.database,
            "brazil",
            "https://brazil.example",
            partition="brazil",
            priority=1,
        )

        task = lease(self.database, "worker-brazil", partition="brazil")

        self.assertEqual(task["task_id"], "brazil")
        self.assertEqual(task["partition_key"], "brazil")

    def test_fails_and_requeues_expired_leases(self) -> None:
        enqueue(self.database, "failed", "https://failed.example")
        lease(self.database, "worker-1")
        fail(self.database, "failed", "worker-1", "HTTP 500")

        enqueue(self.database, "expired", "https://expired.example")
        lease(self.database, "worker-2", seconds=1)
        future = datetime.now(timezone.utc) + timedelta(seconds=2)
        self.assertEqual(requeue_expired(self.database, now=future), 1)

        with closing(self.connect()) as connection:
            states = dict(connection.execute("SELECT task_id, status FROM tasks"))
        self.assertEqual(states, {"failed": "failed", "expired": "todo"})

    def test_exports_jsonl(self) -> None:
        enqueue(self.database, "one", "https://example.com", payload={"name": "Açaí"})
        destination = self.root / "tasks.jsonl"
        self.assertEqual(export_jsonl(self.database, destination), 1)
        exported = json.loads(destination.read_text(encoding="utf-8"))
        self.assertEqual(exported["payload"], {"name": "Açaí"})

    def test_imports_baseline_without_domain_merging(self) -> None:
        (self.root / "funds").mkdir()
        (self.root / "README.md").write_text(
            "[One](funds/one.md)\n[Two](funds/two.md)\n", encoding="utf-8"
        )
        for filename, name in (("one.md", "One"), ("two.md", "Two")):
            (self.root / "funds" / filename).write_text(
                f"# {name}\n- **Website:** https://shared.example/{filename}\n",
                encoding="utf-8",
            )

        self.assertEqual(import_baseline_into_database(self.database, self.root), 2)
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT profile_path, domain FROM baseline_funds ORDER BY profile_path"
            ).fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual({row["domain"] for row in rows}, {"shared.example"})

    def test_cli_reads_payload_and_output_from_utf8_files(self) -> None:
        payload_file = self.root / "payload.json"
        output_file = self.root / "output.json"
        payload_file.write_text('{"nome": "Açaí"}', encoding="utf-8")
        output_file.write_text('{"resultado": "concluído"}', encoding="utf-8")

        self.assertEqual(
            main(
                [
                    "--db",
                    str(self.database),
                    "enqueue",
                    "cli-task",
                    "https://example.com",
                    "--payload-file",
                    str(payload_file),
                ]
            ),
            0,
        )
        lease(self.database, "worker-cli")
        self.assertEqual(
            main(
                [
                    "--db",
                    str(self.database),
                    "complete",
                    "cli-task",
                    "worker-cli",
                    "--output-file",
                    str(output_file),
                ]
            ),
            0,
        )

        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT payload, output FROM tasks WHERE task_id = 'cli-task'"
            ).fetchone()
        self.assertEqual(json.loads(row["payload"]), {"nome": "Açaí"})
        self.assertEqual(json.loads(row["output"]), {"resultado": "concluído"})


if __name__ == "__main__":
    unittest.main()
