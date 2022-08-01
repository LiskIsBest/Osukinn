from flask import Blueprint, redirect, render_template, request, session

from ..extenstions import mongo, osuApi

main = Blueprint('osuStats', __name__)

import datetime

# from ossapi import *
# from dotenv import load_dotenv
# import os

# load_dotenv()
# CLIENT_ID = os.environ.get("CLIENT_ID")
# CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
# REDIRECT_URL = os.environ.get("REDIRECT_URL")

# osuApi = OssapiV2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URL)

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
            "osu_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "fruits_rank": getRank(username=username,mode="fruits"),
            "avatar_url": api.user(username).avatar_url,
            "last_time_refreshed": datetime.datetime.now().replace(microsecond=0)
            }
            
@main.route('/', methods=["GET","POST"])
def users():
    user_database = mongo.db.users
    session["userlist"] = []
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
    username_list=list(map(lambda name: name.strip(),username_list))

    userList = [osuApi.user(username).id for username in username_list]
    
    for index, user_id in enumerate(userList):
        if user_database.find_one({"_id":user_id}) != None:
            userList[index]=user_database.find_one({"_id":user_id})
        else:
            userList[index]=makeUser(api=osuApi,username=osuApi.user(user_id).username)
            user_database.insert_one(userList[index])
    
    session["userlist"] = userList
    session.modified = True
  
    return render_template("index.html", modeChoice=request_mode, userListStr=request_string)

@main.route('/update', methods=["GET","POST"])
def update():
    user_database = mongo.db.users
    
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    
    userList = session["userlist"]
    
    for user in userList:
        user_database.update_one({"username":user["username"]},{ "$set" :makeUser(api=osuApi,username=user["username"])})

    session.pop("userlist", None)
    session.modified = True

    return redirect(f"/?mode={request_mode}&usernames={request_string}")