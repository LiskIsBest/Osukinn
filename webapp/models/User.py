from bson import ObjectId
from typing import Union
from datetime import datetime
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from .Song import Song

class User(BaseModel):
	id: Union[PyObjectId, str] = Field(default_factory=PyObjectId, alias="_id")
	public_id: int = 1516945
	username: str = "None"
	osu_rank: int
	mania_rank: int
	taiko_rank: int
	fruits_rank: int
	avatar_url: str
	last_time_refreshed: datetime
	osu_songs: list[Song] = []
	mania_songs: list[Song] = []
	taiko_songs: list[Song] = []
	fruits_songs: list[Song] = []

	class Config:
		allow_population_by_field_name = True
		arbitrary_types_allowed = True
		json_encoders = {
				ObjectId: str,
				datetime: str,
				}
		
class UpdateUser(BaseModel):
	username: str = "None"
	osu_rank: int
	mania_rank: int
	taiko_rank: int
	fruits_rank: int
	avatar_url: str
	last_time_refreshed: datetime
	osu_songs: list[Song] = []
	mania_songs: list[Song] = []
	taiko_songs: list[Song] = []
	fruits_songs: list[Song] = []

	class Config:
		arbitrary_types_allowed = True
		json_encoders = {
				datetime: str,
				}