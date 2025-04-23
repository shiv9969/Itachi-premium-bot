from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

# Global flag to indicate if the broadcast should be canceled
broadcast_cancelled = False
BATCH_SIZE = 50  # You can adjust this batch size for efficiency

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    # Ask for the broadcast message
    sts = await message.reply_text("Please send me the broadcast message. You can also reply with a message that includes a button!")

    # Set up a message handler to capture the response
    @Client.on_message(filters.text & filters.user(ADMINS))
    async def handle_broadcast_message(bot, user_message):
        global broadcast_cancelled
        if user_message.reply_to_message:
            b_msg = user_message.reply_to_message
            # Check if the message contains a button request (simple rule, can be customized further)
            if "button:" in user_message.text:
                button_text = user_message.text.split("button:")[1].strip()
                keyboard = [
                    [InlineKeyboardButton(button_text, callback_data='broadcast_action')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await sts.edit("Broadcasting your message with a button...")
                # Proceed with broadcasting the message with button
                await broadcast_with_button(sts, b_msg, reply_markup)
            else:
                # Broadcast plain message without button
                await sts.edit("Broadcasting your plain message...")
                await broadcast_plain_message(sts, b_msg)

            # Remove the message handler after one use
            bot.remove_handler(handle_broadcast_message)

async def broadcast_plain_message(sts, b_msg):
    global broadcast_cancelled
    users_cursor = await db.get_all_users()
    start_time = time.time()
    total_users = await db.total_users_count()
    done = success = blocked = deleted = failed = 0
    batch = []

    async for user in users_cursor:
        # Check if broadcast is canceled before each batch
        if broadcast_cancelled:
            await sts.edit("The broadcast has been canceled.")
            break
        
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

            # Add cancel button
            cancel_button = InlineKeyboardButton("Cancel", callback_data='cancel_broadcast')
            cancel_markup = InlineKeyboardMarkup([[cancel_button]])

            await sts.edit(
                f"📢 Broadcasting...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\n"
                f"📦 Progress: {done}/{total_users}",
                reply_markup=cancel_markup
            )

async def broadcast_with_button(sts, b_msg, reply_markup):
    global broadcast_cancelled
    users_cursor = await db.get_all_users()
    start_time = time.time()
    total_users = await db.total_users_count()
    done = success = blocked = deleted = failed = 0
    batch = []

    async for user in users_cursor:
        # Check if broadcast is canceled before each batch
        if broadcast_cancelled:
            await sts.edit("The broadcast has been canceled.")
            break
        
        batch.append(user)
        if len(batch) >= BATCH_SIZE:
            results = await asyncio.gather(*[
                broadcast_messages(int(u['id']), b_msg, reply_markup) for u in batch
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

            # Add cancel button
            cancel_button = InlineKeyboardButton("Cancel", callback_data='cancel_broadcast')
            cancel_markup = InlineKeyboardMarkup([[cancel_button]])

            await sts.edit(
                f"📢 Broadcasting...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"✅ Sent: {success}\n⛔ Blocked: {blocked}\n❌ Deleted: {deleted}\n⚠️ Failed: {failed}\n"
                f"📦 Progress: {done}/{total_users}",
                reply_markup=cancel_markup
            )

# Handle cancel action
@Client.on_callback_query(filters.regex('cancel_broadcast'))
async def cancel_broadcast(bot, callback_query):
    global broadcast_cancelled
    broadcast_cancelled = True  # Set the flag to cancel the broadcast
    await callback_query.answer("Broadcast canceled!")
    await callback_query.message.edit(
        text="The broadcast has been canceled.",
        reply_markup=None
    )
