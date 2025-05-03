from pyrogram import Client, filters
from rapidfuzz import process, fuzz
from database.filters_mdb import get_filters as fetch_filters, get_filter
from pyrogram.types import Message

async def get_best_match_filter(group_id, query, threshold=60):
    filters_list = await fetch_filters(group_id)
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
    if message.chat.type not in ["group", "supergroup"]:
        return

    chat_id = message.chat.id
    text = message.text.lower()

    matched, score = await get_best_match_filter(chat_id, text)
    if not matched:
        await message.reply_text("No matching filter found.")
        return

    filter_data = await get_filter(chat_id, matched)
    if not filter_data:
        await message.reply_text("Filter found but something went wrong fetching content.")
        return

    try:
        if filter_data['file_id']:
            await message.reply_cached_media(
                media=filter_data['file_id'],
                caption=filter_data['reply_text']
            )
        else:
            await message.reply_text(filter_data['reply_text'])
    except Exception as e:
        await message.reply_text(f"Failed to send filter: {e}")
