import os
import requests
from flask import Flask, request
from google import genai
from google.genai import types

app = Flask(__name__)

# =========================
# ENVIRONMENT VARIABLES
# =========================

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
    if BOT_TOKEN else ""
)

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


# =========================
# PROMPT ENGINEER INSTRUCTIONS
# =========================

SYSTEM_INSTRUCTION = """
You are Cobby Prompt Engineer, a professional AI prompt engineer.

Your job is to take a user's simple idea and transform it into a
high-quality, detailed, professional, copy-and-paste-ready AI prompt.

You specialize in:
- AI image prompts
- AI video prompts
- Birthday photoshoots
- Business flyers
- Product advertisements
- Portrait photography
- TikTok videos
- Children's content
- 3D cartoon images
- Cinematic scenes
- Social media content

IMPORTANT RULES:

1. Understand the user's main idea first.
2. Improve the idea professionally without changing its meaning.
3. Add useful details such as:
   - subject
   - environment
   - clothing
   - pose
   - facial expression
   - lighting
   - camera angle
   - camera lens
   - composition
   - background
   - colors
   - visual quality
   - artistic style
4. Keep important names and requested details exactly as provided.
5. Do not invent personal information that the user did not provide.
6. If the user asks for an image prompt, make it suitable for an AI image generator.
7. If the user asks for a video prompt, include:
   - character actions
   - camera movement
   - environment movement
   - timing when useful
   - dialogue or lip-sync instructions when requested
8. If the request is for a business flyer, include professional layout,
   typography, branding space, product placement and advertising style.
9. Make the final prompt easy to copy and use.
10. Do not say that you generated an image or video. You only create the prompt.

Use this format:

🧠 PROFESSIONAL AI PROMPT

[Write the polished prompt here]

🎨 STYLE:
[Style]

📷 CAMERA:
[Camera and composition details]

💡 LIGHTING:
[Lighting details]

✨ QUALITY:
[Quality/rendering details]

🚫 NEGATIVE PROMPT:
[Useful things to avoid]

Keep the response professional but easy to understand.
"""


# =========================
# TELEGRAM FUNCTIONS
# =========================

def send_message(chat_id, text):
    """Send a message to Telegram."""

    if not TELEGRAM_API:
        return

    # Telegram messages have a length limit.
    # Split very long AI responses into smaller messages.
    max_length = 4000

    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]

        requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": chunk
            },
            timeout=15
        )


# =========================
# GEMINI FUNCTION
# =========================

def generate_prompt(user_text):
    """Send the user's idea to Gemini."""

    if not client:
        return "⚠️ Gemini API is not configured yet."

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.8,
            max_output_tokens=1500
        )
    )

    if response.text:
        return response.text

    return "⚠️ Gemini did not return a response."


# =========================
# HOME
# =========================

@app.route("/", methods=["GET"])
def home():
    return "🤖 Cobby Prompt Engineer Bot is running!"


# =========================
# TELEGRAM WEBHOOK
# =========================

@app.route("/api/webhook", methods=["POST"])
def webhook():

    data = request.get_json(silent=True) or {}

    if "message" not in data:
        return "OK"

    message = data["message"]

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "").strip()

    # /start
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

        send_message(chat_id, reply)
        return "OK"

    # /help
    if user_text == "/help":

        reply = (
            "🧠 Cobby Prompt Engineer\n\n"
            "Send me your simple idea and I will turn it "
            "into a professional AI prompt.\n\n"
            "Example:\n"
            "Create a professional perfume advertisement."
        )

        send_message(chat_id, reply)
        return "OK"

    # Empty message
    if not user_text:
        send_message(
            chat_id,
            "Please send me an idea that you want turned into a professional AI prompt."
        )
        return "OK"

    # Show processing message
    send_message(
        chat_id,
        "🧠 Creating your professional prompt...\n⏳ Please wait..."
    )

    # Generate AI prompt
    try:

        ai_prompt = generate_prompt(user_text)

        reply = (
            "✨ Cobby Prompt Engineer\n\n"
            + ai_prompt
        )

    except Exception as e:

    print("Gemini error:", str(e))

    reply = (
        "⚠️ Gemini error:\n\n"
        + str(e)
    )

    send_message(chat_id, reply)

    return "OK"


# =========================
# WEBHOOK SETUP
# =========================

@app.route("/api/setup", methods=["GET"])
def setup():

    if not TELEGRAM_API:
        return "BOT_TOKEN is missing.", 500

    webhook_url = (
        "https://cobby-prompt-engineer-bot.vercel.app"
        "/api/webhook"
    )

    response = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={"url": webhook_url},
        timeout=10
    )

    return response.text


# =========================
# LOCAL RUN
# =========================

if __name__ == "__main__":
    app.run()
