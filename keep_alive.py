from flask import Flask, request
from threading import Thread
import os
from telegram.ext import ApplicationBuilder

app = Flask("")

BOT_TOKEN = "your_bot_token_here"
application = Application.builder().token(BOT_TOKEN).build()

@app.route("/")
def home():
    return "QuickMate Bot is Alive!"

# Telegram webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()