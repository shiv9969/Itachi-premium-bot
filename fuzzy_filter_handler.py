from pyrogram import Client, filters
from rapidfuzz import process, fuzz
from pyrogram.types import Message
from database.filters_mdb import get_filters as fetch_filters, get_filter

async def get_best_match_filter(chat_id, query, threshold=60):
    filters_list = await fetch_filters(chat_id)
    if not filters_list:
        return None, 0

    match, score, _ = process.extractOne(
        query.lower(), filters_list, scorer=fuzz.ratio
    )

    if score >= threshold:
        return match, score
    else:
        return None, score

@Client.on_message(filters.text & filters.incoming)
async def fuzzy_filter_reply(client: Client, message: Message):
    chat_id = message.chat.id
    user_text = message.text.strip().lower()

    matched, score = await get_best_match_filter(chat_id, user_text)

    if not matched:
        return  # No matching filter, silently skip

    filter_data = await get_filter(chat_id, matched)
    if not filter_data:
        await message.reply_text("Filter found, but failed to fetch content.")
        return

    try:
        if filter_data.get("file_id"):
            await message.reply_cached_media(
                media=filter_data["file_id"],
                caption=filter_data.get("reply_text", "")
            )
        else:
            await message.reply_text(filter_data.get("reply_text", ""))
    except Exception as e:
        await message.reply_text(f"Failed to send filter: {e}")
