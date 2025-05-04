from pyrogram import Client, filters
from rapidfuzz import process, fuzz
from database.filters_mdb import get_filters, find_filter
from pyrogram.types import Message
import ast

# Fuzzy match function
async def get_best_match_filter(group_id, query, threshold=60):
    filters_list = await get_filters(group_id)
    if not filters_list:
        return None, 0

    match, score, _ = process.extractOne(
        query.lower(), filters_list, scorer=fuzz.ratio
    )

    return (match, score) if score >= threshold else (None, score)

@Client.on_message(filters.text)
async def fuzzy_filter_reply(client: Client, message: Message):
    if message.chat.type not in ("group", "supergroup", "private"):
        return

    chat_id = message.chat.id
    text = message.text.strip().lower()

    matched, score = await get_best_match_filter(chat_id, text)
    if not matched:
        return  # No matching filter

    reply_text, btn, alert, file_id = await find_filter(chat_id, matched)
    if not reply_text and not file_id:
        return

    try:
        # Handle button (optional)
        reply_markup = None
        if btn:
            try:
                reply_markup = ast.literal_eval(btn)
            except Exception:
                pass

        if file_id:
            await message.reply_cached_media(
                media=file_id,
                caption=reply_text,
                reply_markup=reply_markup
            )
        else:
            await message.reply_text(
                reply_text,
                reply_markup=reply_markup
            )
    except Exception as e:
        await message.reply_text(f"❌ Failed to send filter response:\n`{e}`")
