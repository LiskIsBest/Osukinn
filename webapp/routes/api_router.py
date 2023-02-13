from datetime import datetime, date
import json
from typing import Any
from bson import ObjectId
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic.tools import parse_obj_as
from losuapi import AsyncOsuApi
from losuapi.types import UserCompact, Score, GameMode
from ..extensions import NewAsyncMotorConnection, NewAsyncOsuApiConnection
from ..models import UpdateUser, User, Song, PyObjectId

api = APIRouter()

async def makeUser(username: str | int, update: bool=False) -> User | UpdateUser:
	"""
	Return User/UpdateUser model object.

	parameters:
		username: str | int
			Username or Account ID for Osu account.
		update: bool
			True returns an UpdateUser object, False returns a User object.
	return: models.User | models.UpdateUser
	"""

	OsuApi: AsyncOsuApi = NewAsyncOsuApiConnection()

	match username:
		case "":
			user_id = 1516945
		case _:
			user_id = await OsuApi.user(username=username)
			if not username:
				user_id = 1516945
			else: 
				user_id = user_id.id

	# pull user data
	user: UserCompact = await OsuApi.users(user_ids=[user_id])
	user = user.users[0]
	
	match(update):
		case False:
			data = User(
				public_id = user.id,
				username = user.username,
				osu_rank = getRank(user=user, mode=GameMode.OSU.value),
				mania_rank = getRank(user=user, mode=GameMode.MANIA.value),
				taiko_rank = getRank(user=user, mode=GameMode.TAIKO.value),
				fruits_rank = getRank(user=user, mode=GameMode.FRUITS.value),
				avatar_url = user.avatar_url,
				last_time_refreshed = datetime.now().replace(microsecond=0),
				osu_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.OSU.value),
				mania_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.MANIA.value),
				taiko_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.TAIKO.value),
				fruits_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.FRUITS.value)
				)
		case True:
			data = UpdateUser(
				username = user.username,
				osu_rank = getRank(user=user, mode=GameMode.OSU.value),
				mania_rank = getRank(user=user, mode=GameMode.MANIA.value),
				taiko_rank = getRank(user=user, mode=GameMode.TAIKO.value),
				fruits_rank = getRank(user=user, mode=GameMode.FRUITS.value),
				avatar_url = user.avatar_url,
				last_time_refreshed = datetime.now().replace(microsecond=0),
				osu_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.OSU.value),
				mania_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.MANIA.value),
				taiko_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.TAIKO.value),
				fruits_songs = await getSongData(api=OsuApi, user_id=user.id, mode=GameMode.FRUITS.value)
				)
	
	return data

def getRank(user, mode):
	"""
	Returns a users rank.

	Returns a users global rank for a given osu gamemode.
	If no rank is found then 9,999,999,999 is returned instead.

	parameters:
		user: losuapi.types.UserCompact
			UserCompact object from the ossapi library.

		mode: str
			osu, mania, taiko, or fruits
	return: int
	"""
	match(mode):
		case "osu":
			rankStat: int | None = user.statistics_rulesets.osu
		case "mania":
			rankStat: int | None = user.statistics_rulesets.mania
		case "taiko":
			rankStat: int | None = user.statistics_rulesets.taiko
		case "fruits":
			rankStat: int | None = user.statistics_rulesets.fruits
		case _:
			raise("Invalid mode entered")

	if rankStat != None:
		if rankStat.global_rank == None:
			return 9_999_999_999
		return rankStat.global_rank
	return 9_999_999_999

async def getSongData(api: AsyncOsuApi, user_id: int, mode: str) -> list[dict]:
	"""
	Returns a list of Song dictionaries.

	parameters:
		api: OsuApi
			losuapi.AsyncOsuApi object from makeUser function.
		user_id: int
			Account ID for osu account.
		mode: str
			osu, mania, taiko, or fruits
	return: list[dict]
	"""
	if mode not in GameMode.list():
		mode = "osu"

	songs: list[Score] = await api.user_scores(user_id=user_id, Type="best", limit=5, mode=mode)
	return [
		Song(
			place=index,
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
		for index, score in enumerate(songs, start=1)
	]

def myJsonSerializer(value: Any) -> Any:
	"""
	Custom JSON serializer

	Values:
		datetime.datetime -> str\n
		bson.ObjectId -> str\n
		models.PyObjectId -> str\n
		models.Song -> json str\n
	"""
	if isinstance(value, (date, datetime)):
		return value.isoformat(sep=" ")
	if isinstance(value,ObjectId):
		return str(value)
	if isinstance(value, PyObjectId):
		return str(value)
	if isinstance(value, Song):
		return Song.json(by_alias=True)

class MyJSONResponse(JSONResponse):
	"""Custom JSONResponse object"""
	def render(self, content: Any) -> bytes:
		return json.dumps(
			content,
			ensure_ascii=False,
			allow_nan=True,
			indent=4,
			separators=(",", ":"),
			default= myJsonSerializer,
		).encode("utf-8")

@api.get("/{username}", response_class=MyJSONResponse)
async def getData(username:str) -> MyJSONResponse:
	"""
	Returns JSONResponse.

	route: 0.0.0.0/users/username
	method: GET

	parameters:
		username: str
			{username} path parameter.
	return: MyJSONResponse
	"""
	OsuApi: AsyncOsuApi = NewAsyncOsuApiConnection()

	mongo = NewAsyncMotorConnection()
	db = mongo.osukinnData
	userCollection = db.users

	match(username):
		case "":
			user_id = 1516945
		case _:
			user_id = await OsuApi.user(username=username)
			if not user_id:
				user_id = 1516945
			else: 
				user_id = user_id.id

	if (data:= await userCollection.find_one({"public_id" : user_id})) != None:
		user_data = parse_obj_as(User,data)
		return MyJSONResponse(status_code=status.HTTP_200_OK, content=json.loads(user_data.json(by_alias=True)))
	else:
		user_data = await makeUser(username=user_id)
		await userCollection.insert_one(user_data.dict(by_alias=True))
		return MyJSONResponse(status_code=status.HTTP_200_OK, content=json.loads(user_data.json(by_alias=True)))

@api.put("/{username}", response_class=MyJSONResponse)
async def update(username:str) -> MyJSONResponse:
	"""
	Returns JSONResponse.

	route: 0.0.0.0/users/username
	method: PUT

	parameters:
		username: str
			{username} path parameter.
	return: MyJSONResponse
	"""

	OsuApi: AsyncOsuApi = NewAsyncOsuApiConnection()

	mongo = NewAsyncMotorConnection()
	db = mongo.osukinnData
	userCollection = db.users

	username = "None" if username == "" else username

	match(username):
		case "":
			user_id = 1516945
		case _:
			user_id = await OsuApi.user(username=username)
			if not user_id:
				user_id = 1516945
			else: 
				user_id = user_id.id

	user_data = await makeUser(username=user_id, update=True)
	await userCollection.update_one({"public_id": user_id},{"$set":user_data.dict(by_alias=True)})
	return MyJSONResponse(status_code=status.HTTP_202_ACCEPTED, content={username:"updated", "status": status.HTTP_202_ACCEPTED})