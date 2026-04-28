import ollama
from utils import group_by_developer, get_last_activity, get_inactive_devs
from config import INACTIVE_THRESHOLD

def analyze(commits):
    grouped = group_by_developer(commits)
    last_activity = get_last_activity(commits)
    inactive = get_inactive_devs(last_activity, INACTIVE_THRESHOLD)

    formatted = ""
    for dev, dev_commits in grouped.items():
        formatted += f"\n{dev} ({len(dev_commits)} commits):\n"

        for c in dev_commits:
            formatted += (
                f"- [{c['repo']}] {c['message']} "
                f"(files: {c['files']}, +{c['additions']} / -{c['deletions']})\n"
            )

    inactive_text = ""
    if inactive:
        inactive_text = "\nInactive developers:\n"
        for dev, minutes in inactive:
            inactive_text += f"- {dev}: {minutes} min\n"

    prompt = f"""
You are a strict company assistant.
keep reports short and concise.

{formatted}

{inactive_text}

Analyze developers:
- summarize work
- rate activity
- flag suspicious commits

Then:
- team summary
- most active
- who needs attention

Be direct.
"""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]