from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS
import asyncio
import datetime
import time
import re

broadcast_cancelled = False

@SafariBot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def ask_broadcast_type(_, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Plain Message", callback_data="broadcast_plain")],
        [InlineKeyboardButton("Message With Button", callback_data="broadcast_button")]
    ])
    await message.reply("Select broadcast type:", reply_markup=keyboard)

@SafariBot.on_callback_query(filters.user(ADMINS) & filters.regex("broadcast_(plain|button)"))
async def broadcast_message_input(_, query):
    broadcast_type = query.data.split("_")[1]
    await query.message.delete()
    await query.message.reply(f"Send me the message to broadcast ({'with button' if broadcast_type == 'button' else 'plain'}):")
    
    user_id = query.from_user.id

    def check(_, m: Message):
        return m.from_user.id == user_id

    message = await SafariBot.listen(user_id, filters=filters.text, timeout=300)

    btn_text, btn_url = None, None
    if broadcast_type == "button":
        await message.reply("Now send me the button text and URL in this format:\n\n`Button Text | https://example.com`")
        button_data = await SafariBot.listen(user_id, filters=filters.text, timeout=300)
        try:
            btn_text, btn_url = map(str.strip, button_data.text.split("|", 1))
        except Exception:
            return await message.reply("Invalid format. Use `Button Text | https://example.com`")

    await start_broadcast(message, btn_text, btn_url)

async def start_broadcast(msg: Message, btn_text=None, btn_url=None):
    global broadcast_cancelled
    broadcast_cancelled = False

    sts = await msg.reply("📢 Broadcasting...\n\nPlease wait...")
    users = await get_all_users()
    total_users = len(users)

    done = success = failed = blocked = deleted = 0

    cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel Broadcast", callback_data="cancel_broadcast")]])
    await sts.edit(
        f"📢 Broadcasting...\n\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\n"
        f"📦 Progress: {done}/{total_users}",
        reply_markup=cancel_keyboard
    )

    for user in users:
        if broadcast_cancelled:
            break
        try:
            if btn_text and btn_url:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=btn_url)]])
                await msg.forward(user['user_id'], reply_markup=reply_markup)
            else:
                await msg.forward(user['user_id'])
            success += 1
        except Exception as e:
            if "blocked" in str(e):
                blocked += 1
            elif "chat not found" in str(e):
                deleted += 1
            else:
                failed += 1
        done += 1

        if done % 5 == 0:
            await sts.edit(
                f"📢 Broadcasting...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\n"
                f"📦 Progress: {done}/{total_users}",
                reply_markup=cancel_keyboard
            )

        await asyncio.sleep(0.1)

    if broadcast_cancelled:
        await sts.edit("❌ Broadcast cancelled!")
    else:
        await sts.edit(
            f"✅ Broadcast complete!\n\n"
            f"👥 Total Users: {total_users}\n"
            f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}"
        )

@SafariBot.on_callback_query(filters.user(ADMINS) & filters.regex("cancel_broadcast"))
async def cancel_broadcast_handler(_, query):
    global broadcast_cancelled
    broadcast_cancelled = True
    await query.answer("Broadcast cancelled!", show_alert=True)
