import os
from contextlib import contextmanager
from pathlib import Path

import libsql_experimental as libsql

from config import DB_PATH

TURSO_URL = os.getenv("TURSO_DB_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")

SCHEMA = """
CREATE TABLE IF NOT EXISTS commits (
    sha          TEXT PRIMARY KEY,
    repo         TEXT NOT NULL,
    author       TEXT NOT NULL,
    message      TEXT NOT NULL,
    committed_at TEXT NOT NULL,
    files        INTEGER,
    additions    INTEGER,
    deletions    INTEGER,
    seen_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS idx_commits_author_date ON commits(author, committed_at DESC);
CREATE INDEX IF NOT EXISTS idx_commits_repo_date   ON commits(repo, committed_at DESC);

CREATE TABLE IF NOT EXISTS run_log (
    started_at TEXT PRIMARY KEY,
    status     TEXT NOT NULL,
    new_count  INTEGER NOT NULL,
    error      TEXT
);
"""


def _make_connection():
    parent = Path(DB_PATH).parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)

    if TURSO_URL:
        return libsql.connect(DB_PATH, sync_url=TURSO_URL, auth_token=TURSO_TOKEN)
    return libsql.connect(DB_PATH)


def init_db() -> None:
    with connect() as conn:
        for stmt in filter(None, (s.strip() for s in SCHEMA.split(";"))):
            conn.execute(stmt)
        conn.commit()


def _safe_sync(conn) -> None:
    try:
        conn.sync()
    except Exception:
        pass


@contextmanager
def connect():
    conn = _make_connection()
    if TURSO_URL:
        _safe_sync(conn)
    yield conn
    conn.commit()
    if TURSO_URL:
        _safe_sync(conn)


def dict_rows(cursor) -> list[dict]:
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]
