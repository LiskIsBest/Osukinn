from flask import Blueprint, render_template, request
# from flask_cors import CORS
# from . import statGetter

views = Blueprint('osuStats', __name__)
# CORS(views)

from ossapi import *
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URL = os.environ.get("REDIRECT_URL")

class OsuUser:
    api = OssapiV2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URL)

    def __init__(self,username):
        self.username = username
        self.std_rank = 9999999
        if self.api.user(username,mode="osu").rankHistory != None:
            self.std_rank = self.api.user(username,mode="osu").rankHistory.data[-1]
            
        self.mania_rank = 9999999
        if self.api.user(username,mode="mania").rankHistory != None:
            self.mania_rank = self.api.user(username,mode="mania").rankHistory.data[-1]
            
        self.taiko_rank = 9999999
        if self.api.user(username,mode="taiko").rankHistory != None:
            self.taiko_rank = self.api.user(username,mode="taiko").rankHistory.data[-1]
            
        self.ctb_rank = 9999999
        if self.api.user(username,mode="fruits").rankHistory != None:
            self.ctb_rank = self.api.user(username,mode="fruits").rankHistory.data[-1]
            
        self.avatar_url = self.api.user(username).avatar_url
        self.osuJson = {
                "username": self.username, 
                "std_rank": self.std_rank, 
                "mania_rank": self.mania_rank,
                "taiko_rank": self.taiko_rank,
                "ctb_rank": self.ctb_rank,
                "avatar_url": self.avatar_url
                }
    

@views.route('/users')
def members():
    
    bothUsers = {
        "user1":OsuUser(request.args.get('username1')).osuJson,
        "user2":OsuUser(request.args.get('username2')).osuJson,
        }
    
    return render_template("home.html",user1=bothUsers["user1"],user2=bothUsers["user2"])
