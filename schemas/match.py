# schemas/match.py
from pydantic import BaseModel
from datetime import datetime

class MatchBase(BaseModel):
    team_a_id: int
    team_b_id: int
    score_a: int = 0
    score_b: int = 0
    date: datetime | None = None
    location: str | None = None

class MatchCreate(MatchBase):
    pass

class MatchResponse(MatchBase):
    id: int

    class Config:
        from_attributes = True
