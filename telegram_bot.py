import os
import requests
from telegram.ext import Updater, MessageHandler, Filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:5000/chat")

def handle_message(update, context):
    user_message = update.message.text
    try:
        res = requests.post(API_URL, json={"message": user_message})
        data = res.json()
        reply = data.get("reply", "Sorry, I’m having trouble right now.")
    except Exception as e:
        reply = f"Server error: {e}"
    update.message.reply_text(reply)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
