import re
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import KeyboardButtonUrl

# --- Telegram API credentials (hard-coded) ---
API_ID = 24878661
API_HASH = "7fd279b83c40a0d4228b89978685638a"
SESSION_STRING = "wQQddWAvd90uN+mfpX1+1/hPW5PZQWMtCl67G+kBd+yOqXdzVd9DAeulJLtfP8aHf52g39e5h5Y+7djtitP4rw=="

# --- Channel IDs ---
SOURCE_CHANNEL = "@Signals_Pumps_Free"
TARGET_CHANNEL = "@aixauusdbtcusd_trade"

# --- Replacement Settings ---
REPLACE_WITH = "@aimanagementteambot"

# --- Flask keep-alive server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_web)
    t.start()

# --- Create client from session string ---
# This will also generate a user_session.session file automatically
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Utility: clean text
def clean_text(text):
    if not text:
        return text
    text = re.sub(r"@\w+", REPLACE_WITH, text, flags=re.IGNORECASE)
    text = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, text, flags=re.IGNORECASE)
    return text

# Utility: custom button
def get_custom_button():
    return [KeyboardButtonUrl(text="💬 Join Our Bot", url="https://t.me/aimanagementteambot")]

# Utility: replace links in buttons
def replace_button_links(reply_markup):
    if not reply_markup:
        return None
    try:
        new_rows = []
        for row in reply_markup.rows:
            new_buttons = []
            for button in row.buttons:
                if hasattr(button, 'url') and button.url:
                    new_url = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, button.url, flags=re.IGNORECASE)
                    new_buttons.append(KeyboardButtonUrl(text=button.text, url=new_url))
                else:
                    new_buttons.append(button)
            new_rows.append(type(row)(buttons=new_buttons))
        new_rows.append(type(new_rows[0])(buttons=get_custom_button()))
        return type(reply_markup)(rows=new_rows)
    except Exception as e:
        print(f"⚠️ Error replacing button links: {e}")
        return reply_markup

# --- Bot logic ---
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        message = event.message
        print(f"📥 New message received: {message.id}")
        reply_markup = replace_button_links(message.reply_markup) if message.reply_markup else None
        text_content = clean_text(message.text or message.message or message.raw_text)

        if message.media:
            await client.send_file(TARGET_CHANNEL, message.media, caption=text_content or "", buttons=reply_markup)
        elif text_content:
            await client.send_message(TARGET_CHANNEL, text_content, buttons=reply_markup)
        elif reply_markup:
            await client.send_message(TARGET_CHANNEL, "📢", buttons=reply_markup)

        print(f"✅ Forwarded new message ID {message.id}")
    except Exception as e:
        print(f"⚠️ Error forwarding message {event.id}: {e}")

async def run_bot():
    # Start client and save session to file
    await client.start()
    client.session.save()  # writes user_session.session
    print("🚀 Bot is running 24/7 on Render Free Web Service...")
    # Warm up the source channel so updates start flowing
    async for msg in client.iter_messages(SOURCE_CHANNEL, limit=1):
        print("🔄 Warmed up channel with last message:", msg.id)
    await client.run_until_disconnected()

# --- Start keep-alive server and bot ---
keep_alive()

while True:
    try:
        asyncio.run(run_bot())
    except Exception as e:
        print(f"💥 Bot crashed with error: {e}. Restarting in 10s...")
        import time; time.sleep(10)

