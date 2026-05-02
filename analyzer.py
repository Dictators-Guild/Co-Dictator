from utils import group_by_developer, get_last_activity, get_inactive_devs
from config import INACTIVE_THRESHOLD


def analyze(commits):
    grouped = group_by_developer(commits)
    last_activity = get_last_activity(commits)
    inactive = get_inactive_devs(last_activity, INACTIVE_THRESHOLD)

    report = "Developer Activity Report\n"
    report += "=" * 30 + "\n"

    total_commits = 0
    most_active_dev = None
    most_active_count = 0

    for dev, dev_commits in grouped.items():
        commit_count = len(dev_commits)
        total_commits += commit_count

        if commit_count > most_active_count:
            most_active_count = commit_count
            most_active_dev = dev

        report += f"\n{dev} ({commit_count} commits)\n"

        for c in dev_commits:
            report += (
                f"- [{c['repo']}] {c['message']} "
                f"(files: {c['files']}, +{c['additions']} / -{c['deletions']})\n"
            )

    if inactive:
        report += "\nInactive developers:\n"
        for dev, minutes in inactive:
            report += f"- {dev}: {minutes} min inactive\n"

    report += "\nTeam Summary:\n"
    report += f"- Total commits: {total_commits}\n"

    if most_active_dev:
        report += f"- Most active: {most_active_dev}\n"

    return report