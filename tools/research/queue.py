"""SQLite-backed task queue for parallel research workers."""

from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

try:
    from .normalize import import_baseline
except ImportError:  # Allow `python tools/research/queue.py`.
    from normalize import import_baseline


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    issue INTEGER,
    source_url TEXT NOT NULL,
    partition_key TEXT NOT NULL DEFAULT '',
    priority INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'todo'
        CHECK (status IN ('todo', 'leased', 'done', 'failed')),
    worker TEXT,
    lease_until TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    payload TEXT NOT NULL DEFAULT '{}',
    output TEXT,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS tasks_claim
    ON tasks(status, priority DESC, created_at, task_id);

CREATE TABLE IF NOT EXISTS baseline_funds (
    profile_path TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    website TEXT NOT NULL,
    domain TEXT NOT NULL,
    aliases TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS baseline_domain ON baseline_funds(domain);
"""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def timestamp(value: datetime | None = None) -> str:
    return (value or utc_now()).isoformat(timespec="microseconds")


def connect(database: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(str(database), timeout=30, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 30000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database(database: str | Path) -> None:
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as connection:
        connection.executescript(SCHEMA)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _task_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    result = dict(row)
    for field in ("payload", "output"):
        if result[field] is not None:
            result[field] = json.loads(result[field])
    return result


def enqueue(
    database: str | Path,
    task_id: str,
    source_url: str,
    *,
    issue: int | None = None,
    partition: str = "",
    priority: int = 0,
    payload: Any = None,
) -> bool:
    """Insert a task once. Return False when task_id already exists."""

    now = timestamp()
    with closing(connect(database)) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO tasks (
                task_id, issue, source_url, partition_key, priority, payload,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                issue,
                source_url,
                partition,
                priority,
                _json({} if payload is None else payload),
                now,
                now,
            ),
        )
        return cursor.rowcount == 1


def lease(
    database: str | Path,
    worker: str,
    *,
    seconds: int = 900,
    issue: int | None = None,
    partition: str | None = None,
) -> dict[str, Any] | None:
    """Atomically claim the highest-priority available task."""

    if seconds <= 0:
        raise ValueError("lease seconds must be positive")
    now_value = utc_now()
    now = timestamp(now_value)
    until = timestamp(now_value + timedelta(seconds=seconds))
    connection = connect(database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        query = "SELECT task_id FROM tasks WHERE status = 'todo'"
        parameters: list[Any] = []
        if issue is not None:
            query += " AND issue = ?"
            parameters.append(issue)
        if partition is not None:
            query += " AND partition_key = ?"
            parameters.append(partition)
        query += " ORDER BY priority DESC, created_at, task_id LIMIT 1"
        candidate = connection.execute(query, parameters).fetchone()
        if candidate is None:
            connection.commit()
            return None
        connection.execute(
            """
            UPDATE tasks
            SET status = 'leased', worker = ?, lease_until = ?,
                attempts = attempts + 1, updated_at = ?
            WHERE task_id = ? AND status = 'todo'
            """,
            (worker, until, now, candidate["task_id"]),
        )
        row = connection.execute(
            "SELECT * FROM tasks WHERE task_id = ?", (candidate["task_id"],)
        ).fetchone()
        connection.commit()
        return _task_dict(row)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _finish_lease(
    database: str | Path,
    task_id: str,
    worker: str,
    status: str,
    *,
    output: Any = None,
    error: str | None = None,
) -> None:
    with closing(connect(database)) as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = ?, output = ?, last_error = ?, worker = NULL,
                lease_until = NULL, updated_at = ?
            WHERE task_id = ? AND status = 'leased' AND worker = ?
            """,
            (
                status,
                None if output is None else _json(output),
                error,
                timestamp(),
                task_id,
                worker,
            ),
        )
        if cursor.rowcount != 1:
            raise ValueError(f"task {task_id!r} is not leased by {worker!r}")


def complete(database: str | Path, task_id: str, worker: str, output: Any = None) -> None:
    _finish_lease(database, task_id, worker, "done", output=output)


def fail(database: str | Path, task_id: str, worker: str, error: str) -> None:
    _finish_lease(database, task_id, worker, "failed", error=error)


def requeue_expired(database: str | Path, *, now: datetime | None = None) -> int:
    with closing(connect(database)) as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = 'todo', worker = NULL, lease_until = NULL,
                updated_at = ?
            WHERE status = 'leased' AND lease_until <= ?
            """,
            (timestamp(now), timestamp(now)),
        )
        return cursor.rowcount


def iter_tasks(database: str | Path) -> Iterator[dict[str, Any]]:
    with closing(connect(database)) as connection:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY created_at, task_id"
        ).fetchall()
    for row in rows:
        task = _task_dict(row)
        assert task is not None
        yield task


def export_jsonl(database: str | Path, destination: str | Path) -> int:
    count = 0
    with Path(destination).open("w", encoding="utf-8", newline="\n") as output:
        for task in iter_tasks(database):
            output.write(json.dumps(task, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def import_baseline_into_database(database: str | Path, root: str | Path) -> int:
    funds = import_baseline(root)
    with closing(connect(database)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            connection.execute("DELETE FROM baseline_funds")
            connection.executemany(
                """
                INSERT INTO baseline_funds (
                    profile_path, name, website, domain, aliases
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(profile_path) DO UPDATE SET
                    name = excluded.name,
                    website = excluded.website,
                    domain = excluded.domain,
                    aliases = excluded.aliases
                """,
                [
                    (
                        fund.profile_path,
                        fund.name,
                        fund.website,
                        fund.domain,
                        _json(fund.aliases),
                    )
                    for fund in funds
                ],
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
    return len(funds)


def parse_json(value: str | None, default: Any = None) -> Any:
    return default if value is None else json.loads(value)


def parse_json_input(
    value: str | None,
    file_path: str | None,
    default: Any = None,
) -> Any:
    if file_path is not None:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))
    return parse_json(value, default)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=".work/epic-16/research.sqlite")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init", help="initialize or migrate the database")

    enqueue_parser = commands.add_parser("enqueue", help="enqueue one task idempotently")
    enqueue_parser.add_argument("task_id")
    enqueue_parser.add_argument("source_url")
    enqueue_parser.add_argument("--issue", type=int)
    enqueue_parser.add_argument("--partition", default="")
    enqueue_parser.add_argument("--priority", type=int, default=0)
    enqueue_payload = enqueue_parser.add_mutually_exclusive_group()
    enqueue_payload.add_argument("--payload", help="JSON payload")
    enqueue_payload.add_argument(
        "--payload-file",
        help="UTF-8 JSON file, preferred for PowerShell and Windows",
    )

    lease_parser = commands.add_parser("lease", help="atomically lease one task")
    lease_parser.add_argument("worker")
    lease_parser.add_argument("--seconds", type=int, default=900)
    lease_parser.add_argument("--issue", type=int)
    lease_parser.add_argument("--partition")

    complete_parser = commands.add_parser("complete", help="complete a leased task")
    complete_parser.add_argument("task_id")
    complete_parser.add_argument("worker")
    complete_output = complete_parser.add_mutually_exclusive_group()
    complete_output.add_argument("--output", help="JSON output")
    complete_output.add_argument(
        "--output-file",
        help="UTF-8 JSON file, preferred for PowerShell and Windows",
    )

    fail_parser = commands.add_parser("fail", help="fail a leased task")
    fail_parser.add_argument("task_id")
    fail_parser.add_argument("worker")
    fail_parser.add_argument("error")

    commands.add_parser("requeue-expired", help="requeue expired leases")

    export_parser = commands.add_parser("export", help="export all tasks as JSONL")
    export_parser.add_argument("destination")

    baseline_parser = commands.add_parser(
        "import-baseline", help="import README-linked fund profiles"
    )
    baseline_parser.add_argument("--root", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        init_database(args.db)
        print(args.db)
        return 0

    init_database(args.db)
    if args.command == "enqueue":
        inserted = enqueue(
            args.db,
            args.task_id,
            args.source_url,
            issue=args.issue,
            partition=args.partition,
            priority=args.priority,
            payload=parse_json_input(args.payload, args.payload_file, {}),
        )
        print(json.dumps({"inserted": inserted, "task_id": args.task_id}))
    elif args.command == "lease":
        print(
            json.dumps(
                lease(
                    args.db,
                    args.worker,
                    seconds=args.seconds,
                    issue=args.issue,
                    partition=args.partition,
                ),
                ensure_ascii=False,
            )
        )
    elif args.command == "complete":
        complete(
            args.db,
            args.task_id,
            args.worker,
            parse_json_input(args.output, args.output_file),
        )
    elif args.command == "fail":
        fail(args.db, args.task_id, args.worker, args.error)
    elif args.command == "requeue-expired":
        print(requeue_expired(args.db))
    elif args.command == "export":
        print(export_jsonl(args.db, args.destination))
    elif args.command == "import-baseline":
        print(import_baseline_into_database(args.db, args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
