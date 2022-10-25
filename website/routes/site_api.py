from flask import Blueprint, request, current_app
from flask_pymongo import PyMongo

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
def makeUser(username: str) -> dict:

    # osu api connection
    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)
    
    # Check if username is valid. if not set name to "None"
    if username == "":
        username = "None"
    else:
        try:
            osuApi.user(username).username
        except ValueError:
            username = "None"
    
    # pull user id
    user_id = osuApi.user(username).id

    # function to pull global rank for specified gamemode. 9_999_999_999 used as No rank found value
    getRank = lambda mode, username: 9_999_999_999 if (osuApi.user(username,mode=mode).rankHistory == None) else osuApi.user(username,mode=mode).rankHistory.data[-1]
    
    # dictionary matching MongoDB document layout
    return {"_id": user_id, 
            "username": osuApi.user(user_id).username,
            "osu_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "fruits_rank": getRank(username=username,mode="fruits"),
            "avatar_url": osuApi.user(username).avatar_url,
            "last_time_refreshed": str(datetime.datetime.now().replace(microsecond=0))
            }

@api.route("<string:username>",methods=["GET","PUT"])
def data(username) -> dict:

    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

    mongo = PyMongo(current_app)
    user_database = mongo.db.users

    request_username: str = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(request_username).id
    except:
        # id for None user
        user_id = 1516945

    if request.method == "GET":

        if user_database.find_one({"_id":user_id}) != None:
            user_data = user_database.find_one({"_id":user_id})
        else:
            user_data = makeUser(username=osuApi.user(user_id).username)
            user_database.insert_one(user_data)

        return user_data

    elif request.method == "PUT":

        user_id = osuApi.user(request_username).id
        user_database.update_one({"_id":user_id},{ "$set" :makeUser(username=user_id)})
        return '', 204