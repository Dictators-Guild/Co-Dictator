import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


GITHUB_TOKEN = _require("GH_TOKEN_CUSTOM")
DISCORD_TOKEN = _require("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(_require("DISCORD_CHANNEL_ID"))

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

DB_PATH = os.getenv("DB_PATH", "codictator.db")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))
INACTIVE_THRESHOLD = int(os.getenv("INACTIVE_THRESHOLD", "1440"))
