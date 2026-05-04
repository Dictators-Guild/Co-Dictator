#!/bin/sh
set -e

if [ "${OLLAMA_ENABLED:-true}" = "true" ]; then
    echo "[entrypoint] starting ollama serve"
    ollama serve &
    OLLAMA_PID=$!

    echo "[entrypoint] waiting for ollama"
    for i in $(seq 1 60); do
        if curl -sf "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
    if ! ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$MODEL"; then
        echo "[entrypoint] pulling $MODEL (one-time, persisted to volume)"
        ollama pull "$MODEL" || echo "[entrypoint] pull failed; continuing without AI"
    fi

    trap 'kill $OLLAMA_PID 2>/dev/null; exit 0' TERM INT
fi

echo "[entrypoint] starting bot"
exec python main.py
