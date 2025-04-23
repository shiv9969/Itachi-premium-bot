from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio
import re

BATCH_SIZE = 50
ongoing_broadcast = {"cancel": False}

# Function to parse inline button and clean message text
def parse_buttons_and_clean_text(text):
    pattern = r"\[([^\[]+)\]\((https?://[^\)]+)\)"
    matches = re.findall(pattern, text)

    # Clean the text by removing markdown
    cleaned_text = re.sub(pattern, '', text).strip()
    if not matches:
        return None, cleaned_text

    buttons = InlineKeyboardMarkup([[InlineKeyboardButton(txt, url=url)] for txt, url in matches])
    return buttons, cleaned_text


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def ask_for_broadcast(bot, message):
    await message.reply("Please send the message you want to broadcast (with optional [Text](URL) for button):")
    # Set a flag or store message.user_id if needed for multi-admin


@Client.on_message(filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    if message.reply_to_message:
        return  # Avoid recursion with replied messages

    users_cursor = await db.get_all_users()
    text = message.text or message.caption or ""
    buttons, clean_text = parse_buttons_and_clean_text(text)

    media = None
    if message.photo:
        media = message.photo
    elif message.video:
        media = message.video
    elif message.document:
        media = message.document

    # Notify start
    status = await message.reply("📢 Broadcasting...")

    start_time = time.time()
    total_users = await db.total_users_count()
    done = success = blocked = deleted = failed = 0
    batch = []

    # Reset cancel flag
    ongoing_broadcast["cancel"] = False

    async for user in users_cursor:
        if ongoing_broadcast["cancel"]:
            await status.edit("❌ Broadcast canceled by admin.")
            return

        batch.append(user)
        if len(batch) >= BATCH_SIZE:
            results = await asyncio.gather(*[
                broadcast_messages(
                    int(u["id"]),
                    message=None,
                    text=clean_text,
                    media=media,
                    buttons=buttons
                ) for u in batch
            ])
            for pti, reason in results:
                done += 1
                if pti:
                    success += 1
                else:
                    if reason == "Blocked":
                        blocked += 1
                    elif reason == "Deleted":
                        deleted += 1
                    else:
                        failed += 1
            batch.clear()
            await status.edit(
                f"📢 Broadcasting...\n"
                f"✅ Sent: {success} / {total_users}\n"
                f"⛔ Blocked: {blocked} ❌ Deleted: {deleted} ⚠️ Failed: {failed}\n"
                f"Progress: {done}/{total_users}"
            )

    # Final batch
    if batch:
        results = await asyncio.gather(*[
            broadcast_messages(
                int(u["id"]),
                message=None,
                text=clean_text,
                media=media,
                buttons=buttons
            ) for u in batch
        ])
        for pti, reason in results:
            done += 1
            if pti:
                success += 1
            else:
                if reason == "Blocked":
                    blocked += 1
                elif reason == "Deleted":
                    deleted += 1
                else:
                    failed += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await status.edit(
        f"✅ Broadcast Completed in {time_taken}.\n\n"
        f"Total Users: {total_users}\n"
        f"✅ Success: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}"
    )


# Optional: cancel command
@Client.on_message(filters.command("cancel_broadcast") & filters.user(ADMINS))
async def cancel_broadcast(bot, message):
    ongoing_broadcast["cancel"] = True
    await message.reply("🛑 Broadcast will be canceled shortly.")
