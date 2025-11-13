# schemas/team.py
from pydantic import BaseModel
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    city: str | None = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(TeamBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
