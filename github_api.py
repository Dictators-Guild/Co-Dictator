import logging
import time

import requests

from config import GITHUB_HEADERS

log = logging.getLogger(__name__)

API = "https://api.github.com"
COMMITS_PER_REPO = 10


def _get(url: str, params: dict | None = None) -> requests.Response | None:
    try:
        response = requests.get(url, headers=GITHUB_HEADERS, params=params, timeout=15)
    except requests.RequestException as exc:
        log.warning("GitHub request failed: %s (%s)", url, exc)
        return None

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(response.headers.get("X-RateLimit-Reset", "0"))
        wait = max(0, reset - int(time.time()))
        log.warning("GitHub rate limit hit, resets in %ds — skipping cycle", wait)
        return None

    if response.status_code != 200:
        log.warning("GitHub %s -> %d: %s", url, response.status_code, response.text[:200])
        return None

    return response


def get_all_repos() -> list[str]:
    repos: list[str] = []
    page = 1
    while True:
        response = _get(f"{API}/user/repos", params={"per_page": 100, "page": page})
        if response is None:
            break
        data = response.json()
        if not isinstance(data, list) or not data:
            break
        repos.extend(repo["full_name"] for repo in data)
        if len(data) < 100:
            break
        page += 1

    return repos


def get_commit_details(repo: str, sha: str) -> dict | None:
    response = _get(f"{API}/repos/{repo}/commits/{sha}")
    return response.json() if response else None


def _diff_stats(commit_data: dict) -> dict:
    files = commit_data.get("files", [])
    return {
        "files": len(files),
        "additions": sum(f.get("additions", 0) for f in files),
        "deletions": sum(f.get("deletions", 0) for f in files),
    }


def _author_of(commit: dict) -> str:
    if commit.get("author") and commit["author"].get("login"):
        return commit["author"]["login"]
    return commit["commit"]["author"]["name"]


def get_recent_commits(repo: str) -> list[dict]:
    response = _get(f"{API}/repos/{repo}/commits", params={"per_page": COMMITS_PER_REPO})
    if response is None:
        return []
    data = response.json()
    if not isinstance(data, list):
        return []

    out: list[dict] = []
    for c in data:
        details = get_commit_details(repo, c["sha"])
        if not details:
            continue
        diff = _diff_stats(details)
        out.append({
            "id": c["sha"],
            "repo": repo,
            "author": _author_of(c),
            "message": c["commit"]["message"],
            "date": c["commit"]["author"]["date"],
            **diff,
        })
    return out


def get_all_commits() -> list[dict]:
    commits: list[dict] = []
    for repo in get_all_repos():
        commits.extend(get_recent_commits(repo))
    return commits
