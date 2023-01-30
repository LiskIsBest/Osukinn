from bson import ObjectId
from typing import Union
from datetime import datetime
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from .Song import Song

class User(BaseModel):
	"""
	Model object for user data.

	All data is pulled from the Osu api https://osu.ppy.sh/docs/index.html

	attributes:
		_id: PyObjectId - MonogoDB ObjectId
			Automatically generated on object instantiation.
		public_id: int
			Osu account id.
		username: str
			Osu account username.
		osu_rank: int
			Osu account global rank for the Standard gamemode.
		mania_rank: int
			Osu account global rank for the Mania gamemode.
		taiko_rank: int
			Osu account global rank for the Taiko gamemode.
		fruits_rank: int
			Osu account global rank for the Catch the Beat gamemode.
		avatar_url: str
			Osu account profile image url.
		last_time_refreshed: datetime
			Timestamp of when the User object is created.
		osu_songs: list[Song] - default = []
			List for up to top five plays for Osu Standard gamemode.
		mania_songs: list[Song] - default = []
			List for up to top five plays for Osu Mania gamemode.
		taiko_songs: list[Song] - default = []
			List for up to top five plays for Osu Taiko gamemode.
		fruits_songs: list[Song] - default = []
			List for up to top five plays for Osu Catch the Beat gamemode.
	"""
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
	"""
	Model for updated user data.
	
	attributes:
		username: str
			Osu account username.
		osu_rank: int
			Osu account global rank for the Standard gamemode.
		mania_rank: int
			Osu account global rank for the Mania gamemode.
		taiko_rank: int
			Osu account global rank for the Taiko gamemode.
		fruits_rank: int
			Osu account global rank for the Catch the Beat gamemode.
		avatar_url: str
			Osu account profile image url.
		last_time_refreshed: datetime
			Timestamp of when the User object is created.
		osu_songs: list[Song] - default = []
			List for up to top five plays for Osu Standard gamemode.
		mania_songs: list[Song] - default = []
			List for up to top five plays for Osu Mania gamemode.
		taiko_songs: list[Song] - default = []
			List for up to top five plays for Osu Taiko gamemode.
		fruits_songs: list[Song] - default = []
			List for up to top five plays for Osu Catch the Beat gamemode.
	"""
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