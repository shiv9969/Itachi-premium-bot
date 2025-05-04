import pymongo
from info import DATABASE_URI, DATABASE_NAME
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }
    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except Exception:
        logger.exception('Error in add_filter')


async def get_filter(group_id, name):
    mycol = mydb[str(group_id)]
    result = mycol.find_one({"text": name})
    if not result:
        return None
    return {
        "reply_text": result.get("reply"),
        "btn": result.get("btn"),
        "file_id": result.get("file"),
        "alert": result.get("alert")
    }


async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    query = mycol.find({"text": name})
    for file in query:
        return file['reply'], file['btn'], file.get('alert'), file['file']
    return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]
    return [file['text'] for file in mycol.find()]


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    result = mycol.delete_one({'text': text})
    if result.deleted_count == 1:
        await message.reply_text(f"'`{text}`' deleted.", quote=True, parse_mode=enums.ParseMode.MARKDOWN)
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return
    try:
        mydb[str(group_id)].drop()
        await message.edit_text(f"All filters from {title} have been removed")
    except:
        await message.edit_text("Couldn't remove filters!")


async def count_filters(group_id):
    mycol = mydb[str(group_id)]
    return mycol.count_documents({})
    

async def filter_stats():
    collections = [col for col in mydb.list_collection_names() if col != "CONNECTION"]
    totalcount = sum(mydb[col].count_documents({}) for col in collections)
    return len(collections), totalcount
