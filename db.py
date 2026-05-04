import logging
import os
from pathlib import Path

import libsql_experimental as libsql

from config import DB_PATH

log = logging.getLogger(__name__)

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

_conn = None


def _build_connection():
    parent = Path(DB_PATH).parent
    if str(parent) not in ("", "."):
        parent.mkdir(parents=True, exist_ok=True)

    if TURSO_URL:
        log.info("Connecting to Turso (%s) with local replica at %s", TURSO_URL, DB_PATH)
        return libsql.connect(DB_PATH, sync_url=TURSO_URL, auth_token=TURSO_TOKEN)
    log.info("Connecting to local SQLite at %s", DB_PATH)
    return libsql.connect(DB_PATH)


def get_conn():
    global _conn
    if _conn is None:
        _conn = _build_connection()
        if TURSO_URL:
            _conn.sync()
    return _conn


def init_db() -> None:
    conn = get_conn()
    for stmt in filter(None, (s.strip() for s in SCHEMA.split(";"))):
        conn.execute(stmt)
    conn.commit()
    if TURSO_URL:
        conn.sync()


def commit_and_sync() -> None:
    conn = get_conn()
    conn.commit()
    if TURSO_URL:
        conn.sync()


def dict_rows(cursor) -> list[dict]:
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return [dict(zip(cols, row)) for row in cursor.fetchall()]
