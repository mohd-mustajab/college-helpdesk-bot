# api/webhook.py
import os
import json
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")          # set in Vercel
API_URL = os.getenv("API_URL")              # e.g. https://college-helpdesk-api.vercel.app/chat

if not BOT_TOKEN or not API_URL:
    raise RuntimeError("BOT_TOKEN and API_URL must be set as environment variables")

TELEGRAM_SEND_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def handler(request):
    """
    Vercel Python function entrypoint. Accepts Telegram Update JSON.
    """
    try:
        body = request.json or {}
        # Telegram sends either 'message' or 'edited_message' etc.
        message = body.get("message") or body.get("edited_message")
        if not message:
            # Nothing to process
            return {"statusCode": 200, "body": json.dumps({"ok": True, "info": "no message"})}

        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "") or ""
        if not chat_id or text == "":
            return {"statusCode": 200, "body": json.dumps({"ok": True, "info": "no text or chat id"})}

        # Send text to your chat API and get reply
        api_resp = requests.post(API_URL, json={"message": text}, timeout=10)
        if api_resp.status_code == 200:
            # expect {"reply": "..."} or {"response": "..."}
            data = api_resp.json()
            reply_text = data.get("reply") or data.get("response") or "Sorry, no reply from API."
        else:
            reply_text = "⚠️ Backend error."

        # Send reply back to Telegram
        send_payload = {"chat_id": chat_id, "text": reply_text}
        requests.post(TELEGRAM_SEND_URL, json=send_payload, timeout=10)

        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    except Exception as e:
        # Return 200 to Telegram but log the error message in function logs
        return {"statusCode": 200, "body": json.dumps({"ok": False, "error": str(e)})}
