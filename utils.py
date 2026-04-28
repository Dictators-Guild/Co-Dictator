from datetime import datetime, timezone

def group_by_developer(commits):
    devs = {}
    for c in commits:
        devs.setdefault(c["author"], []).append(c)
    return devs


def get_last_activity(commits):
    last = {}

    for c in commits:
        dev = c["author"]
        t = datetime.fromisoformat(c["date"].replace("Z", "+00:00"))

        if dev not in last or t > last[dev]:
            last[dev] = t

    return last


def get_inactive_devs(last_activity, threshold_minutes):
    now = datetime.now(timezone.utc)
    inactive = []

    for dev, last_time in last_activity.items():
        minutes = (now - last_time).total_seconds() / 60

        if minutes > threshold_minutes:
            inactive.append((dev, int(minutes)))

    return inactive