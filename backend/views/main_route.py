from flask import Blueprint, redirect, render_template, request, session
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from ..extenstions import mongo, osuApi

main = Blueprint('osuStats', __name__)

import datetime

def makeUser(api: object, username: str) -> dict:
    if username == "":
        username = "None"
    else:
        try:
            api.user(username).username
        except ValueError:
            username = "None"
    user_id = api.user(username).id
    getRank = lambda mode, username: 9_999_999_999 if (api.user(username,mode=mode).rankHistory == None) else api.user(username,mode=mode).rankHistory.data[-1]
    return {"_id": user_id, 
            "username": api.user(user_id).username,
            "osu_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "fruits_rank": getRank(username=username,mode="fruits"),
            "avatar_url": api.user(username).avatar_url,
            "last_time_refreshed": datetime.datetime.now().replace(microsecond=0)
            }
            
@main.route('/', methods=["GET"])
def users():
    user_database = mongo.db.users
    session["userlist"] = []
    request_mode = "mania" if request.args.get("mode") == None else request.args.get("mode")
    request_string = "None" if request.args.get("usernames") == "" else request.args.get("usernames")
    username_list = request_string.split(',') if request.args.get("usernames") != None else ["None"]
    username_list=list(map(lambda name: name.strip(),username_list))

    session["request_mode"] = request_mode
    session["request_string"] = request_string

    userList =[]
    for username in username_list:
        try:
            userList.append(osuApi.user(username).id)
        except:
            # id for None user
            userList.append(1516945)
    
    for index, user_id in enumerate(userList):
        if user_database.find_one({"_id":user_id}) != None:
            userList[index]=user_database.find_one({"_id":user_id})
        else:
            userList[index]=makeUser(api=osuApi,username=osuApi.user(user_id).username)
            user_database.insert_one(userList[index])
    
    def keyRank(user):
        return user[f"{request_mode}_rank"]
    
    if request_mode != "all" and len(userList) > 1:
        userList.sort(reverse=False,key=keyRank)
        session["best_user"]=userList[0]
    else:
        session["best_user"]="debug"

    session["userlist"] = userList
    session.modified = True
  
    return render_template("index.html")

@main.route('/update', methods=["GET"])
def update():
    user_database = mongo.db.users
    
    request_mode = session["request_mode"]
    request_string = session["request_string"]
    
    userList = session["userlist"]
    
    db_requests = [
        (UpdateOne({"_id":user["_id"]},{ "$set" :makeUser(api=osuApi,username=user["username"])})) for user in userList
    ]
    
    try:
        user_database.bulk_write(db_requests, ordered=False)
    except BulkWriteError as bwe:
        print(bwe.details)

    session.pop("userlist", None)
    session.pop("request_mode", None)
    session.pop("request_string", None)
    session.modified = True

    return redirect(f"/?mode={request_mode}&usernames={request_string}")