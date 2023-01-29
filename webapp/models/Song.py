from pydantic import BaseModel

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