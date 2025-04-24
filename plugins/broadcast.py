from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import datetime
import time

from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

user_broadcast_sessions = {}

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def ask_for_broadcast_message(bot, message: Message):
    user_id = message.from_user.id
    user_broadcast_sessions[user_id] = {"step": "waiting_for_message"}
    await message.reply_text("📝 Send the message you want to broadcast (markdown/buttons supported).\nSend /cancel to stop.")

@Client.on_message(filters.text & filters.user(ADMINS))
async def handle_broadcast_message(bot, message: Message):
    user_id = message.from_user.id
    if user_id not in user_broadcast_sessions:
        return

    session = user_broadcast_sessions[user_id]
    if session.get("step") != "waiting_for_message":
        return

    broadcast_message = message
    users = await db.get_all_users()
    total_users = await db.total_users_count()
    start_time = time.time()

    sts = await message.reply_text("🚀 Broadcasting started (Max Speed Mode)...")

    done = success = blocked = deleted = failed = 0

    semaphore = asyncio.Semaphore(30)  # Control concurrency: 30 at a time

    async def send_to_user(user):
        nonlocal done, success, blocked, deleted, failed
        async with semaphore:
            try:
                pti, sh = await broadcast_messages(int(user["id"]), broadcast_message)
                if pti:
                    success += 1
                elif sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            except:
                failed += 1
            done += 1

    tasks = []
    async for user in users:
        tasks.append(asyncio.create_task(send_to_user(user)))
        if len(tasks) % 50 == 0:  # Update every 50
            await asyncio.sleep(1)
            await sts.edit(
                f"📣 Broadcast in progress...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Success: {success}\n"
                f"⛔ Blocked: {blocked}\n"
                f"🗑️ Deleted: {deleted}\n"
                f"⚠️ Failed: {failed}\n"
                f"🧾 Completed: {done} / {total_users}"
            )

    await asyncio.gather(*tasks)

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"✅ Broadcast Completed!\n\n"
        f"⏱ Time: {time_taken}\n"
        f"👥 Total Users: {total_users}\n"
        f"✅ Success: {success}\n"
        f"⛔ Blocked: {blocked}\n"
        f"🗑️ Deleted: {deleted}\n"
        f"⚠️ Failed: {failed}"
    )
    user_broadcast_sessions.pop(user_id, None)

@Client.on_message(filters.command("cancel") & filters.user(ADMINS))
async def cancel_broadcast(bot, message):
    user_id = message.from_user.id
    if user_id in user_broadcast_sessions:
        user_broadcast_sessions.pop(user_id)
        await message.reply_text("❌ Broadcast cancelled.")
    else:
        await message.reply_text("❌ You have no active broadcast.")
