from flask import Flask
from threading import Thread
import os

app = Flask("")

@app.route("/")
def home():
    return "QuickMate Bot is Alive!"

def run():
    # Render ka PORT le lo, agar na mile to default 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()