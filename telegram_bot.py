import logging
import requests
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram import Bot

bot = Bot(token=os.getenv("BOT_TOKEN"))
bot.delete_webhook()  # Ensure no webhook is active

# Read environment variables (set in Render dashboard)
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

if not BOT_TOKEN or not API_URL:
    raise ValueError("❌ BOT_TOKEN or API_URL is missing. Set them in Render Dashboard > Environment.")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your College Helpdesk Bot 🤖. Ask me anything!")

# Handle normal text messages
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
        logger.error(f"Error contacting API: {e}")
        reply_text = "❌ Unable to reach the server."

    await update.message.reply_text(reply_text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    app.run_polling()

if __name__ == "__main__":
    main()
