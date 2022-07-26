from dataclasses import dataclass
from flask import Blueprint, redirect, render_template, request, url_for

from ..extenstions import mongo


views = Blueprint('osuStats', __name__)

import datetime

from ossapi import *
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = os.environ.get("REDIRECT_URL")

osuApi = OssapiV2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URL)

def makeUser(api: object, username: str) -> dict:
    if username == "":
        username = "None"
    else:
        try:
            api.user(username).username
        except ValueError:
            username = "None"
    getRank = lambda mode, username: 9_999_999_999 if (api.user(username,mode=mode).rankHistory == None) else api.user(username,mode=mode).rankHistory.data[-1]
    return {"_id": api.user(username).id, 
            "username": username,
            "std_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "ctb_rank": getRank(username=username,mode="fruits"),
            "avatar_url": api.user(username).avatar_url,
            "last_time_refreshed": datetime.datetime.now()
            }

@views.route('/', methods=["GET","POST"])
def members():
    user_database = mongo.db.users
    
    user1 = osuApi.user(request.args.get('username1'))
    user2 = osuApi.user(request.args.get('username2'))
    
    if user_database.find_one(user1.id) != None:
        user1=user_database.find_one(user1.id)
        user1["last_time_refreshed"] = datetime.datetime.now()
    else:
        user1 = makeUser(api=osuApi,username=request.args.get('username1'))
        
    if user_database.find_one(user2.id) != None:
        user2=user_database.find_one(user2.id)
        user2["last_time_refreshed"] = datetime.datetime.now()
    else:
        user2 = makeUser(api=osuApi,username=request.args.get('username2'))
    
    userList = [user1,user2]
    
    for user in userList:
        if user_database.find_one(user["_id"]) == None:
            user_database.insert_one(user)
        else:
            pass

    
    return render_template("base.html", userList=userList)

@views.route('/update', methods=["GET","POST"])
def update():
    user_database = mongo.db.users
    
    user1 = osuApi.user(request.args.get('username1'))
    user2 = osuApi.user(request.args.get('username2'))

    user_database.update_one({"_id":user1.id},{ "$set" :makeUser(api=osuApi,username=request.args.get('username1'))})
    user_database.update_one({"_id":user2.id},{ "$set" :makeUser(api=osuApi,username=request.args.get('username2'))})

    return redirect(f"/?username1={user1.username}&username2={user2.username}")