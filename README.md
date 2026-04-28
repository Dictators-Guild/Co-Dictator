# AI - Developer Monitor

This is my first serious AI project.  
I built it with ChatGPT step by step, without prior experience in Python or backend systems.

The goal is simple:

👉 Monitor GitHub activity  
👉 Analyze commits using local AI  
👉 Send reports to Discord  

---

# What it does

- Tracks commits across all repositories I have access to
- Works with private + public repos
- Uses local AI (Ollama + Mistral) to analyze work
- Groups commits per developer
- Detects inactive developers
- Checks if commit messages match actual code changes
- Sends clean reports to Discord channel

---

# How it works

1. Fetch repositories from GitHub API  
2. Pull latest commits  
3. Get commit diffs (files changed, lines added/deleted)  
4. Analyze everything using AI  
5. Send report to Discord  
6. Repeat every X seconds  

---

# Requirements

You need:

- Python 3.10+
- Git
- Ollama installed

---

# 🔧 Installation

## 1. Clone project