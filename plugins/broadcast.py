
from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, get_users
import asyncio
from pyrogram.errors import FloodWait

@Client.on_message(filters.command('jkbc') & filters.user(ADMINS))
async def user_broadcast(bot, message):
    if not message.reply_to_message:
       return await message.reply("Use this command as a reply to any message!")
    m=await message.reply("Broadcasting...")   

    count, users = await get_users()
    stats     = "⚡ Broadcast Processing.."
    br_msg    = message.reply_to_message
    total     = count       
    remaining = total
    success   = 0
    failed    = 0    
     
    for user in users:
        chat_id = user["_id"]
        trying = await copy_msgs(br_msg, chat_id)
        if trying==False:
           failed+=1
           remaining-=1
        else:
           success+=1
           remaining-=1
        try:                                     
           await m.edit(script.BROADCAST.format(stats, total, remaining, success, failed))                                 
        except:
           pass
    stats = "✅ Broadcast Completed"
    await m.reply(script.BROADCAST.format(stats, total, remaining, success, failed)) 
    await m.delete()                                


async def copy_msgs(br_msg, chat_id):
    try:
       await br_msg.copy(chat_id)       
    except FloodWait as e:
       await asyncio.sleep(e.value)
       await copy_msgs(br_msg, chat_id)
    except: 
       return False      

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
# https://t.me/GetTGLink/4178
async def verupikkals(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed =0

    success = 0
    async for user in users:
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked+=1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def grp_brodcst(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed =0

    success = 0
    async for chat in chats:
        pti, sh = await broadcast_messages(int(chat['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked+=1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Chats {total_chats}\nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Chats {total_chats}\nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}")
