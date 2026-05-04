import logging
import os

import requests

log = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "30"))


def is_available() -> bool:
    if not OLLAMA_ENABLED:
        return False
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False


def summarize(prompt: str) -> str | None:
    if not OLLAMA_ENABLED:
        return None
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
    except requests.RequestException as exc:
        log.warning("Ollama unreachable: %s", exc)
        return None

    if response.status_code != 200:
        log.warning("Ollama %d: %s", response.status_code, response.text[:200])
        return None

    return response.json().get("response", "").strip() or None
