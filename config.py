import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GH_TOKEN_CUSTOM")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

GITHUB_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}"
}

SEEN_FILE = "seen.json"
CHECK_INTERVAL = 60
INACTIVE_THRESHOLD = 1440