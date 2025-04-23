from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import re
from database.broadcast_db import get_all_users  # <- Add this

OWNER_ID = 1525203313  # 🔁 Replace this with your actual Telegram user ID

# Temporary storage for message flow
broadcast_session = {}

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_entry(client, message):
    broadcast_session[message.from_user.id] = {"step": 1}
    await message.reply(
        """📝 Send the message you want to broadcast.\n\n"
        "You can add buttons like this:\n\n"
        "**Example:**\n"
        "🔥 Update is live!\n\n"
        "〽️Button〽️https://example.com〽️Another〽️https://another.com"""
    )

@Client.on_message(filters.text & filters.user(OWNER_ID))
async def handle_broadcast_flow(client, message):
    session = broadcast_session.get(message.from_user.id)
    if not session or session.get("step") != 1:
        return

    broadcast_session.pop(message.from_user.id)

    text = message.text
    # Parse custom buttons using pattern: 〽️Text〽️URL
    button_matches = re.findall(r"〽️(.*?)〽️(https?://[^\s]+)", text)
    buttons = []

    if button_matches:
        for btn_text, url in button_matches:
            buttons.append(InlineKeyboardButton(btn_text.strip(), url=url.strip()))
        # Clean buttons markup from message text
        text = re.sub(r"〽️(.*?)〽️(https?://[^\s]+)", "", text).strip()

    markup = InlineKeyboardMarkup([buttons]) if buttons else None

    await message.reply("📡 Broadcasting...")

    # Get all users from MongoDB
    async for user in get_all_users():
        try:
            await client.send_message(
                chat_id=user["_id"],
                text=text,
                reply_markup=markup
            )
        except Exception as e:
            print(f"❌ Failed to send to {user['_id']}: {e}")

    await message.reply("✅ Broadcast sent!") 
