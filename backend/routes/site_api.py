from flask import Blueprint, request
from flask_cors import CORS
from pymongo import MongoClient

from ossapi import *

import datetime

from dotenv import load_dotenv
import os

load_dotenv() 

CLIENT_ID: int = os.environ.get("CLIENT_ID")
CLIENT_SECRET: str = os.environ.get("CLIENT_SECRET")
REDIRECT_URL: str = os.environ.get("REDIRECT_URL")

api = Blueprint("api",__name__)
CORS(api)

""" Returns User data in dictionary """
def makeUser(username: str) -> dict:

    # osu api connection
    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)
    
    # Check if username is valid. if not set name to "None"
    match username:
        case "":
            username = "None"
        case _:
            try:
                osuApi.user(username).username
            except ValueError:
                username = "None"
    
    # pull user data
    user = osuApi.users(user_ids=[osuApi.user(username).id])[0]

    # function to pull global rank for specified gamemode. 9_999_999_999 used as No rank found value
    def get_rank(user, mode):
        rankStat = eval(f"user.statistics_rulesets.{mode}")
        if rankStat != None:
            if rankStat.global_rank == None:
                return 9_999_999_999
            return rankStat.global_rank
        return 9_999_999_999

    def get_song_data(user_id, mode):
        songs = osuApi.user_scores(user_id=user_id,type_="best", limit=5,mode=mode)
        return f"top_five_{mode}",[
            {
                "place" : index+1,
                "song_id" : score.best_id,
                "accuracy" : score.accuracy,
                "mods" : str(score.mods),
                "score" : score.score,
                "max_combo" : score.max_combo,
                "unweighted_pp" : score.pp,
                "weighted_pp" : score.weight.pp,
                "weight" : score.weight.percentage,
                "mode" : mode
            }
            for index, score in enumerate(songs)
        ]

    # dictionary matching MongoDB document layout
    return {"_id": user.id,
            "publicId": user.id,
            "username": user.username,
            "osu_rank": get_rank(user=user,mode="osu"), 
            "mania_rank": get_rank(user=user,mode="mania"),
            "taiko_rank": get_rank(user=user,mode="taiko"),
            "fruits_rank": get_rank(user=user,mode="fruits"),
            "avatar_url": user.avatar_url,
            "last_time_refreshed": str(datetime.datetime.now().replace(microsecond=0)),
            (osu_songs := get_song_data(user_id=user.id,mode="osu"))[0]:osu_songs[1],
            (mania_songs := get_song_data(user_id=user.id,mode="mania"))[0]:mania_songs[1],
            (taiko_songs := get_song_data(user_id=user.id,mode="taiko"))[0]:taiko_songs[1],
            (fruits_songs := get_song_data(user_id=user.id,mode="fruits"))[0]:fruits_songs[1],
            }

@api.route("<string:username>",methods=["GET","PUT"])
def data(username) -> dict:

    osuApi = OssapiV2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URL)

    client = MongoClient(os.environ.get("MONGO_URI"))
    db = client.osukinnData
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
            if (data := user_database.find_one({"_id":user_id})) != None:
                user_data = data
            else:
                user_data = makeUser(username=user_id)
                user_database.insert_one(user_data)

            return user_data

        case "PUT":
            user_database.update_one({"_id":user_id},{ "$set" :makeUser(username=user_id)})
            return '', 204