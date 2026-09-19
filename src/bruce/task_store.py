from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class Task:
    id: str
    request: str
    status: str
    created_at: str
    updated_at: str


class TaskStore:
    """Small SQLite-backed task journal so interrupted work can be inspected and resumed."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY, request TEXT NOT NULL, status TEXT NOT NULL,
                result TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS task_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
                position INTEGER NOT NULL, tool TEXT NOT NULL, status TEXT NOT NULL,
                output TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
            )""")

    def _connect(self):
        return sqlite3.connect(self.path)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def start(self, request: str) -> str:
        task_id = str(uuid4())
        now = self._now()
        with self._connect() as db:
            db.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)", (task_id, request, "running", "", now, now))
        return task_id

    def step(self, task_id: str, position: int, tool: str, status: str, output: str = "") -> None:
        with self._connect() as db:
            db.execute("INSERT INTO task_steps(task_id, position, tool, status, output, created_at) VALUES (?, ?, ?, ?, ?, ?)", (task_id, position, tool, status, output[:20000], self._now()))

    def finish(self, task_id: str, status: str, result: str) -> None:
        with self._connect() as db:
            db.execute("UPDATE tasks SET status=?, result=?, updated_at=? WHERE id=?", (status, result[:50000], self._now(), task_id))

    def recent(self, limit: int = 10) -> list[Task]:
        with self._connect() as db:
            rows = db.execute("SELECT id, request, status, created_at, updated_at FROM tasks ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [Task(*row) for row in rows]
