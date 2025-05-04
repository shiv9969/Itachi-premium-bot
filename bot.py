from plugins import verification
import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, __version__, filters
from pyrogram.raw.all import layer
from pyrogram.types import Message
from database.ia_filterdb import Media
from database.users_chats_db import db
from database.filters_mdb import get_filters as fetch_filters, get_filter
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, PORT, BIN_CHANNEL, ON_HEROKU
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
import pytz
from utils import temp, check_expired_premium
from rapidfuzz import process, fuzz
import asyncio
import sys
import importlib
import glob
from pathlib import Path
from aiohttp import web
from pyrogram import idle
from SAFARI.template import web_server
from SAFARI.utils import SafariBot
from SAFARI.utils.keepalive import ping_server
from SAFARI.utils.clients import initialize_clients

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

ppath = "plugins/*.py"
files = glob.glob(ppath)
SafariBot.start()
loop = asyncio.get_event_loop()


async def start():
    print('\n')
    print('Initalizing Your Bot')
    bot_info = await SafariBot.get_me()
    SafariBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("All Files Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    me = await SafariBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    SafariBot.username = '@' + me.username
    SafariBot.loop.create_task(check_expired_premium(SafariBot))
    logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    await idle()
    await SafariBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    try:
        m = await SafariBot.send_message(chat_id=BIN_CHANNEL, text="Test")
        await m.delete()
    except:
        logging.error("Make sure bot admin in BIN_CHANNEL, exiting now")
        exit()


# 🔍 Fuzzy Filter Handler (Works in Group + Private)
@SafariBot.on_message(filters.text & filters.incoming)
async def fuzzy_filter_reply(client: Client, message: Message):
    chat_id = message.chat.id
    user_text = message.text.strip().lower()

    filters_list = await fetch_filters(chat_id)
    if not filters_list:
        return

    match, score, _ = process.extractOne(user_text, filters_list, scorer=fuzz.ratio)

    if score < 60:
        return

    filter_data = await get_filter(chat_id, match)
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


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
