from datetime import datetime, date
import json
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ..extensions import NewOsuApiConnection, NewMongoConnection
from ..models.models import User, Song, Modes

router = APIRouter()

# makes dictionaries for database entries
def makeUser(username):

    # osu api connection
    osuApi = NewOsuApiConnection()

    match username:
        case "":
            username = "None"
        case _:
            try:
                osuApi.user(user=username)
            except ValueError:
                username = "None"

    
    # pull user data
    user = osuApi.users(user_ids=[osuApi.user(username).id])[0]

    data = User(
            public_id = user.id,
            username = user.username,
            osu_rank = getRank(user=user, mode=Modes.OSU.value),
            mania_rank = getRank(user=user, mode=Modes.MANIA.value),
            taiko_rank = getRank(user=user, mode=Modes.TAIKO.value),
            fruits_rank = getRank(user=user, mode=Modes.CTB.value),
            avatar_url = user.avatar_url,
            osu_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.OSU.value),
            mania_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.MANIA.value),
            taiko_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.TAIKO.value),
            fruits_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.CTB.value)
            )
    
    return data

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
    return [
        Song(
            place=index+1,
            song_id=score.best_id,
            accuracy=score.accuracy,
            mods=str(score.mods),
            score=score.score,
            max_combo=score.max_combo,
            unweighted_pp=score.pp,
            weighted_pp=score.weight.pp,
            weight=score.weight.percentage,
            mode=mode
        ).dict()
        for index, score in enumerate(songs)
    ]

# serializer for mongoDB json dumps
def userJsonSerializer(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat(sep=" ")

@router.get("/{username}", response_model=User, response_class=JSONResponse)
async def getData(username:str) -> any:
    osuApi = NewOsuApiConnection()

    mongo = NewMongoConnection()
    db = mongo.osukinnData
    userCollection = db.users

    username = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(user=username).id
    except:
        # id for "None" user
        user_id = 1516945

    if (user_data:= await userCollection.find_one({"public_id" : user_id})) != None:
        user_data = jsonable_encoder(user_data)
        mongo.close()
        return JSONResponse(status_code=status.HTTP_302_FOUND, content=user_data)
    else:
        user_data = makeUser(username=user_id)
        user_data = jsonable_encoder(user_data)
        new_user = await userCollection.insert_one(user_data)
        created_user = await userCollection.find_one({"_id":new_user.public_id})
        mongo.close()
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

@router.put("/{username}", response_model=None ,response_class=JSONResponse)
async def update(username:str) -> any:
    osuApi = NewOsuApiConnection()

    mongo = NewMongoConnection()
    db = mongo.osukinnData
    userCollection = db.users

    username = "None" if username == "" else username

    try:
        # check if user id exists
        user_id = osuApi.user(user=username).id
    except:
        # id for "None" user
        user_id = 1516945

    user_data = makeUser(username=user_id)
    await userCollection.update_one({"public_id": user_data.public_id},{"$set":user_data.dict(by_alias=True)})
    mongo.close()
    return JSONResponse(status_code=status.HTTP_200_OK, content={f"{username}":"updated"})