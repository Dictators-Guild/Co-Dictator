import time
from github_api import get_all_commits
from analyzer import analyze
from discord_bot import send_to_discord
from storage import load_seen, save_seen
from config import CHECK_INTERVAL

seen_commits = load_seen()

while True:
    print("Checking commits...")

    commits = get_all_commits()
    new_commits = []

    for c in commits:
        if c["id"] not in seen_commits:
            seen_commits.add(c["id"])
            new_commits.append(c)

    if new_commits:
        print(f"Found {len(new_commits)} new commits")

        report = analyze(new_commits)
        send_to_discord(report)

        save_seen(seen_commits)
        print("Report sent")
    else:
        print("No new commits")

    time.sleep(CHECK_INTERVAL)