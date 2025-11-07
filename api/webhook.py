# api/webhook.py
import os, json, logging
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import requests, joblib, random, numpy as np

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not set")

bot = Bot(token=BOT_TOKEN)

# create a dispatcher (no persistence, created per cold start)
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=False)

# load model and intents ONCE per cold start
vect = joblib.load("models/vectorizer.joblib")
clf = joblib.load("models/classifier.joblib")
intents = json.load(open("data/intents.json","r",encoding="utf-8"))

def get_responses_for_tag(tag):
    for it in intents["intents"]:
        if it["tag"] == tag:
            return it.get("responses", [])
    return []

# handler for /start
def start_handler(update, context):
    update.message.reply_text("Hi! I'm the college helpdesk bot. Ask anything!")

# handler for text messages -> use your model here too (or call /api/chat)
def text_handler(update, context):
    text = update.message.text or ""
    x = vect.transform([text])
    probs = clf.predict_proba(x)[0]
    idx = int(np.argmax(probs))
    tag = str(clf.classes_[idx])
    prob = float(probs[idx])
    if prob < 0.3:
        tag = "fallback"
    resp = random.choice(get_responses_for_tag(tag)) if get_responses_for_tag(tag) else "Sorry, I didn't get that."
    update.message.reply_text(resp)

# register handlers
dispatcher.add_handler(CommandHandler("start", start_handler))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# Vercel handler
def handler(request):
    # request.json is the Telegram Update payload
    body = request.json
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error":"no body"})}
    update = Update.de_json(body, bot)
    dispatcher.process_update(update)
    return {"statusCode": 200, "body": json.dumps({"ok": True})}
