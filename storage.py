import logging
from datetime import datetime, timezone
from typing import Iterable

from db import commit_and_sync, dict_rows, get_conn

log = logging.getLogger(__name__)


def has_seen(sha: str) -> bool:
    row = get_conn().execute(
        "SELECT 1 FROM commits WHERE sha = ? LIMIT 1", (sha,)
    ).fetchone()
    return row is not None


def filter_unseen(shas: Iterable[str]) -> set[str]:
    shas = list(shas)
    if not shas:
        return set()
    placeholders = ",".join("?" * len(shas))
    cur = get_conn().execute(
        f"SELECT sha FROM commits WHERE sha IN ({placeholders})", tuple(shas)
    )
    seen = {r["sha"] for r in dict_rows(cur)}
    return set(shas) - seen


def record_commits(commits: list[dict]) -> int:
    if not commits:
        return 0
    rows = [
        (
            c["id"], c["repo"], c["author"], c["message"], c["date"],
            c["files"], c["additions"], c["deletions"],
        )
        for c in commits
    ]
    cur = get_conn().executemany(
        """
        INSERT OR IGNORE INTO commits
            (sha, repo, author, message, committed_at, files, additions, deletions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    commit_and_sync()
    rowcount = cur.rowcount or 0
    log.info("record_commits: attempted %d, rowcount %d", len(rows), rowcount)
    return rowcount


def last_activity_per_dev() -> dict[str, datetime]:
    cur = get_conn().execute(
        "SELECT author, MAX(committed_at) AS last FROM commits GROUP BY author"
    )
    rows = dict_rows(cur)
    return {
        r["author"]: datetime.fromisoformat(r["last"].replace("Z", "+00:00"))
        for r in rows
        if r["last"]
    }


def log_run(started_at: datetime, status: str, new_count: int, error: str | None = None) -> None:
    get_conn().execute(
        "INSERT OR REPLACE INTO run_log (started_at, status, new_count, error) VALUES (?, ?, ?, ?)",
        (started_at.isoformat(), status, new_count, error),
    )
    commit_and_sync()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
