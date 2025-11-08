import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import asyncio

# --- Setup ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

if not BOT_TOKEN or not API_URL:
    raise ValueError("❌ BOT_TOKEN or API_URL is missing. Set them in Vercel environment variables.")

# Telegram Bot instance
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)

# Create Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your College Helpdesk Bot 🤖. Ask me anything!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = requests.post(API_URL, json={"message": user_message})
        if response.status_code == 200:
            data = response.json()
            reply_text = data.get("reply", "Sorry, something went wrong.")
        else:
            reply_text = f"⚠️ Server error {response.status_code}"
    except Exception as e:
        logging.error(f"Error contacting API: {e}")
        reply_text = "❌ Unable to reach the server."

    await update.message.reply_text(reply_text)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# --- Flask webhook endpoint ---
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Receive updates from Telegram"""
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "OK", 200

# --- Set webhook route ---
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    """Sets Telegram webhook"""
    webhook_url = f"{os.getenv('VERCEL_URL')}/webhook/{BOT_TOKEN}"
    success = bot.set_webhook(url=webhook_url)
    return {"status": "Webhook set" if success else "Failed", "url": webhook_url}

# --- Root test route ---
@app.route("/", methods=["GET"])
def home():
    return "🤖 College Helpdesk Bot is running via Webhook!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
