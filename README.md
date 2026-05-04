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
3. Save them in SQLite so we don't re-report the same ones
4. AI looks at each developer's commits
5. Post the report to Discord
6. Repeat every `CHECK_INTERVAL` seconds

---

# Run it locally

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in tokens
ollama pull llama3.2:3b
python main.py
```

# Deploy to Fly

```bash
fly launch --no-deploy --copy-config
fly volumes create codictator_data --size 5
fly secrets set GH_TOKEN_CUSTOM=... DISCORD_BOT_TOKEN=... DISCORD_CHANNEL_ID=...
fly deploy
```

First boot pulls the model onto the volume. After that, restarts are fast.

---

# Notes

- AI analysis is not 100% accurate
- GitHub API has rate limits — the bot skips a cycle when hit
