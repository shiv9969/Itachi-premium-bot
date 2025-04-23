from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS
import asyncio
import datetime
import time
import re

BATCH_SIZE = 50
active_broadcasts = {}

def parse_buttons(text):
    pattern = r"\[([^\[]+)\]\((https?://[^\)]+)\)"
    matches = re.findall(pattern, text)
    if not matches:
        return None
    buttons = [[InlineKeyboardButton(text=txt, url=url)] for txt, url in matches]
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def start_broadcast(bot, message):
    ask = await message.reply("Please send the message you want to broadcast (text/media). If you want a button, use markdown like:\n\n`[Join Group](https://t.me/mygroup)`")
    active_broadcasts[message.from_user.id] = {"step": "awaiting_message", "ask_msg": ask}

@Client.on_message(filters.private & filters.user(ADMINS))
async def receive_broadcast_content(bot, message):
    user_id = message.from_user.id
    session = active_broadcasts.get(user_id)

    if not session or session.get("step") != "awaiting_message":
        return

    del active_broadcasts[user_id]

    users_cursor = await db.get_all_users()
    total_users = await db.total_users_count()
    sts = await message.reply("Broadcasting started...")
    start_time = time.time()

    buttons = parse_buttons(message.text or message.caption or "")
    content = {
        "text": message.text,
        "caption": message.caption,
        "media": message.photo or message.video or message.document,
        "buttons": buttons,
        "type": message.media.value if message.media else "text"
    }

    done = success = blocked = deleted = failed = 0
    batch = []

    async for user in users_cursor:
        batch.append(user)
        if len(batch) >= BATCH_SIZE:
            results = await asyncio.gather(*[
                send_to_user(bot, int(u['id']), content) for u in batch
            ])
            for result in results:
                done += 1
                if result == "success":
                    success += 1
                elif result == "blocked":
                    blocked += 1
                elif result == "deleted":
                    deleted += 1
                else:
                    failed += 1
            batch.clear()

            await sts.edit(f"📢 Broadcasting...\n\n✅ Sent: {success} / {done}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\nTotal: {total_users}")

    if batch:
        results = await asyncio.gather(*[
            send_to_user(bot, int(u['id']), content) for u in batch
        ])
        for result in results:
            done += 1
            if result == "success":
                success += 1
            elif result == "blocked":
                blocked += 1
            elif result == "deleted":
                deleted += 1
            else:
                failed += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"✅ Broadcast Completed in {time_taken}.\n\n"
        f"Total: {total_users}\n✅ Success: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}"
    )

async def send_to_user(bot, user_id, content):
    try:
        if content["media"]:
            await bot.send_document(
                user_id,
                document=content["media"].file_id,
                caption=content["caption"],
                reply_markup=content["buttons"]
            ) if content["type"] == "document" else await bot.send_photo(
                user_id,
                photo=content["media"].file_id,
                caption=content["caption"],
                reply_markup=content["buttons"]
            ) if content["type"] == "photo" else await bot.send_video(
                user_id,
                video=content["media"].file_id,
                caption=content["caption"],
                reply_markup=content["buttons"]
            )
        else:
            await bot.send_message(user_id, text=content["text"], reply_markup=content["buttons"])
        return "success"
    except Exception as e:
        if "blocked" in str(e).lower():
            return "blocked"
        elif "chat not found" in str(e).lower():
            return "deleted"
        else:
            return "error"
