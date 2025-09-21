import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your latest LocalTunnel URL
API_URL = "https://college-helpdesk-bot.onrender.com/chat"
BOT_TOKEN = "7577946025:AAET6F8SOoeTPeEAxZzMZRfuZO--PK6XQPU"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I am your College Helpdesk Bot. Ask me anything.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    try:
        res = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            json={"message": user_msg},
            timeout=10
        )

        logging.info(f"API raw response: {res.text}")  # debug log

        if res.status_code == 200:
            data = res.json()
            reply = data.get("response", "Sorry, no reply from server.")
        else:
            reply = f"Server error: {res.status_code}"

    except Exception as e:
        reply = f"Error: API not reachable. {str(e)}"

    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
