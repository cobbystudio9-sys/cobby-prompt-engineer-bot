import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if BOT_TOKEN:
    TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
else:
    TELEGRAM_API = ""


def send_message(chat_id, text):
    """Send a message to a Telegram user."""
    if not TELEGRAM_API:
        return

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
    return "🤖 Cobby Prompt Engineer Bot is running!"


@app.route("/api/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}

    # Ignore updates that don't contain a message
    if "message" not in data:
        return "OK"

    message = data["message"]

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "").strip()

    # /start command
    if user_text == "/start":
        reply = (
            "👋 Welcome to Cobby Prompt Engineer!\n\n"
            "🧠 I turn simple ideas into professional AI prompts.\n\n"
            "You can send me things like:\n\n"
            "📸 Birthday photoshoot\n"
            "🎨 Business flyer\n"
            "🎬 AI video\n"
            "👤 Portrait\n"
            "📱 TikTok video\n"
            "🖼️ AI image\n\n"
            "Example:\n"
            "Create a birthday photoshoot for a child."
        )

    # Help command
    elif user_text == "/help":
        reply = (
            "🧠 Cobby Prompt Engineer\n\n"
            "Send me your simple idea and I will help "
            "turn it into a professional AI prompt.\n\n"
            "Example:\n"
            "Create a professional perfume advertisement."
        )

    # Normal message
    else:
        reply = (
            "🧠 PROMPT ENGINEER\n\n"
            f"Your idea:\n{user_text}\n\n"
            "✨ Your professional AI prompt will be generated here.\n\n"
            "🚀 AI generation is the next feature we will connect."
        )

    send_message(chat_id, reply)

    return "OK"


@app.route("/api/setup", methods=["GET"])
def setup():
    """Connect Telegram to this Vercel webhook."""

    if not TELEGRAM_API:
        return "BOT_TOKEN is missing.", 500

    webhook_url = (
        "https://cobby-prompt-engineer-65ztfymqc-cobbystudio9-sys.vercel.app"
        "/api/webhook"
    )

    response = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={"url": webhook_url},
        timeout=10
    )

    return response.text


if __name__ == "__main__":
    app.run()
