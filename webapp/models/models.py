from datetime import datetime
from bson import ObjectId
from enum import Enum
from pydantic import BaseModel, Field

class Modes(Enum):
    OSU = "osu"
    MANIA = "mania"
    TAIKO = "taiko"
    CTB = "fruits"

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Song(BaseModel):
    place: int
    song_id: int
    accuracy: float
    mods: str
    score: int
    max_combo: int
    unweighted_pp: float
    weighted_pp: float
    weight: float
    mode: str

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    public_id: int = 1516945
    username: str = "None"
    osu_rank: int
    mania_rank: int
    taiko_rank: int
    fruits_rank: int
    avatar_url: str
    last_time_refreshed: datetime = datetime.now().replace(microsecond=0)
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