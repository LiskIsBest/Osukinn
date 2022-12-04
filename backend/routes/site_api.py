from flask import Blueprint, request
from pymongo import MongoClient
from bson import json_util
import json

from ..models.models import user_data_class

from ossapi import *

import datetime

from dotenv import load_dotenv
import os

load_dotenv() 

CLIENT_ID: int = os.environ.get("CLIENT_ID")
CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET")
REDIRECT_URL: str = os.environ.get("REDIRECT_URL")

api = Blueprint("api",__name__)

""" Returns User data in dictionary """
def makeUser(username: str) -> user_data_class:

    # osu api connection
    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

    # pull user id
    user_id = osuApi.user(username).id

    # Check if username is valid. if not set name to "None"
    match username:
        case "":
            username = "None"
        case _:
            try:
                osuApi.user(username).username
            except ValueError:
                username = "None"

    # function to pull global rank for specified gamemode. 9_999_999_999 used as No rank found value
    getRank = lambda mode, username: 9_999_999_999 if (osuApi.user(username,mode=mode).rankHistory == None) else osuApi.user(username,mode=mode).rankHistory.data[-1]

    return user_data_class(
            user_id = user_id,
            username = osuApi.user(user_id).username,
            osu_rank = getRank(username=username,mode="osu"), 
            mania_rank = getRank(username=username,mode="mania"),
            taiko_rank = getRank(username=username,mode="taiko"),
            fruits_rank = getRank(username=username,mode="fruits"),
            avatar_url = osuApi.user(username).avatar_url,
            last_time_refreshed = str(datetime.datetime.now().replace(microsecond=0))
            ).dict()

def parse_json(data):
    return json.loads(json_util.dumps(data))

@api.route("<string:username>",methods=["GET","PUT"])
def data(username) -> dict:

    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

    client = MongoClient(os.environ.get("MONGO_URI"))
    db = client.userUsernames
    user_database = db.users

    request_username: str = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(request_username).id
    except:
        # id for None user
        user_id = 1516945

    match request.method:
        case "GET":
            if user_database.find_one({"user_id":user_id}) != None:
                user_data = user_database.find_one({"user_id":user_id})
            else:
                user_data = makeUser(username=user_id)
                user_database.insert_one(user_data)

            return parse_json(user_data)

        case "PUT":
            user_database.update_one({"user_id":user_id},{ "$set" :makeUser(username=user_id)})
            return '', 204