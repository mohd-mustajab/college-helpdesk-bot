import os
import json
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("VERCEL_URL", "").rstrip("/") + "/api/chat"

def handler(request):
    try:
        data = json.loads(request.body or "{}")
        message = data.get("message", {}).get("text", "")
        chat_id = data.get("message", {}).get("chat", {}).get("id")

        if not chat_id or not message:
            return {"statusCode": 400, "body": "Invalid Telegram update"}

        # Send message to chat API
        resp = requests.post(API_URL, json={"message": message})
        reply_data = resp.json()
        reply = reply_data.get("reply", "⚠️ Server error")

        # Send back to Telegram
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

        return {"statusCode": 200, "body": "ok"}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
