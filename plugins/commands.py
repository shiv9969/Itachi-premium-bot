import os
import sys
import logging
import random
import asyncio
import pytz
import requests
from Script import script
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from database.top_search import db3
from database.safaridev import db2
from info import *
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, send_all, get_tutorial, get_shortlink, get_seconds
from database.connections_mdb import active_connection
import re
import json
import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('🍁 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ 🍁', url="https://t.me/{temp.U_NAME}?start=help")
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            curr_time = current_time.hour        
            if curr_time < 12:
                gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 👋" 
            elif curr_time < 17:
                gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 👋" 
            elif curr_time < 21:
                gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 👋"
            else:
                gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 👋"
            # m=await message.reply_sticker("CAACAgUAAxkBAAEkohxmOzL_8-HJRwudONzAED-tMt27LQACRwADJpleD38508ect3TIHgQ") 
            # await asyncio.sleep(2)
            # await m.delete()
            await message.reply_photo(
                photo=(PICS),
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
            if not await db.get_chat(message.chat.id):
                total=await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(temp.B_NAME, message.chat.title, message.chat.id, total, "Unknown"))       
                await db.add_chat(message.chat.id, message.chat.title)
            return 
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, temp.B_NAME))
        if len(message.command) != 2:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('📚 ʙᴀᴄᴋᴜᴘ', url=CHNL_LNK),
                        InlineKeyboardButton('🌿 ɢʀᴏᴜᴘ', url=GRP_LNK),
                        InlineKeyboardButton('🌈 ᴄʜᴀɴɴᴇʟ', url=f'http://t.me/The_Happy_Hour_Hindi')
                    ],[
                        InlineKeyboardButton('🏕️ ᴀʙᴏᴜᴛ', callback_data='about'),
                        InlineKeyboardButton('🍾 ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='seeplans'),
                        InlineKeyboardButton('🍁 ꜱᴛᴀᴛꜱ', callback_data='stats')
                    ],[
                        InlineKeyboardButton('🌹 ʀᴇғғᴇʀ 🌹', callback_data='reffer')
                        ]]
            if IS_VERIFY or IS_SHORTLINK is True:
                buttons.append([
                    InlineKeyboardButton('🏡 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 🏡', callback_data='seeplans')
                ])
            if TOP_SEARCH is True:
                buttons.append([
                    InlineKeyboardButton("🎁 ᴍᴏᴠɪᴇ sᴜɢɢᴇsᴛɪᴏɴ's 🎁", callback_data='movie_suggestion')
                ])
            reply_markup = InlineKeyboardMarkup(buttons)
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            curr_time = current_time.hour        
            if curr_time < 12:
                gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 👋" 
            elif curr_time < 17:
                gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 👋" 
            elif curr_time < 21:
                gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 👋"
            else:
                gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 👋"
            # m=await message.reply_sticker("CAACAgUAAxkBAAEkohxmOzL_8-HJRwudONzAED-tMt27LQACRwADJpleD38508ect3TIHgQ") 
            # await asyncio.sleep(2)
            # await m.delete()
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        if AUTH_CHANNEL and not await is_subscribed(client, message):
            # try:
            #     invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
            # except ChatAdminRequired:
            #     logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
            #     return
            btn = [[
                InlineKeyboardButton("Cʜᴀɴɴᴇʟ 1", url=f't.me/The_Happy_Hour_Hindi'),
                InlineKeyboardButton("Cʜᴀɴɴᴇʟ 2", url=f't.me/The_Happy_Hours')
              ]]
    
            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    pre = 'checksubp' if kk == 'filep' else 'checksub' 
                    btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            await client.send_message(
                chat_id=message.from_user.id,
                text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀɴᴅ ᴍᴏᴠɪᴇ ғɪʟᴇ...✅**",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
                )
            return
        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('📚 ʙᴀᴄᴋᴜᴘ', url=CHNL_LNK),
                        InlineKeyboardButton('🌿 ɢʀᴏᴜᴘ', url=GRP_LNK),
                        InlineKeyboardButton('🌈 ᴄʜᴀɴɴᴇʟ', url=f'http://t.me/The_Happy_Hour_Hindi')
                    ],[
                        InlineKeyboardButton('🏕️ ᴀʙᴏᴜᴛ', callback_data='about'),
                        InlineKeyboardButton('🍾 ᴄᴏᴍᴍᴀɴᴅꜱ', callback_data='seeplans'),
                        InlineKeyboardButton('🍁 ꜱᴛᴀᴛꜱ', callback_data='stats')
                    ],[
                        InlineKeyboardButton('🌹 ʀᴇғғᴇʀ 🌹', callback_data='reffer'),
                        ]]
            if IS_VERIFY or IS_SHORTLINK is True:
                buttons.append([
                    InlineKeyboardButton('🏡 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 🏡', callback_data='seeplans')
                ])
            if TOP_SEARCH is True:
                buttons.append([
                    InlineKeyboardButton("🎁 ᴍᴏᴠɪᴇ sᴜɢɢᴇsᴛɪᴏɴ's 🎁", callback_data='movie_suggestion')
                ])
            reply_markup = InlineKeyboardMarkup(buttons)
            current_time = datetime.now(pytz.timezone(TIMEZONE))
            curr_time = current_time.hour        
            if curr_time < 12:
                gtxt = "ɢᴏᴏᴅ ᴍᴏʀɴɪɴɢ 👋" 
            elif curr_time < 17:
                gtxt = "ɢᴏᴏᴅ ᴀғᴛᴇʀɴᴏᴏɴ 👋" 
            elif curr_time < 21:
                gtxt = "ɢᴏᴏᴅ ᴇᴠᴇɴɪɴɢ 👋"
            else:
                gtxt = "ɢᴏᴏᴅ ɴɪɢʜᴛ 👋"
            # m=await message.reply_sticker("CAACAgUAAxkBAAEkohxmOzL_8-HJRwudONzAED-tMt27LQACRwADJpleD38508ect3TIHgQ") 
            # await asyncio.sleep(2)
            # await m.delete()
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        if len(message.command) == 2 and message.command[1] in ["premium"]:
            buttons = [[
                        InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ', url=f"https://t.me/Master_Jiraya_Bot")
                      ],[
                        InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=(SUBSCRIPTION),
                caption=script.PREPLANS_TXT.format(message.from_user.mention),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return  
        if message.command[1].startswith("reff_"):
            try:
                user_id = int(message.command[1].split("_")[1])
            except ValueError:
                await message.reply_text("Invalid refer!")
                return
            if user_id == message.from_user.id:
                await message.reply_text("Yᴏᴜ Cᴀɴ'ᴛ Rᴇғᴇʀ Yᴏᴜʀsᴇʟғ 🤣!\n\nवो लिंक किसी और को भेजे....!!\n\nकोई भी 10 लोग आपके लिंक पे क्लिक करेंगे तो आपको 1 month फ्री प्रीमियम मिलेगा...✅")
                return
            if db2.is_user_in_list(message.from_user.id):
                await message.reply_text("आप पहले भी इस bot का use कर चुके है....🫠")
                return
            try:
                uss = await client.get_users(user_id)
            except Exception:
                return 	    
            db2.add_user(message.from_user.id)
            fromuse = db2.get_refer_points(user_id) + 10
            db2.add_refer_points(user_id, fromuse)
            await message.reply_text(f"<b>My Name Is Minato⚡.\n\nI am provide Movie & Series 🥲, Just Send Movie Name & Get in Two Seconds 🌿.\n\ninvited by {uss.mention}</b>")
            await client.send_message(user_id, f"<b>Congratulations 🥳 You won 10 Referral point because You Invited {message.from_user.mention}</b>") 
            if fromuse == USER_POINT:
                await db.give_referal(user_id)
                db2.add_refer_points(user_id, 0) 
                await client.send_message(chat_id=user_id,
                    text=f"<b>ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ {uss.mention} 🥳\n\nʏᴏᴜ ɢᴏᴛ 1 ᴍᴏɴᴛʜ ᴘʀᴇᴍɪᴜᴍ....🌿\nʙᴇᴄᴀᴜꜱᴇ ʏᴏᴜ ɪɴᴠᴀʟɪᴅ 10 ᴜꜱᴇʀꜱ....😘\n\nYour Premium Ditels --> /myplan </b>", disable_web_page_preview=True              
                    )
                for admin in ADMINS:
                    await client.send_message(chat_id=REQST_CHANNEL, text=f"Sᴜᴄᴄᴇss ғᴜʟʟʏ reffral ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ ᴛʜɪs ᴜsᴇʀ:\n\nuser Nᴀᴍᴇ: {uss.mention}\n\nUsᴇʀ ɪᴅ: {uss.id}!")	
                return
        if message.command[1] == "movie_suggestion":
            if TOP_SEARCH is True:
                m = await message.reply_text(f"<b>Finding Movie's List For You...😘</b>")
                top_messages = await db3.get_top_messages(30)

                truncated_messages = set()  # Use a set instead of a list
                for msg in top_messages:
                    if len(msg) > 30:
                        truncated_messages.add(msg[:30 - 3].lower().title() + "...")  # Convert to lowercase, capitalize and add to set
                    else:
                        truncated_messages.add(msg.lower().title())  # Convert to lowercase, capitalize and add to set

                keyboard = []
                for i in range(0, len(truncated_messages), 2):
                    row = list(truncated_messages)[i:i+2]  # Convert set to list for indexing
                    keyboard.append(row)
    
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, placeholder="Most searches of the day")
                sf=await message.reply_text(f"<b>ʜᴇʀᴇ ɪs ᴛʜʀ ʟɪsᴛ ᴏғ ᴍᴏᴠɪᴇ's ɴᴀᴍᴇ 👇👇</b>", reply_markup=reply_markup)
                await m.delete()
                await asyncio.sleep(60*60) 
                await sf.delete()
                return
            else:
                await message.reply("ᴛᴏᴘ sᴇᴀʀᴄʜᴇs ᴄᴜʀʀᴇɴᴛʟʏ ᴏғғ")
        data = message.command[1]
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""
        if data.split("-", 1)[0] == "BATCH":
            sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)
            if not msgs:
                file = await client.download_media(file_id)
                try: 
                    with open(file) as file_data:
                        msgs=json.loads(file_data.read())
                except:
                    await sts.edit("Fᴀɪʟᴇᴅ")
                    return await client.send_message(LOG_CHANNEL, "Uɴᴀʙʟᴇ Tᴏ Oᴘᴇɴ Fɪʟᴇ.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
            for msg in msgs:
                title = msg.get("title")
                size=get_size(int(msg.get("size", 0)))
                f_caption=msg.get("caption", "")
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                try:
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                        reply_markup=InlineKeyboardMarkup(
                            [
                             [
                              InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                           ],[
                            InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer'),
                            InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                        ]
                             ]
                        )
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    logger.warning(f"Floodwait of {e.x} sec.")
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                        reply_markup=InlineKeyboardMarkup(
                            [
                             [
                              InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                              
                           ],[
                              InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer'),
                            InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                             ]
                            ]
                        )
                    )
                except Exception as e:
                    logger.warning(e, exc_info=True)
                    continue
                await asyncio.sleep(1) 
            await sts.delete()
            return
        elif data.split("-", 1)[0] == "DSTORE":
            sts = await message.reply("<b>Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            b_string = data.split("-", 1)[1]
            decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
            try:
                f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
            except:
                f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
                protect = "/pbatch" if PROTECT_CONTENT else "batch"
            diff = int(l_msg_id) - int(f_msg_id)
            async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
                if msg.media:
                    media = getattr(msg, msg.media.value)
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                        except Exception as e:
                            logger.exception(e)
                            f_caption = getattr(msg, 'caption', '')
                    else:
                        media = getattr(msg, msg.media.value)
                        file_name = getattr(media, 'file_name', '')
                        f_caption = getattr(msg, 'caption', file_name)
                    try:
                        await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                    except Exception as e:
                        logger.exception(e)
                        continue
                elif msg.empty:
                    continue
                else:
                    try:
                        await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                    except Exception as e:
                        logger.exception(e)
                        continue
                await asyncio.sleep(1) 
            return await sts.delete()
                    
        elif data.split("-", 1)[0] == "verify":
            userid = data.split("-", 2)[1]
            token = data.split("-", 3)[2]
            fileid = data.split("-", 3)[3]
            if str(message.from_user.id) != str(userid):
                return await message.reply_text(
                    text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                    protect_content=True if PROTECT_CONTENT else False
                )
            is_valid = await check_token(client, userid, token)
            if is_valid == True:
                if fileid == "all":
                    btn = [[
                        InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ", callback_data=f"checksub#send_all")
                    ]]
                    await verify_user(client, userid, token)
                    await message.reply_text(
                        text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.</b>",
                        protect_content=True if PROTECT_CONTENT else False,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                btn = [[
                    InlineKeyboardButton("Get File", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
                ]]
                await message.reply_text(
                    text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                await verify_user(client, userid, token)
                return
            else:
                return await message.reply_text(
                    text="<b>Iɴᴠᴀʟɪᴅ ʟɪɴᴋ ᴏʀ Exᴘɪʀᴇᴅ ʟɪɴᴋ !</b>",
                    protect_content=True if PROTECT_CONTENT else False
                )

        if data.startswith("TheHappyHour"):
            btn = [[
                InlineKeyboardButton('📸 sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ 📸', url="https://t.me/Master_Jiraya_Bot")
            ],[
                InlineKeyboardButton('☘️ ꜰᴜᴛᴜʀᴇ ☘️', url="https://graph.org/The-Happy-Hour-12-22-2"),
                InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await message.reply_photo(
            photo="https://telegra.ph/file/71be8b45fd8da04a6531c.jpg",
            caption="""<b>
        <a href='https://graph.org/The-Happy-Hour-12-22-2'>💥 ᴘʀᴇᴍɪᴜᴍ ᴘʀɪᴄᴇ 💥
        
1 Wᴇᴇᴋ = [50 + 0] Rs
1 Mᴏɴᴛʜ = [50 + 10] Rs
2 Mᴏɴᴛʜ = [50 + 30] Rs

🎁 ᴘʀᴇᴍɪᴜᴍ ꜰᴜᴛᴜʀᴇ ᴄʟɪᴄᴋ\nʜᴇᴀʀᴇ ᴛᴏ ʀᴇᴀᴅ
ㅤㅤㅤㅤㅤ</a></b>""",
                reply_markup=reply_markup
            )
            return

        if data.startswith("reffer"):
            user_id = message.from_user.id
            total = db2.get_refer_points(user_id)

            btn = [[
                InlineKeyboardButton(f"invite 🔗", url=f"https://telegram.me/share/url?url=https://telegram.me/{temp.U_NAME}=reff_{user_id}"),
                InlineKeyboardButton(f"⏳{total}", callback_data=f"show_reff"),
                InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await message.reply_photo(
            photo="https://i2f9m2t2.rocketcdn.me/wp-content/uploads/2014/04/shutterstock_175386392.jpg",
            caption=f"<b>ʀᴇғᴇʀʀᴇ ʏᴏᴜʀ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғʀɪᴇɴᴅs, ғᴀᴍɪʟʏ, ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ 1 ᴍᴏɴᴛʜ\n\nʀᴇғᴇʀᴀʟ ʟɪɴᴋ - https://telegram.me/{temp.U_NAME}?start=reff_{user_id}\n\nsʜᴀʀᴇ ᴛʜɪs ʟɪɴᴋ ᴡɪᴛʜ ʏᴏᴜʀ ғʀɪᴇɴᴅs, ᴇᴀᴄʜ ᴛɪᴍᴇ ᴛʜᴇʏ ᴊᴏɪɴ,  ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ 10 ʀᴇғғᴇʀᴀʟ ᴘᴏɪɴᴛs ᴀɴᴅ ᴀғᴛᴇʀ {USER_POINT} ᴘᴏɪɴᴛs ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ 1 ᴍᴏɴᴛʜ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.\n\nʙᴜʏ ᴘᴀɪᴅ ᴘʟᴀɴ ʙʏ - /premium</b>",
                reply_markup=reply_markup
            )
            return
        
        if data.startswith("sendfiles"):
            chat_id = int("-" + file_id.split("-")[1])
            userid = message.from_user.id if message.from_user else None
            g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
            k = await client.send_message(chat_id=message.from_user.id,text=f"<b>Get All Files in a Single Click!!!\n\n📂 ʟɪɴᴋ ➠ : {g}</b>", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('📁 ᴍᴏᴠɪᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📁', url=g)
                        ], [
                            InlineKeyboardButton('🤔 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🤔', url=await get_tutorial(chat_id))
                        ]
                    ]
                )
            )
            return
        elif data.startswith("short"):
            user = message.from_user.id
            if temp.SHORT.get(user)==None:
                await message.reply_text("ᴅᴏɴ'ᴛ ᴄʟɪᴄᴋ ᴏᴛʜᴇʀ ʀᴇsᴜʟᴛ") 
            else:
                chat_id = temp.SHORT.get(message.from_user.id)
            settings = await get_settings(chat_id)
            if settings['is_shortlink'] and not await db.has_premium_access(message.from_user.id):
                files_ = await get_file_details(file_id)
                files = files_[0]
                g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
                k = await client.send_message(chat_id=message.from_user.id,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}.</i></b>", 
                reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton('📂 ᴍᴏᴠɪᴇ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📂', url=g)], 
                            [InlineKeyboardButton('🤔 Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ 🤔', url=await get_tutorial(chat_id))]]))
                return
            else:
                files = await get_file_details(file_id)
                if not files:
                    return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
                filesarr = []
                for file in files:
                    file_id = file.file_id
                    files_ = await get_file_details(file_id)
                    files = files_[0]
                    title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
                    size=get_size(files.file_size)
                    f_caption=files.caption
                    if CUSTOM_FILE_CAPTION:
                        try:
                            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                        except Exception as e:
                            logger.exception(e)
                            f_caption=f_caption
                    if f_caption is None:
                        f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"
                msg=await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=InlineKeyboardMarkup([[
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")],
                          [InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer')]]))
                return 
        elif data.startswith("all"):
            files = temp.GETALL.get(file_id)
            if not files:
                return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
            filesarr = []
            for file in files:
                file_id = file.file_id
                files_ = await get_file_details(file_id)
                files1 = files_[0]
                title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))
                size=get_size(files1.file_size)
                f_caption=files1.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"
                if IS_VERIFY and not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id):
                    btn = [[
                            InlineKeyboardButton("♻️ Vᴇʀɪғʏ ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                            InlineKeyboardButton("⚠️ Hᴏᴡ Tᴏ Vᴇʀɪғʏ ⚠️", url=HOW_TO_VERIFY)
                            ],[
                            InlineKeyboardButton("🏕️ ʀᴇᴍᴏᴠᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 🏕️", url="https://t.me/Hidden_Technology_Bot?start=TheHappyHour")
                            ]]
                    await message.reply_text(
                        text="You Are Not Verifid Today...",
                        protect_content=True if pre == 'filep' else False,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                       ],[
                              InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer')       
                             ]
                        ]
                    )
                )
                #filesarr.append(msg)
            #k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie Files/Videos will be deleted in <b><u>10 mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>")
            #for x in filesarr:
                #await asyncio.sleep(300)
                #await x.delete()
            #await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
            #return   
        
        files_ = await get_file_details(file_id)           
        if not files_:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:
                
                if IS_VERIFY and not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id):
                    btn = [[
                        InlineKeyboardButton("♻️ Vᴇʀɪғʏ ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                        InlineKeyboardButton("⚠️ Hᴏᴡ Tᴏ Vᴇʀɪғʏ ⚠️", url=HOW_TO_VERIFY)
                        ],[
                        InlineKeyboardButton("🏕️ ʀᴇᴍᴏᴠᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 🏕️", url="https://t.me/Hidden_Technology_Bot?start=TheHappyHour")
                    ]]
                    await message.reply_text(
                        text="You Are Not Verified Today...Plzz Verifiy And Get Movie...",
                        protect_content=True if PROTECT_CONTENT else False,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                         [
                          InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                  
                       ],[
                              InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer'),
                             InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                             ]
                        ]
                    )
                )
                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = ' '.join(filter(lambda x: not x.startswith('Linkz') and not x.startswith('boxoffice') and not x.startswith('Original') and not x.startswith('Villa') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('@') and not x.startswith('www'), file.file_name.split()))
                size=get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(f_caption)
                # del_msg = await message.reply_text("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>")
                # safari = msg
                # await asyncio.sleep(300)
                # await safari.delete()
                # await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")
                return
            except:
                pass
            return await message.reply('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = ' '.join(filter(lambda x: not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links') and not x.startswith('boxoffice') and not x.startswith('Original') and not x.startswith('Villa') and not x.startswith('@') and not x.startswith('www'), files.file_name.split()))
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{' '.join(filter(lambda x: not x.startswith('Linkz') and not x.startswith('{') and not x.startswith('Links')and not x.startswith('boxoffice') and not x.startswith('Original') and not x.startswith('Villa') and not x.startswith('@') and not x.startswith('www'), files.file_name.split()))}"
        
        if IS_VERIFY and not await check_verification(client, message.from_user.id) and not await db.has_premium_access(message.from_user.id):
            btn = [[
                InlineKeyboardButton("♻️ Vᴇʀɪғʏ ♻️", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                InlineKeyboardButton("⚠️ Hᴏᴡ Tᴏ Vᴇʀɪғʏ ⚠️", url=HOW_TO_VERIFY)
                ],[
                InlineKeyboardButton("🏕️ ʀᴇᴍᴏᴠᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 🏕️", url="https://t.me/Hidden_Technology_Bot?start=TheHappyHour")
            ]]
            await message.reply_text(
                text="You Are Not Verifird Today...Plzz Veifiy And Get Movie...",
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        msg=await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                 InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")  
                 ],[
                 InlineKeyboardButton("🌹 ʀᴇғғᴇʀ 🌹", url='https://t.me/Hidden_Technology_Bot?start=reffer'),
                 InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                 ]
                ]
            )
        )
        # del_msg = await message.reply_text("<b>⚠️ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀғᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs\n\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ғɪʟᴇ sᴏᴍᴇᴡʜᴇʀᴇ ʙᴇғᴏʀᴇ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ..</b>")
        # safari = msg
        # await asyncio.sleep(300)
        # await safari.delete()
        # await del_msg.edit_text("<b>ʏᴏᴜʀ ғɪʟᴇ ᴡᴀs ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀғᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛ 📢</b>")
        return   
    except Exception as e:
        print (e) 
        # await message.reply(f"error found {e}") 
        
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴛʏᴘᴇ ᴏғ CHANNELS")

    text = '📑 **Iɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Tʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs.\nDᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yᴇs", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cᴀɴᴄᴇʟ", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Eᴠᴇʀʏᴛʜɪɴɢ's Gᴏɴᴇ")
    await message.message.edit('Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ Aʟʟ Tʜᴇ Iɴᴅᴇxᴇᴅ Fɪʟᴇs.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Yᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. Usᴇ /connect {message.chat.id} ɪɴ PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ !", quote=True)
                return
        else:
            await message.reply_text("I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs !", quote=True)
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
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Tᴇxᴛ' if settings["button"] else 'Bᴜᴛᴛᴏɴ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Iᴍᴅʙ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Wᴇʟᴄᴏᴍᴇ Msɢ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Mᴀx Bᴜᴛᴛᴏɴs',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'SʜᴏʀᴛLɪɴᴋ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
        ]

        btn = [[
                InlineKeyboardButton("Oᴘᴇɴ Hᴇʀᴇ ↓", callback_data=f"opnsetgrp#{grp_id}"),
                InlineKeyboardButton("Oᴘᴇɴ Iɴ PM ⇲", callback_data=f"opnsetpm#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ ?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Cʜᴇᴄᴋɪɴɢ ᴛᴇᴍᴘʟᴀᴛᴇ...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Yᴏᴜ ᴀʀᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. Usᴇ /connect {message.chat.id} ɪɴ PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True)
                return
        else:
            await message.reply_text("I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs!", quote=True)
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

    if len(message.command) < 2:
        return await sts.edit("Nᴏ Iɴᴘᴜᴛ!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʜᴀɴɢᴇᴅ ᴛᴇᴍᴘʟᴀᴛᴇ ғᴏʀ {title} ᴛᴏ:\n\n{template}")


@Client.on_message((filters.command(["request", "Request", "Report", "report"]) | filters.regex("#request") | filters.regex("#Request") | filters.regex("#Report") | filters.regex("#report")))
#@Client.on_message(filters.command('request') & filters.incoming & filters.text)
async def requests(client, message):
    search = message.text
    requested_movie = search.replace("/request", "").replace("/Request", "").replace("/Report", "").replace("/report", "").strip()
    user_id = message.from_user.id
    if not requested_movie:
        m=await message.reply_text("<b>अगर कोई मूवी ना मिले तो.....🤒\nआप Admin को रिर्पोट भेज सकते हो...📚\nइस तरह से रिपोर्ट भेजे....👇\n\n/report Pushpa 2021\n/report Chhichhore 2019\n/report Vikings S01 E03\n/report Money Heist S03 E05\n\n👉 मूवी का year भी लिखे... 👀\n\n━━━━━━━━━━━━━━━━━━\n\nɪꜰ ᴍᴏᴠɪᴇ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ʙᴏᴛ...🤒\nᴛʜᴇɴ ꜱᴇɴᴅ ʀᴇᴘᴏʀᴛ ᴛᴏ ᴀᴅᴍɪɴ...📚\nʜᴏᴡ ᴛᴏ ꜱᴇɴᴅ ʀᴇᴘᴏʀᴛ...👇\n\n/report Pushpa 2021\n/report Chhichhore 2019\n/report Vikings S01 E03\n/report Money Heist S03 E05\n\n👉 ᴅᴏɴ'ᴛ ꜰᴏʀɢᴇᴛ ʀᴇʟᴇᴀꜱᴇ ʏᴇᴀʀ 👀</b>")
        await asyncio.sleep(30)
        await m.delete()
        return
    a=await message.reply_text(text=f"ʏᴏᴜʀ ʀᴇᴘᴏʀᴛ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ\nꜱᴇɴᴅᴇᴅ ᴛᴏ ᴀᴅᴍɪɴ...✅")
    await asyncio.sleep(3)
    await a.delete()
    await client.send_message(REQST_CHANNEL,f"📝 #REQUESTED_CONTENT 📝\n\nʙᴏᴛ - {temp.B_NAME}\nɴᴀᴍᴇ - {message.from_user.mention} (<code>{message.from_user.id}</code>)\nRᴇǫᴜᴇꜱᴛ - <code>{requested_movie}</code>",
    reply_markup=InlineKeyboardMarkup(
        [[
            InlineKeyboardButton('Not Release📅', callback_data=f"not_release:{user_id}:{requested_movie}"),
        ],[
            InlineKeyboardButton('Already Available🕵️', callback_data=f"already_available:{user_id}:{requested_movie}"),
            InlineKeyboardButton('Not Available🙅', callback_data=f"not_available:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('Uploaded Done✅', callback_data=f"uploaded:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('Series Msg📝', callback_data=f"series:{user_id}:{requested_movie}"),
            InlineKeyboardButton('Spell Msg✍️', callback_data=f"spelling_error:{user_id}:{requested_movie}")
        ],[
            InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')]
        ]))
        
@Client.on_message(filters.command("send_msg_usr") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Reply With Your Massage\n\nEx : /send ᴜsᴇʀɪᴅ</b>")
@Client.on_message(filters.command("ucast") & filters.user(ADMINS))
async def send_mssg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ɪᴅ. Fᴏʀ ᴇɢ: /send ᴜsᴇʀɪᴅ</b>")
@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. Iᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ PM!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("set_urlshortlink"))
async def shortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>ʜᴇʏ {message.from_user.mention}, ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>ᴄᴏᴍᴍᴀɴᴅ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ !\nɢɪᴠᴇ ᴍᴇ ᴄᴏᴍᴍᴀɴᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ꜱʜᴏʀᴛɴᴇʀ ᴡᴇʙꜱɪᴛᴇ ᴀɴᴅ ᴀᴘɪ.\n\nꜰᴏʀᴍᴀᴛ : <code>/shortlink krishnalink.com c8dacdff6e91a8e4b4f093fdb4d8ae31bc273c1a</code>")
    reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
    shortlink_url = re.sub(r"https?://?", "", shortlink_url)
    shortlink_url = re.sub(r"[:/]", "", shortlink_url)
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ꜱʜᴏʀᴛʟɪɴᴋ ꜰᴏʀ <code>{title}</code>.\n\nꜱʜᴏʀᴛʟɪɴᴋ ᴡᴇʙꜱɪᴛᴇ : <code>{shortlink_url}</code>\nꜱʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ : <code>{api}</code></b>")
 
@Client.on_message(filters.command("urlshortlink_off"))
async def offshortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        await save_group_settings(grpid, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
        return await message.reply_text("ꜱʜᴏʀᴛʟɪɴᴋ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅɪꜱᴀʙʟᴇᴅ.")
    
@Client.on_message(filters.command("urlshortlink_on"))
async def onshortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴛʜɪꜱ ᴀɢᴀɪɴ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        await save_group_settings(grpid, 'is_shortlink', True)
        ENABLE_SHORTLINK = True
        return await message.reply_text("ꜱʜᴏʀᴛʟɪɴᴋ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ.")
        
@Client.on_message(filters.command("urlshortlink_info"))
async def ginfo(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>{message.from_user.mention},\n\nᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    chat_id=message.chat.id
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
#     if 'shortlink' in settings.keys():
#         su = settings['shortlink']
#         sa = settings['shortlink_api']
#     else:
#         return await message.reply_text("<b>Shortener Url Not Connected\n\nYou can Connect Using /shortlink command</b>")
#     if 'tutorial' in settings.keys():
#         st = settings['tutorial']
#     else:
#         return await message.reply_text("<b>Tutorial Link Not Connected\n\nYou can Connect Using /set_tutorial command</b>")
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        settings = await get_settings(chat_id) #fetching settings for group
        if 'shortlink' in settings.keys() and 'tutorial' in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            st = settings['tutorial']
            return await message.reply_text(f"<b><u>ᴄᴜʀʀᴇɴᴛ  ꜱᴛᴀᴛᴜꜱ<u> 📊\n\nᴡᴇʙꜱɪᴛᴇ : <code>{su}</code>\n\nᴀᴘɪ : <code>{sa}</code>\n\nᴛᴜᴛᴏʀɪᴀʟ : {st}</b>", disable_web_page_preview=True)
        elif 'shortlink' in settings.keys() and 'tutorial' not in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            return await message.reply_text(f"<b><u>ᴄᴜʀʀᴇɴᴛ  ꜱᴛᴀᴛᴜꜱ<u> 📊\n\nᴡᴇʙꜱɪᴛᴇ : <code>{su}</code>\n\nᴀᴘɪ : <code>{sa}</code>\n\nᴜꜱᴇ /set_tutorial ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ꜱᴇᴛ ʏᴏᴜʀ ᴛᴜᴛᴏʀɪᴀʟ.")
        elif 'shortlink' not in settings.keys() and 'tutorial' in settings.keys():
            st = settings['tutorial']
            return await message.reply_text(f"<b>ᴛᴜᴛᴏʀɪᴀʟ : <code>{st}</code>\n\nᴜꜱᴇ  /shortlink  ᴄᴏᴍᴍᴀɴᴅ  ᴛᴏ  ᴄᴏɴɴᴇᴄᴛ  ʏᴏᴜʀ  ꜱʜᴏʀᴛɴᴇʀ</b>")
        else:
            return await message.reply_text("ꜱʜᴏʀᴛɴᴇʀ ᴀɴᴅ ᴛᴜᴛᴏʀɪᴀʟ ᴀʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ.\n\nᴄʜᴇᴄᴋ /set_tutorial  ᴀɴᴅ  /shortlink  ᴄᴏᴍᴍᴀɴᴅ.")

@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋꜱ ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    if len(message.command) == 1:
        return await message.reply("<b>ɢɪᴠᴇ ᴍᴇ ᴀ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.\n\nᴜꜱᴀɢᴇ : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ\n\nʏᴏᴜʀ ɢʀᴏᴜᴘ : {title}\n\nʏᴏᴜʀ ᴛᴜᴛᴏʀɪᴀʟ : <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ɪɴᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ !\nᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"ʏᴏᴜ'ʀᴇ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ, ᴛᴜʀɴ ᴏꜰꜰ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>ᴏɴʟʏ ɢʀᴏᴜᴘ ᴏᴡɴᴇʀ ᴏʀ ᴀᴅᴍɪɴ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ !</b>")
    else:
        pass
    reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ✅</b>")

@Client.on_message(filters.command("refresh_argv") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="<b><i>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛɪɴɢ</i></b>", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("<b><i><u>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛᴇᴅ</u> ✅</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command('delete_reffer') & filters.user(ADMINS))
async def remove_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('give me  user id')
    user_id = message.command[1]
    try:
        user_id = int(user_id)
    except:
        user_id = user_id
    try:
        user_exit = db2.is_user_in_list(user_id)   
        db2.remove_user(user_id)
        if not user_exit:
            await message.reply("oops invalid user id") 
        else:
            await message.reply(
                text='user removed in refferal list'
            )
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('reffer') )
async def refer(bot, message):
    try:
        user_id = message.from_user.id
        total = db2.get_refer_points(user_id)
        btn = [[
                InlineKeyboardButton(f"invite 🔗", url=f"https://telegram.me/share/url?url=https://telegram.me/{temp.U_NAME}?start=reff_{user_id}"),
                InlineKeyboardButton(f"⏳{total}", callback_data=f"show_reff"),
                InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
            ]]
        reply_markup = InlineKeyboardMarkup(btn)
        await message.reply_photo(
            photo="https://i2f9m2t2.rocketcdn.me/wp-content/uploads/2014/04/shutterstock_175386392.jpg",
            caption=f"<b>ʀᴇғᴇʀʀᴇ ʏᴏᴜʀ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғʀɪᴇɴᴅs, ғᴀᴍɪʟʏ, ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ɢʀᴏᴜᴘ ᴛᴏ ɢᴇᴛ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ғᴏʀ 1 ᴍᴏɴᴛʜ\n\nʀᴇғᴇʀᴀʟ ʟɪɴᴋ - https://telegram.me/{temp.U_NAME}?start=reff_{user_id}\n\nsʜᴀʀᴇ ᴛʜɪs ʟɪɴᴋ ᴡɪᴛʜ ʏᴏᴜʀ ғʀɪᴇɴᴅs, ᴇᴀᴄʜ ᴛɪᴍᴇ ᴛʜᴇʏ ᴊᴏɪɴ,  ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ 10 ʀᴇғғᴇʀᴀʟ ᴘᴏɪɴᴛs ᴀɴᴅ ᴀғᴛᴇʀ {USER_POINT} ᴘᴏɪɴᴛs ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ 1 ᴍᴏɴᴛʜ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.\n\nʙᴜʏ ᴘᴀɪᴅ ᴘʟᴀɴ ʙʏ - /premium</b>",
            reply_markup=reply_markup
        ),
    except Exception as e:
        print (e) 
        await message.reply(f"error found \n\n{e}")
