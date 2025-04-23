from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio

BATCH_SIZE = 50  # You can tune this for better speed vs stability

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    users_cursor = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text("Broadcasting your messages...")

    start_time = time.time()
    total_users = await db.total_users_count()
    done = success = blocked = deleted = failed = 0
    batch = []

    async for user in users_cursor:
        batch.append(user)
        if len(batch) >= BATCH_SIZE:
            results = await asyncio.gather(*[
                broadcast_messages(int(u['id']), b_msg) for u in batch
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

            await sts.edit(
                f"📢 Broadcasting...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\n"
                f"📦 Progress: {done}/{total_users}"
            )

    # Final batch
    if batch:
        results = await asyncio.gather(*[
            broadcast_messages(int(u['id']), b_msg) for u in batch
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
    await sts.edit(
        f"✅ Broadcast Completed in {time_taken}.\n\n"
        f"Total: {total_users}\n"
        f"✅ Success: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}"
    )
