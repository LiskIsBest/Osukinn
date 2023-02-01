from datetime import datetime, date
import json
from typing import Any, Union
from bson import ObjectId
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic.tools import parse_obj_as
from ossapi import OssapiV2, UserCompact, Score
from ..extensions import NewOsuApiConnection, NewMongoConnection, Modes, MODES
from ..models import UpdateUser, User, Song, PyObjectId

api = APIRouter()

def makeUser(username: Union[str,int], update: bool=False) -> Union[User,UpdateUser]:
	"""
	Return User/UpdateUser model object.

	parameters:
		username: str | int
			Username or Account ID for Osu account.
		update: bool
			True returns an UpdateUser object, False returns a User object.
	return: models.User | models.UpdateUser
	"""
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
	user: UserCompact = osuApi.users(user_ids=[osuApi.user(username).id])[0]
	
	match(update):
		case False:
			data = User(
				public_id = user.id,
				username = user.username,
				osu_rank = getRank(user=user, mode=Modes.OSU.value),
				mania_rank = getRank(user=user, mode=Modes.MANIA.value),
				taiko_rank = getRank(user=user, mode=Modes.TAIKO.value),
				fruits_rank = getRank(user=user, mode=Modes.CTB.value),
				avatar_url = user.avatar_url,
				last_time_refreshed = datetime.now().replace(microsecond=0),
				osu_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.OSU.value),
				mania_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.MANIA.value),
				taiko_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.TAIKO.value),
				fruits_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.CTB.value)
				)
		case True:
			data = UpdateUser(
				username = user.username,
				osu_rank = getRank(user=user, mode=Modes.OSU.value),
				mania_rank = getRank(user=user, mode=Modes.MANIA.value),
				taiko_rank = getRank(user=user, mode=Modes.TAIKO.value),
				fruits_rank = getRank(user=user, mode=Modes.CTB.value),
				avatar_url = user.avatar_url,
				last_time_refreshed = datetime.now().replace(microsecond=0),
				osu_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.OSU.value),
				mania_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.MANIA.value),
				taiko_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.TAIKO.value),
				fruits_songs = getSongData(api=osuApi, user_id=user.id, mode=Modes.CTB.value)
				)
	
	return data

def getRank(user, mode):
	"""
	Returns a users rank.

	Returns a users global rank for a given osu gamemode.
	If no rank is found then 9,999,999,999 is returned instead.

	parameters:
		user: ossapi.UserCompact
			UserCompact object from the ossapi library.

		mode: str
			osu, mania, taiko, or fruits
	return: int
	"""
	match(mode):
		case "osu":
			rankStat: Union[int, None] = user.statistics_rulesets.osu
		case "mania":
			rankStat: Union[int, None] = user.statistics_rulesets.mania
		case "taiko":
			rankStat: Union[int, None] = user.statistics_rulesets.taiko
		case "fruits":
			rankStat: Union[int, None] = user.statistics_rulesets.fruits
		case _:
			raise("Invalid mode entered")

	if rankStat != None:
		if rankStat.global_rank == None:
			return 9_999_999_999
		return rankStat.global_rank
	return 9_999_999_999

def getSongData(api: OssapiV2, user_id: int, mode: str) -> list[dict]:
	"""
	Returns a list of Song dictionaries.

	parameters:
		api: OssapiV2
			ossapi.OssapiV2 object from makeUser function.
		user_id: int
			Account ID for osu account.
		mode: str
			osu, mania, taiko, or fruits
	return: list[dict]
	"""
	if mode not in MODES:
		mode = "osu"

	songs: list[Score] = api.user_scores(user_id=user_id, type_="best", limit=5, mode=mode)
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
			indent=None,
			separators=(",", ":"),
			default= myJsonSerializer,
		).encode("utf-8")

@api.get("/{username}", response_class=MyJSONResponse)
def getData(username:str) -> MyJSONResponse:
	"""
	Returns JSONResponse.

	route: 0.0.0.0/users/username
	method: GET

	parameters:
		username: str
			{username} path parameter.
	return: MyJSONResponse
	"""
	osuApi: OssapiV2 = NewOsuApiConnection()

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

	if (data:= userCollection.find_one({"public_id" : user_id})) != None:
		user_data = parse_obj_as(User,data)
		mongo.close()
		return MyJSONResponse(status_code=status.HTTP_200_OK, content=user_data.json(by_alias=True))
	else:
		user_data = makeUser(username=user_id)
		userCollection.insert_one(user_data.dict(by_alias=True))
		mongo.close()
		return MyJSONResponse(status_code=status.HTTP_200_OK, content=user_data.json(by_alias=True))

@api.put("/{username}", response_class=MyJSONResponse)
def update(username:str) -> MyJSONResponse:
	"""
	Returns JSONResponse.

	route: 0.0.0.0/users/username
	method: PUT

	parameters:
		username: str
			{username} path parameter.
	return: MyJSONResponse
	"""
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

	user_data = makeUser(username=user_id, update=True)
	userCollection.update_one({"public_id": user_id},{"$set":user_data.dict(by_alias=True)})
	mongo.close()
	return MyJSONResponse(status_code=status.HTTP_202_ACCEPTED, content={username:"updated", "status": status.HTTP_202_ACCEPTED})
