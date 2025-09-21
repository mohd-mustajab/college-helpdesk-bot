import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your BotFather token
BOT_TOKEN = "7577946025:AAET6F8SOoeTPeEAxZzMZRfuZO--PK6XQPU"
API_URL ="https://college-helpdesk-bot.onrender.com/chat"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm your College Helpdesk Bot. Ask me anything.")

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    try:
        resp = requests.post(API_URL, json={"message": user_msg}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            await update.message.reply_text(data.get("response", "No reply"))
        else:
            await update.message.reply_text(f"Server error: {resp.status_code}")
            print("Error from API:", resp.text)
    except Exception as e:
        await update.message.reply_text("⚠️ Error: API not reachable.")
        print("Exception:", e)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
