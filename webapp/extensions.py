import os
from dotenv import load_dotenv
from pymongo import MongoClient
from ossapi import OssapiV2
load_dotenv()


MONGO_URL = os.getenv("MONGO_URI")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def NewMongoConnection() -> MongoClient:
    try:
        return MongoClient(host=MONGO_URL)
    except ConnectionError:
        if MONGO_URL == None:
            raise Exception("MONGO_URI not set. Check environment variables.")
        else:
            raise Exception(f"Unable to connect to MongoDB Client.")
        
def NewOsuApiConnection() -> OssapiV2:
    return OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)