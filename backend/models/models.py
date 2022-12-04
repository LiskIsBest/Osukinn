from pydantic import BaseModel
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
        json_encoders = {
                ObjectId: str
                }

