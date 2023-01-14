from datetime import datetime, date
import json

from fastapi import APIRouter, status

from ..extensions import NewOsuApiConnection, NewMongoConnection

router = APIRouter(prefix="/users")

# makes dictionaries for database entries
def makeUser(username):

    # osu api connection
    osuApi = NewOsuApiConnection()
    
    # Check if username is valid. if not set name to "None"
    if username == "":
        username = "None"
    
    if not osuApi.user(user=username):
        username = "None"

    # match username:
    #     case "":
    #         username = "None"
    #     case _:
    #         try:
    #             osuApi.user(user=username).username
    #         except ValueError:
    #             username = "None"

    
    # pull user data
    user = osuApi.users(user_ids=[osuApi.user(username).id])[0]

    # dictionary matching MongoDB document layout
    return {"_id": user.id,
            "publicId": user.id,
            "username": user.username,
            "osu_rank": getRank(user=user, mode="osu"), 
            "mania_rank": getRank(user=user, mode="mania"),
            "taiko_rank": getRank(user=user, mode="taiko"),
            "fruits_rank": getRank(user=user, mode="fruits"),
            "avatar_url": user.avatar_url,
            "last_time_refreshed": datetime.now().replace(microsecond=0),
            (osu_songs := getSongData(api=osuApi, user_id=user.id, mode="osu"))[0] : osu_songs[1],
            (mania_songs := getSongData(api=osuApi, user_id=user.id, mode="mania"))[0] : mania_songs[1],
            (taiko_songs := getSongData(api=osuApi, user_id=user.id, mode="taiko"))[0] : taiko_songs[1],
            (fruits_songs := getSongData(api=osuApi, user_id=user.id, mode="fruits"))[0] : fruits_songs[1],
            }

# function to pull global rank for specified gamemode. 9_999_999_999 used as "No rank" found value
def getRank(user, mode):
    rankStat = eval(f"user.statistics_rulesets.{mode}")
    if rankStat != None:
        if rankStat.global_rank == None:
            return 9_999_999_999
        return rankStat.global_rank
    return 9_999_999_999

# returns list of top 5 plays for given mode
def getSongData(api, user_id, mode):
    songs = api.user_scores(user_id=user_id, type_="best", limit=5, mode=mode)
    return f"top_five_{mode}", [
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

# serializer for mongoDB json dumps
def userJsonSerializer(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ")

@router.get("/{username}", status_code=status.HTTP_200_OK)
async def get_data(username: str = "None"):
    osuApi = NewOsuApiConnection()

    mongo = NewMongoConnection()
    db = mongo.osukinnData
    userCollection = db.users

    # username = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(user=username).id
    except:
        # id for "None" user
        user_id = 1516945

    if (data := userCollection.find_one({"_id" : user_id})) != None:
        user_data = data
    else:
        user_data = makeUser(username=user_id)
        userCollection.insert_one(user_data)

    mongo.close()
    return json.dumps(user_data, default=userJsonSerializer, indent=3)

@router.put("/{username}", status_code=status.HTTP_200_OK)
async def update(username: str = "None"):
    osuApi = NewOsuApiConnection()

    mongo = NewMongoConnection()
    db = mongo.osukinnData
    userCollection = db.users

    # username = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(user=username).id
    except:
        # id for "None" user
        user_id = 1516945

    userCollection.update_one({"_id" : user_id},{"$set" : makeUser(username=user_id)})

    mongo.close()
    return {f"{username}":"Updated"}