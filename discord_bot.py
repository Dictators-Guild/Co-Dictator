import requests
from config import DISCORD_TOKEN, CHANNEL_ID

def send_to_discord(text):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }

    for i in range(0, len(text), 1900):
        requests.post(url, headers=headers, json={
            "content": text[i:i+1900]
        })