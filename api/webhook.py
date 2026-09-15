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
        }
    )


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

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
            "✨ Professional prompt generation will be connected next."
        )

    send_message(chat_id, reply)

    return "OK"


@app.route("/")
def home():
    return "Cobby Prompt Engineer Bot is running!"


if __name__ == "__main__":
    app.run()
