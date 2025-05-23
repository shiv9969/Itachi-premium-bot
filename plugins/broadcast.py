from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.users_chats_db import db
from info import ADMINS
import asyncio
import datetime
import time

BATCH_SIZE = 300
active_broadcasts = {}

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def start_broadcast(bot, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Plain Text", callback_data="broadcast_plain")],
        [InlineKeyboardButton("🔘 Text with Button", callback_data="broadcast_button")],
        [InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]
    ])
    ask = await message.reply(
        "📢 What type of message do you want to broadcast?",
        reply_markup=keyboard
    )
    active_broadcasts[message.from_user.id] = {"step": "choose_type", "ask_msg": ask}


@Client.on_callback_query(filters.user(ADMINS))
async def handle_broadcast_callback(bot, query):
    user_id = query.from_user.id
    session = active_broadcasts.get(user_id)

    if not session:
        return await query.answer("No active broadcast session.")

    data = query.data

    if data == "broadcast_cancel":
        await query.message.edit("❌ Broadcast cancelled.")
        del active_broadcasts[user_id]
        return

    if data == "broadcast_plain":
        session["step"] = "awaiting_plain_text"
        await query.message.edit(
            "📝 Send the plain text message to broadcast.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]])
        )
        return

    if data == "broadcast_button":
        session["step"] = "awaiting_button_text"
        await query.message.edit(
            "📝 Send the message text.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="broadcast_cancel")]])
        )
        return


@Client.on_message(filters.private & filters.user(ADMINS))
async def handle_broadcast_input(bot, message):
    user_id = message.from_user.id
    session = active_broadcasts.get(user_id)

    if not session:
        return

    step = session.get("step")

    if step == "awaiting_plain_text":
        del active_broadcasts[user_id]
        await process_broadcast(bot, message, message.text, None)

    elif step == "awaiting_button_text":
        session["message_text"] = message.text
        session["step"] = "awaiting_button_label"
        await message.reply("🔘 Send the button label text.")

    elif step == "awaiting_button_label":
        session["button_label"] = message.text
        session["step"] = "awaiting_button_url"
        await message.reply("🔗 Send the button URL.")

    elif step == "awaiting_button_url":
        msg_text = session["message_text"]
        button_label = session["button_label"]
        button_url = message.text
        del active_broadcasts[user_id]

        button_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(button_label, url=button_url)]]
        )
        await process_broadcast(bot, message, msg_text, button_markup)


async def process_broadcast(bot, message, text, buttons):
    users_cursor = await db.get_all_users()
    total_users = await db.total_users_count()
    sts = await message.reply("🚀 Broadcasting started...")
    start_time = time.time()

    content = {
        "text": text,
        "caption": None,
        "media": None,
        "buttons": buttons,
        "type": "text"
    }

    success = blocked = deleted = failed = 0
    done = 0
    semaphore = asyncio.Semaphore(40)
    stats_lock = asyncio.Lock()

    async def safe_send(user):
        nonlocal success, blocked, deleted, failed, done
        try:
            async with semaphore:
                result = await send_to_user(bot, int(user["id"]), content)
                async with stats_lock:
                    done += 1
                    if result == "success":
                        success += 1
                    elif result == "blocked":
                        blocked += 1
                    elif result == "deleted":
                        deleted += 1
                    else:
                        failed += 1
        except Exception:
            async with stats_lock:
                done += 1
                failed += 1

    async def status_updater():
        while done < total_users:
            await asyncio.sleep(3)
            async with stats_lock:
                await sts.edit(
                    f"📢 Broadcasting...\n\n"
                    f"✅ Sent: {success} / {done}\n"
                    f"⛔ Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n"
                    f"⚠️ Failed: {failed}\n"
                    f"Total: {total_users}"
                )

    batch = []
    tasks = []
    async for user in users_cursor:
        batch.append(user)
        if len(batch) >= BATCH_SIZE:
            tasks = [safe_send(u) for u in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
            batch.clear()

    if batch:
        tasks = [safe_send(u) for u in batch]
        await asyncio.gather(*tasks, return_exceptions=True)

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts.edit(
        f"✅ Broadcast Completed in {time_taken}.\n\n"
        f"Total: {total_users}\n✅ Success: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}"
    )


async def send_to_user(bot, user_id, content):
    try:
        if content["media"]:
            # Future support for media
            pass
        else:
            await bot.send_message(user_id, text=content["text"], reply_markup=content["buttons"])
        return "success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_to_user(bot, user_id, content)
    except Exception as e:
        err = str(e).lower()
        if "blocked" in err:
            return "blocked"
        elif "chat not found" in err:
            return "deleted"
        else:
            return "error" 
