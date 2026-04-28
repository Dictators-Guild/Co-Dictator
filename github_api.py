import requests
import time
from config import GITHUB_HEADERS

def get_all_repos():
    url = "https://api.github.com/user/repos"
    response = requests.get(url, headers=GITHUB_HEADERS)

    if response.status_code == 403:
        print("Rate limit hit. Sleeping...")
        time.sleep(600)
        return []

    data = response.json()
    if not isinstance(data, list):
        print("GitHub error:", data)
        return []

    return [repo["full_name"] for repo in data]


def get_commit_details(repo, sha):
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    response = requests.get(url, headers=GITHUB_HEADERS)

    if response.status_code != 200:
        return None

    return response.json()


def analyze_diff(commit_data):
    files = commit_data.get("files", [])

    return {
        "files_changed": len(files),
        "additions": sum(f.get("additions", 0) for f in files),
        "deletions": sum(f.get("deletions", 0) for f in files)
    }


def get_all_commits():
    repos = get_all_repos()
    all_commits = []

    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/commits"
        response = requests.get(url, headers=GITHUB_HEADERS)

        if response.status_code != 200:
            continue

        data = response.json()
        if not isinstance(data, list):
            continue

        for c in data[:2]:
            details = get_commit_details(repo, c["sha"])
            if not details:
                continue

            diff = analyze_diff(details)

            author = None

            if c.get("author") and c["author"].get("login"):

                author = c["author"]["login"]
            else:
                author = c["commit"]["author"]["name"]  # fallback

            all_commits.append({
                "id": c["sha"],
                "repo": repo,
                "author": author,
                "message": c["commit"]["message"],
                "date": c["commit"]["author"]["date"],
                "files": diff["files_changed"],
                "additions": diff["additions"],
                "deletions": diff["deletions"]
                })

    return all_commits