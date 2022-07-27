from flask import Blueprint, redirect, render_template, request

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
def users():
    user_database = mongo.db.users
    
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
    def list_strip(value):
        return value.strip()
    map(list_strip,username_list)

    userList = [osuApi.user(username).id for username in username_list]
    
    for index, user_id in enumerate(userList):
        if user_database.find_one({"_id":user_id}) != None:
            userList[index]=user_database.find_one({"_id":user_id})
        else:
            userList[index]=makeUser(api=osuApi,username=osuApi.user(user_id).username)
            user_database.insert_one(userList[index])
  
    return render_template("index.html", userList=userList, modeChoice=request_mode, userListStr=request_string)

@views.route('/update', methods=["GET","POST"])
def update():
    user_database = mongo.db.users
    
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    username_list = request_string.replace(" ","").split(',') if request.args.get("usernames") != None else ["None"]
    
    user_id_list = [osuApi.user(username_list[index]).id for index in range(len(username_list))]

    for index, id in enumerate(user_id_list):
        user_database.update_one({"_id":id},{ "$set" :makeUser(api=osuApi,username=username_list[index])})

    return redirect(f"/?mode={request_mode}&usernames={request_string}")