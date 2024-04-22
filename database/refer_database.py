import re
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio
from pymongo import MongoClient
from info import DATABASE_NAME2, DATABASE_URI2
import time
import datetime



class Database:

    def __init__(self, uri2, database_name2):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri2)
        self.db = self._client[database_name2]
        self.mydb = self._client["referal_user"]

async def referal_add_user(self, user_id, ref_user_id):
    user_db = self.mydb[str(user_id)]
    user = {'_id': ref_user_id}
    try:
        user_db.insert_one(user)
        return True
    except DuplicateKeyError:
        return False
    

async def get_referal_all_users(self, user_id):
    user_db = self.mydb[str(user_id)]
    return user_db.find()
    
async def get_referal_users_count(self, user_id):
    user_db = self.mydb[str(user_id)]
    count = user_db.count_documents({})
    return count
    

async def delete_all_referal_users(self, user_id):
    user_db = self.mydb[str(user_id)]
    user_db.delete_many({}) 


db = Database(DATABASE_URI2, DATABASE_NAME2)
