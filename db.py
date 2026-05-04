import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import DB_PATH

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


def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, isolation_level=None, timeout=30.0)
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        yield conn
    finally:
        conn.close()
