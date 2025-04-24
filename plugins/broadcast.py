from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.users_chats_db import db
from info import ADMINS
import asyncio
import datetime
import time
import re

BATCH_SIZE = 300
active_broadcasts = {}

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def start_broadcast(bot, message):
    ask = await message.reply(
        "📢 What type of message do you want to broadcast?\n"
        "Send `plain` for plain text or `button` for text with a button."
    )
    active_broadcasts[message.from_user.id] = {"step": "choose_type", "ask_msg": ask}


@Client.on_message(filters.private & filters.user(ADMINS))
async def handle_broadcast_input(bot, message):
    user_id = message.from_user.id
    session = active_broadcasts.get(user_id)

    if not session:
        return

    step = session.get("step")

    if step == "choose_type":
        if message.text == "plain":
            session["step"] = "awaiting_plain_text"
            await message.reply("📝 Send the plain text message to broadcast.")
        elif message.text == "button":
            session["step"] = "awaiting_button_text"
            await message.reply("📝 Send the message text.")
        else:
            await message.reply("❌ Invalid option. Please reply with `plain` or `button`.")

    elif step == "awaiting_plain_text":
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

    async def status_updater():
        while done < total_users:
            await asyncio.sleep(3)  # update every 3 seconds
            async with stats_lock:
                await sts.edit(
                    f"📢 Broadcasting...\n\n"
                    f"✅ Sent: {success} / {done}\n"
                    f"⛔ Blocked: {blocked}\n"
                    f"❌ Deleted: {deleted}\n"
                    f"⚠️ Failed: {failed}\n"
                    f"Total: {total_users}"
                )

    tasks = [safe_send(user) async for user in users_cursor]
    await asyncio.gather(status_updater(), *tasks)

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
