from datetime import datetime, timezone

from config import INACTIVE_THRESHOLD
from ollama_client import summarize
from storage import last_activity_per_dev


def _group_by_dev(commits: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for c in commits:
        grouped.setdefault(c["author"], []).append(c)
    return grouped


def _inactive(threshold_minutes: int) -> list[tuple[str, int]]:
    now = datetime.now(timezone.utc)
    out: list[tuple[str, int]] = []
    for dev, last in last_activity_per_dev().items():
        minutes = int((now - last).total_seconds() / 60)
        if minutes > threshold_minutes:
            out.append((dev, minutes))
    out.sort(key=lambda x: -x[1])
    return out


def _ai_review(dev: str, commits: list[dict]) -> str | None:
    bullets = "\n".join(
        f"- [{c['repo']}] {c['message'].splitlines()[0]} "
        f"(files: {c['files']}, +{c['additions']}/-{c['deletions']})"
        for c in commits
    )
    prompt = (
        "You are a terse engineering manager. Given these commits by one developer, "
        "in 1-2 sentences flag if the messages match the apparent scope of the changes "
        "(files/lines), or note anything suspicious. No preamble.\n\n"
        f"Developer: {dev}\nCommits:\n{bullets}"
    )
    return summarize(prompt)


def analyze(new_commits: list[dict]) -> str:
    grouped = _group_by_dev(new_commits)
    inactive = _inactive(INACTIVE_THRESHOLD)

    lines: list[str] = ["Developer Activity Report", "=" * 30]

    total = 0
    most_active: tuple[str, int] | None = None

    for dev, dev_commits in sorted(grouped.items(), key=lambda kv: -len(kv[1])):
        count = len(dev_commits)
        total += count
        if most_active is None or count > most_active[1]:
            most_active = (dev, count)

        lines.append(f"\n{dev} ({count} commits)")
        for c in dev_commits:
            lines.append(
                f"- [{c['repo']}] {c['message']} "
                f"(files: {c['files']}, +{c['additions']} / -{c['deletions']})"
            )
        review = _ai_review(dev, dev_commits)
        if review:
            lines.append(f"  AI: {review}")

    if inactive:
        lines.append("\nInactive developers:")
        for dev, minutes in inactive:
            lines.append(f"- {dev}: {minutes} min inactive")

    lines.append("\nTeam Summary:")
    lines.append(f"- Total commits: {total}")
    if most_active:
        lines.append(f"- Most active: {most_active[0]}")

    return "\n".join(lines)
