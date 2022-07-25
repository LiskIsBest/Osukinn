from flask import Blueprint, render_template, request

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
    return {"username": username,
            "user_id": api.user(username).id, 
            "std_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "ctb_rank": getRank(username=username,mode="fruits"),
            "avatar_url": api.user(username).avatar_url,
            "last_time_refreshed": datetime.datetime.now()
            }

@views.route('/', methods=["GET","POST"])
def members():
    
    user1=makeUser(api=osuApi,username=request.args.get('username1'))
    user2=makeUser(api=osuApi,username=request.args.get('username2'))
    
    return render_template("base.html", userList=[user1,user2])
