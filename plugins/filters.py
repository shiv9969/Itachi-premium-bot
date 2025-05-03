import io
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.filters_mdb import (
    add_filter,
    get_filters,
    delete_filter,
    count_filters
)
from database.connections_mdb import active_connection
from utils import get_file_id, parser, split_quotes
from info import ADMINS
from rapidfuzz import process  # Added for fuzzy matching
import time
from collections import deque

# Anti-spam store
user_message_times = {}  # To track user message timestamps
MAX_MESSAGES = 10  # Max messages per minute
TIME_FRAME = 60  # 1 minute (60 seconds)
USER_COOLDOWN = 300  # 5 minutes (300 seconds) cooldown after exceeding limit

@Client.on_message(filters.command(['filter', 'add']) & filters.incoming)
async def addfilter(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        return

    if len(args) < 2:
        await message.reply_text("Command Incomplete :(", quote=True)
        return

    extracted = split_quotes(args[1])
    text = extracted[0].lower()

    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text("Add some content to save your filter!", quote=True)
        return

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            await message.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = get_file_id(message.reply_to_message)
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]"
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.media:
        try:
            msg = get_file_id(message.reply_to_message)
            fileid = msg.file_id if msg else None
            reply_text, btn, alert = parser(extracted[1], text) if message.reply_to_message.sticker else parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(message.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
    else:
        return

    await add_filter(grp_id, text, reply_text, btn, fileid, alert)

    await message.reply_text(
        f"Filter for  `{text}`  added in  **{title}**",
        quote=True,
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.text & filters.incoming)
async def filter_response(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None

    if not user_id:
        return  # Ignore anonymous users

    now = time.time()

    # Initialize the user's message history if not already
    if user_id not in user_message_times:
        user_message_times[user_id] = {'timestamps': deque(), 'cooldown_until': 0}

    # Check if the user is under cooldown
    if user_message_times[user_id]['cooldown_until'] > now:
        remaining_cooldown = int(user_message_times[user_id]['cooldown_until'] - now)
        return await message.reply_text(f"You're on cooldown. Try again in {remaining_cooldown} seconds.")

    # Remove messages that are older than the allowed time frame (1 minute)
    while user_message_times[user_id]['timestamps'] and user_message_times[user_id]['timestamps'][0] < now - TIME_FRAME:
        user_message_times[user_id]['timestamps'].popleft()

    # Check if the user has sent more than the allowed number of messages in the last minute
    if len(user_message_times[user_id]['timestamps']) >= MAX_MESSAGES:
        # User has exceeded the limit, set a cooldown
        user_message_times[user_id]['cooldown_until'] = now + USER_COOLDOWN
        remaining_cooldown = int(user_message_times[user_id]['cooldown_until'] - now)
        return await message.reply_text(f"You've exceeded the limit of {MAX_MESSAGES} messages in 1 minute. You are on cooldown for {remaining_cooldown} seconds.")

    # Add the current message timestamp to the user's history
    user_message_times[user_id]['timestamps'].append(now)

    # Get filters
    texts = await get_filters(chat_id)
    if not texts:
        return

    query = message.text.lower()

    # Fuzzy match
    match = process.extractOne(query, texts, score_cutoff=60)
    if match:
        matched_text = match[0]
        # Fake call to function that replies based on matched filter
        await message.reply_text(f"Matched filter: `{matched_text}`", parse_mode=enums.ParseMode.MARKDOWN)
