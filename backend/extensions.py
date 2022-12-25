import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(host=os.environ.get("MONGO_URI"))