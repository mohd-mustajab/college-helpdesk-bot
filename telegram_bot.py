import logging
import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
load_dotenv()

BOT_TOKEN = os.geten("7577946025:AAET6F8SOoeTPeEAxZzMZRfuZO--PK6XQPU")
API_URL = os.getenv("https://college-helpdesk-bot.onrender.com/chat")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your College Helpdesk Bot 🤖. Ask me anything!")

# Handle user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = requests.post(API_URL, json={"message": user_message})
        if response.status_code == 200:
            data = response.json()
            reply_text = data.get("reply", "Sorry, something went wrong.")
        else:
            reply_text = f"⚠️ Server error: {response.status_code}"
    except Exception as e:
        logger.error(f"Error contacting API: {e}")
        reply_text = "❌ Unable to reach the server."

    await update.message.reply_text(reply_text)

def main():
    if not BOT_TOKEN or not API_URL:
        raise ValueError("❌ BOT_TOKEN or API_URL not found in .env file")

    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()
