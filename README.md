# AI - Developer Monitor

This is my first serious AI project.
I built it with ChatGPT step by step, without prior experience in Python.

The goal is simple:

- Monitor GitHub activity
- Analyze commits using local AI
- Send reports to Discord

---

# What it does

- Tracks commits across all repos I have access to (private + public)
- Uses local AI (Ollama + llama3.2:3b) to analyze work
- Groups commits per developer
- Detects inactive developers
- Sends reports to a Discord channel

---

# How it works

1. Fetch repos from GitHub
2. Pull latest commits and diffs
3. Save them in SQLite (synced to Turso in production)
4. AI looks at each developer's commits
5. Post the report to Discord
6. Repeat every `CHECK_INTERVAL` seconds

The bot runs on Koyeb. Ollama runs on a laptop and the bot talks to it over
HTTP. If Ollama is unreachable, the report still goes out without the AI part.

---

# Run it

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in tokens
ollama pull llama3.2:3b
python main.py
```

For deployment notes (Koyeb + Turso + Ollama tunnel), see `.env.example`.

---

# Notes

- AI analysis is not 100% accurate
- GitHub API has rate limits — the bot skips a cycle when hit
