from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import re

OWNER_ID = 1525203313  # Replace this with your actual Telegram user ID

# Temporary in-memory storage for the message flow
broadcast_session = {}

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_entry(client, message):
    broadcast_session[message.from_user.id] = {"step": 1}
    await message.reply("📝 Send the message you want to broadcast.

You can add buttons like this:

Hello!

[Button1](https://example.com) [Button2](https://example2.com)")

@Client.on_message(filters.text & filters.user(OWNER_ID))
async def handle_broadcast_flow(client, message):
    session = broadcast_session.get(message.from_user.id)
    if not session or session.get("step") != 1:
        return

    broadcast_session.pop(message.from_user.id)

    text = message.text
    button_matches = re.findall(r"\[(.*?)\]\((https?://.*?)\)", text)
    buttons = []

    if button_matches:
        for btn_text, url in button_matches:
            buttons.append(InlineKeyboardButton(btn_text, url=url))

        # Remove the button markdown from the text
        text = re.sub(r"\[(.*?)\]\((https?://.*?)\)", "", text).strip()

    markup = InlineKeyboardMarkup([buttons]) if buttons else None

    # Replace this with real user ID list from DB
    user_ids = [OWNER_ID]

    async def send_msg(uid):
        try:
            await client.send_message(chat_id=uid, text=text, reply_markup=markup)
        except Exception as e:
            print(f"Error sending to {uid}: {e}")

    await message.reply("📡 Broadcasting...")

    tasks = [send_msg(uid) for uid in user_ids]
    await asyncio.gather(*tasks)
    await message.reply("✅ Broadcast sent!")
