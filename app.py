import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=10
    )


@app.route("/", methods=["GET"])
def home():
    return "Cobby Prompt Engineer Bot is running!"


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    if "message" not in data:
        return "OK"

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    if user_text == "/start":
        reply = (
            "👋 Welcome to Cobby Prompt Engineer!\n\n"
            "Send me any simple idea and I will turn it "
            "into a professional AI prompt. 🚀\n\n"
            "Example:\n"
            "Create a birthday photoshoot for a child."
        )
    else:
        reply = (
            "🧠 PROMPT ENGINEER\n\n"
            f"Your idea:\n{user_text}\n\n"
            "✨ AI prompt generation will be connected next."
        )

    send_message(chat_id, reply)

    return "OK"
