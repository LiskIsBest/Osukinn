from pydantic import BaseModel, Field, validator
import datetime
from bson import ObjectId

class user_data_class(BaseModel):
    user_id: int
    username: str
    osu_rank: int
    mania_rank: int
    taiko_rank: int
    fruits_rank: int
    avatar_url: str
    last_time_refreshed: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
                ObjectId: str
                }








