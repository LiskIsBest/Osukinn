from flask import Blueprint, render_template, request

views = Blueprint('osuStats', __name__)

from ossapi import *
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = os.environ.get("REDIRECT_URL")

osuApi = OssapiV2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URL)

def makeUser(api: object, username: str) -> dict:
    getRank = lambda mode, username: "No rank" if (api.user(username,mode=mode).rankHistory == None) else api.user(username,mode=mode).rankHistory.data[-1]
    return {"username": username, 
            "std_rank": getRank(username=username,mode="osu"), 
            "mania_rank": getRank(username=username,mode="mania"),
            "taiko_rank": getRank(username=username,mode="taiko"),
            "ctb_rank": getRank(username=username,mode="fruits"),
            "avatar_url": api.user(username).avatar_url
            }

@views.route('/', methods=["GET","POST"])
def members():
    
    user1=makeUser(api=osuApi,username=request.args.get('username1'))
    user2=makeUser(api=osuApi,username=request.args.get('username2'))
    
    # return render_template("home.html",user1=user1,user2=user2)
    return render_template("base.html", userList=[user1,user2])
