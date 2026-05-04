from datetime import datetime, timezone
from typing import Iterable

from db import connect, dict_rows


def has_seen(sha: str) -> bool:
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM commits WHERE sha = ? LIMIT 1", (sha,)).fetchone()
        return row is not None


def filter_unseen(shas: Iterable[str]) -> set[str]:
    shas = list(shas)
    if not shas:
        return set()
    with connect() as conn:
        placeholders = ",".join("?" * len(shas))
        cur = conn.execute(
            f"SELECT sha FROM commits WHERE sha IN ({placeholders})", tuple(shas)
        )
        seen = {r["sha"] for r in dict_rows(cur)}
        return set(shas) - seen


def record_commits(commits: list[dict]) -> int:
    if not commits:
        return 0
    with connect() as conn:
        cur = conn.executemany(
            """
            INSERT OR IGNORE INTO commits
                (sha, repo, author, message, committed_at, files, additions, deletions)
            VALUES (:id, :repo, :author, :message, :date, :files, :additions, :deletions)
            """,
            commits,
        )
        return cur.rowcount or 0


def last_activity_per_dev() -> dict[str, datetime]:
    with connect() as conn:
        cur = conn.execute(
            "SELECT author, MAX(committed_at) AS last FROM commits GROUP BY author"
        )
        rows = dict_rows(cur)
    return {
        r["author"]: datetime.fromisoformat(r["last"].replace("Z", "+00:00"))
        for r in rows
        if r["last"]
    }


def log_run(started_at: datetime, status: str, new_count: int, error: str | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO run_log (started_at, status, new_count, error) VALUES (?, ?, ?, ?)",
            (started_at.isoformat(), status, new_count, error),
        )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
