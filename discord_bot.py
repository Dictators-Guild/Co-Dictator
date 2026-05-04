import logging
import time

import requests

from config import CHANNEL_ID, DISCORD_TOKEN

log = logging.getLogger(__name__)

URL = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
HEADERS = {
    "Authorization": f"Bot {DISCORD_TOKEN}",
    "Content-Type": "application/json",
}
CHUNK_LIMIT = 1900
MAX_RETRIES = 3


def _split(text: str, limit: int = CHUNK_LIMIT) -> list[str]:
    chunks: list[str] = []
    buf = ""
    for line in text.splitlines(keepends=True):
        if len(line) > limit:
            if buf:
                chunks.append(buf)
                buf = ""
            for i in range(0, len(line), limit):
                chunks.append(line[i:i + limit])
            continue
        if len(buf) + len(line) > limit:
            chunks.append(buf)
            buf = line
        else:
            buf += line
    if buf:
        chunks.append(buf)
    return chunks


def _post(content: str) -> None:
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                URL, headers=HEADERS, json={"content": content}, timeout=15
            )
        except requests.RequestException as exc:
            log.warning("Discord post failed (attempt %d): %s", attempt + 1, exc)
            time.sleep(2 ** attempt)
            continue

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "1"))
            log.info("Discord rate-limited, sleeping %.2fs", retry_after)
            time.sleep(retry_after)
            continue

        if 200 <= response.status_code < 300:
            return

        log.warning("Discord %d: %s", response.status_code, response.text[:200])
        return


def send_to_discord(text: str) -> None:
    for chunk in _split(text):
        _post(chunk)
